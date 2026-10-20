# Worker 算子单元测试计划

## 一、调研结论

### 项目概述
worker 是一个基于 Ray 的 Python 任务执行器，负责后端发布的 pipeline DAG 计算。核心入口：
- [executor.py](file:///D:/zuoye/DataFlow-main/worker/executor.py)：DAG 拓扑排序 + Ray 分布式 fan-out
- [dispatcher.py](file:///D:/zuoye/DataFlow-main/worker/dispatcher.py)：Kafka consumer + MongoDB graph 拉取
- [base.py](file:///D:/zuoye/DataFlow-main/worker/nodes/base.py)：`BaseNode` ABC + `NodeContext` dataclass

### 依赖
`requirements.txt`：`ray` `kafka-python` `minio` `pillow` `opencv-python-headless` `easyocr` `ffmpeg-python` `pandas` `jmespath` `pytest` `pymongo`

### 关键发现
1. **每个算子都有 `BaseNode.execute(inputs, ctx)` 统一签名**，`NodeContext` 含 MinIO client + bucket 配置。
2. **没有任何现有测试** — `worker/` 下没有 `test_*.py`、`tests/` 或 `conftest.py`。
3. **算子总数 = 41 个**，全部在 [nodes/__init__.py](file:///D:/zuoye/DataFlow-main/worker/nodes/__init__.py#L51-L102) 的 `NODE_REGISTRY` 中注册。
4. **MinIO 是最大外部依赖** — 所有 reader/writer 都访问 MinIO；图像算子则大多通过 `inputs[0]` bytes 传入。
5. **Ray/Kafka/Mongo 是 dispatcher 级依赖** — 算子本身不依赖 Ray，单元测试可完全绕开。

### 测试策略
- 用 **pytest + monkeypatch**：mock MinIO client（只需 `get_object / put_object / list_objects / fput_object` 四个方法）。
- 对图像 / 视频 / OCR 算子用内存 bytes 构造真实 PIL / rasterio / ffmpeg 输入，不必起外部服务。
- 每个测试文件只包含该模块的**功能点**（输入、输出、边界、错误），不重复造复杂 fixture。
- `pytest` 已在 `requirements.txt`，直接用。

---

## 二、测试目录结构

```
worker/
├── tests/
│   ├── conftest.py                     # fixture: mock_minio, sample_tiff_bytes, sample_image_bytes...
│   ├── test_executor.py                # topological_sort, run_pipeline 辅助函数
│   ├── test_dispatcher.py              # _normalize_graph, fetch_graph (mock mongo)
│   ├── readers/
│   │   ├── test_csv_reader.py
│   │   ├── test_json_reader.py
│   │   └── test_minio_reader.py
│   ├── media/
│   │   ├── test_image_resize.py
│   │   ├── test_image_format_convert.py
│   │   ├── test_image_gaussian_blur.py
│   │   ├── test_image_edge_detect.py
│   │   ├── test_image_sharpen.py
│   │   ├── test_image_pooling.py
│   │   ├── test_image_convolution.py
│   │   ├── test_image_threshold.py
│   │   ├── test_image_ocr.py           # easyocr heavy, 只测 smoke
│   │   ├── test_audio_extract.py       # 需要 ffmpeg
│   │   ├── test_video_extract.py       # 需要 ffmpeg
│   │   ├── test_video_transcode.py     # 需要 ffmpeg
│   │   ├── test_image_drone_index.py
│   │   └── test_image_s2_indices.py
│   ├── drone_indices/
│   │   ├── test_drone_base.py          # safe_divide / identify_bands / calc_*
│   │   └── test_drone_nodes.py         # 12 个单指数节点各测一个点
│   ├── S2Indices/
│   │   ├── test_s2_base.py
│   │   └── test_s2_nodes.py            # 9 个单指数节点各测一个点
│   ├── transforms/
│   │   ├── test_filter.py
│   │   ├── test_map.py
│   │   ├── test_json_mapper.py
│   │   ├── test_json_transform.py
│   │   └── test_aggregate.py
│   ├── writers/
│   │   ├── test_csv_writer.py
│   │   └── test_minio_writer.py
│   └── utils/
│       └── test_preview.py
```

共 **27 个测试文件**，覆盖全部 41 个算子 + executor/dispatcher。

---

## 三、公共 fixture (`tests/conftest.py`)

1. **`mock_minio`**：`types.SimpleNamespace`，带 `get_object / put_object / list_objects / fput_object` 可调用属性；`get_object` 返回含 `.read()/.close()/.release_conn()` 的 bytes 容器。
2. **`ctx`**：`NodeContext(task_id='t1', node_id='n1', config={}, minio_client=mock_minio, input_bucket='in', output_bucket='out', temp_bucket='tmp')`。
3. **`sample_png_bytes()`**：用 PIL 生成 32×32 RGB 随机 PNG bytes — 用于所有通用图像算子。
4. **`sample_tiff_bytes_with_bands(descriptions=['B2','B3','B4','B8'])`**：用 rasterio 生成 4 波段 GeoTIFF — 用于指数算子。
5. **`sample_csv_bytes`**：`"a,b,c\n1,2,3\n4,5,6"` 的 bytes。
6. **`sample_json_bytes`**：`'{"x":1,"y":[1,2,3]}'` 的 bytes。
7. **`sample_video_bytes`**：生成一个很短的 mp4 用 ffmpeg；若 ffmpeg 未装则返回 pytest skip。
8. **`sample_audio_bytes`**：生成一个 wav/mp3；同上 skip 策略。

---

## 四、各模块测试点

### 4.1 Base / Executor / Dispatcher

| 文件 | 测什么 |
| --- | --- |
| `test_executor.py` | 1) `_topological_sort` 线性链；2) 分支图；3) 自环报错；4) `_is_batch_result` 判定；5) `run_pipeline` 串联两个普通节点（mock NODE_REGISTRY）；6) batch fan-out 路径 |
| `test_dispatcher.py` | 1) `_normalize_graph` 正常输入；2) node 缺 id 抛；3) edge 缺 source/target 抛 |
| `test_readers/*` | 见 4.2 |

