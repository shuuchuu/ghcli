"""Interact with the GitHub API."""

import os
import sys
import typing

import deal
import requests

from .model import Issue


@deal.raises(SystemExit)
def _get_token() -> str:
    try:
        return os.environ["GHCLI_TOKEN"]
    except KeyError:
        print(
            "Unable to retrieve the GitHub token from the environment variable "
            "GHCLI_TOKEN. Define this variable and restart the program.",
            file=sys.stderr,
        )
        sys.exit(1)


@deal.pre(lambda owner, repo: bool(owner) and bool(repo))
@deal.pre(lambda owner, repo: "/" not in owner)
@deal.pre(lambda owner, repo: "/" not in repo)
@deal.post(lambda issues: all(issue.url.startswith("http") for issue in issues))
@deal.raises(SystemExit, requests.HTTPError)
def list_issues(owner: str, repo: str) -> typing.List[Issue]:
    """Retrieve issues of a GitHub repository."""
    # Call to the GitHub API as detailed here:
    # https://docs.github.com/en/rest/issues/issues#list-repository-issues
    # This call allows us to obtain a response object from the requests library:
    # https://requests.readthedocs.io/en/latest/user/quickstart/#response-content
    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        headers=dict(
            Accept="application/vnd.github.v3+json",
            Authorization=f"token {_get_token()}",
        ),
    )

    # First, let's check that there was no issue. If the request returned an error
    # code, an exception will be raised here.
    response.raise_for_status()

    # We can now retrieve the response content using the json method.
    # This will return a Python data structure that corresponds to the JSON response.
    # Here, it will be a list of dictionaries.
    issues = response.json()

    # Finally, we create Issue objects using each dictionary.
    return [Issue.from_dict(issue) for issue in issues]


@deal.pre(lambda owner, repo, title, body: bool(owner) and bool(repo))
@deal.pre(lambda owner, repo, title, body: "/" not in owner)
@deal.pre(lambda owner, repo, title, body: "/" not in repo)
@deal.post(lambda issue: issue.url.startswith("http"))
@deal.raises(requests.HTTPError, SystemExit)
def create_issue(owner: str, repo: str, title: str, body: str) -> Issue:
    """Create an issue in a GitHub repository."""
    # Call to the GitHub API as detailed here:
    # https://docs.github.com/en/rest/issues/issues#create-an-issue
    # This call allows us to obtain a response object from the requests library:
    # https://requests.readthedocs.io/en/latest/user/quickstart/#response-content
    response = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        json=dict(title=title, body=body),
        headers=dict(
            Accept="application/vnd.github.v3+json",
            Authorization=f"token {_get_token()}",
        ),
    )

    # First, let's check that there was no issue. If the request returned an error
    # code, an exception will be raised here.
    response.raise_for_status()

    # We can now retrieve the response content using the json method.
    # This will return a Python data structure that corresponds to the JSON response.
    # Here, it will be a dictionary.
    issue = response.json()

    # Finally, we create an Issue object using the dictionary.
    return Issue.from_dict(issue)
