# Task cards

A minion sees no conversation, so each task is self-contained. This is where the strong model's tokens are best spent: weak models fail on vague specs.

| Field | Why |
|---|---|
| id, branch, one-paragraph goal | what and where |
| **files it owns** | disjoint from other tasks in the phase |
| **pre-written tests** (paths) | read-only for the minion; Gru checks they are unchanged |
| **reading list** | exact files to read, "do not explore the repo": keeps tokens down |
| `est_tokens` | card + reading list + expected output, estimated as bytes/4 |
| conventions that apply | the few lines pasted in, not "see AGENTS.md" |
| **acceptance commands** | lint, types, tests for the touched code |
| difficulty (`easy`/`medium`/`hard`), risk (`low`/`high`) | sets the starting [tier](tiers.md) |
| rule line | "Do not run git commit/push, do not touch other files, do not read `.env*`." |

## Tests first

For each code task the **strong model writes failing acceptance tests** that pin the behavior (happy path and bad day) and commits them on the task branch before dispatch. Minions only make them pass. A task with no testable behavior says so in its card and starts one tier higher.

## Sizing

Size for the weakest model. If `est_tokens` exceeds half the target model's context window (`context` map in `gru.json`; unknown free models count as 32k), split the task, trim the reading list or start at a tier with a bigger window. Prefer many small cards over one big one.
