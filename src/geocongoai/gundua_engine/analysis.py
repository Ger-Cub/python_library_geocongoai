"""Module `gundua_engine` pour l'analyse déterministe et le traitement d'images géospatiales."""
from typing import Any, Dict, Optional

try:
    import numpy as np
    import rasterio
except ImportError:
    np = None
    rasterio = None


def analyse_deterministe(raster_path: str, rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Analyse basée sur des règles déterministes et calculs d'indices spectraux (NDVI, NDWI).

    Args:
        raster_path: chemin vers un fichier raster TIFF
        rules: dictionnaire de règles ou seuils (ex: {"index": "NDVI", "threshold": 0.3})

    Returns:
        Dictionnaire avec les résultats d'analyse et statistiques des indices
    """
    rules = rules or {}
    index_type = rules.get("index", "NDVI").upper()
    threshold = float(rules.get("threshold", 0.2))

    if rasterio is None or np is None:
        return {
            "raster": raster_path,
            "rules_applied": rules,
            "status": "warning",
            "message": "rasterio et numpy sont requis pour l'analyse spectrale complète.",
            "summary": "logique déterministe basée sur les règles sans rasterio",
        }

    try:
        with rasterio.open(raster_path) as src:
            meta = {
                "width": src.width,
                "height": src.height,
                "count": src.count,
                "crs": str(src.crs),
            }

            if src.count < 2:
                return {
                    "raster": raster_path,
                    "meta": meta,
                    "error": "Le raster doit contenir au moins 2 bandes pour calculer un indice spectral.",
                }

            # Si au moins 4 bandes (Sentinel-2 standard: B2=B, B3=G, B4=R, B8=NIR)
            if index_type == "NDVI" and src.count >= 4:
                red = src.read(3).astype(np.float32)
                nir = src.read(4).astype(np.float32)
                denom = nir + red
                denom[denom == 0] = 1.0
                spectral_index = (nir - red) / denom
            elif index_type == "NDWI" and src.count >= 3:
                green = src.read(2).astype(np.float32)
                nir = src.read(4 if src.count >= 4 else 3).astype(np.float32)
                denom = green + nir
                denom[denom == 0] = 1.0
                spectral_index = (green - nir) / denom
            else:
                b1 = src.read(1).astype(np.float32)
                b2 = src.read(2).astype(np.float32)
                denom = b1 + b2
                denom[denom == 0] = 1.0
                spectral_index = (b2 - b1) / denom

            mask = spectral_index > threshold
            percentage_above_threshold = float(np.mean(mask) * 100)
            mean_index = float(np.mean(spectral_index))

            return {
                "raster": raster_path,
                "meta": meta,
                "rules_applied": rules,
                "index_used": index_type,
                "threshold": threshold,
                "mean_index": round(mean_index, 4),
                "percentage_above_threshold": round(percentage_above_threshold, 2),
                "status": "success",
            }
    except Exception as exc:
        return {
            "raster": raster_path,
            "rules_applied": rules,
            "error": f"Erreur d'analyse du raster: {exc}",
        }


def analyse_ia_fondation(coords_or_tif: str, model_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Appelle le client IA (Prithvi) pour extraire des caractéristiques profondes.

    Si `terratorch` n'est pas installé, la fonction renvoie un message explicite.
    """
    try:
        from geocongoai.ia import PrithviClient
    except Exception:
        return {"error": "Prithvi non disponible: installer geocongoai[ia] (terratorch, torch)"}

    client = PrithviClient(model_name=model_name or "prithvi_eo_v2_300")
    try:
        features = client.extract_deep_features(coords_or_tif, **kwargs)
    except Exception as exc:
        return {"error": str(exc)}

    return {"features": features}


def traiter_image_satellite(ms_path: str = None, pan_path: str = None, out_path: str = None, method: str = "pansharpen") -> Dict[str, Any]:
    """Point d'entrée simple pour traitements d'images satellites.

    Args:
        ms_path: chemin multispectral
        pan_path: chemin panchromatique
        out_path: sortie
        method: méthode de traitement (par défaut 'pansharpen')
    """
    if method == "pansharpen":
        if not (ms_path and pan_path and out_path):
            return {"error": "ms_path, pan_path et out_path requis pour pansharpen"}
        try:
            from geocongoai.vision.pansharpen import pansharpen_brovey
        except Exception:
            return {"error": "rasterio/numpy requis pour pansharpen"}

        out = pansharpen_brovey(ms_path, pan_path, out_path)
        return {"out_path": out}

    return {"error": f"Méthode inconnue: {method}"}


__all__ = ["analyse_deterministe", "analyse_ia_fondation", "traiter_image_satellite"]
