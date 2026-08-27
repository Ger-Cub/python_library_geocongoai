"""Tests unitaires pour le client API Gundua Engine (analyse basée sur des règles)."""
import re
import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from geocongoai.gundua_engine import (
    GunduaEngineClient,
    analyse_basee_sur_des_regles,
    analyse_regles,
    VALID_ANALYSIS_TYPES,
    DEFAULT_GUNDUA_API_URL,
)
from geocongoai.gundua_engine.analysis import _default_datetime_range, DEFAULT_DATETIME_MONTHS
from geocongoai.exceptions import InvalidParametersError, GeoCongoError, ServerError


# ─── Fixtures ────────────────────────────────────────────────────────────────

SAMPLE_BBOX = [28.5, -11.5, 28.6, -11.4]
SAMPLE_DATETIME = "2023-06-01/2023-06-30"

GREENFIELD_RESPONSE = {
    "analysis_type": "greenfield",
    "status": "completed",
    "bbox": SAMPLE_BBOX,
    "result": {"potential": 0.78, "high_potential_area_km2": 4.2},
}

ILLEGAL_MINING_RESPONSE = {
    "analysis_type": "illegal_mining",
    "status": "completed",
    "result": {"risk_level": "high", "bare_soil_ratio": 0.45},
}


# ─── Tests imports et constantes ─────────────────────────────────────────────

def test_valid_analysis_types():
    assert VALID_ANALYSIS_TYPES == {
        "greenfield", "illegal_mining", "lineaments", "landcover", "landslide"
    }


def test_default_api_url():
    assert DEFAULT_GUNDUA_API_URL == "https://geocongo-solafune-greenfield-api.geocongoai.com"


def test_aliases():
    assert analyse_regles is analyse_basee_sur_des_regles


# ─── Tests auto-datetime ──────────────────────────────────────────────────────

def test_default_datetime_range_format():
    """La plage générée doit respecter le format YYYY-MM-DD/YYYY-MM-DD."""
    dt = _default_datetime_range()
    assert re.match(r"\d{4}-\d{2}-\d{2}/\d{4}-\d{2}-\d{2}", dt), f"Format invalide: {dt}"


def test_default_datetime_range_covers_3_months():
    """La plage par défaut (3 mois) doit couvrir environ 90 jours."""
    dt = _default_datetime_range(months=3)
    start_str, end_str = dt.split("/")
    start = date.fromisoformat(start_str)
    end = date.fromisoformat(end_str)
    delta_days = (end - start).days
    assert 85 <= delta_days <= 95, f"Durée attendue ~90 jours, obtenu: {delta_days}"


def test_default_datetime_range_end_is_today():
    """La date de fin doit être la date d'aujourd'hui."""
    dt = _default_datetime_range()
    _, end_str = dt.split("/")
    assert end_str == date.today().isoformat()


def test_default_datetime_range_custom_months():
    """months=6 doit générer ~180 jours."""
    dt = _default_datetime_range(months=6)
    start_str, end_str = dt.split("/")
    delta = (date.fromisoformat(end_str) - date.fromisoformat(start_str)).days
    assert 175 <= delta <= 185


def test_default_datetime_months_constant():
    assert DEFAULT_DATETIME_MONTHS == 3


# ─── Tests GunduaEngineClient ─────────────────────────────────────────────────

def test_client_init_defaults():
    client = GunduaEngineClient()
    assert client.base_url == "https://geocongo-solafune-greenfield-api.geocongoai.com"
    assert client.timeout == 60.0


def test_client_init_custom():
    client = GunduaEngineClient(base_url="https://custom-api.example.com/", timeout=30.0)
    assert client.base_url == "https://custom-api.example.com"  # trailing slash stripped
    assert client.timeout == 30.0


def test_analyze_invalid_type_raises():
    client = GunduaEngineClient()
    with pytest.raises(InvalidParametersError) as exc_info:
        client.analyze("wrong_type", bbox=SAMPLE_BBOX)
    assert "wrong_type" in str(exc_info.value)
    assert "disponibles" in str(exc_info.value)


def test_analyze_missing_analysis_type_raises():
    client = GunduaEngineClient()
    with pytest.raises(InvalidParametersError) as exc_info:
        client.analyze({"bbox": SAMPLE_BBOX})  # pas d'analysis_type
    assert "analysis_type" in str(exc_info.value)


def test_analyze_invalid_bbox_raises():
    client = GunduaEngineClient()
    with pytest.raises(InvalidParametersError) as exc_info:
        client.analyze("greenfield", bbox=[28.5, -11.5])  # bbox tronquée
    assert "bbox" in str(exc_info.value)


def test_analyze_invalid_payload_type_raises():
    client = GunduaEngineClient()
    with pytest.raises(InvalidParametersError):
        client.analyze(123)  # type invalide


