"""Client SDK officiel GeoCongo AI pour interagir avec les Edge Functions Supabase."""
import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List

try:
    import requests
except ImportError:
    requests = None

from .exceptions import (
    GeoCongoError,
    APIError,
    InvalidParametersError,
    InsufficientBalanceError,
    ServerError,
)
from .models import (
    RagResponse,
    DocumentSearchResponse,
    GeologicalSearchResponse,
)

DEFAULT_BASE_URL = "https://tjpopbzjzlrrolqdismq.supabase.co/functions/v1"
VALID_GEOLOGICAL_TYPES = {"all", "documents", "rocks", "maps", "datasets"}


class GeoCongoClient:
    """Client principal pour l'API GeoCongo AI.

    Args:
        api_key: Clé d'API GeoCongo AI (`GEOCONGOAI_API_KEY`) ou Supabase Anon/Service Role.
        base_url: URL racine des Edge Functions (par défaut: https://tjpopbzjzlrrolqdismq.supabase.co/functions/v1).
        timeout: Temps d'attente maximal par requête en secondes (par défaut: 30.0).
        supabase_url: Optionnel. URL du projet Supabase.
        supabase_anon_key: Optionnel. Clé Supabase anon (alias pour api_key).
        user_id: Optionnel. Identifiant utilisateur unique (legacy, conservé pour rétrocompatibilité).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        *,
        supabase_url: Optional[str] = None,
        supabase_anon_key: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        # 1. Résolution de la clé API ou user_id legacy
        self.api_key = api_key or supabase_anon_key or os.getenv("GEOCONGOAI_API_KEY")
        self._user_id = user_id

        if not self.api_key and not self._user_id:
            raise ValueError(
                "Authentification requise : Veuillez fournir api_key='gcg_live_...' "
                "ou définir la variable d'environnement GEOCONGOAI_API_KEY.\n"
                "Vous pouvez générer une clé d'accès dans votre espace membre GeoCongo AI : "
                "https://www.geocongoai.com/api-keys"
            )

        # 2. Résolution de l'URL racine des Edge Functions
        if base_url:
            self.base_url = base_url.rstrip("/")
        elif supabase_url:
            s_url = supabase_url.rstrip("/")
            if s_url.endswith("/functions/v1"):
                self.base_url = s_url
            else:
                self.base_url = f"{s_url}/functions/v1"
        elif os.getenv("SUPABASE_URL"):
            env_url = os.getenv("SUPABASE_URL").rstrip("/")
            if env_url.endswith("/functions/v1"):
                self.base_url = env_url
            else:
                self.base_url = f"{env_url}/functions/v1"
        else:
            self.base_url = DEFAULT_BASE_URL.rstrip("/")

        self.timeout = timeout

        if requests is not None:
            self._session = requests.Session()
            self._session.headers.update(self._get_headers())
        else:
            self._session = None

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["x-geocongo-api-key"] = self.api_key
        return headers

    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Effectue une requête HTTP POST vers l'endpoint spécifié."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()

        if self._session is not None:
            try:
                response = self._session.post(url, json=payload, headers=headers, timeout=self.timeout)
                status_code = response.status_code
                try:
                    data = response.json()
                except Exception:
                    data = {"error": response.text}
            except requests.RequestException as exc:
                raise GeoCongoError(f"Erreur de connexion HTTP vers {url}: {exc}") from exc
        else:
            # Fallback vers la bibliothèque standard urllib.request
            json_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=json_bytes,
                headers=headers,
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

        # Traitement des erreurs selon les codes de statut HTTP
        if 200 <= status_code < 300:
            return data

        error_message = data.get("error") or data.get("message") or f"Erreur HTTP {status_code}"

        if status_code == 400:
            raise InvalidParametersError(f"Paramètres invalides: {error_message}", status_code=400, payload=data)
        elif status_code == 402:
            raise InsufficientBalanceError(
                message=data.get("message") or "Veuillez recharger votre solde unités.",
                status_code=402,
                payload=data,
            )
        elif status_code == 500:
            raise ServerError(f"Erreur interne du serveur: {error_message}", status_code=500, payload=data)
        else:
            raise APIError(f"Erreur API ({status_code}): {error_message}", status_code=status_code, payload=data)

    def ask_rag(
        self,
        query: str,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        voice_name: str = "GeoCongo AI",
        language: str = "fr",
    ) -> RagResponse:
        """Génère une réponse synthétisée avec citations documentaires via l'assistant RAG.

        Args:
            query: Question posée à l'agent
            user_id: Identifiant unique optionnel de l'utilisateur (legacy, facultatif si api_key est fournie)
            conversation_id: Identifiant optionnel de la conversation
            voice_name: Nom du profil vocal dans les métadonnées (par défaut "GeoCongo AI")
            language: Langue de la réponse (par défaut "fr")

        Returns:
            RagResponse contenant `answer` et `sources`

        Raises:
            InsufficientBalanceError: Si le solde d'unités est insuffisant (HTTP 402)
            InvalidParametersError: Si les paramètres sont invalides (HTTP 400)
            ServerError: Si une erreur serveur survient (HTTP 500)
        """
        payload: Dict[str, Any] = {
            "query": query,
            "language": language,
            "metadata": {
                "voice_name": voice_name,
            },
        }
        if conversation_id:
            payload["conversationId"] = conversation_id

        effective_user_id = user_id or self._user_id
        if effective_user_id:
            payload["userId"] = effective_user_id

        data = self._post("/rag-agent", payload)
        return RagResponse.from_dict(data)

    def search_documents(
        self,
        query: str,
        domain: Optional[str] = None,
        category: Optional[str] = None,
        province: Optional[str] = None,
        **filters,
    ) -> DocumentSearchResponse:
        """Effectue une recherche sémantique et textuelle ciblée sur les documents validés.

        Args:
            query: Termes de recherche
            domain: Filtre par domaine (ex: "Mines")
            category: Filtre par catégorie (ex: "Thèse")
            province: Filtre par province (ex: "Lualaba")
            **filters: Filtres supplémentaires.

        Returns:
            DocumentSearchResponse contenant `results`, `total_found`, `query` et `applied_filters`
        """
        combined_filters: Dict[str, Any] = {}
        if domain:
            combined_filters["domaine"] = domain
        if category:
            combined_filters["categorie"] = category
        if province:
            combined_filters["province"] = province
        combined_filters.update(filters)

        payload: Dict[str, Any] = {
            "query": query,
            "filters": combined_filters,
        }

        data = self._post("/search-documents", payload)
        return DocumentSearchResponse.from_dict(data)

    def search_geological(
        self,
        query: str,
        type: str = "all",
        province: Optional[str] = None,
        **filters,
    ) -> GeologicalSearchResponse:
        """Effectue une recherche vectorielle globale (1536D) multimodale.

        Args:
            query: Termes de recherche (ex: "malachite et cuivre")
            type: Type d'éléments recherchés ("all", "documents", "rocks", "maps", "datasets")
            province: Filtre optionnel par province (ex: "Haut-Katanga")
            **filters: Filtres supplémentaires.

        Returns:
            GeologicalSearchResponse contenant `results`, `total_found`, `query` et `type`
        """
        if type not in VALID_GEOLOGICAL_TYPES:
            raise InvalidParametersError(
                f"Type géologique invalide '{type}'. Valeurs acceptées: {sorted(list(VALID_GEOLOGICAL_TYPES))}"
            )

        combined_filters: Dict[str, Any] = {}
        if province:
            combined_filters["province"] = province
        combined_filters.update(filters)

        payload: Dict[str, Any] = {
            "query": query,
            "type": type,
            "filters": combined_filters,
        }

        data = self._post("/search-geological", payload)
        return GeologicalSearchResponse.from_dict(data)


__all__ = ["GeoCongoClient", "DEFAULT_BASE_URL"]

