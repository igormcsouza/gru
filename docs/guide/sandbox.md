# Sandbox

Minions never run bare. Gru picks the isolation **per stage**, not per card, and the [preview](task-cards.md#preview) shows the choice. Set it in `local.yml`:

```yaml
sandbox: {default: bwrap, qa: docker}   # keys: default, plan, tests, build, gate, qa, review
```

| Platform | Default | Notes |
|---|---|---|
| Linux, WSL2 on Windows | `bwrap` | Docker optional, recommended for QA that needs services |
| macOS | `docker` | `bwrap` does not exist there; Docker (or Colima, Podman) is **required** |
| Native Windows | `docker` | Required. WSL2 counts as Linux |

The [interview](setup.md) detects your OS and stops with install guidance if a required backend is missing. Gru never runs a minion unsandboxed on its own.

!!! warning "Docker path is untested on macOS and Windows"
    It is written to be correct but nobody has run it there yet. Reports welcome; there is an open question about Claude login inside containers on macOS ([#8](https://github.com/igormcsouza/gru/issues/8)).

## bwrap

`skills/gru/sandbox.sh`, a [bubblewrap](https://github.com/containers/bubblewrap) wrapper:

```bash
sandbox.sh <worktree> -- <command...>
```

- `$HOME` is an empty tmpfs: no ssh keys, cloud credentials or other repos. The rest of the filesystem is read-only; only the worktree is writable.
- Own pid, ipc and uts namespaces and a new session.
- The network stays on, because the model API needs it. `GRU_SANDBOX_NET=private` gives an empty loopback-only network instead: Gru uses it for commands **it** runs (gate, checks, e2e), so parallel cards never collide on ports.
- A git worktree's main repo is exposed read-only and its git dir writable.
- `GRU_SANDBOX_RW="p1:p2"` / `GRU_SANDBOX_RO="p1:p2"` add writable / read-only paths. In cloud containers Claude Code's shell tool may need `/sys/fs/cgroup` writable; `selftest` detects it and, with your OK, records it as `sandbox_rw` in `local.yml`. Without `bwrap` it exits 127 and refuses to run.

tether minions use tether's own `workspace-write` sandbox, which blocks `.git` and the network.

## Docker

`skills/gru/sandbox-docker.sh <worktree> <image> -- <command...>` runs a throwaway `docker run --rm`: all capabilities dropped, `no-new-privileges`, memory and pid limits, your uid, only the worktree writable, **no Docker socket, ever**. Network stays on; `GRU_DOCKER_NET` joins a card's compose network.

Use it for any stage on macOS and native Windows, and on Linux for the **QA stage** when a card needs real services (databases, queues, browsers, compose). A card declares `needs: [postgres]`; Linux without Docker keeps `bwrap` and tells you that real services are out of reach.

### The image

Resolved once per project, in this order, and stored under `<store>/images/` (**never versioned**):

1. **Your project's own definition**, used as is (devcontainer, a documented development Dockerfile, a compose test service).
2. **Otherwise Gru builds one**: a generic base for the detected stack, plus the harness CLIs your slots use, plus your install command run once. It shows you the Dockerfile and asks once, tags the image with a hash of the lockfiles and rebuilds when that changes. No secrets go into an image.

### Services

Gru starts them, not the minion: `docker compose -p gru-<feature>-<card> up -d --wait`, ports remapped, torn down when the stage ends. The minion's container joins that network and sees only the workspace and the service hostnames.
