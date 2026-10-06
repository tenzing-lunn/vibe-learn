# VibeWise for Codex — first adaptation

A Codex learning skill adapted by Tenzing Lunn from
[VibeWise by Noah Kim](https://github.com/nykooi1/vibe-wise).

It helps you understand a real codebase as you work: explain terms in plain
language, trace data through actual files, discuss choices, and record concepts
you want to revisit. You can ask for more explanation, reason through a change,
or say “just implement this step.” Explicit instructions always set the pace.

## Try it

Without installing anything, tell Codex:

> Read the SKILL.md in this package's skills/vibe-wise-learn folder and use it
> to explain the part of my project we are about to change.

For repository-scoped installation, copy the **entire** `vibe-wise-learn` folder
into your project's `.agents/skills/`, without replacing an existing skill of
that name. Start a new Codex session and invoke `$vibe-wise-learn`.
For user-scoped installation, the documented location is `~/.agents/skills/`.
See [official skill documentation](https://learn.chatgpt.com/docs/build-skills).

`plugin.json` also packages the skill as a hook-free portable plugin using the
[official plugin structure](https://developers.openai.com/plugins/build/plugins).
Plugin installation through an actual Codex host has not been tested yet.

For continuing learning, local notes live in `.vibe-wise/` within the target
project. Keep that directory out of Git if it contains personal notes. There
is no telemetry, service, API key, or Python dependency in this adaptation.
The selected AI client still processes notes as ordinary conversation context.

## What changed from upstream

- Replaced Claude-specific commands and tool names with Codex skill discovery.
- Kept teaching, project maps, learner choices, and evidence-based local notes.
- Made discussion respect existing task authorization: learning does not add
  mandatory approvals to every implementation step.
- Excluded Claude's session-start hook and reset script. Resume explicitly with
  the skill; automatic restoration after session changes is not implemented.

This is a first draft, not a marketplace release. Structural checks do not
establish teaching quality. Try it on real work and adjust the pacing before
publishing a release.

## Attribution and publishing

Upstream source inspected: `c5fc8d813ce6789ebaf631ff4dd2a69658da3f31`
(plugin version 0.1.43). The original repository and files remain outside this
package. This package is intended to be distributable independently.

Preserve `LICENSE` and `NOTICE.md` when copying or publishing it. Describe your
release as an adaptation of VibeWise; the original is Noah Kim's work. This
package has not been published, and no GitHub destination has been configured.
