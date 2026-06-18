import sys
import types
import io
import os
import warnings

try:
    from rasterio.errors import NotGeoreferencedWarning
    warnings.filterwarnings("ignore", category=NotGeoreferencedWarning)
except ImportError:
    pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def pytest_configure(config):
    try:
        config.addinivalue_line(
            "filterwarnings",
            "ignore::rasterio.errors.NotGeoreferencedWarning",
        )
    except Exception:
        pass


def _try_import(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False


_HAS_MINIO = _try_import("minio")
_HAS_RAY = _try_import("ray")
_HAS_KAFKA = _try_import("kafka")
_HAS_PYMONGO = _try_import("pymongo")
_HAS_REPORTER = _try_import("reporter")

if not _HAS_RAY:
    sys.modules["ray"] = types.SimpleNamespace(
        put=lambda x: f"obj-{id(x)}",
        get=lambda x: None,
        remote=lambda *a, **k: (lambda f: f),
        init=lambda *a, **k: None,
        shutdown=lambda *a, **k: None,
        is_initialized=lambda: False,
    )
if not _HAS_KAFKA:
    sys.modules["kafka"] = types.SimpleNamespace(KafkaConsumer=lambda *a, **k: [])
if not _HAS_PYMONGO:
    sys.modules["pymongo"] = types.SimpleNamespace(MongoClient=lambda *a, **k: types.SimpleNamespace())
if not _HAS_REPORTER:
    sys.modules["reporter"] = types.SimpleNamespace(
        success=lambda *a, **k: None,
        failed=lambda *a, **k: None,
        progress=lambda *a, **k: None,
    )

import pytest
from nodes.base import NodeContext


class _FakeResponse:
    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        return self._data

    def close(self):
        pass

    def release_conn(self):
        pass


class _FakeListObj:
    def __init__(self, name: str):
        self.object_name = name


class _FakeMinio:
    def __init__(self):
        self.store: dict[str, bytes] = {}
        self.put_calls: list[tuple[str, str, bytes, str | None]] = []
        self.fput_calls: list[tuple[str, str, str, str | None]] = []

    def get_object(self, bucket: str, key: str):
        full = f"{bucket}/{key}"
        if full not in self.store:
            try:
                from minio.error import S3Error

                import types as _t

                e = S3Error(
                    response=_t.SimpleNamespace(status=404, headers={}),
                    code="NoSuchKey",
                    message="NotFound",
                    resource=full,
                    request_id="x",
                    host_id="y",
                )
                raise e
            except ImportError:
                raise KeyError(full)
        return _FakeResponse(self.store[full])

    def put_object(self, bucket: str, key: str, data: io.BytesIO, length: int | None = None, content_type: str | None = None):
        raw = data.getvalue() if hasattr(data, "getvalue") else bytes(data.read())
        self.put_calls.append((bucket, key, raw, content_type))
        self.store[f"{bucket}/{key}"] = raw

    def fput_object(self, bucket: str, key: str, file_path: str, content_type: str | None = None):
        with open(file_path, "rb") as f:
            raw = f.read()
        self.fput_calls.append((bucket, key, file_path, content_type))
        self.store[f"{bucket}/{key}"] = raw

    def list_objects(self, bucket: str, prefix: str = "", recursive: bool = True):
        prefix_full = f"{bucket}/{prefix}" if prefix else bucket
        names = []
        for k in self.store:
            if k.startswith(prefix_full):
                rest = k[len(bucket) + 1:]
                names.append(rest)
        return [_FakeListObj(n) for n in sorted(names)]


@pytest.fixture
def mock_minio() -> _FakeMinio:
    return _FakeMinio()


@pytest.fixture
def ctx(mock_minio) -> NodeContext:
    return NodeContext(
        task_id="t1",
        node_id="n1",
        config={},
        minio_client=mock_minio,
        input_bucket="in",
        output_bucket="out",
        temp_bucket="tmp",
        output_prefix="run_t1",
        source_key="sample/input.bin",
    )


@pytest.fixture
def sample_csv_bytes() -> bytes:
    return b"a,b,c\n1,2,3\n4,5,6\n7,8,9"


@pytest.fixture
def sample_json_bytes() -> bytes:
    return b'{"x": 1, "y": {"nested": [1, 2, 3]}}'


@pytest.fixture
def sample_png_bytes() -> bytes:
    from PIL import Image
    import numpy as np

    img = Image.fromarray(np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def sample_png_rgba_bytes() -> bytes:
    from PIL import Image
    import numpy as np

    arr = np.zeros((32, 32, 4), dtype=np.uint8)
    arr[:, :, 0] = 128
    arr[:, :, 1] = 64
    arr[:, :, 2] = 200
    arr[:, :, 3] = 255
    img = Image.fromarray(arr, mode="RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def sample_tiff_bytes_rasterio():
    try:
        import rasterio
    except ImportError:
        pytest.skip("rasterio not installed")

    def _build(descriptions: list[str], dtype: str = "float32", zero_as_nodata: bool = True, w: int = 32, h: int = 32) -> bytes:
        import numpy as np

        count = len(descriptions)
        profile = {
            "driver": "GTiff",
            "width": w,
            "height": h,
            "count": count,
            "dtype": dtype,
            "crs": None,
            "transform": rasterio.transform.from_origin(121.0, 31.0, 0.001, -0.001),
            "nodata": 0 if zero_as_nodata else None,
        }
        buf = io.BytesIO()
        with rasterio.open(buf, "w", **profile) as dst:
            for i, desc in enumerate(descriptions, 1):
                if dtype in ("uint16", "int16", "uint32", "int32"):
                    arr = np.arange(w * h, dtype=np.float32).reshape(h, w).astype(dtype) + 1
                else:
                    arr = np.random.rand(h, w).astype(dtype) * 0.5 + 0.25
                dst.write(arr, i)
                dst.set_band_description(i, desc)
        return buf.getvalue()

    return _build


@pytest.fixture
def has_ffmpeg() -> bool:
    try:
        import ffmpeg  # noqa: F401
        return True
    except ImportError:
        return False


@pytest.fixture
def has_rasterio() -> bool:
    try:
        import rasterio  # noqa: F401
        return True
    except ImportError:
        return False


_S2_REAL_TIFF_CACHE: bytes | None = None


@pytest.fixture
def s2_real_tiff_bytes() -> bytes:
    global _S2_REAL_TIFF_CACHE
    if _S2_REAL_TIFF_CACHE is None:
        tiff_path = os.path.join(os.path.dirname(__file__), "S2_yuantu.tiff")
        with open(tiff_path, "rb") as f:
            _S2_REAL_TIFF_CACHE = f.read()
    return _S2_REAL_TIFF_CACHE
