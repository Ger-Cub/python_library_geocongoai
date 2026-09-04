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
from . import vision
from . import ia
from . import pekua_engine
from . import gundua_engine
from . import chimbua_engine

# Alias de rétrocompatibilité pour geoscientifique_database
geoscientifique_database = pekua_engine

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

    # Core Engines
    "pekua_engine",
    "gundua_engine",
    "chimbua_engine",

    # Package Utility Modules
    "datasets",
    "analysis",
    "results",
    "visualization",
    "vision",
    "ia",
    "geoscientifique_database",
]

