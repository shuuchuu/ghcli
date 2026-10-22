"""Web interface to GitHub issues, with Gradio."""

import gradio as gr
from niquests import HTTPError

from .api import create_issue, list_issues
from .model import Issue


def _format_issue(issue: Issue) -> str:
    """Show an issue in Markdown: its title, linked to its page, then its body.

    Args:
        issue: The issue to show.

    Returns:
        Its Markdown.
    """
    return f"### [{issue.title}]({issue.url})\n\n{issue.body}"


def _list_issues(owner: str, repo: str) -> str:
    try:
        issues = list_issues(owner, repo)
    except HTTPError as error:
        return f"Could not list the issues: {error}"
    return "\n\n---\n\n".join(map(_format_issue, issues)) or "No issue."


def _create_issue(owner: str, repo: str, title: str, body: str) -> str:
    try:
        issue = create_issue(owner, repo, title, body)
    except HTTPError as error:
        return f"Could not create the issue: {error}"
    return _format_issue(issue)


def build_app() -> gr.Blocks:
    """Build the interface: a tab lists a repository's issues, another creates one.

    Returns:
        The app, which `launch()` serves.
    """
    with gr.Blocks(title="ghcli") as app:
        gr.Markdown("# ghcli\n\nList and create the issues of a GitHub repository.")
        with gr.Tab("List issues"):
            with gr.Row():
                owner = gr.Textbox(label="Owner", placeholder="octocat")
                repo = gr.Textbox(label="Repository", placeholder="Hello-World")
            button = gr.Button("List the issues")
            issues = gr.Markdown()
            # The function's arguments are the inputs' values, its return value
            # the output's.
            button.click(_list_issues, inputs=[owner, repo], outputs=issues)
        with gr.Tab("Create an issue"):
            with gr.Row():
                owner = gr.Textbox(label="Owner")
                repo = gr.Textbox(label="Repository")
            title = gr.Textbox(label="Title")
            body = gr.Textbox(label="Body", lines=6)
            button = gr.Button("Create the issue")
            issue = gr.Markdown()
            button.click(
                _create_issue, inputs=[owner, repo, title, body], outputs=issue
            )
    return app


def create_gui() -> None:
    """Serve the interface, at http://127.0.0.1:7860 by default."""
    build_app().launch()
