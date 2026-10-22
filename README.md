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
the issues of a GitHub repository, turn it into a package and publish it on Test PyPI.
The repository is a `uv` project whose package, `src/ghcli/`, is still empty.

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

## An entry point

Create the `src/ghcli/cli.py` module, with a `main` function, taking no argument, that
prints `Hello World`. Declare in `pyproject.toml` the `ghcli` command, which runs that
function, then run `uv sync`, which installs it in the project's environment, and try
it: `uv run ghcli`.

**Useful documentation**

- https://docs.astral.sh/uv/concepts/projects/config/#entry-points

<details>
<summary>Additional hints</summary>

A command is declared in the `[project.scripts]` table: its name, then the module and
the function it calls, separated by `:`.

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


def main() -> None:
    """Greet the user."""
    print("Hello World")
```

`pyproject.toml`, after the `[project]` table:

```toml
[project.scripts]
ghcli = "ghcli.cli:main"
```

```console
uv sync
uv run ghcli
```

</details>

## An argument parser

Change `main` so that it reads two arguments from the command line, the owner of a
GitHub repository and its name, and prints them: `uv run ghcli octocat Hello-World`
prints `octocat Hello-World`. What do `uv run ghcli`, with no argument, and `uv run
ghcli --help` give?

**Useful documentation**

- https://docs.python.org/3/library/argparse.html#the-add-argument-method

<details>
<summary>Additional hints</summary>

A positional argument is a name without dashes: `parser.add_argument("owner",
help="...")`. `parse_args()` returns an object with each argument as an attribute
(`args.owner`). With no argument, `argparse` prints the usage and an error; with
`--help`, the help it generates from the `help=` strings.

```python
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="List GitHub issues.")
    parser.add_argument("owner", help="owner of the GitHub repository")
    ...
    args = parser.parse_args()
    print(...)
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

```console
uv run ghcli octocat Hello-World
uv run ghcli --help
```

</details>

## A function for the logic

Create a `src/ghcli/api.py` module, which will hold the software's logic: the calls to
the GitHub API. For now, write in it a `list_issues(owner: str, repo: str) -> None`
function that prints its arguments, and have `main` call `list_issues` with the
arguments it read. `cli.py` keeps only the reading of the arguments.

<details>
<summary>Additional hints</summary>

Inside the package, `from .api import list_issues` imports the function from the
neighboring module.

```python
from .api import list_issues


def main() -> None:
    ...
    list_issues(..., ...)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/api.py`:

```python
"""Calls to the GitHub API."""


def list_issues(owner: str, repo: str) -> None:
    """List the issues of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.
    """
    print(owner, repo)
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
    list_issues(args.owner, args.repo)
```

</details>

## The token, from an environment variable

Write in `api.py` a `_get_token() -> str` function that returns the value of the
`GHCLI_TOKEN` environment variable. When it isn't defined, the function prints this
message to the standard error, then stops the program with the exit code `1`:

```text
Unable to read the GitHub token from the GHCLI_TOKEN environment variable. Define it and
run the program again.
```

Try it with `uv run python -c "from ghcli.api import _get_token; print(_get_token())"`,
in a terminal where you ran `source creds.env`, then in a new terminal.

**Useful documentation**

- https://docs.python.org/3/library/os.html#os.environ
- https://docs.python.org/3/library/sys.html#sys.exit

<details>
<summary>Additional hints</summary>

`os.environ` is a dictionary of the environment variables: a missing key raises a
`KeyError`. `print(..., file=sys.stderr)` writes to the standard error.

```python
import os
import sys


def _get_token() -> str:
    try:
        return ...
    except KeyError:
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


def list_issues(owner: str, repo: str) -> None:
    """List the issues of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.
    """
    print(owner, repo)
```

```console
source creds.env
uv run python -c "from ghcli.api import _get_token; print(_get_token())"
```

</details>

## Listing the issues

