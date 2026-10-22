# Tableau de bord Shiny pour GitHub Issues

*[English version](https://github.com/shuuchuu/ghcli/tree/shiny-en)*

Le projet des travaux pratiques *Tableau de bord Shiny pour GitHub Issues*. Ils partent
de la solution des travaux pratiques [*Interface en ligne de commande pour GitHub
Issues*](https://github.com/shuuchuu/ghcli)&nbsp;: `ghcli list` et `ghcli create`
listent et créent les tickets d'un dépôt, et sont testés. Nous allons leur ajouter un
tableau de bord web, avec Shiny&nbsp;: le nombre de tickets ouverts chaque jour, en
diagramme en barres. Leur énoncé est ci-dessous, pour les faire dans un Codespace
GitHub ou un clone local (Colab n'affiche pas le serveur web qu'ouvre Shiny).

Le projet contient pour cela&nbsp;:

- `src/ghcli/gui.py`, l'application à compléter&nbsp;: `app_ui` en décrit
  l'interface (deux zones de texte, `owner` et `repo`, un bouton, `fetch`, et deux
  sorties, `count` et `plot`), `server` en calculera les sorties, `create_gui` la sert,
  et `_figure_html` transforme une figure Plotly en HTML qu'affiche une sortie&nbsp;;
- dans `src/ghcli/model.py`, la date de création de chaque ticket,
  `Issue.created_at`&nbsp;;
- la commande `ghcli gui`, qui lance l'application.

## Mise en place de l'environnement de travail

Ouvrez le dépôt dans un Codespace, sur sa branche `shiny`&nbsp;: sur GitHub, sur la
branche `shiny`, **Code** > **Codespaces** > **Create codespace on shiny**, ou [ce
lien](https://codespaces.new/shuuchuu/ghcli/tree/shiny). Le Codespace installe les
dépendances à sa création, dans le `.venv` du projet.

Dans un clone local de cette branche (`git clone -b shiny
https://github.com/shuuchuu/ghcli.git`), installez
[uv](https://docs.astral.sh/uv/getting-started/installation/), puis lancez `uv sync` à
la racine du dépôt.

`ghcli` a besoin d'un jeton GitHub&nbsp;: si vous n'en avez pas, créez un dépôt de test
et un jeton comme l'explique [l'énoncé de l'interface en ligne de
commande](https://github.com/shuuchuu/ghcli#un-dépôt-de-test-et-un-jeton-github), et
mettez-le dans un fichier `creds.env` à la racine du dépôt. Les commandes se lancent
dans un terminal à la racine du dépôt (**Terminal** > **Nouveau terminal** dans le
Codespace), après `source creds.env`. `uv run ghcli gui` sert l'application à
l'adresse `http://127.0.0.1:8000`&nbsp;: le Codespace propose de l'ouvrir dans le
navigateur (**Open in Browser**, ou l'onglet **Ports**, à côté du terminal). `Ctrl+C`
l'arrête, avant de la relancer après une modification. Les solutions sont sur la
[branche `shiny-solution`](https://github.com/shuuchuu/ghcli/tree/shiny-solution) du
dépôt.

## Récupérer les tickets au clic

Dans `server`, récupérez les tickets du dépôt (`list_issues`) à chaque clic sur le
bouton, et seulement alors&nbsp;: pas à chaque lettre tapée dans les zones de texte.
Gardez-les dans une valeur réactive, et faites afficher par la sortie `count` leur
nombre, `3 issue(s)`, ou un message d'erreur si l'API en renvoie une.

**Documentation utile**

- https://shiny.posit.co/py/api/core/reactive.value.html
- https://shiny.posit.co/py/api/core/reactive.event.html

<details>
<summary>Conseils supplémentaires</summary>

`reactive.Value([])` est une valeur réactive, qui vaut d'abord une liste vide&nbsp;:
`issues()` la lit, `issues.set(...)` la change, et les sorties qui l'ont lue se
recalculent alors. Un effet décoré par `@reactive.event(input.fetch)` ne s'exécute
qu'au clic sur le bouton `fetch`. Une sortie est une fonction de `server` décorée par
`@render.text`, `@render.ui`…, du nom de son identifiant. Une deuxième valeur réactive
peut garder le message d'erreur&nbsp;; `list_issues` lève une `niquests.HTTPError` pour
un dépôt inconnu.

```python
def server(input: Inputs, output: Outputs, session: Session) -> None:  # ruff: ignore[builtin-argument-shadowing]
    issues: reactive.Value[list[Issue]] = reactive.Value([])
    error = reactive.Value("")

    @reactive.effect
    @reactive.event(input.fetch)
    def fetch() -> None:
        try:
            issues.set(list_issues(input.owner(), input.repo()))
            ...
        except HTTPError as exception:
            ...

    @render.text
    def count() -> str:
        return error() or ...
```

</details>

<details>
<summary>Solution</summary>

Les imports de `src/ghcli/gui.py`&nbsp;:

```python
"""Web interface showing when a repository's issues were opened, with Shiny."""

from collections import Counter
from typing import TYPE_CHECKING

import plotly.graph_objects as go
from niquests import HTTPError
from shiny import App, Inputs, Outputs, Session, reactive, render, run_app, ui

from .api import list_issues

if TYPE_CHECKING:
    from .model import Issue
```

`server`, sans sa docstring&nbsp;:

```python
def server(input: Inputs, output: Outputs, session: Session) -> None:  # ruff: ignore[builtin-argument-shadowing]
    issues: reactive.Value[list[Issue]] = reactive.Value([])
    error = reactive.Value("")

    # Runs on each click of the button only, not when the inputs change.
    @reactive.effect
    @reactive.event(input.fetch)
    def fetch() -> None:
        try:
            issues.set(list_issues(input.owner(), input.repo()))
            error.set("")
        except HTTPError as exception:
            issues.set([])
            error.set(f"Could not list the issues: {exception}")

    # The functions are named after their outputs' IDs.
    @render.text
    def count() -> str:
        return error() or f"{len(issues())} issue(s)"
```

</details>

## Le diagramme

Faites afficher par la sortie `plot` un diagramme en barres du nombre de tickets ouverts
chaque jour, avec Plotly&nbsp;: les jours en abscisse, dans l'ordre, et le nombre de
tickets en ordonnée, avec un titre et le nom des axes. Sans ticket, la sortie n'affiche
rien. Essayez avec un dépôt qui en a beaucoup, comme `octocat`/`Hello-World`.

**Documentation utile**

- https://docs.python.org/fr/3/library/collections.html#collections.Counter
- https://plotly.com/python/bar-charts/

<details>
<summary>Conseils supplémentaires</summary>

`issue.created_at.date()` est le jour de création d'un ticket, et un `Counter` compte
ses éléments&nbsp;: `Counter(["a", "b", "a"])` vaut `Counter({"a": 2, "b": 1})`.
`go.Figure(go.Bar(x=..., y=...))` est un diagramme en barres, et
`figure.update_layout(title=..., xaxis_title=..., yaxis_title=...)` le titre. Une
sortie `@render.ui` qui renvoie `None` n'affiche rien.

```python
def server(input: Inputs, output: Outputs, session: Session) -> None:  # ruff: ignore[builtin-argument-shadowing]
    ...

    @render.ui
    def plot() -> ui.HTML | None:
        if not issues():
            return None
        per_day = Counter(issue.created_at.date() for issue in issues())
        days = sorted(per_day)
        figure = go.Figure(go.Bar(x=days, y=...))
        ...
        return _figure_html(figure)
```

</details>

<details>
<summary>Solution</summary>

`server`&nbsp;:

```python
def server(input: Inputs, output: Outputs, session: Session) -> None:  # ruff: ignore[builtin-argument-shadowing]
    """Compute the outputs from the inputs.

    Args:
        input: The inputs, by ID: `input.owner()` is the owner typed in.
        output: The outputs (unused: the `render` decorators register them).
        session: The browser's session (unused).
    """
    issues: reactive.Value[list[Issue]] = reactive.Value([])
    error = reactive.Value("")

    # Runs on each click of the button only, not when the inputs change.
    @reactive.effect
    @reactive.event(input.fetch)
    def fetch() -> None:
        try:
            issues.set(list_issues(input.owner(), input.repo()))
            error.set("")
        except HTTPError as exception:
            issues.set([])
            error.set(f"Could not list the issues: {exception}")

    # The functions are named after their outputs' IDs.
    @render.text
    def count() -> str:
        return error() or f"{len(issues())} issue(s)"

    @render.ui
    def plot() -> ui.HTML | None:
        if not issues():
            return None
        per_day = Counter(issue.created_at.date() for issue in issues())
        days = sorted(per_day)
        figure = go.Figure(go.Bar(x=days, y=[per_day[day] for day in days]))
        figure.update_layout(
            title="Issues opened per day", xaxis_title="Day", yaxis_title="Issues"
        )
        return _figure_html(figure)
```

</details>
