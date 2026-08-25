# Guide de Publication PyPI — `geocongoai`

Ce guide explique étape par étape comment construire et publier le package Python **`geocongoai`** sur **PyPI** (et **TestPyPI**).

---

## 📋 1. Prérequis & Outillage

Installez les outils officiels de packaging et de téléversement Python :

```bash
python -m pip install --upgrade pip
pip install build twine
```

---

## 🧹 2. Nettoyage & Génération du Build

Avant de construire le package, nettoyez les anciens fichiers de build :

```bash
rm -rf dist/ build/ src/*.egg-info geocongoai.egg-info
```

Générez ensuite les fichiers de distribution (Source Distribution `.tar.gz` et Wheel `.whl`) :

```bash
python -m build
```

Vérifiez que la métadonnée et la syntaxe de la description Markdown sont valides :

```bash
python -m twine check dist/*
```

*(Cette commande doit afficher `PASSED` pour les deux fichiers).*

---

## 🧪 3. Étape 1 : Publication de test sur TestPyPI (Recommandé)

Avant de publier sur le PyPI officiel, il est fortement conseillé de tester le package sur **TestPyPI**.

1. Créez un compte sur [test.pypi.org](https://test.pypi.org/) s'il n'est pas encore créé.
2. Générez un API Token : **Account Settings** > **API tokens** > **Add API token**.
3. Téléversez le package sur TestPyPI :

```bash
python -m twine upload --repository testpypi dist/*
```
- **Username** : `__token__`
- **Password** : `pypi-YOUR_TEST_PYPI_TOKEN_HERE`

4. Testez l'installation depuis TestPyPI dans un venv vierge :

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple geocongoai
```

---

## 🚀 4. Étape 2 : Publication officielle sur PyPI

Une fois la vérification sur TestPyPI validée :

1. Connectez-vous à votre compte officiel sur [pypi.org](https://pypi.org/).
2. Allez dans **Account Settings** > **API tokens** et créez un jeton d'accès pour `geocongoai`.
3. Lancez le téléversement sur PyPI :

```bash
python -m twine upload dist/*
```
- **Username** : `__token__`
- **Password** : `pypi-YOUR_OFFICIAL_PYPI_TOKEN`

4. Une fois publié, le package sera disponible immédiatement pour le monde entier via :

```bash
pip install geocongoai
```

---

## 🤖 5. Automatisation CI/CD via GitHub Actions (Optionnel)

Pour publier automatiquement à chaque création de Tag / Release GitHub :

1. Dans votre dépôt GitHub : **Settings** > **Secrets and variables** > **Actions** > **New repository secret**.
2. Créez un secret nommé `PYPI_API_TOKEN` avec la valeur de votre token PyPI (`pypi-...`).
3. Créez un fichier `.github/workflows/publish.yml` :

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: python -m twine upload dist/*
```
