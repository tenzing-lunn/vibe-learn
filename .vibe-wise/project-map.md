# Project Map

## Purpose
Turn Noah Kim's VibeWise (a Claude Code plugin for learning while AI writes the
code) into a framework anyone can use with any AI coding agent.

## Requirements
- Works for people using any AI coding agent, including people who don't use Claude.
- Installed by cloning or copying it into the user's own project.
- Helps the user learn as they build, following VibeWise's learning loop.
- Parity: provide everything VibeWise does today, or an improved version, possibly more.
- Default to Noah's approach; change it only when a better way is agreed.
- As simple as possible, following each agent's own conventions (Codex first).
- Combine the best ideas from other learning tools (socratic-builder, socratic-skills,
  socrates-skill, jish0desarkar/agent-skills, Frontend Mentor AGENTS.md) into one
  multi-agent tool built on VibeWise. Learner's picks (proposed, not confirmed):
  mentoring questions, build checkpoints, a learning journal for understanding what
  was built, simple analogies for complex code, and a teach mode that never edits
  files. Extras Claude suggested, not chosen: spaced review, predict-first, quiz-me.
  Feature design CONFIRMED 2026-10-07 (not implemented), including the additions below:
  - Review: old lessons resurface when new learning builds on them (relevance, not timer).
  - Predict-first: learner predicts what a change will do before seeing it.
  - Nothing hand-written: the learner chooses architecture, system design, and API
    design; the AI writes all code (Noah's model). Writing code by hand: not chosen.
  - Journal: AI-written Markdown manual alongside project-map.md, easier to read,
    explaining the codebase at several levels of abstraction using vocabulary the
    learner has learned; quoted when past lessons come up.
  - Quiz-me: not chosen.
  - Simple analogies for complex code; teach mode that explains and never edits files.
  - Additions (proposed by Claude, confirmed by learner): `.vibe-wise/journal.md`;
    update after each Implementation report; levels big picture → components →
    key flows → details; "teach mode"/"back to building"; predict-first follows
    checkpoint frequency. Copying their
  text or code must follow each license (only socratic-builder confirmed MIT).
- Published on GitHub as the learner's own skill.
- License constraint: copies must keep Noah Kim's MIT copyright and permission notice.
- Aim for every coding agent (learner named Codex, Gemini, DeepSeek, Claude): "a
  harness that sits on top of your agent to help you understand what you're building."
  Note: DeepSeek is a model; support comes via the agent running it.

Agent facts (searched 2026-10-07; Gemini/Deep Code from docs mirrors and reviews):
- Gemini CLI: skills in `.gemini/skills/` or `.agents/skills/`; SessionStart hook
  (startup|resume|clear) in `.gemini/settings.json`, experimental, off by default.
- Deep Code CLI (community, DeepSeek-optimized): skills in `.agents/skills/`; no hooks found.
- `.agents/skills/` is shared by Codex, Gemini CLI, and Deep Code.
- Always-read instruction files: Codex `AGENTS.md`, Claude Code `CLAUDE.md`, Gemini
  CLI `GEMINI.md`; Cursor and Deep Code not checked.
- Requirement: in any agent, a returning user picks up where they left off (learner:
  "from the journal"); resume state is in progress.md, journal is the readable manual.

## Components
Current code (verified; upstream VibeWise 0.1.43, packaged as a Claude Code plugin):
- (Removed 2026-10-07, commit 2ec0cd9: `.claude-plugin/`, `codex/`, `assets/` icon, `docs/demos/`.)
- `setup.py` (implemented b687c0c): asks for agents or takes `--agents`; installs into
  the clone's parent folder; per-agent skill copy + hook or marked instruction line.
- `skills/vibe-learn/` (renamed from skills/learn; content still Noah's, Claude-specific
  wording): SKILL.md entry, behavior.md, onboarding.md, state-templates.md.
- `hooks/session_start.py`: restore instructions, now pointing at skills/vibe-learn/SKILL.md;
  `hooks/hooks.json` kept only for tests.
- `skills/vibe-learn-reset/`: Noah's reset (still uses ${CLAUDE_PLUGIN_ROOT}; not installed by setup.py yet).
- `tests/`: 48 tests (hook, reset, setup).

Claude Code-specific (verified): `.claude-plugin/` manifest, `/vibe-wise:*` commands,
the `AskUserQuestion` picker, `hooks/hooks.json` and `${CLAUDE_PLUGIN_ROOT}`.
Portable: the Markdown guides' rules, `.vibe-wise/` notes, and the Python scripts.

New framework (proposed by learner, not confirmed or implemented):
- Codex: a `$` skill starts learning; a SessionStart hook restores it each session.
- Delivery plan CONFIRMED 2026-10-07 (not implemented):
  - Clone into project, run `setup.py`; it asks which agents the user uses and sets
    up only those. Project scope only (learning is opt-in per project). Never
    overwrite user files; add to them.
  - Agents with startup hooks (Codex, Claude Code): skill + Noah's hook.
  - Hookless agents: skill + a short line in the project's always-read file.
  - Additions: v1 agents Claude Code, Codex, Gemini CLI, plus "Other agent"
    (`.agents/skills/` + `AGENTS.md` line); Claude Code via project `.claude/skills/`
    and `.claude/settings.json` hook; Gemini via `GEMINI.md` line, not its
    experimental hook; idempotent reruns; print changed files and suggest
    `.gitignore` lines without editing.
  - Name: `vibe-learn` (learner chose 2026-10-07): `$vibe-learn`, `/vibe-learn`,
    cloned folder `vibe-learn/`. Local folder still `vibelearning`.
  - Open: notes folder name (`.vibe-learn/` vs `.vibe-wise/`); README rewrite (now outdated, broken icon link).

Codex facts (verified in OpenAI docs, 2026-10-07):
- Skills: `.agents/skills/` from the starting directory up to the repo root, or
  `~/.agents/skills/`; invoked with `$name`. `agents/openai.yaml` with
  `allow_implicit_invocation: false` makes a skill explicit-only.
- Hooks: `<repo>/.codex/hooks.json`, `~/.codex/hooks.json`, or a plugin
  (`.codex-plugin/plugin.json`, `PLUGIN_ROOT`). Same JSON shape as Claude Code;
  SessionStart sources startup|resume|clear|compact; stdin includes `cwd`;
  stdout `hookSpecificOutput.additionalContext` or plain text. Project hooks run
  only after the user trusts the project's `.codex/` layer and reviews the hook.

## Main Flow
Current (verified):

    /vibe-wise:learn → skills/learn/SKILL.md → onboarding.md (first time) → behavior.md
                     ↔ .vibe-wise/ profile.md · progress.md · project-map.md
    session start / clear / compact → hooks.json → session_start.py → "re-read guide + notes"
    /vibe-wise:reset → reset.py (preview → confirm → backup → fresh notes)

New framework: ? (not designed yet)

## Data and Trust Boundaries
Notes are local Markdown in `.vibe-wise/` at the project's Git root. No backend,
accounts, or telemetry. The agent reads notes as context and treats them as data,
not instructions.

## Build and Deployment
- `python3 -B -m unittest discover -s tests -v`: 48 tests passed on 2026-10-07.
- Codex 0.161.0 real check (2026-10-07): skill discovered; after persisted folder +
  hook trust, the project SessionStart hook runs on the first user message in
  interactive Codex. Not on open; not in `codex exec` with one-run overrides.
- `claude plugin validate ...` commands are documented in `docs/development.md`; not run.
- The learner's Claude Code has Noah's published VibeWise 0.1.43 installed from the
  `nykooi1/vibe-wise` GitHub marketplace (user scope, 2026-10-07); it is separate
  from this working copy.
- Git remote `origin` is github.com/nykooi1/vibe-wise (Noah's repo). The learner's own GitHub destination is not configured.

## Prior Art
- Upstream VibeWise (origin/main, checked 2026-10-07): no commits beyond this copy;
  Claude Code only, no support for other agents.
- Web search 2026-10-07 (not exhaustive): most learning skills are Claude Code-only
  (socratic-builder: has journal + session hook; socratic-skills; socrates-skill,
  328 stars). Closest cross-agent: jish0desarkar/agent-skills (Claude Code, Codex,
  Cursor; approval checkpoints; 1 star; no learning notes or session restore).
  Frontend Mentor ships per-challenge AGENTS.md mentoring files (not general).
  No found tool combines cross-agent + learner-owned design + AI writes code +
  persistent notes + automatic restore.
- Paths open to the learner: own project (MIT allows) or contributing upstream.

## Unknowns
- How one framework gets picked up and followed by different agents.
- Which agents to support, and what each one provides.
- How learning mode resumes in later sessions for each agent.
- What happens to the existing Claude plugin files and `codex/`.
- Project name: folder renamed to `vibelearning`; files still say VibeWise.
