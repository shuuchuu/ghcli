"""Appels à l'API de GitHub."""

import os
import sys

import niquests

from .modele import Ticket

URL_API = "https://api.github.com"


def _lit_jeton() -> str:
    jeton = os.environ.get("GHCLI_TOKEN")
    if not jeton:
        print(
            "Impossible de lire le jeton GitHub dans la variable d'environnement "
            "GHCLI_TOKEN. Définissez-la et relancez le programme.",
            file=sys.stderr,
        )
        sys.exit(1)
    return jeton


def _entetes(jeton: str | None) -> dict[str, str]:
    entetes = {"Accept": "application/vnd.github+json"}
    # Sans jeton, l'API répond tout de même aux lectures des dépôts publics.
    if jeton:
        entetes["Authorization"] = f"Bearer {jeton}"
    return entetes


def liste_tickets(proprietaire: str, depot: str) -> list[Ticket]:
    """Liste les tickets ouverts parmi les 100 derniers d'un dépôt GitHub.

    Args:
        proprietaire: Le propriétaire du dépôt.
        depot: Le nom du dépôt.

    Returns:
        Ses tickets, sans ses pull requests.
    """
    # https://docs.github.com/en/rest/issues/issues#list-repository-issues
    reponse = niquests.get(
        f"{URL_API}/repos/{proprietaire}/{depot}/issues",
        params={"per_page": "100"},
        headers=_entetes(os.environ.get("GHCLI_TOKEN")),
        timeout=10,
    )
    # Un statut d'erreur (404 pour un dépôt inconnu, 401 pour un jeton invalide)
    # lève niquests.HTTPError.
    reponse.raise_for_status()
    # L'API compte les pull requests parmi les tickets.
    return [
        Ticket.depuis_dict(ticket)
        for ticket in reponse.json()
        if "pull_request" not in ticket
    ]


def cree_ticket(proprietaire: str, depot: str, titre: str, corps: str) -> Ticket:
    """Crée un ticket dans un dépôt GitHub.

    Args:
        proprietaire: Le propriétaire du dépôt.
        depot: Le nom du dépôt.
        titre: Le titre du ticket.
        corps: Le corps du ticket.

    Returns:
        Le ticket créé.
    """
    # https://docs.github.com/en/rest/issues/issues#create-an-issue
    reponse = niquests.post(
        f"{URL_API}/repos/{proprietaire}/{depot}/issues",
        json={"title": titre, "body": corps},
        headers=_entetes(_lit_jeton()),
        timeout=10,
    )
    reponse.raise_for_status()
    return Ticket.depuis_dict(reponse.json())
