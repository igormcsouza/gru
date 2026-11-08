# Role agents

Gru runs these roles as minions; each brief is the body of a file in `agents/`. They also work without Gru: `claude --agent team-leader` runs the same flow with plain Claude subagents.

| Agent | Role |
|---|---|
| `planner` | Plans a card (or grills and cuts a whole feature), maps every definition-of-done line to a check, checks the tests, and writes minimal **delta plans** on findings. Read-only. |
| `swe` | Two modes: `tests` writes the failing verification, `build` makes it pass. Does not plan or decide product behavior. |
| `qa` | Exercises the work, hunts bugs, edge cases and smells, reports blocking / should-fix / note. Does not fix. |
| `reviewer` | Ticks the definition of done with evidence, reviews the diff, rules on qa's findings. Merges only when allowed. |
| `team-leader` | Standalone orchestrator for the same flow without the skill. Never implements. |

The planner, qa and reviewer are always [stronger than the swe](roles.md#role-matrix).

## Project rules

Put these in the project's `AGENTS.md`/`CLAUDE.md`: stack, checks, e2e runbooks, branch and commit style, delivery mode, **what done means**, hard stops. The [interview](setup.md) asks and writes them for you.

To customize a role for one project, add `.claude/agents/<role>.md` there; project agents win over global ones.
