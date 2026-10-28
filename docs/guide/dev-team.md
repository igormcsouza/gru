# Dev team agents

Gru acts as the Team Leader and uses these agents. They also work without Gru: start the orchestrator as the main session with `claude --agent team-leader`.

| Agent | Role |
|---|---|
| `team-leader` | Main-session orchestrator and your only point of contact. Relays your vision, sends ideas to `architect`, dispatches `swe`/`qa`/`reviewer`, gathers reports. Never implements. |
| `architect` | Grills the idea until scope is sharp, then produces a phased task plan implementers can follow without further decisions. Read-only. |
| `swe` | Implements one well-specified task on its own branch and worktree. Does not plan or make product decisions. |
| `qa` | Verifies a finished PR or integrated branch end to end and answers `QA: GOOD TO GO` or `BLOCKED`. Does not fix product code. |
| `reviewer` | Reviews for correctness, security, smells and conventions. Merges only when the Team Leader allows and all conditions hold. |

Flow: idea -> `architect` (questions relayed to you, then a plan) -> `swe` per task -> `qa` + `reviewer` on the PR -> merge.

## Project rules

Put these in the project's `AGENTS.md`/`CLAUDE.md`: stack, test and coverage gates, e2e runbooks, branch and commit style, waves vs integration branch, hard stops. Gru's preflight asks and writes them for you.

To customize a role for one project, add `.claude/agents/<role>.md` there; project agents win over global ones. Model choice is not pinned; set `model:` in a project override to cap cost.
