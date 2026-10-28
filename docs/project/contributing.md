# Contributing

Gru is a prompt (`skills/gru/SKILL.md`), one shell script (`sandbox.sh`) and five agent briefs. The full guide is [CONTRIBUTING.md](https://github.com/igormcsouza/gru/blob/main/CONTRIBUTING.md).

- No project-specific facts in the repo.
- Verification stays deterministic and the orchestrator never trusts "done".
- Safety defaults (sandbox, Tier 3 needs your OK, no secrets in logs) stay on.
- Keep `SKILL.md` tight: delete before you add.

```bash
bash -n install.sh skills/gru/sandbox.sh
uv sync --only-group docs && uv run mkdocs build --strict
```
