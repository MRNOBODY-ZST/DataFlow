import os
import pytest

pytestmark = pytest.mark.skipif(os.environ.get("EASYOCR_SKIP", "1") == "1", reason="easyocr heavy")


def test_easyocr_import():
    try:
        import easyocr  # noqa: F401
    except ImportError:
        pytest.skip("easyocr not installed")


def test_ocr_node_class_exists():
    from nodes.media.image_ocr import ImageOCRNode

    assert ImageOCRNode is not None
