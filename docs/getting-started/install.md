# Install

## Requirements

| Needed for | What |
|---|---|
| Running Gru | [Claude Code](https://claude.com/claude-code) (the skill also runs in Codex; the tether MCP step is Claude-only) |
| Cheaper minions | [tether](https://pypi.org/project/tether-sdk/) (installed for you via [`uv`](https://docs.astral.sh/uv/)) and/or [opencode](https://opencode.ai) |
| Sandboxing (Linux, WSL2) | `bwrap` (bubblewrap): `sudo apt install bubblewrap`. Without a sandbox Gru refuses to run minions. |
| Sandboxing (macOS, native Windows) | Docker (Docker Desktop, Colima or Podman providing the `docker` CLI). Untested there so far. Also optional on Linux for QA with real services. |
| Delivery | `git` and `gh` for worktrees, branches and PRs |
| NVIDIA models | `NVIDIA_API_KEY` in your environment (`~/.profile`). Never printed or committed. |

## One command

```bash
curl -fsSL https://raw.githubusercontent.com/igormcsouza/gru/main/install.sh | bash
```

Choose the host with `... | bash -s -- --target claude|codex|both|other`. It clones to `~/.gru` (override with `--dir` or `GRU_HOME`) and symlinks:

- the skill (`SKILL.md` plus its `ref/` files) into `~/.claude/skills/gru` (Codex: `~/.agents/skills/gru`)
- the dev-team agents (`team-leader`, `planner`, `swe`, `qa`, `reviewer`) into `~/.claude/agents/`

For Claude Code it also runs `uv tool install --upgrade "tether-sdk[mcp]"`, adds an `nvidia` provider to `~/.tether/providers.yaml` if missing and registers the `tether` MCP server at user scope. Failures here warn and never abort.

It is idempotent and never overwrites a real file: a `SKIPPED` line means something real already uses that name, so move it away and rerun. Rerun to update.

## From a clone

```bash
git clone https://github.com/igormcsouza/gru.git ~/Projects/gru
~/Projects/gru/install.sh --target claude
```

## Verify

```bash
tether --version
ls -l ~/.claude/skills/gru ~/.claude/agents
```

Start a **new session** (skills and agents load at session start), then run `/gru` in a project: the first run interviews you, and `/gru selftest` checks the harnesses (once per machine and after upgrading one).
