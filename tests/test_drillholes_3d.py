"""Tests unitaires pour le module 3D drillholes (geocongoai.gundua_engine.drillholes)."""
import os
import pytest
from geocongoai.gundua_engine import (
    compute_drillhole_intervals,
    cluster_assay_points,
    generate_cluster_hulls,
    create_3d_drillhole_figure,
    export_3d_visualization,
    analyse_et_visualiser_forages_3d,
)


@pytest.fixture
def sample_drillhole_data():
    collars = [
        {"hole_id": "DH_01", "x": 100.0, "y": 200.0, "z": 50.0, "dip": -90, "azimuth": 0},
        {"hole_id": "DH_02", "x": 110.0, "y": 205.0, "z": 52.0, "dip": -90, "azimuth": 0},
        {"hole_id": "DH_03", "x": 105.0, "y": 210.0, "z": 48.0, "dip": -90, "azimuth": 0},
        {"hole_id": "DH_04", "x": 115.0, "y": 215.0, "z": 49.0, "dip": -90, "azimuth": 0},
    ]

    assays = []
    # Cluster 1 : profondeur 10-30m sur DH_01, DH_02, DH_03, DH_04 avec forte teneur Cu
    for hole_id in ["DH_01", "DH_02", "DH_03", "DH_04"]:
        for depth in range(0, 50, 5):
            cu_pct = 2.5 if 10 <= depth <= 30 else 0.1
            assays.append({
                "hole_id": hole_id,
                "from_m": depth,
                "to_m": depth + 5,
                "cu_pct": cu_pct
            })

    return collars, assays


def test_compute_drillhole_intervals(sample_drillhole_data):
    collars, assays = sample_drillhole_data
    pts = compute_drillhole_intervals(collars, assays)

    assert len(pts) == len(assays)
    first_pt = pts[0]
    assert "x" in first_pt and "y" in first_pt and "z" in first_pt
    assert first_pt["x"] == 100.0
    assert first_pt["y"] == 200.0
    assert first_pt["z"] == 47.5  # 50 - 2.5m (vertical)


def test_cluster_assay_points(sample_drillhole_data):
    collars, assays = sample_drillhole_data
    pts = compute_drillhole_intervals(collars, assays)

    res = cluster_assay_points(pts, grade_field="cu_pct", grade_threshold=1.0, eps=25.0, min_samples=3)

    assert res["status"] == "success"
    assert res["cluster_count"] >= 1
    clusters = res["clusters"]
    assert 0 in clusters
    assert len(clusters[0]) >= 4


def test_generate_cluster_hulls(sample_drillhole_data):
    collars, assays = sample_drillhole_data
    pts = compute_drillhole_intervals(collars, assays)
    res = cluster_assay_points(pts, grade_field="cu_pct", grade_threshold=1.0, eps=25.0, min_samples=3)
    clusters = res["clusters"]

    hulls = generate_cluster_hulls(clusters)
    assert 0 in hulls
    hull_0 = hulls[0]
    assert "x" in hull_0 and "i" in hull_0 and "volume" in hull_0
    assert hull_0["volume"] > 0.0


def test_full_3d_pipeline(sample_drillhole_data, tmp_path):
    collars, assays = sample_drillhole_data
    output_html = str(tmp_path / "drillhole_3d.html")

    result = analyse_et_visualiser_forages_3d(
        collars=collars,
        assays=assays,
        grade_field="cu_pct",
        grade_threshold=1.0,
        eps=25.0,
        min_samples=3,
        output_html_path=output_html,
        title="Test GeoCongo AI 3D"
    )

    assert result["status"] == "success"
    assert result["figure"] is not None
    assert result["html_code"] is not None
    assert os.path.exists(output_html)
    assert os.path.getsize(output_html) > 1000
