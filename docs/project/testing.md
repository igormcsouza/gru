# Testing

Gru is mostly English, so testing it has two very different halves. They are kept apart on purpose.

## CI: static, offline, deterministic

`make test` (what the CI workflow runs on every PR; the workflow lives in `ci/ci.yml`, copy it to `.github/workflows/ci.yml` if it is not there yet) needs **no network, no secrets and no model calls**. A test that cannot be deterministic does not belong here.

| Suite | Checks |
|---|---|
| `test_structure.py` | Frontmatter of the skill and agents is valid YAML; every `ref/` file is referenced and every reference exists; scripts named in the text exist; every command in `SKILL.md` is documented; the docs nav matches the docs tree and links resolve; **token budgets** (`SKILL.md` and each `ref/` file) hold, which protects the load-only-what-a-step-needs design. |
| `test_consistency.py` | One fact, one place: the role matrix is identical in `SKILL.md` and the docs, obeys its own rule, and matches the default `size_slots`; every YAML block parses; `local.yml` and `gru.yml` keys never overlap; every `permissions.*` used exists; stage names, finding kinds and the replan cap agree everywhere; removed concepts (the old escalation ladder, the old planner agent name) do not come back; no secrets in the repo. |
| `test_scripts.py` | `sandbox.sh` and `sandbox-docker.sh` are run with **recording shims** for `bwrap` and `docker`, so the exact flags are asserted (read-only root, hidden `$HOME`, only the worktree writable, private network only on request, capabilities dropped, no Docker socket, refusal when the tool is missing). A real-`bwrap` test runs where bwrap works and skips otherwise. |
| `test_install.py` | The installer links the skill with its `ref/` files and all agents, is idempotent, removes the link of a deleted agent and never overwrites a real file. |
| `test_ci_safety.py` | Workflows use no secrets and never call a model; tests make no model calls; the evals refuse to run when `CI` is set. |

```bash
make test      # pytest, ~2 s
make docs      # mkdocs build --strict
make check     # both
```

## Local: model-backed evals

Prose cannot be unit tested, but its **effects** can be checked. These call a real model through your logged-in `claude`, cost money and are not deterministic, so they run **only on your machine** and refuse to start in CI.

- **Spec quiz** (`make quiz`, about $0.03 on Haiku). The model sees only the files Gru would have loaded at a step and answers one question with a known answer ("size S: who reviews?"). A wrong answer means the text is ambiguous or the answer lives in a file not yet loaded. Each question runs several times and must pass in 2 of 3.
- **Scenarios** (`make scenarios`, about $0.5 to $1). The real skill runs turn by turn against a throwaway project in a temp HOME and is judged on **artifacts and tool use**, not prose: files written, `git status`, YAML values, "no Agent tool used", "nothing dispatched before accept", and "the preview follows the role matrix".

```bash
python evals/quiz.py --dry-run          # what would run, no calls
python evals/quiz.py --only matrix-s-reviewer --repeats 5
python evals/scenarios.py --only interview_none_mode --show --keep
```

Add a question to `evals/quiz.yml` or a scenario to `evals/scenarios/` whenever a real run shows Gru misbehaving: that is how most of the rules in the skill were found.

Not yet covered: parallel scheduling with `limits`, the replan cap with a bump (needs fake minions), Docker with real services, and macOS/Windows.
