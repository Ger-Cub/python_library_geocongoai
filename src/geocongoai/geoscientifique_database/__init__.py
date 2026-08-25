"""Module geoscientifique_database pour GeoCongo AI SDK.

Remplace l'ancien module 'text' et fournit l'accès à la base de données géoscientifique
et aux Edge Functions RAG et de recherche sémantique / multimodale.
"""
from geocongoai.client import GeoCongoClient
from geocongoai.exceptions import (
    GeoCongoError,
    APIError,
    InvalidParametersError,
    InsufficientBalanceError,
    ServerError,
)
from geocongoai.models import (
    RagSource,
    RagResponse,
    DocumentItem,
    DocumentSearchResponse,
    GeologicalItem,
    GeologicalSearchResponse,
)

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
]
