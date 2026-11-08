# Budget and calibration

## Budget

Gru tracks per card and in total: tokens (what the harness reports; otherwise bytes/4, marked `~`), wall-clock and replans. **Paid tokens** are tokens on paid models, Gru itself included; free and local models are tracked but not counted against the cap.

- **Defaults:** a one-line warning at 300k paid tokens (spent by slot, what is left, what is running), stop-and-ask at 400k (raise it, shrink reviews to the risky hunks, shift work to cheaper slots, or stop). Set other numbers in `gru.yml` (team default) or in the preview; with a cap Gru warns at 75% and stops at 100%. A wall-clock cap behaves the same.
- **Cost in the preview:** an estimate per card from its size and roles. Tokens always; dollars when `prices` is set in `local.yml`. Estimates start from rough defaults and sharpen with calibration.
- **On a warning:** no more bumps without asking, no optional should-fix work.
- During long unattended runs Gru sends a push notification (if available and allowed) when it is blocked on you or a threshold is hit.

Quality over savings: if a card has no real checks, Gru says so and asks rather than shipping green-but-wrong.

## Calibration

When a card closes, Gru records its size, the swe slot and model, replans, findings and tokens in `local.yml`, and keeps stats per size and slot (cards, first-pass rate, average replans, bumps). It then **suggests**, never applies on its own:

- "S cards on weak keep needing replans in this repo: move S to mid?"
- "M cards on mid pass first try: try weak for small M?"

Accepted suggestions update `size_slots`. Because `local.yml` lives with the project's logs, calibration carries across Gru sessions on your machine.
