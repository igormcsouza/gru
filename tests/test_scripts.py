"""sandbox.sh and sandbox-docker.sh: the exact flags they pass, checked with recording shims.

No real bwrap or docker is needed (so these run anywhere, deterministically). A few optional
integration tests use a real bwrap and skip themselves when it cannot run.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import ROOT, SKILL_DIR

SANDBOX = SKILL_DIR / "sandbox.sh"
SANDBOX_DOCKER = SKILL_DIR / "sandbox-docker.sh"
BASH = shutil.which("bash")


def _shim(shim_dir: Path, name: str, record: Path, extra: str = "") -> None:
    p = shim_dir / name
    p.write_text(f'#!/bin/sh\n{extra}\nfor a in "$@"; do printf "%s\\n" "$a" >> "{record}"; done\nexit 0\n')
    p.chmod(0o755)


def _run(script, args, env_extra=None, path=None, home=None):
    env = {"PATH": path or os.environ["PATH"], "HOME": str(home or "/tmp/gru-test-home")}
    env.update(env_extra or {})
    return subprocess.run([BASH, str(script), *args], env=env, capture_output=True, text=True)


def _lines(record: Path):
    return record.read_text().splitlines() if record.exists() else []


def _has_seq(lines, *seq):
    return any(lines[i : i + len(seq)] == list(seq) for i in range(len(lines)))


@pytest.mark.parametrize("script", [SANDBOX, SANDBOX_DOCKER, ROOT / "install.sh"])
def test_bash_syntax(script):
    assert subprocess.run([BASH, "-n", str(script)], capture_output=True).returncode == 0


@pytest.mark.skipif(not shutil.which("shellcheck"), reason="shellcheck not installed")
def test_shellcheck_errors():
    r = subprocess.run(["shellcheck", "-S", "error", str(SANDBOX), str(SANDBOX_DOCKER), str(ROOT / "install.sh")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


# ---- sandbox.sh (bwrap) ----
@pytest.fixture
def bwrap(tmp_path, shim_dir):
    record = tmp_path / "bwrap.args"
    _shim(shim_dir, "bwrap", record)
    wt = tmp_path / "wt"
    wt.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    path = f"{shim_dir}:{os.environ['PATH']}"
    return record, wt, home, path


def test_bwrap_default_flags(bwrap):
    record, wt, home, path = bwrap
    r = _run(SANDBOX, [str(wt), "--", "echo", "hi"], path=path, home=home)
    assert r.returncode == 0, r.stderr
    lines = _lines(record)
    assert _has_seq(lines, "--ro-bind", "/", "/"), "root must be read-only"
    assert _has_seq(lines, "--tmpfs", str(home)), "HOME must be hidden"
    assert _has_seq(lines, "--bind", str(wt), str(wt)), "only the worktree is writable"
    for flag in ("--die-with-parent", "--unshare-pid", "--unshare-ipc", "--unshare-uts", "--new-session"):
        assert flag in lines, flag
    assert "--unshare-net" not in lines, "network stays on by default (the model API needs it)"
    assert lines[-3:] == ["--", "echo", "hi"] or lines[-3:] == ["--", "echo", "hi"][-3:]


def test_bwrap_private_network_only_on_request(bwrap):
    record, wt, home, path = bwrap
    _run(SANDBOX, [str(wt), "--", "true"], {"GRU_SANDBOX_NET": "private"}, path, home)
    assert "--unshare-net" in _lines(record)


def test_bwrap_extra_paths(bwrap, tmp_path):
    record, wt, home, path = bwrap
    rw, ro = tmp_path / "rw", tmp_path / "ro"
    rw.mkdir()
    ro.mkdir()
    _run(SANDBOX, [str(wt), "--", "true"], {"GRU_SANDBOX_RW": str(rw), "GRU_SANDBOX_RO": str(ro)}, path, home)
    lines = _lines(record)
    assert _has_seq(lines, "--bind", str(rw), str(rw))
    assert _has_seq(lines, "--ro-bind", str(ro), str(ro))


def test_bwrap_git_worktree_gets_repo_readonly_and_gitdir_writable(bwrap, tmp_path):
    record, wt, home, path = bwrap
    repo = tmp_path / "repo"
    repo.mkdir()
    git = lambda *a, cwd=repo: subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True, env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})
    git("init", "-q", "-b", "main")
    (repo / "f").write_text("x")
    git("add", "-A")
    git("commit", "-q", "-m", "i")
    linked = tmp_path / "linked"
    git("worktree", "add", "-q", "-b", "feat", str(linked))
    _run(SANDBOX, [str(linked), "--", "true"], path=path, home=home)
    lines = _lines(record)
    gitdir = [l for l in lines if "/.git/worktrees/" in l]
    assert gitdir, "worktree git dir must be exposed"
    assert _has_seq(lines, "--ro-bind", str(repo / ".git"), str(repo / ".git"))
    assert _has_seq(lines, "--bind", gitdir[0], gitdir[0])


def test_bwrap_missing_refuses_to_run_unsandboxed(tmp_path, bwrap):
    _, wt, home, _ = bwrap
    bin_dir = tmp_path / "bare"
    bin_dir.mkdir()
    for tool in ("sed", "dirname", "mkdir"):
        (bin_dir / tool).symlink_to(shutil.which(tool))
    r = _run(SANDBOX, [str(wt), "--", "echo", "SHOULD-NOT-RUN"], path=str(bin_dir), home=home)
    assert r.returncode == 127
    assert "refusing to run unsandboxed" in r.stderr
    assert "SHOULD-NOT-RUN" not in r.stdout


def _real_bwrap_works():
    b = shutil.which("bwrap")
    return bool(b) and subprocess.run([b, "--ro-bind", "/", "/", "true"], capture_output=True).returncode == 0


@pytest.mark.skipif(not _real_bwrap_works(), reason="real bwrap not usable here")
def test_real_bwrap_isolation(tmp_path):
    wt = tmp_path / "wt"
    wt.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    (home / "secret").write_text("x")
    run = lambda cmd, env=None: _run(SANDBOX, [str(wt), "--", "sh", "-c", cmd], env, home=home)
    assert run("echo ok > in.txt && cat in.txt").stdout.strip() == "ok"
    assert run("test -e $HOME/secret && echo visible || echo hidden").stdout.strip() == "hidden"
    outside = tmp_path / "outside.txt"
    run(f"echo x > {outside}")
    assert not outside.exists(), "writes outside the worktree must fail"
    # /proc/net/dev reflects the process network namespace (unlike /sys, which shows the mount-time one)
    ifaces = [l.split(":")[0].strip() for l in run("cat /proc/net/dev", {"GRU_SANDBOX_NET": "private"}).stdout.splitlines() if ":" in l]
    assert ifaces == ["lo"]


# ---- sandbox-docker.sh ----
@pytest.fixture
def docker(tmp_path, shim_dir):
    record = tmp_path / "docker.args"
    # `docker info` succeeds silently and records nothing; `docker run ...` records its args
    _shim(shim_dir, "docker", record, extra='[ "$1" = info ] && exit 0')
    wt = tmp_path / "wt"
    wt.mkdir()
    return record, wt, f"{shim_dir}:{os.environ['PATH']}"


def test_docker_security_flags(docker):
    record, wt, path = docker
    r = _run(SANDBOX_DOCKER, [str(wt), "img:1", "--", "pytest", "-q"], path=path)
    assert r.returncode == 0, r.stderr
    lines = _lines(record)
    assert lines[0] == "run"
    assert _has_seq(lines, "--cap-drop", "ALL")
    assert _has_seq(lines, "--security-opt", "no-new-privileges")
    assert "--rm" in lines and "--init" in lines
    assert _has_seq(lines, "--memory", "4g")
    assert _has_seq(lines, "--user", f"{os.getuid()}:{os.getgid()}")
    assert _has_seq(lines, "-v", f"{wt}:{wt}")
    assert not any("docker.sock" in l for l in lines), "the docker socket must never be mounted"
    assert not any(l.startswith("--privileged") for l in lines)
    assert lines[-3:] == ["img:1", "pytest", "-q"], "image then command, last"
    assert "--network" not in lines


def test_docker_network_and_limits_and_mounts(docker, tmp_path):
    record, wt, path = docker
    extra = tmp_path / "extra"
    extra.mkdir()
    env = {"GRU_DOCKER_NET": "gru-feat-c1_default", "GRU_DOCKER_MEM": "1g", "GRU_SANDBOX_RW": str(extra), "GRU_SANDBOX_RO": "/etc/hostname"}
    _run(SANDBOX_DOCKER, [str(wt), "img", "--", "true"], env, path)
    lines = _lines(record)
    assert _has_seq(lines, "--network", "gru-feat-c1_default")
    assert _has_seq(lines, "--memory", "1g")
    assert _has_seq(lines, "-v", f"{extra}:{extra}")
    assert _has_seq(lines, "-v", "/etc/hostname:/etc/hostname:ro")


def test_docker_daemon_down_refuses(tmp_path, shim_dir):
    (shim_dir / "docker").write_text('#!/bin/sh\n[ "$1" = info ] && exit 1\nexit 0\n')
    (shim_dir / "docker").chmod(0o755)
    wt = tmp_path / "wt"
    wt.mkdir()
    r = _run(SANDBOX_DOCKER, [str(wt), "img", "--", "echo", "NO"], path=f"{shim_dir}:{os.environ['PATH']}")
    assert r.returncode == 127 and "daemon not running" in r.stderr and "NO" not in r.stdout


def test_docker_missing_refuses(tmp_path):
    bare = tmp_path / "bare"
    bare.mkdir()
    for tool in ("sed", "dirname", "id"):
        (bare / tool).symlink_to(shutil.which(tool))
    wt = tmp_path / "wt"
    wt.mkdir()
    r = _run(SANDBOX_DOCKER, [str(wt), "img", "--", "true"], path=str(bare))
    assert r.returncode == 127 and "docker missing" in r.stderr
