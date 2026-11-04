# Interface en ligne de commande pour GitHub Issues

*[English version](https://github.com/shuuchuu/ghcli/tree/main-en)*

Le projet des travaux pratiques *Interface en ligne de commande pour GitHub Issues*.
Leur énoncé est ci-dessous, pour les faire dans un Codespace GitHub ou un clone
local&nbsp;; c'est le même que celui du notebook des travaux pratiques, en
[français](https://colab.research.google.com/github/shuuchuu/labs/blob/main/cli-github-issues-cli-hands-on-fr.ipynb)
ou en
[anglais](https://colab.research.google.com/github/shuuchuu/labs/blob/main/cli-github-issues-cli-hands-on-en.ipynb),
qui les fait dans Colab.

Le but de ces travaux pratiques est de mettre en pratique les principes d'ingénierie vus
durant la formation&nbsp;: nous allons créer `ghcli`, une interface en ligne de commande
qui liste et crée les tickets (*issues*) d'un dépôt GitHub, d'abord avec `argparse`,
puis avec `Typer` et `Rich`. Sa publication sur Test PyPI est un prolongement
facultatif. Le dépôt est un projet `uv` dont le paquet, `src/ghcli/`, est encore vide.

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

Sans compte GitHub, ne créez pas `creds.env`&nbsp;: `ghcli list` marche sur un dépôt
public, sans jeton (l'API accepte alors 60 requêtes par heure et par adresse, que se
partage une salle derrière une même adresse), `ghcli create` non, et les tests de
l'étape « Des tests » toujours.

## La commande `ghcli`

Créez le module `src/ghcli/cli.py`, avec une fonction `main` qui lit deux arguments de
la ligne de commande, le propriétaire d'un dépôt GitHub et son nom, et les affiche.
Déclarez dans `pyproject.toml` la commande `ghcli`, qui lance cette fonction, puis
lancez `uv sync`, qui l'installe dans l'environnement du projet, et essayez-la&nbsp;:
`uv run ghcli shuuchuu ghcli` affiche `shuuchuu ghcli`. Que donnent `uv
run ghcli`, sans argument, et `uv run ghcli --help`&nbsp;?

**Documentation utile**

- https://docs.astral.sh/uv/concepts/projects/config/#entry-points
- https://docs.python.org/fr/3/library/argparse.html#the-add-argument-method

<details>
<summary>Conseils supplémentaires</summary>

Une commande se déclare dans la table `[project.scripts]` de `pyproject.toml`&nbsp;: son
nom, puis le module et la fonction qu'elle appelle, séparés par `:`. Un argument
positionnel est un nom sans tirets&nbsp;: `parser.add_argument("owner", help="...")`.
`parse_args()` renvoie un objet dont chaque argument est un attribut (`args.owner`).
Sans argument, `argparse` affiche l'usage et une erreur&nbsp;; avec `--help`, l'aide
qu'il génère des `help=`.

```python
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="List GitHub issues.")
    parser.add_argument("owner", help="owner of the GitHub repository")
    ...
    args = parser.parse_args()
    print(...)
```

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

import argparse


def main() -> None:
    """Read a GitHub repository from the arguments."""
    parser = argparse.ArgumentParser(description="List GitHub issues.")
    parser.add_argument("owner", help="owner of the GitHub repository")
    parser.add_argument("repo", help="name of the GitHub repository")
    args = parser.parse_args()
    print(args.owner, args.repo)
```

`pyproject.toml`, à la suite de la table `[project]`&nbsp;:

```toml
[project.scripts]
ghcli = "ghcli.cli:main"
```

```console
uv sync
```

```console
uv run ghcli shuuchuu ghcli
uv run ghcli --help
```

</details>

## Le jeton, depuis une variable d'environnement

Créez le module `src/ghcli/api.py`, qui contiendra la logique du logiciel&nbsp;: les
appels à l'API de GitHub. Écrivez-y une fonction `_get_token() -> str` qui renvoie la
valeur de la variable d'environnement `GHCLI_TOKEN`. Quand elle n'est pas définie, ou
qu'elle est vide, la fonction affiche sur la sortie d'erreur ce message, puis arrête le
programme avec le code de retour `1`&nbsp;:

```text
Unable to read the GitHub token from the GHCLI_TOKEN environment variable. Define it and
run the program again.
```

Essayez-la avec une fausse valeur, pour que le vrai jeton n'apparaisse jamais à
l'écran&nbsp;: `GHCLI_TOKEN=essai uv run python -c "from ghcli.api import _get_token;
print(_get_token())"`, puis sans la variable&nbsp;: `env -u GHCLI_TOKEN uv run python -c
"..."`.

**Documentation utile**

- https://docs.python.org/fr/3/library/os.html#os.environ
- https://docs.python.org/fr/3/library/sys.html#sys.exit

<details>
<summary>Conseils supplémentaires</summary>

`os.environ.get("GHCLI_TOKEN")` renvoie la valeur de la variable, ou `None` quand elle
n'est pas définie&nbsp;: `if not token` couvre l'absence et la valeur vide. `print(...,
file=sys.stderr)` écrit sur la sortie d'erreur.

```python
import os
import sys


def _get_token() -> str:
    token = os.environ.get(...)
    if not token:
        print(..., file=sys.stderr)
        sys.exit(...)
    return token
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
    token = os.environ.get("GHCLI_TOKEN")
    if not token:
        print(
            "Unable to read the GitHub token from the GHCLI_TOKEN environment "
            "variable. Define it and run the program again.",
            file=sys.stderr,
        )
        sys.exit(1)
    return token
```

```console
GHCLI_TOKEN=essai uv run python -c "from ghcli.api import _get_token; print(_get_token())"
env -u GHCLI_TOKEN uv run python -c "from ghcli.api import _get_token; print(_get_token())" || echo "(code de retour non nul)"
```

</details>

## Lister les tickets

Ajoutez au projet la bibliothèque [`niquests`](https://niquests.readthedocs.io/), qui a
l'interface de `requests`, en plus moderne (`uv add niquests`). Écrivez dans `api.py`
une fonction `list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]` qui
renvoie les tickets ouverts du dépôt, une liste de n-uplets `(titre, corps, url)`, et
faites afficher à `main` une ligne par ticket, `url - titre - corps`. Pourquoi mettre
cette fonction dans `api.py`, et ne garder dans `cli.py` que la lecture des
arguments&nbsp;?

La fonction demande ces tickets à l'API de GitHub&nbsp;:

```python
response = niquests.get(
    f"https://api.github.com/repos/{owner}/{repo}/issues",
    headers=...,
    timeout=10,
)
```

puis lit la réponse, la liste des tickets en JSON&nbsp;: `response.json()`. Trois points
demandent votre attention&nbsp;:

- Les en-têtes&nbsp;: `Accept` vaut `application/vnd.github+json`&nbsp;; `Authorization`
  vaut `Bearer <jeton>`, seulement si `GHCLI_TOKEN` a une valeur. Sans cet en-tête,
  l'API répond aux lectures d'un dépôt public, alors qu'elle refuse un `Bearer` sans
  jeton.
- Les *pull requests*&nbsp;: pour l'API, ce sont des tickets. `list_issues` ne doit
  renvoyer que les vrais tickets.
- La pagination&nbsp;: l'API répond par pages de 30 éléments. Demandez-en 100, le
  maximum, et ne cherchez pas à aller plus loin.

Essayez&nbsp;: `uv run ghcli shuuchuu ghcli` affiche trois tickets, dont un sans
corps, et pas la *pull request* de ce dépôt&nbsp;:

```text
https://github.com/shuuchuu/ghcli/issues/… - Ticket 3 - Corps / Body
https://github.com/shuuchuu/ghcli/issues/… - Ticket 2 -
https://github.com/shuuchuu/ghcli/issues/… - Ticket 1 - Corps / Body
```

Votre dépôt de test n'a pas encore de ticket&nbsp;: `uv run ghcli <votre utilisateur>
ghcli-sandbox`. Que se passe-t-il pour un dépôt qui n'existe pas&nbsp;?

**Documentation utile**

- https://docs.github.com/en/rest/issues/issues#list-repository-issues
- https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api
- https://niquests.readthedocs.io/en/latest/user/quickstart.html#passing-parameters-in-urls
- https://niquests.readthedocs.io/en/latest/user/quickstart.html#response-status-codes

<details>
<summary>Conseils supplémentaires</summary>

Dans le paquet, `from .api import list_issues` importe la fonction du module voisin.
Chaque ticket est un dictionnaire, dont les clés `title`, `body` et `html_url` (l'URL de
sa page, quand `url` est celle de l'API) donnent ce qu'on veut&nbsp;; `body` vaut `None`
pour un ticket sans corps. Une *pull request* est un élément qui a une clé
`pull_request`. `params={"per_page": "100"}` ajoute `?per_page=100` à l'URL&nbsp;;
au-delà, il faudrait suivre l'en-tête `Link` de la réponse.
`response.raise_for_status()` lève une `niquests.HTTPError` quand l'API répond par une
erreur, `404` pour un dépôt inconnu, `401` pour un jeton invalide. Une fonction
`_headers(token: str | None)` construit les en-têtes avec ou sans jeton, et resservira à
`create_issue`.

`cli.py` ne garde que la lecture des arguments&nbsp;: la logique se teste alors sans
parseur (étape « Des tests »), et ne change pas quand le parseur change (étape « `Typer`
et `Rich` »).

```python
def _headers(token: str | None) -> dict[str, str]:
    headers = {"Accept": ...}
    if token:
        headers["Authorization"] = ...
    return headers


def list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]:
    response = niquests.get(
        ..., params=..., headers=_headers(os.environ.get(...)), timeout=10
    )
    response.raise_for_status()
    return [(issue["title"], ..., ...) for issue in response.json() if ...]
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
    token = os.environ.get("GHCLI_TOKEN")
    if not token:
        print(
            "Unable to read the GitHub token from the GHCLI_TOKEN environment "
            "variable. Define it and run the program again.",
            file=sys.stderr,
        )
        sys.exit(1)
    return token


def _headers(token: str | None) -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    # Without a token, the API still answers reads of public repositories.
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]:
    """List the open issues among the 100 latest of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.

    Returns:
        The title, body and URL of each issue, without the pull requests.
    """
    # https://docs.github.com/en/rest/issues/issues#list-repository-issues
    response = niquests.get(
        f"{API_URL}/repos/{owner}/{repo}/issues",
        params={"per_page": "100"},
        headers=_headers(os.environ.get("GHCLI_TOKEN")),
        timeout=10,
    )
    # An error status (404 for an unknown repository, 401 for a bad token)
    # raises niquests.HTTPError.
    response.raise_for_status()
    # The API counts pull requests as issues, and an issue's body is null when it
    # has none.
    return [
        (issue["title"], issue["body"] or "", issue["html_url"])
        for issue in response.json()
        if "pull_request" not in issue
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
uv run ghcli shuuchuu ghcli
uv run ghcli shuuchuu no-such-repository || echo "(code de retour non nul)"
```

</details>

## Créer un ticket&nbsp;: deux commandes

Ajoutez à `api.py` une fonction `create_issue(owner: str, repo: str, title: str, body:
str) -> tuple[str, str, str]`, qui crée un ticket et renvoie son titre, son corps et son
URL. Elle envoie à l'API le titre et le corps du ticket, en JSON, et a besoin du
jeton&nbsp;:

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

Un dépôt inconnu finit pour l'instant sur une trace Python. Une interface en ligne de
commande répond par un message et un code de sortie, comme vient de le faire
`_get_token`&nbsp;: faites que `main` attrape `niquests.HTTPError`, écrive une ligne sur
la sortie d'erreur et s'arrête avec le code `1`. Essayez avec `uv run ghcli list
shuuchuu no-such-repository`.

**Documentation utile**

- https://docs.github.com/en/rest/issues/issues#create-an-issue
- https://docs.python.org/fr/3/library/argparse.html#subcommands

<details>
<summary>Conseils supplémentaires</summary>

`parser.add_subparsers(dest="command", required=True)` renvoie un objet dont
`add_parser("list")` crée le parseur de la sous-commande&nbsp;; `args.command` dit
laquelle a été lancée. Les deux sous-commandes ont `owner` et `repo` en commun&nbsp;:
une boucle les leur ajoute. L'API répond `201 Created` avec le ticket créé, au même
format qu'un ticket de la liste. `headers=_headers(_get_token())` exige le jeton&nbsp;:
sans lui, `create` s'arrête sur le message de `_get_token`.

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
try:
    if args.command == "list":
        ...
    elif args.command == "create":
        ...
except niquests.HTTPError as error:
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

import niquests

API_URL = "https://api.github.com"


def _get_token() -> str:
    token = os.environ.get("GHCLI_TOKEN")
    if not token:
        print(
            "Unable to read the GitHub token from the GHCLI_TOKEN environment "
            "variable. Define it and run the program again.",
            file=sys.stderr,
        )
        sys.exit(1)
    return token


def _headers(token: str | None) -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    # Without a token, the API still answers reads of public repositories.
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]:
    """List the open issues among the 100 latest of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.

    Returns:
        The title, body and URL of each issue, without the pull requests.
    """
    # https://docs.github.com/en/rest/issues/issues#list-repository-issues
    response = niquests.get(
        f"{API_URL}/repos/{owner}/{repo}/issues",
        params={"per_page": "100"},
        headers=_headers(os.environ.get("GHCLI_TOKEN")),
        timeout=10,
    )
    # An error status (404 for an unknown repository, 401 for a bad token)
    # raises niquests.HTTPError.
    response.raise_for_status()
    # The API counts pull requests as issues, and an issue's body is null when it
    # has none.
    return [
        (issue["title"], issue["body"] or "", issue["html_url"])
        for issue in response.json()
        if "pull_request" not in issue
    ]


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
        headers=_headers(_get_token()),
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
import sys

import niquests

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
    try:
        if args.command == "list":
            for title, body, url in list_issues(args.owner, args.repo):
                print(f"{url} - {title} - {body}")
        elif args.command == "create":
            title, body, url = create_issue(
                args.owner, args.repo, args.title, args.body
            )
            print(f"{url} - {title} - {body}")
    except niquests.HTTPError as error:
        print(f"GitHub API error: {error}", file=sys.stderr)
        sys.exit(1)
```

```console
uv run ghcli list shuuchuu no-such-repository || echo "(code de retour non nul)"
uv run ghcli create <votre utilisateur> ghcli-sandbox "Premier ticket" "Créé par ghcli"
uv run ghcli list <votre utilisateur> ghcli-sandbox
```

</details>

## Une classe pour les tickets

Des n-uplets représentent pour l'instant les tickets&nbsp;: il est facile d'en confondre
l'ordre, et d'introduire ainsi des bugs. Créez dans un module `src/ghcli/model.py` une
classe `Issue`, avec le module `dataclasses`, dont les attributs sont le titre, le corps
et l'URL d'un ticket, et une méthode de classe `from_dict` qui construit un `Issue` à
partir d'un ticket de l'API. `list_issues` renvoie alors une `list[Issue]`,
`create_issue` un `Issue`&nbsp;: adaptez-les, ainsi que `cli.py`.

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
    token = os.environ.get("GHCLI_TOKEN")
    if not token:
        print(
            "Unable to read the GitHub token from the GHCLI_TOKEN environment "
            "variable. Define it and run the program again.",
            file=sys.stderr,
        )
        sys.exit(1)
    return token


def _headers(token: str | None) -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    # Without a token, the API still answers reads of public repositories.
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def list_issues(owner: str, repo: str) -> list[Issue]:
    """List the open issues among the 100 latest of a GitHub repository.

    Args:
        owner: The repository's owner.
        repo: The repository's name.

    Returns:
        Its issues, without its pull requests.
    """
    # https://docs.github.com/en/rest/issues/issues#list-repository-issues
    response = niquests.get(
        f"{API_URL}/repos/{owner}/{repo}/issues",
        params={"per_page": "100"},
        headers=_headers(os.environ.get("GHCLI_TOKEN")),
        timeout=10,
    )
    # An error status (404 for an unknown repository, 401 for a bad token)
    # raises niquests.HTTPError.
    response.raise_for_status()
    # The API counts pull requests as issues.
    return [
        Issue.from_dict(issue)
        for issue in response.json()
        if "pull_request" not in issue
    ]


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
        headers=_headers(_get_token()),
        timeout=10,
    )
    response.raise_for_status()
    return Issue.from_dict(response.json())
