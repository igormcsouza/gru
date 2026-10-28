# Quickstart

!!! tip
    Run the orchestrator on Sonnet: `claude --model sonnet`. On Opus the orchestrator itself becomes the biggest paid cost.

## 1. Prove the harnesses

```text
/gru selftest
```

One trivial task ("create `hello.txt` containing `ok`") runs per tier-0/1 harness and model through the sandbox. Gru checks the cwd is respected, `~/.ssh` is hidden, writes outside the worktree fail, usage numbers are reported, and records results in `.claude/gru.json`. A few cents at most.

## 2. Start a feature

```text
/gru add rate limiting to the public API
```

On first use in a project, Gru runs a **preflight**: it pre-fills a `## Dev team specifics` section (code projects) from your Makefile, `package.json`, CI and git history and asks only for what is missing: stack, check commands, E2E, branch and PR style, delivery mode, hard stops, design docs. Non-code projects get a short `## Feature context` instead.

## 3. Get grilled

Gru reads your repo docs first and never asks what they already answer. Then at most 7 questions per round, each with a recommendation: does it fit the repo, should it exist, smallest useful version, non-goals, failure modes, trust boundaries, cost. It may conclude "don't build this" and log that decision.

## 4. Approve the plan preview

`architect` produces the task plan. You see tasks, the starting tier per task, estimated minion cost and a proposed **budget**. One approval covers the plan; Gru asks again only if scope, a cap or Tier 3 changes.

## 5. Watch it work

Gru commits the failing acceptance tests, creates a worktree per task, dispatches minions (up to 3 at once), verifies each result itself, reviews diffs, and opens PRs per your delivery mode. Use:

```text
/gru status
```

## 6. Come back later, then close

```text
/gru resume    # re-attaches in-flight minions
/gru done      # wrap-up, clean leftovers, archive the log
```
