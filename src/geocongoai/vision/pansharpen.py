"""Pansharpening utilities (méthode Brovey, portage léger).

Dépend de `rasterio` et `numpy`. Si `rasterio` n'est pas installé, la fonction lève une erreur informative.
"""
from typing import Optional

try:
    import numpy as np
    import rasterio
    from rasterio.enums import Resampling
except Exception:
    np = None
    rasterio = None


def pansharpen_brovey(ms_path: str, pan_path: str, out_path: str) -> str:
    """Réalise un pansharpen basique par Brovey pour 3 bandes (R,G,B).

    Args:
        ms_path: chemin vers l'image multispectrale (3 bandes attendues)
        pan_path: chemin vers la bande panchromatique (1 bande)
        out_path: chemin de sortie

    Returns:
        out_path
    """
    if rasterio is None or np is None:
        raise ImportError("rasterio et numpy sont requis pour pansharpen_brovey. Installer avec `pip install rasterio numpy`")

    with rasterio.open(pan_path) as pan_src:
        pan = pan_src.read(1).astype(np.float32)
        meta = pan_src.meta.copy()

    with rasterio.open(ms_path) as ms_src:
        # lire les 3 premières bandes et rééchantillonner à la résolution PAN
        ms = ms_src.read(
            [1, 2, 3],
            out_shape=(3, pan.shape[0], pan.shape[1]),
            resampling=Resampling.bilinear
        ).astype(np.float32)

    # Eviter division par zéro
    denom = ms.sum(axis=0)
    denom[denom == 0] = 1.0

    # Brovey transform
    brovey = np.empty_like(ms)
    for i in range(3):
        brovey[i] = (ms[i] / denom) * pan

    # clip et convertir
    brovey = np.clip(brovey, 0, np.iinfo(np.uint16).max).astype(np.uint16)

    meta.update({
        "count": 3,
        "dtype": "uint16",
        "height": pan.shape[0],
        "width": pan.shape[1]
    })

    with rasterio.open(out_path, "w", **meta) as dst:
        dst.write(brovey)

    return out_path


__all__ = ["pansharpen_brovey"]
