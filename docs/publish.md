# Publication sur TestPyPI

Préparer et tester la publication sur TestPyPI.

1) Installer outils de build et twine

```bash
python -m pip install --upgrade pip
pip install build twine
```

2) Construire la distribution

```bash
python -m build
```

3) Publier sur TestPyPI (utiliser un API token stocké dans `TWINE_PASSWORD`)

```bash
python -m twine upload --repository testpypi dist/*
```

Remarques:
- Pour automatiser via GitHub Actions, ajoutez un secret `TEST_PYPI_API_TOKEN` et
  déclenchez le workflow `publish.yml` présent dans `.github/workflows`.
- Ne partagez jamais votre token en clair.

Ajouter le secret GitHub `TEST_PYPI_API_TOKEN` (meilleure pratique):

1. Dans GitHub, allez dans Settings > Secrets and variables > Actions > New repository secret.
2. Créez un secret nommé `TEST_PYPI_API_TOKEN` avec la valeur du token TestPyPI.
3. Le workflow `.github/workflows/publish.yml` utilisera `${{ secrets.TEST_PYPI_API_TOKEN }}`.

Lancer manuellement la publication depuis votre machine (TestPyPI) :

```bash
python -m build
python -m twine upload --repository testpypi dist/* -u __token__ -p <TEST_PYPI_API_TOKEN>
```

Pour publier sur PyPI (apres verification sur TestPyPI) :

1. Créez un token PyPI (Account > API tokens) et stockez-le sous `PYPI_API_TOKEN` dans GitHub secrets.
2. Mettez à jour le workflow pour utiliser `PYPI_API_TOKEN` et publiez.

