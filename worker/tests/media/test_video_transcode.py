import os
import pytest

try:
    import ffmpeg  # noqa: F401
    HAS_FFMPEG = True
except ImportError:
    HAS_FFMPEG = False

pytestmark = pytest.mark.skipif(not HAS_FFMPEG, reason="ffmpeg not installed")


def test_video_transcode_h264(mock_minio, ctx, tmp_path):
    sample = _create_sample_video(tmp_path)
    mock_minio.store["in/v.mp4"] = sample
    ctx.config = {"key": "v.mp4", "codec": "h264", "bitrate": 500}
    ctx.source_key = "v.mp4"
    from nodes.media.video_transcode import VideoTranscodeNode

    out = VideoTranscodeNode().execute([], ctx)
    assert isinstance(out, str)
    assert out.endswith(".mp4")
    assert len(mock_minio.fput_calls) == 1


def test_video_transcode_h265(mock_minio, ctx, tmp_path):
    sample = _create_sample_video(tmp_path)
    mock_minio.store["in/v.mp4"] = sample
    ctx.config = {"key": "v.mp4", "codec": "h265", "bitrate": 500}
    ctx.source_key = "v.mp4"
    from nodes.media.video_transcode import VideoTranscodeNode

    out = VideoTranscodeNode().execute([], ctx)
    assert isinstance(out, str)


def test_video_transcode_vp9_webm(mock_minio, ctx, tmp_path):
    sample = _create_sample_video(tmp_path)
    mock_minio.store["in/v.mp4"] = sample
    ctx.config = {"key": "v.mp4", "codec": "vp9", "bitrate": 500}
    ctx.source_key = "v.mp4"
    from nodes.media.video_transcode import VideoTranscodeNode

    out = VideoTranscodeNode().execute([], ctx)
    assert isinstance(out, str)
    assert out.endswith(".webm") or out.endswith(".ogv")


def _create_sample_video(tmp_path) -> bytes:
    import ffmpeg
    import numpy as np

    arr = np.zeros((16, 16, 3), dtype=np.uint8)
    from PIL import Image
    img = Image.fromarray(arr)
    frame_path = str(tmp_path / "f.png")
    img.save(frame_path)
    out_path = str(tmp_path / "in.mp4")
    ffmpeg.input(frame_path, framerate=1).output(out_path, vcodec="mpeg4").overwrite_output().run(quiet=True)
    with open(out_path, "rb") as f:
        return f.read()
