"""Run setup.py from a clone inside temporary projects, as a user would."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="vibe-learn-setup-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name).resolve() / "my app"
        self.project.mkdir()
        (self.project / ".git").mkdir()
        self.clone = self.make_clone("vibe-learn")

    def make_clone(self, name):
        clone = self.project / name
        clone.mkdir()
        shutil.copy(ROOT / "setup.py", clone)
        for skill in ("vibe-learn", "vibe-learn-reset"):
            shutil.copytree(ROOT / "skills" / skill, clone / "skills" / skill)
        (clone / "hooks").mkdir()
        shutil.copy(ROOT / "hooks/session_start.py", clone / "hooks")
        return clone

    def setup(self, *args, clone=None):
        return subprocess.run(
            [sys.executable, "-B", str((clone or self.clone) / "setup.py"), *args],
            capture_output=True, text=True, timeout=10, stdin=subprocess.DEVNULL,
        )

    def ok(self, *args, **kwargs):
        result = self.setup(*args, **kwargs)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def json(self, relative):
        return json.loads((self.project / relative).read_text())

    def commands(self, relative):
        return [hook["command"] for group in self.json(relative)["hooks"]["SessionStart"]
                for hook in group["hooks"]]

    def test_codex_gets_skill_and_hook_without_fork(self):
        self.ok("--agents", "codex")
        self.assertTrue((self.project / ".agents/skills/vibe-learn/SKILL.md").is_file())
        group = self.json(".codex/hooks.json")["hooks"]["SessionStart"][0]
        self.assertEqual(group["matcher"], "startup|resume|clear|compact")
        self.assertIn(str(self.clone / "hooks/session_start.py"), group["hooks"][0]["command"])

    def test_claude_gets_project_skill_and_settings_hook(self):
        self.ok("--agents", "claude")
        self.assertTrue((self.project / ".claude/skills/vibe-learn/SKILL.md").is_file())
        group = self.json(".claude/settings.json")["hooks"]["SessionStart"][0]
        self.assertIn("fork", group["matcher"])
        self.assertFalse((self.project / ".agents").exists())

    def test_hookless_agents_share_one_skill_and_get_marked_lines(self):
        self.ok("--agents", "gemini,other")
        self.assertTrue((self.project / ".agents/skills/vibe-learn/SKILL.md").is_file())
        for name in ("GEMINI.md", "AGENTS.md"):
            text = (self.project / name).read_text()
            self.assertEqual(text.count("<!-- vibe-learn:start -->"), 1)
            self.assertIn(".agents/skills/vibe-learn/SKILL.md", text)

    def test_rerun_changes_nothing(self):
        self.ok("--agents", "claude,codex,gemini,other")
        before = {p: p.read_bytes() for p in self.project.rglob("*")
                  if p.is_file() and self.clone not in p.parents}
        result = self.ok("--agents", "claude,codex,gemini,other")
        after = {p: p.read_bytes() for p in self.project.rglob("*")
                 if p.is_file() and self.clone not in p.parents}
        self.assertEqual(before, after)
        self.assertNotIn("created", result.stdout)
        self.assertNotIn("updated", result.stdout)

    def test_existing_settings_hooks_and_text_are_kept(self):
        (self.project / ".claude").mkdir()
        (self.project / ".claude/settings.json").write_text(json.dumps({
            "permissions": {"allow": ["Bash(ls)"]},
            "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo mine"}]}]},
        }))
        (self.project / "AGENTS.md").write_text("# House rules\nUse tabs.")
        self.ok("--agents", "claude,other")
        settings = self.json(".claude/settings.json")
        self.assertEqual(settings["permissions"], {"allow": ["Bash(ls)"]})
        self.assertIn("echo mine", self.commands(".claude/settings.json"))
        self.assertEqual(len(self.commands(".claude/settings.json")), 2)
        self.assertTrue((self.project / "AGENTS.md").read_text().startswith("# House rules\nUse tabs.\n"))

    def test_edited_line_is_replaced_not_duplicated(self):
        self.ok("--agents", "other")
        path = self.project / "AGENTS.md"
        path.write_text("Intro\n" + path.read_text().replace("resume", "RESUME") + "Outro\n")
        self.ok("--agents", "other")
        text = path.read_text()
        self.assertEqual(text.count("<!-- vibe-learn:start -->"), 1)
        self.assertNotIn("RESUME", text)
        self.assertTrue(text.startswith("Intro\n") and text.endswith("Outro\n"))

    def test_invalid_json_stops_before_any_change(self):
        (self.project / ".codex").mkdir()
        (self.project / ".codex/hooks.json").write_text("{not json")
        result = self.setup("--agents", "other,codex")
        self.assertEqual(result.returncode, 1)
        self.assertIn("not valid JSON", result.stderr)
        self.assertFalse((self.project / ".agents").exists())
        self.assertFalse((self.project / "AGENTS.md").exists())
        self.assertEqual((self.project / ".codex/hooks.json").read_text(), "{not json")

    def test_moved_clone_replaces_only_its_stale_hook(self):
        (self.project / ".codex").mkdir()
        (self.project / ".codex/hooks.json").write_text(json.dumps({"hooks": {"SessionStart": [
            {"hooks": [{"type": "command", "command": "python3 /tmp/other-tool/start.py"}]}]}}))
        self.ok("--agents", "codex")
        moved = self.project / "tools-vibe-learn"
        self.clone.rename(moved)
        self.ok("--agents", "codex", clone=moved)
        commands = self.commands(".codex/hooks.json")
        self.assertEqual(len(commands), 2)
        self.assertIn("python3 /tmp/other-tool/start.py", commands)
        self.assertTrue(any(str(moved / "hooks/session_start.py") in c for c in commands))

    def test_symlinked_target_is_refused(self):
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text("outside\n")
        (self.project / "AGENTS.md").symlink_to(outside)
        result = self.setup("--agents", "other")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(outside.read_text(), "outside\n")

    def test_unknown_agent_and_missing_choice_are_errors(self):
        self.assertIn("Unknown agents", self.setup("--agents", "notepad").stderr)
        self.assertIn("--agents", self.setup().stderr)
        self.assertEqual(list(self.project.iterdir()).count(self.project / ".agents"), 0)

    def test_both_skills_installed_with_codex_explicit_only_policy(self):
        self.ok("--agents", "codex,claude")
        for base in (".agents/skills", ".claude/skills"):
            for skill in ("vibe-learn", "vibe-learn-reset"):
                folder = self.project / base / skill
                self.assertTrue((folder / "SKILL.md").is_file())
                policy = (folder / "agents/openai.yaml").read_text()
                self.assertIn("allow_implicit_invocation: false", policy)

    def test_changed_nested_skill_file_is_updated(self):
        self.ok("--agents", "codex")
        policy = self.project / ".agents/skills/vibe-learn/agents/openai.yaml"
        policy.write_text("edited\n")
        self.assertIn("updated", self.ok("--agents", "codex").stdout)
        self.assertIn("allow_implicit_invocation", policy.read_text())

    def test_installed_reset_works_without_the_clone(self):
        self.ok("--agents", "other")
        state = self.project / ".vibe-notes"
        state.mkdir()
        (state / "profile.md").write_text("Learning mode: active\n")
        script = self.project / ".agents/skills/vibe-learn-reset/reset.py"
        shutil.rmtree(self.clone)
        result = subprocess.run([sys.executable, "-B", str(script), "--cwd", str(self.project)],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["state"], str(state))

    def test_installed_hook_restores_an_active_project(self):
        self.ok("--agents", "codex")
        state = self.project / ".vibe-notes"
        state.mkdir()
        (state / "profile.md").write_text("# Learner Profile\nLearning mode: active\n")
        command = self.commands(".codex/hooks.json")[0]
        result = subprocess.run(
            command, shell=True, text=True, capture_output=True, timeout=5,
            input=json.dumps({"hook_event_name": "SessionStart", "source": "startup",
                              "cwd": str(self.project)}),
            env={"PATH": os.pathsep.join((str(Path(sys.executable).parent), os.defpath))},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn(str(self.clone / "skills/vibe-learn/SKILL.md"), context)


if __name__ == "__main__":
    unittest.main()
