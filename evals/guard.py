"""Hard guard: model-backed evals are LOCAL ONLY. They refuse to run in CI and never run by accident."""
import os
import shutil
import sys

CI_VARS = ("CI", "GITHUB_ACTIONS", "BUILDKITE", "GITLAB_CI", "JENKINS_URL", "CIRCLECI")


def require_local(estimate: str) -> None:
    if any(os.environ.get(v) for v in CI_VARS):
        sys.exit("evals call a real model and are local-only: refusing to run in CI.")
    if not shutil.which("claude"):
        sys.exit("evals need the `claude` CLI, logged in on this machine.")
    print(f"[evals] real model calls ahead, estimated cost: {estimate}. Ctrl-C to stop.", file=sys.stderr)
