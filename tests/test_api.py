import sys
from typing import Any

import niquests
import pytest

from ghcli.api import _lit_jeton, cree_ticket, liste_tickets
from ghcli.cli import main
from ghcli.modele import Ticket

TICKET = {
    "title": "Un titre",
    "body": "Un corps",
    "html_url": "https://github.com/octocat/sandbox/issues/1",
}


class FausseReponse:
    """Ce que renvoient `niquests.get` et `niquests.post`, sans le réseau."""

    def __init__(self, donnees: Any, statut: int = 200) -> None:
        self.donnees = donnees
        self.statut = statut

    def raise_for_status(self) -> None:
        if self.statut >= 400:
            raise niquests.HTTPError(self.statut)

    def json(self) -> Any:
        return self.donnees


@pytest.fixture(autouse=True)
def jeton(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GHCLI_TOKEN", "un-jeton")


def test_lit_jeton_lit_l_environnement() -> None:
    assert _lit_jeton() == "un-jeton"


def test_lit_jeton_quitte_sans_la_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GHCLI_TOKEN")
    with pytest.raises(SystemExit):
        _lit_jeton()


def test_lit_jeton_quitte_sur_une_variable_vide(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GHCLI_TOKEN", "")
    with pytest.raises(SystemExit):
        _lit_jeton()


def test_liste_tickets(monkeypatch: pytest.MonkeyPatch) -> None:
    appels = []

    def fausse_lecture(url: str, **kwargs: Any) -> FausseReponse:
        appels.append((url, kwargs["headers"]["Authorization"]))
        return FausseReponse([TICKET, {**TICKET, "pull_request": {}}])

    monkeypatch.setattr(niquests, "get", fausse_lecture)
    assert liste_tickets("octocat", "sandbox") == [
        Ticket("Un titre", "Un corps", "https://github.com/octocat/sandbox/issues/1")
    ]
    assert appels == [
        ("https://api.github.com/repos/octocat/sandbox/issues", "Bearer un-jeton")
    ]


def test_liste_tickets_sans_jeton(monkeypatch: pytest.MonkeyPatch) -> None:
    def fausse_lecture(url: str, **kwargs: Any) -> FausseReponse:
        assert "Authorization" not in kwargs["headers"]
        return FausseReponse([])

    monkeypatch.delenv("GHCLI_TOKEN")
    monkeypatch.setattr(niquests, "get", fausse_lecture)
    assert liste_tickets("octocat", "sandbox") == []


def test_liste_tickets_d_un_depot_inconnu(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(niquests, "get", lambda url, **kwargs: FausseReponse({}, 404))
    with pytest.raises(niquests.HTTPError):
        liste_tickets("octocat", "inconnu")


def test_cree_ticket(monkeypatch: pytest.MonkeyPatch) -> None:
    def fausse_ecriture(url: str, **kwargs: Any) -> FausseReponse:
        assert kwargs["json"] == {"title": "Un titre", "body": "Un corps"}
        return FausseReponse(TICKET, 201)

    monkeypatch.setattr(niquests, "post", fausse_ecriture)
    ticket = cree_ticket("octocat", "sandbox", "Un titre", "Un corps")
    assert ticket.url == "https://github.com/octocat/sandbox/issues/1"


def test_cree_ticket_exige_un_jeton(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GHCLI_TOKEN")
    with pytest.raises(SystemExit):
        cree_ticket("octocat", "sandbox", "Un titre", "Un corps")


def test_main_signale_une_erreur_de_l_api(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(niquests, "get", lambda url, **kwargs: FausseReponse({}, 404))
    monkeypatch.setattr(sys, "argv", ["ghcli", "list", "octocat", "inconnu"])
    with pytest.raises(SystemExit) as info_sortie:
        main()
    assert info_sortie.value.code == 1
    assert "404" in capsys.readouterr().err
