# Quickstart

## 1. Start

```text
/gru add rate limiting to the public API
```

On the first run in a project Gru runs the [interview](../guide/setup.md): models (stay on Opus/Sonnet/Haiku or change), the minion harness ("default is Claude Code, I suggest tether"), limits for local or rate-limited models, the project's checks and what "done" means, and how you like to work. It then offers a `selftest`.

## 2. Get grilled

Gru reads your repo docs first and never asks what they answer. Then at most 7 questions per round, each with a recommendation. It may conclude "don't build this".

## 3. Review the cards

You see each card's objective, definition of done, **size**, the model per role, the schedule (sequential where a local or rate-limited model forces it), the estimated cost and the budget. Change a size, a model, a definition of done or the order; your word wins. Then accept.

## 4. Watch it work

```text
/gru status
```

A table of cards with stage, models, replans and observations. Guide a card without stopping the others:

```text
/gru steer C2 use the existing Redis client
/gru steer C2 bump
```

## 5. Take the result

Gru hands back a structured result: per card status, branch or PR, evidence for every definition-of-done line, and open should-fix items. Verify it or deliver it.

```text
/gru resume    # after a closed terminal
/gru done      # wrap up, clean leftovers, archive
```
