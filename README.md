# Interface graphique Tkinter pour GitHub Issues

*[English version](https://github.com/shuuchuu/ghcli/tree/gui-en)*

Le projet des travaux pratiques *Interface graphique Tkinter pour GitHub Issues*. Ils
partent de la solution des travaux pratiques [*Interface en ligne de commande pour
GitHub Issues*](https://github.com/shuuchuu/ghcli)&nbsp;: `ghcli list` et `ghcli
create` listent et créent les tickets d'un dépôt, et sont testés. Nous allons leur
ajouter une interface graphique, avec Tkinter. Leur énoncé est ci-dessous, pour les
faire dans un Codespace GitHub ou un clone local (Colab n'affiche pas de fenêtres).

Le projet contient pour cela&nbsp;:

- `src/ghcli/gui.py`, l'interface à compléter&nbsp;: `cree_interface` ouvre la fenêtre
  principale, dont les deux boutons ouvrent chacun une fenêtre, vide pour l'instant.
  `_ouvre_fenetre` ouvre une fenêtre et renvoie le cadre où placer ses widgets,
  `_ajoute_champ` ajoute à un cadre une ligne de formulaire, un libellé et une zone de
  saisie&nbsp;;
- `src/ghcli/io.py`, dont `enregistre_tickets` enregistre des tickets dans un fichier
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

Écrivez `_ouvre_fenetre_liste`, qui ouvre la fenêtre *Lister les tickets*&nbsp;: trois zones
de saisie, le propriétaire du dépôt, son nom et le fichier où enregistrer ses tickets,
un bouton *Parcourir…* qui choisit ce fichier dans une boîte de dialogue, et un bouton
*Enregistrer les tickets*. Celui-ci liste les tickets du dépôt (`liste_tickets`), les
enregistre dans le fichier (`enregistre_tickets`), puis l'annonce dans une boîte de
dialogue. Une zone vide, ou une erreur de l'API, s'annonce dans une boîte de dialogue
d'erreur.

**Documentation utile**

- https://docs.python.org/fr/3/library/dialog.html#tkinter.filedialog.asksaveasfilename
- https://docs.python.org/fr/3/library/tkinter.messagebox.html

<details>
<summary>Conseils supplémentaires</summary>

`_ajoute_champ(cadre, "Propriétaire :", 0)` place une zone de saisie sur la première
ligne du cadre, et la renvoie&nbsp;: `champ.get()` donne son texte, `champ.delete(0, tk.END)`
le vide et `champ.insert(0, texte)` l'écrit. Les fonctions des boutons se définissent
dans `_ouvre_fenetre_liste`, où elles voient ses zones de saisie. `asksaveasfilename`
renvoie le chemin choisi, ou une chaîne vide si l'on annule. `liste_tickets` lève une
`niquests.HTTPError` pour un dépôt inconnu.

```python
def _ouvre_fenetre_liste() -> None:
    cadre = _ouvre_fenetre("Lister les tickets")
    proprietaire = _ajoute_champ(cadre, "Propriétaire :", 0)
    ...

    def parcourt() -> None:
        chemin = filedialog.asksaveasfilename(defaultextension=".json")
        ...

    def enregistre() -> None:
        try:
            tickets = liste_tickets(proprietaire.get(), depot.get())
        except HTTPError as erreur:
            messagebox.showerror("Erreur", ...)
            return
        ...

    ttk.Button(cadre, text="Parcourir…", command=parcourt).grid(row=2, column=2)
    ...
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/gui.py`, avec ses imports&nbsp;:

```python
"""Interface graphique pour les tickets GitHub, avec Tkinter."""

import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from niquests import HTTPError

from .api import cree_ticket, liste_tickets
from .io import enregistre_tickets
```

```python
def _ouvre_fenetre_liste() -> None:
    """Ouvre la fenêtre qui enregistre les tickets d'un dépôt dans un fichier JSON."""
    cadre = _ouvre_fenetre("Lister les tickets")
    proprietaire = _ajoute_champ(cadre, "Propriétaire :", 0)
    depot = _ajoute_champ(cadre, "Dépôt :", 1)
    sortie = _ajoute_champ(cadre, "Fichier de sortie :", 2)

    def parcourt() -> None:
        chemin = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("Fichiers JSON", "*.json")]
        )
        # Une chaîne vide quand on annule la boîte de dialogue.
        if chemin:
            sortie.delete(0, tk.END)
            sortie.insert(0, chemin)

    def enregistre() -> None:
        if not (proprietaire.get() and depot.get() and sortie.get()):
            messagebox.showerror(
                "Erreur",
                "Renseignez le propriétaire, le dépôt et le fichier de sortie.",
            )
            return
        try:
            tickets = liste_tickets(proprietaire.get(), depot.get())
        except HTTPError as erreur:
            messagebox.showerror(
                "Erreur", f"Impossible de lister les tickets : {erreur}"
            )
            return
        enregistre_tickets(tickets, Path(sortie.get()))
        messagebox.showinfo(
            "Enregistré", f"{len(tickets)} ticket(s) enregistré(s) dans {sortie.get()}"
        )

    ttk.Button(cadre, text="Parcourir…", command=parcourt).grid(
        row=2, column=2, padx=10
    )
    ttk.Button(cadre, text="Enregistrer les tickets", command=enregistre).grid(
        row=3, column=1, pady=10
    )
