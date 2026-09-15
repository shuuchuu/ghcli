DOIT_CONFIG = {
    "backend": "json",
    "default_tasks": ["check"],
    "dep_file": ".doit.json",
    "verbosity": 2,
}


def task_check():
    return {
        "actions": [
            "uv run ruff check src/ghcli tests",
            "uv run ruff format --check src/ghcli tests",
            "uv run ty check src/ghcli tests",
        ],
    }


def task_test():
    return {
        "actions": [
            "uv run pytest",
        ],
    }
