"""Module `gundua_engine.drillholes` pour l'analyse spatiale 3D des forages géologiques.

Conserve la compatibilité descendante 100% avec les versions précédentes en déléguant
aux nouveaux modules `geocongoai.datasets`, `geocongoai.analysis`, `geocongoai.results` et `geocongoai.visualization`.
"""
from typing import List, Dict, Any, Optional
from ..datasets.drillholes import DrillholeDataset
from ..analysis.geometry3d import compute_drillhole_trajectories as compute_drillhole_intervals, compute_convex_hulls
from ..analysis.clustering import cluster_drillholes
from ..visualization.plotly import PlotlyRenderer
from ..visualization.html import HTMLRenderer

try:
    import plotly.graph_objects as go
except ImportError:
    go = None


def cluster_assay_points(
    interval_points: List[Dict[str, Any]],
    grade_field: str = "cu_pct",
    grade_threshold: float = 0.5,
    eps: float = 25.0,
    min_samples: int = 3
) -> Dict[str, Any]:
    """Adaptateur de rétrocompatibilité pour cluster_assay_points."""
    dummy_dataset = DrillholeDataset(collars=[], assays=[])
    # For backwards compatibility where points are pre-computed
    from ..analysis.geochemistry import filter_by_grade_threshold
    try:
        import numpy as np
        from sklearn.cluster import DBSCAN
    except ImportError:
        return {"status": "warning", "message": "numpy et scikit-learn requis.", "clusters": {}}

    filtered = filter_by_grade_threshold(interval_points, element=grade_field, threshold=grade_threshold)
    if not filtered:
        return {"status": "success", "clusters": {}, "filtered_count": 0}

    coords = np.array([[p["x"], p["y"], p["z"]] for p in filtered], dtype=np.float64)
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
    
    clusters: Dict[int, List[Dict[str, Any]]] = {}
    for idx, label in enumerate(clustering.labels_):
        cid = int(label)
        if cid == -1:
            continue
        if cid not in clusters:
            clusters[cid] = []
        p_copy = dict(filtered[idx])
        p_copy["cluster_id"] = cid
        clusters[cid].append(p_copy)

    return {
        "status": "success",
        "grade_threshold": grade_threshold,
        "eps": eps,
        "min_samples": min_samples,
        "total_filtered_points": len(filtered),
        "cluster_count": len(clusters),
        "clusters": clusters
    }


def generate_cluster_hulls(clusters: Dict[int, List[Dict[str, Any]]]) -> Dict[int, Dict[str, Any]]:
    """Adaptateur de rétrocompatibilité pour generate_cluster_hulls."""
    raw_hulls = compute_convex_hulls(clusters)
    res_dict = {}
    for h in raw_hulls:
        cid = h.get("cluster_id")
        vertices = h.get("vertices", {})
        simplices = h.get("simplices", {})
        res_dict[cid] = {
            "x": vertices.get("x", []),
            "y": vertices.get("y", []),
            "z": vertices.get("z", []),
            "i": simplices.get("i", []),
            "j": simplices.get("j", []),
            "k": simplices.get("k", []),
            "volume": h.get("volume_m3", 0.0),
            "area": h.get("area_m2", 0.0)
        }
    return res_dict


def create_3d_drillhole_figure(
    collars: List[Dict[str, Any]],
    interval_points: List[Dict[str, Any]],
    grade_field: str = "cu_pct",
    clusters: Optional[Dict[int, List[Dict[str, Any]]]] = None,
    hulls: Optional[Dict[int, Dict[str, Any]]] = None,
    title: str = "3D Geological Drillhole Viewer - GeoCongo AI"
) -> Any:
    """Adaptateur de rétrocompatibilité pour la génération de figure Plotly."""
    from ..results.result import GeoResult
    geom_list = []
    if hulls:
        for cid, h in hulls.items():
            geom_list.append({
                "cluster_id": cid,
                "vertices": {"x": h.get("x"), "y": h.get("y"), "z": h.get("z")},
                "simplices": {"i": h.get("i"), "j": h.get("j"), "k": h.get("k")},
                "volume_m3": h.get("volume", 0.0)
            })

    geo_res = GeoResult(
        points=interval_points,
        geometries=geom_list,
        collars=collars,
        metadata={"element": grade_field, "title": title}
    )
    renderer = PlotlyRenderer(geo_res)
    return renderer.build_figure(title=title)


def export_3d_visualization(fig: Any, output_html_path: Optional[str] = None) -> str:
    """Adaptateur de rétrocompatibilité pour export HTML."""
    if go is None:
        raise ImportError("plotly est requis pour exporter la visualisation 3D.")
    html_str = fig.to_html(full_html=True, include_plotlyjs='cdn')
    if output_html_path:
        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write(html_str)
    return html_str


def analyse_et_visualiser_forages_3d(
    collars: List[Dict[str, Any]],
    assays: List[Dict[str, Any]],
    grade_field: str = "cu_pct",
    grade_threshold: float = 0.5,
    eps: float = 25.0,
    min_samples: int = 3,
    output_html_path: Optional[str] = None,
    title: str = "GeoCongo AI - Visualisation 3D et Clustering Spatial DBSCAN"
) -> Dict[str, Any]:
    """Pipeline complet 3D utilisant DrillholeDataset et GeoResult."""
    dataset = DrillholeDataset(collars=collars, assays=assays)
    geo_result = dataset.analyze(
        method="dbscan",
        element=grade_field,
        grade_threshold=grade_threshold,
        eps=eps,
        min_samples=min_samples,
        title=title
    )

    fig = None
    html_code = None
    if go is not None:
        fig = geo_result.show_3d(title=title)
        html_code = geo_result.to_html(output_path=output_html_path)

    return {
        "status": "success",
        "total_intervals": len(geo_result.points),
        "clustering_summary": geo_result.metadata,
        "hulls": geo_result.geometries,
        "figure": fig,
        "html_code": html_code,
        "output_html_path": output_html_path,
        "geo_result": geo_result
    }
