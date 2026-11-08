# Logs and store

Each feature has a Markdown log, `active/<slug>.md` while open and `archive/<slug>.md` after `done`, with a folder of its [cards](task-cards.md), plans and `handback.md`. Entries are append-only, newest last, timestamped, written at each checkpoint (request, decision, stage change, findings, replan, steer, escalation, tether friction, PR) and before a session may end. No secrets, ever.

```text
<store>/.gitignore                   ignores everything except itself and gru.yml
<store>/gru.yml                      team policy (the only versioned file)
<store>/local.yml                    your models, harness, limits, calibration (ignored)
<store>/active/<slug>.md             feature log
<store>/active/<slug>/cards/         <id>.md, <id>.plan.md
<store>/active/<slug>/handback.md    result for the caller
<store>/archive/                     the same, after done
```

## Where it lives

Resolved once per session, first match wins:

1. a path named by a `gru store:` (or legacy `feature-context store:`) line in `AGENTS.md`/`CLAUDE.md`
2. `<root>/.claude/gru/` if it exists
3. legacy `<root>/.claude/feature-context/` or `~/.claude/projects/<repo>/feature-context/`
4. otherwise Gru creates `<root>/.claude/gru/` and tells you

In git, `<root>` is the **main repo**, never a worktree. ## What is versioned

| Path | Versioned | Why |
|---|---|---|
| `gru.yml` | **yes** | Team policy that should be identical for everyone: budget defaults, `sensitive` paths, timeout, `tether_repo`, permissions. Small and rarely changes. |
| `local.yml` | no | Depends on *your* models, harness, limits and history; calibration is churny and personal. |
| `active/`, `archive/` (logs, cards, plans, `handback.md`) | no | Per-person working state: noisy diffs, session ids, local paths. Durable facts belong in the PR, in `AGENTS.md` (offered by `done`) and in the hand-back. |
| project facts (checks, "done", branch style) | yes, in `AGENTS.md`/`CLAUDE.md` | Already shared there by the interview. |

Gru writes a `.gitignore` inside the store (`*`, `!.gitignore`, `!gru.yml`), so this holds for any store location. If you do not want even `gru.yml` versioned, delete its `!gru.yml` line.

!!! warning
    Ignored logs die with an ephemeral container or a fresh clone, so `/gru resume` finds nothing there. Point `gru store:` at a persistent path outside the repo if you need it.

## Template

```markdown
# <Title>
- Slug / Status / Started / Updated / Closed
- Branches / PRs
- Budget: warn / stop paid tokens, wall-clock, max replans 2   Used: -

## Goal / Requests / Decisions / Problems
## Cards   | Card | Size | Stage | swe | plan | qa | rev | Replans | Tokens | Notes |
## Tether friction
## Progress log
## Next steps
## Sessions
```
