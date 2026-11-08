# How a card runs

After you accept the preview, each card goes through these stages. Every role is a separate minion session.

```text
plan -> tests -> build -> gate -> qa + review -> done
                   ^                  |
                   +----- replan <----+   (max 2, then it comes to you)
```

1. **Plan** (planner): steps, and which check proves each definition-of-done (DoD) line. Doubts become questions, not guesses.
2. **Tests** (swe A): writes the verification only, one test per DoD line plus bad days, and shows each fails for the right reason. The planner checks coverage. Non-code work gets a checklist, script or link check instead.
3. **Build** (swe B, fresh session): makes the pinned tests pass. Pinned tests are read-only.
4. **Gate** (Gru, deterministic): tests byte-identical, acceptance commands pass, only owned files touched, sane diff, no secrets. Gru never trusts "done".
5. **QA** hunts bugs, edge cases and hard-to-maintain code. The **reviewer** ticks the DoD line by line with evidence and reviews the diff.

## Findings

| Kind | Meaning | Effect |
|---|---|---|
| **blocking** | DoD line unmet, failing check, bug, security, scope violation | replan |
| **should-fix** | smell, missing edge case, maintainability | folded into a replan if cheap, else handed back |
| **note** | advisory | handed back |

## Replan

The card's own planner gets the findings and writes a **delta plan**: keep what passed, change only what was flagged. Pinned tests change only if the planner shows they were wrong. After **2 replans** the card goes to you with a diagnosis. The planner may recommend a **bump** (swe up one slot); that costs more, so Gru asks unless your profile says `autonomy: bump_ok`.

## When Gru asks you

An ambiguous or wrong card or DoD, a doubt the repo cannot answer, two replans used, qa and reviewer disagreeing on something that matters (non-blocking disagreements: the reviewer decides), a bump or split, an L/XL sign-off, a budget cap or hard stop, a broken harness with no fallback.

## Hand-back

Gru returns a structured result to whoever called it (you, or an agent): per card the status, branch or PR, **evidence for every DoD line**, open should-fix items, and what needs input, plus one command that re-checks the whole feature. The caller verifies it or delivers (opens the PR, sends the file). Gru delivers itself only per your project's mode and with your OK.
