"""Modèles de données (Dataclasses) pour le SDK GeoCongo AI."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class RagSource:
    """Source documentaire citée par l'agent RAG."""
    document_id: str
    title: str
    author: Optional[str] = None
    similarity: Optional[float] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RagSource":
        return cls(
            document_id=str(data.get("document_id") or data.get("documentId") or data.get("id") or ""),
            title=str(data.get("title") or data.get("titre") or "Sans titre"),
            author=data.get("author") or data.get("auteur"),
            similarity=float(data["similarity"]) if data.get("similarity") is not None else None,
            raw_data=data,
        )


@dataclass
class RagResponse:
    """Réponse générée par l'agent RAG."""
    answer: str
    sources: List[RagSource] = field(default_factory=list)
    raw_response: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RagResponse":
        sources_raw = data.get("sources") or []
        sources = [RagSource.from_dict(s) for s in sources_raw if isinstance(s, dict)]
        return cls(
            answer=str(data.get("answer") or data.get("response") or ""),
            sources=sources,
            raw_response=data,
        )


@dataclass
class DocumentItem:
    """Document géoscientifique retourné par la recherche sémantique."""
    title: str
    author: Optional[str] = None
    document_url: Optional[str] = None
    similarity: Optional[float] = None
    relevant_chunks: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentItem":
        chunks = data.get("relevantChunks") or data.get("relevant_chunks") or []
        if not isinstance(chunks, list):
            chunks = [str(chunks)]
        return cls(
            title=str(data.get("title") or data.get("titre") or "Sans titre"),
            author=data.get("author") or data.get("auteur"),
            document_url=data.get("document_url") or data.get("documentUrl") or data.get("url"),
            similarity=float(data["similarity"]) if data.get("similarity") is not None else None,
            relevant_chunks=[str(c) for c in chunks],
            raw_data=data,
        )


@dataclass
class DocumentSearchResponse:
    """Résultats de la recherche documentaire."""
    results: List[DocumentItem] = field(default_factory=list)
    total_found: int = 0
    query: str = ""
    applied_filters: Dict[str, Any] = field(default_factory=dict)
    raw_response: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentSearchResponse":
        res_raw = data.get("results") or []
        items = [DocumentItem.from_dict(r) for r in res_raw if isinstance(r, dict)]
        return cls(
            results=items,
            total_found=int(data.get("totalFound") or data.get("total_found") or len(items)),
            query=str(data.get("query") or ""),
            applied_filters=data.get("appliedFilters") or data.get("applied_filters") or {},
            raw_response=data,
        )


@dataclass
class GeologicalItem:
    """Élément géologique multimodal (roche, carte, jeu de données ou document)."""
    item_type: str
    title: str
    similarity: Optional[float] = None
    author: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeologicalItem":
        return cls(
            item_type=str(data.get("item_type") or data.get("itemType") or data.get("type") or "unknown"),
            title=str(data.get("title") or data.get("titre") or data.get("name") or "Sans titre"),
            similarity=float(data["similarity"]) if data.get("similarity") is not None else None,
            author=data.get("author") or data.get("auteur"),
            description=data.get("description"),
            url=data.get("url") or data.get("document_url"),
            raw_data=data,
        )


@dataclass
class GeologicalSearchResponse:
    """Résultats de la recherche géologique multimodale."""
    results: List[GeologicalItem] = field(default_factory=list)
    total_found: int = 0
    query: str = ""
    type: str = "all"
    raw_response: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeologicalSearchResponse":
        res_raw = data.get("results") or []
        items = [GeologicalItem.from_dict(r) for r in res_raw if isinstance(r, dict)]
        return cls(
            results=items,
            total_found=int(data.get("totalFound") or data.get("total_found") or len(items)),
            query=str(data.get("query") or ""),
            type=str(data.get("type") or "all"),
            raw_response=data,
        )


__all__ = [
    "RagSource",
    "RagResponse",
    "DocumentItem",
    "DocumentSearchResponse",
    "GeologicalItem",
    "GeologicalSearchResponse",
]
