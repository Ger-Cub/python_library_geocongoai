"""Génération de QR codes (wrapper simple autour de `qrcode` + Pillow)."""
from typing import Optional

try:
    import qrcode
    from PIL import Image
except Exception:  # keep optional
    qrcode = None
    Image = None


def generate_qr(data: str, out_path: str, box_size: int = 10, border: int = 4) -> str:
    """Génère un QR code et l'enregistre.

    Args:
        data: chaîne à encoder
        out_path: chemin de sortie (ex: 'qrcode.png')
        box_size: taille de chaque point
        border: bordure

    Returns:
        Le chemin du fichier écrit
    """
    if qrcode is None or Image is None:
        raise ImportError("qrcode et Pillow sont requis pour generate_qr. Installer avec `pip install qrcode[pil] Pillow`")

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img.save(out_path)
    return out_path


def generer_qr(*args, **kwargs):
    """Alias français pour `generate_qr`."""
    return generate_qr(*args, **kwargs)


__all__ = ["generate_qr", "generer_qr"]
