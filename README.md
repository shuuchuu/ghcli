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

Une commande se déclare dans la table `[project.scripts]` de `pyproject.toml`&nbsp;: son nom,
puis le module et la fonction qu'elle appelle, séparés par `:`. Un argument positionnel
est un nom sans tirets&nbsp;: `parseur.add_argument("proprietaire", help="...")`.
`parse_args()` renvoie un objet dont chaque argument est un attribut
(`args.proprietaire`). Sans argument, `argparse` affiche l'usage et une erreur&nbsp;; avec
`--help`, l'aide qu'il génère des `help=`.

```python
import argparse


def main() -> None:
    parseur = argparse.ArgumentParser(description="Liste les tickets GitHub.")
    parseur.add_argument("proprietaire", help="propriétaire du dépôt GitHub")
    ...
    args = parseur.parse_args()
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
"""Interface en ligne de commande pour les tickets GitHub."""

import argparse


def main() -> None:
    """Lit un dépôt GitHub dans les arguments."""
    parseur = argparse.ArgumentParser(description="Liste les tickets GitHub.")
    parseur.add_argument("proprietaire", help="propriétaire du dépôt GitHub")
    parseur.add_argument("depot", help="nom du dépôt GitHub")
    args = parseur.parse_args()
    print(args.proprietaire, args.depot)
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
appels à l'API de GitHub. Écrivez-y une fonction `_lit_jeton() -> str` qui renvoie la
valeur de la variable d'environnement `GHCLI_TOKEN`. Quand elle n'est pas définie, ou
qu'elle est vide, la fonction affiche sur la sortie d'erreur ce message, puis arrête le
programme avec le code de retour `1`&nbsp;:

```text
Impossible de lire le jeton GitHub dans la variable d'environnement GHCLI_TOKEN.
Définissez-la et relancez le programme.
```

Essayez-la avec une fausse valeur, pour que le vrai jeton n'apparaisse jamais à
l'écran&nbsp;: `GHCLI_TOKEN=essai uv run python -c "from ghcli.api import _lit_jeton;
print(_lit_jeton())"`, puis sans la variable&nbsp;: `env -u GHCLI_TOKEN uv run python -c
"..."`.

**Documentation utile**

- https://docs.python.org/fr/3/library/os.html#os.environ
- https://docs.python.org/fr/3/library/sys.html#sys.exit

<details>
<summary>Conseils supplémentaires</summary>

`os.environ.get("GHCLI_TOKEN")` renvoie la valeur de la variable, ou `None` quand elle
n'est pas définie&nbsp;: `if not jeton` couvre l'absence et la valeur vide. `print(...,
file=sys.stderr)` écrit sur la sortie d'erreur.

```python
import os
import sys


def _lit_jeton() -> str:
    jeton = os.environ.get(...)
    if not jeton:
        print(..., file=sys.stderr)
        sys.exit(...)
    return jeton
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/api.py`&nbsp;:

```python
"""Appels à l'API de GitHub."""

