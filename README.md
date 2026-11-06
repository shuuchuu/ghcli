# Command-line interface for GitHub Issues

*[Version française](https://github.com/shuuchuu/ghcli)*

The project of the *Command-line interface for GitHub Issues* lab. Its instructions are
below, to run the lab in a GitHub Codespace or a local clone; they are the same as the
lab's notebook, in
[English](https://colab.research.google.com/github/shuuchuu/labs/blob/main/cli-github-issues-cli-hands-on-en.ipynb)
or in
[French](https://colab.research.google.com/github/shuuchuu/labs/blob/main/cli-github-issues-cli-hands-on-fr.ipynb),
which runs it in Colab.

The aim of this lab is to put into practice the engineering principles seen during the
course: we are going to create `ghcli`, a command-line interface that lists and creates
the issues of a GitHub repository, first with `argparse`, then with `Typer` and `Rich`.
Publishing it on Test PyPI is an optional extension. The "Tests" step assumes `pytest`
and `monkeypatch`: if your course hasn't covered them, skip it; at the "`Typer` and
`Rich`" step, then run only `ruff` and `pyrefly`. The repository is a `uv` project
whose package, `src/ghcli/`, is still empty.

## Setting up the working environment

This English version of the lab is the repository's `main-en` branch. Open it in a
Codespace: on GitHub, on the `main-en` branch, **Code** > **Codespaces** > **Create
codespace on main-en**, or [this
link](https://codespaces.new/shuuchuu/ghcli/tree/main-en). The Codespace installs the
dependencies when it is created, in the project's `.venv`.

In a local clone of that branch, install
[uv](https://docs.astral.sh/uv/getting-started/installation/), then run `uv sync` at the
root of the repository:

```console
git clone -b main-en https://github.com/shuuchuu/ghcli.git
cd ghcli
uv sync
```

The commands below run in a terminal at the root of the repository (**Terminal** > **New
Terminal** in the Codespace), through `uv run`, which runs them in the project's
environment. The files are written in the editor. The solutions are also on the
repository's [`solution-en` branch](https://github.com/shuuchuu/ghcli/tree/solution-en).

## A test repository and a GitHub token

`ghcli` creates issues: it needs a repository to create them in, and a token for the
GitHub API that allows only that.

1. If you don't have a GitHub account yet, [create one](https://github.com/signup),
   then sign in.
2. [Create a public repository](https://github.com/new) named `ghcli-sandbox`, with a
   README (**Add README**).
3. [Create a token](https://github.com/settings/personal-access-tokens/new) (a
   *fine-grained personal access token*): **Token name** `GHCLI`, **Expiration** 7
   days, **Repository access** > **Only select repositories** > `ghcli-sandbox`, then,
   under **Permissions**, **Add permissions** > **Issues**, as **Read and write**. Copy
   its value, which starts with `github_pat_`: GitHub shows it only once.
4. At the root of the repository, create a `creds.env` file (which `.gitignore` keeps
   out of commits) holding:

   ```shell
   export GHCLI_TOKEN=github_pat_...
   ```

   and run `source creds.env` in every new terminal, before `ghcli`.

Without a GitHub account, don't create `creds.env`: `ghcli list` works on a public
repository, without a token (the API then accepts 60 requests per hour and per address,
which a room behind one address shares), `ghcli create` doesn't, and the tests of the
"Tests" step always do.

## The `ghcli` command

Create the `src/ghcli/cli.py` module, with a `main` function that reads two arguments
from the command line, the owner of a GitHub repository and its name, and prints them.
Declare in `pyproject.toml` the `ghcli` command, which runs that function, then run `uv
sync`, which installs it in the project's environment, and try it: `uv run ghcli
shuuchuu ghcli` prints `shuuchuu ghcli`. What do `uv run ghcli`, with no
argument, and `uv run ghcli --help` give?

**Useful documentation**

- https://docs.astral.sh/uv/concepts/projects/config/#entry-points
- https://docs.python.org/3/library/argparse.html#the-add-argument-method

<details>
<summary>Additional hints</summary>

A command is declared in the `[project.scripts]` table of `pyproject.toml`: its name,
then the module and the function it calls, separated by `:`. A positional argument is a
name without dashes: `parser.add_argument("owner", help="...")`. `parse_args()` returns
an object with each argument as an attribute (`args.owner`). With no argument,
`argparse` prints the usage and an error; with `--help`, the help it generates from the
`help=` strings.

```python
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="List GitHub issues.")
    parser.add_argument("owner", help="owner of the GitHub repository")
    ...
    args = parser.parse_args()
    print(...)
```

```toml
[project.scripts]
ghcli = "ghcli....:..."
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/cli.py`:

```python
"""Command-line interface to GitHub issues."""

import argparse


def main() -> None:
    """Read a GitHub repository from the arguments."""
    parser = argparse.ArgumentParser(description="List GitHub issues.")
    parser.add_argument("owner", help="owner of the GitHub repository")
    parser.add_argument("repo", help="name of the GitHub repository")
    args = parser.parse_args()
    print(args.owner, args.repo)
```

`pyproject.toml`, after the `[project]` table:

```toml
[project.scripts]
ghcli = "ghcli.cli:main"
```

```console
uv sync
```

```console
uv run ghcli shuuchuu ghcli
uv run ghcli --help
```

</details>

## The token, from an environment variable

Create the `src/ghcli/api.py` module, which will hold the software's logic: the calls to
the GitHub API. Write in it a `_get_token() -> str` function that returns the value of
the `GHCLI_TOKEN` environment variable. When it isn't defined, or is empty, the function
prints this message to the standard error, then stops the program with the exit code
`1`:

```text
Unable to read the GitHub token from the GHCLI_TOKEN environment variable. Define it and
run the program again.
```

Try it with a fake value, so that the real token never appears on the screen:
`GHCLI_TOKEN=test uv run python -c "from ghcli.api import _get_token;
print(_get_token())"`, then without the variable: `env -u GHCLI_TOKEN uv run python -c
"..."`.

**Useful documentation**

- https://docs.python.org/3/library/os.html#os.environ
- https://docs.python.org/3/library/sys.html#sys.exit

<details>
<summary>Additional hints</summary>

`os.environ.get("GHCLI_TOKEN")` returns the variable's value, or `None` when it isn't
defined: `if not token` covers both a missing and an empty value. `print(...,
file=sys.stderr)` writes to the standard error.

```python
import os
import sys


def _get_token() -> str:
    token = os.environ.get(...)
    if not token:
        print(..., file=sys.stderr)
        sys.exit(...)
    return token
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/api.py`:

```python
"""Calls to the GitHub API."""

import os
import sys


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
```

```console
GHCLI_TOKEN=test uv run python -c "from ghcli.api import _get_token; print(_get_token())"
env -u GHCLI_TOKEN uv run python -c "from ghcli.api import _get_token; print(_get_token())" || echo "(non-zero exit code)"
```

</details>

## Listing the issues

Add the [`niquests`](https://niquests.readthedocs.io/) library to the project, which has
`requests`'s interface, in a more modern form (`uv add niquests`). Write in `api.py` a
`list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]` function that returns
the repository's open issues, a list of `(title, body, url)` tuples, and have `main`
print one line per issue, `url - title - body`. Why put this function in `api.py`, and
keep only the reading of the arguments in `cli.py`?

The function asks the GitHub API for these issues:

```python
response = niquests.get(
    f"https://api.github.com/repos/{owner}/{repo}/issues",
    headers=...,
    timeout=10,
)
```

then reads the response, the list of issues as JSON: `response.json()`. Three points
need your attention:

- The headers: `Accept` is `application/vnd.github+json`; `Authorization` is `Bearer
  <token>`, only if `GHCLI_TOKEN` has a value. Without that header, the API answers
  reads of a public repository, whereas it refuses a `Bearer` with no token.
- The pull requests: to the API, they are issues. `list_issues` must return the real
  issues only.
- Pagination: the API answers in pages of 30 items. Ask for 100, the maximum, and don't
  try to go further.

Try it: `uv run ghcli shuuchuu ghcli` prints three issues, one of them without a
body, and not this repository's pull request:

```text
https://github.com/shuuchuu/ghcli/issues/88 - Ticket 3 - Corps / Body
https://github.com/shuuchuu/ghcli/issues/87 - Ticket 2 -
https://github.com/shuuchuu/ghcli/issues/86 - Ticket 1 - Corps / Body
```

Your test repository has no issue yet: `uv run ghcli <your user> ghcli-sandbox`. What
happens for a repository that doesn't exist?

**Useful documentation**

- https://docs.github.com/en/rest/issues/issues#list-repository-issues
- https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api
- https://niquests.readthedocs.io/en/latest/user/quickstart.html#passing-parameters-in-urls
- https://niquests.readthedocs.io/en/latest/user/quickstart.html#response-status-codes

<details>
<summary>Additional hints</summary>

In the package, `from .api import list_issues` imports the function from the neighboring
module. Each issue is a dictionary whose `title`, `body` and `html_url` keys (the URL of
its page, whereas `url` is the API's) give what we want; `body` is `None` for an issue
without a body. A pull request is an item that has a `pull_request` key.
`params={"per_page": "100"}` adds `?per_page=100` to the URL; to go further, you would
follow the response's `Link` header. `response.raise_for_status()` raises a
`niquests.HTTPError` when the API answers with an error, `404` for an unknown
repository, `401` for an invalid token. A `_headers(token: str | None)` function builds
the headers with or without a token, and will serve `create_issue` too.

`cli.py` keeps only the reading of the arguments: the logic can then be tested without a
parser (the "Tests" step), and doesn't change when the parser does (the "`Typer` and
`Rich`" step).

```python
def _headers(token: str | None) -> dict[str, str]:
    headers = {"Accept": ...}
    if token:
        headers["Authorization"] = ...
    return headers


def list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]:
    response = niquests.get(
        ..., params=..., headers=_headers(os.environ.get(...)), timeout=10
    )
    response.raise_for_status()
    return [(issue["title"], ..., ...) for issue in response.json() if ...]
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/api.py`:

```python
"""Calls to the GitHub API."""

import os
import sys

import niquests

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


def list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]:
    """List the open issues among the 100 latest of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.

    Returns:
        The title, body and URL of each issue, without the pull requests.
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
    # The API counts pull requests as issues, and an issue's body is null when it
    # has none.
    return [
        (issue["title"], issue["body"] or "", issue["html_url"])
        for issue in response.json()
        if "pull_request" not in issue
    ]
```

`src/ghcli/cli.py`:

```python
"""Command-line interface to GitHub issues."""

import argparse

from .api import list_issues


def main() -> None:
    """List the issues of the GitHub repository the arguments name."""
    parser = argparse.ArgumentParser(description="List GitHub issues.")
    parser.add_argument("owner", help="owner of the GitHub repository")
    parser.add_argument("repo", help="name of the GitHub repository")
    args = parser.parse_args()
    for title, body, url in list_issues(args.owner, args.repo):
        print(f"{url} - {title} - {body}")
```

```console
uv add niquests
uv run ghcli shuuchuu ghcli
uv run ghcli shuuchuu no-such-repository || echo "(non-zero exit code)"
```

</details>

## Creating an issue: two commands

Add to `api.py` a `create_issue(owner: str, repo: str, title: str, body: str) ->
tuple[str, str, str]` function, which creates an issue and returns its title, body and
URL. It sends the issue's title and body to the API, as JSON, and needs the token:

```python
response = niquests.post(
    f"https://api.github.com/repos/{owner}/{repo}/issues",
    json={"title": title, "body": body},
    headers=...,
    timeout=10,
)
```

`ghcli` now has two commands, `ghcli list <owner> <repository>` and `ghcli create
<owner> <repository> <title> <body>`: make them two subcommands of the parser, each with
its arguments. Create an issue in your test repository, then list it.

An unknown repository ends in a Python traceback for now. A command-line interface
answers with a message and an exit code, as `_get_token` just did: make `main` catch
`niquests.HTTPError`, write one line to the standard error and stop with the exit code
`1`. Try it with `uv run ghcli list shuuchuu no-such-repository`.

**Useful documentation**

- https://docs.github.com/en/rest/issues/issues#create-an-issue
- https://docs.python.org/3/library/argparse.html#subcommands

<details>
<summary>Additional hints</summary>

`parser.add_subparsers(dest="command", required=True)` returns an object whose
`add_parser("list")` creates the subcommand's parser; `args.command` says which one ran.
Both subcommands share `owner` and `repo`: a loop adds them to both. The API answers
`201 Created` with the created issue, in the same format as an issue of the list.
`headers=_headers(_get_token())` requires the token: without it, `create` stops on
`_get_token`'s message.

```python
subparsers = parser.add_subparsers(dest="command", required=True)
list_parser = subparsers.add_parser("list", help="list a repository's issues")
create_parser = subparsers.add_parser("create", help="create an issue")
for subparser in (list_parser, create_parser):
    subparser.add_argument("owner", help="owner of the GitHub repository")
    ...
create_parser.add_argument("title", help="title of the issue")
...
args = parser.parse_args()
try:
    if args.command == "list":
        ...
    elif args.command == "create":
        ...
except niquests.HTTPError as error:
    print(..., file=sys.stderr)
    sys.exit(...)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/api.py`:

```python
"""Calls to the GitHub API."""

import os
import sys

import niquests

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


def list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]:
    """List the open issues among the 100 latest of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.

    Returns:
        The title, body and URL of each issue, without the pull requests.
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
    # The API counts pull requests as issues, and an issue's body is null when it
    # has none.
    return [
        (issue["title"], issue["body"] or "", issue["html_url"])
        for issue in response.json()
        if "pull_request" not in issue
    ]


def create_issue(owner: str, repo: str, title: str, body: str) -> tuple[str, str, str]:
    """Create an issue in a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.
        title: The issue's title.
        body: The issue's body.

    Returns:
        The title, body and URL of the created issue.
    """
    # https://docs.github.com/en/rest/issues/issues#create-an-issue
    response = niquests.post(
        f"{API_URL}/repos/{owner}/{repo}/issues",
        json={"title": title, "body": body},
        headers=_headers(_get_token()),
        timeout=10,
    )
    response.raise_for_status()
    issue = response.json()
    return issue["title"], issue["body"] or "", issue["html_url"]
```

`src/ghcli/cli.py`:

```python
"""Command-line interface to GitHub issues."""

import argparse
import sys

import niquests

from .api import create_issue, list_issues


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List and create GitHub issues.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="list a repository's issues")
    create_parser = subparsers.add_parser("create", help="create an issue")
    for subparser in (list_parser, create_parser):
        subparser.add_argument("owner", help="owner of the GitHub repository")
        subparser.add_argument("repo", help="name of the GitHub repository")
    create_parser.add_argument("title", help="title of the issue")
    create_parser.add_argument("body", help="body of the issue")
    return parser


def main() -> None:
    """Run the command the arguments name."""
    args = _create_parser().parse_args()
    try:
        if args.command == "list":
            for title, body, url in list_issues(args.owner, args.repo):
                print(f"{url} - {title} - {body}")
        elif args.command == "create":
            title, body, url = create_issue(
                args.owner, args.repo, args.title, args.body
            )
            print(f"{url} - {title} - {body}")
    except niquests.HTTPError as error:
        print(f"GitHub API error: {error}", file=sys.stderr)
        sys.exit(1)
```

```console
uv run ghcli list shuuchuu no-such-repository || echo "(non-zero exit code)"
uv run ghcli create <your user> ghcli-sandbox "First issue" "Created by ghcli"
uv run ghcli list <your user> ghcli-sandbox
```

</details>

## A class for the issues

Tuples represent the issues for now: it's easy to mix up their order, and so to
introduce bugs. In a `src/ghcli/model.py` module, create an `Issue` class, with the
`dataclasses` module, whose attributes are an issue's title, body and URL, and a
`from_dict` class method that builds an `Issue` from an issue of the API. `list_issues`
then returns a `list[Issue]`, `create_issue` an `Issue`: adapt them, and `cli.py` too.

**Useful documentation**

- https://docs.python.org/3/library/dataclasses.html
- https://docs.python.org/3/library/functions.html#classmethod

<details>
<summary>Additional hints</summary>

`@dataclass` generates the constructor, the representation and the comparison from the
annotated attributes. A class method receives the class (`cls`) instead of an instance:
it's another constructor, `Issue.from_dict(issue)`.

```python
from dataclasses import dataclass
from typing import Any, Self


@dataclass
class Issue:
    title: str
    ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(title=data["title"], body=..., url=...)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/model.py`:

```python
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
```

`src/ghcli/api.py`:

```python
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
```

`src/ghcli/cli.py`:

```python
"""Command-line interface to GitHub issues."""

import argparse
import sys

import niquests

from .api import create_issue, list_issues
from .model import Issue


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List and create GitHub issues.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="list a repository's issues")
    create_parser = subparsers.add_parser("create", help="create an issue")
    for subparser in (list_parser, create_parser):
        subparser.add_argument("owner", help="owner of the GitHub repository")
        subparser.add_argument("repo", help="name of the GitHub repository")
    create_parser.add_argument("title", help="title of the issue")
    create_parser.add_argument("body", help="body of the issue")
    return parser