Add the [`niquests`](https://niquests.readthedocs.io/) library to the project, which
has `requests`'s interface, in a more modern form (`uv add niquests`). Then turn
`list_issues` into a function that returns the repository's open issues, a list of
`(title, body, url)` tuples: its signature becomes `list_issues(owner: str, repo: str)
-> list[tuple[str, str, str]]`. It asks the GitHub API for these issues:

```python
response = niquests.get(
    f"https://api.github.com/repos/{owner}/{repo}/issues",
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {_get_token()}",
    },
    timeout=10,
)
```

then reads the response, the list of issues as JSON: `response.json()`. Have `main`
print one line per issue, `url - title - body`, and try it: `uv run ghcli <your user>
ghcli-sandbox`, which has none yet, then `uv run ghcli octocat Hello-World`. What
happens for a repository that doesn't exist?

**Useful documentation**

- https://docs.github.com/en/rest/issues/issues#list-repository-issues
- https://niquests.readthedocs.io/en/latest/user/quickstart.html#response-status-codes

<details>
<summary>Additional hints</summary>

Each issue is a dictionary whose `title`, `body` and `html_url` keys (the URL of its
page, whereas `url` is the API's) give what we want; `body` is `None` for an issue
without a body. `response.raise_for_status()` raises a `niquests.HTTPError` when the API
answers with an error, `404` for an unknown repository, `401` for an invalid token. The
API also lists the pull requests, which are issues to it.

```python
def list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]:
    response = niquests.get(...)
    response.raise_for_status()
    return [(issue["title"], ..., ...) for issue in response.json()]
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


def list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]:
    """List the open issues of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.

    Returns:
        The title, body and URL of each issue.
    """
    # https://docs.github.com/en/rest/issues/issues#list-repository-issues
    response = niquests.get(
        f"{API_URL}/repos/{owner}/{repo}/issues", headers=_headers(), timeout=10
    )
    # An error status (404 for an unknown repository, 401 for a bad token)
    # raises niquests.HTTPError.
    response.raise_for_status()
    # An issue's body is null when it has none.
    return [
        (issue["title"], issue["body"] or "", issue["html_url"])
        for issue in response.json()
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
uv run ghcli octocat Hello-World
```

For an unknown repository, `raise_for_status` raises a `niquests.HTTPError` (`404 Client
Error: Not Found`).

</details>

## Creating an issue: two commands

Add to `api.py` a `create_issue(owner: str, repo: str, title: str, body: str) ->
tuple[str, str, str]` function, which creates an issue and returns its title, body and
URL. It sends the issue's title and body to the API, as JSON:

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

**Useful documentation**

- https://docs.github.com/en/rest/issues/issues#create-an-issue
- https://docs.python.org/3/library/argparse.html#subcommands

<details>
<summary>Additional hints</summary>

`parser.add_subparsers(dest="command", required=True)` returns an object whose
`add_parser("list")` creates the subcommand's parser; `args.command` says which one
ran. Both subcommands share `owner` and `repo`: a loop adds them to both. The API
answers `201 Created` with the created issue, in the same format as an issue of the
list.

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
if args.command == "list":
    ...
elif args.command == "create":
    ...
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/api.py`, after `list_issues`:

```python
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
        headers=_headers(),
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
    if args.command == "list":
        for title, body, url in list_issues(args.owner, args.repo):
            print(f"{url} - {title} - {body}")
    elif args.command == "create":
        title, body, url = create_issue(args.owner, args.repo, args.title, args.body)
        print(f"{url} - {title} - {body}")
```

```console
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
```

`src/ghcli/cli.py`:

```python
"""Command-line interface to GitHub issues."""

import argparse

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
    if args.command == "list":
        for issue in list_issues(args.owner, args.repo):
            _show(issue)
    elif args.command == "create":
        _show(create_issue(args.owner, args.repo, args.title, args.body))
```

</details>

## Tests

Write in `tests/test_api.py` tests of `_get_token`, `list_issues` and `create_issue`,
and run them with `uv run pytest`. They must depend neither on the network nor on your
token: replace `niquests.get` and `niquests.post` with functions that return a fake
response, and the environment variable with a test value. Also check the error cases: a
missing variable, an unknown repository.

**Useful documentation**

- https://docs.pytest.org/en/stable/how-to/monkeypatch.html
- https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions

<details>
<summary>Additional hints</summary>

`pytest`'s `monkeypatch` fixture replaces an attribute for the duration of a test
(`monkeypatch.setattr(niquests, "get", fake_get)`) and sets or removes an environment
variable (`setenv`, `delenv`). A fake response only needs the methods the code calls:
`raise_for_status` and `json`. An `autouse=True` fixture applies to every test of the
module.

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
```

</details>

<details>
<summary>Solution</summary>

`tests/test_api.py`:

```python
from typing import Any

import niquests
import pytest

from ghcli.api import _get_token, create_issue, list_issues
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


def test_list_issues(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def get(url: str, **kwargs: Any) -> FakeResponse:
        calls.append((url, kwargs["headers"]["Authorization"]))
        return FakeResponse([ISSUE])

    monkeypatch.setattr(niquests, "get", get)
    assert list_issues("octocat", "sandbox") == [
        Issue("A title", "A body", "https://github.com/octocat/sandbox/issues/1")
    ]
    assert calls == [
        ("https://api.github.com/repos/octocat/sandbox/issues", "Bearer a-token")
    ]


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
```

```console
uv run pytest
```

</details>

## Publishing on Test PyPI

Everything seems ready for a first release. Publish your package on Test PyPI, PyPI's
test index:

1. The name `ghcli` can be published only once: in `pyproject.toml`, rename the project
   `ghcli-<your GitHub user>`, in lowercase, without changing the name of the package
   one imports, `ghcli`.
2. Declare in `pyproject.toml` the `testpypi` index, its URL and the one packages are
   published to.
3. [Create an account](https://test.pypi.org/account/register/) on Test PyPI (it asks
   for two-factor authentication), then [an API
   token](https://test.pypi.org/manage/account/token/), for the whole account.
4. Build the package with `uv build`, then publish it with `uv publish --index testpypi
   --token <your token>`.
5. Find its page on Test PyPI, then install and run it, without the repository: `uvx
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

`pyproject.toml`, here for the user `octocat`:

```toml
[project]
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
uv build
uv publish --index testpypi --token <your token>
uvx --index https://pypi.org/simple/ --default-index https://test.pypi.org/simple/ --from ghcli-<your user> ghcli --help
```

The package's page is `https://test.pypi.org/project/ghcli-<your user>/`.

</details>
