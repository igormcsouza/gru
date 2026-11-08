"""Shared helpers. Everything in tests/ is static and deterministic: no network, no model calls."""
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "gru"
REF_DIR = SKILL_DIR / "ref"
AGENTS_DIR = ROOT / "agents"
DOCS_DIR = ROOT / "docs"


def read(path) -> str:
    return Path(path).read_text(encoding="utf-8")


def fenced_blocks(text: str, lang: str):
    """Yield the bodies of ```lang fenced blocks."""
    for m in re.finditer(rf"```{lang}\n(.*?)```", text, re.S):
        yield m.group(1)


def frontmatter(path):
    text = read(path)
    assert text.startswith("---\n"), f"{path} has no frontmatter"
    end = text.index("\n---\n", 4)
    return yaml.safe_load(text[4:end]), text[end + 5 :]


def all_text_files():
    skip = {".git", ".venv", "site", "__pycache__", "node_modules"}
    for p in ROOT.rglob("*"):
        if p.is_file() and not (set(p.relative_to(ROOT).parts) & skip) and p.suffix in {".md", ".yml", ".yaml", ".sh", ".toml"}:
            yield p


@pytest.fixture
def shim_dir(tmp_path):
    d = tmp_path / "shims"
    d.mkdir()
    return d
