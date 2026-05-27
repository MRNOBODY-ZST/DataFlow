import os
import pathlib
import tempfile

from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


def _stem(key: str) -> str:
    return pathlib.PurePosixPath(key).stem


class AudioExtractNode(BaseNode):

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="audio_extract",
            label="音频提取",
            category="media",
            icon="MusicalNoteIcon",
            fields=[
                FieldDef(key="key", label="源文件 Key（无上游时必填）", type="file-picker",
                         placeholder="input/xxx/video.mp4"),
                FieldDef(key="format", label="音频格式", type="select",
                         placeholder="mp3", required=True,
                         options=["mp3", "aac", "wav"], inline=True),
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

        audio_format = ctx.config.get("format", "mp3")
        default_name = f"{_stem(ctx.source_key)}.{audio_format}" if ctx.source_key else f"audio.{audio_format}"
        output_key = ctx.output_key(ctx.config.get("key") or default_name)

        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, "input")
            out_path = os.path.join(tmpdir, f"audio.{audio_format}")
            with open(in_path, "wb") as f:
                f.write(raw)

            (
                ffmpeg
                .input(in_path)
                .output(out_path, **{"vn": None, "f": audio_format})
                .overwrite_output()
                .run(quiet=True)
            )

            ctx.minio_client.fput_object(ctx.output_bucket, output_key, out_path)

        return output_key