```

`src/ghcli/cli.py`&nbsp;:

```python
"""Command-line interface to GitHub issues."""

import argparse
import sys

import niquests

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
    try:
        if args.command == "list":
            for issue in list_issues(args.owner, args.repo):
                _show(issue)
        elif args.command == "create":
            _show(create_issue(args.owner, args.repo, args.title, args.body))
    except niquests.HTTPError as error:
        print(f"GitHub API error: {error}", file=sys.stderr)
        sys.exit(1)
```

```console
uv run ghcli list shuuchuu ghcli
```

</details>

## Des tests

Écrivez dans `tests/test_api.py` des tests de `_get_token`, `list_issues`,
`create_issue` et `main`, et lancez-les avec `uv run pytest`. Ils ne doivent dépendre ni
du réseau, ni de votre jeton&nbsp;: remplacez `niquests.get` et `niquests.post` par des
fonctions qui renvoient une fausse réponse, et la variable d'environnement par une
valeur de test. Vérifiez aussi les cas limites et les cas d'erreur&nbsp;: une variable
absente ou vide, une liste sans jeton, une *pull request* à écarter, un dépôt inconnu,
pour lequel `main` écrit sur la sortie d'erreur et sort avec le code `1`.

Terminez par les outils que le dépôt configure strictement dans `pyproject.toml`&nbsp;:
`uv run ruff check`, `uv run ruff format --check` et `uv run pyrefly check` doivent
passer.

**Documentation utile**

- https://docs.pytest.org/en/stable/how-to/monkeypatch.html
- https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions
- https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html#accessing-captured-output-from-a-test-function

<details>
<summary>Conseils supplémentaires</summary>

La fixture `monkeypatch` de `pytest` remplace un attribut le temps d'un test
(`monkeypatch.setattr(niquests, "get", fake_get)`) et définit ou retire une variable
d'environnement (`setenv`, `delenv`). Une fausse réponse n'a besoin que des méthodes
qu'appelle le code&nbsp;: `raise_for_status` et `json`. Une fixture `autouse=True`
s'applique à tous les tests du module. `main` lit `sys.argv`, que `monkeypatch` remplace
aussi&nbsp;; la fixture `capsys` donne ce que le code a écrit sur la sortie d'erreur.

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


def test_main_reports_an_api_error(monkeypatch, capsys):
    monkeypatch.setattr(niquests, "get", ...)
    monkeypatch.setattr(sys, "argv", ["ghcli", "list", "octocat", "unknown"])
    with pytest.raises(SystemExit) as exit_info:
        main()
    assert exit_info.value.code == ...
    assert "404" in capsys.readouterr().err
```

