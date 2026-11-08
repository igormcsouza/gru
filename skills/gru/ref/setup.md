# Setup: the interview, config and selftest

Run this on the first `/gru` in a project, the first time with this Gru version (`version` < 2 or only a legacy `.claude/gru.json`), and on `/gru setup`. The goal is to know **the human and the project** so every role works the way they expect. Pre-fill everything the repo already answers (Makefile, `package.json`, `pyproject.toml`, CI, `git log`, `AGENTS.md`, `gh repo view`) and ask only the rest. Max 4 questions per round, each with a default; never guess. Show a short summary at the end and ask for a correction before writing.

If a legacy `.claude/gru.json` exists, migrate `claude_config_dir`, `sensitive` (map `min_tier` 0-1 to `weak`, 2 to `mid`, 3 to `strong`), `tether_repo`, `timeout_min`, `context`, `verified`; drop `tiers`. Tell the user the tier ladder is gone.

## 0. Does Gru leave files in this repo?
Ask first, because it decides where everything else is written. Say: "Should Gru leave anything in this repo? **team** (default): a small `gru.yml` policy and the project notes in `AGENTS.md`/`CLAUDE.md` are versioned so teammates share them. **none**: nothing is versioned and nothing in the repo changes; Gru keeps everything in a git-ignored store and leaves no trace in commits or PRs. Use `none` where people don't want Gru around." Record `versioning: team|none` in `local.yml`. A default in `profile.yml` (`versioning`) pre-selects the answer for new projects.
- `none` means: no `gru.yml` (its keys live in `local.yml` instead); project notes go to `<store>/project.md`, never `AGENTS.md`/`CLAUDE.md`; no `gru store:` line; the store's `.gitignore` is just `*` (it ignores itself too, so `git status` stays clean); commits, branches and PR text carry no mention of Gru; `done` writes lessons to `<store>/project.md` instead of offering them to `AGENTS.md`; Gru adds nothing to the repo's own `.gitignore`.

## 1. Models (strength slots)
Say: "Gru works with three strengths: **strong** (thinks, plans, reviews), **mid**, **weak** (types small, clear cards). Defaults: strong = Opus, mid = Sonnet, weak = Haiku. Stay on the defaults or change them?" If they change: ask for the model per slot (any model the chosen harness can run). Optionally a `strong_alt`: a second strong model from another family, used to review the work of a strong swe.

## 2. Harness for the minions
Say exactly this shape: "Which harness do you want for the minions? The default is **Claude Code**, but I suggest **tether** (recommended). If tether breaks on a card, I fall back to Claude Code for that card automatically and offer to report the problem to the tether repo." Accept `claude`, `tether`, `opencode` or another the user names.
- The answer sets `minion_harness`. A harness can only run the models it supports: for `tether`/`opencode` ask which of its models fill which slot (tether is usually best for `weak`, sometimes `mid`). Any slot left blank stays on `claude`. Do not move `strong` off a harness the user does not trust with it.
- If `tether`: ask for `tether_repo` (default `igormcsouza/tether`).

## 2b. Operating system and sandbox
Detect the OS (`uname -s`; on Linux check `/proc/version` for WSL). Linux and WSL2: default sandbox `bwrap` (check `bwrap --version`; if missing, tell the user how to install it). macOS and native Windows: **Docker is required** (anything providing the `docker` CLI and a running daemon); if missing, stop the interview with install guidance (Docker Desktop, Colima or Podman) and say the Docker path is untested there. Ask whether Docker should also be used for the **qa/e2e stage** (default yes if Docker is available and the project has e2e, services or compose). Ask for the **install command** and which services tests need, if the project did not already say. Image resolution and building are in `ref/sandbox.md`; the image files live under `<store>/images/` and are never versioned. Record `sandbox: {default: bwrap|docker, qa: bwrap|docker}`.
Ask whether any chosen model is **local** (e.g. a Qwen on this machine) or **rate-limited** (e.g. NVIDIA free tier). Record each as a `limits` entry. These force sequential or throttled scheduling, and the plan preview shows it.

## 4. The project (written to the project's `AGENTS.md`/`CLAUDE.md`, section `## Dev team specifics` for code, `## Feature context` otherwise; with `versioning: none` written to `<store>/project.md` instead)
One short line each: stack and layout; check commands (lint, types, tests, coverage gate); e2e/manual QA; branch, commit and PR style and **who merges**; delivery mode (PR per card, or waves/integration branch); **what "done" means in this team** (this feeds every definition of done); risky areas and hard stops (what always needs the user); design docs to read; where the **store** lives (`gru store:` line, default `<root>/.claude/gru/`; no line in `none` mode). Non-code projects: only a one-line project description and the store path.

