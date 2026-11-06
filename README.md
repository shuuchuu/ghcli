# Gradio web interface for GitHub Issues

*[Version française](https://github.com/shuuchuu/ghcli/tree/gradio)*

The project of the *Gradio web interface for GitHub Issues* lab. It starts from the
solution of the [*Command-line interface for GitHub
Issues*](https://github.com/shuuchuu/ghcli/tree/main-en) lab: `ghcli list` and `ghcli
create` list and create a repository's issues, and are tested. We are going to add a
web interface to them, with Gradio. Its instructions are below, to run the lab in a
GitHub Codespace or a local clone; they are the same as the lab's notebook, in
[English](https://colab.research.google.com/github/shuuchuu/labs/blob/main/gui-github-issues-gradio-hands-on-en.ipynb)
or in
[French](https://colab.research.google.com/github/shuuchuu/labs/blob/main/gui-github-issues-gradio-hands-on-fr.ipynb),
which runs it in Colab.

For that, the project holds:

- `src/ghcli/gui.py`, the interface to complete: `build_app` builds an app with two
  tabs, empty for now, `create_gui` serves it, and `_format_issue` writes an issue in
  Markdown;
- the `ghcli gui` command, which starts the interface.

## Setting up the working environment

This English version of the lab is the repository's `gradio-en` branch. Open it in a
Codespace: on GitHub, on the `gradio-en` branch, **Code** > **Codespaces** > **Create
codespace on gradio-en**, or [this
link](https://codespaces.new/shuuchuu/ghcli/tree/gradio-en). The Codespace installs
the dependencies when it is created, in the project's `.venv`.

In a local clone of that branch (`git clone -b gradio-en
https://github.com/shuuchuu/ghcli.git`), install
[uv](https://docs.astral.sh/uv/getting-started/installation/), then run `uv sync` at the
root of the repository.

`ghcli` needs a GitHub token: if you don't have one, create a test repository and a
token as [the command-line interface's
instructions](https://github.com/shuuchuu/ghcli/tree/main-en#a-test-repository-and-a-github-token)
explain, and put it in a `creds.env` file at the root of the repository. The commands
run in a terminal at the root of the repository (**Terminal** > **New Terminal** in the
Codespace), after `source creds.env`. `uv run ghcli gui` serves the interface at
`http://127.0.0.1:7860`: the Codespace offers to open it in the browser (**Open in
Browser**, or the **Ports** tab, next to the terminal). `Ctrl+C` stops it, before
starting it again after a change. The solutions are on the repository's
[`gradio-solution-en` branch](https://github.com/shuuchuu/ghcli/tree/gradio-solution-en).

## Listing a repository's issues

In `build_app`'s *List issues* tab, add two text boxes, the repository's owner and its
name, a *List the issues* button and a Markdown area where the issues show. The button
calls a `_list_issues(owner: str, repo: str) -> str` function, to write, which returns
the repository's issues in Markdown, separated by a horizontal rule (`---`), `No
issue.` when it has none, or an error message when the API returns one.

**Useful documentation**

- https://www.gradio.app/guides/blocks-and-event-listeners
- https://www.gradio.app/docs/gradio/textbox
- https://www.gradio.app/docs/gradio/markdown

<details>
<summary>Additional hints</summary>

Inside a `with gr.Tab(...)` block, each component created is added to the tab, and
`with gr.Row():` lays out several side by side. `button.click(function, inputs=[...],
outputs=...)` calls the function with the input components' values, and shows what it
returns in the output one. `list_issues` raises a `niquests.HTTPError` for an unknown
repository.

```python
def _list_issues(owner: str, repo: str) -> str:
    try:
        issues = list_issues(owner, repo)
    except HTTPError as error:
        return ...
    return "\n\n---\n\n".join(...) or "No issue."


# In build_app:
with gr.Tab("List issues"):
    with gr.Row():
        owner = gr.Textbox(label="Owner", placeholder="octocat")
        ...
    button = gr.Button("List the issues")
    issues = gr.Markdown()
    button.click(_list_issues, inputs=[...], outputs=...)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/gui.py`, with its imports:

```python
"""Web interface to GitHub issues, with Gradio."""

import gradio as gr
from niquests import HTTPError

from .api import create_issue, list_issues
from .model import Issue
```

```python
def _list_issues(owner: str, repo: str) -> str:
    try:
        issues = list_issues(owner, repo)
    except HTTPError as error:
        return f"Could not list the issues: {error}"
    return "\n\n---\n\n".join(map(_format_issue, issues)) or "No issue."
```

In `build_app`:

```python
with gr.Tab("List issues"):
    with gr.Row():
        owner = gr.Textbox(label="Owner", placeholder="octocat")
        repo = gr.Textbox(label="Repository", placeholder="Hello-World")
    button = gr.Button("List the issues")
    issues = gr.Markdown()
    # The function's arguments are the inputs' values, its return value
    # the output's.
    button.click(_list_issues, inputs=[owner, repo], outputs=issues)
```

</details>

## Creating an issue

In the *Create an issue* tab, add the repository's owner, its name, the issue's title
and its body (a multi-line text box), a *Create the issue* button and a Markdown area
that shows the created issue, or an error message. The button calls a `_create_issue`
function, to write. Create an issue in your test repository, then list its issues in
the other tab.

<details>
<summary>Additional hints</summary>

`gr.Textbox(label="Body", lines=6)` is a six-line text box. The two tabs can reuse the
same variable names: each `click` gets the components that exist when it's called.

```python
def _create_issue(owner: str, repo: str, title: str, body: str) -> str:
    try:
        issue = create_issue(owner, repo, title, body)
    except HTTPError as error:
        return ...
    return _format_issue(issue)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/gui.py`:

```python
def _create_issue(owner: str, repo: str, title: str, body: str) -> str:
    try:
        issue = create_issue(owner, repo, title, body)
    except HTTPError as error:
        return f"Could not create the issue: {error}"
    return _format_issue(issue)
```

In `build_app`:

```python
with gr.Tab("Create an issue"):
    with gr.Row():
        owner = gr.Textbox(label="Owner")
        repo = gr.Textbox(label="Repository")
    title = gr.Textbox(label="Title")
    body = gr.Textbox(label="Body", lines=6)
    button = gr.Button("Create the issue")
    issue = gr.Markdown()
    button.click(_create_issue, inputs=[owner, repo, title, body], outputs=issue)
```

</details>
