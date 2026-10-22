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
