"""Interface graphique pour les tickets GitHub, avec Tkinter."""

import tkinter as tk
from tkinter import ttk


def _ouvre_fenetre(titre: str) -> ttk.Frame:
    """Ouvre une fenêtre au-dessus de la principale.

    Args:
        titre: Le titre de la fenêtre.

    Returns:
        Le cadre de la fenêtre, où placer ses widgets avec `grid`.
    """
    fenetre = tk.Toplevel()
    fenetre.title(titre)
    cadre = ttk.Frame(fenetre, padding=10)
    cadre.grid()
    return cadre


def _ajoute_champ(cadre: ttk.Frame, libelle: str, ligne: int) -> ttk.Entry:
    """Ajoute un champ de saisie avec son libellé sur une ligne d'un cadre.

    Args:
        cadre: Le cadre où l'ajouter.
        libelle: Le texte à sa gauche.
        ligne: Sa ligne dans la grille du cadre.

    Returns:
        Le champ, dont `get()` donne le texte saisi.
    """
    ttk.Label(cadre, text=libelle).grid(
        row=ligne, column=0, padx=10, pady=5, sticky="w"
    )
    champ = ttk.Entry(cadre, width=40)
    champ.grid(row=ligne, column=1, padx=10, pady=5)
    return champ


def _ouvre_fenetre_liste() -> None:
    """Ouvre la fenêtre qui enregistre les tickets d'un dépôt dans un fichier JSON."""
    # Votre code ici


def _ouvre_fenetre_creation() -> None:
    """Ouvre la fenêtre qui crée un ticket."""
    # Votre code ici


def cree_interface() -> None:
    """Ouvre la fenêtre principale, dont les boutons ouvrent les autres."""
    racine = tk.Tk()
    racine.title("ghcli")
    cadre = ttk.Frame(racine, padding=10)
    cadre.grid()
    ttk.Button(cadre, text="Lister les tickets", command=_ouvre_fenetre_liste).grid(
        row=0, column=0, padx=20, pady=10
    )
    ttk.Button(cadre, text="Créer un ticket", command=_ouvre_fenetre_creation).grid(
        row=1, column=0, padx=20, pady=10
    )
    racine.mainloop()
