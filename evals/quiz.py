#!/usr/bin/env python3
"""Spec quiz (LOCAL ONLY, real model calls, cents to ~$1).

For each question the model sees ONLY the skill files Gru would have loaded at that step and must
answer in one line; a regex decides pass/fail. A wrong answer usually means the text is ambiguous,
or that the answer lives in a file that would not be loaded yet (the progressive-disclosure check).

  python evals/quiz.py [--model haiku] [--repeats 3] [--only ID ...] [--dry-run]
"""
import argparse
import concurrent.futures as cf
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from guard import require_local  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "gru"
PROMPT = """You are Gru, an orchestrator. Below are the ONLY instruction files you have loaded at this step.
Answer the question using them alone, in at most two short sentences. If the files do not say, answer "UNKNOWN".

{files}

Question: {question}"""


def ask(q, model):
    files = "\n\n".join(f"===== {f} =====\n{(SKILL / f).read_text()}" for f in q["load"])
    with tempfile.TemporaryDirectory() as cwd:
        r = subprocess.run(
            ["claude", "-p", PROMPT.format(files=files, question=q["question"]), "--model", model,
             "--output-format", "json", "--no-session-persistence", "--tools", ""],
            cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=180,
        )
    d = json.loads(r.stdout)
    return d["result"], d.get("total_cost_usd", 0.0)


def judge(q, answer):
    ok = re.search(q["expect"], answer, re.I | re.S) is not None
    if "forbid" in q and re.search(q["forbid"], answer, re.I | re.S):
        ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--pass-ratio", type=float, default=0.6, help="share of repeats that must pass (0.6 = 2 of 3)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    qs = [q for q in yaml.safe_load((Path(__file__).parent / "quiz.yml").read_text()) if not a.only or q["id"] in a.only]
    calls = len(qs) * a.repeats
    if a.dry_run:
        for q in qs:
            tokens = sum(len((SKILL / f).read_text()) for f in q["load"]) // 4
            print(f"{q['id']:<28} loads {q['load']} (~{tokens} tokens)")
        print(f"{calls} calls with --repeats {a.repeats}")
        return 0
    require_local(f"{calls} calls on {a.model}, roughly ${calls * 0.004:.2f}")
    jobs = [(q, i) for q in qs for i in range(a.repeats)]
    results, total = {}, 0.0
    with cf.ThreadPoolExecutor(4) as ex:
        for (q, _), fut in [(j, ex.submit(ask, j[0], a.model)) for j in jobs]:
            ans, cost = fut.result()
            total += cost
            results.setdefault(q["id"], []).append((judge(q, ans), ans.strip().replace("\n", " ")))
    failed = 0
    for q in qs:
        rs = results[q["id"]]
        ratio = sum(ok for ok, _ in rs) / len(rs)
        good = ratio >= a.pass_ratio
        failed += not good
        print(f"{'PASS' if good else 'FAIL'} {q['id']:<28} {sum(ok for ok, _ in rs)}/{len(rs)}")
        if not good:
            for ok, ans in rs:
                print(f"     {'ok ' if ok else 'BAD'} {ans[:200]}")
    print(f"\n{len(qs) - failed}/{len(qs)} questions passed, cost ${total:.3f}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
