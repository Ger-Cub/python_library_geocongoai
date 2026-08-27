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
from .drillholes import (
    compute_drillhole_intervals,
    cluster_assay_points,
    generate_cluster_hulls,
    create_3d_drillhole_figure,
    export_3d_visualization,
    analyse_et_visualiser_forages_3d,
)

__all__ = [
    # Analyse basée sur des règles (API distante)
    "GunduaEngineClient",
    "analyse_basee_sur_des_regles",
    "analyse_regles",
    "DEFAULT_GUNDUA_API_URL",
    "VALID_ANALYSIS_TYPES",
    # Analyse déterministe locale
    "analyse_deterministe",
    "analyse_ia_fondation",
    "traiter_image_satellite",
    # Forages 3D
    "compute_drillhole_intervals",
    "cluster_assay_points",
    "generate_cluster_hulls",
    "create_3d_drillhole_figure",
    "export_3d_visualization",
    "analyse_et_visualiser_forages_3d",
]


