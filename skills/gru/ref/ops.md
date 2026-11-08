# Ops: status, steer, resume, done, store, logging, budget, calibration

## Store
Resolve once per session, first match wins: (1) path in a `gru store:` / `feature-context store:` line of `AGENTS.md`/`CLAUDE.md`; (2) `<root>/.claude/gru/` if it exists; (3) legacy `<root>/.claude/feature-context/` or `~/.claude/projects/<repo>/feature-context/`; (4) create `<root>/.claude/gru/` and tell the user. In git use the **main repo** root, never a worktree: `dirname "$(git rev-parse --path-format=absolute --git-common-dir)"`.
```
<store>/.gitignore                   ignores everything except itself and gru.yml
<store>/gru.yml                      team policy (the only versioned file)
<store>/local.yml                    your models, harness, limits, calibration (ignored)
<store>/active/<slug>.md             feature log
<store>/active/<slug>/cards/<id>.md  card, <id>.plan.md  its plan
<store>/active/<slug>/handback.md    result for the caller
<store>/archive/...                  the same, after done
```
**Logs are never versioned.** On creating a store write `<store>/.gitignore` containing `*`, `!.gitignore`, `!gru.yml` (so logs, cards, plans, hand-backs, archive and `local.yml` are ignored wherever the store lives, even a custom path). Never `git add` anything but `gru.yml` there. No secrets in anything stored. Consequence: a fresh container or clone has no logs, so `resume` finds nothing there; for ephemeral environments point `gru store:` at a persistent path outside the repo. Durable facts belong in the PR, `AGENTS.md` (via `done`) or the hand-back.

## status [feature]
Default: the active feature (if several, list them and ask). Show a table, one row per card, then 4 lines at most below it.

| Card | Title | Size | Stage | swe / plan / qa / rev | Replans | Tokens | Observations |
|---|---|---|---|---|---|---|---|

- **Stage** is one of `planned, plan, tests, build, gate, qa+review, replan, done, needs-input, parked`, with the running harness if live.
- **Observations**: what matters now in <=12 words: "2 blocking from reviewer, replan 1/2", "waiting: local qwen busy", "tests pinned, 5 DoD lines", "on claude: tether crash".
- Below: budget (paid tokens vs warn/stop, wall-clock), what runs now, decisions needed from the caller, calibration notes. Source: the log, the card files and a quick liveness check of in-flight minions (`tether_status`, `git worktree list`, session ids). Read, do not change anything.

## steer `<card> <instruction>`
Change one card's course. Parse the instruction:
- free text: a **binding note** for that card. Append it to the card (`## Steering`), log it, and deliver it at the next safe point: a running tether session via `tether_send`, otherwise included in the next stage's brief. If the note changes the objective or the DoD, show the new DoD, get the caller's OK, and restate the affected checks (a DoD change after tests are pinned goes through the planner and a re-pin).
- `bump [weak|mid|strong]`: raise the swe slot one level (or to the named one), recompute the roles by the matrix, show the new row and cost, and apply on OK. The tests already pinned stay; build restarts with a fresh swe B session and the previous failure output.
- `resize <XS..XL>`: change the size; recompute slots and estimate as above.
- `rerun <stage>`: restart from that stage (keeps earlier artifacts).
- `stop`: terminate the card's minions, keep the work, set `parked`.
Always confirm what changed in one line and log it. Steering never exceeds an approved cap without asking.

## resume
List `active/*.md` (slug, goal, status, updated, top 3 next steps, budget used). Confirm which. Read it fully, summarize in <=10 lines, then **reconcile minions**: for each in-flight card check its worktree/branch/session and either re-attach or restart that stage at its recorded slot. Resume logging.

## done
1. Write the wrap-up (outcome, decisions, PRs, debt, lessons, cost by slot vs what it solved, calibration changes), and offer to copy durable lessons into the project's `AGENTS.md` (user approves the text).
2. **Clean up leftovers**, listing first and acting only on what this feature created (the log lists them): kill minion processes still running (`pgrep -af "opencode run|bwrap"` filtered to the feature's worktrees; `tether_list` for open sessions); `git worktree remove` each feature worktree whose branch is merged or pushed, then `git worktree prune`; delete merged local task branches (`git branch -d`, never `-D`, never remote); remove scratch files and the selftest worktree. Anything with unpushed or unmerged work is **kept** and listed with its path. Never delete by glob; remove by recorded path.
3. Set `Status: done`, `Closed`, move the log and its folder to `archive/`, stop logging, report what was removed and what was kept.

## Logging (automatic while a feature is active)
Append only, newest last, timestamped `YYYY-MM-DD HH:MM`, at each checkpoint (request, decision, card stage change, finding summary, replan, steer, escalation, tether friction, PR, merge) and before the session may end; reply with a one-line "logged". Record what a cold start needs: paths, commands, branches, PRs, session ids, gotchas.

Log template:
```markdown
# <Title>
- Slug: <slug>   Status: active   Started: <date>   Updated: <date>   Closed: -
- Branches / PRs: -
- Budget: warn <n> / stop <n> paid tokens, wall-clock <n> min, max replans 2   Used: -
## Goal / Requests / Decisions / Problems
## Cards
| Card | Size | Stage | swe | plan | qa | rev | Replans | Tokens | Notes |
|---|---|---|---|---|---|---|---|---|---|
## Tether friction
## Progress log
## Next steps
- [ ]
## Sessions
| Date | Session note |
```

## Budget
Track per card and total: tokens (what the harness reports; otherwise bytes/4 marked `~`), wall-clock, replans. **Paid tokens** are tokens on paid models, including Gru itself; free and local models are tracked but not counted against the cap. Read session usage if a tool offers it, else estimate and mark `~`.
- Defaults from `gru.yml` (`budget`; yours may override in `local.yml`): tell the caller at the warn line (one line: spent by slot, what is left, what is running), stop and ask at the stop line (raise it, shrink reviews to the risky hunks, move work to cheaper slots, or stop). The preview may set other numbers; with a cap, warn at 75%, stop at 100%. A wall-clock cap behaves the same.
- On a warning: no more bumps without asking, and no new optional should-fix work.
- Quality over savings: if the gate for a card looks too weak (no real checks), say so and ask rather than shipping green-but-wrong.

## Calibration (learn the project)
When a card closes, append to `local.yml` `calibration.history`: `{date, feature, card, size, swe_slot, swe_model, harness, replans, bumped, blocking, should_fix, tokens, minutes, outcome}`; keep the last 200. Recompute `calibration.stats["size/slot"]`: `n`, `first_pass` (share done with 0 replans), `avg_replans`, `bumps`.
Suggest, never apply on your own, in the next preview and in `status`:
- `n >= 5` and (`first_pass` < 0.5 or `avg_replans` >= 1): "S cards on weak keep needing replans here; move S to mid?"
- `n >= 8`, `first_pass` >= 0.9 and almost no blocking findings: "M cards on mid pass first try; try weak for small M?"
Accepted suggestions are written to `size_slots` in `local.yml`. Also use the stats to sharpen token estimates per size and to bench models that keep failing.
