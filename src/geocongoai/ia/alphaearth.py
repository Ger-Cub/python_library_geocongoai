"""AlphaEarth client for extracting pre-computed satellite embeddings from Google Earth Engine.

This module provides a wrapper around `earthengine-api` (ee) to fetch 64-dimensional
AlphaEarth annual satellite embeddings (`GOOGLE/SATELLITE_EMBEDDING_V1_ANNUAL`).
"""
from typing import Optional, Any, Dict


class AlphaEarthClient:
    """Client for extracting 64-dimensional AlphaEarth satellite embeddings from GEE."""

    def __init__(self, service_account: Optional[str] = None, credentials_json: Optional[str] = None) -> None:
        """Initialize AlphaEarth client.

        Args:
            service_account: Optional service account email for GEE authentication.
            credentials_json: Optional path to JSON key file for service account.
        """
        self._initialized = False
        self.service_account = service_account
        self.credentials_json = credentials_json
        self.ee = None
        self.model_asset = None

    def authenticate(self) -> None:
        """Authenticate and initialize the Google Earth Engine Python API."""
        try:
            import ee
        except Exception as exc:
            raise ImportError("earthengine-api is required (pip install earthengine-api)") from exc

        self.ee = ee

        if self.credentials_json:
            try:
                credentials = ee.ServiceAccountCredentials(self.service_account, self.credentials_json)
                ee.Initialize(credentials)
            except Exception:
                ee.Initialize()
        else:
            ee.Initialize()

        self._initialized = True

    def set_model_asset(self, model_asset_id: str) -> None:
        """Configure optional custom model asset ID."""
        self.model_asset = model_asset_id

    def extract_embeddings(self, geometry: Any, year: int, max_pixels: int = 100000) -> Dict[str, Any]:
        """Extract pre-computed 64-dimensional AlphaEarth embeddings from GEE for a geometry and year.

        Args:
            geometry: ee.Geometry or GeoJSON-like bounding box describing the AOI.
            year: Year for which the annual satellite embedding should be fetched (e.g. 2023).
            max_pixels: Maximum number of sampled pixels/vectors to retrieve.

        Returns:
            Dict containing:
                - 'samples': List of 64-dimensional embedding feature property dicts or arrays.
                - 'count': Number of vectors extracted.
                - 'bands': Band identifiers ('A00' through 'A63').
        """
        if not self._initialized:
            self.authenticate()

        ee = self.ee

        # Access the official Google AlphaEarth 64-D Satellite Embedding ImageCollection
        embedding_col = ee.ImageCollection("GOOGLE/SATELLITE_EMBEDDING_V1_ANNUAL")
        annual_image = embedding_col.filter(ee.Filter.calendarRange(year, year, "year")).first()

        # Sample the 64 embedding bands (A00-A63) at 10m resolution
        sampled = annual_image.sample(region=geometry, scale=10, numPixels=max_pixels, geometries=False)

        try:
            data = sampled.getInfo()
            embeddings = [feat["properties"] for feat in data.get("features", [])]
            bands = [f"A{str(i).zfill(2)}" for i in range(64)]
            return {"samples": embeddings, "count": len(embeddings), "bands": bands}
        except Exception as exc:
            return {"error": f"Failed to retrieve pre-computed embeddings: {exc}"}


__all__ = ["AlphaEarthClient"]