</details>

<details>
<summary>Solution</summary>

`tests/test_api.py`&nbsp;:

```python
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
```

```console
uv run pytest
uv run ruff check
uv run ruff format --check
uv run pyrefly check
```

</details>

## `Typer` et `Rich`

`argparse` a fait son travail, au prix de nombreuses lignes qui ne font que déclarer des
arguments. Ajoutez au projet `typer` et `rich` (`uv add typer rich`), et réécrivez
`cli.py` avec `typer.Typer()` et `@app.command()`, vus en cours&nbsp;:

- Les commandes restent `ghcli list <propriétaire> <dépôt>` et `ghcli create
  <propriétaire> <dépôt> <titre> <corps>`, et chaque argument garde son aide.
- `list` affiche les tickets dans une `rich.table.Table`, avec leur URL entière.
- `main` reste le point d'entrée de `pyproject.toml`, et attrape toujours les erreurs de
  l'API.

Regardez `uv run ghcli --help`, puis `uv run ghcli list shuuchuu ghcli`. Que
devient `_create_parser`&nbsp;? Que reste-t-il à changer dans `api.py`&nbsp;? Et dans
les tests, qui doivent passer sans qu'on y touche&nbsp;?

**Documentation utile**

- https://typer.tiangolo.com/tutorial/commands/name/
- https://rich.readthedocs.io/en/stable/console.html