@patch("geocongoai.gundua_engine.analysis.requests")
def test_analyze_greenfield_dict_payload(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = GREENFIELD_RESPONSE
    mock_requests.Session.return_value.post.return_value = mock_response

    client = GunduaEngineClient()
    result = client.analyze({
        "analysis_type": "greenfield",
        "bbox": SAMPLE_BBOX,
        "datetime": SAMPLE_DATETIME,
    })

    assert result["analysis_type"] == "greenfield"
    assert result["result"]["potential"] == 0.78
    mock_requests.Session.return_value.post.assert_called_once()
    call_args = mock_requests.Session.return_value.post.call_args
    assert call_args[0][0].endswith("/analyze")


@patch("geocongoai.gundua_engine.analysis.requests")
def test_analyze_greenfield_string_type(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = GREENFIELD_RESPONSE
    mock_requests.Session.return_value.post.return_value = mock_response

    client = GunduaEngineClient()
    result = client.analyze("greenfield", bbox=SAMPLE_BBOX)

    assert result["status"] == "completed"
    # Vérifier que le payload envoyé contient bbox ET un datetime auto-généré
    sent_payload = mock_requests.Session.return_value.post.call_args[1]["json"]
    assert sent_payload["analysis_type"] == "greenfield"
    assert sent_payload["bbox"] == SAMPLE_BBOX
    # datetime auto-généré : format YYYY-MM-DD/YYYY-MM-DD
    assert re.match(r"\d{4}-\d{2}-\d{2}/\d{4}-\d{2}-\d{2}", sent_payload["datetime"])


@patch("geocongoai.gundua_engine.analysis.requests")
def test_analyze_auto_datetime_without_explicit_datetime(mock_requests):
    """Sans fournir datetime, le SDK génère automatiquement la plage temporelle."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = GREENFIELD_RESPONSE
    mock_requests.Session.return_value.post.return_value = mock_response

    client = GunduaEngineClient()
    # Aucun datetime passé !
    client.analyze("greenfield", bbox=SAMPLE_BBOX)

    sent_payload = mock_requests.Session.return_value.post.call_args[1]["json"]
    assert "datetime" in sent_payload
    assert re.match(r"\d{4}-\d{2}-\d{2}/\d{4}-\d{2}-\d{2}", sent_payload["datetime"])


@patch("geocongoai.gundua_engine.analysis.requests")
def test_analyze_explicit_datetime_overrides_auto(mock_requests):
    """Un datetime fourni explicitement doit être préservé tel quel."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = GREENFIELD_RESPONSE
    mock_requests.Session.return_value.post.return_value = mock_response

    client = GunduaEngineClient()
    client.analyze("greenfield", bbox=SAMPLE_BBOX, datetime=SAMPLE_DATETIME)

    sent_payload = mock_requests.Session.return_value.post.call_args[1]["json"]
    assert sent_payload["datetime"] == SAMPLE_DATETIME


@patch("geocongoai.gundua_engine.analysis.requests")
def test_analyze_custom_months_window(mock_requests):
    """Le paramètre months permet de choisir la fenêtre temporelle auto."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = GREENFIELD_RESPONSE
    mock_requests.Session.return_value.post.return_value = mock_response

    client = GunduaEngineClient()
    client.analyze("greenfield", bbox=SAMPLE_BBOX, months=6)

    sent_payload = mock_requests.Session.return_value.post.call_args[1]["json"]
    start_str, end_str = sent_payload["datetime"].split("/")
    delta = (date.fromisoformat(end_str) - date.fromisoformat(start_str)).days
    assert 175 <= delta <= 185


@patch("geocongoai.gundua_engine.analysis.requests")
def test_analyze_illegal_mining(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = ILLEGAL_MINING_RESPONSE
    mock_requests.Session.return_value.post.return_value = mock_response

    client = GunduaEngineClient()
    result = client.analyze("illegal_mining", bbox=SAMPLE_BBOX, datetime=SAMPLE_DATETIME)

    assert result["result"]["risk_level"] == "high"


@patch("geocongoai.gundua_engine.analysis.requests")
def test_analyze_http_400_raises_invalid_params(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "bbox invalide"}
    mock_requests.Session.return_value.post.return_value = mock_response

    client = GunduaEngineClient()
    with pytest.raises(InvalidParametersError):
        client.analyze("greenfield", bbox=SAMPLE_BBOX)


@patch("geocongoai.gundua_engine.analysis.requests")
def test_analyze_http_500_raises_server_error(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "internal server error"}
    mock_requests.Session.return_value.post.return_value = mock_response

    client = GunduaEngineClient()
    with pytest.raises(ServerError):
        client.analyze("landslide", bbox=SAMPLE_BBOX)


# ─── Tests fonctions utilitaires ─────────────────────────────────────────────

@patch("geocongoai.gundua_engine.analysis.requests")
def test_analyse_basee_sur_des_regles_function(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = GREENFIELD_RESPONSE
    mock_requests.Session.return_value.post.return_value = mock_response

    result = analyse_basee_sur_des_regles(
        "greenfield",
        bbox=SAMPLE_BBOX,
        datetime=SAMPLE_DATETIME,
    )
    assert result["analysis_type"] == "greenfield"


@patch("geocongoai.gundua_engine.analysis.requests")
def test_analyse_basee_sur_des_regles_custom_api_url(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"analysis_type": "landcover", "status": "completed"}
    mock_requests.Session.return_value.post.return_value = mock_response

    result = analyse_basee_sur_des_regles(
        "landcover",
        bbox=SAMPLE_BBOX,
        api_url="https://my-custom-gundua.example.com",
    )
    assert result["analysis_type"] == "landcover"
    call_url = mock_requests.Session.return_value.post.call_args[0][0]
    assert "my-custom-gundua.example.com" in call_url


# ─── Tests tous les types d'analyse valides ──────────────────────────────────

@pytest.mark.parametrize("analysis_type", list(VALID_ANALYSIS_TYPES))
@patch("geocongoai.gundua_engine.analysis.requests")
def test_all_valid_analysis_types_accepted(mock_requests, analysis_type):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"analysis_type": analysis_type, "status": "completed"}
    mock_requests.Session.return_value.post.return_value = mock_response

    result = analyse_basee_sur_des_regles(
        analysis_type,
        bbox=SAMPLE_BBOX,
        datetime=SAMPLE_DATETIME,
    )
    assert result["analysis_type"] == analysis_type
    assert result["status"] == "completed"
