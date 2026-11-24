"""Stage TIFFs and invoke the unmodified delivery model in its own environment."""
import os
from pathlib import Path
import shutil
import subprocess


def stage_tiff(target, ctx, *, key=None, data=None):
    if data is not None:
        target.write_bytes(data)
    else:
        response = ctx.minio_client.get_object(ctx.input_bucket, key)
        try:
            with target.open("wb") as stream:
                shutil.copyfileobj(response, stream)
        finally:
            response.close()
            response.release_conn()
    with target.open("rb") as stream:
        if stream.read(4) not in (b"II*\0", b"MM\0*", b"II+\0", b"MM\0+"):
            raise ValueError(f"不是 TIFF / BigTIFF 文件：{key or target.name}")


def infer(kind, directory, args):
    python = Path(os.environ.get("UAV_RGB_PYTHON", ""))
    script = Path(os.environ.get("UAV_DELIVERY_ROOT", "")) / "run.py"
    if not all(p.is_absolute() and p.is_file() for p in (python, script)):
        raise RuntimeError("请在 Worker 设置 UAV_RGB_PYTHON 和 UAV_DELIVERY_ROOT 为绝对路径")
    env = os.environ.copy()
    for name in ("PYTHONPATH", "PYTHONHOME", "PYTHONOPTIMIZE"):
        env.pop(name, None)
    env.update(PYTHONUTF8="1", PYTHONNOUSERSITE="1", HF_HUB_OFFLINE="1")
    if os.name == "nt":
        prefix = python.parent
        env["PATH"] = os.pathsep.join(map(str, (prefix, prefix / "Library/bin", prefix / "Scripts", env["PATH"])))
    out = directory / "result"
    timeout = max(1, int(env.get("NODE_TIMEOUT_SECONDS", "300")) - 10)
    try:
        result = subprocess.run([str(python), "-B", str(script), "--model", kind,
                                 *args, "--out", str(out), "--device", "cpu"],
                                cwd=script.parent, env=env, timeout=timeout,
                                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"{kind} 推理超过 {timeout} 秒") from exc
    if result.returncode:
        raise RuntimeError(f"{kind} 推理失败 ({result.returncode}): {result.stderr[-1600:].strip()}")
    overlay = out / "overlay.png"
    if not overlay.is_file():
        raise RuntimeError(f"{kind} 推理未生成 overlay.png")
    return overlay.read_bytes()