<details>
<summary>Conseils supplémentaires</summary>

`_create_parser` disparaît&nbsp;: les annotations des fonctions déclarent les arguments.
Rien ne change dans `api.py`, et les tests passent tels quels&nbsp;: c'est ce que
rapporte la séparation entre `cli.py` et `api.py`. `@app.command("list")` nomme la
commande, ce qui évite d'appeler une fonction `list` comme la fonction native. Un alias
`Annotated[str, typer.Argument(help=...)]` sert aux deux commandes, et la docstring
d'une commande devient son aide. `add_column("URL", no_wrap=True)` garde une colonne sur
une ligne&nbsp;: une URL coupée ne mène plus nulle part.
`Console(markup=False).print(...)` affiche le tableau, sans prendre les crochets d'un
titre de ticket pour un style. `app()` lance la commande&nbsp;: `main` l'entoure de son
`try`.

```python
app = typer.Typer(help=...)
console = Console(markup=False)

Proprietaire = Annotated[str, typer.Argument(help=...)]
...


@app.command("list")
def lister(owner: Proprietaire, repo: ...) -> None:
    """Liste les tickets ouverts d'un dépôt."""
    tableau = Table("Titre", "Corps")
    tableau.add_column("URL", no_wrap=True)
    for issue in list_issues(owner, repo):
        tableau.add_row(...)
    console.print(tableau)


def main() -> None:
    try:
        app()
    except niquests.HTTPError as error:
        ...
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/cli.py`&nbsp;:

