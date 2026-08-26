"""Tests unitaires pour les renderers de visualisation 3D (Plotly, HTML).
"""
import os
import pytest
from geocongoai.results import GeoResult
from geocongoai.visualization import PlotlyRenderer, HTMLRenderer


def test_plotly_renderer_build_figure():
    res = GeoResult(
        points=[{"x": 100, "y": 200, "z": 300, "cu_pct": 2.5, "hole_id": "DH_01"}],
        collars=[{"hole_id": "DH_01", "x": 100, "y": 200, "z": 300}],
        metadata={"title": "Test 3D Title", "element": "cu_pct"}
    )
    renderer = PlotlyRenderer(res)
    fig = renderer.build_figure()

    assert fig is not None
    assert "Test 3D Title" in fig.layout.title.text
    # Verify circle markers in traces
    assert len(fig.data) >= 2
    assert fig.data[0].marker.symbol == "circle"
    assert fig.data[1].marker.symbol == "circle"


def test_html_renderer_render(tmp_path):
    res = GeoResult(
        points=[{"x": 100, "y": 200, "z": 300, "cu_pct": 2.5, "hole_id": "DH_01"}],
        collars=[{"hole_id": "DH_01", "x": 100, "y": 200, "z": 300}],
        metadata={"title": "Test HTML Export", "element": "cu_pct"}
    )
    out_file = tmp_path / "test_export.html"
    renderer = HTMLRenderer(res)
    html_code = renderer.render(str(out_file))

    assert os.path.exists(out_file)
    assert "data:image/png;base64" in html_code or "GeoCongo AI" in html_code
    assert "LÉGENDE" in html_code
