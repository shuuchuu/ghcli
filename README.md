# Interface en ligne de commande pour GitHub Issues

*[English version](https://github.com/shuuchuu/ghcli/tree/main-en)*

Le projet des travaux pratiques *Interface en ligne de commande pour GitHub Issues*.
Leur énoncé est ci-dessous, pour les faire dans un Codespace GitHub ou un clone
local&nbsp;; c'est le même que celui du notebook des travaux pratiques, en
[français](https://colab.research.google.com/github/shuuchuu/labs/blob/main/cli-github-issues-cli-hands-on-fr.ipynb)
ou en
[anglais](https://colab.research.google.com/github/shuuchuu/labs/blob/main/cli-github-issues-cli-hands-on-en.ipynb),
qui les fait dans Colab.

Le but de ces travaux pratiques est de mettre en pratique les principes d'ingénierie
vus durant la formation&nbsp;: nous allons créer `ghcli`, une interface en ligne de
commande qui liste et crée les tickets (*issues*) d'un dépôt GitHub, en faire un paquet
et le publier sur Test PyPI. Le dépôt est un projet `uv` dont le paquet,
`src/ghcli/`, est encore vide.

## Mise en place de l'environnement de travail

Ouvrez le dépôt dans un Codespace&nbsp;: sur GitHub, **Code** > **Codespaces** >
**Create codespace on main**, ou [ce lien](https://codespaces.new/shuuchuu/ghcli). Le
Codespace installe les dépendances à sa création, dans le `.venv` du projet.

Dans un clone local, installez
[uv](https://docs.astral.sh/uv/getting-started/installation/), puis lancez `uv sync` à
la racine du dépôt.

Les commandes ci-dessous se lancent dans un terminal à la racine du dépôt (**Terminal** >
**Nouveau terminal** dans le Codespace), avec `uv run`, qui les exécute dans
l'environnement du projet. Les fichiers s'écrivent dans l'éditeur. Les solutions sont
aussi sur la [branche `solution`](https://github.com/shuuchuu/ghcli/tree/solution) du
dépôt.

## Un dépôt de test et un jeton GitHub

`ghcli` crée des tickets&nbsp;: il lui faut un dépôt où les créer, et un jeton
d'accès à l'API de GitHub qui n'autorise que cela.

1. Si vous n'avez pas encore de compte GitHub, [créez-en un](https://github.com/signup),
   puis identifiez-vous.
2. [Créez un dépôt](https://github.com/new) public nommé `ghcli-sandbox`, avec un
   README (**Add README**).
3. [Créez un jeton](https://github.com/settings/personal-access-tokens/new)
   (*fine-grained personal access token*)&nbsp;: **Token name** `GHCLI`, **Expiration**
   7 jours, **Repository access** > **Only select repositories** > `ghcli-sandbox`,
   puis, dans **Permissions**, **Add permissions** > **Issues**, en **Read and write**.
   Copiez sa valeur, qui commence par `github_pat_`&nbsp;: GitHub ne l'affiche qu'une
   fois.
4. Créez à la racine du dépôt un fichier `creds.env` (que `.gitignore` exclut des
   commits) qui contient&nbsp;:

   ```shell
   export GHCLI_TOKEN=github_pat_...
   ```

   et lancez `source creds.env` dans chaque nouveau terminal, avant `ghcli`.

## Un point d'entrée

Créez le module `src/ghcli/cli.py`, avec une fonction `main`, sans argument, qui
affiche `Hello World`. Déclarez dans `pyproject.toml` la commande `ghcli`, qui lance
cette fonction, puis lancez `uv sync`, qui l'installe dans l'environnement du projet,
et essayez-la&nbsp;: `uv run ghcli`.

**Documentation utile**

- https://docs.astral.sh/uv/concepts/projects/config/#entry-points

<details>
<summary>Conseils supplémentaires</summary>

Une commande se déclare dans la table `[project.scripts]`&nbsp;: son nom, puis le
module et la fonction qu'elle appelle, séparés par `:`.

```toml
[project.scripts]
ghcli = "ghcli....:..."
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/cli.py`&nbsp;:

```python
"""Command-line interface to GitHub issues."""


def main() -> None:
    """Greet the user."""
    print("Hello World")
```

`pyproject.toml`, à la suite de la table `[project]`&nbsp;:

```toml
[project.scripts]
ghcli = "ghcli.cli:main"
```

```console
uv sync
uv run ghcli
```

</details>

## Un parseur d'arguments

Modifiez `main` pour qu'elle lise deux arguments de la ligne de commande, le
propriétaire d'un dépôt GitHub et son nom, et qu'elle les affiche&nbsp;: `uv run ghcli
octocat Hello-World` affiche `octocat Hello-World`. Que donnent `uv run ghcli`, sans
argument, et `uv run ghcli --help`&nbsp;?

**Documentation utile**

- https://docs.python.org/fr/3/library/argparse.html#the-add-argument-method

<details>
<summary>Conseils supplémentaires</summary>

Un argument positionnel est un nom sans tirets&nbsp;: `parser.add_argument("owner",
help="...")`. `parse_args()` renvoie un objet dont chaque argument est un attribut
(`args.owner`). Sans argument, `argparse` affiche l'usage et une erreur&nbsp;; avec
`--help`, l'aide qu'il génère des `help=`.

```python
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="List GitHub issues.")
    parser.add_argument("owner", help="owner of the GitHub repository")
    ...
    args = parser.parse_args()
    print(...)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/cli.py`&nbsp;:

```python
"""Command-line interface to GitHub issues."""

import argparse


def main() -> None:
    """Read a GitHub repository from the arguments."""
    parser = argparse.ArgumentParser(description="List GitHub issues.")
    parser.add_argument("owner", help="owner of the GitHub repository")
    parser.add_argument("repo", help="name of the GitHub repository")
    args = parser.parse_args()
    print(args.owner, args.repo)
```

```console
uv run ghcli octocat Hello-World
uv run ghcli --help
```

</details>

## Une fonction pour la logique

Créez un module `src/ghcli/api.py`, qui contiendra la logique du logiciel&nbsp;: les
appels à l'API de GitHub. Écrivez-y pour l'instant une fonction `list_issues(owner:
str, repo: str) -> None` qui affiche ses arguments, et faites appeler `list_issues` par
`main`, avec les arguments qu'elle a lus. `cli.py` ne garde que la lecture des
arguments.

<details>
<summary>Conseils supplémentaires</summary>

Dans le paquet, `from .api import list_issues` importe la fonction du module voisin.

```python
from .api import list_issues


def main() -> None:
    ...
    list_issues(..., ...)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/api.py`&nbsp;:

```python
"""Calls to the GitHub API."""


def list_issues(owner: str, repo: str) -> None:
    """List the issues of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.
    """
    print(owner, repo)
```

`src/ghcli/cli.py`&nbsp;:

```python
"""Command-line interface to GitHub issues."""

import argparse

from .api import list_issues


def main() -> None:
    """List the issues of the GitHub repository the arguments name."""
    parser = argparse.ArgumentParser(description="List GitHub issues.")
    parser.add_argument("owner", help="owner of the GitHub repository")
    parser.add_argument("repo", help="name of the GitHub repository")
    args = parser.parse_args()
    list_issues(args.owner, args.repo)
```

</details>

## Le jeton, depuis une variable d'environnement

Écrivez dans `api.py` une fonction `_get_token() -> str` qui renvoie la valeur de la
variable d'environnement `GHCLI_TOKEN`. Quand elle n'est pas définie, la fonction
affiche sur la sortie d'erreur ce message, puis arrête le programme avec le code de
retour `1`&nbsp;:

```text
Unable to read the GitHub token from the GHCLI_TOKEN environment variable. Define it and
run the program again.
```

Essayez-la avec `uv run python -c "from ghcli.api import _get_token;
print(_get_token())"`, dans un terminal où vous avez lancé `source creds.env`, puis
dans un nouveau terminal.

**Documentation utile**

- https://docs.python.org/fr/3/library/os.html#os.environ
- https://docs.python.org/fr/3/library/sys.html#sys.exit

<details>
<summary>Conseils supplémentaires</summary>

`os.environ` est un dictionnaire des variables d'environnement&nbsp;: une clé absente
lève une `KeyError`. `print(..., file=sys.stderr)` écrit sur la sortie d'erreur.

```python
import os
import sys


def _get_token() -> str:
    try:
        return ...
    except KeyError:
        print(..., file=sys.stderr)
        sys.exit(...)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/api.py`&nbsp;:

```python
"""Calls to the GitHub API."""

import os
import sys


def _get_token() -> str:
    try:
        return os.environ["GHCLI_TOKEN"]
    except KeyError:
        print(
            "Unable to read the GitHub token from the GHCLI_TOKEN environment "
            "variable. Define it and run the program again.",
            file=sys.stderr,
        )
        sys.exit(1)


def list_issues(owner: str, repo: str) -> None:
    """List the issues of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.
    """
    print(owner, repo)
```

```console
source creds.env
uv run python -c "from ghcli.api import _get_token; print(_get_token())"
```

</details>

## Lister les tickets

Ajoutez au projet la bibliothèque [`niquests`](https://niquests.readthedocs.io/), qui a
l'interface de `requests`, en plus moderne (`uv add niquests`). Faites ensuite de
`list_issues` une fonction qui renvoie les tickets ouverts du dépôt, une liste de
n-uplets `(titre, corps, url)`&nbsp;: sa signature devient `list_issues(owner: str,
repo: str) -> list[tuple[str, str, str]]`. Elle demande ces tickets à l'API de
GitHub&nbsp;:

```python
response = niquests.get(
    f"https://api.github.com/repos/{owner}/{repo}/issues",
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {_get_token()}",
    },
    timeout=10,
)
```

puis lit la réponse, la liste des tickets en JSON&nbsp;: `response.json()`. Faites
afficher à `main` une ligne par ticket, `url - titre - corps`, et essayez&nbsp;: `uv
run ghcli <votre utilisateur> ghcli-sandbox`, qui n'en a pas encore, puis `uv run ghcli
octocat Hello-World`. Que se passe-t-il pour un dépôt qui n'existe pas&nbsp;?

**Documentation utile**

- https://docs.github.com/en/rest/issues/issues#list-repository-issues
- https://niquests.readthedocs.io/en/latest/user/quickstart.html#response-status-codes

<details>
<summary>Conseils supplémentaires</summary>

Chaque ticket est un dictionnaire, dont les clés `title`, `body` et `html_url` (l'URL
de sa page, quand `url` est celle de l'API) donnent ce qu'on veut&nbsp;; `body` vaut
`None` pour un ticket sans corps. `response.raise_for_status()` lève une
`niquests.HTTPError` quand l'API répond par une erreur, `404` pour un dépôt inconnu,
`401` pour un jeton invalide. L'API liste aussi les *pull requests*, qui sont des
tickets pour elle.

```python
def list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]:
    response = niquests.get(...)
    response.raise_for_status()
    return [(issue["title"], ..., ...) for issue in response.json()]
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/api.py`&nbsp;:

```python
"""Calls to the GitHub API."""

import os
import sys

import niquests

API_URL = "https://api.github.com"


def _get_token() -> str:
    try:
        return os.environ["GHCLI_TOKEN"]
    except KeyError:
        print(
            "Unable to read the GitHub token from the GHCLI_TOKEN environment "
            "variable. Define it and run the program again.",
            file=sys.stderr,
        )
        sys.exit(1)


def _headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {_get_token()}",
    }


def list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]:
    """List the open issues of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.

    Returns:
        The title, body and URL of each issue.
    """
    # https://docs.github.com/en/rest/issues/issues#list-repository-issues
    response = niquests.get(
        f"{API_URL}/repos/{owner}/{repo}/issues", headers=_headers(), timeout=10
    )
    # An error status (404 for an unknown repository, 401 for a bad token)
    # raises niquests.HTTPError.
    response.raise_for_status()
    # An issue's body is null when it has none.
    return [
        (issue["title"], issue["body"] or "", issue["html_url"])
        for issue in response.json()
    ]
```

`src/ghcli/cli.py`&nbsp;:

```python
"""Command-line interface to GitHub issues."""

import argparse

from .api import list_issues


def main() -> None:
    """List the issues of the GitHub repository the arguments name."""
    parser = argparse.ArgumentParser(description="List GitHub issues.")
    parser.add_argument("owner", help="owner of the GitHub repository")
    parser.add_argument("repo", help="name of the GitHub repository")
    args = parser.parse_args()
    for title, body, url in list_issues(args.owner, args.repo):
        print(f"{url} - {title} - {body}")
```

```console
uv add niquests
uv run ghcli octocat Hello-World
```

Pour un dépôt inconnu, `raise_for_status` lève une `niquests.HTTPError` (`404 Client
Error: Not Found`).

</details>

## Créer un ticket&nbsp;: deux commandes

Ajoutez à `api.py` une fonction `create_issue(owner: str, repo: str, title: str, body:
str) -> tuple[str, str, str]`, qui crée un ticket et renvoie son titre, son corps et
son URL. Elle envoie à l'API le titre et le corps du ticket, en JSON&nbsp;:

```python
response = niquests.post(
    f"https://api.github.com/repos/{owner}/{repo}/issues",
    json={"title": title, "body": body},
    headers=...,
    timeout=10,
)
```

`ghcli` a maintenant deux commandes, `ghcli list <propriétaire> <dépôt>` et `ghcli
create <propriétaire> <dépôt> <titre> <corps>`&nbsp;: faites-en deux sous-commandes du
parseur, chacune avec ses arguments. Créez un ticket dans votre dépôt de test, puis
listez-le.

**Documentation utile**

- https://docs.github.com/en/rest/issues/issues#create-an-issue
- https://docs.python.org/fr/3/library/argparse.html#subcommands

<details>
<summary>Conseils supplémentaires</summary>

`parser.add_subparsers(dest="command", required=True)` renvoie un objet dont
`add_parser("list")` crée le parseur de la sous-commande&nbsp;; `args.command` dit
laquelle a été lancée. Les deux sous-commandes ont `owner` et `repo` en commun&nbsp;:
une boucle les leur ajoute. L'API répond `201 Created` avec le ticket créé, au même
format qu'un ticket de la liste.

```python
subparsers = parser.add_subparsers(dest="command", required=True)
list_parser = subparsers.add_parser("list", help="list a repository's issues")
create_parser = subparsers.add_parser("create", help="create an issue")
for subparser in (list_parser, create_parser):
    subparser.add_argument("owner", help="owner of the GitHub repository")
    ...
create_parser.add_argument("title", help="title of the issue")
...
args = parser.parse_args()
if args.command == "list":
    ...
elif args.command == "create":
    ...
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/api.py`, à la suite de `list_issues`&nbsp;:

```python
def create_issue(owner: str, repo: str, title: str, body: str) -> tuple[str, str, str]:
    """Create an issue in a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.
        title: The issue's title.
        body: The issue's body.

    Returns:
        The title, body and URL of the created issue.
    """
    # https://docs.github.com/en/rest/issues/issues#create-an-issue
    response = niquests.post(
        f"{API_URL}/repos/{owner}/{repo}/issues",
        json={"title": title, "body": body},
        headers=_headers(),
        timeout=10,
    )
    response.raise_for_status()
    issue = response.json()
    return issue["title"], issue["body"] or "", issue["html_url"]
```

`src/ghcli/cli.py`&nbsp;:

```python
"""Command-line interface to GitHub issues."""

import argparse

from .api import create_issue, list_issues


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List and create GitHub issues.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="list a repository's issues")
    create_parser = subparsers.add_parser("create", help="create an issue")
    for subparser in (list_parser, create_parser):
        subparser.add_argument("owner", help="owner of the GitHub repository")
        subparser.add_argument("repo", help="name of the GitHub repository")
    create_parser.add_argument("title", help="title of the issue")
    create_parser.add_argument("body", help="body of the issue")
    return parser


def main() -> None:
    """Run the command the arguments name."""
    args = _create_parser().parse_args()
    if args.command == "list":
        for title, body, url in list_issues(args.owner, args.repo):
            print(f"{url} - {title} - {body}")
    elif args.command == "create":
        title, body, url = create_issue(args.owner, args.repo, args.title, args.body)
        print(f"{url} - {title} - {body}")
```

```console
uv run ghcli create <votre utilisateur> ghcli-sandbox "Premier ticket" "Créé par ghcli"
uv run ghcli list <votre utilisateur> ghcli-sandbox
```

</details>

## Une classe pour les tickets

Des n-uplets représentent pour l'instant les tickets&nbsp;: il est facile d'en
confondre l'ordre, et d'introduire ainsi des bugs. Créez dans un module
`src/ghcli/model.py` une classe `Issue`, avec le module `dataclasses`, dont les
attributs sont le titre, le corps et l'URL d'un ticket, et une méthode de classe
`from_dict` qui construit un `Issue` à partir d'un ticket de l'API. `list_issues`
renvoie alors une `list[Issue]`, `create_issue` un `Issue`&nbsp;: adaptez-les, ainsi
que `cli.py`.

**Documentation utile**

- https://docs.python.org/fr/3/library/dataclasses.html
- https://docs.python.org/fr/3/library/functions.html#classmethod

<details>
<summary>Conseils supplémentaires</summary>

`@dataclass` génère le constructeur, la représentation et la comparaison à partir des
attributs annotés. Une méthode de classe reçoit la classe (`cls`) au lieu d'une
instance&nbsp;: c'est un autre constructeur, `Issue.from_dict(issue)`.

```python
from dataclasses import dataclass
from typing import Any, Self


@dataclass
class Issue:
    title: str
    ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(title=data["title"], body=..., url=...)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/model.py`&nbsp;:

```python
"""The issues the CLI handles."""

from dataclasses import dataclass
from typing import Any, Self


@dataclass
class Issue:
    """A GitHub issue, reduced to what the CLI shows."""

    title: str
    body: str
    url: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Build an issue from a dictionary of the GitHub API.

        Args:
            data: An issue, as the API returns it.

        Returns:
            The issue.
        """
        # An issue's body is null when it has none.
        return cls(title=data["title"], body=data["body"] or "", url=data["html_url"])
```

`src/ghcli/api.py`&nbsp;:

```python
"""Calls to the GitHub API."""

import os
import sys

import niquests

from .model import Issue

API_URL = "https://api.github.com"


def _get_token() -> str:
    try:
        return os.environ["GHCLI_TOKEN"]
    except KeyError:
        print(
            "Unable to read the GitHub token from the GHCLI_TOKEN environment "
            "variable. Define it and run the program again.",
            file=sys.stderr,
        )
        sys.exit(1)


def _headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {_get_token()}",
    }


def list_issues(owner: str, repo: str) -> list[Issue]:
    """List the open issues of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.

    Returns:
        Its issues.
    """
    # https://docs.github.com/en/rest/issues/issues#list-repository-issues
    response = niquests.get(
        f"{API_URL}/repos/{owner}/{repo}/issues", headers=_headers(), timeout=10
    )
    # An error status (404 for an unknown repository, 401 for a bad token)
    # raises niquests.HTTPError.
    response.raise_for_status()
    return [Issue.from_dict(issue) for issue in response.json()]


def create_issue(owner: str, repo: str, title: str, body: str) -> Issue:
    """Create an issue in a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.
        title: The issue's title.
        body: The issue's body.

    Returns:
        The created issue.
    """
    # https://docs.github.com/en/rest/issues/issues#create-an-issue
    response = niquests.post(
        f"{API_URL}/repos/{owner}/{repo}/issues",
        json={"title": title, "body": body},
        headers=_headers(),
        timeout=10,
    )
    response.raise_for_status()
    return Issue.from_dict(response.json())
```

`src/ghcli/cli.py`&nbsp;:

```python
"""Command-line interface to GitHub issues."""

import argparse

from .api import create_issue, list_issues
from .model import Issue


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List and create GitHub issues.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="list a repository's issues")
    create_parser = subparsers.add_parser("create", help="create an issue")
    for subparser in (list_parser, create_parser):
        subparser.add_argument("owner", help="owner of the GitHub repository")
        subparser.add_argument("repo", help="name of the GitHub repository")
    create_parser.add_argument("title", help="title of the issue")
    create_parser.add_argument("body", help="body of the issue")
    return parser


def _show(issue: Issue) -> None:
    print(f"{issue.url} - {issue.title} - {issue.body}")


def main() -> None:
    """Run the command the arguments name."""
    args = _create_parser().parse_args()
    if args.command == "list":
        for issue in list_issues(args.owner, args.repo):
            _show(issue)
    elif args.command == "create":
        _show(create_issue(args.owner, args.repo, args.title, args.body))
```

</details>

## Des tests

Écrivez dans `tests/test_api.py` des tests de `_get_token`, `list_issues` et
`create_issue`, et lancez-les avec `uv run pytest`. Ils ne doivent dépendre ni du
réseau, ni de votre jeton&nbsp;: remplacez `niquests.get` et `niquests.post` par des
fonctions qui renvoient une fausse réponse, et la variable d'environnement par une
valeur de test. Vérifiez aussi les cas d'erreur&nbsp;: une variable absente, un dépôt
inconnu.

**Documentation utile**

- https://docs.pytest.org/en/stable/how-to/monkeypatch.html
- https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions

<details>
<summary>Conseils supplémentaires</summary>

La fixture `monkeypatch` de `pytest` remplace un attribut le temps d'un test
(`monkeypatch.setattr(niquests, "get", fake_get)`) et définit ou retire une variable
d'environnement (`setenv`, `delenv`). Une fausse réponse n'a besoin que des méthodes
qu'appelle le code&nbsp;: `raise_for_status` et `json`. Une fixture
`autouse=True` s'applique à tous les tests du module.

```python
class FakeResponse:
    def __init__(self, data, status_code=200):
        self.data = data
        ...

    def raise_for_status(self):
        if self.status_code >= 400:
            raise niquests.HTTPError(self.status_code)

    def json(self):
        return self.data


def test_list_issues(monkeypatch):
    monkeypatch.setenv("GHCLI_TOKEN", "a-token")
    monkeypatch.setattr(niquests, "get", lambda url, **kwargs: FakeResponse([...]))
    assert list_issues("octocat", "sandbox") == [...]
```

</details>

<details>
<summary>Solution</summary>

`tests/test_api.py`&nbsp;:

```python
from typing import Any

import niquests
import pytest

from ghcli.api import _get_token, create_issue, list_issues
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


def test_list_issues(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def get(url: str, **kwargs: Any) -> FakeResponse:
        calls.append((url, kwargs["headers"]["Authorization"]))
        return FakeResponse([ISSUE])

    monkeypatch.setattr(niquests, "get", get)
    assert list_issues("octocat", "sandbox") == [
        Issue("A title", "A body", "https://github.com/octocat/sandbox/issues/1")
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
```

```console
uv run pytest
```

</details>

## Publication sur Test PyPI

Tout semble prêt pour une première version. Publiez votre paquet sur Test PyPI, l'index
de test de PyPI&nbsp;:

1. Le nom `ghcli` ne peut être publié qu'une fois&nbsp;: dans `pyproject.toml`,
   renommez le projet `ghcli-<votre utilisateur GitHub>`, en minuscules, sans changer
   le nom du paquet qu'on importe, `ghcli`.
2. Déclarez dans `pyproject.toml` l'index `testpypi`, son URL et celle où l'on publie.
3. [Créez un compte](https://test.pypi.org/account/register/) sur Test PyPI (il
   demande une authentification à deux facteurs), puis [un jeton
   d'API](https://test.pypi.org/manage/account/token/), pour tout le compte.
4. Construisez le paquet avec `uv build`, puis publiez-le avec `uv publish --index
   testpypi --token <votre jeton>`.
5. Trouvez sa page sur Test PyPI, puis installez-le et lancez-le, sans le dépôt&nbsp;:
   `uvx --index https://pypi.org/simple/ --default-index https://test.pypi.org/simple/
   --from ghcli-<votre utilisateur> ghcli --help`.

**Documentation utile**

- https://docs.astral.sh/uv/concepts/build-backend/#modules
- https://docs.astral.sh/uv/guides/integration/alternative-indexes/
- https://docs.astral.sh/uv/guides/package/#publishing-your-package

<details>
<summary>Conseils supplémentaires</summary>

Le module que construit `uv build` porte par défaut le nom du projet&nbsp;: `module-name`,
dans `[tool.uv.build-backend]`, le fixe. Un index se déclare dans une table
`[[tool.uv.index]]`&nbsp;: `name`, `url`, `publish-url`, et `explicit = true`, pour que
`uv` n'y cherche que les paquets qu'on lui attribue. L'URL de Test PyPI est
`https://test.pypi.org/simple/`, celle où l'on publie `https://test.pypi.org/legacy/`.
Pour `uvx`, PyPI passe avant Test PyPI&nbsp;: `uv` prend chaque paquet sur le premier
index qui l'a, donc `niquests` et ses dépendances sur PyPI, aux versions à jour, et
votre paquet, qui n'existe que sur Test PyPI, sur ce dernier.

```toml
[project]
name = "ghcli-..."

[tool.uv.build-backend]
module-name = ...

[[tool.uv.index]]
name = "testpypi"
url = ...
publish-url = ...
explicit = true
```

</details>

<details>
<summary>Solution</summary>

`pyproject.toml`, ici pour l'utilisateur `octocat`&nbsp;:

```toml
[project]
name = "ghcli-octocat"
...

[tool.uv.build-backend]
module-name = "ghcli"

[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true
```

```console
uv build
uv publish --index testpypi --token <votre jeton>
uvx --index https://pypi.org/simple/ --default-index https://test.pypi.org/simple/ --from ghcli-<votre utilisateur> ghcli --help
```

La page du paquet est `https://test.pypi.org/project/ghcli-<votre utilisateur>/`.

</details>