## 4b. What you expect from QA and review (project-specific, not general)
Ask in the user's words, per stage, and write it with the project facts (same place as section 4):
- **QA expects**: what they want to see (scenario table, screenshots or recordings, performance numbers, particular environments or data), and where the report goes (terminal, PR comment).
- **Review expects**: beyond smells, edge cases and the definition of done, what else (security depth, API or schema compatibility, docs, changelog, test style, size limits).
- **Extra checks** for this project only, one per line: `<qa|review>: <what> [source: <tool>]`, e.g. `review: the linked Asana task exists and its acceptance criteria match the DoD [source: asana]`. Tool-backed checks are gathered by Gru with its own session's tools, not by the minions (`ref/standalone.md`, Expectations); ask which tool or connector each uses and whether Gru has it here. Do not generalize: record only what this project asked for, and add nothing the user did not say.
Offer to remember `permissions.post_reviews: ask|allow` (posting a review on a PR is outward-facing; default `ask`).

## 5. You (written to `~/.config/gru/profile.yml`, once per machine)
How the user likes to work, so Gru fits them: how they want questions (batched with recommendations, or one at a time); how much to decide alone (`autonomy`: `ask` = confirm bumps and splits, `bump_ok` = may bump a swe one slot within budget); review depth they expect; language/verbosity; whether to push-notify when blocked; machine specifics (`claude_config_dir` for a separate minion login). Offer to copy the model/harness answers into the profile so new projects start from them.

## 6. Write and check
Write `<store>/local.yml`, `<store>/gru.yml` (`team` mode only, and only if missing; never overwrite a teammate's policy without asking), the store's `.gitignore` (see ops.md, Store) and `~/.config/gru/profile.yml` (create dirs). Show a 6-line summary. Offer `selftest` (below) and run it if accepted. Then continue with the user's original request.

## Files

`<store>/local.yml` (**git-ignored**, yours: depends on your models, machine and history; no secrets):
```yaml
version: 2
versioning: team             # team | none (none: nothing versioned; gru.yml's keys below also live here)
sandbox: {default: bwrap, qa: docker}   # per stage: default, plan, tests, build, gate, qa, review; bwrap | docker | none
slots:
  strong: {model: opus,   harness: claude}
  mid:    {model: sonnet, harness: claude}
  weak:   {model: haiku,  harness: claude}
  strong_alt: null            # optional: other-family strong model, for reviewing strong swes
minion_harness: claude        # claude | tether | opencode | ...
size_slots: {XS: weak, S: weak, M: mid, L: strong, XL: strong}   # swe slot per size (calibration may suggest edits)
limits:                       # glob on harness:model
  - {match: "tether:ollama/*", max_parallel: 1, kind: local}
  - {match: "tether:nvidia/*", max_parallel: 2, rpm: 40}
context: {}                   # model -> context window tokens (unknown free models count as 32k)
prices: {}                    # optional $/Mtok per model; without it cost is shown in tokens
verified: {}                  # selftest results
calibration:
  history: []                 # one entry per closed card (ref/ops.md, Calibration)
  stats: {}                   # per "size/slot": n, first_pass, avg_replans, bumps
```
`<store>/gru.yml` (**versioned**, team policy: the same for everyone on the project; no secrets, no machine paths):
```yaml
version: 2
tether_repo: igormcsouza/tether
budget: {warn_tokens: 300000, stop_tokens: 400000}   # paid tokens; the preview may override per feature
timeout_min: 10
max_parallel: 3
sensitive: [{path: "infra/**", min_slot: mid}]       # free/third-party endpoints never see these below min_slot
permissions: {file_tether_issues: ask, post_reviews: ask}   # ask | allow
```
`~/.config/gru/profile.yml`: `versioning` (default for new projects), `autonomy`, `questions` (`batched|one`), `verbosity`, `notify`, `claude_config_dir`, plus optional default `slots`/`minion_harness`/`limits` for new projects.

## selftest
Prove each configured slot and harness works (a few cents). In a throwaway worktree run one trivial XS card ("create `hello.txt` containing `ok`") through every distinct slot+harness pair in `local.yml`, via `sandbox.sh` where it applies (`ref/harnesses.md`). Check and report in <=8 lines: the cwd is respected, the sandbox hides `~/.ssh` and writes outside the worktree fail, usage numbers are reported, the model name is valid, auth works, and whether `opencode run` needs `--standalone`. Record under `verified` (harness, model, date, usage-reporting yes/no), then delete the worktree. Add the sandbox checks from `ref/sandbox.md`. A pair that fails: say why, offer to fall back to `claude` for that slot, never silently.
