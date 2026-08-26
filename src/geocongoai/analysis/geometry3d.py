"""Calculs de géométrie 3D, trajectoires de forages et enveloppes convexes (Convex Hull).
"""
import math
from typing import List, Dict, Any, Optional

try:
    import numpy as np
except ImportError:
    np = None

try:
    from scipy.spatial import ConvexHull
except ImportError:
    ConvexHull = None


def compute_drillhole_trajectories(
    collars: List[Dict[str, Any]],
    assays: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Calcule les coordonnées 3D (X, Y, Z) au milieu de chaque intervalle d'analyse.

    Args:
        collars: Liste de colliers ex: [{"hole_id": "DH01", "x": 500.0, "y": 1000.0, "z": 120.0, "dip": -90, "azimuth": 0}]
        assays: Liste d'analyses ex: [{"hole_id": "DH01", "from_m": 0, "to_m": 10, "cu_pct": 1.25}]

    Returns:
        Liste d'intervalles enrichis avec 'x', 'y', 'z' (point central 3D) et 'mid_depth'.
    """
    collar_dict = {c["hole_id"]: c for c in collars}
    computed_assays = []

    for assay in assays:
        hole_id = assay.get("hole_id")
        if hole_id not in collar_dict:
            continue

        collar = collar_dict[hole_id]
        cx = float(collar.get("x", 0.0))
        cy = float(collar.get("y", 0.0))
        cz = float(collar.get("z", 0.0))
        dip = float(collar.get("dip", -90.0))
        azimuth = float(collar.get("azimuth", 0.0))

        from_m = float(assay.get("from_m", 0.0))
        to_m = float(assay.get("to_m", 0.0))
        mid_depth = (from_m + to_m) / 2.0

        dip_rad = math.radians(abs(dip))
        az_rad = math.radians(azimuth)

        horizontal_dist = mid_depth * math.cos(dip_rad)
        dz = - mid_depth * math.sin(dip_rad) if dip < 0 else mid_depth * math.sin(dip_rad)

        dx = horizontal_dist * math.sin(az_rad)
        dy = horizontal_dist * math.cos(az_rad)

        x = cx + dx
        y = cy + dy
        z = cz + dz

        item = dict(assay)
        item.update({"x": x, "y": y, "z": z, "mid_depth": mid_depth})
        computed_assays.append(item)

    return computed_assays


def compute_convex_hulls(clusters: Dict[int, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Génère la géométrie 3D Convex Hull (enveloppe convexe) pour chaque cluster.

    Args:
        clusters: Dictionnaire {cluster_id: [points]}

    Returns:
        Liste de dictionnaires représentant les maillages 3D.
    """
    if ConvexHull is None or np is None:
        return []

    geometries = []
    for cid, points in clusters.items():
        if len(points) < 4:
            continue

        pts = np.array([[p["x"], p["y"], p["z"]] for p in points], dtype=np.float64)
        try:
            hull = ConvexHull(pts)
            i_idx = hull.simplices[:, 0].tolist()
            j_idx = hull.simplices[:, 1].tolist()
            k_idx = hull.simplices[:, 2].tolist()

            geometries.append({
                "cluster_id": cid,
                "type": "convex_hull",
                "volume_m3": float(hull.volume),
                "area_m2": float(hull.area),
                "num_vertices": len(pts),
                "vertices": {
                    "x": pts[:, 0].tolist(),
                    "y": pts[:, 1].tolist(),
                    "z": pts[:, 2].tolist(),
                },
                "simplices": {
                    "i": i_idx,
                    "j": j_idx,
                    "k": k_idx,
                }
            })
        except Exception:
            continue

    return geometries
