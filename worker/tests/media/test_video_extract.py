import os
import pytest

try:
    import ffmpeg  # noqa: F401
    HAS_FFMPEG = True
except ImportError:
    HAS_FFMPEG = False

pytestmark = pytest.mark.skipif(not HAS_FFMPEG, reason="ffmpeg not installed")


def test_video_extract_uploads_frames(mock_minio, ctx, tmp_path):
    sample = _create_sample_video(tmp_path)
    mock_minio.store["in/v.mp4"] = sample
    ctx.config = {"key": "v.mp4", "fps": 0.5, "output_prefix": "frames/"}
    from nodes.media.video_extract import VideoExtractNode

    out = VideoExtractNode().execute([], ctx)
    assert isinstance(out, list)
    assert len(out) >= 1


def _create_sample_video(tmp_path) -> bytes:
    import ffmpeg
    import numpy as np
    from PIL import Image

    arr = np.zeros((16, 16, 3), dtype=np.uint8)
    for i in range(16):
        arr[i, :, 0] = i * 15
    img = Image.fromarray(arr)
    frame_path = str(tmp_path / "f.png")
    img.save(frame_path)
    out_path = str(tmp_path / "in.mp4")
    ffmpeg.input(frame_path, framerate=1).output(out_path).overwrite_output().run(quiet=True)
    with open(out_path, "rb") as f:
        return f.read()