import os
import sys


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
```

```console
GHCLI_TOKEN=essai uv run python -c "from ghcli.api import _lit_jeton; print(_lit_jeton())"
env -u GHCLI_TOKEN uv run python -c "from ghcli.api import _lit_jeton; print(_lit_jeton())" || echo "(code de retour non nul)"
```

</details>

## Lister les tickets

Ajoutez au projet la bibliothèque [`niquests`](https://niquests.readthedocs.io/), qui a
l'interface de `requests`, en plus moderne (`uv add niquests`). Écrivez dans `api.py`
une fonction `liste_tickets(proprietaire: str, depot: str) -> list[tuple[str, str,
str]]` qui renvoie les tickets ouverts du dépôt, une liste de n-uplets `(titre, corps,
url)`, et faites afficher à `main` une ligne par ticket, `url - titre - corps`. Pourquoi
mettre cette fonction dans `api.py`, et ne garder dans `cli.py` que la lecture des
arguments&nbsp;?

La fonction demande ces tickets à l'API de GitHub&nbsp;:

```python
reponse = niquests.get(
    f"https://api.github.com/repos/{proprietaire}/{depot}/issues",
    headers=...,
    timeout=10,
)
```

puis lit la réponse, la liste des tickets en JSON&nbsp;: `reponse.json()`. Trois points
demandent votre attention&nbsp;:

- Les en-têtes&nbsp;: `Accept` vaut `application/vnd.github+json`&nbsp;; `Authorization`
  vaut `Bearer <jeton>`, seulement si `GHCLI_TOKEN` a une valeur. Sans cet en-tête,
  l'API répond aux lectures d'un dépôt public, alors qu'elle refuse un `Bearer` sans
  jeton.
- Les *pull requests*&nbsp;: pour l'API, ce sont des tickets. `liste_tickets` ne doit
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

Dans le paquet, `from .api import liste_tickets` importe la fonction du module voisin.
Chaque ticket est un dictionnaire, dont les clés `title`, `body` et `html_url` (l'URL de
sa page, quand `url` est celle de l'API) donnent ce qu'on veut&nbsp;; `body` vaut `None`
pour un ticket sans corps. Une *pull request* est un élément qui a une clé
`pull_request`. `params={"per_page": "100"}` ajoute `?per_page=100` à l'URL&nbsp;;
au-delà, il faudrait suivre l'en-tête `Link` de la réponse.
`reponse.raise_for_status()` lève une `niquests.HTTPError` quand l'API répond par une
erreur, `404` pour un dépôt inconnu, `401` pour un jeton invalide. Une fonction
`_entetes(jeton: str | None)` construit les en-têtes avec ou sans jeton, et resservira à
`cree_ticket`.

`cli.py` ne garde que la lecture des arguments&nbsp;: la logique se teste alors sans
parseur (étape « Des tests »), et ne change pas quand le parseur change (étape « `Typer`
et `Rich` »).

```python
def _entetes(jeton: str | None) -> dict[str, str]:
    entetes = {"Accept": ...}
    if jeton:
        entetes["Authorization"] = ...
    return entetes


def liste_tickets(proprietaire: str, depot: str) -> list[tuple[str, str, str]]:
    reponse = niquests.get(
        ..., params=..., headers=_entetes(os.environ.get(...)), timeout=10
    )
    reponse.raise_for_status()
    return [(ticket["title"], ..., ...) for ticket in reponse.json() if ...]
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/api.py`&nbsp;:

```python
"""Appels à l'API de GitHub."""

import os
import sys

import niquests

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


def liste_tickets(proprietaire: str, depot: str) -> list[tuple[str, str, str]]:
    """Liste les tickets ouverts parmi les 100 derniers d'un dépôt GitHub.

    Args:
        proprietaire: Le propriétaire du dépôt.
        depot: Le nom du dépôt.

    Returns:
        Le titre, le corps et l'URL de chaque ticket, sans les pull requests.
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
    # L'API compte les pull requests parmi les tickets, et le corps d'un ticket vaut
    # null quand il n'en a pas.
    return [
        (ticket["title"], ticket["body"] or "", ticket["html_url"])
        for ticket in reponse.json()
        if "pull_request" not in ticket
    ]
```

`src/ghcli/cli.py`&nbsp;:

```python
"""Interface en ligne de commande pour les tickets GitHub."""

import argparse

from .api import liste_tickets


def main() -> None:
    """Liste les tickets du dépôt GitHub que nomment les arguments."""
    parseur = argparse.ArgumentParser(description="Liste les tickets GitHub.")
    parseur.add_argument("proprietaire", help="propriétaire du dépôt GitHub")
    parseur.add_argument("depot", help="nom du dépôt GitHub")
    args = parseur.parse_args()
    for titre, corps, url in liste_tickets(args.proprietaire, args.depot):
        print(f"{url} - {titre} - {corps}")
```

```console
uv add niquests
uv run ghcli shuuchuu ghcli
uv run ghcli shuuchuu depot-inexistant || echo "(code de retour non nul)"
```

</details>

## Créer un ticket&nbsp;: deux commandes

Ajoutez à `api.py` une fonction `cree_ticket(proprietaire: str, depot: str, titre: str,
corps: str) -> tuple[str, str, str]`, qui crée un ticket et renvoie son titre, son corps
et son URL. Elle envoie à l'API le titre et le corps du ticket, en JSON, et a besoin du
jeton&nbsp;:

```python
reponse = niquests.post(
    f"https://api.github.com/repos/{proprietaire}/{depot}/issues",
    json={"title": titre, "body": corps},
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
`_lit_jeton`&nbsp;: faites que `main` attrape `niquests.HTTPError`, écrive une ligne sur
la sortie d'erreur et s'arrête avec le code `1`. Essayez avec `uv run ghcli list
shuuchuu depot-inexistant`.

**Documentation utile**

- https://docs.github.com/en/rest/issues/issues#create-an-issue
- https://docs.python.org/fr/3/library/argparse.html#subcommands

<details>
<summary>Conseils supplémentaires</summary>

`parseur.add_subparsers(dest="commande", required=True)` renvoie un objet dont
`add_parser("list")` crée le parseur de la sous-commande&nbsp;; `args.commande` dit
laquelle a été lancée. Les deux sous-commandes ont `proprietaire` et `depot` en commun&nbsp;:
une boucle les leur ajoute. L'API répond `201 Created` avec le ticket créé, au même
format qu'un ticket de la liste. `headers=_entetes(_lit_jeton())` exige le jeton&nbsp;:
sans lui, `create` s'arrête sur le message de `_lit_jeton`.

```python
sous_parseurs = parseur.add_subparsers(dest="commande", required=True)
parseur_liste = sous_parseurs.add_parser("list", help="liste les tickets d'un dépôt")
parseur_creation = sous_parseurs.add_parser("create", help="crée un ticket")
for sous_parseur in (parseur_liste, parseur_creation):
    sous_parseur.add_argument("proprietaire", help="propriétaire du dépôt GitHub")
    ...
parseur_creation.add_argument("titre", help="titre du ticket")
...
args = parseur.parse_args()
try:
    if args.commande == "list":
        ...
    elif args.commande == "create":
        ...
except niquests.HTTPError as erreur:
    print(..., file=sys.stderr)
    sys.exit(...)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/api.py`&nbsp;:

```python
"""Appels à l'API de GitHub."""

