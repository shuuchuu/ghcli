"""Enregistrement des tickets dans des fichiers."""

import json
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path

from .modele import Ticket


def enregistre_tickets(tickets: Iterable[Ticket], chemin: Path) -> None:
    """Enregistre des tickets dans un fichier JSON, sous forme de liste d'objets.

    Args:
        tickets: Les tickets à enregistrer.
        chemin: Le fichier JSON à écrire.
    """
    donnees = [asdict(ticket) for ticket in tickets]
    chemin.write_text(
        json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8"
    )
