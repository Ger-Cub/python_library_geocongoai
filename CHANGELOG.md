# Changelog

## [0.2.1] - 2026-08-26
### Added
- Nouveau design HTML canonique et responsive pour les exports `HTMLRenderer` avec en-tête professionnel, logo GeoCongo AI et badges statistiques.
- Rendu automatique du design HTML complet dans les cellules de Notebooks Jupyter lors de l'appel à `result.show_3d()`.
- Remplacement des marqueurs carrés par des symboles circulaires (`symbol='circle'`) pour les trajectoires de forages et les points d'analyse géochimique.
- Suppression automatique des titres et logos en surimpression sur la scène 3D Plotly lors de l'export HTML afin d'éviter tout doublon visuel avec l'en-tête HTML.

## [0.2.0] - 2026-08-26
### Added
- Refonte architecturale modulaire : `Dataset` -> `Analysis` -> `GeoResult` -> `Visualization`.
- Module `geocongoai.datasets` (`DrillholeDataset`, `SampleDataset`) pour le chargement et la validation de forages et d'échantillons depuis CSV, DataFrames Pandas et listes de dictionnaires.
- Module `geocongoai.analysis` (`geometry3d`, `geochemistry`, `clustering`) avec calculs 3D, seuillages et clustering DBSCAN 3D.
- Module `geocongoai.results` et classe universelle `GeoResult` supportant les exports `to_dict()`, `to_json()`, `to_geojson()`, `to_dataframe()`, `show_3d()` et `to_html()`.
- Module `geocongoai.visualization` (`PlotlyRenderer`, `HTMLRenderer`) pour les scènes 3D interactives Plotly et les exports HTML autonomes offline.
- Maintien de la rétrocompatibilité à 100% avec les modules et fonctions `gundua_engine.drillholes` existants.

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
