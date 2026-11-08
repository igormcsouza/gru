# Static, offline, deterministic (this is what CI runs):
test:
	uv run --group test pytest -q
docs:
	uv run --group docs mkdocs build --strict
check: test docs

# LOCAL ONLY: real model calls through your logged-in `claude` (they refuse to run when CI is set).
quiz:            ## spec quiz on Haiku, ~$0.03
	uv run --group test python evals/quiz.py
scenarios:       ## end-to-end scenarios on Sonnet, ~$0.5-1
	uv run --group test python evals/scenarios.py --show
.PHONY: test docs check quiz scenarios