```

</details>

## Créer un ticket

Écrivez `_ouvre_fenetre_creation`, qui ouvre la fenêtre *Créer un ticket*&nbsp;: le
propriétaire du dépôt, son nom et le titre du ticket dans des zones de saisie, son
corps dans une zone de texte de plusieurs lignes, et un bouton *Créer le ticket* qui
crée le ticket (`cree_ticket`), puis donne son URL dans une boîte de dialogue. Créez
un ticket dans votre dépôt de test, puis enregistrez ses tickets avec l'autre fenêtre.

**Documentation utile**

- https://tkdocs.com/tutorial/text.html

<details>
<summary>Conseils supplémentaires</summary>

`tk.Text(cadre, width=40, height=10)` est une zone de texte de plusieurs lignes, qui se
place avec `grid` comme les autres widgets. `corps.get("1.0", tk.END)` donne son
contenu, de son premier caractère (ligne 1, colonne 0) à sa fin, qui comprend un retour
à la ligne final&nbsp;: `strip()` l'enlève.

```python
def _ouvre_fenetre_creation() -> None:
    cadre = _ouvre_fenetre("Créer un ticket")
    ...
    corps = tk.Text(cadre, width=40, height=10)
    corps.grid(row=3, column=1, padx=10, pady=5)

    def cree() -> None:
        texte = corps.get("1.0", tk.END).strip()
        ...
        messagebox.showinfo("Créé", f"Ticket créé : {ticket.url}")

    ...
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/gui.py`&nbsp;:

```python
def _ouvre_fenetre_creation() -> None:
    """Ouvre la fenêtre qui crée un ticket."""
    cadre = _ouvre_fenetre("Créer un ticket")
    proprietaire = _ajoute_champ(cadre, "Propriétaire :", 0)
    depot = _ajoute_champ(cadre, "Dépôt :", 1)
    titre = _ajoute_champ(cadre, "Titre :", 2)
    ttk.Label(cadre, text="Corps :").grid(row=3, column=0, padx=10, pady=5, sticky="nw")
    corps = tk.Text(cadre, width=40, height=10)
    corps.grid(row=3, column=1, padx=10, pady=5)

    def cree() -> None:
        # Le contenu d'un Text va du premier caractère de sa première ligne ("1.0") à
        # sa fin, retour à la ligne compris.
        texte = corps.get("1.0", tk.END).strip()
        if not (proprietaire.get() and depot.get() and titre.get() and texte):
            messagebox.showerror("Erreur", "Renseignez tous les champs.")
            return
        # Sans jeton, cree_ticket arrête le programme, et la fenêtre avec lui.
        if not os.environ.get("GHCLI_TOKEN"):
            messagebox.showerror(
                "Erreur",
                "Impossible de créer le ticket sans jeton GitHub : définissez la "
                "variable d'environnement GHCLI_TOKEN.",
            )
            return
        try:
            ticket = cree_ticket(proprietaire.get(), depot.get(), titre.get(), texte)
        except HTTPError as erreur:
            messagebox.showerror("Erreur", f"Impossible de créer le ticket : {erreur}")
            return
        messagebox.showinfo("Créé", f"Ticket créé : {ticket.url}")

    ttk.Button(cadre, text="Créer le ticket", command=cree).grid(
        row=4, column=1, pady=10
    )
```

</details>
