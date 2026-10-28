# Gru

**A strong model that thinks, plans and verifies, while free and cheap models do the typing.** Gru is a [Claude Code](https://claude.com/claude-code) skill (plain English, no framework) that turns a request into small, test-pinned task cards, hands them to "minion" models on other harnesses ([opencode](https://opencode.ai), [tether](https://github.com/igormcsouza/tether)), checks every result itself, and escalates tier by tier only on evidence.

[![License: MIT](https://img.shields.io/badge/License-MIT-f59e0b.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/Docs-igormcsouza.github.io%2Fgru-f59e0b)](https://igormcsouza.github.io/gru/)

```text
/gru add rate limiting to the public API
```

---

## Why Gru?

Running the biggest model on every keystroke is the most expensive way to ship code. Most of a feature is typing against a clear spec, and cheap models can type if the spec is tight and someone checks the work. Gru is that someone.

- **Grill first.** Gru reads your repo docs, then asks sharp questions (each with a recommendation) until scope is tight. It may tell you "don't build this".
- **Tests before typing.** The strong model writes the failing acceptance tests; minions only make them pass. Gru verifies the tests are byte-identical and the diff only touches owned files.
- **Cost ladder.** Tier 0 free models, tier 1 Haiku, tier 2 Sonnet. Tier 3 (Opus/Fable) never without your explicit OK, each time.
- **Escalate on evidence.** A failed check retries once with the exact failure; a second failure, a stall or a rate limit moves the task up one tier.
- **Sandboxed minions.** opencode runs in bubblewrap with `$HOME` hidden and only the task's worktree writable. No `bwrap`, no run.
- **Budget aware.** Paid tokens, wall-clock and escalations are tracked against caps you approve in the plan preview.
- **Remembers.** A cross-session log per feature (`resume`, `status`, `done`) that survives closed terminals.

## Commands

```text
/gru <request>   # grill, plan, then run minions; starts a logged feature
/gru resume      # pick up an unfinished feature and re-attach its minions
/gru status      # tasks, tiers, spend vs budget
/gru selftest    # prove each harness and model works here (a few cents)
/gru done        # wrap up, clean worktrees and processes, archive the log
```

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/igormcsouza/gru/main/install.sh | bash
```

The installer asks where to put Gru (Claude Code, Codex, both, or your own folders), clones to `~/.gru`, and symlinks the skill and the dev-team agents. For Claude Code it also installs/upgrades [tether](https://pypi.org/project/tether-sdk/) with `uv`, adds an `nvidia` provider and registers the `tether` MCP server (export `NVIDIA_API_KEY`; it is never printed). Run it again to update. Then start a new session and run `/gru selftest` once. Details: [docs](https://igormcsouza.github.io/gru/getting-started/install/).

## What is in the box

```text
skills/gru/    SKILL.md (the program) and sandbox.sh (bubblewrap wrapper for opencode)
agents/        team-leader, architect, swe, qa, reviewer: the dev team Gru acts through
docs/          the mkdocs site
```

The dev-team agents also work alone: `claude --agent team-leader` runs the same idea -> architect -> swe -> qa/reviewer -> merge flow with Claude subagents.

Project specifics (stack, check commands, branch style, who merges) are never in this repo. Gru asks once and writes them into your project's `AGENTS.md`/`CLAUDE.md`.

## Contributing

Gru is a prompt plus a shell script: improving a sentence in `SKILL.md` is a code change. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) © 2026 Igor Souza
