# Sandbox

`--auto` in opencode is not a sandbox. Gru runs opencode through `skills/gru/sandbox.sh`, a [bubblewrap](https://github.com/containers/bubblewrap) wrapper:

```bash
sandbox.sh <worktree> -- <command...>
```

- `$HOME` is replaced by an empty tmpfs: no ssh keys, cloud credentials or other repos.
- The whole filesystem is read-only except the task's worktree.
- opencode's own config and state dirs are re-bound (config read-only, state writable).
- For a git worktree, the main repo is exposed read-only and the worktree's git dir writable, so `git status` works.
- The network stays on, because the model API needs it.
- `GRU_SANDBOX_RW="p1:p2"` adds extra writable paths.
- If `bwrap` is missing the script exits 127 and **refuses to run unsandboxed**. Gru then asks you rather than bypassing it.

tether minions use tether's own `workspace-write` sandbox, which blocks `.git` and the network.
