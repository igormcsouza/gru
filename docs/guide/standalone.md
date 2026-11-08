# Single stages

You do not always want the whole pipeline. A teammate opened a PR and you want QA and a review; a card has a plan and tests and you only want it built. Run one stage, or QA plus review, on existing work.

```text
/gru check 142                  # QA, then the reviewer rules on its findings, on PR #142
/gru qa feat/rate-limit         # QA only, on a branch
/gru review https://github.com/o/r/pull/142
/gru run build C3               # one stage of an active card
/gru run plan "add audit log"   # planner only: cards, nothing runs
```

## What happens

1. **Target.** A PR (number or URL), a branch or range, the current diff, or a card id. The code is checked out in a throwaway worktree, never your working tree.
2. **Ad-hoc card.** Objective from the PR and its linked issue; definition of done from the issue's acceptance criteria or the PR checklist, rewritten as checkable lines. With none, Gru proposes lines and asks once; if you decline, the review says it could not check a DoD and covers conventions, correctness and smells only.
3. **Size and roles.** Guessed from the diff, overridable ("as L", "with strong"). The [role matrix](roles.md#role-matrix) applies: QA and the reviewer are stronger than whoever wrote it. A human-authored PR is treated as that size's swe; the L/XL sign-off flag applies only to PRs a strong minion wrote.
4. **Run** in the [sandbox](sandbox.md) configured for the stage, starting services first if QA needs them.
5. **Report**, saved under `<store>/runs/` (git-ignored): the DoD table with evidence, findings as blocking / should-fix / note, each project **extra check** as met / unmet / unverified, and what QA did not check. There is no replan loop here.

## Your expectations

The [interview](setup.md) asked what you expect to see from QA and review in *this* project, and any checks specific to it. For example: "review: the linked Asana task exists and its acceptance criteria match the DoD". Tool-backed checks like that are gathered by Gru with the tools its own session has, then handed to the reviewer as quoted evidence, because minions on other harnesses usually do not have your connectors. If Gru has no tool for a check it reports it `unverified` and asks; it never invents evidence.

## Posting and next steps

Posting a review on a PR is outward-facing, so Gru shows the text and asks first (`permissions.post_reviews: allow` skips the question). In `versioning: none` mode the post carries no mention of Gru. Afterwards Gru offers to turn the blocking findings into a card and run the normal pipeline from `plan`, or leave them to the PR author.

## Stages and what they need

| Stage | Needs |
|---|---|
| `qa`, `review`, `check` | only the code |
| `gate` | pinned tests (without them it only runs the checks) |
| `build` | a plan and pinned tests; Gru offers to run `plan` and `tests` first |
| `tests` | a plan or a small card |
| `plan` | an objective |

Standalone runs count against the budget and are logged, but do not feed calibration.
