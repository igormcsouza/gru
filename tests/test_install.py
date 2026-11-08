"""install.sh: links, idempotency, cleanup of removed agents, never overwriting real files. Offline."""
import os
import shutil
import subprocess

from conftest import AGENTS_DIR, ROOT


def _copy_repo(dst):
    # a copy without .git so the installer never tries `git pull` (no network in tests)
    for item in ("skills", "agents", "install.sh"):
        src = ROOT / item
        (shutil.copytree if src.is_dir() else shutil.copy)(src, dst / item)
    return dst


def _install(repo, home, skills, agents):
    return subprocess.run(
        ["bash", str(repo / "install.sh"), "--target", "other", "--skills", str(skills), "--agents", str(agents), "--dir", str(repo)],
        env={"PATH": os.environ["PATH"], "HOME": str(home)}, capture_output=True, text=True,
    )


def test_install_links_skill_and_all_agents(tmp_path):
    repo = _copy_repo(tmp_path / "repo")
    skills, agents = tmp_path / "s", tmp_path / "a"
    r = _install(repo, tmp_path, skills, agents)
    assert r.returncode == 0, r.stderr
    assert (skills / "gru").is_symlink() and (skills / "gru" / "SKILL.md").exists()
    assert (skills / "gru" / "ref" / "setup.md").exists(), "ref/ files must come along with the skill"
    for f in AGENTS_DIR.glob("*.md"):
        assert (agents / f.name).is_symlink()


def test_install_is_idempotent(tmp_path):
    repo = _copy_repo(tmp_path / "repo")
    skills, agents = tmp_path / "s", tmp_path / "a"
    _install(repo, tmp_path, skills, agents)
    r = _install(repo, tmp_path, skills, agents)
    assert r.returncode == 0 and "linked" not in r.stdout.replace("relinked", "")


def test_install_removes_dangling_link_of_deleted_agent(tmp_path):
    repo = _copy_repo(tmp_path / "repo")
    skills, agents = tmp_path / "s", tmp_path / "a"
    agents.mkdir()
    (agents / "architect.md").symlink_to(repo / "agents" / "architect.md")  # target does not exist
    r = _install(repo, tmp_path, skills, agents)
    assert r.returncode == 0
    assert not (agents / "architect.md").is_symlink()


def test_install_never_overwrites_a_real_file(tmp_path):
    repo = _copy_repo(tmp_path / "repo")
    skills, agents = tmp_path / "s", tmp_path / "a"
    agents.mkdir()
    (agents / "swe.md").write_text("mine")
    r = _install(repo, tmp_path, skills, agents)
    assert r.returncode == 1 and "SKIPPED" in r.stdout
    assert (agents / "swe.md").read_text() == "mine"
