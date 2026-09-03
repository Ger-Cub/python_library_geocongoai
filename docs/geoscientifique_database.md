# Guide du SDK `geoscientifique_database` (GeoCongo AI)

Ce module fournit un client Python typé permettant d'interagir directement avec les 3 Edge Functions Supabase de la plateforme **GeoCongo AI**.

---

## 1. Initialisation

```python
import os
from geocongoai import GeoCongoClient

# Option A : via la variable d'environnement GEOCONGOAI_API_KEY (Recommandé)
os.environ["GEOCONGOAI_API_KEY"] = "gcg_live_votre_cle_api"
client = GeoCongoClient()

# Option B : via l'argument du constructeur
client = GeoCongoClient(api_key="gcg_live_votre_cle_api")
```

---

## 2. Agent RAG (`/rag-agent`)

Permet de poser des questions complexes et d'obtenir des synthèses documentées. L'Edge Function Supabase authentifie la requête via le header `x-geocongo-api-key`.

```python
response = client.ask_rag(
    query="Quel est le potentiel géologique du Katanga ?",
    conversation_id="optionnel-uuid",
    voice_name="GeoCongo AI"
)

print(response.answer)
for source in response.sources:
    print(f"- {source.title} (Auteur: {source.author}, Score: {source.similarity})")
```

---

## 3. Recherche Documentaire (`/search-documents`)

Recherche sémantique ciblée sur les thèses, rapports et publications.

```python
docs_response = client.search_documents(
    query="cuivre et cobalt",
    domain="Mines",      # Optionnel
    category="Thèse",    # Optionnel
    province="Lualaba"   # Optionnel
)

print(f"Total trouvé : {docs_response.total_found}")
for doc in docs_response.results:
    print(f"Fichier : {doc.title} -> {doc.document_url}")
```

---

## 4. Recherche Géologique Multimodale (`/search-geological`)

Recherche vectorielle 1536D à travers roches, cartes, jeux de données et documents.

Valeurs acceptées pour `type` : `"all"`, `"documents"`, `"rocks"`, `"maps"`, `"datasets"`.

```python
geo_response = client.search_geological(
    query="malachite et cuivre",
    type="rocks",
    province="Haut-Katanga"
)

for item in geo_response.results:
    print(f"[{item.item_type}] {item.title} (Score: {item.similarity})")
```

---

## 5. Gestion des Erreurs

Toutes les exceptions dérivent de `GeoCongoError` :

* `InvalidParametersError` (HTTP 400) : Paramètres manquants ou invalides.
* `InsufficientBalanceError` (HTTP 402) : Solde d'unités épuisé.
* `ServerError` (HTTP 500) : Erreur serveur interne Supabase.
