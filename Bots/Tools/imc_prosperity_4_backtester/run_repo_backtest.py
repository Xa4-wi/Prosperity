#!/usr/bin/env python3
"""Repo-local launcher for the imported Prosperity 4 backtester.

This keeps the upstream tool mostly untouched while making it easy to run
against our bots from the Prosperity repo root.
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = TOOL_DIR / "prosperity4bt"
DEFAULT_OUTPUT_DIR = TOOL_DIR / "output"


def _has_flag(argv: list[str], *flags: str) -> bool:
    return any(arg in flags for arg in argv)


def main() -> int:
    argv = sys.argv[1:]
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    command = [sys.executable, "-m", "prosperity4bt", *argv]
    if not _has_flag(argv, "--out", "--no-out"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        command.extend(["--out", str(DEFAULT_OUTPUT_DIR / f"{timestamp}.log")])

    env = os.environ.copy()
    py_paths = [str(TOOL_DIR), str(PACKAGE_DIR)]
    if env.get("PYTHONPATH"):
        py_paths.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(py_paths)

    completed = subprocess.run(command, cwd=Path.cwd(), env=env)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
