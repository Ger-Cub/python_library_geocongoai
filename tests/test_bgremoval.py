import os
import tempfile
import pytest
from PIL import Image

from geocongoai.vision.bgremoval import remove_background, supprimer_background


def test_remove_background_with_pil_image():
    try:
        import rembg  # noqa: F401
    except Exception:
        pytest.skip("rembg not installed; skipping test")

    # Create dummy PIL image
    img = Image.new("RGB", (50, 50), color="red")
    result = remove_background(img)

    assert result is not None
    assert isinstance(result, Image.Image)


def test_remove_background_with_file_path():
    try:
        import rembg  # noqa: F401
    except Exception:
        pytest.skip("rembg not installed; skipping test")

    # Create temp image file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_in:
        in_path = tmp_in.name
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_out:
        out_path = tmp_out.name

    try:
        img = Image.new("RGB", (40, 40), color="green")
        img.save(in_path)

        res = supprimer_background(in_path, out_path=out_path)
        assert os.path.exists(out_path)
        assert isinstance(res, Image.Image)
    finally:
        if os.path.exists(in_path):
            os.remove(in_path)
        if os.path.exists(out_path):
            os.remove(out_path)


def test_remove_background_file_not_found():
    with pytest.raises(FileNotFoundError):
        remove_background("non_existent_image_file_12345.jpg")
