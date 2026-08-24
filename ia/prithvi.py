"""Client léger pour interagir avec les modèles Prithvi via terratorch.

Ce module tente d'utiliser `terratorch` BACKBONE_REGISTRY pour construire
le backbone si `terratorch` est installé. Le package n'embarque pas
de poids : l'utilisateur doit fournir `model_name` ou un checkpoint externe.
"""
from typing import Optional, Any

class PrithviClient:
    def __init__(self, model_name: str = "prithvi_eo_v2_300", device: Optional[str] = None, pretrained: bool = True):
        self.model_name = model_name
        self.device = device
        self.pretrained = pretrained
        self.model = None

    def load_model(self, **build_kwargs) -> None:
        try:
            from terratorch import BACKBONE_REGISTRY
            import torch
        except Exception as exc:
            raise ImportError("terratorch et torch sont requis pour PrithviClient: pip install terratorch torch") from exc

        device = self.device or ("cuda" if torch.cuda.is_available() else "cpu")
        # Build model via registry; user may override build kwargs
        self.model = BACKBONE_REGISTRY.build(self.model_name, pretrained=self.pretrained, **build_kwargs)
        self.model.to(device)
        self.model.eval()
        self._device = device

    def extract_deep_features(self, tif_path: str, **kwargs) -> Any:
        """Extrait des caractéristiques profondes pour un fichier tiff donné.

        Cette méthode charge le modèle si nécessaire. Retourne un dictionnaire
        léger contenant des tenseurs NumPy ou structures sérialisables.
        """
        if self.model is None:
            self.load_model()

        # Implémentation minimale: lire le tif, préparer batch, exécuter forward
        try:
            import rasterio
            import numpy as np
            import torch
        except Exception as exc:
            raise ImportError("rasterio, numpy et torch sont requis pour extract_deep_features") from exc

        with rasterio.open(tif_path) as src:
            arr = src.read().astype(np.float32)

        # Convertir en batch simple: (B, C, H, W)
        x = np.expand_dims(arr, axis=0)
        x = torch.from_numpy(x).to(self._device)

        with torch.no_grad():
            out = self.model(x)

        # Essayer de convertir en CPU numpy
        try:
            if isinstance(out, (list, tuple)):
                out_cpu = [o.detach().cpu().numpy() for o in out]
            else:
                out_cpu = out.detach().cpu().numpy()
        except Exception:
            out_cpu = str(type(out))

        return {"model_name": self.model_name, "features": out_cpu}


__all__ = ["PrithviClient"]
