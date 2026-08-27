# GeoCongo AI — Geological, Geospatial & AI Python SDK (v0.2.1)

> **The Python SDK for geological, geospatial and AI-powered exploration workflows.**

`geocongoai` est le SDK officiel Python pour **GeoCongo AI** : moteur d'analyse géologique 3D, gestion unifiée de jeux de données, accès aux Edge Functions Supabase RAG/Géologie, traitements d'images satellites et modèles fondations IA.

---

## 🏛️ Les 4 Piliers de GeoCongo AI SDK

```text
                       GEOCONGO AI SDK (v0.2.1)
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
     01 DATA                  02 ANALYSIS              03 RESULTS              04 VISUALIZATION
         │                        │                        │                        │
  • DrillholeDataset       • DBSCAN 3D              • GeoResult              • Plotly 3D
  • SampleDataset          • Trajectoires 3D        • Contract JSON v1.0     • Export HTML Offline
  • CSV / DataFrames       • Convex Hull Mesh       • GeoJSON / DataFrame    • React / Three.js
  • PostGIS / Supabase     • Seuillage Géochimique  • Metadata & Stats       • Jupyter Notebook

  05 GUNDUA ENGINE (Règles)
         │
  • Greenfield (potentiel minier)
  • Illegal Mining (risque)
  • Lineaments (failles/fractures)
  • Landcover (occupation sol)
  • Landslide (susceptibilité)
```

---

## 🚀 Modules principaux

1. **`geocongoai.datasets` (`DrillholeDataset`, `SampleDataset`)** :
   - Ingestion et validation unifiées de forages (collars, assays, dev) et d'échantillons de surface.
   - Chargement transparent depuis CSV, DataFrames `pandas` ou Supabase.
2. **`geocongoai.analysis` (`geometry3d`, `geochemistry`, `clustering`)** :
   - Calculs trigonométriques des trajectoires 3D désaxées (`dip`, `azimuth`).
   - Moteur de clustering spatial 3D (`DBSCAN`) et génération d'enveloppes 3D (*Convex Hulls*).
3. **`geocongoai.results` (`GeoResult`)** :
   - Objet universel standardisé de résultat scientifique.
   - Exporte instantanément vers du JSON (`to_json()`), du GeoJSON (`to_geojson()`), des DataFrames (`to_dataframe()`) ou un dictionnaire Python (`to_dict()`).
4. **`geocongoai.visualization` (`PlotlyRenderer`, `HTMLRenderer`)** :
   - Visualisation 3D interactive dans Jupyter via `result.show_3d()`.
   - Export HTML autonome offline avec `result.to_html("export.html")`.
5. **`geocongoai.geoscientifique_database` (ou `GeoCongoClient`)** :
   - Agent RAG (`ask_rag`), Recherche Documentaire (`search_documents`), Recherche Géologique Multimodale 1536D (`search_geological`).
6. **`geocongoai.gundua_engine` (`GunduaEngineClient`, `analyse_basee_sur_des_regles`)** :
   - Moteur de découverte géospatiale par **analyse basée sur des règles** via API dédiée.
   - 5 types d'analyses : `greenfield`, `illegal_mining`, `lineaments`, `landcover`, `landslide`.
   - Utilisation directe avec un payload JSON, sans dépendances lourdes.
7. **`geocongoai.vision` & `geocongoai.ia`** :
   - Pansharpening, détourage d'images, wrappers Prithvi v2 & Google Earth Engine.

---

## 🛠️ Installation

```bash
# Installation standard
pip install geocongoai

# Avec dépendances 3D (Plotly, Scipy, Scikit-Learn)
pip install geocongoai[spatial3d]

# Avec dépendances Vision / IA complets
pip install geocongoai[vision,ia,spatial3d]
```

---

## 💻 Exemple 1 : Workflow d'Analyse 3D des Forages

```python
from geocongoai import DrillholeDataset

# 1. Ingestion des données de forages (CSV ou DataFrames)
dataset = DrillholeDataset.from_csv(
    collar_path="collars.csv",
    assay_path="assays.csv"
)

# Diagnostic exécutif du dataset (détecte automatiquement tous les éléments géochimiques)
print(dataset.info())

# 2. Analyse Spatiale 3D & DBSCAN (ex. sur la colonne 'CU' ou 'cu_pct')
result = dataset.analyze(
    method="dbscan",
    element="CU",         # Accepte le nom exact de la colonne (ex: 'CU', 'cu_pct', 'NI', 'FE', 'S')
    grade_threshold=0.5,  # Teneur de coupure 0.5%
    eps=25.0,             # Rayon 25m
    min_samples=3
)

# 3. Visualisation 3D directe dans un Notebook Jupyter
result.show_3d()

# 4. Export HTML autonome pour consultation offline
result.to_html("rapport_forages_3d.html")

# 5. Export JSON pour FastAPI et Frontend React
json_payload = result.to_json()
```

