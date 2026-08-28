"""Exemple complet : Clay Foundation Model + TorchGeo Embeddings.

Ce script démontre les 3 voies d'utilisation de ClayClient :

  1. Embeddings précalculés GeoParquet (sans GPU) → PCA → carte RGB
  2. Modèle TorchGeo natif (DOFA) sur un GeoTIFF local
  3. Clustering KMeans des patches pour segmentation non supervisée

Références :
  - Clay Foundation Model : https://github.com/Clay-foundation/model
  - TorchGeo : https://torchgeo.readthedocs.io/en/stable/tutorials/embeddings.html
  - Source Cooperative embeddings : https://source.coop/clay/

Usage::

    # Installation des dépendances (voie légère)
    pip install geocongoai geopandas pyarrow scikit-learn numpy

    # Installation complète (TorchGeo + GPU)
    pip install geocongoai[ia] torchgeo scikit-learn tqdm rasterio

    python examples/clay_example.py
"""

from __future__ import annotations

import os
import tempfile

# ── Imports geocongoai ──────────────────────────────────────────────────────
from geocongoai.ia.clay import ClayClient, ClayEmbeddingDataset


# ===========================================================================
# 1. Embeddings précalculés depuis Source Cooperative (sans GPU)
# ===========================================================================

def demo_precomputed_embeddings() -> None:
    """Charge des embeddings Clay précalculés et applique PCA → RGB.

    Utilise les embeddings publiés par Clay Foundation sur Source Cooperative.
    Aucun GPU requis, aucun modèle à télécharger.
    """
    print("\n" + "=" * 60)
    print("VOIE 1 : Embeddings précalculés (GeoParquet sans GPU)")
    print("=" * 60)

    # URL exemple (remplacer par une URL réelle de Source Cooperative)
    # https://source.coop/clay/clay-model-v0-embeddings/
    EXAMPLE_URL = (
        "https://source.coop/clay/clay-model-v0-embeddings/"
        "tiles/14/8481/7664.parquet"
    )

    client = ClayClient(use_torchgeo=False)

    # Charge les embeddings (~ quelques MB, pas de GPU)
    print(f"Chargement depuis : {EXAMPLE_URL}")
    try:
        ds: ClayEmbeddingDataset = client.load_precomputed_embeddings(EXAMPLE_URL)
        print(f"  → {ds}")

        # Matrice d'embeddings
        emb_matrix = ds.embedding_matrix()
        print(f"  → Forme de la matrice : {emb_matrix.shape}")

        # PCA → 3 composantes RGB
        pca_result = client.apply_pca(emb_matrix, n_components=3)
        print(f"  → Variance expliquée (PCA 3D) : "
              f"{[f'{v:.1%}' for v in pca_result['explained_variance_ratio']]}")
        print(f"  → Shape PCA : {pca_result['pca_features'].shape}")

    except Exception as exc:
        print(f"  [ATTENTION] Chargement URL échoué (connexion requise) : {exc}")
        print("  → Simulation avec données aléatoires…")

        import numpy as np
        fake_embs = np.random.randn(50, 768).astype("float32")  # 50 patches, 768-D
        pca_result = client.apply_pca(fake_embs, n_components=3)
        print(f"  → PCA simulée - Variance expliquée : "
              f"{[f'{v:.1%}' for v in pca_result['explained_variance_ratio']]}")


# ===========================================================================
# 2. TorchGeo natif : DOFA sur des patches Sentinel-2
# ===========================================================================

def demo_torchgeo_embeddings() -> None:
    """Extrait des embeddings avec DOFA (ViT-B/16) via TorchGeo.

    Génère un patch synthétique Sentinel-2 (3 bandes, 256×256) et en extrait
    un vecteur 768-D. En production, remplacez par vos vrais patches GeoTIFF.
    """
    print("\n" + "=" * 60)
    print("VOIE 2 : TorchGeo natif (DOFA / ViT-B/16)")
    print("=" * 60)

    try:
        import torch
        import numpy as np
    except ImportError:
        print("  [SKIP] PyTorch non installé.")
        return

    client = ClayClient(
        use_torchgeo=True,
        torchgeo_backbone="dofa",   # ou "resnet18"
    )

    print("  → Chargement du modèle DOFA (TorchGeo, poids mis en cache HF)…")
    try:
        client.load_model(
            wavelengths=[0.49, 0.56, 0.66]  # Sentinel-2 B2/B3/B4
        )
        print(f"  → Backend : {client._backend}")
    except Exception as exc:
        print(f"  [ATTENTION] Chargement modèle échoué : {exc}")
        return

    # Patch synthétique Sentinel-2 RGB (1 image, 3 bandes, 256×256)
    # En production : chargez votre GeoTIFF via rasterio
    patch = np.random.randint(0, 3000, size=(1, 3, 256, 256), dtype=np.int16).astype(np.float32)
    patch /= 10_000.0  # Scale DN → réflectance [0, 1]

    print(f"  → Extraction embeddings sur patch {patch.shape}…")
    result = client.extract_embeddings(
        patch,
        wavelengths=[0.49, 0.56, 0.66],
    )
    print(f"  → Embedding shape : {result['shape']}")

    # PCA vers 3 composantes
    pca = client.apply_pca(result["embeddings"], n_components=3)
    print(f"  → PCA variance expliquée : "
          f"{[f'{v:.1%}' for v in pca['explained_variance_ratio']]}")


