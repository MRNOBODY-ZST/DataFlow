#!/usr/bin/env bash
# Worker 单元测试一键脚本（bash 版）
# 用法:
#   ./run_tests.sh              跑全部（忽略 OCR / 音视频 慢测试）
#   ./run_tests.sh --all        含 skip 用例
#   ./run_tests.sh --fast       只跑轻量模块
#   ./run_tests.sh --indices    只跑 drone + S2 指数
#   ./run_tests.sh media/test_image_resize.py
#   ./run_tests.sh -k resize

set -euo pipefail
cd "$(dirname "$0")"

IGNORE=(
  --ignore=tests/media/test_image_ocr.py
  --ignore=tests/media/test_audio_extract.py
  --ignore=tests/media/test_video_extract.py
  --ignore=tests/media/test_video_transcode.py
)

case "${1:-}" in
  --all)
    python -m pytest tests/ -v --tb=short
    ;;
  --fast)
    python -m pytest \
      tests/readers tests/transforms tests/writers tests/utils \
      tests/test_executor.py tests/test_dispatcher.py \
      -v --tb=short
    ;;
  --indices)
    python -m pytest tests/droneIndices tests/S2Indices -v --tb=short
    ;;
  "")
    python -m pytest tests/ -v --tb=short "${IGNORE[@]}"
    ;;
  *)
    python -m pytest tests/ "$@" --tb=short "${IGNORE[@]}"
    ;;
esac
