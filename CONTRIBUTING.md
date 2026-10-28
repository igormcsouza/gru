# Contributing to Gru

Gru is a skill (Markdown prompts) plus one shell script and five agent briefs. Both prompt and script changes get review.

## Ground rules

- **No project-specific facts in the repo.** Stacks, paths, repo names and channel names belong in the consuming project's `AGENTS.md`/`CLAUDE.md`.
- **Verify, never trust.** Prompts must make the orchestrator check files, tests and diffs itself instead of believing a minion's "done".
- **Safety stays default-on.** Minions run sandboxed; Tier 3 needs explicit OK; no secrets in logs or briefs. Do not weaken these.
- **Keep SKILL.md tight.** It is read on every run. Delete before you add.

## Setup and checks

```bash
git clone https://github.com/igormcsouza/gru.git && cd gru && ./install.sh --target claude
bash -n install.sh skills/gru/sandbox.sh
uv sync --only-group docs && uv run mkdocs build --strict   # if you touched docs/
```

Install is symlinks, so edits are live after a new session. Run `/gru selftest` after changing routing or the sandbox, and say in the PR what you ran and what you could not verify.

## License

By contributing you agree that your work is released under the [MIT license](LICENSE).