### 4.2 readers（3 个算子）

**`csv_reader`**
1. 正常 CSV bytes → DataFrame 行列数正确、数据正确
2. malformed CSV → `pd.errors.ParserError` 抛出
3. minio.get_object 返回空 → 可能异常或空 DF（按实际行为）

**`json_reader`**
1. 合法 JSON dict/list → 返回 Python 对象
2. malformed JSON → `json.JSONDecodeError`
3. 顶层是数组 vs 对象

**`minio_reader`**
1. `key` 单文件模式 → 返回 bytes
2. `prefix` 批量模式 → 返回 `[{key, data}, ...]`
3. 前缀无文件 → `FileNotFoundError`
4. 既没 key 也没 prefix → `ValueError`
5. `S3Error(NoSuchKey)` → 转为 `FileNotFoundError`
6. key 以 `/` 结尾 → 视为 batch 模式

### 4.3 transforms（5 个）

**`filter`**
1. 合法 query：`"age > 30"` 行过滤正确
2. 空 query → 返回原 DF 不变
3. 非法 query 语法 → `pandas.errors.ParserError`
4. 输入不是 DF → `TypeError`

**`map`**
1. rename 正常
2. select 正常
3. rename + select 组合（rename 先于 select）
4. select 含不存在列 → 静默忽略
5. 输入不是 DF → `TypeError`

**`aggregate`**
1. group_by + agg 正常聚合
2. group_by 空 → 返回原 DF
3. agg 空 → 返回原 DF
4. 输入不是 DF → `TypeError`

**`json_transform`**
1. JMESPath `"foo.bar"` 正常
2. `"[*].id"` 数组展开
3. 默认 `@` 返回原对象
4. 非法表达式 → jmespath 抛错

