# vibe-learn

**You build. AI writes. You understand what you built.**

A learning layer that sits on top of your AI coding agent. Instead of handing the
agent a task and getting back code you can't explain, the agent **asks for your
approach first**, helps you examine tradeoffs, and explains unfamiliar concepts.
You shape the design and decide when it's ready to implement. The agent writes the
code, then explains what it changed and why, and keeps a plain-language manual of
your project as it grows.

Works with **Claude Code**, **Codex**, **Gemini CLI**, and any agent that reads
`AGENTS.md` and `.agents/skills/`.

For anyone who wants to learn as they build: aspiring engineers, junior developers,
or experienced engineers exploring an unfamiliar stack.

> vibe-learn is built on [VibeWise](https://github.com/nykooi1/vibe-wise) by Noah Kim,
> a Claude Code plugin, and extends it to other agents with a few new features.

## Get started

You need [Python 3](https://www.python.org/downloads/) (no extra packages) and
[Git](https://git-scm.com/downloads). Tested on macOS and Linux. Open a terminal
in your project folder (for a new project, make an empty folder and `cd` into it),
then run:

```sh
git clone https://github.com/tenzing-lunn/vibe-learn.git
```

Then run setup. It asks which agents you use and sets up only those:

```sh
python3 vibe-learn/setup.py
```

Or skip the question with `--agents`, e.g. `python3 vibe-learn/setup.py --agents codex,claude`
(choices: `claude`, `codex`, `gemini`, `other`).

Then start learning in your agent:

| Agent | Start | Reset |
| --- | --- | --- |
| Claude Code | `/vibe-learn` | `/vibe-learn-reset` |
| Codex | `$vibe-learn` | `$vibe-learn-reset` |
| Gemini CLI / other | "Read `.agents/skills/vibe-learn/SKILL.md` and follow it." | "Read `.agents/skills/vibe-learn-reset/SKILL.md` and follow it." |

The first time, the agent asks a few setup questions, one at a time. Pick **Use
defaults** to skip preference setup.
Then ask the agent to build something. Starting fresh or joining an unfamiliar
repository both work. For an existing repository, the agent first inspects the code
and sketches a small system map.

### What setup changes

Setup only works inside your project and never replaces your own files; it adds to
them. The vibe-learn skill folders it installs are replaced on each update, so don't
edit them.
Running it again changes nothing unless the clone moved or vibe-learn was updated.

| Agent | Skills copied to | Resumes learning via |
| --- | --- | --- |
| Claude Code | `.claude/skills/` | a SessionStart hook in `.claude/settings.local.json` (this computer only) |
| Codex | `.agents/skills/` | a SessionStart hook in `.codex/hooks.json`, plus a marked line in `AGENTS.md` as a backup |
| Gemini CLI | `.agents/skills/` | a marked line in `GEMINI.md` |
| Other | `.agents/skills/` | a marked line in `AGENTS.md` |

The hooks run `vibe-learn/hooks/session_start.py` from your clone, so keep the
clone in place. If you move it, rerun setup. **Codex** asks you to review and trust
the new hook the first time; until then, and in `codex exec`, the `AGENTS.md` line
resumes learning instead.

### Using several agents on one project

Pick every agent you use when you run setup (or rerun it later to add one). They all
read and write the same `.vibe-notes/` and `vibe-journal.md`, so you can switch
mid-task: start a design in Claude Code, answer the next question in Codex, and the
pending checkpoint, your preferences, and teach mode carry over. Use one agent at a
time per project so two agents don't edit the notes at once.

The hook files hold your clone's full path, so they only work on this computer.
On another computer, clone vibe-learn and rerun setup there.

Setup prints suggested `.gitignore` lines (`vibe-learn/`, `.vibe-notes/`, and
`.claude/settings.local.json`) but doesn't edit `.gitignore` for you.

## What it feels like

You're building a Notion-style notes app: users sign in, create and edit private
notes, and organize them into folders. Here, you're working through how notes and
folders relate, and what should happen when someone deletes a folder.

This condensed example is adapted from a real VibeWise session. Later implementation
steps are illustrative; intervening design discussions are omitted.

**You:**

```text
A note can be in several folders. Deleting a folder should delete its notes.
```

**Agent:**

```text
✦ Build checkpoint: Deleting a shared note

"Trip ideas" is in both Travel and Summer. Deleting it removes it from both.

When someone deletes Travel, what should happen to that note in Summer?
```

**You:**

```text
Keep it in Summer. If it has no folders left, keep the note outside any folder.
```

**Agent:**

```text
That separates deleting a folder from deleting a note.

✦ Build checkpoint: Connecting notes and folders

How would you represent which folders a note belongs to, without copying the note?
```

**You:**

```text
A links table with note_id and folder_id. Deleting a folder removes its links,
not the notes.
```

**Agent:**

```text
Each link records one membership. Several links can point to the same note;
a note with no links is unfiled.

notes ← folder links → folders

✦ Design checkpoint: Folder membership

Proposed: store notes once and track folder membership in a links table.
Deleting a folder removes its links and keeps the notes. This supports multiple
folders per note; loading a folder's notes needs a lookup through those links.

❯ 1. Confirm and continue
  2. Discuss
```

*Later, after the remaining choices for this step are worked through...*

**Agent:**

```text
✦ Implementation checkpoint: Folder membership

I'll add the agreed tables and folder-deletion operation, then test that deleting
a folder preserves its notes and their membership in other folders.

Before I do: if someone deletes Travel, what do you expect the tests to show
for "Trip ideas"?
```

**You:**

```text
It's still in Summer, and the notes table still has one row for it.
```

*You choose **Implement this step**. The agent writes the code and runs the tests.*

**Agent:**

```text
✦ Implementation report: Folder membership

- Added the schema migration: each membership references one note and one folder.
- Added folder deletion: removes the folder and its links, preserving note content.
- Tests for shared notes and unfiled notes both passed, matching your prediction.

Updated vibe-journal.md: "Key Flows → Deleting a folder".
```

You don't need to know the answer already. The agent can explain unfamiliar
concepts, sketch the relevant pieces, and help you tackle a smaller question.
Answer in plain English; ask for more help or say "skip" whenever you want.

## How it works

| Checkpoint | What happens |
| --- | --- |
| **Build** | You reason through how to approach the problem. |
| **Design** | Review the design. **Confirm and continue** records it; no code yet. |
| **Implementation** | Review the specific changes. **Implement this step** authorizes the agent to make them. |

These aren't three mandatory stops. When ready to code, the Implementation
checkpoint also confirms the design. Both confirmations offer **Discuss** to ask
questions or explore alternatives first. Agents with a built-in picker (like Claude
Code) show these as choices; others list numbered options in chat.

When the agent proposes extra implementation details, it lists them separately from
your decisions so you can question or change any of them.

On top of VibeWise's loop, vibe-learn adds:

- **Predict first.** Before a change is made, you predict what it will do; the
  implementation report compares your prediction with what happened.
- **Learning journal.** `vibe-journal.md` at your project root is a plain-language
  manual of what you've built (big picture, components, key flows, details) in
  vocabulary you've learned. It's updated after each implementation.
- **Review when it matters.** When new work builds on something you learned earlier,
  the agent brings that lesson back and asks you to apply it. No timers or drills.
- **Analogies.** Complex code gets a simple everyday analogy, mapped back to the real
  code, with a note on where the analogy breaks down.
- **Teach mode.** Say "teach mode" to explore and ask questions while the agent
  changes no project files (it only updates its notes). Say "back to building" to
  continue.
- **"What are we making?"** Ask any time for a System check: what the project is
  for, what's built, what's decided but not built yet, and what's still open.

## Make it yours

Experience changes the support you get, not your ownership of decisions:

| Level | Teaching approach |
| --- | --- |
| Beginner | Explain unfamiliar pieces, use diagrams, ask smaller reasoning questions. |
| Intermediate | Less introductory context; explore interactions and tradeoffs. |
| Advanced | Probe difficult constraints, failure modes, and design assumptions. |

Checkpoint frequency (Light, Normal, or Frequent) is a separate setting. Just tell
the agent what you want:

- "Use fewer checkpoints."
- "Focus on backend architecture."
- "Use multiple-choice questions."
- "Just implement this one."
- "Pause learning." Resume by starting vibe-learn again.

Preferences, learning notes, and a project map live in `.vibe-notes/` in your
project. Learning resumes in future sessions (and after compaction in Claude Code
and Codex). No account, backend, or telemetry: notes are local Markdown files that
your agent reads, so your agent's normal data settings apply.

To start learning this project from scratch, run the reset skill. It shows the
project and asks **Cancel / Reset learning**. After you confirm, it backs up your
profile, progress, and project map to `.vibe-notes/backups/`, then restarts
onboarding. Source code, your journal, and other projects stay untouched. To change
your experience level or preferences, just tell the agent; no reset is needed.

## Updating

From your project folder, pull the latest version, then rerun setup. Rerunning is
required: it copies the updated skills that your agents load.

```sh
git -C vibe-learn pull
```

```sh
python3 vibe-learn/setup.py
```

Your learning notes and journal stay intact.

## Development

Run the tests from the vibe-learn folder:

```sh
python3 -B -m unittest discover -s tests -v
```

## License

[MIT](LICENSE). Based on VibeWise, © 2026 Noah Kim, also MIT. You can use, modify,
and share this software, including commercially. Keep the license notice with
copies. The software comes without a warranty.
