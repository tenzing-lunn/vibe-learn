"""Install vibe-learn into the project that contains this clone.

Run from your project after cloning:  python3 vibe-learn/setup.py
It asks which coding agents you use and sets up only those, inside this project.
Existing files are added to, never replaced. Running it again changes nothing
unless this clone moved or its skill files changed.
"""

import argparse
import filecmp
import json
from pathlib import Path
import shlex
import shutil
import sys


CLONE = Path(__file__).resolve().parent
SKILL = CLONE / "skills" / "vibe-learn"
HOOK = CLONE / "hooks" / "session_start.py"

# key: (display name, skill folder, how learning resumes, file that does it)
AGENTS = {
    "claude": ("Claude Code", ".claude/skills", "hook", ".claude/settings.json"),
    "codex": ("Codex", ".agents/skills", "hook", ".codex/hooks.json"),
    "gemini": ("Gemini CLI", ".agents/skills", "line", "GEMINI.md"),
    "other": ("Other agent", ".agents/skills", "line", "AGENTS.md"),
}
# Session sources each agent documents for SessionStart. Codex has no "fork".
MATCHERS = {
    "claude": "startup|resume|clear|compact|fork",
    "codex": "startup|resume|clear|compact",
}

START, END = "<!-- vibe-learn:start -->", "<!-- vibe-learn:end -->"
RESUME_LINE = (
    "If `.vibe-wise/profile.md` exists in this project and does not say "
    "`Learning mode: paused`, read `.agents/skills/vibe-learn/SKILL.md` before "
    "responding and follow it to resume learning from the notes in `.vibe-wise/`."
)


class SetupError(Exception):
    pass


def hook_command():
    # An absolute path avoids depending on which folder the agent runs hooks from.
    return "python3 " + shlex.quote(str(HOOK))


def is_stale_copy(command):
    """A vibe-learn hook from a clone that has since moved or been deleted."""
    try:
        parts = shlex.split(command)
    except ValueError:
        return False
    return (len(parts) == 2 and parts[0] == "python3"
            and parts[1].endswith("/hooks/session_start.py")
            and not Path(parts[1]).exists())


def check_target(path):
    # Writing through a link could change files outside this project.
    if path.is_symlink():
        raise SetupError("Refusing to write through a symlink: {}".format(path))


def read_json(path):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError):
        raise SetupError("{} is not valid JSON. Fix it first; nothing was changed.".format(path))
    if not isinstance(data, dict):
        raise SetupError("{} must contain a JSON object; nothing was changed.".format(path))
    return data


def plan_hook(path, agent):
    """Return new JSON text with our SessionStart hook, or None if already present."""
    data = read_json(path)
    hooks = data.setdefault("hooks", {})
    groups = hooks.setdefault("SessionStart", []) if isinstance(hooks, dict) else None
    if not isinstance(groups, list):
        raise SetupError("Unexpected hooks layout in {}; nothing was changed.".format(path))
    command = hook_command()
    for group in groups:
        for hook in group.get("hooks", []) if isinstance(group, dict) else []:
            if isinstance(hook, dict) and hook.get("command") == command:
                return None
    # Drop only our own entries that point at a clone path that no longer exists.
    for group in groups:
        if isinstance(group, dict) and isinstance(group.get("hooks"), list):
            group["hooks"] = [h for h in group["hooks"] if not (
                isinstance(h, dict) and is_stale_copy(h.get("command", "")))]
    groups[:] = [g for g in groups if not (isinstance(g, dict) and g.get("hooks") == [])]
    groups.append({"matcher": MATCHERS[agent], "hooks": [
        {"type": "command", "command": command, "timeout": 5}]})
    return json.dumps(data, indent=2) + "\n"


def plan_line(path):
    """Return instruction-file text containing our marked block, or None if current."""
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    block = "{}\n{}\n{}".format(START, RESUME_LINE, END)
    if START in text and END in text:
        before, rest = text.split(START, 1)
        after = rest.split(END, 1)[1]
        new = before + block + after
    else:
        new = text + ("\n" if text and not text.endswith("\n") else "") + \
            ("\n" if text else "") + block + "\n"
    return None if new == text else new


