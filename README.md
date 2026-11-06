# Shiny dashboard for GitHub Issues

*[Version française](https://github.com/shuuchuu/ghcli/tree/shiny)*

The project of the *Shiny dashboard for GitHub Issues* lab. It starts from the solution
of the [*Command-line interface for GitHub
Issues*](https://github.com/shuuchuu/ghcli/tree/main-en) lab: `ghcli list` and `ghcli
create` list and create a repository's issues, and are tested. We are going to add a
web dashboard to them, with Shiny: the number of issues opened each day, as a bar
chart. Its instructions are below, to run the lab in a GitHub Codespace or a local clone
(Colab doesn't show the web server Shiny opens).

For that, the project holds:

- `src/ghcli/gui.py`, the app to complete: `app_ui` describes its interface (two text
  boxes, `owner` and `repo`, a button, `fetch`, and two outputs, `count` and `plot`),
  `server` will compute its outputs, `create_gui` serves it, and `_figure_html` turns a
  Plotly figure into HTML an output shows;
- in `src/ghcli/model.py`, each issue's creation date, `Issue.created_at`;
- the `ghcli gui` command, which starts the app.

## Setting up the working environment

This English version of the lab is the repository's `shiny-en` branch. Open it in a
Codespace: on GitHub, on the `shiny-en` branch, **Code** > **Codespaces** > **Create
codespace on shiny-en**, or [this
link](https://codespaces.new/shuuchuu/ghcli/tree/shiny-en). The Codespace installs the
dependencies when it is created, in the project's `.venv`.

In a local clone of that branch (`git clone -b shiny-en
https://github.com/shuuchuu/ghcli.git`), install
[uv](https://docs.astral.sh/uv/getting-started/installation/), then run `uv sync` at the
root of the repository.

`ghcli` needs a GitHub token: if you don't have one, create a test repository and a
token as [the command-line interface's
instructions](https://github.com/shuuchuu/ghcli/tree/main-en#a-test-repository-and-a-github-token)
explain, and put it in a `creds.env` file at the root of the repository. The commands
run in a terminal at the root of the repository (**Terminal** > **New Terminal** in the
Codespace), after `source creds.env`. `uv run ghcli gui` serves the app at
`http://127.0.0.1:8000`: the Codespace offers to open it in the browser (**Open in
Browser**, or the **Ports** tab, next to the terminal). `Ctrl+C` stops it, before
starting it again after a change. The solutions are on the repository's
[`shiny-solution-en` branch](https://github.com/shuuchuu/ghcli/tree/shiny-solution-en).

## Fetching the issues on a click

In `server`, fetch the repository's issues (`list_issues`) on each click of the button,
and only then: not on each letter typed in the text boxes. Keep them in a reactive
value, and have the `count` output show their number, `3 issue(s)`, or an error message
when the API returns one.

**Useful documentation**

- https://shiny.posit.co/py/api/core/reactive.value.html
- https://shiny.posit.co/py/api/core/reactive.event.html

<details>
<summary>Additional hints</summary>

`reactive.Value([])` is a reactive value, an empty list at first: `issues()` reads it,
`issues.set(...)` changes it, and the outputs that read it are then computed again. An
effect decorated with `@reactive.event(input.fetch)` runs only on a click of the
`fetch` button. An output is a function of `server` decorated with `@render.text`,
`@render.ui`…, named after its ID. A second reactive value can keep the error message;
`list_issues` raises a `niquests.HTTPError` for an unknown repository.

```python
def server(input: Inputs, output: Outputs, session: Session) -> None:  # ruff: ignore[builtin-argument-shadowing]
    issues: reactive.Value[list[Issue]] = reactive.Value([])
    error = reactive.Value("")

    @reactive.effect
    @reactive.event(input.fetch)
    def fetch() -> None:
        try:
            issues.set(list_issues(input.owner(), input.repo()))
            ...
        except HTTPError as exception:
            ...

    @render.text
    def count() -> str:
        return error() or ...
```

</details>

<details>
<summary>Solution</summary>

The imports of `src/ghcli/gui.py`:

```python
"""Web interface showing when a repository's issues were opened, with Shiny."""

from collections import Counter
from typing import TYPE_CHECKING

import plotly.graph_objects as go
from niquests import HTTPError
from shiny import App, Inputs, Outputs, Session, reactive, render, run_app, ui

from .api import list_issues

if TYPE_CHECKING:
    from .model import Issue
```

`server`, without its docstring:

```python
def server(input: Inputs, output: Outputs, session: Session) -> None:  # ruff: ignore[builtin-argument-shadowing]
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
```

</details>

## The chart

Have the `plot` output show a bar chart of the number of issues opened each day, with
Plotly: the days on the x axis, in order, and the number of issues on the y axis, with
a title and the axes' names. Without issues, the output shows nothing. Try it with a
repository that has many, such as `octocat`/`Hello-World`.

**Useful documentation**

- https://docs.python.org/3/library/collections.html#collections.Counter
- https://plotly.com/python/bar-charts/

<details>
<summary>Additional hints</summary>

`issue.created_at.date()` is the day an issue was created, and a `Counter` counts its
elements: `Counter(["a", "b", "a"])` is `Counter({"a": 2, "b": 1})`.
`go.Figure(go.Bar(x=..., y=...))` is a bar chart, and
`figure.update_layout(title=..., xaxis_title=..., yaxis_title=...)` titles it. A
`@render.ui` output that returns `None` shows nothing.

```python
def server(input: Inputs, output: Outputs, session: Session) -> None:  # ruff: ignore[builtin-argument-shadowing]
    ...

    @render.ui
    def plot() -> ui.HTML | None:
        if not issues():
            return None
        per_day = Counter(issue.created_at.date() for issue in issues())
        days = sorted(per_day)
        figure = go.Figure(go.Bar(x=days, y=...))
        ...
        return _figure_html(figure)
```

</details>

<details>
<summary>Solution</summary>

`server`:

```python
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
```

</details>
