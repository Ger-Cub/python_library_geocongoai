"""AlphaEarth client for extracting embeddings from Google Earth Engine.

This module provides a light wrapper around the `earthengine-api` (ee).
It does NOT include credentials; users must authenticate separately (service
account or user account). The module samples image pixels and returns arrays
ready to be fed to an external foundation model (alphaearth) or to a deployed
model endpoint.
"""
from typing import Optional, Any, Dict


class AlphaEarthClient:
    def __init__(self, service_account: Optional[str] = None, credentials_json: Optional[str] = None, mode: str = "precomputed") -> None:
        """Create an AlphaEarth client.

        Parameters
        ----------
        service_account: Optional[str]
            Service‑account email for GEE authentication (if using a service account).
        credentials_json: Optional[str]
            Path to the JSON key for the service account.
        mode: str, default "precomputed"
            * ``"precomputed"`` – fetch the already‑computed 64‑dimensional satellite
              embeddings from the public GEE collection ``GOOGLE/SATELLITE_EMBEDDING_V1_ANNUAL``.
            * ``"raw"`` – keep the legacy behaviour of sampling Sentinel‑2 pixels and
              returning raw spectral values (useful for on‑the‑fly custom embeddings).
        """
        self._initialized = False
        self.service_account = service_account
        self.credentials_json = credentials_json
        self.ee = None
        self.mode = mode
        if mode not in {"precomputed", "raw"}:
            raise ValueError("mode must be either 'precomputed' or 'raw'")

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

    def extract_embeddings(
        self,
        geometry: Any,
        year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        bands: Optional[list] = None,
        scale: int = 30,
        max_pixels: int = 100000,
    ) -> Dict[str, Any]:
        """Extract satellite embeddings.

        The method works in two distinct modes controlled by ``self.mode``:

        * **precomputed** (default) – pulls the 64‑dimensional AlphaEarth embeddings
          from the public GEE collection ``GOOGLE/SATELLITE_EMBEDDING_V1_ANNUAL``.
          The user must supply a ``year`` (e.g., ``2023``). ``scale`` is ignored
          because the dataset is already at 10 m resolution.
        * **raw** – historic behaviour; samples Sentinel‑2 pixels and returns the
          raw spectral values. ``start_date``/``end_date``/``bands``/``scale``
          remain relevant.

        Parameters
        ----------
        geometry: Any
            ``ee.Geometry`` or GeoJSON‑like bounding box describing the AOI.
        year: Optional[int]
            Year for which the pre‑computed embedding should be fetched (required
            in ``precomputed`` mode).
        start_date, end_date: Optional[str]
            Date range for the Sentinel‑2 composite (only used in ``raw`` mode).
        bands: Optional[list]
            List of band names when ``raw`` mode is active. Ignored in
            ``precomputed`` mode.
        scale: int, default 30
            Sampling resolution for ``raw`` mode.
        max_pixels: int, default 100000
            Maximum number of pixels to sample in ``raw`` mode.

        Returns
        -------
        Dict[str, Any]
            * ``samples`` – list of embedding vectors (64‑D for precomputed,
              N‑D for raw).
            * ``count`` – number of vectors returned.
            * ``bands`` – band identifiers (``A00``‑``A63`` for precomputed,
              original band names for raw).
        """
        if not self._initialized:
            self.authenticate()

        ee = self.ee

        if self.mode == "precomputed":
            if year is None:
                raise ValueError("In 'precomputed' mode a 'year' argument is required.")
            # Access the official AlphaEarth embedding collection
            embedding_col = ee.ImageCollection('GOOGLE/SATELLITE_EMBEDDING_V1_ANNUAL')
            annual_image = embedding_col.filter(ee.Filter.calendarRange(year, year, 'year')).first()
            # Sample the 64 embedding bands (A00‑A63)
            sampled = annual_image.sample(region=geometry, scale=10, numPixels=max_pixels, geometries=False)
            try:
                data = sampled.getInfo()
                embeddings = [feat["properties"] for feat in data.get("features", [])]
                bands = [f"A{str(i).zfill(2)}" for i in range(64)]
                return {"samples": embeddings, "count": len(embeddings), "bands": bands}
            except Exception as exc:
                return {"error": f"Failed to retrieve pre‑computed embeddings: {exc}"}

        # ---------------------------------------------------------------------
        # Legacy raw‑pixel path (mode == "raw")
        # ---------------------------------------------------------------------
        if bands is None:
            bands = ["B4", "B3", "B2", "B8"]  # R,G,B,NIR typical

        collection = ee.ImageCollection("COPERNICUS/S2_SR")
        if start_date:
            collection = collection.filterDate(start_date, end_date or start_date)
        if geometry is not None:
            collection = collection.filterBounds(geometry)

        composite = collection.median().select(bands)
        sampled = composite.sample(region=geometry, scale=scale, numPixels=max_pixels, geometries=False)
        try:
            features = sampled.getInfo()
            samples = [list(f["properties"].values()) for f in features.get("features", [])]
        except Exception:
            return {"error": "failed to retrieve samples client-side. Use a service account with appropriate quotas or export via ee.batch.Export."}

        return {"samples": samples, "count": len(samples), "bands": bands}


__all__ = ["AlphaEarthClient"]
