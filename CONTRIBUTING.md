# Contributing to Gru

Gru is a skill (Markdown prompts: a small `SKILL.md` that loads `skills/gru/ref/*.md` on demand) plus two shell scripts (the sandboxes) and five role briefs in `agents/`. Both prompt and script changes get review.

## Ground rules

- **No project-specific facts in the repo.** Stacks, paths, repo names and channel names belong in the consuming project's `AGENTS.md`/`CLAUDE.md`.
- **Verify, never trust.** Prompts must make the orchestrator check files, tests and diffs itself instead of believing a minion's "done".
- **Safety stays default-on.** Minions run sandboxed; outward-facing actions need the user's OK; no secrets in logs or briefs. Do not weaken these.
- **Keep SKILL.md tight.** It is read on every run; put step detail in `ref/` so a run loads only what it needs. Delete before you add.

## Tests

`make test` is static, offline and deterministic: it is what CI runs and what you run before every PR. Model-backed checks (`make quiz`, `make scenarios`) are local-only and cost a little; see [docs/project/testing.md](docs/project/testing.md). Prompt changes should come with a quiz question or a scenario when a real run showed the problem.

## Setup and checks

```bash
git clone https://github.com/igormcsouza/gru.git && cd gru && ./install.sh --target claude
bash -n install.sh skills/gru/sandbox.sh skills/gru/sandbox-docker.sh
uv sync --only-group docs && uv run mkdocs build --strict   # if you touched docs/
```

Install is symlinks, so edits are live after a new session. Run `/gru selftest` after changing roles, harness recipes or the sandbox, and say in the PR what you ran and what you could not verify.

## Releases

Tag `vX.Y.Z`, then create the GitHub release and use **Generate release notes**: `.github/release.yml` groups merged PRs by label (`breaking`, `feature`, `bug`, `docs`, `tests`). Before publishing, make sure the notes have three parts: **What's new**, **Bug fixes** and **Breaking changes** (say what to do to migrate; write "None" if empty).

## License

By contributing you agree that your work is released under the [MIT license](LICENSE).
