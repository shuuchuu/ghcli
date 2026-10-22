from datetime import UTC, datetime
from typing import Any

import niquests
import pytest

from ghcli.api import _get_token, create_issue, list_issues
from ghcli.model import Issue

ISSUE = {
    "title": "A title",
    "body": "A body",
    "html_url": "https://github.com/octocat/sandbox/issues/1",
    "created_at": "2026-10-22T09:30:00Z",
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


def test_list_issues(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def get(url: str, **kwargs: Any) -> FakeResponse:
        calls.append((url, kwargs["headers"]["Authorization"]))
        return FakeResponse([ISSUE])

    monkeypatch.setattr(niquests, "get", get)
    assert list_issues("octocat", "sandbox") == [
        Issue(
            "A title",
            "A body",
            "https://github.com/octocat/sandbox/issues/1",
            datetime(2026, 10, 22, 9, 30, tzinfo=UTC),
        )
    ]
    assert calls == [
        ("https://api.github.com/repos/octocat/sandbox/issues", "Bearer a-token")
    ]


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
