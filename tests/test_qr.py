import os
import tempfile
import pytest

from geocongoai.vision.qr import generate_qr


def test_generate_qr_or_skip():
    try:
        import qrcode  # noqa: F401
        from PIL import Image  # noqa: F401
    except Exception:
        pytest.skip("qrcode and Pillow not installed; install extras 'vision' to run this test")

    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        out = generate_qr("https://example.com", path)
        assert os.path.exists(out)
        assert out == path
    finally:
        if os.path.exists(path):
            os.remove(path)