### 🔬 Gestion Multi-Éléments (CU, NI, FE, S, Au...)
> **Note sur le nom des colonnes** : Vous n'êtes **pas obligé de renommer vos colonnes** en `cu_pct`. Le paramètre `element="cu_pct"` est simplement une **valeur par défaut**. Vous pouvez passer directement le nom de n'importe quelle colonne numérique de la table `assay`.

Exemple d'analyse dynamique sur plusieurs éléments :
```python
# Seuils de coupure personnalisés par élément
seuils = {"CU": 0.5, "NI": 0.2, "FE": 10.0, "S": 1.0}

results = {}
for elem in dataset.info()["elements"]:
    threshold = seuils.get(elem, 0.5)
    results[elem] = dataset.analyze(method="dbscan", element=elem, grade_threshold=threshold)

# Visualisation 3D du Nickel
results["NI"].show_3d()
```

---

## 🌍 Exemple 2 : Analyses Basées sur des Règles — Gundua Engine

> Le **Gundua Engine** est le moteur de découverte géospatiale de GeoCongo AI. Il analyse des images satellitaires (Sentinel-2, DEM) pour détecter des zones minières, cartographier l'occupation du sol ou évaluer les risques géologiques, **sans installation de dépendances lourdes**.

```python
from geocongoai.gundua_engine import GunduaEngineClient, analyse_basee_sur_des_regles

# --- Option A : Client orienté-objet (recommandé) ---
client = GunduaEngineClient()

# 1. Analyse du potentiel minier (Greenfield)
result = client.analyze(
    "greenfield",
    bbox=[28.5, -11.5, 28.6, -11.4],   # [min_lon, min_lat, max_lon, max_lat]
    datetime="2023-06-01/2023-06-30"
)
print(result)  # {"potential": 0.78, "high_potential_area_km2": 4.2, ...}

# 2. Détection de mines illicites
result = client.analyze(
    "illegal_mining",
    bbox=[28.5, -11.5, 28.6, -11.4],
    datetime="2023-06-01/2023-06-30"
)
print(result["risk_level"])  # "high"

# 3. Extraction de linéaments (failles/fractures)
result = client.analyze("lineaments", bbox=[28.5, -11.5, 28.6, -11.4])

# 4. Classification d'occupation du sol
result = client.analyze("landcover", bbox=[28.5, -11.5, 28.6, -11.4])

# 5. Susceptibilité aux glissements de terrain
result = client.analyze("landslide", bbox=[28.5, -11.5, 28.6, -11.4])
```

```python
# --- Option B : Payload dict direct (style API REST) ---
result = analyse_basee_sur_des_regles({
    "analysis_type": "greenfield",
    "bbox": [28.5, -11.5, 28.6, -11.4],
    "datetime": "2023-06-01/2023-06-30"
})
```

### 📊 Types d'analyse disponibles

| Type | Source de données | Détection | Sortie principale |
|---|---|---|---|
| `greenfield` | Sentinel-2 | Indices minéraux pondérés | `potential` (0–1) |
| `illegal_mining` | Sentinel-2 | Sol nu + végétation | `risk_level` + stats |
| `lineaments` | DEM | Hillshade + bords | LineStrings + orientation |
| `landcover` | Sentinel-2 | Seuils spectraux | 4 classes d'occupation |
| `landslide` | DEM + S2 | Pente + humidité | `susceptibility` (high/mod/low) |

---

## 💻 Exemple 3 : Interroger l'Agent RAG & la Base Géoscientifique

```python
from geocongoai import GeoCongoClient

client = GeoCongoClient(api_key="VOTRE_SUPABASE_ANON_KEY")

# Poser une question à l'Agent RAG
response = client.ask_rag(
    query="Quels sont les gisements connus de cobalt au Lualaba ?",
    user_id="user_123"
)
print("Réponse :", response.answer)
```

---

## 📦 Publication sur PyPI (Pour les mainteneurs)

```bash
# Build
python -m build

# Verification
python -m twine check dist/*

# Publication Officielle
python -m twine upload dist/*
```
