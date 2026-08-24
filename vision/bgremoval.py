"""Wrapper léger pour suppression de fond d'images (rembg).

Cette fonction est optionnelle et doit être installée via extras: `pip install geocongoai[vision]`
"""
from typing import Optional, Union

try:
    from PIL import Image
except Exception:
    Image = None

def remove_background(input_image: Union[str, "Image.Image"], out_path: Optional[str] = None) -> "Image.Image":
    """Supprime le fond d'une image en utilisant `rembg`.

    Args:
        input_image: chemin vers l'image ou instance PIL.Image
        out_path: chemin de sauvegarde (optionnel). Si None, l'image résultat est retournée.

    Returns:
        PIL.Image résultat

    Raises:
        ImportError si `rembg` ou `Pillow` manquent
    """
    try:
        from rembg import remove as rembg_remove
    except Exception:
        raise ImportError("rembg est requis pour remove_background. Installer avec `pip install rembg Pillow`")

    if Image is None:
        raise ImportError("Pillow est requis pour remove_background. Installer avec `pip install Pillow`")

    if isinstance(input_image, str):
        img = Image.open(input_image)
    else:
        img = input_image

    output = rembg_remove(img)
    if out_path:
        output.save(out_path)
    return output


def supprimer_background(*args, **kwargs):
    return remove_background(*args, **kwargs)


__all__ = ["remove_background", "supprimer_background"]