**`json_mapper`**
1. 单映射 source→target
2. 多映射、嵌套路径 `"a.b.c"`
3. 含 `[*]` 数组展开
4. default 兜底
5. mappings 空 → 返回原数据
6. 无 inputs → `ValueError`

### 4.4 media 图像通用（11 个）

**`image_resize`**
1. 给 width+height 精确 resize
2. 只给 width → 等比
3. 只给 height → 等比
4. 不给 → 原图
5. format=JPEG 正常保存
6. inputs 空走 minio fallback

**`image_format_convert`**
1. TIFF → PNG（走 rasterio 分支）
2. PNG → TIFF（走 PIL 分支）
3. RGBA → JPEG（背景合成）
4. 8-bit F 模式 float 图像 → 归一化到 L
5. 目标格式大写/小写

**`image_gaussian_blur`**
1. 默认 radius=2 输出存在且与输入尺寸相同
2. 自定义 radius=5
3. RGBA → JPEG 自动转 RGB

**`image_edge_detect`**
1. 4 种 PIL filter 枚举：find_edges / contour / edge_enhance / edge_enhance_more
2. `sobel` 方法走 numpy 路径

**`image_sharpen`**
1. 默认 unsharp_mask + 默认参数
2. `sharpen_filter`
3. `detail`
4. factor != 1.0 再额外 enhancer

**`image_pooling`**
1. method=max 正常
2. method=mean 正常
3. stride != pool_size 不同步验证输出尺寸
4. 灰度图 vs 彩色图

**`image_convolution`**
1. 7 种预设（blur/sharpen/contour/detail/edge_enhance/emboss/smooth）
2. 自定义 kernel JSON 字符串
3. kernel sum 为 0 → scale=1 兜底

**`image_threshold`**
1. 5 种方法：binary / binary_inv / truncate / to_zero / otsu
2. otsu 阈值在 0-255 之间
3. 自定义 threshold 值生效

**`image_ocr`**
1. smoke：输入含文字的 PNG → 返回非空字符串（slow 测，默认 skip）
2. 通过 `--runxfail` 或标记 skipif 环境变量 `EASYOCR_SKIP=1`

**`audio_extract` / `video_extract` / `video_transcode`**
1. 需要 ffmpeg，测 `ffmpeg` import 失败时 skip
2. 正常路径：minio_client 收到 `fput_object` 调用
3. audio 不同 format 参数；video 不同 codec

**`image_drone_index` / `image_s2_indices`（平台节点）**
1. 输入 4 波段 tiff → 输出 `{"multi_files": [bytes, ...]}`
2. multi_files 长度 = 支持的指数个数
3. 每个 bytes 都是合法 GeoTIFF（用 rasterio 打开验证）
4. minio fallback（inputs 为空）

### 4.5 droneIndices 基础 + 12 个单指数节点

**`droneIndices/test_drone_base.py`**
1. `safe_divide` 分母 0 时返回 nan
2. `normalize_name` 去空格/下划线/连字符并小写
3. `identify_bands` 对 descriptions `['Red','NIR','Green','RedEdge']` 识别正确
4. `calc_ndvi` 用简单数组手动算出预期值对比
5. 所有 `calc_*` 函数 smoke

**`droneIndices/test_drone_nodes.py`**
12 个节点（ndvi / gndvi / ndre / lci / sipi2 / gci / cirededge / ngrdi / rvi / dvi / savi / msavi）统一套路：
- 传入一个 4 波段 `sample_tiff_bytes`，调用 `node.execute([data], ctx)`
- 验证返回 dict 含 key；或 bytes；或 tiff bytes
- 用 rasterio 打开输出，shape 与输入一致，dtype float32/nodata nan
- 关键指数数学验证：如 NDVI 在 [-1, 1] 之间，MSAVI 不为负值

### 4.6 S2Indices 基础 + 9 个单指数节点

