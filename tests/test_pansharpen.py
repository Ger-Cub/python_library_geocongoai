import os
import tempfile
import numpy as np
import pytest

from geocongoai.vision.pansharpen import pansharpen_brovey


def create_dummy_tiff(path, bands, height=16, width=16, dtype="uint16"):
    import rasterio

    meta = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": bands,
        "dtype": dtype,
    }
    data = (np.random.rand(bands, height, width) * 1000).astype(dtype)
    with rasterio.open(path, "w", **meta) as dst:
        dst.write(data)


def test_pansharpen_brovey_or_skip():
    try:
        import rasterio  # noqa: F401
        import numpy as _np  # noqa: F401
    except Exception:
        pytest.skip("rasterio/numpy not installed; install extras 'vision' to run this test")

    tmpdir = tempfile.mkdtemp()
    ms_path = os.path.join(tmpdir, "ms.tif")
    pan_path = os.path.join(tmpdir, "pan.tif")
    out_path = os.path.join(tmpdir, "out.tif")

    try:
        # multispectral with 3 bands
        create_dummy_tiff(ms_path, bands=3, height=8, width=8)
        # panchromatic single band but higher size to simulate HR
        create_dummy_tiff(pan_path, bands=1, height=16, width=16)

        out = pansharpen_brovey(ms_path, pan_path, out_path)
        assert os.path.exists(out)

        import rasterio

        with rasterio.open(out) as src:
            assert src.count == 3
    finally:
        for p in [ms_path, pan_path, out_path]:
            if os.path.exists(p):
                os.remove(p)
        try:
            os.rmdir(tmpdir)
        except Exception:
            pass
