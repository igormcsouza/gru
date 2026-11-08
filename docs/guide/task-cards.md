# Task cards

A minion sees no conversation, so each card is self-contained. Strong-model tokens are best spent here: weak models fail on vague cards. Each card has an **objective** and a **definition of done**.

| Field | Why |
|---|---|
| id, title, **size** (XS to XL), risk, kind | what it is, and which slots run it |
| **Objective** | what changes, for whom, why |
| **Definition of done** | a checklist; every line names its check (a test, a command, or what the reviewer inspects) |
| `files_owned`, `depends_on`, `resources` | scheduling: disjoint files, order, rate-limited or local models |
| `needs` | services it needs while testing (database, browser); drives the QA [sandbox](sandbox.md) |
| **Context** | at most 10 lines of the small whole picture |
| **Reading list** | exact files to read; "do not explore the repo" |
| **Conventions** | the few project lines that apply, pasted in |
| **Rules** | no commit/push, no touching other files, no `.env*` |
| **Estimate** | tokens by stage, and cost if prices are known |

"Works well" or "is clean" is not a definition of done. If Gru cannot make a line checkable it asks you.

## Sizing

Gru guesses the size, you decide in the preview (or later with `/gru steer <card> resize <size>`). An XL probably wants splitting. If `est_tokens` exceeds half the target model's context window (unknown free models count as 32k), Gru splits the card or trims the reading list.

## Preview

Before anything runs you see a table (card, size, risk, dependencies, the model per role, harness, the sandbox per stage, estimated tokens and cost), the **schedule** (what runs together, and why anything is sequential), the budget, and flags (L/XL sign-offs, cards needing services the sandbox cannot give, calibration notes). Change anything; your decision wins.
