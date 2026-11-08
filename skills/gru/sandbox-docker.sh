#!/usr/bin/env bash
# Run a minion command in a throwaway container (macOS, native Windows, or any stage that needs real services).
# Usage: sandbox-docker.sh <worktree> <image> -- <cmd...>
# Env:   GRU_DOCKER_NET=<network>  join this docker network (e.g. the compose project Gru started for the card)
#        GRU_DOCKER_MEM=4g         memory limit (default 4g)     GRU_DOCKER_PIDS=512   pids limit
#        GRU_SANDBOX_RW="p1:p2"    extra writable bind mounts    GRU_SANDBOX_RO="p1:p2"  extra read-only mounts
# Only the worktree (and a worktree's git dir) is writable; no host $HOME, no docker socket, all capabilities dropped.
# The network stays on (the model API needs it). UNTESTED on macOS/Windows: see docs/guide/sandbox.md.
set -eu
wt="$(cd "$1" && pwd)"; image="$2"; shift 2; [ "${1:-}" = "--" ] && shift
command -v docker >/dev/null || { echo "gru sandbox: docker missing, refusing to run unsandboxed" >&2; exit 127; }
docker info >/dev/null 2>&1 || { echo "gru sandbox: docker daemon not running, refusing to run unsandboxed" >&2; exit 127; }
args=(run --rm --init --cap-drop ALL --security-opt no-new-privileges
      --memory "${GRU_DOCKER_MEM:-4g}" --pids-limit "${GRU_DOCKER_PIDS:-512}"
      --user "$(id -u):$(id -g)" -e HOME=/tmp/gruhome --tmpfs /tmp:exec,mode=1777
      -v "$wt:$wt" -w "$wt")
[ -n "${GRU_DOCKER_NET:-}" ] && args+=(--network "$GRU_DOCKER_NET")
# a git worktree's .git file points into the main repo: expose that read-only and the worktree's git dir writable
if [ -f "$wt/.git" ]; then g="$(sed -n 's/^gitdir: //p' "$wt/.git")"; c="$(dirname "$(dirname "$g")")"; args+=(-v "$c:$c:ro" -v "$g:$g"); fi
IFS=: read -ra extra <<< "${GRU_SANDBOX_RW:-}"
for p in "${extra[@]}"; do [ -n "$p" ] && args+=(-v "$p:$p"); done
IFS=: read -ra ro <<< "${GRU_SANDBOX_RO:-}"
for p in "${ro[@]}"; do [ -n "$p" ] && args+=(-v "$p:$p:ro"); done
exec docker "${args[@]}" "$image" "$@"
