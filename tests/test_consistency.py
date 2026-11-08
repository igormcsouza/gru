"""One fact, one place: the same rules must agree across SKILL.md, ref/, agents/ and docs/."""
import re

import yaml

from conftest import AGENTS_DIR, DOCS_DIR, REF_DIR, ROOT, SKILL_DIR, all_text_files, fenced_blocks, read

STRENGTHS = ("weak", "mid", "strong")


def _matrix(text):
    """Parse a table whose first column is a size group (XS, S | M | L, XL) into {size: (swe, planner, qa, reviewer)}."""
    rows = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and re.fullmatch(r"(XS|S|M|L|XL)(, (XS|S|M|L|XL))*", cells[0]):
            roles = []
            for c in cells[1:5]:
                m = re.search(r"\b(weak|mid|strong)\b", c)
                assert m, f"no strength in cell {c!r}"
                roles.append(m.group(1))
            for size in cells[0].split(", "):
                rows[size] = tuple(roles)
    return rows


def test_role_matrix_is_identical_in_skill_and_docs():
    skill = _matrix(read(SKILL_DIR / "SKILL.md"))
    docs = _matrix(read(DOCS_DIR / "guide" / "roles.md"))
    assert set(skill) == {"XS", "S", "M", "L", "XL"}
    assert skill == docs


def test_role_matrix_obeys_its_own_rule():
    rank = {s: i for i, s in enumerate(STRENGTHS)}
    for size, (swe, planner, qa, reviewer) in _matrix(read(SKILL_DIR / "SKILL.md")).items():
        assert rank[planner] >= max(rank[swe], rank["mid"]), size
        if swe != "strong":  # nothing is stronger than strong, those rows rely on sign-off
            assert rank[qa] > rank[swe] and rank[reviewer] > rank[swe], size


def test_default_size_slots_match_matrix_swe_column():
    setup = read(REF_DIR / "setup.md")
    local = next(yaml.safe_load(b) for b in fenced_blocks(setup, "yaml") if "size_slots" in b)
    swe = {size: roles[0] for size, roles in _matrix(read(SKILL_DIR / "SKILL.md")).items()}
    assert local["size_slots"] == swe


def test_all_yaml_blocks_parse():
    for p in [*REF_DIR.glob("*.md"), *DOCS_DIR.rglob("*.md")]:
        for i, block in enumerate(fenced_blocks(read(p), "yaml")):
            try:
                yaml.safe_load(block)
            except yaml.YAMLError as e:  # pragma: no cover - message only
                raise AssertionError(f"{p.name} yaml block {i}: {e}")


def _schema():
    setup = read(REF_DIR / "setup.md")
    blocks = [yaml.safe_load(b) for b in fenced_blocks(setup, "yaml")]
    local = next(b for b in blocks if "slots" in b)
    team = next(b for b in blocks if "tether_repo" in b)
    return local, team


def test_schemas_have_a_version_and_split_keys():
    local, team = _schema()
    assert local["version"] == team["version"] == 2
    assert not (set(local) & set(team)) - {"version"}, "a key lives in both local.yml and gru.yml"
    assert {"slots", "minion_harness", "size_slots", "sandbox", "limits", "calibration", "versioning"} <= set(local)
    assert {"budget", "permissions", "sensitive", "timeout_min", "max_parallel", "tether_repo"} <= set(team)


def test_every_permission_mentioned_exists_in_schema():
    _, team = _schema()
    known = set(team["permissions"])
    text = "".join(read(p) for p in [SKILL_DIR / "SKILL.md", *REF_DIR.glob("*.md"), *DOCS_DIR.rglob("*.md")])
    for key in set(re.findall(r"permissions\.([a-z_]+)", text)):
        assert key in known, f"permissions.{key} is used but not in the gru.yml schema"


def test_stages_are_consistent():
    stages = {"plan", "tests", "build", "gate", "qa", "review"}
    sandbox_md = read(REF_DIR / "sandbox.md")
    run_md = read(REF_DIR / "run.md")
    for s in stages:
        assert f"`{s}`" in sandbox_md or f"{s}" in sandbox_md, s
        assert re.search(rf"\b{s}\b", run_md), s
    standalone = read(REF_DIR / "standalone.md")
    assert all(f"`{s}`" in standalone for s in stages)


def test_finding_kinds_everywhere_they_matter():
    for name in ("qa", "reviewer", "planner"):
        text = read(AGENTS_DIR / f"{name}.md").lower()
        assert "blocking" in text and "should-fix" in text, name
    for p in (REF_DIR / "run.md", DOCS_DIR / "guide" / "pipeline.md"):
        text = read(p)
        assert all(k in text for k in ("blocking", "should-fix", "note")), p.name


def test_store_gitignore_rule_is_stated_the_same_way():
    for p in (REF_DIR / "ops.md", DOCS_DIR / "guide" / "store.md"):
        text = read(p)
        assert "!gru.yml" in text and "!.gitignore" in text, p.name


def test_replan_cap_is_two_everywhere():
    for p in (SKILL_DIR / "SKILL.md", REF_DIR / "run.md", DOCS_DIR / "guide" / "pipeline.md"):
        assert re.search(r"(max(imum)?(?: of)? 2|at most 2|2 replans|Cap: 2)", read(p)), p.name


def test_removed_concepts_do_not_come_back():
    allowed_tier = {"setup.md", "troubleshooting.md"}  # migration notes only
    for p in all_text_files():
        if p.name in ("test_consistency.py", "uv.lock"):
            continue
        text = read(p)
        assert "architect" not in text.lower() or p.name == "install.sh", f"{p.relative_to(ROOT)} mentions architect"
        if p.suffix == ".md" and p.name not in allowed_tier:
            assert not re.search(r"\btiers?\b", text, re.I), f"{p.relative_to(ROOT)} mentions tiers"


def test_no_secrets_or_private_facts_in_repo():
    patterns = [r"sk-ant-[A-Za-z0-9_-]{10,}", r"ghp_[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"nvapi-[A-Za-z0-9_-]{10,}"]
    for p in all_text_files():
        text = read(p)
        for pat in patterns:
            assert not re.search(pat, text), f"{p.relative_to(ROOT)} matches {pat}"


def test_default_store_is_consistent():
    for p in (SKILL_DIR / "SKILL.md", REF_DIR / "ops.md", REF_DIR / "setup.md", DOCS_DIR / "guide" / "store.md"):
        text = read(p)
        assert "<root>/.claude/gru/` and tell" not in text, p.name  # old default creation text
    assert "<root>/.gru/" in read(REF_DIR / "ops.md")
