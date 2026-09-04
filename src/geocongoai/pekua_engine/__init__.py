"""Pekua Engine pour GeoCongo AI SDK ('pekua' = fouiller / rechercher dans les livres en Swahili).

Moteur de recherche géoscientifique, d'extraction documentaire et d'assistance RAG.
Accès aux Edge Functions Supabase (/rag-agent, /search-documents, /search-geological)
et à la recherche vectorielle pgvector 1536D.
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
