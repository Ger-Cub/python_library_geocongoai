"""Tests unitaires pour ClayClient (geocongoai.ia.ClayClient)."""
import pytest
import numpy as np
from geocongoai.ia import ClayClient


def test_clay_client_init():
    client = ClayClient(model_name="made-with-clay/Clay", use_torchgeo=True)
    assert client.model_name == "made-with-clay/Clay"
    assert client.use_torchgeo is True
    assert client.model is None


def test_clay_pca_reduction_2d():
    client = ClayClient()
    # Simuler des embeddings de dimension 64 (100 échantillons)
    np.random.seed(42)
    fake_embeddings = np.random.randn(100, 64)

    res = client.apply_pca(fake_embeddings, n_components=3, normalize=True)
    assert "pca_features" in res
    assert "normalized_components" in res
    assert res["pca_features"].shape == (100, 3)
    assert res["normalized_components"].shape == (100, 3)
    assert res["normalized_components"].dtype == np.uint8
    assert len(res["explained_variance_ratio"]) == 3


def test_clay_pca_reduction_spatial_3d():
    client = ClayClient()
    # Simuler une grille spatiale (H=20, W=20, D=32)
    np.random.seed(42)
    fake_spatial = np.random.randn(20, 20, 32)

    res = client.apply_pca(fake_spatial, n_components=3, normalize=True)
    assert res["rgb_image"] is not None
    assert res["rgb_image"].shape == (20, 20, 3)
    assert res["rgb_image"].dtype == np.uint8


def test_clay_extract_embeddings_fallback():
    client = ClayClient()
    fake_patch = np.zeros((3, 32, 32), dtype=np.float32)

    # Assure qu'en mode fallback (sans télécharger de checkpoint lourd), extract_embeddings retourne une structure valide
    res = client.extract_embeddings(fake_patch)
    assert "embeddings" in res
    assert res["model"] == "made-with-clay/Clay"
