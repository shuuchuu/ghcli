# Command-Line Interface for GitHub Issues

[Final version on GitHub](https://github.com/shuuchuu/ghcli/tree/main-en).

The goal of this practical exercise is to apply the engineering principles learned during the training. We will create a command-line interface for GitHub Issues, package it, and publish it on Test PyPI.

For the development environment, we will use GitHub Codespaces.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/shuuchuu/ghcli/tree/main-en)

## Creating a GitHub Token

To interact with the GitHub API, you will need a token:

1. If you don’t have a GitHub account yet, create one by following [this link](https://github.com/signup), then log in.
2. Create a token by following [this link](https://github.com/settings/tokens/new) with the following options:
    - `Note`: `GHCLI`
    - `Expiration`: `7 days`
    - `public_repo`: checked
3. Create a file named `creds.env` and copy the token value into it in the following format:

    ```shell
    export GHCLI_TOKEN=ghp_123
    ```

  You can then run `source creds.env` in the terminal before launching the software to authenticate.

## Creating an Entry Point

- Create a `cli.py` file in your source directory.
- Write a `main` function inside it that takes no arguments and prints `Hello World`.
- Modify the `pyproject.toml` file so that the `ghcli` command launches the `main` function from `cli.py`, as explained in the [`uv` documentation](https://docs.astral.sh/uv/concepts/projects/config/#entry-points):

    ```toml
    [project.scripts]
    ghcli = 'ghcli.cli:main'
    ```

- Run the command `uv sync` to activate the entry point.
- Test it by running `ghcli`.

## Adding a Simple Parser

Modify the `main` function in `cli.py` to accept two command-line arguments: a GitHub repository owner (`owner`) and a repository name (`repo`). Eventually, we will use these arguments to fetch issues.

For now, simply display these arguments in the console.

## Connecting the Simple Parser to a Function

Create a new file named `api.py`, which will contain the logic of our software.

For now, define a function `list_issues` with the following signature:

```python
def list_issues(owner: str, repo: str) -> None:
```

This function should simply print the arguments it receives. Then, ensure that when `ghcli` is executed, it calls `list_issues` with the retrieved arguments.

## Retrieving the GitHub Token from an Environment Variable

Implement a function `_get_token` in `api.py` with the following signature:

```python
def _get_token() -> str:
```

It should return the value of the `GHCLI_TOKEN` environment variable. You can use the `os` module and its `environ` dictionary, which contains all accessible environment variables and their values.

If `GHCLI_TOKEN` is not found in `os.environ`, use the following error handling code:

```python
print(
    "Unable to retrieve the GitHub token from the GHCLI_TOKEN environment variable. "
    "Please set this variable and restart the program.",
    file=sys.stderr,
)
sys.exit(1)
```

## Implementing the `list_issues` Function

Now, implement the `list_issues` function with the following signature:

```python
def list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]:
```

This function should return a list of tuples, where each tuple contains the title, body, and URL of an issue.

To request all issues from a given repository on GitHub, use the following code:

```python
response = requests.get(
    f"https://api.github.com/repos/{owner}/{repo}/issues",
    headers=dict(
        Accept="application/vnd.github.v3+json",
        Authorization=f"token {_get_token()}",
    ),
)
```

You can then extract the response content using:

```python
response.json()
```

For more information on the response format, refer to the [GitHub documentation](https://docs.github.com/en/rest/issues/issues#list-repository-issues).

Finally, ensure the function’s return value is used in `cli.py` to display the results to the user.

## Implementing the `create_issue` Function and Connecting It to `cli.py`

Start by defining a `create_issue` function with the following signature:

```python
def create_issue(
  owner: str, repo: str, title: str, body: str
) -> tuple[str, str, str]:
```

The first step in this exercise is to connect `cli.py` to this function, similar to how we did for `list_issues`. The challenge here is introducing two distinct commands in our interface: `create` and `list`. Refer to the course materials for guidance.

Once connected, implement the function so that it creates an issue and returns a tuple containing the issue’s title, body, and URL.

To request GitHub to create an issue, use:

```python
response = requests.post(
  f"https://api.github.com/repos/{owner}/{repo}/issues",
  json=dict(title=title, body=body),
  headers=dict(
    Accept="application/vnd.github.v3+json",
    Authorization=f"token {_get_token()}",
  ),
)
```

Extract the response content with:

```python
response.json()
```

For more details on the response format, check the [GitHub documentation](https://docs.github.com/en/rest/issues/issues#create-an-issue).

Finally, make sure `cli.py` displays the function’s return values to the user.

## Using a Class to Represent Issues

Currently, we use tuples to represent issues, but this is not ideal—it’s easy to mix up values and introduce bugs.

Using the [`dataclasses` module](https://docs.python.org/3/library/dataclasses.html) from the standard library, create an `Issue` class and update the parts of the code that used tuples accordingly.

## Adding Tests

Now that your project has basic functionality, it’s time to add tests (in a TDD approach, we would have started with these).

Add one test per function in the `tests` folder.

## Publishing

Everything seems ready for the first release! Publish your package on Test PyPI (remember to use the `--index testpypi` argument in your publishing command).
