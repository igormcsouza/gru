# Feedback: help improve Gru itself

Gru is open source (`igormcsouza/gru`) and improves from real runs. When you learn something about **Gru itself**, record it and, with the user's OK, offer to file an issue.

## What counts
- A recipe, script or rule that failed or needed a workaround (a sandbox flag, a permission problem, a harness quirk).
- An instruction that was ambiguous, contradictory, or that you had to guess.
- The user corrected how Gru behaved ("no, do it this way") and it should be the default.
- A missing command, option or question in the interview; a repeated friction; calibration or estimates that are consistently off; an idea the user voiced.
Not Gru's fault, so not for this repo: bugs in the user's project, a model's mistake on one card, tether bugs (those go to the tether repo, `ref/harnesses.md`).

## Record
Append each to the log under `## Gru feedback` the moment you notice it: one line of what happened, what you expected, what would fix it. Keep collecting; do not interrupt the user for it.

## Offer
Offer **once per feature**, at the hand-back or in `done`, as a short list ("I noticed N things about Gru itself; want me to draft issues for them?"). Offer earlier only if it blocked the work, and always when the user runs `/gru feedback [note]` (their note is the first item). `permissions.file_gru_issues` in `gru.yml`/`local.yml`: `ask` (default), `never` (record only, stop offering), `allow` (file after showing the draft, still never without showing it).

## Draft
One issue per item (group tiny related ones). Title, then: **What happened**, **Expected**, **Suggested improvement**, **Environment** (OS, Gru commit via `git -C <skill-dir> rev-parse --short HEAD`, harness and model names, sandbox backend, `versioning` mode). Write it **generically**:
- No project or repo names, file paths, code, ticket ids, internal URLs, people, or secrets. Replace them with placeholders ("a Python project", "a tracker task").
- No log excerpts unless the user reviewed them. In `versioning: none` mode treat the whole project as confidential: describe the Gru behavior only.
- Search first: `gh issue list --repo igormcsouza/gru --search "<keywords>" --state all`. A duplicate gets an extra-evidence comment instead (also asked).

## File (outward-facing)
**Rule: never file an issue without first showing the user its full text and getting a yes.** Show every draft in full and ask. On yes: `gh issue create --repo igormcsouza/gru --title ... --body ...` (end the body with a line saying it was drafted by Gru with the user's approval). No `gh` or no auth: print the draft for the user to paste at `https://github.com/igormcsouza/gru/issues/new`. Record the issue links in the log. If the user declines, drop it; do not ask again for the same item.
