"""Module results.result contenant l'objet universel GeoResult.
"""
import json
from typing import List, Dict, Any, Optional

try:
    import pandas as pd
except ImportError:
    pd = None


class GeoResult:
    """Objet standard de résultat d'analyse géospatiale et géologique (GeoResult).

    Fournit un contrat uniforme entre le moteur de calcul Python et tous les consommateurs
    (Frontends React/Three.js, FastAPI, Jupyter Notebooks, QGIS, export HTML).
    """

    def __init__(
        self,
        points: List[Dict[str, Any]],
        geometries: Optional[List[Dict[str, Any]]] = None,
        statistics: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        collars: Optional[List[Dict[str, Any]]] = None,
    ):
        self.points = points or []
        self.geometries = geometries or []
        self.statistics = statistics or {}
        self.metadata = metadata or {}
        self.collars = collars or []

    def to_dict(self) -> Dict[str, Any]:
        """Retourne la représentation Dictionnaire conforme au standard GeoCongo AI v1.0."""
        return {
            "type": "GeoCongoResult",
            "version": "1.0",
            "crs": self.metadata.get("crs", "EPSG:4326"),
            "metadata": self.metadata,
            "statistics": self.statistics,
            "points": self.points,
            "geometries": self.geometries,
            "collars": self.collars,
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        """Sérialise en JSON standard."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_geojson(self) -> Dict[str, Any]:
        """Convertit les points du résultat au format GeoJSON standard FeatureCollection."""
        features = []
        for p in self.points:
            x = p.get("x", 0.0)
            y = p.get("y", 0.0)
            z = p.get("z", 0.0)
            properties = {k: v for k, v in p.items() if k not in ("x", "y", "z")}
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [x, y, z]
                },
                "properties": properties
            })
        return {
            "type": "FeatureCollection",
            "features": features
        }

    def to_dataframe(self) -> Any:
        """Exporte les points sous forme de DataFrame pandas."""
        if pd is None:
            raise ImportError("pandas est requis pour utiliser to_dataframe().")
        return pd.DataFrame(self.points)

    def show_3d(self, title: Optional[str] = None) -> Any:
        """Affiche la scène 3D interactif Plotly directement dans le notebook Jupyter."""
        from ..visualization.plotly import PlotlyRenderer
        renderer = PlotlyRenderer(self)
        return renderer.show(title=title)

    def to_html(self, output_path: Optional[str] = None) -> str:
        """Exporte un fichier HTML 3D autonome offline."""
        from ..visualization.html import HTMLRenderer
        renderer = HTMLRenderer(self)
        return renderer.render(output_path=output_path)
