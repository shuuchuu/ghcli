"""Calls to the GitHub API."""

import os
import sys

import niquests

from .model import Issue

API_URL = "https://api.github.com"


def _get_token() -> str:
    token = os.environ.get("GHCLI_TOKEN")
    if not token:
        print(
            "Unable to read the GitHub token from the GHCLI_TOKEN environment "
            "variable. Define it and run the program again.",
            file=sys.stderr,
        )
        sys.exit(1)
    return token


def _headers(token: str | None) -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    # Without a token, the API still answers reads of public repositories.
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def list_issues(owner: str, repo: str) -> list[Issue]:
    """List the open issues among the 100 latest of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.

    Returns:
        Its issues, without its pull requests.
    """
    # https://docs.github.com/en/rest/issues/issues#list-repository-issues
    response = niquests.get(
        f"{API_URL}/repos/{owner}/{repo}/issues",
        params={"per_page": "100"},
        headers=_headers(os.environ.get("GHCLI_TOKEN")),
        timeout=10,
    )
    # An error status (404 for an unknown repository, 401 for a bad token)
    # raises niquests.HTTPError.
    response.raise_for_status()
    # The API counts pull requests as issues.
    return [
        Issue.from_dict(issue)
        for issue in response.json()
        if "pull_request" not in issue
    ]


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
        headers=_headers(_get_token()),
        timeout=10,
    )
    response.raise_for_status()
    return Issue.from_dict(response.json())
