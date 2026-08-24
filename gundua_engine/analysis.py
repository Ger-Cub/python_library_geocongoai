"""Module `gundua_engine` léger exposant fonctions demandées par l'utilisateur.

Contient des implémentations simples / stubs pour v1.
"""
from typing import Any, Dict, Optional

def analyse_deterministe(raster_path: str, rules: Dict[str, Any]) -> Dict[str, Any]:
    """Analyse basée sur des règles simples.

    Args:
        raster_path: chemin vers un raster (pour l'instant non utilisé en détail)
        rules: dictionnaire de règles (ex: seuils par bande)

    Returns:
        Résultats sommaires (stub)
    """
    # Implémentation minimale: retourner les règles appliquées et un champ 'ok'
    result = {"raster": raster_path, "rules_applied": rules, "summary": "stub - implémenter logique"}
    return result


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
