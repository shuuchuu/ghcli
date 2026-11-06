"""Interface web montrant quand les tickets d'un dépôt ont été ouverts, avec Shiny."""

import plotly.graph_objects as go
from shiny import App, Inputs, Outputs, Session, run_app, ui

interface = ui.page_fluid(
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
        Son HTML, qui charge le JavaScript de Plotly depuis son CDN.
    """
    return ui.HTML(figure.to_html(full_html=False, include_plotlyjs="cdn"))


def serveur(entrees: Inputs, sorties: Outputs, session: Session) -> None:
    """Calcule les sorties à partir des entrées.

    Args:
        entrees: Les entrées, par identifiant : `entrees.proprietaire()` est le
            propriétaire saisi.
        sorties: Les sorties (inutilisées : les décorateurs `render` les enregistrent).
        session: La session du navigateur (inutilisée).
    """
    # Votre code ici


def cree_interface() -> None:
    """Sert l'interface, à l'adresse http://127.0.0.1:8000 par défaut."""
    run_app(App(interface, serveur))  # pyrefly: ignore[not-callable]
