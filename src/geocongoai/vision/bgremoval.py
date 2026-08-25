"""Wrapper léger pour suppression de fond d'images (rembg).

Cette fonction est optionnelle et doit être installée via extras: `pip install geocongoai[vision]`
"""
import io
import importlib
import os
from typing import Optional, Union, Any

def remove_background(
    input_image: Union[str, os.PathLike, Any],
    out_path: Optional[Union[str, os.PathLike]] = None,
    session: Optional[Any] = None,
    **kwargs: Any
) -> Any:
    """Supprime le fond d'une image en utilisant `rembg`.

    Args:
        input_image: Chemin vers l'image (str/Path) ou instance PIL.Image.Image.
        out_path: Chemin de sauvegarde (optionnel). Si None, l'image résultat est retournée.
        session: Session rembg optionnelle (ex: rembg.new_session("u2net")).
        **kwargs: Arguments supplémentaires passés à `rembg.remove`.

    Returns:
        PIL.Image.Image: Image résultat avec fond transparent (RGBA).

    Raises:
        ImportError: Si `rembg` ou `Pillow` ne sont pas installés.
        FileNotFoundError: Si le fichier image spécifié n'existe pas.
        RuntimeError: Si une erreur survient durant l'initialisation ou l'exécution de rembg.
    """
    importlib.invalidate_caches()

    # 1. Vérification de PIL / Pillow
    try:
        from PIL import Image
    except (ImportError, ModuleNotFoundError) as err:
        raise ImportError(
            "Pillow est requis pour remove_background. Installer avec `pip install Pillow` ou `pip install geocongoai[vision]`"
        ) from err

    # 2. Vérification de rembg
    try:
        from rembg import remove as rembg_remove
    except (ImportError, ModuleNotFoundError) as err:
        raise ImportError(
            "rembg est requis pour remove_background. Installer avec `pip install rembg Pillow` ou `pip install geocongoai[vision]`"
        ) from err
    except Exception as err:
        raise RuntimeError(
            f"Erreur d'importation de la dépendance rembg ({err.__class__.__name__}: {err}). "
            "Vérifiez que rembg et ses dépendances (onnxruntime, etc.) sont correctement installés."
        ) from err

    # 3. Chargement de l'image source
    if isinstance(input_image, (str, os.PathLike)):
        img_path = str(input_image)
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Fichier image introuvable : '{img_path}'")
        try:
            img = Image.open(img_path)
        except Exception as err:
            raise RuntimeError(f"Impossible d'ouvrir l'image '{img_path}' avec Pillow: {err}") from err
    elif hasattr(input_image, "convert") or isinstance(input_image, Image.Image):
        img = input_image
    else:
        raise TypeError(f"Type d'image d'entrée non supporté : {type(input_image)}")

    # 4. Traitement du détourage
    try:
        if session is not None:
            output = rembg_remove(img, session=session, **kwargs)
        else:
            output = rembg_remove(img, **kwargs)
    except Exception as err:
        raise RuntimeError(
            f"Erreur lors de l'exécution de rembg.remove: {err.__class__.__name__} - {err}"
        ) from err

    # 5. Conversion du résultat en PIL.Image si nécessaire
    if not isinstance(output, Image.Image):
        if isinstance(output, bytes):
            output = Image.open(io.BytesIO(output))
        elif hasattr(output, "__array__"):
            output = Image.fromarray(output)
        else:
            raise TypeError(f"Le format retourné par rembg ({type(output)}) ne peut pas être converti en PIL.Image.")

    # 6. Sauvegarde optionnelle
    if out_path:
        out_path_str = str(out_path)
        out_dir = os.path.dirname(out_path_str)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        output.save(out_path_str)

    return output


def supprimer_background(*args: Any, **kwargs: Any) -> Any:
    """Alias francisé pour remove_background."""
    return remove_background(*args, **kwargs)


__all__ = ["remove_background", "supprimer_background"]

