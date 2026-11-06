# Tkinter graphical interface for GitHub Issues

*[Version française](https://github.com/shuuchuu/ghcli/tree/gui)*

The project of the *Tkinter graphical interface for GitHub Issues* lab. It starts from
the solution of the [*Command-line interface for GitHub
Issues*](https://github.com/shuuchuu/ghcli/tree/main-en) lab: `ghcli list` and `ghcli
create` list and create a repository's issues, and are tested. We are going to add a
graphical interface to them, with Tkinter. Its instructions are below, to run the lab in
a GitHub Codespace or a local clone (Colab shows no windows).

For that, the project holds:

- `src/ghcli/gui.py`, the interface to complete: `create_gui` opens the main window,
  whose two buttons each open a window, empty for now. `_window` opens a window and
  returns the frame to lay out its widgets in, `_entry` adds a form row to a frame, a
  label and an entry;
- `src/ghcli/io.py`, whose `save_issues_to_file` saves issues to a JSON file;
- the `ghcli gui` command, which starts the interface.

## Setting up the working environment

This English version of the lab is the repository's `gui-en` branch. Open it in a
Codespace: on GitHub, on the `gui-en` branch, **Code** > **Codespaces** > **Create
codespace on gui-en**, or [this
link](https://codespaces.new/shuuchuu/ghcli/tree/gui-en). The Codespace installs the
dependencies when it is created, in the project's `.venv`, and a desktop, where the
windows show: in the **Ports** tab, next to the terminal, hover over the line of port
6080 (*Bureau / Desktop*), click the globe icon (**Open in Browser**), then
**Connect**.

In a local clone of that branch (`git clone -b gui-en
https://github.com/shuuchuu/ghcli.git`), install
[uv](https://docs.astral.sh/uv/getting-started/installation/), then run `uv sync` at the
root of the repository: the Python `uv` installs includes Tkinter.

`ghcli` needs a GitHub token: if you don't have one, create a test repository and a
token as [the command-line interface's
instructions](https://github.com/shuuchuu/ghcli/tree/main-en#a-test-repository-and-a-github-token)
explain, and put it in a `creds.env` file at the root of the repository. The commands
run in a terminal at the root of the repository (**Terminal** > **New Terminal** in the
Codespace), after `source creds.env`. Start the interface with `uv run ghcli gui`, and
close it (the main window) before starting it again after a change. The solutions are
on the repository's [`gui-solution-en`
branch](https://github.com/shuuchuu/ghcli/tree/gui-solution-en).

## Saving a repository's issues

Write `_open_list_window`, which opens the *List issues* window: three entries, the
repository's owner, its name and the file to save its issues to, a *Browse…* button
that picks that file in a dialog, and a *Save the issues* button. The latter lists the
repository's issues (`list_issues`), saves them to the file (`save_issues_to_file`),
then says so in a dialog. An empty entry, or an error of the API, is reported in an
error dialog.

**Useful documentation**

- https://docs.python.org/3/library/dialog.html#tkinter.filedialog.asksaveasfilename
- https://docs.python.org/3/library/tkinter.messagebox.html

<details>
<summary>Additional hints</summary>

`_entry(frame, "Owner:", 0)` puts an entry on the frame's first row, and returns it:
`entry.get()` gives its text, `entry.delete(0, tk.END)` clears it and `entry.insert(0,
text)` writes it. The buttons' functions are defined inside `_open_list_window`, where
they see its entries. `asksaveasfilename` returns the chosen path, or an empty string
when cancelled. `list_issues` raises a `niquests.HTTPError` for an unknown repository.

```python
def _open_list_window() -> None:
    frame = _window("List issues")
    owner = _entry(frame, "Owner:", 0)
    ...

    def browse() -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json")
        ...

    def save() -> None:
        try:
            issues = list_issues(owner.get(), repo.get())
        except HTTPError as error:
            messagebox.showerror("Error", ...)
            return
        ...

    ttk.Button(frame, text="Browse…", command=browse).grid(row=2, column=2)
    ...
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/gui.py`, with its imports:

```python
"""Graphical user interface to GitHub issues, with Tkinter."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from niquests import HTTPError

from .api import create_issue, list_issues
from .io import save_issues_to_file
```

```python
def _open_list_window() -> None:
    """Open the window that saves a repository's issues to a JSON file."""
    frame = _window("List issues")
    owner = _entry(frame, "Owner:", 0)
    repo = _entry(frame, "Repository:", 1)
    output = _entry(frame, "Output file:", 2)

    def browse() -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
        # An empty string when the dialog is cancelled.
        if path:
            output.delete(0, tk.END)
            output.insert(0, path)

    def save() -> None:
        if not (owner.get() and repo.get() and output.get()):
            messagebox.showerror(
                "Error", "Fill in the owner, the repository and the output file."
            )
            return
        try:
            issues = list_issues(owner.get(), repo.get())
        except HTTPError as error:
            messagebox.showerror("Error", f"Could not list the issues: {error}")
            return
        save_issues_to_file(issues, Path(output.get()))
        messagebox.showinfo("Saved", f"{len(issues)} issue(s) saved to {output.get()}")

    ttk.Button(frame, text="Browse…", command=browse).grid(row=2, column=2, padx=10)
    ttk.Button(frame, text="Save the issues", command=save).grid(
        row=3, column=1, pady=10
    )
```

</details>

## Creating an issue

Write `_open_create_window`, which opens the *Create an issue* window: the repository's
owner, its name and the issue's title in entries, its body in a multi-line text area,
and a *Create the issue* button that creates the issue (`create_issue`), then gives its
URL in a dialog. Create an issue in your test repository, then save its issues with the
other window.

**Useful documentation**

- https://tkdocs.com/tutorial/text.html

<details>
<summary>Additional hints</summary>

`tk.Text(frame, width=40, height=10)` is a multi-line text area, laid out with `grid`
like the other widgets. `text.get("1.0", tk.END)` gives its content, from its first
character (line 1, column 0) to its end, which includes a final newline: `strip()`
removes it.

```python
def _open_create_window() -> None:
    frame = _window("Create an issue")
    ...
    body = tk.Text(frame, width=40, height=10)
    body.grid(row=3, column=1, padx=10, pady=5)

    def create() -> None:
        text = body.get("1.0", tk.END).strip()
        ...
        messagebox.showinfo("Created", f"Issue created: {issue.url}")

    ...
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/gui.py`:

```python
def _open_create_window() -> None:
    """Open the window that creates an issue."""
    frame = _window("Create an issue")
    owner = _entry(frame, "Owner:", 0)
    repo = _entry(frame, "Repository:", 1)
    title = _entry(frame, "Title:", 2)
    ttk.Label(frame, text="Body:").grid(row=3, column=0, padx=10, pady=5, sticky="nw")
    body = tk.Text(frame, width=40, height=10)
    body.grid(row=3, column=1, padx=10, pady=5)

    def create() -> None:
        # A Text's content runs from its first line's first character ("1.0") to
        # its end, a newline included.
        text = body.get("1.0", tk.END).strip()
        if not (owner.get() and repo.get() and title.get() and text):
            messagebox.showerror("Error", "Fill in every field.")
            return
        try:
            issue = create_issue(owner.get(), repo.get(), title.get(), text)
        except HTTPError as error:
            messagebox.showerror("Error", f"Could not create the issue: {error}")
            return
        messagebox.showinfo("Created", f"Issue created: {issue.url}")

    ttk.Button(frame, text="Create the issue", command=create).grid(
        row=4, column=1, pady=10
    )
```

</details>
