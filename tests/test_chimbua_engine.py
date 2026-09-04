"""Unit tests pour le module Chimbua Engine dans GeoCongo AI SDK."""
import pytest
from geocongoai import chimbua_engine
from geocongoai.chimbua_engine.drillholes import (
    compute_drillhole_intervals,
    cluster_assay_points,
    generate_cluster_hulls,
    analyse_et_visualiser_forages_3d,
)


def test_chimbua_engine_exports():
    assert hasattr(chimbua_engine, "compute_drillhole_intervals")
    assert hasattr(chimbua_engine, "cluster_assay_points")
    assert hasattr(chimbua_engine, "generate_cluster_hulls")
    assert hasattr(chimbua_engine, "create_3d_drillhole_figure")
    assert hasattr(chimbua_engine, "export_3d_visualization")
    assert hasattr(chimbua_engine, "analyse_et_visualiser_forages_3d")


def test_chimbua_drillholes_functional():
    collars = [
        {"hole_id": "DH_A", "x": 500000.0, "y": 9200000.0, "z": 1200.0, "dip": -90, "azimuth": 0},
    ]
    assays = [
        {"hole_id": "DH_A", "from_m": 0.0, "to_m": 2.0, "cu_pct": 1.45},
    ]
    intervals = compute_drillhole_intervals(collars, assays)
    assert len(intervals) == 1
    assert intervals[0]["hole_id"] == "DH_A"
    assert intervals[0]["z"] == 1199.0  # (0 + 2)/2 = 1m down
