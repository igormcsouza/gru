# Troubleshooting

**`/gru` unknown.** Skills load at session start. Check `ls -l ~/.claude/skills/gru`, then start a new session.

**`SKIPPED ... exists and is not a symlink`.** A real file or directory already has that name in your skills or agents folder. Move it away and rerun the installer.

**`gru sandbox: bwrap missing, refusing to run unsandboxed`.** Install bubblewrap (`sudo apt install bubblewrap`). Gru will not run opencode without it.

**tether MCP tools missing.** The installer registers it at user scope; check `claude mcp get tether`, and that `uv` and `tether --version` work. Restart the session.

**`NVIDIA_API_KEY` warning.** Export it in `~/.profile`; the installer only checks that it exists.

**A minion hangs or loops.** Gru enforces `timeout_min` (default 10) and treats a stall as a failed gate. Run `/gru selftest` to see whether opencode needs `--standalone` here.

**A tether run failed.** Expected sometimes. If it was tether's fault, Gru logs a `Tether friction` entry, reruns that stage on Claude Code and asks before filing an issue on the tether repo. If it was not (bad card, auth, quota), it is handled as a normal failure.

**The interview runs again.** It runs when your `local.yml` is missing or older than version 2 (a fresh clone has none, because it is git-ignored) (for example after upgrading from the tier-based Gru). Your old `.claude/gru.json` is migrated.

**Cards run one at a time.** A `limits` rule (local model, rate-limited provider), a dependency or shared files forces it. The preview shows why.

**Lost track after closing the terminal.** `/gru resume` reads the log and re-attaches or restarts in-flight minions at their recorded slot.

**Worktrees left behind.** `/gru done` lists and removes only what the feature created; unpushed work is kept and listed.
