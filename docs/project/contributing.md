# Contributing

Gru is a prompt (`skills/gru/SKILL.md` plus on-demand files in `skills/gru/ref/`), one shell script (`sandbox.sh`) and five role briefs in `agents/`. The full guide is [CONTRIBUTING.md](https://github.com/igormcsouza/gru/blob/main/CONTRIBUTING.md).

- No project-specific facts in the repo.
- Verification stays deterministic and the orchestrator never trusts "done".
- Safety defaults (sandbox, outward-facing actions need the user's OK, no secrets in logs) stay on.
- Keep `SKILL.md` tight and load detail from `ref/` only when a step needs it: delete before you add.

```bash
bash -n install.sh skills/gru/sandbox.sh
uv sync --only-group docs && uv run mkdocs build --strict
```
