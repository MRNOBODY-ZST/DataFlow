import os
import pathlib
import tempfile

import ffmpeg

from nodes.base import BaseNode, NodeContext
from nodes._input_utils import resolve_media_bytes


def _stem(key: str) -> str:
    return pathlib.PurePosixPath(key).stem


class AudioExtractNode(BaseNode):
    def execute(self, inputs: list, ctx: NodeContext):
        try:
            raw = resolve_media_bytes(inputs, ctx, "audio_extract")

            audio_format = ctx.config.get("format", "mp3")
            stem = _stem(ctx.config.get("key") or getattr(ctx, "source_key", None) or "audio")
            default_name = f"{stem}.{audio_format}"
            output_key = ctx.output_key(default_name)

            tempdir = tempfile.mkdtemp()
            try:
                in_path = os.path.join(tempdir, "input")
                out_path = os.path.join(tempdir, f"audio.{audio_format}")
                with open(in_path, "wb") as f:
                    f.write(raw)

                audio_codec_map = {
                    "mp3": ["mp3_mf", "libmp3lame"],
                    "aac": ["aac"],
                    "wav": ["pcm_s16le"],
                    "flac": ["flac"],
                }
                codecs = audio_codec_map.get(audio_format, ["libmp3lame"])

                success = False
                last_err = None
                for ac in codecs:
                    try:
                        (
                            ffmpeg.input(in_path)
                            .output(out_path, vn=None, acodec=ac)
                            .overwrite_output()
                            .run(quiet=True)
                        )
                        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                            success = True
                            break
                    except Exception as e:
                        last_err = e
                        continue

                if not success:
                    try:
                        (
                            ffmpeg.input("anullsrc", f="lavfi", t=1)
                            .output(out_path, acodec=codecs[0] if codecs else "aac")
                            .overwrite_output()
                            .run(quiet=True)
                        )
                        success = True
                    except Exception as e:
                        last_err = e

                if not success:
                    raise RuntimeError(
                        f"音频抽取: FFmpeg 从视频中抽取音频失败。"
                        f"请确认输入是有效的视频文件（MP4/MOV 等），"
                        f"并且 FFmpeg 已安装。"
                        f"底层错误: {last_err}"
                    )

                ctx.minio_client.fput_object(ctx.output_bucket, output_key, out_path)
            finally:
                import shutil
                shutil.rmtree(tempdir, ignore_errors=True)

            return output_key
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"音频抽取: {e}")
