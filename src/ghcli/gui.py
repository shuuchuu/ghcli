"""Web interface showing when a repository's issues were opened, with Shiny."""

import plotly.graph_objects as go
from shiny import App, Inputs, Outputs, Session, run_app, ui

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
    # Your code here


def create_gui() -> None:
    """Serve the interface, at http://127.0.0.1:8000 by default."""
    run_app(App(app_ui, server))  # ty: ignore[call-non-callable]
