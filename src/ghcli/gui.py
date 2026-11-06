"""Web interface showing when a repository's issues were opened, with Shiny."""

from collections import Counter
from typing import TYPE_CHECKING

import plotly.graph_objects as go
from niquests import HTTPError
from shiny import App, Inputs, Outputs, Session, reactive, render, run_app, ui

from .api import list_issues

if TYPE_CHECKING:
    from .model import Issue

app_ui = ui.page_fluid(
    ui.h1("Issues by creation date"),
    ui.input_text("owner", "Repository owner", value="octocat"),
    ui.input_text("repo", "Repository name", value="Hello-World"),
    ui.input_action_button("fetch", "Fetch the issues"),
    ui.output_text("count"),
    ui.output_ui("plot"),
)


def _figure_html(figure: go.Figure) -> ui.HTML:
    """Turn a Plotly figure into HTML that a `render.ui` output shows.

    Args:
        figure: The figure.

    Returns:
        Its HTML, loading Plotly's JavaScript from its CDN.
    """
    return ui.HTML(figure.to_html(full_html=False, include_plotlyjs="cdn"))


def server(input: Inputs, output: Outputs, session: Session) -> None:  # ruff: ignore[builtin-argument-shadowing]
    """Compute the outputs from the inputs.

    Args:
        input: The inputs, by ID: `input.owner()` is the owner typed in.
        output: The outputs (unused: the `render` decorators register them).
        session: The browser's session (unused).
    """
    issues: reactive.Value[list[Issue]] = reactive.Value([])
    error = reactive.Value("")

    # Runs on each click of the button only, not when the inputs change.
    @reactive.effect
    @reactive.event(input.fetch)
    def fetch() -> None:
        try:
            issues.set(list_issues(input.owner(), input.repo()))
            error.set("")
        except HTTPError as exception:
            issues.set([])
            error.set(f"Could not list the issues: {exception}")

    # The functions are named after their outputs' IDs.
    @render.text
    def count() -> str:
        return error() or f"{len(issues())} issue(s)"

    @render.ui
    def plot() -> ui.HTML | None:
        if not issues():
            return None
        per_day = Counter(issue.created_at.date() for issue in issues())
        days = sorted(per_day)
        figure = go.Figure(go.Bar(x=days, y=[per_day[day] for day in days]))
        figure.update_layout(
            title="Issues opened per day", xaxis_title="Day", yaxis_title="Issues"
        )
        return _figure_html(figure)


def create_gui() -> None:
    """Serve the interface, at http://127.0.0.1:8000 by default."""
    run_app(App(app_ui, server))  # pyrefly: ignore[not-callable]
