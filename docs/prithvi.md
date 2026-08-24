# PrithviClient (geocongoai.ia.prithvi)

Installation recommandée (extras `ia`):

```bash
python -m pip install -e .[ia]
```

Pré-requis:
- `torch` adapté à votre plateforme (GPU/CPU)
- `terratorch` (fournit `BACKBONE_REGISTRY`)
- `rasterio`, `numpy` pour la lecture des tiffs

Usage minimal:

```python
from geocongoai.ia import PrithviClient

client = PrithviClient(model_name="prithvi_eo_v2_300", pretrained=True)
# charger le modèle (lazy-load)
client.load_model()

# extraire des features depuis un TIF local
res = client.extract_deep_features("/path/to/image.tif")
print(res.keys())
```

Notes:
- Le package ne contient pas les poids du modèle. `PrithviClient` construit le backbone via `terratorch`.
- Pour utiliser des poids custom, fournissez l'argument `build_kwargs` à `load_model()` ou configurez `terratorch` selon la documentation du fournisseur des poids.
- Les pipelines de prétraitement (mosaïque, normalisation) doivent être appliqués côté utilisateur ou ajoutés via `PrithviClient` avant l'appel `extract_deep_features`.