import os
import sys

import niquests

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


def liste_tickets(proprietaire: str, depot: str) -> list[tuple[str, str, str]]:
    """Liste les tickets ouverts parmi les 100 derniers d'un dépôt GitHub.

    Args:
        proprietaire: Le propriétaire du dépôt.
        depot: Le nom du dépôt.

    Returns:
        Le titre, le corps et l'URL de chaque ticket, sans les pull requests.
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
    # L'API compte les pull requests parmi les tickets, et le corps d'un ticket vaut
    # null quand il n'en a pas.
    return [
        (ticket["title"], ticket["body"] or "", ticket["html_url"])
        for ticket in reponse.json()
        if "pull_request" not in ticket
    ]


def cree_ticket(
    proprietaire: str, depot: str, titre: str, corps: str
) -> tuple[str, str, str]:
    """Crée un ticket dans un dépôt GitHub.

    Args:
        proprietaire: Le propriétaire du dépôt.
        depot: Le nom du dépôt.
        titre: Le titre du ticket.
        corps: Le corps du ticket.

    Returns:
        Le titre, le corps et l'URL du ticket créé.
    """
    # https://docs.github.com/en/rest/issues/issues#create-an-issue
    reponse = niquests.post(
        f"{URL_API}/repos/{proprietaire}/{depot}/issues",
        json={"title": titre, "body": corps},
        headers=_entetes(_lit_jeton()),
        timeout=10,
    )
    reponse.raise_for_status()
    ticket = reponse.json()
    return ticket["title"], ticket["body"] or "", ticket["html_url"]
```

`src/ghcli/cli.py`&nbsp;:

```python
"""Interface en ligne de commande pour les tickets GitHub."""

import argparse
import sys

import niquests

from .api import cree_ticket, liste_tickets


def _cree_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(description="Liste et crée les tickets GitHub.")
    sous_parseurs = parseur.add_subparsers(dest="commande", required=True)
    parseur_liste = sous_parseurs.add_parser(
        "list", help="liste les tickets d'un dépôt"
    )
    parseur_creation = sous_parseurs.add_parser("create", help="crée un ticket")
    for sous_parseur in (parseur_liste, parseur_creation):
        sous_parseur.add_argument("proprietaire", help="propriétaire du dépôt GitHub")
        sous_parseur.add_argument("depot", help="nom du dépôt GitHub")
    parseur_creation.add_argument("titre", help="titre du ticket")
    parseur_creation.add_argument("corps", help="corps du ticket")
    return parseur


def main() -> None:
    """Exécute la commande que nomment les arguments."""
    args = _cree_parseur().parse_args()
    try:
        if args.commande == "list":
            for titre, corps, url in liste_tickets(args.proprietaire, args.depot):
                print(f"{url} - {titre} - {corps}")
        elif args.commande == "create":
            titre, corps, url = cree_ticket(
                args.proprietaire, args.depot, args.titre, args.corps
            )
            print(f"{url} - {titre} - {corps}")
    except niquests.HTTPError as erreur:
        print(f"Erreur de l'API GitHub : {erreur}", file=sys.stderr)
        sys.exit(1)
```

```console
uv run ghcli list shuuchuu depot-inexistant || echo "(code de retour non nul)"
uv run ghcli create <votre utilisateur> ghcli-sandbox "Premier ticket" "Créé par ghcli"
uv run ghcli list <votre utilisateur> ghcli-sandbox
```

</details>

## Une classe pour les tickets

Des n-uplets représentent pour l'instant les tickets&nbsp;: il est facile d'en confondre
l'ordre, et d'introduire ainsi des bugs. Créez dans un module `src/ghcli/modele.py` une
classe `Ticket`, avec le module `dataclasses`, dont les attributs sont le titre, le
corps et l'URL d'un ticket, et une méthode de classe `depuis_dict` qui construit un
`Ticket` à partir d'un ticket de l'API. `liste_tickets` renvoie alors une
`list[Ticket]`, `cree_ticket` un `Ticket`&nbsp;: adaptez-les, ainsi que `cli.py`.

**Documentation utile**

- https://docs.python.org/fr/3/library/dataclasses.html
- https://docs.python.org/fr/3/library/functions.html#classmethod

<details>
<summary>Conseils supplémentaires</summary>

`@dataclass` génère le constructeur, la représentation et la comparaison à partir des
attributs annotés. Une méthode de classe reçoit la classe (`cls`) au lieu d'une
instance&nbsp;: c'est un autre constructeur, `Ticket.depuis_dict(ticket)`.

```python
from dataclasses import dataclass
from typing import Any, Self


@dataclass
class Ticket:
    titre: str
    ...

    @classmethod
    def depuis_dict(cls, donnees: dict[str, Any]) -> Self:
        return cls(titre=donnees["title"], corps=..., url=...)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/modele.py`&nbsp;:

```python
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
```

`src/ghcli/api.py`&nbsp;:

```python
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
```

`src/ghcli/cli.py`&nbsp;:

```python
"""Interface en ligne de commande pour les tickets GitHub."""

import argparse
import sys

import niquests

from .api import cree_ticket, liste_tickets
from .modele import Ticket


def _cree_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(description="Liste et crée les tickets GitHub.")
    sous_parseurs = parseur.add_subparsers(dest="commande", required=True)
    parseur_liste = sous_parseurs.add_parser(
        "list", help="liste les tickets d'un dépôt"
    )
    parseur_creation = sous_parseurs.add_parser("create", help="crée un ticket")
    for sous_parseur in (parseur_liste, parseur_creation):
        sous_parseur.add_argument("proprietaire", help="propriétaire du dépôt GitHub")
        sous_parseur.add_argument("depot", help="nom du dépôt GitHub")
    parseur_creation.add_argument("titre", help="titre du ticket")
    parseur_creation.add_argument("corps", help="corps du ticket")
    return parseur


def _affiche(ticket: Ticket) -> None:
    print(f"{ticket.url} - {ticket.titre} - {ticket.corps}")


def main() -> None:
    """Exécute la commande que nomment les arguments."""
    args = _cree_parseur().parse_args()
    try:
        if args.commande == "list":
            for ticket in liste_tickets(args.proprietaire, args.depot):
                _affiche(ticket)
        elif args.commande == "create":
            _affiche(cree_ticket(args.proprietaire, args.depot, args.titre, args.corps))
    except niquests.HTTPError as erreur:
        print(f"Erreur de l'API GitHub : {erreur}", file=sys.stderr)
        sys.exit(1)
```

```console
uv run ghcli list shuuchuu ghcli
```

</details>

## Des tests

Écrivez dans `tests/test_api.py` des tests de `_lit_jeton`, `liste_tickets`,
`cree_ticket` et `main`, et lancez-les avec `uv run pytest`. Ils ne doivent dépendre ni
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
(`monkeypatch.setattr(niquests, "get", fausse_lecture)`) et définit ou retire une
variable d'environnement (`setenv`, `delenv`). Une fausse réponse n'a besoin que des
méthodes qu'appelle le code&nbsp;: `raise_for_status` et `json`. Une fixture `autouse=True`
s'applique à tous les tests du module. `main` lit `sys.argv`, que `monkeypatch` remplace
aussi&nbsp;; la fixture `capsys` donne ce que le code a écrit sur la sortie d'erreur.

```python
class FausseReponse:
    def __init__(self, donnees, statut=200):
        self.donnees = donnees
        ...

    def raise_for_status(self):
        if self.statut >= 400:
            raise niquests.HTTPError(self.statut)

    def json(self):
        return self.donnees


def test_liste_tickets(monkeypatch):
    monkeypatch.setenv("GHCLI_TOKEN", "un-jeton")
    monkeypatch.setattr(niquests, "get", lambda url, **kwargs: FausseReponse([...]))
    assert liste_tickets("octocat", "sandbox") == [...]


def test_main_signale_une_erreur_de_l_api(monkeypatch, capsys):
    monkeypatch.setattr(niquests, "get", ...)
    monkeypatch.setattr(sys, "argv", ["ghcli", "list", "octocat", "inconnu"])
    with pytest.raises(SystemExit) as info_sortie:
        main()
    assert info_sortie.value.code == ...
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
devient `_cree_parseur`&nbsp;? Que reste-t-il à changer dans `api.py`&nbsp;? Et dans
les tests, qui doivent passer sans qu'on y touche&nbsp;?

**Documentation utile**

- https://typer.tiangolo.com/tutorial/commands/name/
- https://rich.readthedocs.io/en/stable/console.html

<details>
<summary>Conseils supplémentaires</summary>

`_cree_parseur` disparaît&nbsp;: les annotations des fonctions déclarent les arguments.
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
def lister(proprietaire: Proprietaire, depot: ...) -> None:
    """Liste les tickets ouverts d'un dépôt."""
    tableau = Table("Titre", "Corps")
    tableau.add_column("URL", no_wrap=True)
    for ticket in liste_tickets(proprietaire, depot):
        tableau.add_row(...)
    console.print(tableau)