```python
"""Command-line interface to GitHub issues."""

import sys
from typing import Annotated

import niquests
import typer
from rich.console import Console
from rich.table import Table

from .api import create_issue, list_issues

app = typer.Typer(help="Liste et crée les tickets d'un dépôt GitHub.")
# Sans balises : le titre d'un ticket peut contenir des crochets.
console = Console(markup=False)

Proprietaire = Annotated[str, typer.Argument(help="Propriétaire du dépôt GitHub.")]
Depot = Annotated[str, typer.Argument(help="Nom du dépôt GitHub.")]


@app.command("list")
def lister(owner: Proprietaire, repo: Depot) -> None:
    """Liste les tickets ouverts d'un dépôt."""
    tableau = Table("Titre", "Corps")
    # Sans retour à la ligne : une URL coupée ne mène plus nulle part.
    tableau.add_column("URL", no_wrap=True)
    for issue in list_issues(owner, repo):
        tableau.add_row(issue.title, issue.body, issue.url)
    console.print(tableau)


@app.command("create")
def creer(
    owner: Proprietaire,
    repo: Depot,
    title: Annotated[str, typer.Argument(help="Titre du ticket.")],
    body: Annotated[str, typer.Argument(help="Corps du ticket.")],
) -> None:
    """Crée un ticket."""
    issue = create_issue(owner, repo, title, body)
    console.print(f"{issue.url} - {issue.title} - {issue.body}")


def main() -> None:
    """Run the command the arguments name."""
    try:
        app()
    except niquests.HTTPError as error:
        print(f"GitHub API error: {error}", file=sys.stderr)
        sys.exit(1)
```