def _show(issue: Issue) -> None:
    print(f"{issue.url} - {issue.title} - {issue.body}")


def main() -> None:
    """Run the command the arguments name."""
    args = _create_parser().parse_args()
    try:
        if args.command == "list":
            for issue in list_issues(args.owner, args.repo):
                _show(issue)
        elif args.command == "create":
            _show(create_issue(args.owner, args.repo, args.title, args.body))
    except niquests.HTTPError as error:
        print(f"GitHub API error: {error}", file=sys.stderr)
        sys.exit(1)
```

```console
uv run ghcli list shuuchuu ghcli
```

</details>

## Tests

Write in `tests/test_api.py` tests of `_get_token`, `list_issues`, `create_issue` and
`main`, and run them with `uv run pytest`. They must depend neither on the network nor
on your token: replace `niquests.get` and `niquests.post` with functions that return a
fake response, and the environment variable with a test value. Also check the edge and
error cases: a missing or empty variable, a list without a token, a pull request to
leave out, an unknown repository, for which `main` writes to the standard error and
exits with the code `1`.

Finish with the tools the repository configures strictly in `pyproject.toml`: `uv run
ruff check`, `uv run ruff format --check` and `uv run pyrefly check` must pass.

**Useful documentation**

- https://docs.pytest.org/en/stable/how-to/monkeypatch.html
- https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions
- https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html#accessing-captured-output-from-a-test-function

<details>
<summary>Additional hints</summary>

`pytest`'s `monkeypatch` fixture replaces an attribute for the duration of a test
(`monkeypatch.setattr(niquests, "get", fake_get)`) and sets or removes an environment
variable (`setenv`, `delenv`). A fake response only needs the methods the code calls:
`raise_for_status` and `json`. An `autouse=True` fixture applies to every test of the
module. `main` reads `sys.argv`, which `monkeypatch` replaces too; the `capsys` fixture
gives what the code wrote to the standard error.

```python
class FakeResponse:
    def __init__(self, data, status_code=200):
        self.data = data
        ...

    def raise_for_status(self):
        if self.status_code >= 400:
            raise niquests.HTTPError(self.status_code)

    def json(self):
        return self.data


