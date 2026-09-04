# GeoCongo AI — Geological, Geospatial & Mining AI Python SDK (v0.3.0)

> **The Python SDK for geological RAG, geospatial remote sensing, and 3D mining resource modeling workflows.**

`geocongoai` est le SDK officiel Python pour **GeoCongo AI**. Il est structuré autour de **3 moteurs principaux** (Pekua, Gundua et Chimbua) appuyés par des outils scientifiques utilitaires (3D, géochimie, vision, IA fondation).

---

## 🏛️ L'Architecture des 3 Moteurs GeoCongo AI

```text
                                  GEOCONGO AI SDK (v0.3.0)
                                             │
        ┌────────────────────────────────────┼────────────────────────────────────┐
        ▼                                    ▼                                    ▼
  01 PEKUA ENGINE                      02 GUNDUA ENGINE                     03 CHIMBUA ENGINE
  (RAG & Recherche)                   (Découverte & Télédétection)         (Modélisation Géologique & Mine)
        │                                    │                                    │
  • Agent RAG Géoscientifique         • Analyse basée sur Règles           • Drillhole DB & QA/QC
  • Recherche Documentaire            • AI Foundation Models (GPU API)     • Compositing (Longueur fixe/Litho)
  • Recherche Vectorielle pgvector    • Télédétection Hyperspectrale       • Domaines Géologiques (IA + Déterm.)
  • Citation & Sources PDF/Cartes     • Ciblage Greenfield & Linéaments    • Wireframes & Solides 3D
                                                                           • Block Model 3D & Sub-blocking
                                                                           • Géostatistique & Krigeage (OK/IDW)
                                                                           • Estimation & Classification (JORC)
                                                                           • Optimisation de Fosse (Cônes)
                                                                           • Évaluation Économique (NPV/IRR)

  ── UTILITAIRES / TOOLBOX ────────────────────────────────────────────────────────────────────────────
  • datasets (DrillholeDataset, SampleDataset)   • visualization (Plotly 3D, Export HTML)
  • results (GeoResult universel)                • ia (Clay v1.5, Prithvi v2, AlphaEarth)
  • vision (Pansharpening, Rembg, Raster)
```

---

## 🚀 Présentation des 3 Moteurs

### 1. 🔍 Pekua Engine (`geocongoai.pekua_engine`)
>
> *"Pekua"* signifie *fouiller / rechercher dans les livres* en Swahili.

* **Rôle** : Moteur de recherche géoscientifique, d'extraction documentaire et d'assistance RAG.
* **Fonctionnalités** :
  * Interfaçage avec les Edge Functions Supabase (`/rag-agent`, `/search-documents`, `/search-geological`).
  * Recherche vectorielle 1536D dans pgvector (documents, cartes, roches, jeux de données).
  * Agent RAG géoscientifique multilingue avec résolution automatique des clés API (`GEOCONGOAI_API_KEY`).

### 2. 🛰️ Gundua Engine (`geocongoai.gundua_engine`)
>
> *"Gundua"* signifie *découvrir / explorer* en Swahili.

* **Rôle** : Moteur de découverte minière par télédétection, imagerie satellite et IA géospatiale.
* **Fonctionnalités** :
  * Module d'analyse basée sur des règles (`greenfield`, `illegal_mining`, `lineaments`, `landcover`, `landslide`).
  * Module d'analyse basées sur les modèles de fondation géospatiaux (Clay v1.5, Prithvi v2, AlphaEarth) exécutés sur des serveurs distants GPU.
  * Module d'analyse des données hyperspectrales.

### 3. ⛏️ Chimbua Engine (`geocongoai.chimbua_engine`)
>
> *"Chimbua"* signifie *extraire / miner / exploiter* en Swahili.

* **Rôle** : Moteur de gestion des forages, modélisation géologique 3D, géostatistique, estimation de ressources et évaluation technico-économique.
* **Fonctionnalités** :
  * **Drillholes & QA/QC** : Ingestion, validation topologique des sondages et trajectoires 3D.
  * **Compositing** : Régularisation des longueurs d'échantillonnage.
  * **Domaines Géologiques & Wireframes 3D** : Délimitation déterministe et assistée par IA des enveloppes minéralisées.
  * **Block Model 3D** : Grille régularisée, sous-blocs et contraintes de domaine.
  * **Géostatistique & Krigeage** : Variogrammes empiriques/modélisés, Krigeage Ordinaire (OK), IDW, NN.
  * **Resource Estimation & Classification** : Tonnage, teneurs, métal contenu et classification (Mesuré, Indiqué, Inféré).
  * **Optimisation de Fosse & Économie** : Cônes emboîtés, ratio de stérile, CAPEX, OPEX, Cash-Flow, NPV, IRR.

