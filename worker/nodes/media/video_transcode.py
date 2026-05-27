import os
import pathlib
import tempfile

from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


def _stem(key: str) -> str:
    return pathlib.PurePosixPath(key).stem


class VideoTranscodeNode(BaseNode):

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="video_transcode",
            label="视频转码",
            category="media",
            icon="VideoCameraIcon",
            fields=[
                FieldDef(key="key", label="源文件 Key（无上游时必填）", type="file-picker",
                         placeholder="input/xxx/video.mp4"),
                FieldDef(key="codec", label="编码格式", type="select",
                         placeholder="h264", required=True,
                         options=["h264", "h265", "vp9"], inline=True),
                FieldDef(key="bitrate", label="码率 (kbps)", type="number",
                         placeholder="2000", inline=True),
            ],
        )

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
        default_name = f"{_stem(ctx.source_key)}.{extension}" if ctx.source_key else f"transcoded.{extension}"
        output_key = ctx.output_key(ctx.config.get("key") or default_name)

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
