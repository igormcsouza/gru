# Logs and store

Each feature has a Markdown log, `active/<slug>.md` while open and `archive/<slug>.md` after `done`. Entries are append-only, newest last, timestamped `YYYY-MM-DD HH:MM`, written at each checkpoint (request, decision, problem, dispatch, verify result, escalation, PR, merge) and before a session may end. No secrets, ever.

## Where it lives

Resolved once per session, first match wins:

1. a path named by a `gru store:` (or legacy `feature-context store:`) line in `AGENTS.md`/`CLAUDE.md`
2. `<root>/.claude/gru/` if it exists
3. legacy `<root>/.claude/feature-context/` or `~/.claude/projects/<repo>/feature-context/`
4. otherwise Gru creates `<root>/.claude/gru/{active,archive}/` and tells you

In git, `<root>` is the **main repo**, never a worktree. For an in-repo store, Gru commits and pushes the log with the working branch (an uncommitted log dies with the container).

## Template

```markdown
# <Title>
- Slug / Status / Started / Updated / Closed
- Branches / PRs
- Budget: warn 300k / stop 400k paid tokens (or your caps), wall-clock, max escalations   Used: —

## Goal / Requests / Decisions / Problems
## Plan (task cards)
## Ledger   | Task | Tier | Model | Harness | Session | Attempt | Tokens | Time | Result |
## Tether friction
## Progress log
## Next steps
## Sessions
```
