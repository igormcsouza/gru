# Commands

| Command | What it does |
|---|---|
| `/gru <request>` | The main one. First time: the [interview](setup.md). Then grill, cut into [cards](task-cards.md), preview, run, hand back. |
| `/gru status [feature]` | A table of cards with stage, models, replans, tokens and observations. |
| `/gru steer <card> <...>` | Change one card's course (below). |
| `/gru resume` | Pick up an unfinished feature after a closed terminal. |
| `/gru setup` | Redo the interview. |
| `/gru selftest` | Prove each configured slot and harness works here. |
| `/gru done` | Wrap up, clean leftovers, archive. |

## `/gru <request>`

1. **Preflight.** No `local.yml` (or an older version)? The interview comes first, then your request.
2. **Grill.** Gru reads the repo docs, then asks at most 7 sharp questions per round, each with a recommendation. It may say "don't build this".
3. **Cards.** Each with objective, [definition of done](task-cards.md), size and files owned.
4. **Preview.** Cards, models, schedule, cost, budget. You edit, then accept.
5. **Run.** The [pipeline](pipeline.md) per card, then the hand-back.

A small request (a question, a one-file tweak) is one XS card with no grill.

## `/gru status`

```text
| Card | Title            | Size | Stage      | swe / plan / qa / rev   | Replans | Tokens | Observations                     |
| C1   | Rate limit core  | S    | qa+review  | weak / mid / mid / mid  | 0       | 38k    | tests pinned, 5 DoD lines        |
| C2   | Per-key config   | M    | replan     | mid / strong x3         | 1/2     | 96k    | 2 blocking from reviewer         |
| C3   | Docs             | XS   | planned    | weak / mid              | 0       | -      | waits for C1                     |
```

Below the table: budget used, what runs now, decisions needed from you, calibration notes. Read-only.

## `/gru steer`

```text
/gru steer C2 use the existing Redis client, do not add a dependency
/gru steer C2 bump            # swe up one slot (or: bump strong)
/gru steer C2 resize L
/gru steer C2 rerun build
/gru steer C2 stop            # park it, keep the work
```

Free text becomes a binding note delivered to the card's next stage (or to a live tether session). Changing the objective or definition of done goes back through the planner and a re-pin of the checks. Steering never exceeds a cap without asking.

## `/gru resume`, `selftest`, `done`

`resume` lists active features, reads the chosen log and re-attaches or restarts in-flight minions at their recorded slot (logs are local and git-ignored, so a fresh clone or container has none). `selftest` runs one trivial card per slot and harness pair and records the result under `verified`, including the sandbox checks (hidden `$HOME`, worktree-only writes, network, Docker image and services). `done` writes the wrap-up and cleans only what the feature created: it kills leftover minions, removes worktrees of merged or pushed branches, deletes merged local task branches (`git branch -d`, never `-D`), and keeps and lists anything unpushed.
