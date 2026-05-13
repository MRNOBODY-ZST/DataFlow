import os
import tempfile

from nodes.base import BaseNode, NodeContext


class VideoTranscodeNode(BaseNode):
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

        codec = ctx.config.get("codec", "h264")
        bitrate = str(ctx.config.get("bitrate", 2000)) + "k"
        extension = "mp4" if codec in {"h264", "h265"} else "webm"
        output_key = ctx.config.get("key", f"output/{ctx.task_id}/transcoded.{extension}")

        codec_map = {
            "h264": "libx264",
            "h265": "libx265",
            "vp9": "libvpx-vp9",
        }
        video_codec = codec_map.get(codec, "libx264")

        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, "input")
            out_path = os.path.join(tmpdir, f"output.{extension}")
            with open(in_path, "wb") as f:
                f.write(raw)

            (
                ffmpeg
                .input(in_path)
                .output(out_path, vcodec=video_codec, video_bitrate=bitrate)
                .overwrite_output()
                .run(quiet=True)
            )

            ctx.minio_client.fput_object(ctx.output_bucket, output_key, out_path)

        return output_key
