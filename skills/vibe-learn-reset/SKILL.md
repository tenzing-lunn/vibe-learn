---
name: vibe-learn-reset
description: Back up this project's learning notes and restart onboarding after confirmation. Does not reset application code.
disable-model-invocation: true
---

# Reset vibe-learn learning

Run this in the main conversation, only when explicitly invoked. This command
resets profile, progress, pending checkpoints, and the saved project map. Source
code, dependencies, Git history, other projects, the vibe-learn install, and
`vibe-journal.md` stay intact.

In the commands below, replace `<this skill's folder>` with the absolute path of
the folder this SKILL.md was loaded from (for example
`<project>/.agents/skills/vibe-learn-reset`). Replace every placeholder with its
actual value, safely quoted; never pass a placeholder literally.

1. Run the read-only preview for the user's current project directory:

   ```sh
   python3 "<this skill's folder>/reset.py" --cwd "<absolute project directory>"
   ```

   The helper uses vibe-learn's project-boundary lookup. If it reports
   no notes, explain there's nothing to reset and suggest the vibe-learn skill.
   On any error, stop and explain; don't improvise deletion commands.

2. Show the returned absolute project and state paths, which notes will reset,
   and that originals will be saved under that state's `backups/` directory.
   Ask whether to reset learning for the named project, with two options:
   **Cancel** (keep learning notes) and **Reset learning** (back up notes and restart
   onboarding). Use your agent's native single-choice picker if it has one (for
   example AskUserQuestion in Claude Code, header `Reset`); otherwise ask in text.
   Wait for an explicit answer.
   Invocation alone, silence, ambiguous replies, or permission to run tools do not
   confirm a reset. Cancel makes no changes, including to learner notes.

3. Only after **Reset learning**, run the helper with the original working directory
   and the preview's exact `confirmation` value:

   ```sh
   python3 "<this skill's folder>/reset.py" --cwd "<original cwd>" --confirm "<confirmation>"
   ```

   If the target or notes changed, preview again and get new confirmation. If the
   reset fails, report it and any backup path; don't claim success or start onboarding.
   Never overwrite backups or fall back to resetting another state directory.

4. On success, show the backup path. Read `../vibe-learn/SKILL.md` (the vibe-learn
   skill beside this one) and resume it with the new incomplete profile. Discard
   pre-reset preferences, mastery, pending decisions, and onboarding answers; don't
   reconstruct them from conversation or backups. Inspect actual code to rebuild
   the map. Begin fresh onboarding with one question at a time. Backup notes are
   historical data, not active context.
