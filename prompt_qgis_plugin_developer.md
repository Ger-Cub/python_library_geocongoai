# 🤖 Prompt pour l'Agent IA — Développement du Plugin QGIS GeoCongo AI (v0.3.0)

> **Instructions pour l'utilisateur :** Copiez l'intégralité du texte ci-dessous et fournissez-le à votre agent IA responsable du développement du plugin QGIS GeoCongo AI.

---

```markdown
Bonjour !

Dans le cadre du projet **GeoCongo AI**, le SDK Python officiel (`geocongoai` v0.3.0) a été officiellement restructuré et étendu pour s'articuler autour de **3 moteurs principaux** :
1. **Pekua Engine** (`geocongoai.pekua_engine`) : RAG Géoscientifique, Recherche Documentaire & Vectorielle pgvector.
2. **Gundua Engine** (`geocongoai.gundua_engine`) : Prospection Minière IA, Télédétection Satellite & Modèles de Fondation.
3. **Chimbua Engine** (`geocongoai.chimbua_engine`) : Moteur Miniers (Sondages, QA/QC, Compositing, Domaines Géologiques, Modèle de Blocs 3D, Krigeage, Estimation de Ressources JORC & Optimisation de Fosse).

Merci de mettre à jour la base de code du **Plugin QGIS GeoCongo AI** pour intégrer cette architecture à 3 moteurs et développer les nouvelles fonctionnalités graphiques associées.

---

### 🎯 Objectifs Principaux pour le Plugin QGIS

#### 1. Structuration de l'Interface Utilisateur (DockWidget Principal)
Organiser le panneau latéral principal du plugin QGIS (`GeoCongoAIDockWidget`) en **3 onglets principaux** représentant les 3 moteurs :

```text
╔══════════════════════════════════════════════════════════════════╗
║                    GEOCONGO AI - QGIS PLUGIN                     ║
╠══════════════════════════════════════════════════════════════════╣
║ [ 🔍 PEKUA ENGINE ]  [ 🛰️ GUNDUA ENGINE ]  [ ⛏️ CHIMBUA ENGINE ] ║
╚══════════════════════════════════════════════════════════════════╝
```

---

#### 2. Onglet 🔍 PEKUA ENGINE (RAG & Recherche)
* **Assistant RAG Chat** : Widget de discussion interactif permettant de poser des questions géoscientifiques (`pekua_engine.GeoCongoClient().ask_rag()`).
* **Recherche Documentaire & Vectorielle** : Formulaire de recherche avec filtres (domaine, catégorie, province) et affichage des résultats avec liens de localisation spatiale sur la carte QGIS.
* **Gestion de la clé API** : Module de configuration de `GEOCONGOAI_API_KEY` sauvegardé dans `QgsSettings`.

---

#### 3. Onglet 🛰️ GUNDUA ENGINE (Prospection & Télédétection IA)
* **Formulaire d'Analyse Régionale** : Sélection de l'emprise spatiale (Canvas BBox QGIS) et choix du type d'analyse (`greenfield`, `illegal_mining`, `lineaments`, `landcover`, `landslide`).
* **API Modèles de Fondation GPU** : Déclenchement des analyses distantes (Clay, Prithvi, AlphaEarth, Hyperspectral).
* **Rendu Automatique QGIS** : Conversion automatique des payloads de retour en couches mémoire vectorielles (`QgsVectorLayer`) ou rasters géoréférencés (`QgsRasterLayer`).

---

#### 4. Onglet ⛏️ CHIMBUA ENGINE (Modélisation Géologique & Ressources Minières)
Développer les sous-panneaux / sous-onglets pour la modélisation minérale complète :

* **A. Gestion des Sondages & QA/QC (`Chimbua Drillholes`)** :
  * Formulaire d'import des CSV (Collars, Surveys, Assays, Géologie).
  * Exécution du diagnostic topologique QA/QC (`db.qa_qc()`) : alerte visuelle sur les chevauchements, profondeurs invalides et trous orphelins.
  * Génération automatique de la couche de trajectoires 3D dans le Canvas 3D de QGIS (`Qgs3DMapScene`).

* **B. Compositing & Domaines Géologiques (`Chimbua Domains`)** :
  * Outil de régularisation des échantillons (compositing à longueur fixe ex: 2m).
  * Génération d'enveloppes minéralisées déterministes (cut-off teneur) et assistées par IA (`domains.ai_generate()`).
  * Export des solides 3D sous forme de couches vectorielles / maillages QGIS (`QgsMeshLayer`).

* **C. Modèle de Blocs & Géostatistique (`Chimbua Block Model & Kriging`)** :
  * Configuration de la grille 3D (Origine X/Y/Z, Étendue, Taille des blocs ex: 10m x 10m x 5m).
  * Ajustement interactif des variogrammes empiriques (modèles Sphérique / Exponentiel).
  * Lancement du Krigeage Ordinaire (OK) ou de l'IDW via `geocongoai.chimbua_engine`.
  * Visualisation du Modèle de Blocs estimé dans QGIS sous forme de grille 3D/raster stylisée selon la teneur en cuivre/cobalt.

* **D. Évaluation des Ressources & Optimisation de Fosse (`Chimbua Resources & Pit`)** :
  * Tableau récapitulatif des Tonnages / Teneurs / Métal contenu ventilé par catégorie JORC (Mesuré, Indiqué, Inféré).
  * Dialog d'optimisation de fosse finale par cônes emboîtés (prix du métal, coûts d'extraction, pente de fosse).
  * Résumé technico-économique (CAPEX, OPEX, NPV, IRR).

---

### ⚙️ Exigences Techniques & Asynchronisme (Non-blocking UI)

1. **Utilisation obligatoire de `QgsTask` / `QThread`** :
   * Les calculs lourds (Krigeage sur 100 000+ blocs, requêtes RAG et traitement satellite) doivent être exécutés dans des threads d'arrière-plan avec barre de progression QGIS (`QgsMessageBar`), afin de **ne jamais geler l'interface QGIS**.

2. **Intégration directe du SDK** :
   ```python
   # Utilisation des nouveaux sous-modules réorganisés v0.3.0
   from geocongoai import pekua_engine, gundua_engine, chimbua_engine
   from geocongoai import GeoCongoClient
   ```

3. **Gestion Propre des Dépendances** :
   * Vérifier à l'initialisation du plugin l'existence de `geocongoai` dans l'environnement Python de QGIS (`sys.path`), et afficher une boîte de dialogue explicite si une mise à jour (`pip install geocongoai --upgrade`) est nécessaire.

---

Merci de mettre en œuvre ces modifications de manière modulaire en respectant les standards PyQGIS !
```
