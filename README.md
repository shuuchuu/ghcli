# Interface graphique Tkinter pour GitHub Issues

*[English version](https://github.com/shuuchuu/ghcli/tree/gui-en)*

Le projet des travaux pratiques *Interface graphique Tkinter pour GitHub Issues*. Ils
partent de la solution des travaux pratiques [*Interface en ligne de commande pour
GitHub Issues*](https://github.com/shuuchuu/ghcli)&nbsp;: `ghcli list` et `ghcli
create` listent et créent les tickets d'un dépôt, et sont testés. Nous allons leur
ajouter une interface graphique, avec Tkinter. Leur énoncé est ci-dessous, pour les
faire dans un Codespace GitHub ou un clone local (Colab n'affiche pas de fenêtres).

Le projet contient pour cela&nbsp;:

- `src/ghcli/gui.py`, l'interface à compléter&nbsp;: `create_gui` ouvre la fenêtre
  principale, dont les deux boutons ouvrent chacun une fenêtre, vide pour l'instant.
  `_window` ouvre une fenêtre et renvoie le cadre où placer ses widgets, `_entry`
  ajoute à un cadre une ligne de formulaire, un libellé et une zone de saisie&nbsp;;
- `src/ghcli/io.py`, dont `save_issues_to_file` enregistre des tickets dans un fichier
  JSON&nbsp;;
- la commande `ghcli gui`, qui lance l'interface.

## Mise en place de l'environnement de travail

Ouvrez le dépôt dans un Codespace, sur sa branche `gui`&nbsp;: sur GitHub, sur la
branche `gui`, **Code** > **Codespaces** > **Create codespace on gui**, ou [ce
lien](https://codespaces.new/shuuchuu/ghcli/tree/gui). Le Codespace installe les
dépendances à sa création, dans le `.venv` du projet, et un bureau, où s'affichent
les fenêtres&nbsp;: dans l'onglet **Ports**, à côté du terminal, survolez la ligne du
port 6080 (*Bureau / Desktop*), cliquez sur l'icône du globe (**Open in Browser**),
puis sur **Connect**.

Dans un clone local de cette branche (`git clone -b gui
https://github.com/shuuchuu/ghcli.git`), installez
[uv](https://docs.astral.sh/uv/getting-started/installation/), puis lancez `uv sync` à
la racine du dépôt&nbsp;: le Python que `uv` installe contient Tkinter.

`ghcli` a besoin d'un jeton GitHub&nbsp;: si vous n'en avez pas, créez un dépôt de test
et un jeton comme l'explique [l'énoncé de l'interface en ligne de
commande](https://github.com/shuuchuu/ghcli#un-dépôt-de-test-et-un-jeton-github), et
mettez-le dans un fichier `creds.env` à la racine du dépôt. Les commandes se lancent
dans un terminal à la racine du dépôt (**Terminal** > **Nouveau terminal** dans le
Codespace), après `source creds.env`. Lancez l'interface avec `uv run ghcli gui`, et
fermez-la (la fenêtre principale) avant de la relancer après une modification. Les
solutions sont sur la [branche
`gui-solution`](https://github.com/shuuchuu/ghcli/tree/gui-solution) du dépôt.

## Enregistrer les tickets d'un dépôt

Écrivez `_open_list_window`, qui ouvre la fenêtre *List issues*&nbsp;: trois zones de
saisie, le propriétaire du dépôt, son nom et le fichier où enregistrer ses tickets, un
bouton *Browse…* qui choisit ce fichier dans une boîte de dialogue, et un bouton *Save
the issues*. Celui-ci liste les tickets du dépôt (`list_issues`), les enregistre dans le
fichier (`save_issues_to_file`), puis l'annonce dans une boîte de dialogue. Une zone
vide, ou une erreur de l'API, s'annonce dans une boîte de dialogue d'erreur.

**Documentation utile**

- https://docs.python.org/fr/3/library/dialog.html#tkinter.filedialog.asksaveasfilename
- https://docs.python.org/fr/3/library/tkinter.messagebox.html

<details>
<summary>Conseils supplémentaires</summary>

`_entry(frame, "Owner:", 0)` place une zone de saisie sur la première ligne du cadre, et
la renvoie&nbsp;: `entry.get()` donne son texte, `entry.delete(0, tk.END)` le vide et
`entry.insert(0, texte)` l'écrit. Les fonctions des boutons se définissent dans
`_open_list_window`, où elles voient ses zones de saisie. `asksaveasfilename` renvoie le
chemin choisi, ou une chaîne vide si l'on annule. `list_issues` lève une
`niquests.HTTPError` pour un dépôt inconnu.

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

`src/ghcli/gui.py`, avec ses imports&nbsp;:

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

## Créer un ticket

Écrivez `_open_create_window`, qui ouvre la fenêtre *Create an issue*&nbsp;: le
propriétaire du dépôt, son nom et le titre du ticket dans des zones de saisie, son
corps dans une zone de texte de plusieurs lignes, et un bouton *Create the issue* qui
crée le ticket (`create_issue`), puis donne son URL dans une boîte de dialogue. Créez
un ticket dans votre dépôt de test, puis enregistrez ses tickets avec l'autre fenêtre.

**Documentation utile**

- https://tkdocs.com/tutorial/text.html

<details>
<summary>Conseils supplémentaires</summary>

`tk.Text(frame, width=40, height=10)` est une zone de texte de plusieurs lignes, qui se
place avec `grid` comme les autres widgets. `text.get("1.0", tk.END)` donne son
contenu, de son premier caractère (ligne 1, colonne 0) à sa fin, qui comprend un retour
à la ligne final&nbsp;: `strip()` l'enlève.

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

`src/ghcli/gui.py`&nbsp;:

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
