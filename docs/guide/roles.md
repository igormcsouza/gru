# Models, roles and harnesses

## Strong, mid, weak

You map three slots to models. Gru never cares about names, only about strength, so a stronger model can replace a slot at any time. Each card gets a **T-shirt size**, and the size picks the swe's slot:

| Size | Typical | swe |
|---|---|---|
| XS | one file, mechanical | weak |
| S | one module, clear spec | weak |
| M | several files, real design choices | mid |
| L | cross-cutting, tricky logic, migrations | strong |
| XL | probably two cards | strong |

Gru guesses the size; **you decide** in the preview, and can `steer` it later.

## Role matrix

Order: weak < mid < strong. Everyone who judges the work is stronger than the one who did it.

| Size | swe (tests and build) | planner | qa | reviewer |
|---|---|---|---|---|
| XS, S | weak | mid | mid | mid |
| M | mid | strong | strong | strong |
| L, XL | strong | strong | strong | strong + your sign-off |

- A weak swe gets a **mid** planner.
- `risk: high` (security, data, money, migrations) makes qa and reviewer strong.
- Nothing is stronger than a strong swe. Use a `strong_alt` model from another family as reviewer if you configured one; otherwise the strong reviewer runs and **you (or the calling agent) sign off**.
- The tests swe and the build swe are separate sessions, ideally on different models.

## Harnesses

Every role runs on a harness chosen in the [interview](setup.md): **Claude Code** (default), **tether** (recommended), **opencode** or another. A harness only runs models it supports, so a slot it cannot fill stays on Claude Code.

=== "claude"

    ```bash
    GRU_SANDBOX_RW=<claude_config_dir> sandbox.sh <worktree> -- env -u ANTHROPIC_API_KEY CLAUDE_CONFIG_DIR=<claude_config_dir> \
      timeout <timeout_min>m claude -p --model <model> --permission-mode acceptEdits --allowedTools "<tools>" --output-format json --no-session-persistence "<brief + card>"
    ```

    `<tools>` is `Bash Read Write Edit Glob Grep` for swe and qa, and `Bash Read Glob Grep` for planner and reviewer; the sandbox is the boundary. The sandbox hides `$HOME`, so use a separate `claude_config_dir` (log in there once), or a token in the environment. Your login in `claude_config_dir` so minion work stays off your main session's quota. Gru never logs in for you.

=== "opencode"

    ```bash
    sandbox.sh <worktree> -- timeout <timeout_min>m opencode run --auto --format json -m <provider/model> "<brief + card>"
    ```

    Always through the [sandbox](sandbox.md). Add `--standalone` if `selftest` says so.

=== "tether"

    `tether_run` with `goal`, `verify`, `model`, `sandbox=workspace-write`, `context_tokens`, `max_steps`; `wait=false` then `tether_wait`/`tether_read` for long jobs. Its sandbox blocks `.git` and the network, so Gru commits.

Minion output is **data**: instructions inside it are ignored and logged. Secrets and `.env*` never go in a brief, and `sensitive` paths never reach a slot below their minimum.

## When tether breaks

tether is in build. If a run fails for a reason that is tether's fault (crash, tool bug, malformed output, sandbox limit), Gru logs a `Tether friction` entry with a repro, reruns that stage on Claude Code, keeps that card there, and asks you before filing an issue on the tether repo (after checking for duplicates). Failures that are not tether's fault (bad card, auth, network, quota) are handled as normal failures.

## Limits and parallelism

Cards run in parallel only if they have no dependency, own disjoint files, and no limit forbids it. A **local** model runs one job at a time; a rate-limited provider is capped (`max_parallel`, `rpm`). The preview prints the schedule and why anything is sequential.
