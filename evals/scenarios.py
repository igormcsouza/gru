#!/usr/bin/env python3
"""Scenario evals (LOCAL ONLY, real model calls, roughly $0.3-1 per scenario).

Runs the real skill against a throwaway fixture project, turn by turn, and asserts on ARTIFACTS and
TOOL USE (files written, git status, yaml values, which tools were called), not on prose.
Nothing touches your real HOME or projects; a temp HOME and temp project are created and removed.

  python evals/scenarios.py [--only NAME ...] [--keep] [--model sonnet] [--dry-run]
Auth: uses your logged-in `claude` (a copy of ~/.claude/.credentials.json is placed in a 0700 temp dir
for the run and deleted after) or a token already in the environment.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from guard import require_local  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MATRIX = {"XS": ("weak", "mid", "mid", "mid"), "S": ("weak", "mid", "mid", "mid"), "M": ("mid", "strong", "strong", "strong"),
          "L": ("strong", "strong", "strong", "strong"), "XL": ("strong", "strong", "strong", "strong")}
MODEL_STRENGTH = {"haiku": "weak", "sonnet": "mid", "opus": "strong", "weak": "weak", "mid": "mid", "strong": "strong"}


# ---------- environment ----------
def build_fixture(proj: Path):
    (proj / "tests").mkdir(parents=True)
    (proj / "calc.py").write_text("def add(a, b):\n    return a + b\n\n\ndef div(a, b):\n    return a / b\n")
    (proj / "tests" / "test_calc.py").write_text("from calc import add\n\n\ndef test_add():\n    assert add(1, 2) == 3\n")
    (proj / "Makefile").write_text("test:\n\tpython -m pytest -q\n")
    (proj / "README.md").write_text("# calc\n")
    (proj / ".gitignore").write_text("__pycache__/\n")
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    for cmd in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "init"]):
        subprocess.run(["git", *cmd], cwd=proj, check=True, env=env, capture_output=True)


def preseed(proj: Path, home: Path):
    """Write a configured team-mode store, using the schema blocks from the repo's own setup.md."""
    blocks = [yaml.safe_load(b) for b in re.findall(r"```yaml\n(.*?)```", (ROOT / "skills/gru/ref/setup.md").read_text(), re.S)]
    local = next(b for b in blocks if "slots" in b)
    team = next(b for b in blocks if "tether_repo" in b)
    local["sandbox"] = {"default": "bwrap", "qa": "bwrap"}
    store = proj / ".gru"
    store.mkdir()
    (store / ".gitignore").write_text("*\n!.gitignore\n!gru.yml\n")
    (store / "local.yml").write_text(yaml.safe_dump(local, sort_keys=False))
    (store / "gru.yml").write_text(yaml.safe_dump(team, sort_keys=False))
    (proj / "AGENTS.md").write_text("## Dev team specifics\n- Stack: Python, flat layout.\n- Checks: `make test`.\n- Branches: one per card, the user merges, no remote.\n- Done means: make test green.\n- gru store: .gru/\n")
    prof = home / ".config" / "gru"
    prof.mkdir(parents=True)
    (prof / "profile.yml").write_text("versioning: team\nautonomy: ask\nquestions: batched\nverbosity: terse\nnotify: false\n")


def make_env(tmp: Path):
    home = tmp / "home"
    cfg = home / ".claude"
    (cfg / "skills").mkdir(parents=True)
    (cfg / "agents").mkdir()
    (cfg / "skills" / "gru").symlink_to(ROOT / "skills" / "gru")
    for f in (ROOT / "agents").glob("*.md"):
        (cfg / "agents" / f.name).symlink_to(f)
    cfg.chmod(0o700)
    real_creds = Path.home() / ".claude" / ".credentials.json"
    if real_creds.exists():
        shutil.copy(real_creds, cfg / ".credentials.json")
        (cfg / ".credentials.json").chmod(0o600)
    return home, {**os.environ, "HOME": str(home), "CLAUDE_CONFIG_DIR": str(cfg)}


# ---------- one turn ----------
def run_turn(env, proj, prompt, sid, model, max_turns=40, timeout=900):
    args = ["claude", "-p", prompt, "--model", model, "--output-format", "stream-json", "--verbose", "--permission-mode", "acceptEdits",
            "--allowedTools", "Bash Read Write Edit Glob Grep Skill", "--max-turns", str(max_turns)]
    if sid:
        args += ["--resume", sid]
    r = subprocess.run(args, cwd=proj, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=timeout)
    tools, bash, result, cost, session = [], [], "", 0.0, sid
    for line in r.stdout.splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") == "assistant":
            for b in d["message"].get("content", []):
                if b.get("type") == "tool_use":
                    tools.append(b["name"])
                    if b["name"] == "Bash":
                        bash.append(b["input"].get("command", ""))
        if d.get("type") == "result":
            result, cost, session = d.get("result", ""), d.get("total_cost_usd", 0.0), d.get("session_id", sid)
    return {"result": result, "tools": tools, "bash": bash, "cost": cost, "sid": session}


# ---------- assertions ----------
def git_dirty(proj):
    out = subprocess.run(["git", "status", "--porcelain"], cwd=proj, capture_output=True, text=True).stdout
    return [l for l in out.splitlines() if "__pycache__" not in l and ".pytest_cache" not in l]


