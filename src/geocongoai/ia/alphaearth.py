"""AlphaEarth client for extracting embeddings from Google Earth Engine.

This module provides a light wrapper around the `earthengine-api` (ee).
It does NOT include credentials; users must authenticate separately (service
account or user account). The module samples image pixels and returns arrays
ready to be fed to an external foundation model (alphaearth) or to a deployed
model endpoint.
"""
from typing import Optional, Any, Dict


class AlphaEarthClient:
    def __init__(self, service_account: Optional[str] = None, credentials_json: Optional[str] = None):
        self._initialized = False
        self.service_account = service_account
        self.credentials_json = credentials_json
        self.ee = None

    def authenticate(self) -> None:
        try:
            import ee
        except Exception as exc:
            raise ImportError("earthengine-api is required (pip install earthengine-api)") from exc

        self.ee = ee

        if self.credentials_json:
            # service account flow
            try:
                credentials = ee.ServiceAccountCredentials(self.service_account, self.credentials_json)
                ee.Initialize(credentials)
            except Exception:
                # fallback to interactive initialize
                ee.Initialize()
        else:
            # attempt default initialize
            ee.Initialize()

        self._initialized = True

    def set_model_asset(self, model_asset_id: str) -> None:
        """Configure l'asset du modèle foundation (ex: 'users/me/alphaearth_model')."""
        self.model_asset = model_asset_id

    def extract_embeddings(self, geometry: Any, start_date: Optional[str] = None, end_date: Optional[str] = None, bands: Optional[list] = None, scale: int = 30, max_pixels: int = 100000) -> Dict[str, Any]:
        """Sample pixels from GEE composite and return arrays that can be
        converted to embeddings by a foundation model.

        Args:
            geometry: ee.Geometry or GeoJSON-like geometry describing the area
            start_date/end_date: date range for the ImageCollection
            bands: list of band names to select
            scale: resolution in meters
            max_pixels: max pixels to sample

        Returns:
            dict with 'samples' (list of pixel vectors) and metadata.
        """
        if not self._initialized:
            self.authenticate()

        ee = self.ee

        # Build a simple Sentinel-2 composite if no bands specified
        if bands is None:
            bands = ["B4", "B3", "B2", "B8"]  # R,G,B,NIR typical

        # Create collection
        collection = ee.ImageCollection("COPERNICUS/S2_SR")
        if start_date:
            collection = collection.filterDate(start_date, end_date or start_date)
        if geometry is not None:
            collection = collection.filterBounds(geometry)

        composite = collection.median().select(bands)

        # Sample the region
        sampled = composite.sample(region=geometry, scale=scale, numPixels=max_pixels, geometries=False)

        # Convert to client-side list (warning: may be large)
        try:
            features = sampled.getInfo()
            # features is a dict with 'features': list of {'properties': {band: value}}
            samples = [list(f["properties"].values()) for f in features.get("features", [])]
        except Exception:
            # If server-side getInfo is denied, return the uncomputed ee object and instructions
            return {"error": "failed to retrieve samples client-side. Use a service account with appropriate quotas or export via ee.batch.Export."}

        return {"samples": samples, "count": len(samples), "bands": bands}


__all__ = ["AlphaEarthClient"]
