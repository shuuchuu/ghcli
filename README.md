# Interface en ligne de commande pour GitHub Issues

[Rendu final sur GitHub](https://github.com/shuuchuu/ghcli).

Le but de ces travaux pratiques est de mettre en pratique les principes d'ingénierie vus durant la formation. Nous allons créer une interface en ligne de commande pour GitHub Issues, créer un paquet et le publier sur Test PyPI.

Pour l'environnement de travail, nous allons travailler sur GitHub Codespaces.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/shuuchuu/ghcli)

## Création d'un token GitHub

Pour pouvoir interagir avec l'API GitHub, vous aurez besoin d'un token :

1. Si vous n'avez pas encore de compte GitHub, créez-en en suivant [ce lien](https://github.com/signup), puis identifiez-vous.
2. Créez ensuite un token en suivant [ce lien](https://github.com/settings/tokens/new) avec les options suivantes :
    - `Note` : `GHCLI`
    - `Expiration` : `7 days`
    - `public_repo` : coché
3. Créez un fichier `creds.env` et copiez-y la valeur du token sous la forme suivante :

    ```shell
    export GHCLI_TOKEN=ghp_123
    ```

  Vous pourrez exécuter `source creds.env` dans le terminal avant de lancer le logiciel pour vous authentifier.

## Création d'un point d'entrée

- Créez le fichier `cli.py` dans votre dossier source
- Codez-y une fonction `main` qui ne prend aucun argument et affiche `Hello World`
- Modifiez le fichier `pyproject.toml` pour que la commande `ghcli` lance la fonction `main` du fichier `cli.py`, comme expliqué dans la [doc `uv`](https://docs.astral.sh/uv/concepts/projects/config/#entry-points) :

    ```toml
    [project.scripts]
    ghcli = 'ghcli.cli:main'
    ```

- Exécutez la commande `uv sync` pour que le point d'entrée devienne effectif
- Testez le avec la commande `ghcli`

## Ajout d'un parseur simple

Modifiez la fonction `main` du fichier `cli.py` pour qu'elle récupère deux arguments depuis la ligne de commande : un propriétaire de dépôt GitHub et le nom d'un dépôt GitHub. À terme, cela nous servira à aller récupérer dessus les issues.

Pour le moment, une fois ces arguments récupérés, affichez-les simplement dans la console.

## Connexion du parseur simple à une fonction

Créez maintenant un fichier `api.py` : c'est lui qui contiendra la logique de notre logiciel.

Pour l'instant, créez dedans une fonction `list_issues` à la signature qui suit :

```python
def list_issues(owner: str, repo: str) -> None:
```

Et qui affiche simplement les arguments qu'on lui passe. Faites ensuite en sorte que lorsque l'on appelle `ghcli`, cela appelle la fonction `list_issues` en transmettant les arguments récupérés.

## Récupération du token GitHub depuis une variable d'environnement

Implémentez dans le fichier `api.py` la fonction `_get_token` avec la signature suivante :

```python
def _get_token() -> str:
```

Elle devra retourner la valeur de la variable d'environnement `GHCLI_TOKEN`. Pour cela, vous pourrez utiliser le module `os` et son dictionnaire `environ` qui contient toutes les variables d'environnements accessibles et leur valeur.

Si la variable d'environnement `GHCLI_TOKEN` n'est pas dans le dictionnaire `os.environ`, utilisez le code d'erreur suivant :

```python
print(
    "Impossible de récupérer le token GitHub dans la variable d'environnement "
    "GHCLI_TOKEN. Définissez cette variable et relancez le programme.",
    file=sys.stderr,
)
sys.exit(1)

```

## Implémentation de la fonction `list_issues`

Implémentez maintenant la fonction `list_issues` avec la signature suivante :

```python
def list_issues(owner: str, repo: str) -> list[tuple[str, str, str]]:
```

Le but est que cette fonction renvoie une liste de n-uplets où chaque n-uplet contiendra le titre, le corps et l'url d'une issue.

Pour requêter le serveur GitHub afin qu'il vous renvoie toutes les issues d'un dépôt donné, vous pourrez utiliser le code suivant :

```python
response = requests.get(
    f"https://api.github.com/repos/{owner}/{repo}/issues",
    headers=dict(
        Accept="application/vnd.github.v3+json",
        Authorization=f"token {_get_token()}",
    ),
)
```

Il sera ensuite possible de récupérer le contenu de la réponse à l'aide du code suivant :

```python
response.json()
```

Pour plus d'informations sur la réponse retournée, vous pouvez consulter [la documentation GitHub](https://docs.github.com/en/rest/issues/issues#list-repository-issues).

Enfin, pensez à utiliser le retour de la fonction dans le fichier `cli.py` afin de montrer les résultats de l'appel à l'utilisateur.

## Implémentation de la fonction `create_issue` et connexion à `cli.py`

Commencez par créer une fonction `create_issue` avec la signature suivante :

```python
def create_issue(
  owner: str, repo: str, title: str, body: str
) -> tuple[str, str, str]:
```

La première partie de cet exercice consiste à connecter `cli.py` à cette fonction, comme nous l'avons déjà fait pour `list_issues`. La difficulté est qu'il va falloir maintenant introduire deux commandes distinctes dans notre interface : `create` et `list`. Vous pouvez pour cela consulter le cours.

Une fois la fonction connectée, vous pouvez l'implémenter : le but est que cette fonction crée une issue puis renvoie un n-uplet qui contient le titre, le corps et l'url de l'issue créée.

Pour requêter le serveur GitHub afin qu'il crée une issue, vous pourrez utiliser le code suivant :

```python
response = requests.post(
  f"https://api.github.com/repos/{owner}/{repo}/issues",
  json=dict(title=title, body=body),
  headers=dict(
    Accept="application/vnd.github.v3+json",
    Authorization=f"token {_get_token()}",
  ),
)
```

Il sera ensuite possible de récupérer le contenu de la réponse à l'aide du code suivant :

```python
response.json()
```

Pour plus d'informations sur la réponse retournée, vous pouvez consulter [la documentation GitHub](https://docs.github.com/en/rest/issues/issues#create-an-issue).

Enfin, pensez à utiliser le retour de la fonction dans le fichier `cli.py` afin de montrer les résultats de l'appel à l'utilisateur.

## Utilisation d'une classe pour représenter les issues

Pour l'instant, nous utilisons des n-uplets pour représenter les issues. Ce n'est pas le meilleur moyen : il est facile par exemple de confondre l'ordre des valeurs et d'introduire des bugs.

À l'aide du [module `dataclasses`](https://docs.python.org/fr/3/library/dataclasses.html) de la bibliothèque standard, créez une classe `Issue` et adaptez les éléments de code qui utilisaient les n-uplets.

## Ajout de tests

Maintenant que votre projet a des fonctionnalités de base, il est temps d'ajouter des tests (dans une démarche TDD, on aurait bien sûr commencé par ceux-ci).

Ajoutez un test par fonction dans le dossier `tests`.

## Publication

Tout semble prêt pour une première release ! Publiez votre paquet sur Test PyPI (pour rappel, utilisez bien l'argument `--index testpypi` dans votre commande de publication).
