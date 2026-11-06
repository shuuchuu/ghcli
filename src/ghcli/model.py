"""The issues the CLI handles."""

from dataclasses import dataclass
from typing import Any, Self


@dataclass
class Issue:
    """A GitHub issue, reduced to what the CLI shows."""

    title: str
    body: str
    url: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Build an issue from a dictionary of the GitHub API.

        Args:
            data: An issue, as the API returns it.

        Returns:
            The issue.
        """
        # An issue's body is null when it has none.
        return cls(title=data["title"], body=data["body"] or "", url=data["html_url"])
