import os
import pathlib
import tempfile

import ffmpeg

from nodes.base import BaseNode, NodeContext
from nodes._input_utils import resolve_media_bytes


def _stem(key: str) -> str:
    return pathlib.PurePosixPath(key).stem


class VideoTranscodeNode(BaseNode):
    def execute(self, inputs: list, ctx: NodeContext):
        try:
            raw = resolve_media_bytes(inputs, ctx, "video_transcode")

            want = ctx.config.get("codec", "h264")
            bitrate = str(ctx.config.get("bitrate", 2000)) + "k"
            candidate_ext = {
                "h264": "mp4", "h265": "mp4", "vp9": "webm",
            }
            codecs_by_want = {
                "h264": ["libx264", "h264_mf", "mpeg4"],
                "h265": ["libx265", "hevc_mf", "mpeg4"],
                "vp9": ["libvpx-vp9", "libtheora"],
            }
            extensions_by_codec = {
                "libx264": "mp4", "h264_mf": "mp4", "mpeg4": "mp4",
                "libx265": "mp4", "hevc_mf": "mp4",
                "libvpx-vp9": "webm", "libtheora": "ogv",
            }

            chosen_codec = None
            chosen_ext = candidate_ext.get(want, "mp4")
            tempdir = tempfile.mkdtemp()
            try:
                in_path = os.path.join(tempdir, "input")
                with open(in_path, "wb") as f:
                    f.write(raw)

                for candidate in codecs_by_want.get(want, ["libx264", "mpeg4"]):
                    ext = extensions_by_codec.get(candidate, chosen_ext)
                    out_path = os.path.join(tempdir, f"output.{ext}")
                    try:
                        (
                            ffmpeg.input(in_path)
                            .output(out_path, vcodec=candidate, video_bitrate=bitrate)
                            .overwrite_output()
                            .run(quiet=True)
                        )
                        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                            chosen_codec = candidate
                            chosen_ext = ext
                            break
                    except Exception:
                        continue

                if chosen_codec is None:
                    raise RuntimeError(
                        f"视频转码: 找不到可用的 {want} 编码器。"
                        f"请安装带 libx264/libx265 的 GPL 版 FFmpeg。"
                    )

                stem = _stem(ctx.config.get("key") or getattr(ctx, "source_key", None) or "transcoded")
                default_name = f"{stem}.{chosen_ext}"
                output_key = ctx.output_key(default_name)
                final_path = os.path.join(tempdir, f"output.{chosen_ext}")

                ctx.minio_client.fput_object(ctx.output_bucket, output_key, final_path)
            finally:
                import shutil
                shutil.rmtree(tempdir, ignore_errors=True)

            return output_key
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"视频转码: {e}")
