"""Interface web pour les tickets GitHub, avec Gradio."""

import gradio as gr

from .modele import Ticket


def _formate_ticket(ticket: Ticket) -> str:
    """Montre un ticket en Markdown : son titre, lié à sa page, puis son corps.

    Args:
        ticket: Le ticket à montrer.

    Returns:
        Son Markdown.
    """
    return f"### [{ticket.titre}]({ticket.url})\n\n{ticket.corps}"


def construit_app() -> gr.Blocks:
    """Construit l'application : un onglet liste les tickets, un autre en crée un.

    Returns:
        L'application, que `launch()` sert.
    """
    with gr.Blocks(title="ghcli") as app:
        gr.Markdown("# ghcli\n\nListe et crée les tickets d'un dépôt GitHub.")
        with gr.Tab("Lister les tickets"):
            # Votre code ici
            ...
        with gr.Tab("Créer un ticket"):
            # Votre code ici
            ...
    return app


def cree_interface() -> None:
    """Sert l'interface, à l'adresse http://127.0.0.1:7860 par défaut."""
    construit_app().launch()
