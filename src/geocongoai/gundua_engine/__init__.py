"""Gundua Engine pour GeoCongo AI SDK ('gundua' = découvrir / explorer en Swahili).

Moteur de découverte minière assisté par IA, télédétection, imagerie satellite multi/hyperspectrale
et modèles de fondation géospatiaux distants.
"""
from .analysis import (
    analyse_deterministe,
    analyse_ia_fondation,
    traiter_image_satellite,
    GunduaEngineClient,
    analyse_basee_sur_des_regles,
    analyse_regles,
    DEFAULT_GUNDUA_API_URL,
    VALID_ANALYSIS_TYPES,
)
# Rétrocompatibilité : ré-exportation depuis chimbua_engine.drillholes
from geocongoai.chimbua_engine.drillholes import (
    compute_drillhole_intervals,
    cluster_assay_points,
    generate_cluster_hulls,
    create_3d_drillhole_figure,
    export_3d_visualization,
    analyse_et_visualiser_forages_3d,
)

__all__ = [
    # Analyse basée sur des règles et API distantes (Gundua Core)
    "GunduaEngineClient",
    "analyse_basee_sur_des_regles",
    "analyse_regles",
    "DEFAULT_GUNDUA_API_URL",
    "VALID_ANALYSIS_TYPES",
    # Modèles de fondation et télédétection
    "analyse_deterministe",
    "analyse_ia_fondation",
    "traiter_image_satellite",
    # Alias de rétrocompatibilité (Gundua -> Chimbua Engine)
    "compute_drillhole_intervals",
    "cluster_assay_points",
    "generate_cluster_hulls",
    "create_3d_drillhole_figure",
    "export_3d_visualization",
    "analyse_et_visualiser_forages_3d",
]



