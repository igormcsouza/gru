# Commands

| Command | What it does |
|---|---|
| `/gru <request>` or `/gru new <name>` | Start a feature: log, grill, plan, preview, dispatch. |
| `/gru resume` | List active features (slug, goal, status, updated, top 3 next steps, budget used), read the chosen log, summarize in 10 lines or fewer, then reconcile minions. |
| `/gru status` | Tasks by state, tier and attempts; spend vs budget; blocked items; decisions needed. Max 10 lines. |
| `/gru selftest` | Prove the harnesses before trusting them. |
| `/gru done` | Wrap up, clean up, archive. |

## start

1. Slug is kebab-case; Gru refuses if `active/<slug>.md` exists (use `resume`). The log is created from a template, and anything this session already did is backfilled with a `(backfilled)` prefix, never invented.
2. **Grill** the PO (you).
3. `architect` returns a task plan with [task cards](task-cards.md) and acceptance tests written first.
4. **Plan preview** with tiers and budget.
5. Dispatch loop.

## Dispatch loop

Per task, in parallel when files are disjoint (cap 3 minions at once):

1. Create a worktree (`.claude/worktrees/<slug>-<id>`), pick tier, model and harness, run the card, record it in the ledger.
2. **Verify yourself**: acceptance commands, pre-written tests byte-identical to the committed ones, `git status --porcelain` (tracked and untracked) a subset of owned files, non-empty and sane diff, no secrets.
3. Pass: commit on the task branch. Fail: retry once at the same tier with the exact failure appended; fail again, stall or rate limit: escalate one tier.
4. Escalating into Tier 3 or past budget: stop and ask with options and a recommendation.
5. Parallel branches merge into an integration branch in dependency order; checks rerun; conflicts go back as a new small card. Tasks sharing a contract run in sequence.
6. **Review** the diff (never the whole repo) with `reviewer` or yourself, then `qa` if the project defines e2e.
7. Deliver per the project's mode (PR per task by default, body `Closes #N`). Merge only if the project allows and `reviewer`'s conditions hold. Never force push, delete data, or touch cloud, DNS or money without you.

## resume

For each task marked in flight, Gru checks its worktree, branch and session (`git worktree list`, `tether_status`, opencode session id) and either re-attaches or restarts it at its recorded tier. On a git store it first runs `git fetch` and looks on `main` and the current branch for newer logs.

## selftest

Recorded under `verified` in `.claude/gru.json` with harness, date and whether usage is reported. Run it on your first `/gru` in a project and after harness upgrades.

## done

1. Wrap-up: outcome, decisions, PRs, debt, lessons, **what each tier cost vs what it solved**. Offers to copy durable lessons into `AGENTS.md` (you approve the text).
2. **Clean up** only what this feature created: kill leftover minion processes, remove worktrees of merged or pushed branches, `git worktree prune`, delete merged local task branches (`git branch -d`, never `-D`, never remote), remove scratch files. Anything unpushed or unmerged is **kept** and listed with its path. Never by glob.
3. Mark the log done, move it to `archive/`, report what was removed and kept.
