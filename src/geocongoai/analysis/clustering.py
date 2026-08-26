"""Moteur de clustering spatial 3D (DBSCAN) pour les datasets géologiques.
"""
from typing import List, Dict, Any, Optional
from .geometry3d import compute_drillhole_trajectories, compute_convex_hulls
from .geochemistry import filter_by_grade_threshold, compute_grade_statistics
from ..results.result import GeoResult

try:
    import numpy as np
except ImportError:
    np = None

try:
    from sklearn.cluster import DBSCAN
except ImportError:
    DBSCAN = None


def cluster_drillholes(
    dataset: Any,
    element: str = "cu_pct",
    grade_threshold: float = 0.5,
    eps: float = 25.0,
    min_samples: int = 3,
    **kwargs
) -> GeoResult:
    """Effectue un clustering spatial 3D DBSCAN sur un DrillholeDataset et retourne un GeoResult.

    Args:
        dataset: Instance de DrillholeDataset.
        element: Champ de teneur à analyser (ex: 'cu_pct').
        grade_threshold: Seuil minimal de coupure géochimique.
        eps: Rayon de recherche DBSCAN (en mètres).
        min_samples: Nombre minimum de points par cluster.

    Returns:
        Objet GeoResult enrichi des points, des clusters, des enveloppes 3D et des métadonnées.
    """
    collars = getattr(dataset, "collars", [])
    assays = getattr(dataset, "assays", [])

    # 1. Calcul des coordonnées 3D (X, Y, Z) des intervalles
    points_3d = compute_drillhole_trajectories(collars, assays)

    # 2. Filtrage géochimique selon le seuil
    filtered_points = filter_by_grade_threshold(points_3d, element=element, threshold=grade_threshold)

    # 3. Clustering spatial DBSCAN 3D
    clusters: Dict[int, List[Dict[str, Any]]] = {}
    if filtered_points and np is not None and DBSCAN is not None:
        coords = np.array([[p["x"], p["y"], p["z"]] for p in filtered_points], dtype=np.float64)
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
        labels = clustering.labels_

        for idx, label in enumerate(labels):
            cid = int(label)
            p_copy = dict(filtered_points[idx])
            p_copy["cluster"] = cid
            if cid != -1:
                if cid not in clusters:
                    clusters[cid] = []
                clusters[cid].append(p_copy)
            filtered_points[idx] = p_copy

    # 4. Génération des enveloppes 3D Convex Hulls
    geometries = compute_convex_hulls(clusters)

    # 5. Calcul des statistiques géochimiques
    stats = compute_grade_statistics(filtered_points, element=element)

    metadata = {
        "analysis_type": "dbscan_3d",
        "element": element,
        "grade_threshold": grade_threshold,
        "eps": eps,
        "min_samples": min_samples,
        "total_intervals": len(points_3d),
        "filtered_intervals": len(filtered_points),
        "cluster_count": len(clusters),
        "crs": kwargs.get("crs", "EPSG:4326")
    }

    return GeoResult(
        points=filtered_points,
        geometries=geometries,
        statistics=stats,
        metadata=metadata,
        collars=collars
    )
