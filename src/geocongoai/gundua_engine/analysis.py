"""Module `gundua_engine` pour l'analyse déterministe, l'analyse basée sur des règles (API à distance) et le traitement d'images géospatiales."""
import json
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional, Union

try:
    import requests
except ImportError:
    requests = None

try:
    import numpy as np
    import rasterio
except ImportError:
    np = None
    rasterio = None

from geocongoai.exceptions import (
    GeoCongoError,
    InvalidParametersError,
    ServerError,
    APIError,
)

DEFAULT_GUNDUA_API_URL = "https://geocongo-solafune-greenfield-api.geocongoai.com"
VALID_ANALYSIS_TYPES = {"greenfield", "illegal_mining", "lineaments", "landcover", "landslide"}


class GunduaEngineClient:
    """Client API pour le moteur d'analyse basée sur des règles (Gundua Engine).

    Permet d'exécuter 5 types d'analyses géospatiales distantes:
    - greenfield (Sentinel-2, indices minéraux pondérés)
    - illegal_mining (Sentinel-2, sol nu + végétation)
    - lineaments (MNT/DEM, hillshade + détection de contours)
    - landcover (Sentinel-2, seuils spectraux - 4 classes)
    - landslide (DEM + Sentinel-2, pente + humidité)

    Args:
        base_url: URL racine de l'API (par défaut: https://geocongo-solafune-greenfield-api.geocongoai.com).
        timeout: Temps d'attente maximal en secondes (par défaut: 60.0).
    """

    def __init__(
        self,
        base_url: str = DEFAULT_GUNDUA_API_URL,
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        if requests is not None:
            self._session = requests.Session()
            self._session.headers.update({"Content-Type": "application/json"})
        else:
            self._session = None

    def analyze(
        self,
        payload_or_type: Union[str, Dict[str, Any]],
        bbox: Optional[List[float]] = None,
        datetime: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Exécute une analyse basée sur des règles via l'API distante Gundua Engine.

        Args:
            payload_or_type: Dictionnaire complet d'analyse OU type d'analyse 
                             (ex: 'greenfield', 'illegal_mining', 'lineaments', 'landcover', 'landslide').
            bbox: Emprise spatiale [min_lon, min_lat, max_lon, max_lat] (ex: [28.5, -11.5, 28.6, -11.4]).
            datetime: Plage temporelle ISO/STAC (ex: "2023-06-01/2023-06-30").
            **kwargs: Paramètres additionnels pour l'analyse.

        Returns:
            Dictionnaire de résultats renvoyé par l'API Gundua Engine.
        """
        if isinstance(payload_or_type, dict):
            payload = dict(payload_or_type)
            payload.update(kwargs)
        elif isinstance(payload_or_type, str):
            payload = {"analysis_type": payload_or_type}
            if bbox is not None:
                payload["bbox"] = bbox
            if datetime is not None:
                payload["datetime"] = datetime
            payload.update(kwargs)
        else:
            raise InvalidParametersError(
                "L'argument principal doit être un dictionnaire d'analyse ou une chaîne représentant le type d'analyse."
            )

        analysis_type = payload.get("analysis_type")
        if not analysis_type:
            raise InvalidParametersError("Le champ 'analysis_type' est obligatoire dans le payload.")

        if analysis_type not in VALID_ANALYSIS_TYPES:
            valid_types = ", ".join(sorted(list(VALID_ANALYSIS_TYPES)))
            raise InvalidParametersError(
                f"Type d'analyse invalide '{analysis_type}'. Types d'analyse disponibles: {valid_types}"
            )

        if "bbox" in payload and payload["bbox"] is not None:
            bbox_val = payload["bbox"]
            if not isinstance(bbox_val, (list, tuple)) or len(bbox_val) != 4:
                raise InvalidParametersError(
                    "Le paramètre 'bbox' doit être une liste ou un tuple de 4 nombres [min_lon, min_lat, max_lon, max_lat]."
                )

        url = f"{self.base_url}/analyze"

        if self._session is not None:
            try:
                response = self._session.post(url, json=payload, timeout=self.timeout)
                status_code = response.status_code
                try:
                    data = response.json()
                except Exception:
                    data = {"error": response.text}
            except requests.RequestException as exc:
                raise GeoCongoError(f"Erreur de connexion HTTP vers {url}: {exc}") from exc
        else:
            json_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=json_bytes,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    status_code = resp.getcode()
                    resp_body = resp.read().decode("utf-8")
                    try:
                        data = json.loads(resp_body)
                    except Exception:
                        data = {"error": resp_body}
            except urllib.error.HTTPError as exc:
                status_code = exc.code
                resp_body = exc.read().decode("utf-8")
                try:
                    data = json.loads(resp_body)
                except Exception:
                    data = {"error": resp_body}
            except urllib.error.URLError as exc:
                raise GeoCongoError(f"Erreur réseau lors de l'accès à {url}: {exc}") from exc

        if 200 <= status_code < 300:
            return data

        error_message = data.get("error") or data.get("message") or f"Erreur HTTP {status_code}"

        if status_code == 400:
            raise InvalidParametersError(f"Paramètres invalides: {error_message}", status_code=400, payload=data)
        elif status_code == 500:
            raise ServerError(f"Erreur serveur Gundua Engine: {error_message}", status_code=500, payload=data)
        else:
            raise APIError(f"Erreur API Gundua Engine ({status_code}): {error_message}", status_code=status_code, payload=data)


def analyse_basee_sur_des_regles(
    payload_or_type: Union[str, Dict[str, Any]],
    bbox: Optional[List[float]] = None,
    datetime: Optional[str] = None,
    api_url: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Exécute une analyse basée sur des règles via l'API distante Gundua Engine.

    Args:
        payload_or_type: Dictionnaire d'analyse { "analysis_type": "greenfield", "bbox": [...], ... } 
                         OU type d'analyse ('greenfield', 'illegal_mining', 'lineaments', 'landcover', 'landslide').
        bbox: Emprise spatiale [min_lon, min_lat, max_lon, max_lat].
        datetime: Intervalle de temps (ex: "2023-06-01/2023-06-30").
        api_url: URL personnalisée de l'API (par défaut: https://geocongo-solafune-greenfield-api.geocongoai.com).
        **kwargs: Paramètres additionnels pour l'analyse.

    Returns:
        Dictionnaire de résultats.
    """
    client = GunduaEngineClient(base_url=api_url or DEFAULT_GUNDUA_API_URL)
    return client.analyze(payload_or_type, bbox=bbox, datetime=datetime, **kwargs)


# Alias raccourci
analyse_regles = analyse_basee_sur_des_regles


def analyse_deterministe(
    raster_path_or_payload: Optional[Union[str, Dict[str, Any]]] = None,
    rules: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Analyse basée sur des règles déterministes.

    Prend en charge à la fois :
    1. L'analyse déterministe distante Gundua Engine si un dictionnaire ou un type d'analyse reconnu est transmis.
    2. L'analyse spectrale locale d'un fichier raster TIFF via rasterio (`raster_path_or_payload="chemin.tif"`).

    Args:
        raster_path_or_payload: Chemin vers un fichier raster TIFF OU dictionnaire d'analyse Gundua Engine OU type d'analyse.
        rules: Dictionnaire de règles ou seuils pour analyse raster locale.

    Returns:
        Dictionnaire avec les résultats d'analyse.
    """
    if isinstance(raster_path_or_payload, dict):
        return analyse_basee_sur_des_regles(raster_path_or_payload, **kwargs)
    elif isinstance(raster_path_or_payload, str) and raster_path_or_payload in VALID_ANALYSIS_TYPES:
        return analyse_basee_sur_des_regles(raster_path_or_payload, **kwargs)

    raster_path = raster_path_or_payload
    rules = rules or {}
    index_type = rules.get("index", "NDVI").upper()
    threshold = float(rules.get("threshold", 0.2))

    if not raster_path:
        return {"error": "Un chemin de fichier raster ou un dictionnaire d'analyse est requis."}

    if rasterio is None or np is None:
        return {
            "raster": raster_path,
            "rules_applied": rules,
            "status": "warning",
            "message": "rasterio et numpy sont requis pour l'analyse spectrale complète.",
            "summary": "logique déterministe basée sur les règles sans rasterio",
        }

    try:
        with rasterio.open(raster_path) as src:
            meta = {
                "width": src.width,
                "height": src.height,
                "count": src.count,
                "crs": str(src.crs),
            }

            if src.count < 2:
                return {
                    "raster": raster_path,
                    "meta": meta,
                    "error": "Le raster doit contenir au moins 2 bandes pour calculer un indice spectral.",
                }

            if index_type == "NDVI" and src.count >= 4:
                red = src.read(3).astype(np.float32)
                nir = src.read(4).astype(np.float32)
                denom = nir + red
                denom[denom == 0] = 1.0
                spectral_index = (nir - red) / denom
            elif index_type == "NDWI" and src.count >= 3:
                green = src.read(2).astype(np.float32)
                nir = src.read(4 if src.count >= 4 else 3).astype(np.float32)
                denom = green + nir
                denom[denom == 0] = 1.0
                spectral_index = (green - nir) / denom
            else:
                b1 = src.read(1).astype(np.float32)
                b2 = src.read(2).astype(np.float32)
                denom = b1 + b2
                denom[denom == 0] = 1.0
                spectral_index = (b2 - b1) / denom

            mask = spectral_index > threshold
            percentage_above_threshold = float(np.mean(mask) * 100)
            mean_index = float(np.mean(spectral_index))

            return {
                "raster": raster_path,
                "meta": meta,
                "rules_applied": rules,
                "index_used": index_type,
                "threshold": threshold,
                "mean_index": round(mean_index, 4),
                "percentage_above_threshold": round(percentage_above_threshold, 2),
                "status": "success",
            }
    except Exception as exc:
        return {
            "raster": raster_path,
            "rules_applied": rules,
            "error": f"Erreur d'analyse du raster: {exc}",
        }


def analyse_ia_fondation(coords_or_tif: str, model_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Appelle le client IA (Prithvi) pour extraire des caractéristiques profondes.

    Si `terratorch` n'est pas installé, la fonction renvoie un message explicite.
    """
    try:
        from geocongoai.ia import PrithviClient
    except Exception:
        return {"error": "Prithvi non disponible: installer geocongoai[ia] (terratorch, torch)"}

    client = PrithviClient(model_name=model_name or "prithvi_eo_v2_300")
    try:
        features = client.extract_deep_features(coords_or_tif, **kwargs)
    except Exception as exc:
        return {"error": str(exc)}

    return {"features": features}


def traiter_image_satellite(ms_path: str = None, pan_path: str = None, out_path: str = None, method: str = "pansharpen") -> Dict[str, Any]:
    """Point d'entrée simple pour traitements d'images satellites.

    Args:
        ms_path: chemin multispectral
        pan_path: chemin panchromatique
        out_path: sortie
        method: méthode de traitement (par défaut 'pansharpen')
    """
    if method == "pansharpen":
        if not (ms_path and pan_path and out_path):
            return {"error": "ms_path, pan_path et out_path requis pour pansharpen"}
        try:
            from geocongoai.vision.pansharpen import pansharpen_brovey
        except Exception:
            return {"error": "rasterio/numpy requis pour pansharpen"}

        out = pansharpen_brovey(ms_path, pan_path, out_path)
        return {"out_path": out}

    return {"error": f"Méthode inconnue: {method}"}


__all__ = [
    "DEFAULT_GUNDUA_API_URL",
    "VALID_ANALYSIS_TYPES",
    "GunduaEngineClient",
    "analyse_basee_sur_des_regles",
    "analyse_regles",
    "analyse_deterministe",
    "analyse_ia_fondation",
    "traiter_image_satellite",
]

