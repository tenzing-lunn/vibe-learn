"""Install vibe-learn into the project that contains this clone.

Run from your project after cloning:  python3 vibe-learn/setup.py
It asks which coding agents you use and sets up only those, inside this project.
Your existing files are added to, never replaced; the installed skill folders
are refreshed from this clone. Running it again changes nothing
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
# Installed side by side; the reset skill finds vibe-learn as its sibling.
SKILLS = [CLONE / "skills" / "vibe-learn", CLONE / "skills" / "vibe-learn-reset"]
HOOK = CLONE / "hooks" / "session_start.py"

# key: (display name, skill folder, [(how learning resumes, file that does it)])
AGENTS = {
    # settings.local.json is per machine, since the hook holds this clone's absolute path.
    "claude": ("Claude Code", ".claude/skills", [("hook", ".claude/settings.local.json")]),
    # Codex skips project hooks until the user trusts them, and in `codex exec`.
    # It always reads AGENTS.md, so the line there is the fallback.
    "codex": ("Codex", ".agents/skills", [("hook", ".codex/hooks.json"), ("line", "AGENTS.md")]),
    "gemini": ("Gemini CLI", ".agents/skills", [("line", "GEMINI.md")]),
    "other": ("Other agent", ".agents/skills", [("line", "AGENTS.md")]),
}
# Session sources each agent documents for SessionStart. Codex has no "fork".
MATCHERS = {
    "claude": "startup|resume|clear|compact|fork",
    "codex": "startup|resume|clear|compact",
}

START, END = "<!-- vibe-learn:start -->", "<!-- vibe-learn:end -->"
RESUME_LINE = (
    "If `.vibe-notes/profile.md` exists in this project and does not say "
    "`Learning mode: paused`, read `.agents/skills/vibe-learn/SKILL.md` before "
    "responding and follow it to resume learning from the notes in `.vibe-notes/`. "
    "If it says `Teach mode: on`, change no project files, even if asked to skip "
    "teaching or just implement, until the learner says \"back to building\"."
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


def check_target(path, project):
    # Writing through a link (the file or any folder above it) could change files
    # outside this project, e.g. a .claude folder linked to ~/.claude.
    while path != project:
        if path.is_symlink():
            raise SetupError("Refusing to write through a symlink: {}".format(path))
        path = path.parent


def read_json(path):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
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
        hooks_list = group.get("hooks") if isinstance(group, dict) else None
        for hook in hooks_list if isinstance(hooks_list, list) else []:
            if isinstance(hook, dict) and hook.get("command") == command:
                return None
    # Drop only our own entries that point at a clone path that no longer exists.
    drop_ours(groups, is_stale_copy)
    groups.append({"matcher": MATCHERS[agent], "hooks": [
        {"type": "command", "command": command, "timeout": 5}]})
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def drop_ours(groups, is_ours):
    """Remove our hook entries; drop only the groups that removal left empty."""
    removed = False
    for group in list(groups):
        hooks = group.get("hooks") if isinstance(group, dict) else None
        if not isinstance(hooks, list):
            continue
        kept = [h for h in hooks if not (isinstance(h, dict)
                and isinstance(h.get("command"), str) and is_ours(h["command"]))]
        if len(kept) != len(hooks):
            removed = True
            if kept:
                group["hooks"] = kept
            else:
                groups.remove(group)
    return removed


def plan_unhook(path):
    """Return JSON text without our hook, or None if it isn't there.

    Earlier versions put Claude Code's hook in the shared .claude/settings.json.
    """
    try:
        data = read_json(path)
    except SetupError:
        return None  # Only cleanup; a file we can't parse is left exactly as it is.
    hooks = data.get("hooks")
    groups = hooks.get("SessionStart") if isinstance(hooks, dict) else None
    if not isinstance(groups, list):
        return None
    if not drop_ours(groups, lambda c: c == hook_command() or is_stale_copy(c)):
        return None
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def plan_line(path):
    """Return instruction-file text containing our marked block, or None if current."""
    text = read_text(path)
    nl = "\r\n" if "\r\n" in text else "\n"  # keep the file's own line endings
    block = nl.join((START, RESUME_LINE, END))
    starts, ends = text.count(START), text.count(END)
    if starts == ends == 1 and text.index(START) < text.index(END):
        before, rest = text.split(START, 1)
        new = before + block + rest.split(END, 1)[1]
    elif starts == ends == 0:
        new = text + (nl if text and not text.endswith("\n") else "") + \
            (nl if text else "") + block + nl
    else:
        # Guessing which markers are ours could delete the user's own text.
        raise SetupError("Unmatched vibe-learn markers in {}. Keep one start and one "
                         "end line (or remove both), then rerun; nothing was changed.".format(path))
    return None if new == text else new


def read_text(path):
    if not path.exists():
        return ""
    with path.open(encoding="utf-8", newline="") as stream:
        return stream.read()


def skill_differs(source, dest):
    """True if dest's files don't exactly match source's, at any depth."""
    if not dest.exists():
        return True
    pending = [filecmp.dircmp(str(source), str(dest))]
    while pending:
        comparison = pending.pop()
        if (comparison.left_only or comparison.right_only
                or comparison.diff_files or comparison.funny_files):
            return True
        pending.extend(comparison.subdirs.values())
    return False


def plan(project, agents):
    """Work out every change before writing anything, so an error changes nothing."""
    skills, files = [], {}
    for agent in agents:
        _, skill_dir, resumes = AGENTS[agent]
        for source in SKILLS:
            dest = project / skill_dir / source.name
            check_target(dest, project)
            if (source, dest) not in skills:
                skills.append((source, dest))
        for mode, target in resumes:
            path = project / target
            check_target(path, project)
            if path not in files:
                files[path] = plan_hook(path, agent) if mode == "hook" else plan_line(path)
    if "claude" in agents:
        shared = project / ".claude/settings.json"
        check_target(shared, project)
        text = plan_unhook(shared)
        if text is not None:
            files[shared] = text
    return skills, files


def apply(skills, files):
    changes = []
    for source, dest in skills:
        status = "unchanged"
        if skill_differs(source, dest):
            status = "updated" if dest.exists() else "created"
            # Replace the whole folder so files removed upstream don't linger.
            # rmtree removes links inside dest without following them.
            if dest.exists():
                shutil.rmtree(str(dest))
            shutil.copytree(str(source), str(dest),
                            ignore=shutil.ignore_patterns("__pycache__"))
        changes.append((status, dest))
    for path, text in files.items():
        if text is None:
            changes.append(("unchanged", path))
            continue
        status = "updated" if path.exists() else "created"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as stream:
            stream.write(text)
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
    print("in other agents: \"Read .agents/skills/vibe-learn/SKILL.md and follow it.\"")
    print("Start over later with $vibe-learn-reset or /vibe-learn-reset.")
    if "codex" in agents:
        print("Codex will ask you to review and trust the new hook the first time it runs.")
    print("Suggested .gitignore lines (not added automatically):")
    print("  {}/".format(CLONE.relative_to(project)) if CLONE.parent == project else "  (your vibe-learn clone)")
    print("  .vibe-notes/")
    if "claude" in agents:
        print("  .claude/settings.local.json")
    if "codex" in agents:
        print("Note: .codex/hooks.json holds this clone's full path; on another computer, rerun setup.")
    print("Agents set up: {}".format(", ".join(names)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
