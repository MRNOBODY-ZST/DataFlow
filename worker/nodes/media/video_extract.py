import io
import os
import tempfile
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import resolve_media_bytes


class VideoExtractNode(BaseNode):
    """Extract frames from a video at a given FPS using FFmpeg."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            import ffmpeg

            raw = resolve_media_bytes(inputs, ctx, "video_extract")

            fps = float(ctx.config.get("fps", 1.0))
            if fps <= 0:
                raise RuntimeError("视频抽帧: fps 必须大于 0。")
            prefix = ctx.output_key(ctx.config.get("output_prefix", "frames/"))

            with tempfile.TemporaryDirectory() as tmpdir:
                in_path = os.path.join(tmpdir, "input.mp4")
                with open(in_path, "wb") as f:
                    f.write(raw)

                out_pattern = os.path.join(tmpdir, "frame_%04d.jpg")
                try:
                    (
                        ffmpeg.input(in_path)
                        .filter("fps", fps=fps)
                        .output(out_pattern, format="image2", vcodec="mjpeg")
                        .overwrite_output()
                        .run(quiet=True)
                    )
                except Exception as e:
                    raise RuntimeError(
                        f"视频抽帧: FFmpeg 抽帧失败。"
                        f"请确认输入是有效的视频（MP4/MOV/AVI 等）。底层错误: {e}"
                    )

                uploaded_keys = []
                for fname in sorted(os.listdir(tmpdir)):
                    if not fname.startswith("frame_"):
                        continue
                    fpath = os.path.join(tmpdir, fname)
                    obj_key = prefix + fname
                    ctx.minio_client.fput_object(ctx.output_bucket, obj_key, fpath, content_type="image/jpeg")
                    uploaded_keys.append(obj_key)

            if not uploaded_keys:
                raise RuntimeError(
                    f"视频抽帧: 抽帧结果为空。可能 fps={fps} 过小或视频过短。"
                )

            return uploaded_keys
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"视频抽帧: {e}")
