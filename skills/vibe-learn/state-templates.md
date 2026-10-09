# Local state templates

Create only these three files in the chosen project's `.vibe-notes/`, plus
`vibe-journal.md` beside that folder (the project root) after the first
Implementation report. Use the directory selected by SKILL.md.
Replace bracketed values with actual evidence or “Not specified.” Keep the status
lines unformatted and near the top; the restoration hook reads `Learning mode`.
Do not replace existing state with a fresh template.

## profile.md

```markdown
# Learner Profile

Learning mode: active
Onboarding: complete
Teach mode: off

## Project
Situation: [New / Existing / Known]
Building: [project purpose]
Codebase familiarity: [answer]
Learning scope: [entire system / parts we touch / mixed]

## Experience
Overall programming: [Beginner / Intermediate / Advanced, or Not specified]
Stack familiarity: [per-technology levels if given; otherwise Not specified]

## Goals
Primary: [answer]
Capability goal: [optional answer]

## Preferences
Checkpoint frequency: Normal
Question style: Open-ended
Implementation style: AI writes code
Journal: on

## Strong Concepts
No demonstrated understanding recorded yet.

## Developing Concepts
None recorded yet.

## Revisit
None recorded yet.
```

## progress.md

```markdown
# Learning Progress

No learning events recorded yet.
```

Rules for adding to progress.md are in behavior.md under Preserve evidence.

## project-map.md

```markdown
# Project Map

## Purpose
[What this software does.]

## Requirements
[User needs and constraints. These do not automatically settle technical choices.]

## Components
[Components, responsibilities, and supporting file paths.]

## Main Flow
[Compact text diagram with labeled arrows. Mark unknowns and distinguish proposed,
chosen, and implemented components. Reflect the learner's model refined together,
or verified existing code; don't fill missing relationships with assumed designs.]

## Data and Trust Boundaries
[Storage, ownership, auth, external services; unknown when unverified.]

## Build and Deployment
[Commands and configuration paths verified in the repository.]

## Unknowns
[Unresolved technical choices and what needs inspection, including relevant stack,
storage location/model, data structures, interfaces, and deployment choices.]
```

## vibe-journal.md

```markdown
# [Project name] Journal

A plain-language manual of what we've built, written with the words you've learned.

## Big Picture
[What the software does and its main parts, in a few sentences.]

## Components
[Each part: what it's responsible for, where it lives, what it talks to.]

## Key Flows
[Step-by-step walk-throughs of the important paths, e.g. "When a user saves a note…".]

## Details
[Mechanisms worth remembering, linked to the concepts behind them.]
```

Write the journal for the learner, not for the agent: use vocabulary they've been
taught or demonstrated, define anything new in a phrase, and keep an analogy where
one helped. Describe only implemented code, not plans; plans stay in project-map.md.
Revise sections in place so it reads as a current manual, not a changelog.
