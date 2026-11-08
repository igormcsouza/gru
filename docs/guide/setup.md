# First run: the interview

The first time you run `/gru` in a project (and the first time with this version of Gru), it interviews you before it does anything else. Knowing the project and you is what makes the roles work the way you expect. It pre-fills what the repo already answers and asks only the rest.

1. **Models.** Gru works with three strengths: **strong** (thinks, plans, reviews), **mid** and **weak**. Defaults: Opus, Sonnet, Haiku. Stay or change.
2. **Harness for the minions.** "The default is Claude Code, but I suggest tether (recommended)." You can also choose opencode or another. If tether breaks on a card, Gru falls back to Claude Code for that card and offers to report the problem to the tether repo.
3. **Limits.** Any local model (a Qwen on your machine) or rate-limited provider (NVIDIA free tier)? Those run sequentially or throttled.
4. **The project.** Stack, check commands, e2e, branch and PR style, who merges, delivery mode, **what "done" means in your team**, risky areas, hard stops, design docs. Written to `AGENTS.md`/`CLAUDE.md`.
5. **You.** How you want to be asked, how much Gru may decide alone, verbosity, notifications. Written once per machine to `~/.config/gru/profile.yml`.

Then Gru offers a `selftest`. Redo it any time with `/gru setup`.

## Files

Two files in the [store](store.md), neither with secrets.

`<store>/local.yml` (**git-ignored**, yours): slots, harness, limits, sizes, prices, verified harnesses and [calibration](budget.md#calibration).

```yaml
version: 2
slots:
  strong: {model: opus,   harness: claude}
  mid:    {model: sonnet, harness: claude}
  weak:   {model: haiku,  harness: claude}
minion_harness: claude
size_slots: {XS: weak, S: weak, M: mid, L: strong, XL: strong}
limits:
  - {match: "tether:ollama/*", max_parallel: 1, kind: local}
  - {match: "tether:nvidia/*", max_parallel: 2, rpm: 40}
```

`<store>/gru.yml` (**versioned**, team policy):

```yaml
version: 2
tether_repo: igormcsouza/tether
budget: {warn_tokens: 300000, stop_tokens: 400000}
timeout_min: 10
max_parallel: 3
sensitive: [{path: "infra/**", min_slot: mid}]
permissions: {file_tether_issues: ask}
```

`~/.config/gru/profile.yml`: your working style (`autonomy`, `questions`, `verbosity`, `notify`) and machine specifics such as `claude_config_dir`.

An old `.claude/gru.json` is migrated: the tier ladder is dropped, the rest is kept.
