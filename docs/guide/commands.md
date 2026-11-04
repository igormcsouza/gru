# Commands

| Command | What it does |
|---|---|
| `/gru <request>` or `/gru new <name>` | Plan, grill, split into task cards, show them, then run them on minions after you accept. |
| `/gru resume` | List active features (slug, goal, status, updated, top 3 next steps, budget used), read the chosen log, summarize in 10 lines or fewer, then reconcile minions. |
| `/gru status` | Tasks by state, tier and attempts; spend vs budget; blocked items; decisions needed. Max 10 lines. |
| `/gru selftest` | Prove the harnesses before trusting them. |
| `/gru done` | Wrap up, clean up, archive. |

## start

A request can be a change, a question, a clarification or research. A **small** one (a question, a lookup, a one-file tweak) goes to one minion and you get the answer back. A **large or risky** one runs the pipeline:

1. **Log.** `/gru new <name>` always starts a new session log. `/gru <request>` with no active log creates one for you (slug from the request); with one already active it continues it. Slug is kebab-case; Gru refuses if `active/<slug>.md` exists (use `resume`). The log is created from a template, and anything this session already did is backfilled with a `(backfilled)` prefix, never invented.
2. **Plan and grill** the PO (you) on the edge cases and issues the plan brings.
3. **Split** into small, self-contained [task cards](task-cards.md) (`swe`, `qa`, `review`, `research`, `docs`) with acceptance tests written first. A tier too weak for a card is skipped; a card no tier fits is listed for you instead of dispatched.
4. **Show the tasks**: id, agent, expected output, harness and model, tier, estimated cost, and the budget. You accept.
5. **Spawn and gather**: minions run, Gru verifies and reports the results together.
6. **Gru does not type product changes itself** unless you agreed beforehand, with a reason given in the plan.

## Dispatch loop

Per task, in parallel when files are disjoint (cap 3 minions at once):

1. Pick tier, model and harness and run the card in your workspace (minions write there; cards running together own disjoint files), then record it in the ledger.
2. **Verify yourself**: acceptance commands, pre-written tests byte-identical to the committed ones, `git status --porcelain` (tracked and untracked) a subset of owned files, non-empty and sane diff, no secrets.
3. Pass: commit. Fail: retry once at the same tier with the exact failure appended; fail again, stall or rate limit: escalate one tier.
4. Escalating into an Opus/Fable rung or past budget: stop and ask with options and a recommendation.
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
