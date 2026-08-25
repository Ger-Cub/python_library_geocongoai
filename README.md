# GeoCongo AI — Python SDK & Geospatial Utilities (v0.1.0)

Bibliothèque Python officielle pour **GeoCongo AI** : accès aux Edge Functions Supabase, traitements d'images satellites et modèles d'IA géospatiaux.

---

## 🚀 Modules principaux

1. **`geocongoai.geoscientifique_database` (ou `GeoCongoClient`)** :
   - Client SDK officiel pour interagir avec les Edge Functions Supabase :
     - Agent RAG (`/rag-agent`) : synthèses et réponses documentées avec citations.
     - Recherche Documentaire (`/search-documents`) : recherche sémantique avec filtres (domaine, catégorie, province).
     - Recherche Géologique Multimodale (`/search-geological`) : recherche vectorielle (1536D) à travers roches, cartes, jeux de données et documents.
2. **`geocongoai.vision`** :
   - `generate_qr` : génération de QR codes.
   - `remove_background` : détourage d'image via `rembg`.
   - `pansharpen_brovey` : fusion d'images multispectrales et panchromatiques (Brovey method).
3. **`geocongoai.ia`** :
   - `PrithviClient` : wrapper pour les modèles d'IA géospatiaux Prithvi v2 via `terratorch`.
   - `AlphaEarthClient` : wrapper pour l'échantillonnage de pixels via Google Earth Engine (GEE).
4. **`geocongoai.gundua_engine`** :
   - `analyse_deterministe` : calculs d'indices spectraux (NDVI, NDWI) et analyse par règles.
   - `analyse_ia_fondation` & `traiter_image_satellite`.

---

## 🛠️ Installation

```bash
# Installation de base avec le SDK Edge Functions
python -m pip install -e .

# Optionnel : support Vision (Pansharpening, QR, Rembg)
python -m pip install -e .[vision]

# Optionnel : support IA (Prithvi, PyTorch, Earth Engine)
python -m pip install -e .[ia]
```

---

## 💻 Exemple d'utilisation rapide du SDK

```python
from geocongoai import GeoCongoClient
from geocongoai.exceptions import InsufficientBalanceError

# Initialisation du client avec la clé Supabase
client = GeoCongoClient(api_key="VOTRE_SUPABASE_ANON_KEY")

# 1. Poser une question à l'Agent RAG
try:
    response = client.ask_rag(
        query="Quels sont les indices de cobalt dans le Lualaba ?",
        user_id="123e4567-e89b-12d3-a456-426614174000"
    )
    print("Réponse :", response.answer)
    print("Sources :", response.sources)
except InsufficientBalanceError:
    print("Veuillez recharger votre solde unités.")

# 2. Recherche documentaire filtrée
docs = client.search_documents(
    query="cuivre et cobalt",
    domain="Mines",
    category="Thèse",
    province="Lualaba"
)
print(f"Trouvé {docs.total_found} documents.")

# 3. Rechercher des échantillons de roches ou cartes
results = client.search_geological(
    query="kimberlite diamant",
    type="rocks",
    province="Kasaï"
)
for item in results.results:
    print(f"[{item.item_type}] {item.title} (Score: {item.similarity})")
```

Voir les guides détaillés dans le dossier `docs/`.
