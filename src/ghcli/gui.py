"""Graphical User Interface (GUI) to interact with GitHub issues."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from requests import HTTPError

from .api import create_issue, list_issues
from .io import save_issues_to_file


def _open_list_window() -> None:
    # Creates a new window to list issues
    list_window = tk.Toplevel()
    list_window.title("List Issues")  # Sets the window title

    # Adds a frame to organize widgets
    frame = ttk.Frame(list_window, padding="10")
    frame.grid(row=0, column=0, padx=10, pady=10)

    # Function to open a dialog box and select a file to save the issues
    def browse_file() -> None:
        # Opens a dialog box to choose a file, with .json as the default extension
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        # If the user selects a file, the path is inserted into the entry field
        if file_path:
            entry_outputfile.delete(0, tk.END)  # Clears the entry field
            entry_outputfile.insert(0, file_path)  # Inserts the file path

    # Function to retrieve issues from a GitHub repository and save them to a file
    def retrieve_and_save_issues() -> None:
        # Retrieves the values from input fields
        owner = entry_owner.get()
        repo = entry_repo.get()
        outputfile = entry_outputfile.get()

        # Checks that all fields are filled
        if not owner or not repo or not outputfile:
            messagebox.showerror(
                "Error",
                "Please provide all required inputs: Owner, Repository, and Output "
                "File.",
            )
            return

        # Calls the function to list the issues of the repository
        try:
            issues = list_issues(owner, repo)

            # If issues are retrieved, they are saved to the specified file
            if issues:
                save_issues_to_file(issues, Path(outputfile))
                messagebox.showinfo(
                    "Success", f"Issues successfully saved to {outputfile}"
                )
        except HTTPError:
            messagebox.showerror(
                "Error", "Failed to retrieve issues. Check the repository details."
            )

    # Creating widgets for the window interface
    ttk.Label(frame, text="Owner:").grid(row=0, column=0, padx=10, pady=5)
    entry_owner = ttk.Entry(frame)
    entry_owner.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Repository:").grid(row=1, column=0, padx=10, pady=5)
    entry_repo = ttk.Entry(frame)
    entry_repo.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Output File:").grid(row=2, column=0, padx=10, pady=5)
    entry_outputfile = ttk.Entry(frame)
    entry_outputfile.grid(row=2, column=1, padx=10, pady=5)

    # Button to browse files
    browse_button = ttk.Button(frame, text="Browse", command=browse_file)
    browse_button.grid(row=2, column=2, padx=10, pady=5)

    # Button to retrieve and save issues
    retrieve_button = ttk.Button(
        frame, text="Retrieve and Save Issues", command=retrieve_and_save_issues
    )
    retrieve_button.grid(row=3, column=1, padx=10, pady=10)


def _open_create_window() -> None:
    # Creates a new window to create an issue
    create_window = tk.Toplevel()
    create_window.title("Create Issue")  # Sets the window title

    # Adds a frame to organize widgets
    frame = ttk.Frame(create_window, padding="10")
    frame.grid(row=0, column=0, padx=10, pady=10)

    # Function to submit a new issue
    def submit_issue() -> None:
        # Retrieves the values from input fields
        owner = entry_owner.get()
        repo = entry_repo.get()
        title = entry_title.get()
        body = text_body.get("1.0", tk.END).strip()  # Retrieves the issue content

        # Checks that all fields are filled
        if owner and repo and title and body:
            # Calls the function to create an issue
            try:
                result = create_issue(owner, repo, title, body)
                messagebox.showinfo(
                    "Success", f"Issue created: {result.url}"
                )  # Success message
            except HTTPError:
                messagebox.showerror(
                    "Error", "Failed to create the issue. Check your input."
                )
        else:
            messagebox.showerror("Error", "All fields must be filled.")

    # Creating widgets for the window interface
    ttk.Label(frame, text="Owner:").grid(row=0, column=0, padx=10, pady=5)
    entry_owner = ttk.Entry(frame)
    entry_owner.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Repository:").grid(row=1, column=0, padx=10, pady=5)
    entry_repo = ttk.Entry(frame)
    entry_repo.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Title:").grid(row=2, column=0, padx=10, pady=5)
    entry_title = ttk.Entry(frame)
    entry_title.grid(row=2, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Body:").grid(row=3, column=0, padx=10, pady=5)
    # Multiline text area for the issue body
    text_body = tk.Text(frame, width=40, height=10)
    text_body.grid(row=3, column=1, padx=10, pady=5)

    # Button to submit the issue
    submit_button = ttk.Button(frame, text="Create Issue", command=submit_issue)
    submit_button.grid(row=4, column=1, padx=10, pady=10)


def create_gui() -> None:
    """Create the GHCLI GUI."""
    # Creates the main application window
    root = tk.Tk()
    root.title("GHCLI")  # Sets the main window title

    # Adds a frame to organize widgets
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, padx=10, pady=10)

    # Button to open the issue listing window
    list_button = ttk.Button(frame, text="List Issues", command=_open_list_window)
    list_button.pack(padx=20, pady=10)

    # Button to open the issue creation window
    create_button = ttk.Button(frame, text="Create Issue", command=_open_create_window)
    create_button.pack(padx=20, pady=10)

    # Starts the Tkinter main loop
    root.mainloop()
