"""Command Line Interface (CLI) to interact with GitHub issues."""

import argparse


def _add_repo_args(parser: argparse.ArgumentParser) -> None:
    # Adding the owner option with a default value that points to the Git repository
    # of the project. The other option would have been to add an argument here
    # (same syntax but without the --). In that case, providing a value would have
    # been mandatory to call GHCLI.
    parser.add_argument(
        "--owner", default="mlambda", help="Owner of the GitHub repository"
    )

    # Adding the repo option with a default value that points to the Git repository
    # of the project. The other option would have been to add an argument here
    # (same syntax but without the --). In that case, providing a value would have
    # been mandatory to call GHCLI.
    parser.add_argument("--repo", default="tp-ghcli", help="GitHub repository")


def _create_parser() -> argparse.ArgumentParser:
    # Creating the argument parser
    parser = argparse.ArgumentParser(
        description="GHCLI - CLI to list and create GitHub issues."
    )

    # Creating a subparsers object. This will allow us to create a parser per
    # command: one for the list command, and one for the create command.
    subparsers = parser.add_subparsers(help="Commands", dest="command")

    # Creating the sub-parser for the list command
    parser_list = subparsers.add_parser("list")
    # Adding arguments to identify the target GitHub repository
    _add_repo_args(parser_list)

    # Creating the sub-parser for the create command
    parser_create = subparsers.add_parser("create")
    # Adding arguments to identify the target GitHub repository
    _add_repo_args(parser_create)
    # Adding arguments that allow specifying the content of the issue to be created
    parser_create.add_argument("title", help="Title of the GitHub issue")
    parser_create.add_argument("body", help="Body of the GitHub issue")

    return parser


def main() -> None:
    """Parse CLI arguments and call the corresponding parts of GHCLI."""
    # Creating the argument parser
    parser = _create_parser()

    # Retrieving the arguments passed to the program
    args = parser.parse_args()

    # Using these arguments

    # First, let's check which command was called
    if args.command == "list":
        from .api import list_issues

        # Then, we can use the retrieved arguments to call the corresponding function
        issues = list_issues(owner=args.owner, repo=args.repo)
        for issue in issues:
            print(f"{issue.url} - {issue.title} - {issue.body}")
    if args.command == "create":
        from .api import create_issue

        # And similarly for the create command
        issue = create_issue(
            owner=args.owner, repo=args.repo, title=args.title, body=args.body
        )
        print(f"{issue.url} - {issue.title} - {issue.body}")
    # If no command was called, launch the GUI
    else:
        from .gui import create_gui

        create_gui()
