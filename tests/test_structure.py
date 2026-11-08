"""Structure of the skill, agents and docs: files exist, links resolve, budgets hold."""
import re

import yaml

from conftest import AGENTS_DIR, DOCS_DIR, REF_DIR, ROOT, SKILL_DIR, frontmatter, read

# token budgets are bytes/4, the same estimate Gru uses; they protect the "load only what a step needs" design
SKILL_BUDGET = 2200
REF_BUDGET = 3500


def test_skill_frontmatter():
    meta, _ = frontmatter(SKILL_DIR / "SKILL.md")
    assert meta["name"] == "gru"
    assert 40 < len(meta["description"]) < 1500


def test_agent_frontmatter():
    files = sorted(AGENTS_DIR.glob("*.md"))
    assert {f.stem for f in files} >= {"planner", "swe", "qa", "reviewer", "team-leader"}
    for f in files:
        meta, body = frontmatter(f)
        assert meta["name"] == f.stem, f
        assert meta.get("description"), f
        assert body.strip(), f


def test_no_stale_agents():
    assert not (AGENTS_DIR / "architect.md").exists()


def test_skill_references_every_ref_file_and_only_existing_ones():
    skill = read(SKILL_DIR / "SKILL.md")
    referenced = set(re.findall(r"ref/([a-z-]+)\.md", skill))
    on_disk = {p.stem for p in REF_DIR.glob("*.md")}
    assert referenced == on_disk, f"SKILL.md loads {referenced}, ref/ has {on_disk}"
    # any ref/x.md mention anywhere in the skill must exist
    for p in [SKILL_DIR / "SKILL.md", *REF_DIR.glob("*.md")]:
        for name in re.findall(r"ref/([a-z-]+)\.md", read(p)):
            assert (REF_DIR / f"{name}.md").exists(), f"{p.name} mentions missing ref/{name}.md"


def test_agent_briefs_named_in_harnesses_exist():
    text = read(REF_DIR / "harnesses.md")
    for role in re.findall(r"agents/([a-z-]+)\.md", text):
        assert (AGENTS_DIR / f"{role}.md").exists(), role


def test_scripts_named_in_skill_exist():
    text = read(SKILL_DIR / "SKILL.md") + "".join(read(p) for p in REF_DIR.glob("*.md"))
    for script in set(re.findall(r"\b(sandbox(?:-docker)?\.sh)\b", text)):
        assert (SKILL_DIR / script).exists(), script


def test_size_budgets():
    skill_tokens = len(read(SKILL_DIR / "SKILL.md").encode()) // 4
    assert skill_tokens <= SKILL_BUDGET, f"SKILL.md is ~{skill_tokens} tokens (budget {SKILL_BUDGET})"
    for p in REF_DIR.glob("*.md"):
        tokens = len(read(p).encode()) // 4
        assert tokens <= REF_BUDGET, f"{p.name} is ~{tokens} tokens (budget {REF_BUDGET})"


def _skill_commands():
    section = read(SKILL_DIR / "SKILL.md").split("## Commands", 1)[1].split("\n## ", 1)[0]
    names = set()
    for line in section.splitlines():
        if line.startswith("- `"):
            head = line.split(": ", 1)[0]  # everything before the description: one or more `commands`
            for span in re.findall(r"`([^`]+)`", head):
                names.update(n for n in span.split()[0].split("|") if not n.startswith("<"))
    return names


def test_every_skill_command_is_documented():
    names = _skill_commands()
    assert names >= {"status", "steer", "resume", "setup", "selftest", "done", "feedback", "qa", "review", "check", "run"}
    commands_doc = read(DOCS_DIR / "guide" / "commands.md")
    for n in names:
        assert f"/gru {n}" in commands_doc, f"/gru {n} missing from docs/guide/commands.md"


def test_mkdocs_nav_matches_docs_tree():
    cfg = yaml.safe_load(read(ROOT / "mkdocs.yml").replace("!!python/name:pymdownx.superfences.fence_code_format", "x"))
    in_nav = set()

    def walk(node):
        if isinstance(node, str):
            in_nav.add(node)
        elif isinstance(node, list):
            for n in node:
                walk(n)
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)

    walk(cfg["nav"])
    on_disk = {str(p.relative_to(DOCS_DIR)) for p in DOCS_DIR.rglob("*.md")}
    assert in_nav == on_disk, f"only in nav: {in_nav - on_disk}; only on disk: {on_disk - in_nav}"


def test_relative_markdown_links_resolve():
    for page in DOCS_DIR.rglob("*.md"):
        for target in re.findall(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)", read(page)):
            if target.startswith("http"):
                continue
            assert (page.parent / target).resolve().exists(), f"{page.relative_to(ROOT)} -> {target}"
