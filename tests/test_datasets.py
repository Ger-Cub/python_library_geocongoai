"""Tests unitaires pour le module geocongoai.datasets (DrillholeDataset).
"""
import pytest
from geocongoai.datasets import DrillholeDataset, SampleDataset
from geocongoai import GeoResult

def test_drillhole_dataset_creation_and_info():
    collars = [
        {"hole_id": "DH01", "x": 500000.0, "y": 9200000.0, "z": 120.0, "dip": -90, "azimuth": 0},
        {"hole_id": "DH02", "x": 500100.0, "y": 9200050.0, "z": 125.0, "dip": -90, "azimuth": 0},
    ]
    assays = [
        {"hole_id": "DH01", "from_m": 0, "to_m": 10, "cu_pct": 1.25, "co_pct": 0.05},
        {"hole_id": "DH01", "from_m": 10, "to_m": 20, "cu_pct": 0.85, "co_pct": 0.03},
        {"hole_id": "DH02", "from_m": 0, "to_m": 10, "cu_pct": 0.40, "co_pct": 0.01},
    ]

    ds = DrillholeDataset(collars=collars, assays=assays)
    info = ds.info()

    assert info["drillhole_count"] == 2
    assert info["assay_count"] == 3
    assert "cu_pct" in info["elements"]
    assert info["bounding_box"]["x_min"] == 500000.0
    assert info["bounding_box"]["x_max"] == 500100.0


def test_drillhole_dataset_analyze():
    collars = [
        {"hole_id": "DH01", "x": 500000.0, "y": 9200000.0, "z": 120.0, "dip": -90, "azimuth": 0},
        {"hole_id": "DH02", "x": 500010.0, "y": 9200005.0, "z": 120.0, "dip": -90, "azimuth": 0},
    ]
    assays = [
        {"hole_id": "DH01", "from_m": 0, "to_m": 10, "cu_pct": 1.25},
        {"hole_id": "DH02", "from_m": 0, "to_m": 10, "cu_pct": 1.10},
    ]

    ds = DrillholeDataset(collars=collars, assays=assays)
    res = ds.analyze(method="dbscan", element="cu_pct", grade_threshold=0.5, eps=50.0, min_samples=1)

    assert isinstance(res, GeoResult)
    assert len(res.points) == 2
    assert res.metadata["element"] == "cu_pct"
    assert res.statistics["count"] == 2