def skill_differs(dest):
    if not dest.exists():
        return True
    comparison = filecmp.dircmp(str(SKILL), str(dest))
    return bool(comparison.left_only or comparison.diff_files or comparison.funny_files)


def plan(project, agents):
    """Work out every change before writing anything, so an error changes nothing."""
    skills, files = [], {}
    for agent in agents:
        _, skill_dir, mode, target = AGENTS[agent]
        dest = project / skill_dir / "vibe-learn"
        check_target(dest)
        check_target(project / target)
        if dest not in skills:
            skills.append(dest)
        path = project / target
        if path not in files:
            files[path] = plan_hook(path, agent) if mode == "hook" else plan_line(path)
    return skills, files


def apply(skills, files):
    changes = []
    for dest in skills:
        status = "unchanged"
        if skill_differs(dest):
            status = "updated" if dest.exists() else "created"
            shutil.copytree(str(SKILL), str(dest), dirs_exist_ok=True)
        changes.append((status, dest))
    for path, text in files.items():
        if text is None:
            changes.append(("unchanged", path))
            continue
        status = "updated" if path.exists() else "created"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        changes.append((status, path))
    return changes


def ask_agents():
    keys = list(AGENTS)
    print("Which coding agents do you use in this project?")
    for number, key in enumerate(keys, 1):
        print("  {}. {}".format(number, AGENTS[key][0]))
    while True:
        answer = input("Numbers separated by commas (e.g. 1,2), or 'all': ").strip().lower()
        if answer == "all":
            return keys
        try:
            picked = [keys[int(part) - 1] for part in answer.split(",") if part.strip()]
        except (ValueError, IndexError):
            picked = []
        if picked:
            return list(dict.fromkeys(picked))
        print("Please enter numbers from the list.")


def parse_agents(value):
    picked = [part.strip().lower() for part in value.split(",") if part.strip()]
    unknown = [p for p in picked if p not in AGENTS]
    if unknown or not picked:
        raise SetupError("Unknown agents: {}. Choose from: {}.".format(
            ", ".join(unknown) or "(none)", ", ".join(AGENTS)))
    return list(dict.fromkeys(picked))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--agents", help="Comma-separated: " + ", ".join(AGENTS))
    parser.add_argument("--project", help="Project folder (default: the folder containing this clone)")
    args = parser.parse_args(argv)
    project = Path(args.project).resolve() if args.project else CLONE.parent
    try:
        if not project.is_dir():
            raise SetupError("Project folder not found: {}".format(project))
        if project == CLONE:
            raise SetupError("Clone vibe-learn inside your project, then run setup from there.")
        if args.agents:
            agents = parse_agents(args.agents)
        elif sys.stdin.isatty():
            agents = ask_agents()
        else:
            raise SetupError("No terminal to ask in. Pass --agents, e.g. --agents codex,claude.")
        changes = apply(*plan(project, agents))
    except SetupError as error:
        print("Setup stopped: {}".format(error), file=sys.stderr)
        return 1

    print("\nvibe-learn set up in {}".format(project))
    for status, path in changes:
        print("  {:<9} {}".format(status, path.relative_to(project)))
    names = [AGENTS[a][0] for a in agents]
    print("\nStart learning: $vibe-learn in Codex, /vibe-learn in Claude Code;")
    print("in other agents, ask them to use the vibe-learn skill.")
    if "codex" in agents:
        print("Codex will ask you to review and trust the new hook the first time it runs.")
    print("Suggested .gitignore lines (not added automatically):")
    print("  {}/".format(CLONE.relative_to(project)) if CLONE.parent == project else "  (your vibe-learn clone)")
    print("  .vibe-wise/")
    print("Agents set up: {}".format(", ".join(names)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
