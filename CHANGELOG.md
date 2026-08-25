# Changelog

## [0.1.0] - 2026-08-24
### Added
- Passage à la structure standard `src/geocongoai/` (src-layout) pour une meilleure compatibilité de packaging et de distribution pip.
- Module SDK `geocongoai.geoscientifique_database` et classe principale `GeoCongoClient` pour l'intégration des 3 Edge Functions Supabase:
  - Agent RAG (`ask_rag` -> `/rag-agent`) avec gestion du solde d'unités (HTTP 402 `InsufficientBalanceError`).
  - Recherche Documentaire (`search_documents` -> `/search-documents`) avec filtres par domaine, catégorie et province.
  - Recherche Géologique Multimodale (`search_geological` -> `/search-geological`) pour la recherche vectorielle 1536D (roches, cartes, jeux de données, documents).
- Dataclasses typées : `RagResponse`, `RagSource`, `DocumentSearchResponse`, `DocumentItem`, `GeologicalSearchResponse`, `GeologicalItem`.
- `gundua_engine.analysis`: enrichissement d' `analyse_deterministe` avec le calcul automatique d'indices spectraux (NDVI, NDWI).

### Removed
- Suppression du module obsolète `geocongoai.text` (`saluer`, `introduire`, `dire_au_revoir`), remplacé par `geoscientifique_database`.
