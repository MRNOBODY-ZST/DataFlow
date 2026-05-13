import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

WORKER_DIR = Path(__file__).resolve().parent
DISPATCHER_FILE = WORKER_DIR / "dispatcher.py"
PID_FILE = WORKER_DIR / "worker.pid"
LOG_FILE = WORKER_DIR / "worker.log"


def resolve_python_executable() -> Path:
    venv_python = WORKER_DIR / "venv" / "bin" / "python"
    if venv_python.exists():
        return venv_python
    return Path(sys.executable)


def read_pid() -> int | None:
    if not PID_FILE.exists():
        return None

    content = PID_FILE.read_text(encoding="utf-8").strip()
    if not content:
        PID_FILE.unlink(missing_ok=True)
        return None

    try:
        return int(content)
    except ValueError:
        PID_FILE.unlink(missing_ok=True)
        return None


def write_pid(pid: int) -> None:
    temp_file = PID_FILE.with_suffix(".pid.tmp")
    temp_file.write_text(f"{pid}\n", encoding="utf-8")
    os.replace(temp_file, PID_FILE)


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def is_worker_process(pid: int) -> bool:
    if not process_exists(pid):
        return False

    cmdline_path = Path("/proc") / str(pid) / "cmdline"
    if not cmdline_path.exists():
        return True

    try:
        cmdline = cmdline_path.read_text(encoding="utf-8", errors="ignore").replace("\x00", " ")
    except OSError:
        return True

    return str(DISPATCHER_FILE) in cmdline or "dispatcher.py" in cmdline


def remove_pid_file() -> None:
    PID_FILE.unlink(missing_ok=True)


def get_running_pid() -> int | None:
    pid = read_pid()
    if pid is None:
        return None

    if is_worker_process(pid):
        return pid

    remove_pid_file()
    return None


def read_log_lines(limit: int) -> list[str]:
    if not LOG_FILE.exists():
        return []
    lines = LOG_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
    return lines[-limit:]


def start_worker() -> int:
    running_pid = get_running_pid()
    if running_pid is not None:
        print(f"Worker is already running (PID {running_pid}).")
        return 1

    python_executable = resolve_python_executable()

    with LOG_FILE.open("a", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            [str(python_executable), str(DISPATCHER_FILE)],
            cwd=WORKER_DIR,
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

    time.sleep(1)
    if process.poll() is not None:
        print("Worker failed to start. Recent logs:")
        for line in read_log_lines(20):
            print(line)
        return 1

    write_pid(process.pid)
    print(f"Worker started (PID {process.pid}).")
    print(f"Logs: {LOG_FILE}")
    return 0


def stop_worker(wait_seconds: float = 10) -> int:
    pid = read_pid()
    if pid is None:
        print("Worker is not running.")
        return 1

    if not is_worker_process(pid):
        remove_pid_file()
        print("Worker is not running. Removed stale PID file.")
        return 1

    print(f"Stopping worker (PID {pid})...")
    os.kill(pid, signal.SIGTERM)

    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        if not process_exists(pid):
            remove_pid_file()
            print("Worker stopped.")
            return 0
        time.sleep(0.2)

    print("Worker did not stop within 10 seconds.")
    return 1


def status_worker() -> int:
    pid = read_pid()
    if pid is None:
        print("Worker is not running.")
        return 1

    if not is_worker_process(pid):
        remove_pid_file()
        print("Worker is not running. Removed stale PID file.")
        return 1

    print(f"Worker is running (PID {pid}).")
    return 0


def print_pid() -> int:
    pid = read_pid()
    if pid is None:
        print("Worker is not running.")
        return 1

    if not is_worker_process(pid):
        remove_pid_file()
        print("Worker is not running. Removed stale PID file.")
        return 1

    print(pid)
    return 0


def show_logs(lines: int, follow: bool) -> int:
    if not LOG_FILE.exists():
        print("No log file found.")
        return 1

    for line in read_log_lines(lines):
        print(line)

    if not follow:
        return 0

    try:
        with LOG_FILE.open("r", encoding="utf-8", errors="ignore") as log_file:
            log_file.seek(0, os.SEEK_END)
            while True:
                line = log_file.readline()
                if line:
                    print(line, end="")
                    continue
                time.sleep(0.5)
    except KeyboardInterrupt:
        return 0


def restart_worker() -> int:
    pid = get_running_pid()
    if pid is not None and stop_worker() != 0:
        return 1
    return start_worker()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the DataFlow worker process.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("start", help="Start the worker in the background.")
    subparsers.add_parser("stop", help="Stop the worker.")
    subparsers.add_parser("restart", help="Restart the worker.")
    subparsers.add_parser("status", help="Show whether the worker is running.")
    subparsers.add_parser("pid", help="Print the worker PID.")

    logs_parser = subparsers.add_parser("logs", help="Show worker logs.")
    logs_parser.add_argument("-n", "--lines", type=int, default=50, help="Number of lines to show.")
    logs_parser.add_argument("-f", "--follow", action="store_true", help="Follow log output.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "start":
        return start_worker()
    if args.command == "stop":
        return stop_worker()
    if args.command == "restart":
        return restart_worker()
    if args.command == "status":
        return status_worker()
    if args.command == "pid":
        return print_pid()
    if args.command == "logs":
        return show_logs(args.lines, args.follow)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
