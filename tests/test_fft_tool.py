import numpy as np
from fft_tool.fft_tool import compute_fft
from pathlib import Path


def test_compute_fft(tmp_path):
    # create a simple 4×4 image
    arr = np.arange(16, dtype=np.uint8).reshape((4, 4))
    img_path = tmp_path / "in.png"
    out_mag = tmp_path / "mag.png"
    out_phase = tmp_path / "phase.png"
    # save arr as PNG
    from PIL import Image

    Image.fromarray(arr).save(img_path)

    meta = compute_fft(str(img_path), str(out_mag), str(out_phase))
    assert "mag_min" in meta and "mag_max" in meta
    assert out_mag.exists()
    assert out_phase.exists()
