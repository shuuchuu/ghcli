"""Shiny app for plotting GitHub issues by creation date."""


def create_gui() -> None:
    import pandas as pd
    import plotly.express as px
    from shiny import App, Inputs, Outputs, Session, run_app, ui
    from shiny.reactive import Value, effect, event
    from shiny.render import ui as render_ui
    from shiny.ui import h1, input_action_button, input_text, output_ui, page_fluid

    from .api import list_issues
    from .model import Issue

    app_ui = page_fluid(
        h1("GitHub Issues by Creation Date"),
        input_text("owner", "Repository Owner", value="microsoft"),
        input_text("repo", "Repository Name", value="typescript"),
        input_action_button("fetch", "Fetch Issues"),
        output_ui("plot"),
    )

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        issues: Value[list[Issue]] = Value([])

        @effect
        @event(input.fetch)
        def _() -> None:
            try:
                iss = list_issues(input.owner(), input.repo())
                issues.set(iss)
            except Exception as e:
                print(f"Error fetching issues: {e}")
                issues.set([])

        @output
        @render_ui
        def plot() -> ui.Tag | ui.HTML:
            iss = issues()
            if not iss:
                return ui.p("No issues found.")

            df = pd.DataFrame(
                {"created_at": [issue.created_at.date() for issue in iss]}
            )

            df_count = df.groupby("created_at").size().reset_index(name="count")

            fig = px.bar(
                df_count,
                x="created_at",
                y="count",
                title="Number of Issues Opened by Date",
            )
            return ui.HTML(fig.to_html())

    run_app(App(app_ui, server), host="0.0.0.0")  # type: ignore
