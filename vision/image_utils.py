"""Helpers pour conversions d'images et chargement léger."""
from typing import Union

try:
    from PIL import Image
    import numpy as np
except Exception:
    Image = None
    np = None


def load_image(path: str):
    if Image is None:
        raise ImportError("Pillow est requis pour load_image. Installer avec `pip install Pillow`")
    return Image.open(path)


def to_array(pil_image):
    if np is None:
        raise ImportError("numpy est requis pour to_array. Installer avec `pip install numpy`")
    return np.array(pil_image)


def from_array(arr):
    if Image is None or np is None:
        raise ImportError("Pillow et numpy sont requis pour from_array. Installer avec `pip install Pillow numpy`")
    return Image.fromarray(arr)


__all__ = ["load_image", "to_array", "from_array"]
