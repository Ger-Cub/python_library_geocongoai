"""Exceptions pour le SDK GeoCongo AI."""
from typing import Optional, Any, Dict


class GeoCongoError(Exception):
    """Exception de base pour toutes les erreurs du SDK GeoCongo AI."""
    pass


class APIError(GeoCongoError):
    """Exception levée en cas d'erreur HTTP retournée par l'API GeoCongo AI."""

    def __init__(self, message: str, status_code: Optional[int] = None, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"[HTTP {self.status_code}] {self.message}"
        return self.message


class InvalidParametersError(APIError):
    """Exception levée lorsque les paramètres transmis sont invalides (HTTP 400)."""
    pass


class InsufficientBalanceError(APIError):
    """Exception levée lorsque le solde d'unités de l'utilisateur est insuffisant (HTTP 402)."""

    def __init__(self, message: str = "Veuillez recharger votre solde unités.", status_code: int = 402, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=status_code, payload=payload)


class ServerError(APIError):
    """Exception levée en cas d'erreur interne du serveur GeoCongo AI (HTTP 500)."""
    pass


__all__ = [
    "GeoCongoError",
    "APIError",
    "InvalidParametersError",
    "InsufficientBalanceError",
    "ServerError",
]
