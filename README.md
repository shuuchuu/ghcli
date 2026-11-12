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

- `src/ghcli/gui.py`, l'application à compléter&nbsp;: `interface` en décrit l'interface
  (deux zones de texte, `proprietaire` et `depot`, un bouton, `recupere`, et deux
  sorties, `nombre` et `graphique`) et charge dans l'en-tête de la page le JavaScript
  de Plotly, `serveur` en calculera les sorties, `cree_interface` la sert, et
  `_convertit_en_html` transforme une figure Plotly en HTML qu'affiche une
  sortie&nbsp;;
- dans `src/ghcli/modele.py`, la date de création de chaque ticket,
  `Ticket.date_creation`&nbsp;;
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

Dans `serveur`, récupérez les tickets du dépôt (`liste_tickets`) à chaque clic sur le
bouton, et seulement alors&nbsp;: pas à chaque lettre tapée dans les zones de texte.
Gardez-les dans une valeur réactive, et faites afficher par la sortie `nombre` leur
nombre, `3 ticket(s)`, ou un message d'erreur si l'API en renvoie une.

**Documentation utile**

- https://shiny.posit.co/py/api/core/reactive.value.html
- https://shiny.posit.co/py/api/core/reactive.event.html

<details>
<summary>Conseils supplémentaires</summary>

`reactive.Value([])` est une valeur réactive, qui vaut d'abord une liste vide&nbsp;:
`tickets()` la lit, `tickets.set(...)` la change, et les sorties qui l'ont lue se
recalculent alors. Un effet décoré par `@reactive.event(entrees.recupere)` ne s'exécute
qu'au clic sur le bouton `recupere`. Une sortie est une fonction de `serveur` décorée
par `@render.text`, `@render.ui`…, du nom de son identifiant. Une deuxième valeur
réactive peut garder le message d'erreur&nbsp;; `liste_tickets` lève une `niquests.HTTPError`
pour un dépôt inconnu.

```python
def serveur(entrees: Inputs, sorties: Outputs, session: Session) -> None:
    tickets: reactive.Value[list[Ticket]] = reactive.Value([])
    erreur = reactive.Value("")

    @reactive.effect
    @reactive.event(entrees.recupere)
    def recupere() -> None:
        try:
            tickets.set(liste_tickets(entrees.proprietaire(), entrees.depot()))
            ...
        except HTTPError as exception:
            ...

    @render.text
    def nombre() -> str:
        return erreur() or ...
```

</details>

<details>
<summary>Solution</summary>

Les imports de `src/ghcli/gui.py`&nbsp;:

```python
"""Interface web montrant quand les tickets d'un dépôt ont été ouverts, avec Shiny."""

from collections import Counter
from typing import TYPE_CHECKING

import plotly.graph_objects as go
from niquests import HTTPError
from plotly.offline import get_plotlyjs_version
from shiny import App, Inputs, Outputs, Session, reactive, render, run_app, ui

from .api import liste_tickets

if TYPE_CHECKING:
    from .modele import Ticket
```

`serveur`, sans sa docstring&nbsp;:

```python
def serveur(entrees: Inputs, sorties: Outputs, session: Session) -> None:
    tickets: reactive.Value[list[Ticket]] = reactive.Value([])
    erreur = reactive.Value("")

    # S'exécute à chaque clic sur le bouton seulement, pas quand les entrées changent.
    @reactive.effect
    @reactive.event(entrees.recupere)
    def recupere() -> None:
        try:
            tickets.set(liste_tickets(entrees.proprietaire(), entrees.depot()))
            erreur.set("")
        except HTTPError as exception:
            tickets.set([])
            erreur.set(f"Impossible de lister les tickets : {exception}")

    # Les fonctions portent le nom des identifiants de leurs sorties.
    @render.text
    def nombre() -> str:
        return erreur() or f"{len(tickets())} ticket(s)"
```

</details>

## Le diagramme

Faites afficher par la sortie `graphique` un diagramme en barres du nombre de tickets
ouverts chaque jour, avec Plotly&nbsp;: les jours en abscisse, dans l'ordre, et le nombre de
tickets en ordonnée, avec un titre et le nom des axes. Sans ticket, la sortie n'affiche
rien. Essayez avec un dépôt qui en a beaucoup, comme `octocat`/`Hello-World`.

**Documentation utile**

- https://docs.python.org/fr/3/library/collections.html#collections.Counter
- https://plotly.com/python/bar-charts/

<details>
<summary>Conseils supplémentaires</summary>

`ticket.date_creation.date()` est le jour de création d'un ticket, et un `Counter`
compte ses éléments&nbsp;: `Counter(["a", "b", "a"])` vaut `Counter({"a": 2, "b": 1})`.
`go.Figure(go.Bar(x=..., y=...))` est un diagramme en barres, et
`figure.update_layout(title=..., xaxis_title=..., yaxis_title=...)` le titre. Une sortie
`@render.ui` qui renvoie `None` n'affiche rien.

```python
def serveur(entrees: Inputs, sorties: Outputs, session: Session) -> None:
    ...

    @render.ui
    def graphique() -> ui.HTML | None:
        if not tickets():
            return None
        par_jour = Counter(ticket.date_creation.date() for ticket in tickets())
        jours = sorted(par_jour)
        figure = go.Figure(go.Bar(x=jours, y=...))
        ...
        return _convertit_en_html(figure)
```

</details>

<details>
<summary>Solution</summary>

`serveur`&nbsp;:

```python
def serveur(entrees: Inputs, sorties: Outputs, session: Session) -> None:
    """Calcule les sorties à partir des entrées.

    Args:
        entrees: Les entrées, par identifiant : `entrees.proprietaire()` est le
            propriétaire saisi.
        sorties: Les sorties (inutilisées : les décorateurs `render` les enregistrent).
        session: La session du navigateur (inutilisée).
    """
    tickets: reactive.Value[list[Ticket]] = reactive.Value([])
    erreur = reactive.Value("")

    # S'exécute à chaque clic sur le bouton seulement, pas quand les entrées changent.
    @reactive.effect
    @reactive.event(entrees.recupere)
    def recupere() -> None:
        try:
            tickets.set(liste_tickets(entrees.proprietaire(), entrees.depot()))
            erreur.set("")
        except HTTPError as exception:
            tickets.set([])
            erreur.set(f"Impossible de lister les tickets : {exception}")

    # Les fonctions portent le nom des identifiants de leurs sorties.
    @render.text
    def nombre() -> str:
        return erreur() or f"{len(tickets())} ticket(s)"

    @render.ui
    def graphique() -> ui.HTML | None:
        if not tickets():
            return None
        par_jour = Counter(ticket.date_creation.date() for ticket in tickets())
        jours = sorted(par_jour)
        figure = go.Figure(go.Bar(x=jours, y=[par_jour[jour] for jour in jours]))
        figure.update_layout(
            title="Tickets ouverts par jour", xaxis_title="Jour", yaxis_title="Tickets"
        )
        return _convertit_en_html(figure)
```

</details>
