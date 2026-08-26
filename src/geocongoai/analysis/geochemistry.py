"""Analyses et traitements géochimiques (filtrage par seuil, statistiques).
"""
from typing import List, Dict, Any, Tuple

def filter_by_grade_threshold(
    points: List[Dict[str, Any]],
    element: str = "cu_pct",
    threshold: float = 0.5
) -> List[Dict[str, Any]]:
    """Filtre les points d'analyse conservant uniquement ceux qui égalent ou dépassent le seuil.

    Args:
        points: Liste de points enrichis (contenant la clé `element`).
        element: Nom du champ de teneur (ex: 'cu_pct').
        threshold: Seuil minimal.

    Returns:
        Liste de points filtrés.
    """
    filtered = []
    for p in points:
        val = p.get(element)
        if val is not None:
            try:
                if float(val) >= threshold:
                    filtered.append(p)
            except (ValueError, TypeError):
                continue
    return filtered


def compute_grade_statistics(points: List[Dict[str, Any]], element: str = "cu_pct") -> Dict[str, Any]:
    """Calcule des statistiques basiques sur un élément géochimique.

    Args:
        points: Liste des points.
        element: Nom de la variable géochimique.

    Returns:
        Dictionnaire avec count, min, max, mean.
    """
    vals = []
    for p in points:
        val = p.get(element)
        if val is not None:
            try:
                vals.append(float(val))
            except (ValueError, TypeError):
                continue

    if not vals:
        return {"count": 0, "min": None, "max": None, "mean": None}

    vals_sorted = sorted(vals)
    n = len(vals_sorted)
    mean_val = sum(vals_sorted) / n

    return {
        "count": n,
        "min": vals_sorted[0],
        "max": vals_sorted[-1],
        "mean": mean_val,
    }
