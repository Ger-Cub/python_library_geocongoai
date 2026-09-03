"""geocongoai package - v0.2.4

SDK officiel Python pour GeoCongo AI : moteur d'analyse géospatiale et géologique,
jeux de données 3D (DrillholeDataset), visualisations interactives et IA géospatiale.
"""
__version__ = "0.2.4"

from .client import GeoCongoClient
from .exceptions import (
    GeoCongoError,
    APIError,
    InvalidParametersError,
    InsufficientBalanceError,
    ServerError,
)
from .models import (
    RagSource,
    RagResponse,
    DocumentItem,
    DocumentSearchResponse,
    GeologicalItem,
    GeologicalSearchResponse,
)

from .datasets import DrillholeDataset, SampleDataset
from .results import GeoResult
from .ia import PrithviClient, AlphaEarthClient, ClayClient


from . import datasets
from . import analysis
from . import results
from . import visualization
from . import geoscientifique_database
from . import vision
from . import ia
from . import gundua_engine

__all__ = [
    # Top-level client & exceptions
    "GeoCongoClient",
    "GeoCongoError",
    "APIError",
    "InvalidParametersError",
    "InsufficientBalanceError",
    "ServerError",
    # Models
    "RagSource",
    "RagResponse",
    "DocumentItem",
    "DocumentSearchResponse",
    "GeologicalItem",
    "GeologicalSearchResponse",
    # Modern Scientific Abstractions
    "DrillholeDataset",
    "SampleDataset",
    "GeoResult",
    "PrithviClient",
    "AlphaEarthClient",
    "ClayClient",

    # Package Modules
    "datasets",
    "analysis",
    "results",
    "visualization",
    "geoscientifique_database",
    "vision",
    "ia",
    "gundua_engine",
]
