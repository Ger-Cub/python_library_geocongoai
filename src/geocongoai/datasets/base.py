"""Base module pour tous les jeux de données géologiques dans GeoCongo AI.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseGeologicalDataset(ABC):
    """Classe abstraite de base représentant un jeu de données géospatial / géologique."""

    @abstractmethod
    def info(self) -> Dict[str, Any]:
        """Retourne un dictionnaire de résumé exécutif du jeu de données."""
        pass

    @abstractmethod
    def analyze(self, method: str = "dbscan", **kwargs) -> Any:
        """Exécute une analyse spatiale / géochimique sur le jeu de données."""
        pass