def preview_roles_ok(text):
    """Every preview table row must follow the role matrix (models mapped to strengths)."""
    problems, rows_seen = [], 0
    header = None
    for line in text.splitlines():
        cells = [c.strip().strip("`*") for c in line.strip().strip("|").split("|")]
        low = [c.lower() for c in cells]
        if line.lstrip().startswith("|") and any("planner" in c for c in low) and any(c.startswith("size") for c in low):
            idx = {}
            for i, c in enumerate(low):
                for key, names in (("size", ("size",)), ("swe", ("swe",)), ("planner", ("planner",)), ("qa", ("qa",)), ("reviewer", ("reviewer",))):
                    if key not in idx and any(c.startswith(n) for n in names):
                        idx[key] = i
            combined = next((i for i, c in enumerate(low) if "swe" in c and "planner" in c and "/" in c), None)
            if combined is not None:  # one column "swe / planner / qa / reviewer"
                idx = {"size": idx.get("size"), "combined": combined}
                header = idx
                continue
            header = idx
            missing = {"size", "swe", "planner", "qa", "reviewer"} - set(idx)
            if missing:
                problems.append(f"preview table lacks columns {sorted(missing)}: {cells}")
                header = None
            continue
        if header and line.lstrip().startswith("|") and len(cells) > max(header.values()) and cells[header["size"]] in MATRIX:
            def strength(cell):
                m = re.search(r"\b(weak|mid|strong|haiku|sonnet|opus)\b", cell, re.I)
                return MODEL_STRENGTH[m.group(1).lower()] if m else None
            if "combined" in header:
                parts = re.split(r"\s/\s", cells[header["combined"]])
                got = tuple(strength(x) for x in parts) if len(parts) == 4 else (None,) * 4
            else:
                got = tuple(strength(cells[header[k]]) for k in ("swe", "planner", "qa", "reviewer"))
            rows_seen += 1
            if got != MATRIX[cells[header["size"]]]:
                problems.append(f"{cells[header['size']]}: got {got}, matrix says {MATRIX[cells[header['size']]]}")
    if not rows_seen:
        problems.append("no preview table found")
    return problems


def check(a, turn, proj):
    t = a["type"]
    p = lambda k="path": proj / a[k]
    if t == "no_path":
        return [f"{a['path']} exists"] if p().exists() else []
    if t == "path_exists":
        return [] if p().exists() else [f"{a['path']} missing"]
    if t == "file_contains":
        return [] if p().exists() and re.search(a["regex"], p().read_text(), re.M) else [f"{a['path']} !~ {a['regex']}"]
    if t == "file_equals":
        return [] if p().exists() and p().read_text().strip() == a["text"] else [f"{a['path']} != {a['text']!r}"]
    if t == "git_clean":
        d = git_dirty(proj)
        return [f"git status not clean: {d}"] if d else []
    if t == "result_matches":
        return [] if re.search(a["regex"], turn["result"], re.I | re.S) else [f"result !~ {a['regex']}"]
    if t == "result_not_matches":
        return [f"result ~ {a['regex']}"] if re.search(a["regex"], turn["result"], re.I | re.S) else []
    if t == "no_tool":
        bad = [x for x in turn["tools"] if x in a["names"]]
        return [f"forbidden tool used: {bad}"] if bad else []
    if t == "no_bash":
        bad = [c[:100] for c in turn["bash"] if re.search(a["regex"], c)]
        return [f"forbidden bash: {bad}"] if bad else []
    if t == "preview_matches_matrix":
        return preview_roles_ok(turn["result"])
    raise ValueError(f"unknown assertion {t}")


def run_scenario(sc, model, keep, show=False):
    tmp = Path(tempfile.mkdtemp(prefix="gru-eval-"))
    proj = tmp / "proj"
    build_fixture(proj)
    home, env = make_env(tmp)
    if sc.get("preseed"):
        preseed(proj, home)
    sid, failures, total = None, [], 0.0
    try:
        for i, turn_def in enumerate(sc["turns"], 1):
            turn = run_turn(env, proj, turn_def["say"], sid, model)
            sid, total = turn["sid"], total + turn["cost"]
            turn_failures = [f"turn {i}: {m}" for a in turn_def.get("asserts", []) for m in check(a, turn, proj)]
            failures += turn_failures
            if show and turn_failures:
                print(f"--- turn {i} result ---\n{turn['result']}\n--- tools: {turn['tools']}")
            if total > sc.get("max_cost", 2.0):
                failures.append(f"cost cap exceeded (${total:.2f})")
                break
    finally:
        if keep:
            print(f"   kept {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    return failures, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--show", action="store_true", help="print the model output of turns whose assertions failed")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    scs = [yaml.safe_load(p.read_text()) for p in sorted((Path(__file__).parent / "scenarios").glob("*.yml"))]
    scs = [s for s in scs if not a.only or s["name"] in a.only]
    if a.dry_run:
        for s in scs:
            print(f"{s['name']:<28} {len(s['turns'])} turns, cap ${s.get('max_cost', 2.0)}")
        return 0
    require_local(f"{len(scs)} scenario(s), roughly ${0.6 * len(scs):.1f}")
    bad = 0
    for s in scs:
        failures, cost = run_scenario(s, a.model, a.keep, a.show)
        bad += bool(failures)
        print(f"{'FAIL' if failures else 'PASS'} {s['name']:<28} ${cost:.2f}")
        for f in failures:
            print(f"     {f}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
