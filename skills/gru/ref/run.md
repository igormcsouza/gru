# Run: the pipeline per card

Each role is a separate minion session started through the harness (`ref/harnesses.md`) with the role brief (`agents/<role>.md`, body only) plus the card. Roles never share a session. Run each stage in the sandbox backend chosen for it (`ref/sandbox.md`), starting a card's services first if it needs them. Write stage changes to the log immediately.

## Role matrix
The matrix is in `SKILL.md` (always loaded). Extra rules: the tests swe and the build swe are separate sessions of the same slot, ideally different models when two exist in that slot. If a user override or a `bump` changes the swe slot, recompute the row. L/XL sign-off: when no `strong_alt` exists, mark the card **needs caller sign-off** at the review stage; the caller must confirm before it counts as done.

## Stages
`planned > plan > tests > build > gate > qa+review > done`, with `replan`, `needs-input` and `parked` as side states.

1. **plan** (planner): reads the card and reading list, writes `cards/<id>.plan.md`: steps, which test proves each DoD line, risks, what is out of scope. Short for XS/S. Raises doubts about the card as questions instead of guessing; unanswered doubts go to the caller.
2. **tests** (swe A): writes the verification only, one test (or check) per DoD line, plus bad-day cases. Code: failing unit tests; other kinds: a checklist, script or link check. Runs them and shows they fail for the right reason. Commit them as pinned. **Planner checks** the tests against the DoD (every line covered, nothing vacuous) before build starts; gaps go back to swe A once.
3. **build** (swe B, fresh session): implements until the pinned checks pass. Pinned tests are read-only.
4. **gate** (you, deterministic, in the workspace): pinned tests byte-identical to the committed ones; acceptance commands pass; `git status --porcelain` (tracked and untracked) is a subset of `files_owned`; diff non-empty and sane; no secrets in the diff. A failed gate: one retry of swe B with the exact failure output; a second failure counts as a **replan**.
5. **qa + review** (qa and reviewer, in parallel unless `limits` forbid it). Brief both with the project's QA/review **expectations** and **extra checks**; gather tool-backed evidence yourself first (`ref/standalone.md`, Expectations):
   - **qa**: runs the work, probes edge cases and bad days, hunts bugs, smells and hard-to-maintain code, writes extra checks as findings (does not fix).
   - **reviewer**: ticks the **definition of done** line by line with evidence, reviews the diff for correctness, security, conventions and smells, and rules on qa's findings.
   Both return findings of three kinds:
   - **blocking**: a DoD line not met, a failing check, a bug, a security problem, a scope violation.
   - **should-fix**: smells, missing edge-case coverage, maintainability issues that are not wrong today.
   - **note**: advisory.
6. **done**: no blocking findings and (L/XL) the caller signed off. **Before writing the hand-back, append the card to `local.yml` `calibration.history`:** `{date, feature, card, size, swe_slot, swe_model, harness, replans, bumped, blocking, should_fix, tokens, minutes, outcome}` (keep the last 200) and recompute `calibration.stats["size/slot"]` (`n`, `first_pass`, `avg_replans`, `bumps`). Suggestions are in `ref/ops.md`, Calibration. Open should-fix and notes ride along in the hand-back.

## Replan (save the work)
Triggered by blocking findings, a twice-failed gate, or a planner doubt. The **same planner** that owns the card gets the findings and writes a **delta plan**: keep everything that passed, change only what was flagged, say which pinned tests stay (a pinned test changes only if the planner shows it was wrong, and then it is re-pinned and re-checked against the DoD). It may fold in cheap should-fix items while it is there. Then swe B fixes just that, the gate re-runs, and qa/review re-check only what changed plus the DoD.
- **Cap: 2 replans per card.** The third failure goes to the caller as `needs-input`, with the findings and the planner's diagnosis (spec ambiguous, tests wrong, swe too weak, task too big).
- The planner may *recommend* a `bump` (swe up one slot, roles recomputed by the matrix). A bump spends more, so ask the caller unless `profile.yml` has `autonomy: bump_ok` and the budget allows; then log it.
- A model that fails 2 gates in a row in this feature is benched for it.

## Disagreements
qa and reviewer disagree: if it is only about should-fix/notes, the **reviewer decides**. If it touches a blocking finding, the DoD, security, scope or the plan, **escalate to the caller** with both positions and your recommendation.

## Escalate to the caller (human or invoking agent)
Stop that card (others continue if independent) and ask, with options and a recommendation, when: the card or DoD is ambiguous or looks wrong; the planner has a doubt it cannot resolve from the repo; 2 replans are used; qa and reviewer disagree on something that matters; a bump or split is needed; an L/XL review needs sign-off; a budget cap, hard stop or `sensitive` path is hit; a harness is broken and the fallback also failed; a `limits` rule blocks progress. State the card id, stage, what you tried, and the smallest decision needed. Send a `PushNotification` if available and `profile.yml` `notify` allows it.

## Scheduling and limits
Run cards in parallel only if all hold: no `depends_on` between them, disjoint `files_owned`, total running <= `max_parallel`, and no `limits` rule is exceeded. A `limits` entry matching `harness:model` caps concurrent runs of that model (`max_parallel`) and, with `rpm`, spaces requests; `kind: local` models (e.g. a local Qwen) run one at a time and are never run next to other heavy local work. Stages of one card are sequential. Print the waves in the preview; if a limit changes the schedule mid-run (rate limit hit), mark that model down for the run, queue its cards, tell the caller once.
Cards that need the same fixed host port or a shared service instance are sequenced, or each gets its own compose project. Merge parallel card branches into one integration branch in dependency order, rerun the project checks on the result, and send conflicts back as a new small card.

## Hand-back to the caller
When all cards are done, parked or waiting, write `<store>/active/<slug>/handback.md`, show it, and (if the caller is an agent) return it as the final message. Format:
```yaml
feature: <slug>
status: done | blocked | needs-input     # per card too
cards:
  - id: C1
    status: done
    branch: feat/c1-...            # and/or commit SHAs, PR URL if delivered
    dod:                            # evidence for every line
      - {line: "DoD-1 ...", met: true, evidence: "tests/x.py::test_a passed; reviewer note"}
    open_should_fix: ["path:line: ..."]
    notes: [...]
    signoff_needed: false           # true for L/XL reviews
needs_input:                        # questions that block cards, with options + recommendation
verification_hint: "<one command that re-checks the whole feature>"
spend: {paid_tokens: ~, by_slot: {...}, wall_min: ~}
```
The caller then verifies on its own or delivers (open the PR, ship the file). Deliver yourself only per the project's delivery mode and with the user's OK (`gh pr create`, body `Closes #N`); never merge unless the project allows it, never force push, delete data or touch cloud/DNS/money without the user.
