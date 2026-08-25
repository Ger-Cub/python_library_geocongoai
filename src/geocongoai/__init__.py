"""geocongoai package - v0.1.1

SDK officiel Python pour GeoCongo AI : utilitaires géospatiaux, traitements d'images,
modèles fondations IA et accès à la base de données géoscientifique.
"""
__version__ = "0.1.1"

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

from . import geoscientifique_database
from . import vision
from . import ia
from . import gundua_engine

__all__ = [
    "GeoCongoClient",
    "GeoCongoError",
    "APIError",
    "InvalidParametersError",
    "InsufficientBalanceError",
    "ServerError",
    "RagSource",
    "RagResponse",
    "DocumentItem",
    "DocumentSearchResponse",
    "GeologicalItem",
    "GeologicalSearchResponse",
    "geoscientifique_database",
    "vision",
    "ia",
    "gundua_engine",
]
