# Plan: grill, cards, preview

## 0. Size the request
- **Small** (a question, a lookup, a one-file tweak): make it one XS card (still a card file under `cards/`), run it through the harness recipe in the sandbox (never the Agent/Task tool), relay the answer with the hand-back. A question card is **read-only**: no file changes, no extra tests, unless the user asked for them (offer them as a follow-up instead). No grill, no preview unless it costs more than expected. Log it in one line.
- Anything else: the full flow below. A session log is created now (slug = kebab-case of the request, refuse if `active/<slug>.md` exists and suggest `resume`; backfill earlier work prefixed `(backfilled)`, never invent).

## 1. Grill
Read the repo docs first and never ask what they answer. Draft the plan, then ask the caller about what it raises: max 7 sharp questions per round, each with your recommendation, most scope-defining first: does it fit the project and its fixed decisions; should it exist at all; smallest useful version; non-goals; edge cases and failure modes; trust boundaries and data privacy; backward compatibility; cost; how will we know it is done. Repeat until nothing material is open. You may say "don't build this" and log that as the decision. Respect `profile.yml` `questions`.

## 2. Cut into cards
Cut the agreed scope into cards as small and self-contained as possible. The **planner of the feature** may be you or a `strong` minion for big scopes (relay its questions verbatim). Cards must be so well written that a weak model can run them; this is where strong tokens are best spent.

Card file `<store>/active/<slug>/cards/<id>.md`:
```markdown
# <id> <title>
- size: XS|S|M|L|XL      risk: low|high      kind: swe | docs | research
- depends_on: [ids]      files_owned: [paths]      resources: [harness:model needing a limit]
- needs: [services it needs while testing, e.g. postgres, browser]   (drives the qa sandbox)
## Objective
One paragraph: what changes for whom, and why.
## Definition of done
- [ ] DoD-1 <observable outcome> -- check: `<test path or command>` | reviewer inspects <what>
- [ ] DoD-2 ...
## Context
<=10 lines of the small whole picture this card needs. Nothing else of the conversation.
## Reading list
Exact files to read; "do not explore the repo".
## Conventions
The few project lines that apply, pasted (not "see AGENTS.md").
## Rules
Do not git commit/push, do not touch files outside files_owned or the pinned tests, do not read `.env*`.
## Estimate
tokens by stage and total (bytes/4 for card + reading list + output); cost if prices known.
```
- **Every DoD line names its check**: a test, a command, or a specific thing the reviewer inspects. "Works well", "clean", "robust" are rejected: rewrite them or ask the caller. Ask for the missing facts instead of inventing them.
- Non-code cards keep the same shape; "check" is a checklist, a link check, a script, or cited sources.
- Cards in a phase own disjoint files; cards sharing a contract, migration or lockfile are sequenced via `depends_on`.
- `est_tokens` over half of the target model's context (`context`, unknown = 32k): split, trim the reading list or move up a size.

## 3. Size and models
Guess the T-shirt size from scope, files touched, risk and unknowns:
| Size | Typical | swe slot (from `size_slots`) |
|---|---|---|
| XS | one file, mechanical, obvious | weak |
| S | one module, clear spec | weak |
| M | several files or real design choices | mid |
| L | cross-cutting, tricky logic, migrations | strong |
| XL | probably two cards: split unless it is truly indivisible | strong |
`risk: high` (security, data, money, migrations) never lowers a slot and raises qa/reviewer to `strong`. Then fill the other roles from the **Role matrix in `SKILL.md`**, exactly (S means weak swes with mid planner, qa and reviewer; do not upgrade roles on your own). If calibration (`ref/ops.md`) has a suggestion for a size, show it as a note; the caller decides.

## 4. Preview (the caller reviews cards and the execution plan)
Show one table, one row per card: id, title, size, risk, depends_on, swe/planner/qa/reviewer slots and models, harness, est tokens and cost, DoD count, and the **sandbox per stage** where it is not the default (e.g. `qa: docker`). Below it:
- **Schedule**: waves of cards that run together, and why anything is sequential (shared files, dependencies, a `limits` match such as a local model or a rate-limited provider).
- **Budget**: paid-token warn/stop (defaults from `gru.yml`, editable; the preview's numbers apply to this feature only), wall-clock cap, max replans (default 2 per card).
- **Flags**: cards that need services the chosen sandbox cannot give (e.g. Linux without Docker), L/XL cards whose review needs the caller's sign-off (no stronger model exists), cards no configured model fits, calibration notes.
The caller may change a size, slot, DoD, order or drop a card. **Their decision wins**; recompute the row and show only what changed. Wait for an explicit accept; ask again only if scope, a cap or a slot above the approved one changes. Then read `ref/run.md` and `ref/harnesses.md`.
