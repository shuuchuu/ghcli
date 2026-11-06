# Interface web Gradio pour GitHub Issues

*[English version](https://github.com/shuuchuu/ghcli/tree/gradio-en)*

Le projet des travaux pratiques *Interface web Gradio pour GitHub Issues*. Ils partent
de la solution des travaux pratiques [*Interface en ligne de commande pour GitHub
Issues*](https://github.com/shuuchuu/ghcli)&nbsp;: `ghcli list` et `ghcli create`
listent et créent les tickets d'un dépôt, et sont testés. Nous allons leur ajouter une
interface web, avec Gradio. Leur énoncé est ci-dessous, pour les faire dans un
Codespace GitHub ou un clone local&nbsp;; c'est le même que celui du notebook des
travaux pratiques, en
[français](https://colab.research.google.com/github/shuuchuu/labs/blob/main/gui-github-issues-gradio-hands-on-fr.ipynb)
ou en
[anglais](https://colab.research.google.com/github/shuuchuu/labs/blob/main/gui-github-issues-gradio-hands-on-en.ipynb),
qui les fait dans Colab.

Le projet contient pour cela&nbsp;:

- `src/ghcli/gui.py`, l'interface à compléter&nbsp;: `construit_app` construit une
  application à deux onglets, vides pour l'instant, `cree_interface` la sert, et
  `_formate_ticket` écrit un ticket en Markdown&nbsp;;
- la commande `ghcli gui`, qui lance l'interface.

## Mise en place de l'environnement de travail

Ouvrez le dépôt dans un Codespace, sur sa branche `gradio`&nbsp;: sur GitHub, sur la
branche `gradio`, **Code** > **Codespaces** > **Create codespace on gradio**, ou [ce
lien](https://codespaces.new/shuuchuu/ghcli/tree/gradio). Le Codespace installe les
dépendances à sa création, dans le `.venv` du projet.

Dans un clone local de cette branche (`git clone -b gradio
https://github.com/shuuchuu/ghcli.git`), installez
[uv](https://docs.astral.sh/uv/getting-started/installation/), puis lancez `uv sync` à
la racine du dépôt.

`ghcli` a besoin d'un jeton GitHub&nbsp;: si vous n'en avez pas, créez un dépôt de test
et un jeton comme l'explique [l'énoncé de l'interface en ligne de
commande](https://github.com/shuuchuu/ghcli#un-dépôt-de-test-et-un-jeton-github), et
mettez-le dans un fichier `creds.env` à la racine du dépôt. Les commandes se lancent
dans un terminal à la racine du dépôt (**Terminal** > **Nouveau terminal** dans le
Codespace), après `source creds.env`. `uv run ghcli gui` sert l'interface à l'adresse
`http://127.0.0.1:7860`&nbsp;: le Codespace propose de l'ouvrir dans le navigateur
(**Open in Browser**, ou l'onglet **Ports**, à côté du terminal). `Ctrl+C` l'arrête,
avant de la relancer après une modification. Les solutions sont sur la [branche
`gradio-solution`](https://github.com/shuuchuu/ghcli/tree/gradio-solution) du dépôt.

## Lister les tickets d'un dépôt

Dans l'onglet *Lister les tickets* de `construit_app`, ajoutez deux zones de texte, le
propriétaire du dépôt et son nom, un bouton *Afficher les tickets* et une zone de
Markdown où s'affichent les tickets. Le bouton appelle une fonction
`_liste_tickets(proprietaire: str, depot: str) -> str`, à écrire, qui renvoie les
tickets du dépôt en Markdown, séparés par une ligne horizontale (`---`), `Aucun ticket.`
s'il n'en a pas, ou un message d'erreur si l'API en renvoie une.

**Documentation utile**

- https://www.gradio.app/guides/blocks-and-event-listeners
- https://www.gradio.app/docs/gradio/textbox
- https://www.gradio.app/docs/gradio/markdown

<details>
<summary>Conseils supplémentaires</summary>

Dans un bloc `with gr.Tab(...)`, chaque composant créé s'ajoute à l'onglet, et `with
gr.Row():` en place plusieurs côte à côte. `bouton.click(fonction, inputs=[...],
outputs=...)` appelle la fonction avec les valeurs des composants d'entrée, et affiche
ce qu'elle renvoie dans celui de sortie. `liste_tickets` lève une `niquests.HTTPError`
pour un dépôt inconnu.

```python
def _liste_tickets(proprietaire: str, depot: str) -> str:
    try:
        tickets = liste_tickets(proprietaire, depot)
    except HTTPError as erreur:
        return ...
    return "\n\n---\n\n".join(...) or "Aucun ticket."


# Dans construit_app :
with gr.Tab("Lister les tickets"):
    with gr.Row():
        proprietaire = gr.Textbox(label="Propriétaire", placeholder="octocat")
        ...
    bouton = gr.Button("Afficher les tickets")
    tickets = gr.Markdown()
    bouton.click(_liste_tickets, inputs=[...], outputs=...)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/gui.py`, avec ses imports&nbsp;:

```python
"""Interface web pour les tickets GitHub, avec Gradio."""

import gradio as gr
from niquests import HTTPError

from .api import cree_ticket, liste_tickets
from .modele import Ticket
```

```python
def _liste_tickets(proprietaire: str, depot: str) -> str:
    try:
        tickets = liste_tickets(proprietaire, depot)
    except HTTPError as erreur:
        return f"Impossible de lister les tickets : {erreur}"
    return "\n\n---\n\n".join(map(_formate_ticket, tickets)) or "Aucun ticket."
```

Dans `construit_app`&nbsp;:

```python
with gr.Tab("Lister les tickets"):
    with gr.Row():
        proprietaire = gr.Textbox(label="Propriétaire", placeholder="octocat")
        depot = gr.Textbox(label="Dépôt", placeholder="Hello-World")
    bouton = gr.Button("Afficher les tickets")
    tickets = gr.Markdown()
    # Les arguments de la fonction sont les valeurs des entrées, sa valeur de
    # retour celle de la sortie.
    bouton.click(_liste_tickets, inputs=[proprietaire, depot], outputs=tickets)
```

</details>

## Créer un ticket

Dans l'onglet *Créer un ticket*, ajoutez le propriétaire du dépôt, son nom, le titre du
ticket et son corps (une zone de texte de plusieurs lignes), un bouton *Créer le
ticket* et une zone de Markdown qui affiche le ticket créé, ou un message d'erreur. Le
bouton appelle une fonction `_cree_ticket`, à écrire. Créez un ticket dans votre dépôt
de test, puis listez ses tickets dans l'autre onglet.

<details>
<summary>Conseils supplémentaires</summary>

`gr.Textbox(label="Corps", lines=6)` est une zone de texte de six lignes. Les deux
onglets peuvent réutiliser les mêmes noms de variables&nbsp;: chaque `click` reçoit les
composants qui existent à son appel.

```python
def _cree_ticket(proprietaire: str, depot: str, titre: str, corps: str) -> str:
    try:
        ticket = cree_ticket(proprietaire, depot, titre, corps)
    except HTTPError as erreur:
        return ...
    return _formate_ticket(ticket)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/gui.py`&nbsp;:

```python
def _cree_ticket(proprietaire: str, depot: str, titre: str, corps: str) -> str:
    try:
        ticket = cree_ticket(proprietaire, depot, titre, corps)
    except HTTPError as erreur:
        return f"Impossible de créer le ticket : {erreur}"
    return _formate_ticket(ticket)
```

Dans `construit_app`&nbsp;:

```python
with gr.Tab("Créer un ticket"):
    with gr.Row():
        proprietaire = gr.Textbox(label="Propriétaire")
        depot = gr.Textbox(label="Dépôt")
    titre = gr.Textbox(label="Titre")
    corps = gr.Textbox(label="Corps", lines=6)
    bouton = gr.Button("Créer le ticket")
    ticket = gr.Markdown()
    bouton.click(
        _cree_ticket, inputs=[proprietaire, depot, titre, corps], outputs=ticket
    )
```

</details>
