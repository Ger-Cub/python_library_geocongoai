"""Unit tests pour le module SDK geoscientifique_database de GeoCongo AI."""
import pytest
from unittest.mock import MagicMock, patch

from geocongoai import GeoCongoClient
from geocongoai.geoscientifique_database import GeoCongoClient as DBClient
from geocongoai.exceptions import (
    GeoCongoError,
    InvalidParametersError,
    InsufficientBalanceError,
    ServerError,
)
from geocongoai.models import (
    RagResponse,
    DocumentSearchResponse,
    GeologicalSearchResponse,
)


def test_imports_and_alias():
    assert GeoCongoClient is DBClient


def test_client_init():
    client = GeoCongoClient(api_key="test-key-123")
    assert client.api_key == "test-key-123"
    assert "tjpopbzjzlrrolqdismq.supabase.co" in client.base_url

    with pytest.raises(ValueError):
        GeoCongoClient(api_key="")


@patch("geocongoai.client.requests")
def test_ask_rag_success(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "answer": "Le Katanga possède de riches gisements de cuivre et de cobalt.",
        "sources": [
            {
                "document_id": "doc-001",
                "title": "Géologie du Katanga",
                "author": "Dr. Tshilombo",
                "similarity": 0.92,
            }
        ]
    }
    mock_requests.Session.return_value.post.return_value = mock_response

    client = GeoCongoClient(api_key="dummy-key")
    res = client.ask_rag(
        query="Quel est le potentiel géologique du Katanga ?",
        user_id="123e4567-e89b-12d3-a456-426614174000",
        conversation_id="conv-1",
    )

    assert isinstance(res, RagResponse)
    assert "Katanga" in res.answer
    assert len(res.sources) == 1
    assert res.sources[0].title == "Géologie du Katanga"
    assert res.sources[0].similarity == 0.92


@patch("geocongoai.client.requests")
def test_ask_rag_insufficient_balance(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 402
    mock_response.json.return_value = {"message": "Veuillez recharger votre solde unités."}
    mock_requests.Session.return_value.post.return_value = mock_response

    client = GeoCongoClient(api_key="dummy-key")
    with pytest.raises(InsufficientBalanceError) as exc_info:
        client.ask_rag(query="Test", user_id="user-1")

    assert "recharger votre solde" in str(exc_info.value)
    assert exc_info.value.status_code == 402


@patch("geocongoai.client.requests")
def test_search_documents(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query": "cuivre et cobalt",
        "totalFound": 2,
        "appliedFilters": {"domaine": "Mines", "categorie": "Thèse", "province": "Lualaba"},
        "results": [
            {
                "title": "Étude des gisements de Lualaba",
                "author": "Prof. Kambale",
                "document_url": "https://example.com/doc1.pdf",
                "similarity": 0.88,
                "relevantChunks": ["Extrait relatif au cuivre..."],
            }
        ]
    }
    mock_requests.Session.return_value.post.return_value = mock_response

    client = GeoCongoClient(api_key="dummy-key")
    res = client.search_documents(
        query="cuivre et cobalt",
        domain="Mines",
        category="Thèse",
        province="Lualaba",
    )

    assert isinstance(res, DocumentSearchResponse)
    assert res.total_found == 2
    assert len(res.results) == 1
    assert res.results[0].title == "Étude des gisements de Lualaba"
    assert res.results[0].relevant_chunks == ["Extrait relatif au cuivre..."]


@patch("geocongoai.client.requests")
def test_search_geological(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query": "malachite",
        "type": "rocks",
        "totalFound": 1,
        "results": [
            {
                "item_type": "rock",
                "title": "Échantillon Malachite Haut-Katanga",
                "similarity": 0.95,
                "author": "Musée de Lubumbashi",
            }
        ]
    }
    mock_requests.Session.return_value.post.return_value = mock_response

    client = GeoCongoClient(api_key="dummy-key")
    res = client.search_geological(
        query="malachite et cuivre",
        type="rocks",
        province="Haut-Katanga",
    )

    assert isinstance(res, GeologicalSearchResponse)
    assert res.type == "rocks"
    assert len(res.results) == 1
    assert res.results[0].item_type == "rock"
    assert res.results[0].similarity == 0.95


def test_search_geological_invalid_type():
    client = GeoCongoClient(api_key="dummy-key")
    with pytest.raises(InvalidParametersError):
        client.search_geological(query="test", type="invalid_type")