```console
uv add typer rich
uv run ghcli --help
uv run ghcli list shuuchuu ghcli
uv run ghcli list shuuchuu no-such-repository || echo "(code de retour non nul)"
uv run pytest
uv run ruff check
uv run ruff format --check
uv run pyrefly check
```

</details>

## Prolongement facultatif&nbsp;: publier sur Test PyPI

Ce prolongement reprend sur `ghcli` la publication du TP sur les paquets, avec le compte
Test PyPI et le jeton de ce TP&nbsp;: sans eux, arrêtez-vous ici.

1. Le nom `ghcli` ne peut être publié qu'une fois&nbsp;: dans `pyproject.toml`, renommez
   le projet `ghcli-<votre utilisateur GitHub>`, en minuscules, sans changer le nom du
   paquet qu'on importe, `ghcli`, et mettez-vous dans `authors`, qui part avec le
   paquet.
2. Déclarez dans `pyproject.toml` l'index `testpypi`, son URL et celle où l'on publie.
3. Construisez le paquet avec `uv build`, puis publiez-le avec `uv publish --index
   testpypi --token <votre jeton>`.
4. Trouvez sa page sur Test PyPI, puis installez-le et lancez-le, sans le dépôt&nbsp;:
   `uvx --index https://pypi.org/simple/ --default-index https://test.pypi.org/simple/
   --from ghcli-<votre utilisateur> ghcli --help`.

**Documentation utile**

- https://docs.astral.sh/uv/concepts/build-backend/#modules
- https://docs.astral.sh/uv/guides/integration/alternative-indexes/
- https://docs.astral.sh/uv/guides/package/#publishing-your-package

<details>
<summary>Conseils supplémentaires</summary>

Le module que construit `uv build` porte par défaut le nom du projet&nbsp;:
`module-name`, dans `[tool.uv.build-backend]`, le fixe. Un index se déclare dans une
table `[[tool.uv.index]]`&nbsp;: `name`, `url`, `publish-url`, et `explicit = true`,
pour que `uv` n'y cherche que les paquets qu'on lui attribue. L'URL de Test PyPI est
`https://test.pypi.org/simple/`, celle où l'on publie `https://test.pypi.org/legacy/`.
Pour `uvx`, PyPI passe avant Test PyPI&nbsp;: `uv` prend chaque paquet sur le premier
index qui l'a, donc `niquests` et ses dépendances sur PyPI, aux versions à jour, et
votre paquet, qui n'existe que sur Test PyPI, sur ce dernier.

```toml
[project]
authors = [...]
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
authors = [
  {name = "octocat"},
]
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
rm -rf dist
uv build
uv publish --index testpypi --token <votre jeton>
uvx --index https://pypi.org/simple/ --default-index https://test.pypi.org/simple/ --from ghcli-<votre utilisateur> ghcli --help
```

La page du paquet est `https://test.pypi.org/project/ghcli-<votre utilisateur>/`.

</details>
