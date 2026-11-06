"""Saving issues to files."""

import json
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path

from .model import Issue


def save_issues_to_file(issues: Iterable[Issue], path: Path) -> None:
    """Save issues to a JSON file, as a list of objects.

    Args:
        issues: The issues to save.
        path: The JSON file to write.
    """
    data = [asdict(issue) for issue in issues]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
