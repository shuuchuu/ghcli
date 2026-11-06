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


@app.command()
def gui() -> None:
    """Open the graphical interface."""
    # Imported here: the other commands don't need the interface's libraries.
    from .gui import create_gui

    create_gui()


def main() -> None:
    """Run the command the arguments name."""
    try:
        app()
    except niquests.HTTPError as error:
        print(f"GitHub API error: {error}", file=sys.stderr)
        sys.exit(1)
