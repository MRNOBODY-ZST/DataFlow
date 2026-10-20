import pytest

# inject S3Error fallback when minio not installed
try:
    from minio.error import S3Error  # type: ignore
except ImportError:  # pragma: no cover
    class S3Error(Exception):
        code = "NoSuchKey"
        def __init__(self, message="", code=None):
            self.message = message
            self.code = code or self.code

from nodes.readers.minio_reader import MinioReaderNode


def _put(mock_minio, bucket: str, key: str, data: bytes):
    full = f"{bucket}/{key}"
    mock_minio.store[full] = data


def test_minio_reader_single_key(mock_minio, ctx):
    _put(mock_minio, "in", "a.bin", b"hello")
    ctx.config = {"key": "a.bin"}
    data = MinioReaderNode().execute([], ctx)
    assert data == b"hello"


def test_minio_reader_batch_prefix(mock_minio, ctx):
    _put(mock_minio, "in", "data/1.bin", b"one")
    _put(mock_minio, "in", "data/2.bin", b"two")
    _put(mock_minio, "in", "data/sub/", b"ignored")
    ctx.config = {"prefix": "data/"}
    out = MinioReaderNode().execute([], ctx)
    assert isinstance(out, list)
    keys = {item["key"] for item in out}
    assert "data/1.bin" in keys
    assert "data/2.bin" in keys


def test_minio_reader_batch_empty_prefix(mock_minio, ctx):
    ctx.config = {"prefix": "empty/"}
    with pytest.raises(RuntimeError):
        MinioReaderNode().execute([], ctx)


def test_minio_reader_no_key(mock_minio, ctx):
    ctx.config = {}
    with pytest.raises(RuntimeError):
        MinioReaderNode().execute([], ctx)


def test_minio_reader_key_with_slash_is_batch(mock_minio, ctx):
    _put(mock_minio, "in", "batch/f.bin", b"x")
    ctx.config = {"key": "batch/"}
    out = MinioReaderNode().execute([], ctx)
    assert isinstance(out, list)


def test_minio_reader_missing_key_raises(mock_minio, ctx):
    ctx.config = {"key": "does_not_exist.bin"}
    with pytest.raises(RuntimeError):
        MinioReaderNode().execute([], ctx)
