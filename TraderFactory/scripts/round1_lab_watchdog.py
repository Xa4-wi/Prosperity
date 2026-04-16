#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CACHE_ROOT = REPO_ROOT / ".cache" / "overnight_lab"
os.environ.setdefault("MPLCONFIGDIR", str(DEFAULT_CACHE_ROOT / "matplotlib"))
os.environ.setdefault("PYTHONPYCACHEPREFIX", str(DEFAULT_CACHE_ROOT / "pycache"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
Path(os.environ["PYTHONPYCACHEPREFIX"]).mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _default_root(name: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return REPO_ROOT / "Analysis" / "output" / "round1_overnight_lab" / f"{name}_{stamp}"


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Watchdog that relaunches the Round 1 overnight lab when it stops.")
    parser.add_argument("--root-output-dir", type=Path, default=None, help="Root directory for watchdog outputs.")
    parser.add_argument("--name", default="watchdog_live", help="Name prefix for the watchdog run.")
    parser.add_argument("--hours", type=float, default=8.0, help="Total wall-clock hours to supervise.")
    parser.add_argument("--check-seconds", type=int, default=1800, help="How often to verify the lab is still running.")
    parser.add_argument("--max-restarts", type=int, default=6, help="Maximum number of relaunches.")
    parser.add_argument("--run-args", nargs=argparse.REMAINDER, default=[], help="Arguments forwarded to round1_overnight_lab.py.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    root_output_dir = (args.root_output_dir.expanduser().resolve() if args.root_output_dir else _default_root(args.name))
    root_output_dir.mkdir(parents=True, exist_ok=True)
    attempts_dir = root_output_dir / "attempts"
    attempts_dir.mkdir(exist_ok=True)
    log_path = root_output_dir / "watchdog.log"
    state_path = root_output_dir / "watchdog_state.json"
    latest_attempt_path = root_output_dir / "LATEST_ATTEMPT.txt"

    python_bin = REPO_ROOT / ".venv-traderfactory" / "bin" / "python"
    script_path = REPO_ROOT / "TraderFactory" / "scripts" / "round1_overnight_lab.py"

    deadline = time.time() + args.hours * 3600.0
    restarts = 0
    attempt_index = 0
    child: subprocess.Popen[str] | None = None
    child_log_handle = None
    current_attempt_dir: Path | None = None

    def start_attempt() -> None:
        nonlocal attempt_index, child, child_log_handle, current_attempt_dir
        attempt_index += 1
        current_attempt_dir = attempts_dir / f"attempt_{attempt_index:02d}"
        current_attempt_dir.mkdir(parents=True, exist_ok=True)
        child_log_handle = (current_attempt_dir / "run.log").open("a")
        cmd = [
            str(python_bin),
            str(script_path),
            "--output-dir",
            str(current_attempt_dir),
        ] + list(args.run_args)
        child = subprocess.Popen(
            cmd,
            cwd=str(REPO_ROOT),
            stdout=child_log_handle,
            stderr=subprocess.STDOUT,
            text=True,
            env=dict(os.environ, PYTHONPATH=os.environ.get("PYTHONPATH", "TraderFactory")),
        )
        latest_attempt_path.write_text(str(current_attempt_dir) + "\n")
        with log_path.open("a") as handle:
            handle.write(f"[{_now()}] started attempt {attempt_index} pid={child.pid} dir={current_attempt_dir}\n")
        _write_json(
            state_path,
            {
                "updated_at": _now(),
                "attempt_index": attempt_index,
                "restarts": restarts,
                "deadline": deadline,
                "current_attempt_dir": str(current_attempt_dir),
                "child_pid": child.pid,
            },
        )

    start_attempt()
    try:
        while time.time() < deadline:
            time.sleep(max(1, args.check_seconds))
            if child is None:
                break
            rc = child.poll()
            if rc is None:
                with log_path.open("a") as handle:
                    handle.write(f"[{_now()}] healthy pid={child.pid} dir={current_attempt_dir}\n")
                _write_json(
                    state_path,
                    {
                        "updated_at": _now(),
                        "attempt_index": attempt_index,
                        "restarts": restarts,
                        "deadline": deadline,
                        "current_attempt_dir": str(current_attempt_dir) if current_attempt_dir else None,
                        "child_pid": child.pid,
                        "status": "running",
                    },
                )
                continue

            if child_log_handle is not None:
                child_log_handle.flush()
                child_log_handle.close()
                child_log_handle = None
            with log_path.open("a") as handle:
                handle.write(f"[{_now()}] stopped rc={rc} attempt={attempt_index} dir={current_attempt_dir}\n")
            if restarts >= args.max_restarts or time.time() >= deadline:
                break
            restarts += 1
            start_attempt()
    finally:
        if child is not None and child.poll() is None:
            with log_path.open("a") as handle:
                handle.write(f"[{_now()}] watchdog exiting while child still running pid={child.pid}\n")
        if child_log_handle is not None and not child_log_handle.closed:
            child_log_handle.flush()
            child_log_handle.close()
        _write_json(
            state_path,
            {
                "updated_at": _now(),
                "attempt_index": attempt_index,
                "restarts": restarts,
                "deadline": deadline,
                "current_attempt_dir": str(current_attempt_dir) if current_attempt_dir else None,
                "child_pid": child.pid if child is not None else None,
                "child_returncode": child.poll() if child is not None else None,
                "status": "finished",
            },
        )

    print(f"Watchdog root: {root_output_dir}")
    if current_attempt_dir is not None:
        print(f"Latest attempt dir: {current_attempt_dir}")


if __name__ == "__main__":
    main()
