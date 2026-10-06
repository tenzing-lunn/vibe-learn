# Project-local learning notes

From the working directory, search upward for `.vibe-wise/`, or legacy
`.sensible-vibes/`, stopping at the nearest `.git` file or directory. At each
level prefer `.vibe-wise/`. Use the nearest existing state within that project.
Never borrow notes from a parent repository, another worktree, or the installed
skill. An invalid candidate is an issue to explain, not permission to fall back
to unrelated notes. Refuse symlinked state directories and note files.

If none exists and the user requested continuing learning, create `.vibe-wise/`
at the Git root (working directory without Git). A single explanation need not
create persistent notes. Show the notes location; recommend an ignore rule if
needed, without silently editing `.gitignore`. Do not publish these notes.

Discover files before reading them. If present, read `profile.md` and
`project-map.md`. Search all of `progress.md` for pending decisions and read their
full sections plus relevant topics. A short excerpt cannot establish that no
decision is pending. A restart or a stored proposal does not authorize coding.
Resolve old pending choices against the user's newest instructions.

Maintain only three Markdown files, using normal file tools:

- `profile.md`: `Learning mode: active` or `Learning mode: paused`, goals,
  preferences, and demonstrated/developing concepts. Record “Not specified”
  for unknown preferences rather than guessing a programming level.
- `progress.md`: short topic sections distinguishing concepts explained by the
  assistant, reasoning demonstrated by the learner, and topics to revisit.
  Record pending choices with their proposal and the actual reply needed;
  remove them when resolved. No pending section for already authorized work.
- `project-map.md`: purpose, requirements, components with supporting paths,
  a small data flow, verified commands, and unresolved questions. Distinguish
  proposed, chosen, and implemented behavior.

Update notes rather than append duplicate lessons. Recreate missing files from
evidence only. Preserve existing notes and legacy location. Do not reset or
migrate them as part of resuming; a reset is a separate user request.

These are editable Markdown records, not a service or a database. The skill
maintains them when loaded; no background process updates them.
