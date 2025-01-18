check:
	ruff check src/ghcli tests
	mypy src/ghcli tests

.PHONY: check
