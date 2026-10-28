# Troubleshooting

**`/gru` unknown.** Skills load at session start. Check `ls -l ~/.claude/skills/gru`, then start a new session.

**`SKIPPED ... exists and is not a symlink`.** A real file or directory already has that name in your skills or agents folder. Move it away and rerun the installer.

**`gru sandbox: bwrap missing, refusing to run unsandboxed`.** Install bubblewrap (`sudo apt install bubblewrap`). Gru will not run opencode without it.

**tether MCP tools missing.** The installer registers it at user scope; check `claude mcp get tether`, and that `uv` and `tether --version` work. Restart the session.

**`NVIDIA_API_KEY` warning.** Export it in `~/.profile`; the installer only checks that it exists.

**opencode hangs or loops.** Gru enforces `timeout_min` (default 10) and escalates on stall. Run `/gru selftest` to see whether `--standalone` is needed here.

**A tether run failed.** Expected sometimes: Gru logs a `Tether friction` entry and retries on opencode at the same tier.

**Lost track after closing the terminal.** `/gru resume` reads the log and re-attaches or restarts in-flight minions at their recorded tier.

**Worktrees left behind.** `/gru done` lists and removes only what the feature created; unpushed work is kept and listed.
