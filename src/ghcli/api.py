"""Calls to the GitHub API."""

import os
import sys

import niquests

from .model import Issue

API_URL = "https://api.github.com"


def _get_token() -> str:
    try:
        return os.environ["GHCLI_TOKEN"]
    except KeyError:
        print(
            "Unable to read the GitHub token from the GHCLI_TOKEN environment "
            "variable. Define it and run the program again.",
            file=sys.stderr,
        )
        sys.exit(1)


def _headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {_get_token()}",
    }


def list_issues(owner: str, repo: str) -> list[Issue]:
    """List the open issues of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.

    Returns:
        Its issues.
    """
    # https://docs.github.com/en/rest/issues/issues#list-repository-issues
    response = niquests.get(
        f"{API_URL}/repos/{owner}/{repo}/issues", headers=_headers(), timeout=10
    )
    # An error status (404 for an unknown repository, 401 for a bad token)
    # raises niquests.HTTPError.
    response.raise_for_status()
    return [Issue.from_dict(issue) for issue in response.json()]


def create_issue(owner: str, repo: str, title: str, body: str) -> Issue:
    """Create an issue in a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.
        title: The issue's title.
        body: The issue's body.

    Returns:
        The created issue.
    """
    # https://docs.github.com/en/rest/issues/issues#create-an-issue
    response = niquests.post(
        f"{API_URL}/repos/{owner}/{repo}/issues",
        json={"title": title, "body": body},
        headers=_headers(),
        timeout=10,
    )
    response.raise_for_status()
    return Issue.from_dict(response.json())
