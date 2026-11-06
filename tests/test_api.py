import sys
from typing import Any

import niquests
import pytest

from ghcli.api import _get_token, create_issue, list_issues
from ghcli.cli import main
from ghcli.model import Issue

ISSUE = {
    "title": "A title",
    "body": "A body",
    "html_url": "https://github.com/octocat/sandbox/issues/1",
}


class FakeResponse:
    """What `niquests.get` and `niquests.post` return, without the network."""

    def __init__(self, data: Any, status_code: int = 200) -> None:
        self.data = data
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise niquests.HTTPError(self.status_code)

    def json(self) -> Any:
        return self.data


@pytest.fixture(autouse=True)
def token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GHCLI_TOKEN", "a-token")


def test_get_token_reads_the_environment() -> None:
    assert _get_token() == "a-token"


def test_get_token_exits_without_the_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GHCLI_TOKEN")
    with pytest.raises(SystemExit):
        _get_token()


def test_get_token_exits_on_an_empty_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GHCLI_TOKEN", "")
    with pytest.raises(SystemExit):
        _get_token()


def test_list_issues(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def get(url: str, **kwargs: Any) -> FakeResponse:
        calls.append((url, kwargs["headers"]["Authorization"]))
        return FakeResponse([ISSUE, {**ISSUE, "pull_request": {}}])

    monkeypatch.setattr(niquests, "get", get)
    assert list_issues("octocat", "sandbox") == [
        Issue("A title", "A body", "https://github.com/octocat/sandbox/issues/1")
    ]
    assert calls == [
        ("https://api.github.com/repos/octocat/sandbox/issues", "Bearer a-token")
    ]


def test_list_issues_without_a_token(monkeypatch: pytest.MonkeyPatch) -> None:
    def get(url: str, **kwargs: Any) -> FakeResponse:
        assert "Authorization" not in kwargs["headers"]
        return FakeResponse([])

    monkeypatch.delenv("GHCLI_TOKEN")
    monkeypatch.setattr(niquests, "get", get)
    assert list_issues("octocat", "sandbox") == []


def test_list_issues_of_an_unknown_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(niquests, "get", lambda url, **kwargs: FakeResponse({}, 404))
    with pytest.raises(niquests.HTTPError):
        list_issues("octocat", "unknown")


def test_create_issue(monkeypatch: pytest.MonkeyPatch) -> None:
    def post(url: str, **kwargs: Any) -> FakeResponse:
        assert kwargs["json"] == {"title": "A title", "body": "A body"}
        return FakeResponse(ISSUE, 201)

    monkeypatch.setattr(niquests, "post", post)
    issue = create_issue("octocat", "sandbox", "A title", "A body")
    assert issue.url == "https://github.com/octocat/sandbox/issues/1"


def test_create_issue_needs_a_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GHCLI_TOKEN")
    with pytest.raises(SystemExit):
        create_issue("octocat", "sandbox", "A title", "A body")


def test_main_reports_an_api_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(niquests, "get", lambda url, **kwargs: FakeResponse({}, 404))
    monkeypatch.setattr(sys, "argv", ["ghcli", "list", "octocat", "unknown"])
    with pytest.raises(SystemExit) as exit_info:
        main()
    assert exit_info.value.code == 1
    assert "404" in capsys.readouterr().err
