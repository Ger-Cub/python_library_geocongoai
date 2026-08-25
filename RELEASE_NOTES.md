# Release v0.1.0 — geocongoai

Date: 2026-08-24

Résumé:
- Migration vers la structure standard `src/geocongoai/` résolvant les problèmes d'importation et de packaging Python.
- Remplacement du module `text` par le SDK officiel `geoscientifique_database` (`GeoCongoClient`), permettant d'interagir avec les Edge Functions Supabase GeoCongo AI (`/rag-agent`, `/search-documents`, `/search-geological`).
- Ajout de la gestion typée des exceptions HTTP (ex: `InsufficientBalanceError` pour le statut 402, `InvalidParametersError` pour 400).
- Amélioration de `gundua_engine` avec calculs d'indices spectraux (NDVI, NDWI).
- Validation complète de la suite de tests unitaires `pytest` (100% de réussite).