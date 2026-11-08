# Logs and store

Each feature has a Markdown log, `active/<slug>.md` while open and `archive/<slug>.md` after `done`, with a folder of its [cards](task-cards.md), plans and `handback.md`. Entries are append-only, newest last, timestamped, written at each checkpoint (request, decision, stage change, findings, replan, steer, escalation, tether friction, PR) and before a session may end. No secrets, ever.

```text
<store>/.gitignore                   ignores everything except itself and gru.yml
<store>/gru.yml                      team policy (the only versioned file)
<store>/local.yml                    your models, harness, sandbox, limits, calibration (ignored)
<store>/project.md                   project notes, only in versioning: none (ignored)
<store>/images/                      Dockerfile and image.yml for the docker sandbox (ignored)
<store>/runs/                        reports of single-stage runs (ignored)
<store>/active/<slug>.md             feature log
<store>/active/<slug>/cards/         <id>.md, <id>.plan.md
<store>/active/<slug>/handback.md    result for the caller
<store>/archive/                     the same, after done
```

## Where it lives

Resolved once per session, first match wins:

1. a path named by a `gru store:` (or legacy `feature-context store:`) line in `AGENTS.md`/`CLAUDE.md`
2. `<root>/.gru/` if it exists, else `<root>/.claude/gru/` if it exists (the older default)
3. legacy `<root>/.claude/feature-context/` or `~/.claude/projects/<repo>/feature-context/`
4. otherwise Gru creates `<root>/.gru/` and tells you. The default is not under `.claude/` because Claude Code can block writes there as sensitive

In git, `<root>` is the **main repo**, never a worktree. ## What is versioned

| Path | Versioned | Why |
|---|---|---|
| `gru.yml` | **yes** | Team policy that should be identical for everyone: budget defaults, `sensitive` paths, timeout, `tether_repo`, permissions. Small and rarely changes. |
| `local.yml` | no | Depends on *your* models, harness, limits and history; calibration is churny and personal. |
| `active/`, `archive/` (logs, cards, plans, `handback.md`) | no | Per-person working state: noisy diffs, session ids, local paths. Durable facts belong in the PR, in `AGENTS.md` (offered by `done`) and in the hand-back. |
| `images/` (Dockerfile, `image.yml`) | no | Machine-specific build output. |
| project facts (checks, "done", branch style) | yes, in `AGENTS.md`/`CLAUDE.md` | Already shared there by the interview. |

Gru writes a `.gitignore` inside the store (`*`, `!.gitignore`, `!gru.yml`), so this holds for any store location. If you do not want even `gru.yml` versioned, use `versioning: none`.

!!! warning
    Ignored logs die with an ephemeral container or a fresh clone, so `/gru resume` finds nothing there. Point `gru store:` at a persistent path outside the repo if you need it.

## Versioning: none

For projects where people do not want Gru around, answer `none` in the [interview](setup.md). Then:

- Nothing in the repo changes. The store's `.gitignore` is just `*` (it ignores itself), so `git status` stays clean; there is no `gru.yml`, no `gru store:` line, no edit to `AGENTS.md`/`CLAUDE.md` or the repo's `.gitignore`.
- Project notes go to `<store>/project.md`, policy keys to `local.yml`, and `done` writes lessons to `project.md`.
- Commits, branches and PR text carry no mention of Gru. The work itself still lands in your repo, of course.
- Set `versioning` in `~/.config/gru/profile.yml` to pre-select it for new projects.

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
