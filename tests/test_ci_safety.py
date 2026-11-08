"""CI must stay free, offline and deterministic: no secrets, no model calls, evals refuse to run in CI."""
import os
import re
import subprocess
import sys

from conftest import ROOT, read


def test_workflows_use_no_secrets_and_no_models():
    for wf in [*(ROOT / ".github" / "workflows").glob("*.yml"), *(ROOT / "ci").glob("*.yml")]:
        text = read(wf)
        assert set(re.findall(r"secrets\.([A-Za-z_]+)", text)) <= {"GITHUB_TOKEN"}, wf.name
        assert not re.search(r"anthropic|claude|evals/|openai", text, re.I), f"{wf.name} must not call models"


def test_ci_runs_the_static_suite_on_pull_requests():
    # the template in ci/ is what gets installed as .github/workflows/ci.yml
    live = ROOT / ".github" / "workflows" / "ci.yml"
    ci = read(live if live.exists() else ROOT / "ci" / "ci.yml")
    assert "pull_request" in ci and "pytest" in ci and "mkdocs build --strict" in ci


def test_tests_make_no_model_calls():
    for t in (ROOT / "tests").glob("test_*.py"):
        if t.name == "test_ci_safety.py":
            continue
        text = read(t)
        assert not re.search(r"import anthropic|from anthropic|import openai", text), t.name
        assert not re.search(r"\[\s*[\"']claude[\"']", text), f"{t.name} must not run the claude CLI"


def test_evals_refuse_to_run_in_ci():
    for script in ("quiz.py", "scenarios.py"):
        r = subprocess.run([sys.executable, str(ROOT / "evals" / script)], env={**os.environ, "CI": "true"}, capture_output=True, text=True, timeout=60)
        assert r.returncode != 0, script
        assert "local-only" in (r.stderr + r.stdout), script


def test_evals_dry_run_is_offline_and_lists_work():
    r = subprocess.run([sys.executable, str(ROOT / "evals" / "quiz.py"), "--dry-run"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0 and "calls with --repeats" in r.stdout


def test_every_quiz_question_points_at_real_files():
    import yaml

    for q in yaml.safe_load(read(ROOT / "evals" / "quiz.yml")):
        assert {"id", "load", "question", "expect"} <= set(q), q.get("id")
        re.compile(q["expect"])
        for f in q["load"]:
            assert (ROOT / "skills" / "gru" / f).exists(), f"{q['id']} loads missing {f}"


def test_scenarios_are_well_formed():
    import yaml

    kinds = {"no_path", "path_exists", "file_contains", "file_equals", "git_clean", "result_matches", "result_not_matches", "no_tool", "no_bash", "preview_matches_matrix"}
    for p in (ROOT / "evals" / "scenarios").glob("*.yml"):
        sc = yaml.safe_load(read(p))
        assert sc["name"] == p.stem and sc["turns"], p.name
        for turn in sc["turns"]:
            assert turn["say"].strip()
            for a in turn.get("asserts", []):
                assert a["type"] in kinds, f"{p.name}: {a['type']}"
