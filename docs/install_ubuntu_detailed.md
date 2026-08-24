# Installation système détaillée (Ubuntu/Debian)

Ce guide explique comment préparer un environnement Ubuntu/Debian pour développer et exécuter `geocongoai` (notamment `rasterio`, `rembg`, `torch` et outils GDAL/PROJ).

1) Mise à jour

```bash
sudo apt update && sudo apt upgrade -y
```

2) Paquets communs (Ubuntu 22.04+ / Debian 11+)

```bash
sudo apt install -y build-essential git curl ca-certificates \
  python3-dev python3-venv python3-pip \
  gdal-bin libgdal-dev proj-bin libproj-dev \
  libjpeg-dev libpng-dev libwebp-dev libtiff-dev \
  libgeos-dev
```

Remarques par version:
- Ubuntu 20.04: certains paquets peuvent avoir des versions plus anciennes; utilisez les backports ou un PPA pour obtenir des versions récentes de GDAL si nécessaire.
- Ubuntu 22.04/24.04 et Debian 12+ contiennent des paquets récents pour `rasterio` et `gdal`.

3) Configuration virtuelle Python

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

4) Installer les dépendances Python (vision)

```bash
pip install qrcode[pil] Pillow numpy
pip install rasterio
pip install rembg
```

Notes pour `rasterio`:
- Si `rasterio` échoue à l'installation, vérifiez que `gdal-config` est dans le PATH. Exemple:
  `export CPLUS_INCLUDE_PATH=/usr/include/gdal` avant le `pip install rasterio`.

Notes pour `rembg`:
- `rembg` installe `pymatting` et `opencv-python-headless`; s'assurer que `libwebp-dev` et `libjpeg-dev` sont présents.

5) Installer `torch` (IA)

Suivez la page officielle https://pytorch.org/get-started/locally/ pour sélectionner la bonne commande selon votre GPU/CPU et CUDA. Exemple (CPU-only):

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

6) Dépannage commun
- Erreur `gdal-config not found`: installez `libgdal-dev` et assurez-vous que `gdal-config` est accessible.
- Erreurs liées à `numpy`/`scipy`: installez d'abord `python3-dev` et `build-essential`.

7) Tester l'installation minimale

```bash
python - <<'PY'
from PIL import Image
import qrcode
import rasterio
print('Pillow, qrcode et rasterio OK')
PY
```
