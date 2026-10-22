"""Graphical user interface to GitHub issues, with Tkinter."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from niquests import HTTPError

from .api import create_issue, list_issues
from .io import save_issues_to_file


def _window(title: str) -> ttk.Frame:
    """Open a window on top of the main one.

    Args:
        title: The window's title.

    Returns:
        The window's frame, to lay out its widgets in with `grid`.
    """
    window = tk.Toplevel()
    window.title(title)
    frame = ttk.Frame(window, padding=10)
    frame.grid()
    return frame


def _entry(frame: ttk.Frame, label: str, row: int) -> ttk.Entry:
    """Add a labeled entry on a row of a frame.

    Args:
        frame: The frame to add it to.
        label: The text on its left.
        row: Its row in the frame's grid.

    Returns:
        The entry, whose `get()` gives the text typed in.
    """
    ttk.Label(frame, text=label).grid(row=row, column=0, padx=10, pady=5, sticky="w")
    entry = ttk.Entry(frame, width=40)
    entry.grid(row=row, column=1, padx=10, pady=5)
    return entry


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


def create_gui() -> None:
    """Open the main window, whose buttons open the others."""
    root = tk.Tk()
    root.title("ghcli")
    frame = ttk.Frame(root, padding=10)
    frame.grid()
    ttk.Button(frame, text="List issues", command=_open_list_window).grid(
        row=0, column=0, padx=20, pady=10
    )
    ttk.Button(frame, text="Create an issue", command=_open_create_window).grid(
        row=1, column=0, padx=20, pady=10
    )
    root.mainloop()
