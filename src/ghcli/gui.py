"""Web interface to GitHub issues, with Gradio."""

import gradio as gr

from .model import Issue


def _format_issue(issue: Issue) -> str:
    """Show an issue in Markdown: its title, linked to its page, then its body.

    Args:
        issue: The issue to show.

    Returns:
        Its Markdown.
    """
    return f"### [{issue.title}]({issue.url})\n\n{issue.body}"


def build_app() -> gr.Blocks:
    """Build the interface: a tab lists a repository's issues, another creates one.

    Returns:
        The app, which `launch()` serves.
    """
    with gr.Blocks(title="ghcli") as app:
        gr.Markdown("# ghcli\n\nList and create the issues of a GitHub repository.")
        with gr.Tab("List issues"):
            # Your code here
            ...
        with gr.Tab("Create an issue"):
            # Your code here
            ...
    return app


def create_gui() -> None:
    """Serve the interface, at http://127.0.0.1:7860 by default."""
    build_app().launch()
