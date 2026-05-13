import os
import pathlib
import tempfile

from nodes.base import BaseNode, NodeContext


def _stem(key: str) -> str:
    return pathlib.PurePosixPath(key).stem


class AudioExtractNode(BaseNode):
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
