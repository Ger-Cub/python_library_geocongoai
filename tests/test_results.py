"""Tests unitaires pour l'objet standard GeoResult et ses sérialiseurs.
"""
import json
from geocongoai.results import GeoResult

def test_geo_result_exports():
    points = [
        {"hole_id": "DH01", "x": 100.0, "y": 200.0, "z": -10.0, "cu_pct": 1.5, "cluster": 0},
        {"hole_id": "DH02", "x": 105.0, "y": 205.0, "z": -12.0, "cu_pct": 2.1, "cluster": 0},
    ]
    geometries = [
        {"cluster_id": 0, "type": "convex_hull", "volume_m3": 1500.0}
    ]
    stats = {"count": 2, "min": 1.5, "max": 2.1, "mean": 1.8}
    meta = {"element": "cu_pct", "crs": "EPSG:32735"}

    res = GeoResult(points=points, geometries=geometries, statistics=stats, metadata=meta)

    # 1. to_dict
    d = res.to_dict()
    assert d["type"] == "GeoCongoResult"
    assert d["version"] == "1.0"
    assert d["crs"] == "EPSG:32735"
    assert len(d["points"]) == 2

    # 2. to_json
    json_str = res.to_json()
    parsed = json.loads(json_str)
    assert parsed["type"] == "GeoCongoResult"

    # 3. to_geojson
    geojson = res.to_geojson()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 2
    assert geojson["features"][0]["geometry"]["coordinates"] == [100.0, 200.0, -10.0]
