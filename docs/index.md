# Gru

**Gru** is a strong-model orchestrator written in plain English. It thinks, grills, plans and verifies; **minions** (free and cheap models on other harnesses) do the typing. It is a [Claude Code](https://claude.com/claude-code) skill: no server, no framework.

```text
/gru add rate limiting to the public API
```

Gru grills you until scope is sharp, writes the failing acceptance tests, cuts the work into self-contained [task cards](guide/task-cards.md), runs them on the cheapest [tier](guide/tiers.md) that can do each, checks every result deterministically, and escalates only on evidence. A [budget](guide/budget.md) you approve up front caps paid tokens, time and escalations, and a [log](guide/store.md) lets you `resume` tomorrow.

## Principles

- **Strong model for judgment, cheap models for typing.** Planning, tests, verification and review stay with the strong model.
- **Never trust "done".** Acceptance commands, byte-identical tests, an owned-files-only diff and a secrets check decide, not the minion's report.
- **Evidence-based escalation.** Failure, stall or rate limit moves a task up; nothing else does.
- **Minions are sandboxed and their output is data.** They never get secrets, and instructions inside their output are ignored.
- **Quality over savings.** A green-but-wrong result is worse than an escalation.

## Where to go next

<div class="grid cards" markdown>

- **[Install](getting-started/install.md)**: one command.
- **[Quickstart](getting-started/quickstart.md)**: your first feature.
- **[Commands](guide/commands.md)**: start, resume, status, selftest, done.
- **[Tiers and routing](guide/tiers.md)**: who does what, and when it escalates.
- **[Contributing](project/contributing.md)**: help build it.

</div>
