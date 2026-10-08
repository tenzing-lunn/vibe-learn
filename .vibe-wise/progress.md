# Learning Progress

## How agents find their instructions
- Introduced (Claude explained): the agent program decides which files it reads,
  which commands exist, and which tools the model gets. Claude Code-specific pieces
  in this repo: `.claude-plugin/plugin.json`, `/plugin:skill` commands, the
  `AskUserQuestion` picker, and `hooks/hooks.json` with `${CLAUDE_PLUGIN_ROOT}`.
  Codex fact: skills live in `.agents/skills/` and are invoked with `$name`.
- Learner reasoning: expected Codex to behave the same unless something is specific
  to Claude Code; didn't yet know which parts are.
- Learner skipped the sorting exercise ("help me start building"). Claude gave the
  answer: steps 1, 6, the step 3 picker, and the reset command need Claude Code;
  steps 2, 4, 5, the onboarding questions, and the Python scripts are portable.
  Not demonstrated by the learner.
- Needs reinforcement: which parts are portable versus Claude Code-specific.

## Delivering VibeWise in Codex
- Learner reasoning: proposed mirroring Noah's delivery with Codex equivalents: a
  `$` skill to start learning and a SessionStart hook to restore it; as simple as
  possible, following Codex conventions. Proposed, not yet confirmed.
- Introduced (Claude explained): Codex's hook format nearly matches Claude Code's,
  so Noah's hook script is mostly reusable; where Codex looks for skills and hooks;
  project hooks need user trust.

## Choosing the tool's features
- Learner picked ideas from other tools: mentoring questions, build checkpoints,
  a learning journal, simple analogies, teach mode without edits; later added
  predict-first and relevance-based review from Claude's suggestions.
- Learner reasoning: old lessons should resurface when they compound into new
  learning; the journal is a rereadable manual explaining the codebase at several
  levels of abstraction, AI-written in vocabulary the learner has learned, sitting
  alongside project-map. Corrected Claude: nothing is hand-written; the learner
  chooses architecture, system design, and API design.
- Confirmed 2026-10-07 (Design checkpoint, Confirm and continue): the feature set
  and Claude's five proposed additions (see map). Confirmation is readiness, not
  demonstrated understanding.

## Cleaning up Noah's packaging
- Learner decided to remove pieces not needed for the tool ("old brainstorming").
- Implemented 2026-10-07 (commit 2ec0cd9): removed `.claude-plugin/`, `codex/`,
  `assets/vibewise-icon.png`, `docs/demos/notion-dupe.md`. Kept hooks.json for tests.
  37 tests passed after removal.

## Naming
- Learner chose `vibe-learn` (2026-10-07) after reviewing Greek alternatives
  (maieutic, mathesis, tekton, episteme, anamnesis, kairos, and others).

## Pending decision
Decision: Build order (Build checkpoint)
Stage: awaiting reasoning
Asked: order for (a) adapting the skill (rename, remove Claude-only instructions),
(b) adding new features to the teaching rules, (c) writing setup.py, and why,
considering dependencies.
Also open for later: notes folder `.vibe-learn/` vs `.vibe-wise/`, and legacy reading.
Learner asked to be taught. Claude explained dependencies and building a thin
end-to-end slice first, plus facts: setup.py copies the skill (needs its final name
and layout); adapting the skill sets those; features mostly change guide content.
Learner chose order: setup first, then adapting the skill, then new features.
Claude flagged that setup depends on the skill's final layout; resolved by renaming
folders within the setup step and deferring content changes.
Implemented 2026-10-07 (commit b687c0c): folders renamed; setup.py; tests/test_setup.py
(11 tests); 48 tests pass. Real Codex 0.161.0 check in a throwaway project: skill
`vibe-learn` discovered; SessionStart hook did NOT run under `codex exec`, even with
--dangerously-bypass-hook-trust and a one-run project-trust override. Cause unknown
(exec mode vs. persisted project trust). Next: interactive check by the learner.

## Pending decision
Decision: Adapt the skill content (next build step; not yet asked)
Codex interactive check passed 2026-10-07: after the learner trusted the folder and
the hook via Codex's own prompts, the SessionStart hook ran on the first message
(marker at 22:12) and Codex read the guide and notes. Not run on open; not run in
`codex exec` with one-run overrides. Codex used its own commands where Noah's guide
says "Read tool" (wording to make agent-neutral). Throwaway folder remains trusted
in ~/.codex/config.toml; offered to remove.