---

## 🛠️ Installation

```bash
# Installation standard
pip install geocongoai

# Avec dépendances 3D & Chimbua Engine (Plotly, Scipy, Scikit-Learn)
pip install geocongoai[spatial3d]

# Avec dépendances IA et Vision complètes
pip install geocongoai[vision,ia,spatial3d]
```

---

## 💻 Exemples d'Utilisation

### 🔑 Initialisation du Client (Authentification API Key)

```python
import os
from geocongoai import GeoCongoClient

# Recommandé : via variable d'environnement
os.environ["GEOCONGOAI_API_KEY"] = "gcg_live_votre_cle_api"
client = GeoCongoClient()

# Ou directement dans le constructeur
# client = GeoCongoClient(api_key="gcg_live_votre_cle_api")
```

---

### 🔍 Exemple 1 : Pekua Engine (Agent RAG & Recherche Géoscientifique)

```python
from geocongoai import GeoCongoClient

client = GeoCongoClient(api_key="gcg_live_votre_cle_api")

# 1. Poser une question à l'Agent RAG
response = client.ask_rag("Quels sont les gisements connus de cobalt au Lualaba ?")
print("Réponse :", response.answer)
for src in response.sources:
    print(f"- Source : {src.title} (similarité : {src.similarity})")

# 2. Recherche documentaire ciblée
docs = client.search_documents(
    query="cuivre et cobalt",
    domain="Mines",
    province="Lualaba"
)
print(f"Trouvé {docs.total_found} documents.")

# 3. Recherche géologique vectorielle multimodale
geo_results = client.search_geological(
    query="malachite et roche sédimentaire",
    type="rocks",
    province="Haut-Katanga"
)
```

---

### 🛰️ Exemple 2 : Gundua Engine (Télédétection & Prospection IA)

```python
from geocongoai.gundua_engine import GunduaEngineClient

client = GunduaEngineClient()

# 1. Analyse du potentiel minier (Greenfield)
result = client.analyze(
    "greenfield",
    bbox=[28.5, -11.5, 28.6, -11.4],   # [min_lon, min_lat, max_lon, max_lat]
    datetime="2023-06-01/2023-06-30"
)
print("Potentiel minier :", result.get("potential"))

# 2. Extraction de linéaments (failles / structures)
lineaments = client.analyze("lineaments", bbox=[28.5, -11.5, 28.6, -11.4])

# 3. Utilisation de Clay Foundation Model v1.5
from geocongoai.ia import ClayClient
clay = ClayClient(use_torchgeo=False)
embeddings = clay.load_precomputed_embeddings("https://source.coop/clay/kivu.parquet")
pca_rgb = clay.apply_pca(embeddings.embedding_matrix())
```

---

### ⛏️ Exemple 3 : Chimbua Engine (Gestion Forages, Clustering 3D & Visualisation)

```python
from geocongoai.chimbua_engine import (
    analyse_et_visualiser_forages_3d,
    compute_drillhole_intervals,
    cluster_assay_points,
    generate_cluster_hulls
)

collars = [
    {"hole_id": "DH01", "x": 500000, "y": 9200000, "z": 1200, "dip": -90, "azimuth": 0},
    {"hole_id": "DH02", "x": 500050, "y": 9200050, "z": 1205, "dip": -90, "azimuth": 0},
]
assays = [
    {"hole_id": "DH01", "from_m": 0, "to_m": 5, "cu_pct": 1.8},
    {"hole_id": "DH02", "from_m": 0, "to_m": 5, "cu_pct": 2.1},
]

# Pipeline complet 3D & Clustering DBSCAN
result = analyse_et_visualiser_forages_3d(
    collars=collars,
    assays=assays,
    grade_field="cu_pct",
    grade_threshold=1.0,
    output_html_path="rapport_3d.html"
)
print("Nombre d'intervalles analysés :", result["total_intervals"])
```

---

## 📦 Publication sur PyPI (Mainteneurs)

```bash
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```
