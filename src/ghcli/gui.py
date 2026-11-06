"""Web interface showing when a repository's issues were opened, with Shiny."""

import plotly.graph_objects as go
from plotly.offline import get_plotlyjs_version
from shiny import App, Inputs, Outputs, Session, run_app, ui

# Plotly's JavaScript, loaded once by the page, in its head: loaded by each figure, it
# would come too late to draw the first one.
PLOTLY_SCRIPT = f"https://cdn.plot.ly/plotly-{get_plotlyjs_version()}.min.js"

app_ui = ui.page_fluid(
    ui.head_content(ui.tags.script(src=PLOTLY_SCRIPT)),
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
        Its HTML, without Plotly's JavaScript, which the page's head loads.
    """
    return ui.HTML(figure.to_html(full_html=False, include_plotlyjs=False))


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
    run_app(App(app_ui, server))  # pyrefly: ignore[not-callable]
