"""Unit tests pour le module SDK Pekua Engine de GeoCongo AI."""
import os
import pytest
from unittest.mock import MagicMock, patch

from geocongoai import GeoCongoClient
from geocongoai.pekua_engine import GeoCongoClient as PekuaClient
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
    assert GeoCongoClient is PekuaClient
    assert GeoCongoClient is DBClient


def test_client_init():
    client = GeoCongoClient(api_key="gcg_live_test123")
    assert client.api_key == "gcg_live_test123"
    assert "tjpopbzjzlrrolqdismq.supabase.co" in client.base_url

    # Exception si aucune clé ni user_id
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            GeoCongoClient()
        assert "Authentification requise" in str(exc_info.value)
        assert "GEOCONGOAI_API_KEY" in str(exc_info.value)


def test_client_init_env_var():
    with patch.dict(os.environ, {"GEOCONGOAI_API_KEY": "gcg_live_envkey"}, clear=True):
        client = GeoCongoClient()
        assert client.api_key == "gcg_live_envkey"


def test_client_init_legacy_user_id():
    with patch.dict(os.environ, {}, clear=True):
        client = GeoCongoClient(user_id="user-uuid-1234")
        assert client._user_id == "user-uuid-1234"
        assert client.api_key is None


@patch("geocongoai.client.requests")
def test_ask_rag_success_with_api_key_without_user_id(mock_requests):
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
    mock_session = MagicMock()
    mock_session.post.return_value = mock_response
    mock_requests.Session.return_value = mock_session

    client = GeoCongoClient(api_key="gcg_live_testkey")
    res = client.ask_rag(
        query="Quel est le potentiel géologique du Katanga ?",
        conversation_id="conv-1",
    )

    assert isinstance(res, RagResponse)
    assert "Katanga" in res.answer
    assert len(res.sources) == 1
    assert res.sources[0].title == "Géologie du Katanga"

    # Vérifier l'appel session.post et les headers inclus
    mock_session.post.assert_called_once()
    call_args, call_kwargs = mock_session.post.call_args
    headers = call_kwargs.get("headers", {})
    assert headers.get("Authorization") == "Bearer gcg_live_testkey"
    assert headers.get("x-geocongo-api-key") == "gcg_live_testkey"

    # Vérifier que userId n'est pas requis dans le payload si non transmis
    payload = call_kwargs.get("json", {})
    assert payload.get("query") == "Quel est le potentiel géologique du Katanga ?"
    assert payload.get("conversationId") == "conv-1"
    assert "userId" not in payload


@patch("geocongoai.client.requests")
def test_ask_rag_insufficient_balance(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 402
    mock_response.json.return_value = {"message": "Veuillez recharger votre solde unités."}
    mock_session = MagicMock()
    mock_session.post.return_value = mock_response
    mock_requests.Session.return_value = mock_session

    client = GeoCongoClient(api_key="dummy-key")
    with pytest.raises(InsufficientBalanceError) as exc_info:
        client.ask_rag(query="Test")

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
    mock_session = MagicMock()
    mock_session.post.return_value = mock_response
    mock_requests.Session.return_value = mock_session

    client = GeoCongoClient(api_key="gcg_live_key")
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

    # Vérifier les headers
    call_args, call_kwargs = mock_session.post.call_args
    headers = call_kwargs.get("headers", {})
    assert headers.get("x-geocongo-api-key") == "gcg_live_key"


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
    mock_session = MagicMock()
    mock_session.post.return_value = mock_response
    mock_requests.Session.return_value = mock_session

    client = GeoCongoClient(api_key="gcg_live_key")
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

