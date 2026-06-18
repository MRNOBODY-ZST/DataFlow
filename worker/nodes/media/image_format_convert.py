import io
import numpy as np
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import resolve_media_bytes


class ImageFormatConvertNode(BaseNode):
    """Convert image format with rasterio fallback for TIF/TIFF."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            from PIL import Image

            raw = resolve_media_bytes(inputs, ctx, "image_format_convert")
            target_format = ctx.config.get("format", "PNG").upper()
            if not target_format:
                raise RuntimeError(
                    "图像格式转换: 请在节点配置中设置 format（如 'PNG'/'JPEG'/'TIFF'）。"
                )

            try:
                import rasterio
                with rasterio.MemoryFile(raw) as mf:
                    with mf.open() as src:
                        arr = src.read()
                        arr = np.squeeze(arr)
                        arr_min, arr_max = np.nanmin(arr), np.nanmax(arr)
                        if arr_max - arr_min < 1e-8:
                            arr_scaled = np.zeros_like(arr, dtype=np.uint8)
                        else:
                            arr_scaled = ((arr - arr_min) / (arr_max - arr_min) * 255).astype(np.uint8)
                        if len(arr_scaled.shape) == 3:
                            img = Image.fromarray(np.transpose(arr_scaled, (1, 2, 0)))
                        else:
                            img = Image.fromarray(arr_scaled, "L")
            except RuntimeError:
                raise
            except Exception:
                try:
                    img = Image.open(io.BytesIO(raw))
                except Exception as e:
                    raise RuntimeError(
                        f"图像格式转换: 无法解析输入文件。"
                        f"请确认是有效的图片（PNG/JPEG/TIFF），实际收到的是 {len(raw)} 字节。"
                    ) from e

            if img.mode == "F":
                arr = np.array(img, dtype=np.float32)
                arr_min, arr_max = np.nanmin(arr), np.nanmax(arr)
                arr_scaled = ((arr - arr_min) / (arr_max - arr_min) * 255).astype(np.uint8) if arr_max > arr_min else np.zeros_like(arr, dtype=np.uint8)
                img = Image.fromarray(arr_scaled, "L")

            if target_format in ("JPEG", "JPG"):
                if img.mode in ("RGBA", "LA"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode == "P":
                    img = img.convert("RGB")
                elif img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

            buf = io.BytesIO()
            img.save(buf, format=target_format)
            return buf.getvalue()
        except (ValueError, TypeError, OSError, RuntimeError):
            raise
        except Exception as e:
            raise RuntimeError(f"图像格式转换: {e}")
