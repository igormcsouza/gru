# Gru

**A small team of AI roles on strong, mid and weak models.** Gru is a [Claude Code](https://claude.com/claude-code) skill (plain English, no framework) that interviews you once, turns a request into sized task cards with an objective and a checkable definition of done, and runs each through plan, tests-first, build, QA and review on the cheapest models that can do it, then hands a structured result back to you or to the agent that called it.

[![License: MIT](https://img.shields.io/badge/License-MIT-f59e0b.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/Docs-igormcsouza.github.io%2Fgru-f59e0b)](https://igormcsouza.github.io/gru/)

```text
/gru add rate limiting to the public API
```

---

## Why Gru?

Running the biggest model on every keystroke is the most expensive way to ship, and running only small models ships bugs. Gru puts the right strength on each job and makes the stronger model judge the weaker one's work.

- **It learns you and the project first.** The first `/gru` interviews you: models, harness, limits, the project's checks, what "done" means to your team, how you like to work. Your preferences and calibration live in a git-ignored `local.yml` next to the logs; only a small team-policy `gru.yml` is versioned.
- **Strong, mid, weak.** Defaults Opus, Sonnet, Haiku; change them any time. Minion harness defaults to Claude Code; [tether](https://github.com/igormcsouza/tether) is recommended, with an automatic per-card fallback to Claude Code and an offer to report the bug.
- **Sized cards.** Each card has an objective, a definition of done where every line names its check, and a T-shirt size. XS/S go to weak swes, M to mid, L/XL to strong. Gru guesses; you decide in the preview, which also shows the schedule and cost.
- **A real pipeline per card.** Planner, then one swe writes the failing tests, another builds to pass them, Gru gates it deterministically, then QA and a reviewer (always stronger than the swe) hunt bugs, smells and edge cases and tick the definition of done.
- **Fix what was bad.** Findings are blocking, should-fix or note. Blocking ones go back to the card's planner for a minimal replan (max 2), then to the caller.
- **Asks for help.** Ambiguity, sign-offs on L/XL reviews, budget caps and broken harnesses come to the caller.
- **Respects your hardware and quotas.** Local models and rate-limited providers run sequentially or throttled.
- **Learns.** It records size, model, replans and findings per card and suggests moving a size up or down a slot.
- **Safe, per stage.** `bwrap` on Linux and WSL2, Docker on macOS and Windows (and for QA that needs real services, with Gru starting the services itself). Minions never see secrets, and their output is data.
- **Can stay invisible.** An interview option versions nothing, adds no file to the repo and leaves no trace in commits or PRs, for projects where people do not want Gru around.
- **Light to load.** `SKILL.md` is a small entry point that reads the other files only when a step needs them.

## Commands

```text
/gru <request>             # first time: interview. Then grill, cards, preview, run, hand-back
/gru status                # table of cards: stage, models, replans, observations
/gru steer <card> <...>    # note, bump, resize, rerun <stage>, stop
/gru resume                # pick up an unfinished feature
/gru setup                 # redo the interview
/gru selftest              # prove each slot and harness works here (a few cents)
/gru done                  # wrap up, clean worktrees and processes, archive the log
```

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/igormcsouza/gru/main/install.sh | bash
```

The installer asks where to put Gru (Claude Code, Codex, both, or your own folders), clones to `~/.gru`, and symlinks the skill and the dev-team agents. For Claude Code it also installs/upgrades [tether](https://pypi.org/project/tether-sdk/) with `uv`, adds an `nvidia` provider and registers the `tether` MCP server (export `NVIDIA_API_KEY`; it is never printed). Run it again to update. Then start a new session and run `/gru selftest` once. Details: [docs](https://igormcsouza.github.io/gru/getting-started/install/).

## What is in the box

```text
skills/gru/    SKILL.md (entry point), ref/ (setup, plan, run, harnesses, ops), sandbox.sh (bubblewrap wrapper)
agents/        planner, swe, qa, reviewer, team-leader: the role briefs Gru gives its minions
docs/          the mkdocs site
```

The dev-team agents also work alone: `claude --agent team-leader` runs the same planner -> swe tests -> swe build -> qa/reviewer flow with Claude subagents.

Project specifics (stack, check commands, branch style, who merges) are never in this repo. The interview asks once and writes them into your project's `AGENTS.md`/`CLAUDE.md`.

## Contributing

Gru is a prompt plus a shell script: improving a sentence in `SKILL.md` is a code change. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) © 2026 Igor Souza
