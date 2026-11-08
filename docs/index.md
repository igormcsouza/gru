# Gru

**Gru** orchestrates a small team of AI roles written in plain English: a planner, two software engineers, a QA and a reviewer, each on a **strong, mid or weak** model. It is a [Claude Code](https://claude.com/claude-code) skill: no server, no framework.

```text
/gru add rate limiting to the public API
```

The first time, Gru [interviews you](guide/setup.md) to learn the project and how you work. Then it grills the idea, cuts it into [cards](guide/task-cards.md) (objective, definition of done, T-shirt size), shows you the models, schedule and cost, and after you accept runs each card through [plan, tests, build, QA and review](guide/pipeline.md), replanning on findings, before handing a structured result back.

## Principles

- **Judge with the stronger model.** Planner, QA and reviewer are always stronger than the swe who built the work.
- **Tests before code, by someone else.** One swe writes the verification, another builds to pass it.
- **Never trust "done".** Gru's deterministic gate and the reviewer's evidence per definition-of-done line decide.
- **Fix what was bad.** Findings go back to the card's planner for a minimal replan, max 2, then to you.
- **Ask when stuck.** Ambiguity, limits and sign-offs come to the caller.
- **You decide.** Sizes, models and order are guesses until you accept them.
- **Safe by default.** Minions are sandboxed, never see secrets, and their output is data.

## Where to go next

<div class="grid cards" markdown>

- **[Install](getting-started/install.md)**: one command.
- **[Quickstart](getting-started/quickstart.md)**: your first feature.
- **[Commands](guide/commands.md)**: request, status, steer and more.
- **[Roles and models](guide/roles.md)**: strong/mid/weak and who reviews whom.
- **[Contributing](project/contributing.md)**: help build it.

</div>