**`S2Indices/test_s2_base.py`**
1. `SCALE_FACTOR=10000.0` 常量在 calc_* 中生效（NDVI=100% reflectance 场景）
2. 11 个波段（Blue/Green/Red/RE1/RE2/RE3/NIR/NIRn/SWIR1/SWIR2）全部识别
3. `calc_ireci` 需要 4 个红边波段齐全时才执行（缺一个→跳过）
4. `ZERO_AS_NODATA=True` → 0 值波段会被当成 nan

**`S2Indices/test_s2_nodes.py`**
9 个节点（ndvi / gndvi / ndre / ireci / savi / lswi / ndwi / mndwi / evi）统一套路：
- 输入构造不同波段集合（NDRE 需要 NIRn+RE1，IRECI 需要 RE3+Red+RE1+RE2）
- 输出 tiff bytes → rasterio 打开 shape 一致
- EVI 的 B* 系数公式手动验算一个数组

### 4.7 writers（2 个）

**`csv_writer`**
1. DataFrame → minio.put_object 被调，key 以 .csv 结尾
2. 自定义 key
3. 输入非 DF → TypeError
4. 无 inputs → ValueError

**`minio_writer`**
1. bytes（JPEG 签名）→ 自动加 .jpg content_type=image/jpeg
2. DataFrame → CSV + .csv
3. str → .txt
4. list/dict → JSON + .json
5. 已含扩展名 → 不再追加
6. `multi_files` dict → 循环 put_object，返回原始 key 前缀
7. 不支持的类型 → TypeError

### 4.8 utils/preview

**`preview`**
1. bytes → put_object 进 temp_bucket
2. DataFrame → CSV
3. str / list / dict → 各自编码
4. tif 扩展名自动改 tiff
5. label config 优先于 source_key
6. 透传：返回值 == 输入 data

---

## 五、执行计划

1. 创建 `worker/tests/` 目录和 `conftest.py`（monkeypatch minio + 生成样例 bytes）。
2. 写 `test_executor.py` + `test_dispatcher.py`。
3. 写 `readers/test_*.py`、`transforms/test_*.py`、`writers/test_*.py`、`utils/test_preview.py` — 纯 Python 无外部依赖。
4. 写 `droneIndices/test_drone_base.py` + `test_drone_nodes.py`（需 rasterio）。
5. 写 `S2Indices/test_s2_base.py` + `test_s2_nodes.py`（需 rasterio）。
6. 写 `media/test_image_*` + `test_image_*indices.py`（需 PIL / rasterio / easyocr(optional) / ffmpeg(optional)）。
7. 运行 `pytest worker/tests -v` 修正失败。

---

## 六、风险与处理

| 风险 | 处理 |
| --- | --- |
| easyocr 初始化很慢（~10s + 首次下载模型） | 设 `skipif(EASYOCR_SKIP)`；只留 smoke |
| ffmpeg-python 需要系统装 ffmpeg 二进制 | audio/video 三个节点 `skipif(not has_ffmpeg)` |
| rasterio 在 Windows 安装可能困难 | requirements 已经有，若失败改用 pip GDAL 包或 conda-forge；测试内 `skipif(ImportError)` |
| Ray 初始化占端口 | executor 测试只测纯函数（`_topological_sort` 等）或 monkeypatch `ray.put/get`；`run_pipeline` 可用真实 Ray（worker 里已有 ray） |
| MinIO monkeypatch 接口不一致 | fixture 用最简单的 `.read() -> bytes + .close() + .release_conn()`；list_objects 返回简单对象列表 |
| tests 数量变多时变慢 | 用 `-x`，后期可加 `pytest-xdist` |

---

## 七、运行命令

```powershell
cd D:\zuoye\DataFlow-main\worker
python -m pytest tests/ -v
python -m pytest tests/ -k "drone" -v
python -m pytest tests/ --ignore=tests/media/test_image_ocr.py --ignore=tests/media/test_audio_extract.py
```
