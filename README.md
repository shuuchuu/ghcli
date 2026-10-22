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

- `src/ghcli/gui.py`, l'interface à compléter&nbsp;: `build_app` construit une
  application à deux onglets, vides pour l'instant, `create_gui` la sert, et
  `_format_issue` écrit un ticket en Markdown&nbsp;;
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

Dans l'onglet *List issues* de `build_app`, ajoutez deux zones de texte, le
propriétaire du dépôt et son nom, un bouton *List the issues* et une zone de Markdown
où s'affichent les tickets. Le bouton appelle une fonction `_list_issues(owner: str,
repo: str) -> str`, à écrire, qui renvoie les tickets du dépôt en Markdown, séparés par
une ligne horizontale (`---`), `No issue.` s'il n'en a pas, ou un message d'erreur si
l'API en renvoie une.

**Documentation utile**

- https://www.gradio.app/guides/blocks-and-event-listeners
- https://www.gradio.app/docs/gradio/textbox
- https://www.gradio.app/docs/gradio/markdown

<details>
<summary>Conseils supplémentaires</summary>

Dans un bloc `with gr.Tab(...)`, chaque composant créé s'ajoute à l'onglet, et `with
gr.Row():` en place plusieurs côte à côte. `button.click(fonction, inputs=[...],
outputs=...)` appelle la fonction avec les valeurs des composants d'entrée, et affiche
ce qu'elle renvoie dans celui de sortie. `list_issues` lève une `niquests.HTTPError`
pour un dépôt inconnu.

```python
def _list_issues(owner: str, repo: str) -> str:
    try:
        issues = list_issues(owner, repo)
    except HTTPError as error:
        return ...
    return "\n\n---\n\n".join(...) or "No issue."


# Dans build_app :
with gr.Tab("List issues"):
    with gr.Row():
        owner = gr.Textbox(label="Owner", placeholder="octocat")
        ...
    button = gr.Button("List the issues")
    issues = gr.Markdown()
    button.click(_list_issues, inputs=[...], outputs=...)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/gui.py`, avec ses imports&nbsp;:

```python
"""Web interface to GitHub issues, with Gradio."""

import gradio as gr
from niquests import HTTPError

from .api import create_issue, list_issues
from .model import Issue
```

```python
def _list_issues(owner: str, repo: str) -> str:
    try:
        issues = list_issues(owner, repo)
    except HTTPError as error:
        return f"Could not list the issues: {error}"
    return "\n\n---\n\n".join(map(_format_issue, issues)) or "No issue."
```

Dans `build_app`&nbsp;:

```python
with gr.Tab("List issues"):
    with gr.Row():
        owner = gr.Textbox(label="Owner", placeholder="octocat")
        repo = gr.Textbox(label="Repository", placeholder="Hello-World")
    button = gr.Button("List the issues")
    issues = gr.Markdown()
    # The function's arguments are the inputs' values, its return value
    # the output's.
    button.click(_list_issues, inputs=[owner, repo], outputs=issues)
```

</details>

## Créer un ticket

Dans l'onglet *Create an issue*, ajoutez le propriétaire du dépôt, son nom, le titre du
ticket et son corps (une zone de texte de plusieurs lignes), un bouton *Create the
issue* et une zone de Markdown qui affiche le ticket créé, ou un message d'erreur. Le
bouton appelle une fonction `_create_issue`, à écrire. Créez un ticket dans votre dépôt
de test, puis listez ses tickets dans l'autre onglet.

<details>
<summary>Conseils supplémentaires</summary>

`gr.Textbox(label="Body", lines=6)` est une zone de texte de six lignes. Les deux
onglets peuvent réutiliser les mêmes noms de variables&nbsp;: chaque `click` reçoit les
composants qui existent à son appel.

```python
def _create_issue(owner: str, repo: str, title: str, body: str) -> str:
    try:
        issue = create_issue(owner, repo, title, body)
    except HTTPError as error:
        return ...
    return _format_issue(issue)
```

</details>

<details>
<summary>Solution</summary>

`src/ghcli/gui.py`&nbsp;:

```python
def _create_issue(owner: str, repo: str, title: str, body: str) -> str:
    try:
        issue = create_issue(owner, repo, title, body)
    except HTTPError as error:
        return f"Could not create the issue: {error}"
    return _format_issue(issue)
```

Dans `build_app`&nbsp;:

```python
with gr.Tab("Create an issue"):
    with gr.Row():
        owner = gr.Textbox(label="Owner")
        repo = gr.Textbox(label="Repository")
    title = gr.Textbox(label="Title")
    body = gr.Textbox(label="Body", lines=6)
    button = gr.Button("Create the issue")
    issue = gr.Markdown()
    button.click(_create_issue, inputs=[owner, repo, title, body], outputs=issue)
```

</details>
