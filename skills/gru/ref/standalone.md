# Standalone stages: run one step on existing work

For work that already exists (a teammate's PR, a branch, a finished card) the user wants one stage, not the whole pipeline. Commands:

| Command | Runs |
|---|---|
| `qa <target>` | qa only |
| `review <target>` | reviewer only |
| `check <target>` | qa then reviewer (reviewer rules on qa's findings), in parallel if `limits` allow |
| `run <stage> <target>` | any one stage: `plan`, `tests`, `build`, `gate`, `qa`, `review` |

Options the user may add in words: a size (`as L`), a slot (`with strong`), `no services`, `post it`, `dry`. Preflight (and the interview, if due) still run first.

## 1. Resolve the target
- **PR** (number or URL): `gh pr view <n> --json title,body,author,headRefName,baseRefName,statusCheckRollup,closingIssuesReferences`, `gh pr diff <n>`, `gh pr checks <n>`. Fetch the head branch into a **throwaway worktree** (never the user's working tree).
- **Branch or range** (`feat/x`, `main..feat/x`), **the current diff** (working tree vs base), or a **card id** of an active feature (use its card and plan as they are).
- Unknown or ambiguous target: ask once. A target outside the project root or another repo: ask first.

## 2. Build the ad-hoc card
- **Objective**: from the PR title/body and the linked issue. **Definition of done**: the issue's acceptance criteria or the PR's checklist, rewritten as checkable lines. If there are none, propose lines from the description and diff, show them, and take one confirmation; if the user declines, mark the run `no DoD supplied`: the reviewer then checks conventions, correctness and smells only, and says the DoD could not be checked.
- **Size** from the diff (files, lines, risk), shown and overridable. **Roles** from the matrix in `ref/run.md` using that size. A human-authored PR counts as the size's swe slot; the L/XL "caller sign-off" flag applies only when a strong minion authored it.
- `needs` for qa: from the card, else detect compose/e2e config, else ask. Sandbox per stage as configured (`ref/sandbox.md`); start the services if needed.
- Prerequisites by stage: `qa`/`review`/`check` need only the code. `gate` needs pinned tests (else it only runs checks). `build` needs a plan and pinned tests (offer to run `plan` and `tests` first). `tests` needs a plan (or a small card). `plan` needs an objective. Missing prerequisite: say so and offer to run it; never skip silently.

## 3. Expectations and extra checks
Read the project's QA and review **expectations** and **extra checks** from the project notes (`AGENTS.md` section, or `<store>/project.md` in `versioning: none`). Put them in the role briefs. For each extra check with a `source` tool (Asana, Jira, Slack, ...): **you gather the evidence yourself** with the tools your session has (the minion's harness usually lacks them), paste only the needed text (never tokens or secrets), and give it to the reviewer or qa as quoted data. If you have no tool for it, mark the check `unverified` and ask the user whether to continue. Never invent evidence.

## 4. Run
Dispatch the stage(s) through the harness with the role briefs as in `ref/run.md` and `ref/harnesses.md`. `check`: after both return, the reviewer rules on qa's findings; a blocking disagreement is escalated to the user as in the pipeline. No replan loop here.

## 5. Report
Write `<store>/runs/<date>-<target-slug>.md` (git-ignored) and show it: the DoD table with evidence, findings as blocking / should-fix / note (one per line, `path:line`), each **extra check** as met / unmet / unverified, what qa did not check, and a one-line verdict (`CLEAN`, `BLOCKERS`, `ESCALATE`). Match what the user said they expect to see (format, depth, screenshots, numbers).
- **Posting is outward-facing.** Offer to post the review on the PR (`gh pr review` with the findings) and show the text first; post only on yes, or when `permissions.post_reviews: allow`. In `versioning: none` mode the post carries no mention of Gru.
- **Next steps, offered not done:** turn the blocking findings into a card and run the normal pipeline from `plan`; or leave them to the PR author.
- Log the run and count its tokens against the budget. Standalone runs do not feed calibration. Remove the throwaway worktree and any services started.
