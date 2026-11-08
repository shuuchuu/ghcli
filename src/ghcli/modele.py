"""Les tickets que manipule l'interface en ligne de commande."""

from dataclasses import dataclass
from typing import Any, Self


@dataclass
class Ticket:
    """Un ticket GitHub, réduit à ce que montre l'interface en ligne de commande."""

    titre: str
    corps: str
    url: str

    @classmethod
    def depuis_dict(cls, donnees: dict[str, Any]) -> Self:
        """Construit un ticket depuis un dictionnaire de l'API GitHub.

        Args:
            donnees: Un ticket, tel que l'API le renvoie.

        Returns:
            Le ticket.
        """
        # Le corps d'un ticket vaut null quand il n'en a pas.
        return cls(
            titre=donnees["title"], corps=donnees["body"] or "", url=donnees["html_url"]
        )
