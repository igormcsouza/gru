#!/usr/bin/env bash
# Run a minion command with only <worktree> writable. Usage: sandbox.sh <worktree> -- <cmd...>
# Hides $HOME (ssh keys, cloud creds, other repos); re-binds only what opencode needs.
# Network stays on (the model API needs it). Extra RW paths: GRU_SANDBOX_RW="p1:p2"; extra read-only: GRU_SANDBOX_RO="p1:p2".
set -eu
wt="$(cd "$1" && pwd)"; shift; [ "${1:-}" = "--" ] && shift
command -v bwrap >/dev/null || { echo "gru sandbox: bwrap missing, refusing to run unsandboxed" >&2; exit 127; }
args=(--ro-bind / / --dev /dev --proc /proc --tmpfs /tmp --tmpfs "$HOME" --die-with-parent --chdir "$wt" --bind "$wt" "$wt")
for p in "$HOME/.opencode" "$HOME/.config/opencode"; do [ -e "$p" ] && args+=(--ro-bind "$p" "$p"); done
for p in "$HOME/.local/share/opencode" "$HOME/.local/state/opencode" "$HOME/.cache/opencode"; do
  mkdir -p "$p"; args+=(--bind "$p" "$p")
done
# a git worktree's .git file points into the main repo: expose that read-only so `git status` works
if [ -f "$wt/.git" ]; then g="$(sed -n 's/^gitdir: //p' "$wt/.git")"; c="$(dirname "$(dirname "$g")")"; args+=(--ro-bind "$c" "$c" --bind "$g" "$g"); fi
IFS=: read -ra extra <<< "${GRU_SANDBOX_RW:-}"
for p in "${extra[@]}"; do [ -n "$p" ] && args+=(--bind "$p" "$p"); done
IFS=: read -ra ro <<< "${GRU_SANDBOX_RO:-}"
for p in "${ro[@]}"; do [ -n "$p" ] && args+=(--ro-bind "$p" "$p"); done
exec bwrap "${args[@]}" -- "$@"
