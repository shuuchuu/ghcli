"""Graphical user interface to GitHub issues, with Tkinter."""

import tkinter as tk
from tkinter import ttk


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
    # Your code here


def _open_create_window() -> None:
    """Open the window that creates an issue."""
    # Your code here


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
