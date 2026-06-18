import os
import pytest

try:
    import ffmpeg  # noqa: F401
    HAS_FFMPEG = True
except ImportError:
    HAS_FFMPEG = False

pytestmark = pytest.mark.skipif(not HAS_FFMPEG, reason="ffmpeg not installed")


def test_audio_extract_fput_called(mock_minio, ctx, tmp_path):
    sample = _create_sample_video(tmp_path)
    mock_minio.store["in/video.mp4"] = sample

    from nodes.media.audio_extract import AudioExtractNode

    ctx.config = {"key": "video.mp4", "format": "mp3"}
    ctx.source_key = "video.mp4"
    out = AudioExtractNode().execute([], ctx)
    assert isinstance(out, str)
    assert out.endswith(".mp3")
    assert len(mock_minio.fput_calls) == 1


def _create_sample_video(tmp_path) -> bytes:
    import ffmpeg
    import numpy as np
    tmp_out = tmp_path / "out.mp4"
    arr = np.zeros((16, 16, 3), dtype=np.uint8)
    for i in range(16):
        arr[i, :, 0] = i * 15
    from PIL import Image
    img = Image.fromarray(arr)
    buf = str(tmp_path / "frame.png")
    img.save(buf)
    ffmpeg.input(buf, framerate=1).output(str(tmp_out), vcodec="mpeg4").overwrite_output().run(quiet=True)
    with open(tmp_out, "rb") as f:
        return f.read()
