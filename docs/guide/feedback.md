# Feedback to Gru

Gru improves from real runs. When it hits something about **itself** (a recipe that failed and needed a workaround, an instruction it had to guess, a correction you made that should be the default, a missing question in the interview), it writes it down in the feature log under `## Gru feedback`.

At the end of the feature (`done`), or when you run `/gru feedback [note]`, Gru offers once to turn those items into issues on [`igormcsouza/gru`](https://github.com/igormcsouza/gru/issues):

- **You see the full text first**, and nothing is filed without your yes.
- **Generic by design.** No project or repo names, paths, code, ticket ids, people or secrets. In `versioning: none` mode Gru describes only its own behavior. Each draft has what happened, what was expected, a suggested improvement, and the environment (OS, Gru commit, harness, models, sandbox).
- **No duplicates.** Gru searches the existing issues first and offers to add evidence to a match instead.
- **No `gh`?** Gru prints the draft so you can paste it.
- **Quiet if you want.** `permissions.file_gru_issues: never` records but stops offering.

Bugs in your own project, a model's mistake on a single card, and tether bugs are not Gru feedback; tether problems go to the tether repo as described in [Models, roles and harnesses](roles.md#when-tether-breaks).