def test_list_issues(monkeypatch):
    monkeypatch.setenv("GHCLI_TOKEN", "a-token")
    monkeypatch.setattr(niquests, "get", lambda url, **kwargs: FakeResponse([...]))
    assert list_issues("octocat", "sandbox") == [...]


def test_main_reports_an_api_error(monkeypatch, capsys):
    monkeypatch.setattr(niquests, "get", ...)
    monkeypatch.setattr(sys, "argv", ["ghcli", "list", "octocat", "unknown"])
    with pytest.raises(SystemExit) as exit_info:
        main()
    assert exit_info.value.code == ...
    assert "404" in capsys.readouterr().err
```

</details>

<details>
<summary>Solution</summary>

`tests/test_api.py`:

```python
import sys
from typing import Any

import niquests
import pytest

from ghcli.api import _get_token, create_issue, list_issues
from ghcli.cli import main
from ghcli.model import Issue

ISSUE = {
    "title": "A title",
    "body": "A body",
    "html_url": "https://github.com/octocat/sandbox/issues/1",
}


class FakeResponse:
    """What `niquests.get` and `niquests.post` return, without the network."""

    def __init__(self, data: Any, status_code: int = 200) -> None:
        self.data = data
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise niquests.HTTPError(self.status_code)

    def json(self) -> Any:
        return self.data


