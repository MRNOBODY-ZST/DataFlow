# Worker Tests 依赖

测试分为"必装"与"可选"两类。未装的可选包会被 pytest 自动 skip，不影响 164 条核心用例通过。

## 一、必装（164 tests，0 skip）

```bash
pip install pytest pandas jmespath pillow opencv-python-headless rasterio minio
```

| 包 | 用途 | 用例数 |
| --- | --- | --- |
| `pytest` | 测试框架 | — |
| `pandas` | csv_reader / csv_writer / filter / map / aggregate / preview | 55 |
| `jmespath` | json_transform | 4 |
| `pillow` | image_resize / blur / edge / sharpen / pooling / convolution / threshold / format_convert | 35 |
| `opencv-python-headless` | image_edge_detect 的 sobel 路径 + image_threshold otsu | 6 |
| `rasterio` | droneIndices / S2Indices / image_drone_index / image_s2_indices / format_convert tiff 分支 | 44 |
| `minio` | minio_reader / minio_writer / NodeContext 类型声明 | 8 |

## 二、可选（装了可多跑 7 条，不装即 skip）

```bash
pip install easyocr ffmpeg-python
```

| 包 | 系统依赖 | 用例 | 备注 |
| --- | --- | --- | --- |
| `easyocr` | 无 | `tests/media/test_image_ocr.py`（1 条 smoke） | 首次运行会下载模型（~10s + 200MB）；可设 `EASYOCR_SKIP=1` 继续跳过 |
| `ffmpeg-python` | **需系统装 ffmpeg 二进制** | `tests/media/test_audio_extract.py`、`test_video_extract.py`、`test_video_transcode.py`（共 6 条）| 没装系统 ffmpeg 二进制时，3 个文件全 skip |

系统 ffmpeg 安装：
- Windows：`choco install ffmpeg` 或 https://www.gyan.dev/ffmpeg/builds/
- Linux：`apt install ffmpeg`
- Mac：`brew install ffmpeg`

## 三、Stub 依赖（不需要装）

- `ray`、`kafka-python`、`pymongo`、`reporter` — 测试里全部通过 `conftest.py` 自动注入 stub 绕过；executor / dispatcher 的纯函数用例（拓扑排序、normalize graph）不依赖这些包。
- 想跑完整 Ray 分布式端到端时再装：`pip install ray kafka-python pymongo`。

## 四、一键装

```bash
# 仅核心用例（推荐，~2min）
pip install pytest pandas jmespath pillow opencv-python-headless rasterio minio

# 可选增强
pip install easyocr ffmpeg-python

# 生成 requirements.txt 锁版本
pip freeze > requirements.lock
```

## 五、运行

```bash
cd worker
.\run_tests.bat               # 默认：跳过 OCR / 音视频
.\run_tests.bat --fast        # 只跑轻量模块（< 30s）
.\run_tests.bat --indices    # 只跑 drone + S2 指数
.\run_tests.bat --all        # 含 7 条 skip（没装就真 skip）
**Q: 想重跑某一组失败的用例**
#python -m pytest tests/ --tb=short -q
python -m pytest tests/droneIndices -v
```

## 六、当前环境验证结果

```
python -m pytest tests/ --tb=short -q
164 passed, 7 skipped, 0 failed
```

（Windows / Python 3.x / 已装必装、未装 easyocr & ffmpeg 二进制）
