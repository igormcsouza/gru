# Budget

Gru tracks, per task and in total: tokens (what the harness reports; otherwise bytes/4, marked `~`), wall-clock, attempts and escalations. **Paid tokens** are Tier 1+ minions, `reviewer`, `architect` and Gru itself.

- **Default watch line:** a one-line warning at 300k paid tokens (spent, per tier, what is left, what is running), and stop-and-ask at 400k (raise the cap, shift work to cheaper tiers, or stop).
- **Your caps:** set other numbers in the plan preview. With a cap, Gru warns at 75% and stops at 100%. A wall-clock cap behaves the same way.
- **On a warning:** stop escalating, push remaining tasks to the cheapest tier that has not failed on them, shrink reviews to the risky hunks.
- During long unattended runs Gru sends a push notification (if available) when it is blocked on you or a threshold is hit.

Quality over savings: if the verify gate looks too weak for a task (no tests cover it), Gru says so and raises the tier or asks you.
