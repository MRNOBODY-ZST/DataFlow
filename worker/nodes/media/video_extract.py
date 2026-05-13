import io
import os
import tempfile
from nodes.base import BaseNode, NodeContext


class VideoExtractNode(BaseNode):
    """Extract frames from a video at a given FPS using FFmpeg.

    Config:
        fps: float — frames per second to extract, default 1.0
        output_prefix: str — MinIO key prefix for output frames
    """

    def execute(self, inputs: list, ctx: NodeContext):
        import ffmpeg

        raw = inputs[0] if inputs else None
        if raw is None:
            key = ctx.config.get("key") or ctx.config.get("input_key")
            response = ctx.minio_client.get_object(ctx.input_bucket, key)
            try:
                raw = response.read()
            finally:
                response.close()
                response.release_conn()

        fps = float(ctx.config.get("fps", 1.0))
        prefix = ctx.output_key(ctx.config.get("output_prefix", "frames/"))

        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, "input.mp4")
            with open(in_path, "wb") as f:
                f.write(raw)

            out_pattern = os.path.join(tmpdir, "frame_%04d.jpg")
            (
                ffmpeg
                .input(in_path)
                .filter("fps", fps=fps)
                .output(out_pattern, format="image2", vcodec="mjpeg")
                .overwrite_output()
                .run(quiet=True)
            )

            uploaded_keys = []
            for fname in sorted(os.listdir(tmpdir)):
                if not fname.startswith("frame_"):
                    continue
                fpath = os.path.join(tmpdir, fname)
                obj_key = prefix + fname
                ctx.minio_client.fput_object(ctx.output_bucket, obj_key, fpath, content_type="image/jpeg")
                uploaded_keys.append(obj_key)

        return uploaded_keys
