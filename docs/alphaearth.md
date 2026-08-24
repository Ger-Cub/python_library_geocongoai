# AlphaEarth (GEE) - guide d'utilisation

Ce document explique comment configurer l'acces a Google Earth Engine (GEE)
et utiliser `geocongoai.ia.alphaearth.AlphaEarthClient` pour extraire des
echantillons de pixels prêts a etre transformes en embeddings par un modele.

Prerequis:
- Avoir un compte GEE et les droits necessaires.
- Installer `earthengine-api`:

```bash
pip install earthengine-api
```

Authentification (service account recommande pour serveurs):

1. Creez une cle JSON pour votre compte de service dans Google Cloud.
2. Assignez au compte les roles necessaires pour acceder aux assets Earth Engine.
3. Dans Python:

```python
from geocongoai.ia.alphaearth import AlphaEarthClient

client = AlphaEarthClient(service_account='your-service-account@project.iam.gserviceaccount.com', credentials_json='/path/to/key.json')
client.authenticate()
```

Exemple d'extraction d'echantillons (pixels) pour une geometrie donnee:

```python
from geocongoai.ia.alphaearth import AlphaEarthClient
import ee

client = AlphaEarthClient()
client.authenticate()

geom = ee.Geometry.Polygon([[ [29.4, -2.5], [29.5, -2.5], [29.5, -2.6], [29.4, -2.6] ]])
res = client.extract_embeddings(geometry=geom, start_date='2022-01-01', end_date='2022-12-31', bands=['B4','B3','B2'])
print(res.get('count'))
```

Notes pratiques:
- La methode `extract_embeddings` retourne des vecteurs de pixels (pas encore
  des embeddings). Vous pouvez soit deployer un endpoint qui prend ces vecteurs
  et renvoie des embeddings, soit telecharger un modele et faire l'inference
  localement.
- Pour traiter de grandes zones, utilisez les mecanismes d'export (ee.batch.Export) au lieu de `getInfo()`.