def main() -> None:
    try:
        app()
    except niquests.HTTPError as erreur:
        ...
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/cli.py`&nbsp;:

```python
"""Interface en ligne de commande pour les tickets GitHub."""

import sys
from typing import Annotated

import niquests
import typer
from rich.console import Console
from rich.table import Table

from .api import cree_ticket, liste_tickets

app = typer.Typer(help="Liste et crée les tickets d'un dépôt GitHub.")
# Sans balises : le titre d'un ticket peut contenir des crochets.
console = Console(markup=False)

Proprietaire = Annotated[str, typer.Argument(help="Propriétaire du dépôt GitHub.")]
Depot = Annotated[str, typer.Argument(help="Nom du dépôt GitHub.")]


@app.command("list")
def lister(proprietaire: Proprietaire, depot: Depot) -> None:
    """Liste les tickets ouverts d'un dépôt."""
    tableau = Table("Titre", "Corps")
    # Sans retour à la ligne : une URL coupée ne mène plus nulle part.
    tableau.add_column("URL", no_wrap=True)
    for ticket in liste_tickets(proprietaire, depot):
        tableau.add_row(ticket.titre, ticket.corps, ticket.url)
    console.print(tableau)


@app.command("create")
def creer(
    proprietaire: Proprietaire,
    depot: Depot,
    titre: Annotated[str, typer.Argument(help="Titre du ticket.")],
    corps: Annotated[str, typer.Argument(help="Corps du ticket.")],
) -> None:
    """Crée un ticket."""
    ticket = cree_ticket(proprietaire, depot, titre, corps)
    console.print(f"{ticket.url} - {ticket.titre} - {ticket.corps}")


def main() -> None:
    """Exécute la commande que nomment les arguments."""
    try:
        app()
    except niquests.HTTPError as erreur:
        print(f"Erreur de l'API GitHub : {erreur}", file=sys.stderr)
        sys.exit(1)
```

```console
uv add typer rich
uv run ghcli --help
uv run ghcli list shuuchuu ghcli
uv run ghcli list shuuchuu depot-inexistant || echo "(code de retour non nul)"
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
