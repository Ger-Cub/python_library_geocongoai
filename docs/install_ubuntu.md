# Installation système (Ubuntu / Debian) pour geocongoai

Ce guide couvre les dépendances système souvent requises pour `rasterio`,
`rembg` et autres bibliothèques natives.

1) Mettre à jour le système

```bash
sudo apt update && sudo apt upgrade -y
```

2) Installer dépendances communes (GDAL, PROJ, libjpeg, libpng, libwebp)

```bash
sudo apt install -y build-essential python3-dev python3-venv \
    gdal-bin libgdal-dev libgdal27 libproj-dev proj-bin \
    libjpeg-dev libpng-dev libwebp-dev libtiff-dev
```

3) Créer et activer un environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

4) Installer les dépendances Python recommandées pour `geocongoai[vision]`

```bash
pip install -e .[vision]
```

Remarques:
- Sur certaines distributions, `libgdal-dev` a un nom différent; consultez
  la documentation de votre distribution.
- Pour `rembg`, il peut être nécessaire d'installer `libwebp` et d'autres
  dépendances natives (fourni ci-dessus).
- Pour `torch`, suivez la page officielle (CPU ou CUDA) et installez la
  version adaptée à votre matériel si vous activez `geocongoai[ia]`.
