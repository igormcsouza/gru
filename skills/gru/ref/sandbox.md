# Sandbox: per-stage isolation, Docker path, images, services

Read this when dispatching a stage, during `selftest`, or when the setup asks about sandboxing. `local.yml` has `sandbox: {default: bwrap, qa: docker}` (keys: `default` and any stage `plan|tests|build|gate|qa|review`). The preview shows the choice per card; the user can override it.

## Backends
- **bwrap** (`sandbox.sh`): Linux and WSL2. Hides `$HOME`, rest of the filesystem read-only, only the worktree writable, own pid/ipc/uts namespaces. Network on (the model API needs it). `GRU_SANDBOX_NET=private` gives an empty loopback-only network: use it for commands **you** run (gate, project checks, e2e driven by Gru), never for a minion that must reach a model API. Each card then has its own loopback, so parallel cards never collide on ports.
- **docker** (`sandbox-docker.sh <worktree> <image> -- cmd`): macOS, native Windows, or any stage that needs real services (databases, queues, browsers, compose). Throwaway `docker run --rm`: caps dropped, no-new-privileges, memory/pids limits, only the worktree writable, **no docker socket, ever**. Podman, Colima or Docker Desktop all work if they provide the `docker` CLI. The Docker path is **untested on macOS and Windows**; say so when you use it there, and see issue #8 for the open Claude-auth question.
- **none**: only if the user chose it explicitly; log it.
- No backend available for a stage: stop and ask. Never run a minion unsandboxed on your own.

## Choosing per stage
Defaults: `plan` and `review` need no write access (read-only worktree is enough; use the default backend). `tests`, `build`, `gate`: the default backend. `qa`: `docker` if the card declares `needs: [services]` or the project has e2e/compose and Docker is available; otherwise the default. Linux without Docker keeps `bwrap` and says that real services are out of reach. Windows (native) and macOS: `docker` is required for every stage; setup stops with install guidance if it is missing.

## The image (only when a stage uses docker)
Resolve once per project, in this order; store everything under `<store>/images/` (git-ignored, never committed):
1. **The project's own definition**, used as is: `.devcontainer/devcontainer.json` image or Dockerfile, a `Dockerfile` the project documents for development/tests, or a compose service named for tests. Prefer what the project's docs name.
2. **Otherwise Gru builds one.** Detect the stack (lockfiles, manifests), pick a generic official base for it, add the harness CLIs the configured slots need (claude, opencode, tether), and run the install command from the interview once. Write `<store>/images/Dockerfile`, **show it and ask once**, then `docker build -t gru-<project>:<hash> -f <store>/images/Dockerfile <root>`, where `<hash>` is the hash of the lockfiles and the Dockerfile. Record `image`, `hash`, `built` in `<store>/images/image.yml`. Rebuild (ask not needed) when the hash changes; prune old `gru-<project>:*` tags with the user's OK in `done`.
Secrets are never baked into an image or passed as build args.

## Services (Gru starts them, not the minion)
If a card needs services and the project defines them (compose file): Gru runs `docker compose -p gru-<slug>-<card> up -d --wait <services>` with ports remapped to free host ports (and none published when only the container needs them), sets `GRU_DOCKER_NET=gru-<slug>-<card>_default` so the stage's container joins that network, gives the card the service hostnames, and tears it down (`down -v`) when the stage ends or the card is parked. The minion sees only the workspace and the service hostnames. No compose file: the card says what it needs and Gru asks the user how to provide it.

## selftest additions
Per backend actually configured: the sandbox hides `~/.ssh` (or `$HOME`) and writes outside the worktree fail; the model API is reachable; with `GRU_SANDBOX_NET=private` an outside host is unreachable; for docker: the image runs as the invoking uid, the docker socket is not visible, and (if services are configured) a compose project comes up and goes down cleanly. Record under `verified`.