@pytest.fixture(autouse=True)
def token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GHCLI_TOKEN", "a-token")


def test_get_token_reads_the_environment() -> None:
    assert _get_token() == "a-token"


def test_get_token_exits_without_the_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GHCLI_TOKEN")
    with pytest.raises(SystemExit):
        _get_token()


def test_get_token_exits_on_an_empty_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GHCLI_TOKEN", "")
    with pytest.raises(SystemExit):
        _get_token()


def test_list_issues(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def get(url: str, **kwargs: Any) -> FakeResponse:
        calls.append((url, kwargs["headers"]["Authorization"]))
        return FakeResponse([ISSUE, {**ISSUE, "pull_request": {}}])

    monkeypatch.setattr(niquests, "get", get)
    assert list_issues("octocat", "sandbox") == [
        Issue("A title", "A body", "https://github.com/octocat/sandbox/issues/1")
    ]
    assert calls == [
        ("https://api.github.com/repos/octocat/sandbox/issues", "Bearer a-token")
    ]


def test_list_issues_without_a_token(monkeypatch: pytest.MonkeyPatch) -> None:
    def get(url: str, **kwargs: Any) -> FakeResponse:
        assert "Authorization" not in kwargs["headers"]
        return FakeResponse([])

    monkeypatch.delenv("GHCLI_TOKEN")
    monkeypatch.setattr(niquests, "get", get)
    assert list_issues("octocat", "sandbox") == []


def test_list_issues_of_an_unknown_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(niquests, "get", lambda url, **kwargs: FakeResponse({}, 404))
    with pytest.raises(niquests.HTTPError):
        list_issues("octocat", "unknown")


def test_create_issue(monkeypatch: pytest.MonkeyPatch) -> None:
    def post(url: str, **kwargs: Any) -> FakeResponse:
        assert kwargs["json"] == {"title": "A title", "body": "A body"}
        return FakeResponse(ISSUE, 201)

    monkeypatch.setattr(niquests, "post", post)
    issue = create_issue("octocat", "sandbox", "A title", "A body")
    assert issue.url == "https://github.com/octocat/sandbox/issues/1"


def test_create_issue_needs_a_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GHCLI_TOKEN")
    with pytest.raises(SystemExit):
        create_issue("octocat", "sandbox", "A title", "A body")


def test_main_reports_an_api_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(niquests, "get", lambda url, **kwargs: FakeResponse({}, 404))
    monkeypatch.setattr(sys, "argv", ["ghcli", "list", "octocat", "unknown"])
    with pytest.raises(SystemExit) as exit_info:
        main()
    assert exit_info.value.code == 1
    assert "404" in capsys.readouterr().err
```

```console
uv run pytest
uv run ruff check
uv run ruff format --check
uv run pyrefly check
```

</details>

## `Typer` and `Rich`

`argparse` did its job, at the cost of many lines that only declare arguments. Add
`typer` and `rich` to the project (`uv add typer rich`), and rewrite `cli.py` with
`typer.Typer()` and `@app.command()`, seen in the course:

- The commands stay `ghcli list <owner> <repository>` and `ghcli create <owner>
  <repository> <title> <body>`, and each argument keeps its help.
- `list` shows the issues in a `rich.table.Table`, with their whole URL.
- `main` stays the entry point of `pyproject.toml`, and still catches the API's errors.

Look at `uv run ghcli --help`, then `uv run ghcli list shuuchuu ghcli`. What
becomes of `_create_parser`? What is left to change in `api.py`? And in the tests, which
must pass without being touched?

**Useful documentation**

- https://typer.tiangolo.com/tutorial/commands/name/
- https://rich.readthedocs.io/en/stable/console.html

<details>
<summary>Additional hints</summary>

`_create_parser` disappears: the functions' annotations declare the arguments. Nothing
changes in `api.py`, and the tests pass as they are: that is what the separation between
`cli.py` and `api.py` brings. `@app.command("list")` names the command, which avoids
calling a function `list` like the built-in one. An `Annotated[str,
typer.Argument(help=...)]` alias serves both commands, and a command's docstring becomes
its help. `add_column("URL", no_wrap=True)` keeps a column on one line: a cut URL no
longer leads anywhere. `Console(markup=False).print(...)` prints the table, without
taking the square brackets of an issue's title for a style. `app()` runs the command:
`main` wraps it in its `try`.

```python
app = typer.Typer(help=...)
console = Console(markup=False)

Owner = Annotated[str, typer.Argument(help=...)]
...


@app.command("list")
def list_command(owner: Owner, repo: ...) -> None:
    """List the open issues of a repository."""
    table = Table("Title", "Body")
    table.add_column("URL", no_wrap=True)
    for issue in list_issues(owner, repo):
        table.add_row(...)
    console.print(table)


def main() -> None:
    try:
        app()
    except niquests.HTTPError as error:
        ...
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/cli.py`:

```python
"""Command-line interface to GitHub issues."""

import sys
from typing import Annotated

import niquests
import typer
from rich.console import Console
from rich.table import Table

from .api import create_issue, list_issues

app = typer.Typer(help="List and create the issues of a GitHub repository.")
# Without markup: an issue's title can hold square brackets.
console = Console(markup=False)

Owner = Annotated[str, typer.Argument(help="Owner of the GitHub repository.")]
Repo = Annotated[str, typer.Argument(help="Name of the GitHub repository.")]


@app.command("list")
def list_command(owner: Owner, repo: Repo) -> None:
    """List the open issues of a repository."""
    table = Table("Title", "Body")
    # Without wrapping: a cut URL no longer leads anywhere.
    table.add_column("URL", no_wrap=True)
    for issue in list_issues(owner, repo):
        table.add_row(issue.title, issue.body, issue.url)
    console.print(table)


@app.command("create")
def create_command(
    owner: Owner,
    repo: Repo,
    title: Annotated[str, typer.Argument(help="Title of the issue.")],
    body: Annotated[str, typer.Argument(help="Body of the issue.")],
) -> None:
    """Create an issue."""
    issue = create_issue(owner, repo, title, body)
    console.print(f"{issue.url} - {issue.title} - {issue.body}")


def main() -> None:
    """Run the command the arguments name."""
    try:
        app()
    except niquests.HTTPError as error:
        print(f"GitHub API error: {error}", file=sys.stderr)
        sys.exit(1)
```

```console
uv add typer rich
uv run ghcli --help
uv run ghcli list shuuchuu ghcli
uv run ghcli list shuuchuu no-such-repository || echo "(non-zero exit code)"
uv run pytest
uv run ruff check
uv run ruff format --check
uv run pyrefly check
```

</details>

## Optional extension: publishing on Test PyPI

This extension repeats on `ghcli` the publishing of the packaging lab, with that lab's
Test PyPI account and token: without them, stop here.

1. The name `ghcli` can be published only once: in `pyproject.toml`, rename the project
   `ghcli-<your GitHub user>`, in lowercase, without changing the name of the package
   one imports, `ghcli`, and put yourself in `authors`, which ships with the package.
2. Declare in `pyproject.toml` the `testpypi` index, its URL and the one packages are
   published to.
3. Build the package with `uv build`, then publish it with `uv publish --index testpypi
   --token <your token>`.
4. Find its page on Test PyPI, then install and run it, without the repository: `uvx
   --index https://pypi.org/simple/ --default-index https://test.pypi.org/simple/ --from
   ghcli-<your user> ghcli --help`.

**Useful documentation**

- https://docs.astral.sh/uv/concepts/build-backend/#modules
- https://docs.astral.sh/uv/guides/integration/alternative-indexes/
- https://docs.astral.sh/uv/guides/package/#publishing-your-package

<details>
<summary>Additional hints</summary>

The module `uv build` builds is named after the project by default: `module-name`, in
`[tool.uv.build-backend]`, sets it. An index is declared in a `[[tool.uv.index]]` table:
`name`, `url`, `publish-url`, and `explicit = true`, so that `uv` only looks there for
the packages assigned to it. Test PyPI's URL is `https://test.pypi.org/simple/`, the one
packages are published to `https://test.pypi.org/legacy/`. For `uvx`, PyPI comes before
Test PyPI: `uv` takes each package from the first index that has it, so `niquests` and
its dependencies from PyPI, at their current versions, and your package, which only
exists on Test PyPI, from the latter.

```toml
[project]
authors = [...]
name = "ghcli-..."

[tool.uv.build-backend]
module-name = ...

[[tool.uv.index]]
name = "testpypi"
url = ...
publish-url = ...
explicit = true
```

</details>

<details>
<summary>Solution</summary>

`pyproject.toml`, here for the `octocat` user:

```toml
[project]
authors = [
  {name = "octocat"},
]
name = "ghcli-octocat"
...

[tool.uv.build-backend]
module-name = "ghcli"

[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true
```

```console
rm -rf dist
uv build
uv publish --index testpypi --token <your token>
uvx --index https://pypi.org/simple/ --default-index https://test.pypi.org/simple/ --from ghcli-<your user> ghcli --help
```

The package's page is `https://test.pypi.org/project/ghcli-<your user>/`.

</details>
