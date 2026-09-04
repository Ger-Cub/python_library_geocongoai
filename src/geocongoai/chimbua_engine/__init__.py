"""Chimbua Engine pour GeoCongo AI SDK ('chimbua' = extraire / miner en Swahili).

Moteur de modélisation géologique 3D, géostatistique, modèle de blocs, estimation des ressources
et évaluation technico-économique des projets miniers.
"""
from .drillholes import (
    compute_drillhole_intervals,
    cluster_assay_points,
    generate_cluster_hulls,
    create_3d_drillhole_figure,
    export_3d_visualization,
    analyse_et_visualiser_forages_3d,
)

__all__ = [
    "compute_drillhole_intervals",
    "cluster_assay_points",
    "generate_cluster_hulls",
    "create_3d_drillhole_figure",
    "export_3d_visualization",
    "analyse_et_visualiser_forages_3d",
]
