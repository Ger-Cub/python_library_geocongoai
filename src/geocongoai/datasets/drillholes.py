"""Gestion des jeux de données de forages géologiques (DrillholeDataset).
"""
import os
from typing import List, Dict, Any, Optional, Union
from .base import BaseGeologicalDataset

try:
    import pandas as pd
except ImportError:
    pd = None


class DrillholeDataset(BaseGeologicalDataset):
    """Jeu de données de forages géologiques composé de colliers (collars) et d'analyses (assays)."""

    def __init__(
        self,
        collars: Union[List[Dict[str, Any]], Any],
        assays: Union[List[Dict[str, Any]], Any],
        survey: Optional[Union[List[Dict[str, Any]], Any]] = None
    ):
        """Initialise le dataset avec les colliers et les analyses.

        Args:
            collars: Liste de dicts ou DataFrame pandas des colliers (hole_id, x, y, z, dip, azimuth).
            assays: Liste de dicts ou DataFrame pandas des analyses (hole_id, from_m, to_m, teneurs...).
            survey: Trajectoires de déviation optionnelles.
        """
        self.collars = self._normalize_to_list(collars)
        self.assays = self._normalize_to_list(assays)
        self.survey = self._normalize_to_list(survey) if survey is not None else []
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
        """Valide la présence minimale des champs requis."""
        if not self.collars:
            return
        
        req_collar_fields = {"hole_id", "x", "y", "z"}
        first_collar = set(self.collars[0].keys())
        missing_collar = req_collar_fields - first_collar
        if missing_collar:
            raise ValueError(f"Colonnes manquantes dans les colliers: {missing_collar}")

        if self.assays:
            req_assay_fields = {"hole_id", "from_m", "to_m"}
            first_assay = set(self.assays[0].keys())
            missing_assay = req_assay_fields - first_assay
            if missing_assay:
                raise ValueError(f"Colonnes manquantes dans les analyses: {missing_assay}")

    @classmethod
    def from_csv(
        cls,
        collar_path: str,
        assay_path: str,
        survey_path: Optional[str] = None
    ) -> "DrillholeDataset":
        """Charge un dataset de forages depuis deux ou trois fichiers CSV.

        Args:
            collar_path: Chemin du fichier CSV des colliers.
            assay_path: Chemin du fichier CSV des analyses.
            survey_path: Chemin optionnel du fichier CSV des devis d'orientation.
        """
        if pd is None:
            import csv
            def read_csv_simple(path: str) -> List[Dict[str, Any]]:
                with open(path, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    records = []
                    for row in reader:
                        converted = {}
                        for k, v in row.items():
                            try:
                                converted[k] = float(v)
                            except (ValueError, TypeError):
                                converted[k] = v
                        records.append(converted)
                    return records

            collars = read_csv_simple(collar_path)
            assays = read_csv_simple(assay_path)
            surveys = read_csv_simple(survey_path) if survey_path and os.path.exists(survey_path) else None
            return cls(collars=collars, assays=assays, survey=surveys)
        else:
            collars_df = pd.read_csv(collar_path)
            assays_df = pd.read_csv(assay_path)
            surveys_df = pd.read_csv(survey_path) if survey_path and os.path.exists(survey_path) else None
            return cls(collars=collars_df, assays=assays_df, survey=surveys_df)

    @classmethod
    def from_dataframe(
        cls,
        collars_df: Any,
        assays_df: Any,
        survey_df: Optional[Any] = None
    ) -> "DrillholeDataset":
        """Crée un dataset depuis des DataFrames pandas."""
        return cls(collars=collars_df, assays=assays_df, survey=survey_df)

    @classmethod
    def from_dict(
        cls,
        collars: List[Dict[str, Any]],
        assays: List[Dict[str, Any]],
        survey: Optional[List[Dict[str, Any]]] = None
    ) -> "DrillholeDataset":
        """Crée un dataset depuis des listes de dictionnaires."""
        return cls(collars=collars, assays=assays, survey=survey)

    def get_element_columns(self) -> List[str]:
        """Identifie les colonnes numériques susceptibles d'être des valeurs géochimiques."""
        if not self.assays:
            return []
        sample = self.assays[0]
        elements = []
        for k, v in sample.items():
            if k not in ("hole_id", "from_m", "to_m", "x", "y", "z", "mid_depth") and isinstance(v, (int, float)):
                elements.append(k)
        return elements

    def info(self) -> Dict[str, Any]:
        """Génère un dictionnaire de synthèses exécutives du jeu de données."""
        hole_ids = {c["hole_id"] for c in self.collars}
        xs = [float(c["x"]) for c in self.collars if "x" in c]
        ys = [float(c["y"]) for c in self.collars if "y" in c]
        zs = [float(c["z"]) for c in self.collars if "z" in c]

        elements = self.get_element_columns()

        return {
            "dataset_type": "DrillholeDataset",
            "drillhole_count": len(hole_ids),
            "assay_count": len(self.assays),
            "elements": elements,
            "bounding_box": {
                "x_min": min(xs) if xs else None,
                "x_max": max(xs) if xs else None,
                "y_min": min(ys) if ys else None,
                "y_max": max(ys) if ys else None,
                "z_min": min(zs) if zs else None,
                "z_max": max(zs) if zs else None,
            }
        }

    def analyze(
        self,
        method: str = "dbscan",
        element: str = "cu_pct",
        grade_threshold: float = 0.5,
        eps: float = 25.0,
        min_samples: int = 3,
        **kwargs
    ) -> Any:
        """Lance l'analyse spatiale/géochimique 3D et retourne un objet GeoResult."""
        from ..analysis.clustering import cluster_drillholes
        return cluster_drillholes(
            dataset=self,
            element=element,
            grade_threshold=grade_threshold,
            eps=eps,
            min_samples=min_samples,
            **kwargs
        )
