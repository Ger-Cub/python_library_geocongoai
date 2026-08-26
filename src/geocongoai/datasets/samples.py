"""Gestion des jeux de données d'échantillons de surface ou ponctuels (SampleDataset).
"""
from typing import List, Dict, Any, Optional, Union
from .base import BaseGeologicalDataset

try:
    import pandas as pd
except ImportError:
    pd = None


class SampleDataset(BaseGeologicalDataset):
    """Jeu de données géologiques pour des points d'échantillonnage de surface ou ponctuels."""

    def __init__(self, samples: Union[List[Dict[str, Any]], Any]):
        """Initialise le dataset d'échantillons.

        Args:
            samples: Liste de dictionnaires ou DataFrame pandas.
        """
        self.samples = self._normalize_to_list(samples)
        self._validate_schema()

    @staticmethod
    def _normalize_to_list(data: Any) -> List[Dict[str, Any]]:
        if data is None:
            return []
        if isinstance(data, list):
            return data
        if pd is not None and isinstance(data, pd.DataFrame):
            return data.to_dict(orient="records")
        raise TypeError("Les données doivent être une liste de dictionnaires ou un DataFrame pandas.")

    def _validate_schema(self) -> None:
        if not self.samples:
            return
        sample = self.samples[0]
        if "x" not in sample or "y" not in sample:
            raise ValueError("Les échantillons doivent contenir au minimum les coordonnées 'x' et 'y'.")

    @classmethod
    def from_csv(cls, path: str) -> "SampleDataset":
        """Charge un dataset d'échantillons depuis un fichier CSV."""
        if pd is None:
            import csv
            with open(path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                records = [{k: (float(v) if v.replace('.','',1).isdigit() else v) for k, v in row.items()} for row in reader]
            return cls(samples=records)
        else:
            df = pd.read_csv(path)
            return cls(samples=df)

    def info(self) -> Dict[str, Any]:
        """Synthèse du jeux de données d'échantillons."""
        xs = [float(s["x"]) for s in self.samples if "x" in s]
        ys = [float(s["y"]) for s in self.samples if "y" in s]
        zs = [float(s.get("z", 0.0)) for s in self.samples if "z" in s]

        return {
            "dataset_type": "SampleDataset",
            "sample_count": len(self.samples),
            "bounding_box": {
                "x_min": min(xs) if xs else None,
                "x_max": max(xs) if xs else None,
                "y_min": min(ys) if ys else None,
                "y_max": max(ys) if ys else None,
                "z_min": min(zs) if zs else None,
                "z_max": max(zs) if zs else None,
            }
        }

    def analyze(self, method: str = "dbscan", element: str = "cu_pct", **kwargs) -> Any:
        raise NotImplementedError("L'analyse sur SampleDataset sera disponible prochainement.")
