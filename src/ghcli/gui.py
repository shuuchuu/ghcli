"""Interface graphique pour les tickets GitHub, avec Tkinter."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from niquests import HTTPError

from .api import cree_ticket, liste_tickets
from .io import enregistre_tickets


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
        try:
            ticket = cree_ticket(proprietaire.get(), depot.get(), titre.get(), texte)
        except HTTPError as erreur:
            messagebox.showerror("Erreur", f"Impossible de créer le ticket : {erreur}")
            return
        messagebox.showinfo("Créé", f"Ticket créé : {ticket.url}")

    ttk.Button(cadre, text="Créer le ticket", command=cree).grid(
        row=4, column=1, pady=10
    )


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