# ===========================================================================
# 3. Clustering KMeans sur des embeddings multi-patches
# ===========================================================================

def demo_clustering() -> None:
    """Segmentation non-supervisée via KMeans sur des embeddings Clay.

    Simule 200 patches d'embeddings 768-D et les regroupe en 6 clusters
    correspondant aux classes de terrain (forêt, eau, mine, etc.).
    """
    print("\n" + "=" * 60)
    print("VOIE 3 : Clustering KMeans des embeddings")
    print("=" * 60)

    try:
        import numpy as np
    except ImportError:
        print("  [SKIP] NumPy non installé.")
        return

    client = ClayClient(use_torchgeo=False)

    # Simulation : 200 patches, 768-D (remplacez par vos vrais embeddings)
    np.random.seed(42)
    fake_embeddings = np.random.randn(200, 768).astype(np.float32)

    print("  → Clustering KMeans (6 clusters)…")
    cluster_result = client.cluster_embeddings(fake_embeddings, n_clusters=6)

    labels = cluster_result["labels"]
    inertia = cluster_result["inertia"]
    for k in range(6):
        count = (labels == k).sum()
        print(f"     Cluster {k} : {count:3d} patches")
    print(f"  → Inertie KMeans : {inertia:.2f}")

    # PCA 2D pour visualisation
    pca_2d = client.apply_pca(fake_embeddings, n_components=2, normalize=False)
    print(f"  → PCA 2D variance expliquée : "
          f"{[f'{v:.1%}' for v in pca_2d['explained_variance_ratio']]}")


# ===========================================================================
# 4. Recherche de similarité cosinus
# ===========================================================================

def demo_similarity_search() -> None:
    """Recherche les 5 patches les plus similaires à un patch requête."""
    print("\n" + "=" * 60)
    print("VOIE 4 : Recherche de similarité cosinus")
    print("=" * 60)

    try:
        import numpy as np
    except ImportError:
        print("  [SKIP] NumPy non installé.")
        return

    client = ClayClient(use_torchgeo=False)
    np.random.seed(0)

    query = np.random.randn(768).astype(np.float32)       # Vecteur requête
    candidates = np.random.randn(100, 768).astype(np.float32)  # 100 patches

    result = client.similarity_search(query, candidates, top_k=5)
    print("  → Top 5 patches similaires :")
    for rank, (idx, score) in enumerate(zip(result["indices"], result["scores"])):
        print(f"     #{rank+1}  patch_idx={idx:3d}  score cosinus={score:.4f}")


# ===========================================================================
# 5. Carte spatiale PCA depuis GeoTIFF
# ===========================================================================

def demo_spatial_pca_map(tif_path: str | None = None) -> None:
    """Génère une carte PCA RGB depuis un GeoTIFF multi-bandes.

    Si ``tif_path`` est None, un GeoTIFF synthétique est créé pour la démo.
    En production, passez votre fichier Sentinel-2 ou drone.
    """
    print("\n" + "=" * 60)
    print("VOIE 5 : Carte spatiale PCA depuis GeoTIFF")
    print("=" * 60)

    try:
        import numpy as np
        import rasterio
        from rasterio.transform import from_bounds
    except ImportError:
        print("  [SKIP] rasterio ou numpy non installé.")
        return

    # Crée un GeoTIFF synthétique si aucun fichier fourni
    if tif_path is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)
        tif_path = tmp.name
        tmp.close()

        data = (np.random.randint(200, 3000, (4, 64, 64), dtype=np.uint16))
        profile = {
            "driver": "GTiff", "dtype": "uint16",
            "count": 4, "height": 64, "width": 64,
            "crs": "EPSG:4326",
            "transform": from_bounds(29.0, -2.8, 29.5, -2.3, 64, 64),
        }
        with rasterio.open(tif_path, "w", **profile) as dst:
            dst.write(data)
        print(f"  → GeoTIFF synthétique créé : {tif_path}")

    client = ClayClient(use_torchgeo=False)  # Pas de modèle : fallback spectral

    out_tif = tif_path.replace(".tif", "_pca_rgb.tif")
    print(f"  → Génération carte PCA RGB (patch_size=8, stride=4)…")

    result = client.generate_spatial_pca_map(
        tif_path,
        output_rgb_tif=out_tif,
        n_components=3,
        patch_size=8,
        stride=4,
    )
    print(f"  → Patches analysés : {result['n_patches']}")
    print(f"  → Variance expliquée : "
          f"{[f'{v:.1%}' for v in result['variance_explained']]}")
    if result["output_path"]:
        print(f"  → GeoTIFF RGB sauvegardé : {result['output_path']}")


# ===========================================================================
# Point d'entrée
# ===========================================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║    GeoCongoAI — Clay Foundation Model + TorchGeo Demo   ║")
    print("╚══════════════════════════════════════════════════════════╝")

    demo_precomputed_embeddings()
    demo_torchgeo_embeddings()
    demo_clustering()
    demo_similarity_search()
    demo_spatial_pca_map()

    print("\n✓ Démo terminée.")
