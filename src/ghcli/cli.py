"""Interface en ligne de commande pour les tickets GitHub."""

import sys
from typing import Annotated

import niquests
import typer
from rich.console import Console
from rich.table import Table

from .api import cree_ticket, liste_tickets

app = typer.Typer(help="Liste et crée les tickets d'un dépôt GitHub.")
# Sans balises : le titre d'un ticket peut contenir des crochets.
console = Console(markup=False)

Proprietaire = Annotated[str, typer.Argument(help="Propriétaire du dépôt GitHub.")]
Depot = Annotated[str, typer.Argument(help="Nom du dépôt GitHub.")]


@app.command("list")
def lister(proprietaire: Proprietaire, depot: Depot) -> None:
    """Liste les tickets ouverts d'un dépôt."""
    tableau = Table("Titre", "Corps")
    # Sans retour à la ligne : une URL coupée ne mène plus nulle part.
    tableau.add_column("URL", no_wrap=True)
    for ticket in liste_tickets(proprietaire, depot):
        tableau.add_row(ticket.titre, ticket.corps, ticket.url)
    console.print(tableau)


@app.command("create")
def creer(
    proprietaire: Proprietaire,
    depot: Depot,
    titre: Annotated[str, typer.Argument(help="Titre du ticket.")],
    corps: Annotated[str, typer.Argument(help="Corps du ticket.")],
) -> None:
    """Crée un ticket."""
    ticket = cree_ticket(proprietaire, depot, titre, corps)
    console.print(f"{ticket.url} - {ticket.titre} - {ticket.corps}")


@app.command("gui")
def ouvrir() -> None:
    """Ouvre l'interface graphique."""
    # Importée ici : les autres commandes n'ont pas besoin des bibliothèques de
    # l'interface.
    from .gui import cree_interface

    cree_interface()


def main() -> None:
    """Exécute la commande que nomment les arguments."""
    try:
        app()
    except niquests.HTTPError as erreur:
        print(f"Erreur de l'API GitHub : {erreur}", file=sys.stderr)
        sys.exit(1)
