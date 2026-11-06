"""Interface web montrant quand les tickets d'un dépôt ont été ouverts, avec Shiny."""

from collections import Counter
from typing import TYPE_CHECKING

import plotly.graph_objects as go
from niquests import HTTPError
from plotly.offline import get_plotlyjs_version
from shiny import App, Inputs, Outputs, Session, reactive, render, run_app, ui

from .api import liste_tickets

if TYPE_CHECKING:
    from .modele import Ticket

# Le JavaScript de Plotly, que la page charge une fois, dans son en-tête : chargé par
# chaque figure, il arriverait trop tard pour dessiner la première.
SCRIPT_PLOTLY = f"https://cdn.plot.ly/plotly-{get_plotlyjs_version()}.min.js"

interface = ui.page_fluid(
    ui.head_content(ui.tags.script(src=SCRIPT_PLOTLY)),
    ui.h1("Tickets par date de création"),
    ui.input_text("proprietaire", "Propriétaire du dépôt", value="octocat"),
    ui.input_text("depot", "Nom du dépôt", value="Hello-World"),
    ui.input_action_button("recupere", "Récupérer les tickets"),
    ui.output_text("nombre"),
    ui.output_ui("graphique"),
)


def _convertit_en_html(figure: go.Figure) -> ui.HTML:
    """Convertit une figure Plotly en HTML qu'affiche une sortie `render.ui`.

    Args:
        figure: La figure.

    Returns:
        Son HTML, sans le JavaScript de Plotly, que charge l'en-tête de la page.
    """
    return ui.HTML(figure.to_html(full_html=False, include_plotlyjs=False))


def serveur(entrees: Inputs, sorties: Outputs, session: Session) -> None:
    """Calcule les sorties à partir des entrées.

    Args:
        entrees: Les entrées, par identifiant : `entrees.proprietaire()` est le
            propriétaire saisi.
        sorties: Les sorties (inutilisées : les décorateurs `render` les enregistrent).
        session: La session du navigateur (inutilisée).
    """
    tickets: reactive.Value[list[Ticket]] = reactive.Value([])
    erreur = reactive.Value("")

    # S'exécute à chaque clic sur le bouton seulement, pas quand les entrées changent.
    @reactive.effect
    @reactive.event(entrees.recupere)
    def recupere() -> None:
        try:
            tickets.set(liste_tickets(entrees.proprietaire(), entrees.depot()))
            erreur.set("")
        except HTTPError as exception:
            tickets.set([])
            erreur.set(f"Impossible de lister les tickets : {exception}")

    # Les fonctions portent le nom des identifiants de leurs sorties.
    @render.text
    def nombre() -> str:
        return erreur() or f"{len(tickets())} ticket(s)"

    @render.ui
    def graphique() -> ui.HTML | None:
        if not tickets():
            return None
        par_jour = Counter(ticket.date_creation.date() for ticket in tickets())
        jours = sorted(par_jour)
        figure = go.Figure(go.Bar(x=jours, y=[par_jour[jour] for jour in jours]))
        figure.update_layout(
            title="Tickets ouverts par jour", xaxis_title="Jour", yaxis_title="Tickets"
        )
        return _convertit_en_html(figure)


def cree_interface() -> None:
    """Sert l'interface, à l'adresse http://127.0.0.1:8000 par défaut."""
    run_app(App(interface, serveur))  # pyrefly: ignore[not-callable]
