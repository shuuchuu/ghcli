"""Interface web pour les tickets GitHub, avec Gradio."""

import gradio as gr
from niquests import HTTPError

from .api import cree_ticket, liste_tickets
from .modele import Ticket


def _formate_ticket(ticket: Ticket) -> str:
    """Montre un ticket en Markdown : son titre, lié à sa page, puis son corps.

    Args:
        ticket: Le ticket à montrer.

    Returns:
        Son Markdown.
    """
    return f"### [{ticket.titre}]({ticket.url})\n\n{ticket.corps}"


def _liste_tickets(proprietaire: str, depot: str) -> str:
    try:
        tickets = liste_tickets(proprietaire, depot)
    except HTTPError as erreur:
        return f"Impossible de lister les tickets : {erreur}"
    return "\n\n---\n\n".join(map(_formate_ticket, tickets)) or "Aucun ticket."


def _cree_ticket(proprietaire: str, depot: str, titre: str, corps: str) -> str:
    try:
        ticket = cree_ticket(proprietaire, depot, titre, corps)
    except HTTPError as erreur:
        return f"Impossible de créer le ticket : {erreur}"
    return _formate_ticket(ticket)


def construit_app() -> gr.Blocks:
    """Construit l'application : un onglet liste les tickets, un autre en crée un.

    Returns:
        L'application, que `launch()` sert.
    """
    with gr.Blocks(title="ghcli") as app:
        gr.Markdown("# ghcli\n\nListe et crée les tickets d'un dépôt GitHub.")
        with gr.Tab("Lister les tickets"):
            with gr.Row():
                proprietaire = gr.Textbox(label="Propriétaire", placeholder="octocat")
                depot = gr.Textbox(label="Dépôt", placeholder="Hello-World")
            bouton = gr.Button("Afficher les tickets")
            tickets = gr.Markdown()
            # Les arguments de la fonction sont les valeurs des entrées, sa valeur de
            # retour celle de la sortie.
            bouton.click(_liste_tickets, inputs=[proprietaire, depot], outputs=tickets)
        with gr.Tab("Créer un ticket"):
            with gr.Row():
                proprietaire = gr.Textbox(label="Propriétaire")
                depot = gr.Textbox(label="Dépôt")
            titre = gr.Textbox(label="Titre")
            corps = gr.Textbox(label="Corps", lines=6)
            bouton = gr.Button("Créer le ticket")
            ticket = gr.Markdown()
            bouton.click(
                _cree_ticket, inputs=[proprietaire, depot, titre, corps], outputs=ticket
            )
    return app


def cree_interface() -> None:
    """Sert l'interface, à l'adresse http://127.0.0.1:7860 par défaut."""
    construit_app().launch()
