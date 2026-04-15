from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from trader_factory.core.paths import (
    ensure_dir,
    generated_root,
    internal_backtest_script,
    prosperity_data_root,
    prosperity_rust_backtester_cargo_wrapper,
    prosperity_rust_backtester_root,
    trader_factory_root,
)


FINAL_TOTAL_RE = re.compile(r"Final total PnL:\s*([-+]?\d+(?:\.\d+)?)")
PRICE_FILE_RE = re.compile(r"^prices_(.+)_day_(-?\d+)\.csv$")
TRADE_FILE_RE = re.compile(r"^trades_(.+)_day_(-?\d+)\.csv$")
DeterministicEngine = Literal["internal", "rust"]


@dataclass(slots=True)
class DeterministicRunResult:
    bot_path: Path
    day: int
    output_dir: Path
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    summary_path: Path
    step_log_path: Path
    fills_path: Path
    product_log_path: Path
    final_total_pnl: float | None
    engine: DeterministicEngine = "internal"
    metrics_path: Path | None = None
    submission_log_path: Path | None = None


def default_output_dir(bot_path: Path, day: int, *, engine: DeterministicEngine = "internal") -> Path:
    if engine == "rust":
        return ensure_dir(generated_root() / "runs" / "deterministic" / "rust" / f"{bot_path.stem}_day_{day}")
    return ensure_dir(generated_root() / "runs" / "deterministic" / f"{bot_path.stem}_day_{day}")


def parse_final_total_pnl(summary_path: Path, stdout: str) -> float | None:
    text = summary_path.read_text() if summary_path.exists() else stdout
    match = FINAL_TOTAL_RE.search(text)
    if match is None:
        return None
    return float(match.group(1))


def _looks_like_data_dir(path: Path) -> bool:
    return path.is_dir() and any(PRICE_FILE_RE.match(item.name) for item in path.iterdir() if item.is_file())


def _discover_dataset_tags(path: Path) -> list[str]:
    price_tags = {
        match.group(1)
        for item in path.iterdir()
        if item.is_file()
        for match in [PRICE_FILE_RE.match(item.name)]
        if match
    }
    trade_tags = {
        match.group(1)
        for item in path.iterdir()
        if item.is_file()
        for match in [TRADE_FILE_RE.match(item.name)]
        if match
    }
    return sorted(price_tags & trade_tags)


def _resolve_data_dir(data_root: str | Path | None = None) -> Path:
    if data_root is not None:
        candidate = Path(data_root).expanduser().resolve()
        if not candidate.exists():
            raise FileNotFoundError(f"Data directory does not exist: {candidate}")
        if not _looks_like_data_dir(candidate):
            raise FileNotFoundError(f"Data directory does not contain Prosperity replay CSVs: {candidate}")
        return candidate

    for candidate in (trader_factory_root() / "data", prosperity_data_root()):
        if candidate.exists() and _looks_like_data_dir(candidate):
            return candidate.resolve()
    raise FileNotFoundError("Could not find replay data under TraderFactory/data or Prosperity/Data.")


def _resolve_dataset_tag(data_dir: Path, dataset_tag: str | None = None) -> str:
    tags = _discover_dataset_tags(data_dir)
    if dataset_tag is not None:
        if dataset_tag not in tags:
            raise FileNotFoundError(
                f"Dataset tag {dataset_tag!r} not found in {data_dir}. Available tags: {', '.join(tags) or '(none)'}"
            )
        return dataset_tag
    if len(tags) == 1:
        return tags[0]
    if not tags:
        raise FileNotFoundError(f"No replay datasets found in {data_dir}")
    raise ValueError(f"Multiple dataset tags found in {data_dir}: {', '.join(tags)}. Pass --dataset-tag explicitly.")


def _resolve_rust_dataset_input(*, day: int, data_root: str | Path | None, dataset_tag: str | None) -> str:
    if data_root is None and dataset_tag is None:
        return "workspace"

    resolved_data_root = _resolve_data_dir(data_root)
    resolved_dataset_tag = _resolve_dataset_tag(resolved_data_root, dataset_tag)
    price_path = resolved_data_root / f"prices_{resolved_dataset_tag}_day_{day}.csv"
    trade_path = resolved_data_root / f"trades_{resolved_dataset_tag}_day_{day}.csv"
    if not price_path.exists():
        raise FileNotFoundError(f"Could not find Rust-backtester price file: {price_path}")
    if not trade_path.exists():
        raise FileNotFoundError(f"Could not find Rust-backtester trade file: {trade_path}")
    return str(price_path)


def _parse_rust_metrics(metrics_path: Path) -> float | None:
    if not metrics_path.exists():
        return None
    payload = json.loads(metrics_path.read_text())
    value = payload.get("final_pnl_total")
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _write_rust_summary(summary_path: Path, *, final_total_pnl: float | None, metrics_path: Path, submission_log_path: Path) -> Path:
    lines = [
        "Deterministic engine: rust",
        f"Metrics: {metrics_path}",
        f"Submission log: {submission_log_path}",
        f"Final total PnL: {final_total_pnl}",
    ]
    summary_path.write_text("\n".join(lines) + "\n")
    return summary_path


def _run_internal_deterministic(
    bot: Path,
    *,
    day: int,
    out_dir: Path,
    data_root: str | Path | None,
    dataset_tag: str | None,
    python_bin: str,
    timeout_seconds: float | None,
    check: bool,
) -> DeterministicRunResult:
    command = [
        python_bin,
        str(internal_backtest_script()),
        str(bot),
        "--day",
        str(day),
        "--output",
        str(out_dir),
    ]
    if data_root is not None:
        command.extend(["--data-root", str(Path(data_root).expanduser().resolve())])
    if dataset_tag is not None:
        command.extend(["--dataset-tag", dataset_tag])
    process = subprocess.run(
        command,
        cwd=trader_factory_root(),
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    if check and process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or "Deterministic run failed")

    summary_path = out_dir / "summary.txt"
    return DeterministicRunResult(
        bot_path=bot,
        day=day,
        output_dir=out_dir,
        command=command,
        returncode=process.returncode,
        stdout=process.stdout,
        stderr=process.stderr,
        summary_path=summary_path,
        step_log_path=out_dir / "step_log.csv",
        fills_path=out_dir / "fills.csv",
        product_log_path=out_dir / "product_log.csv",
        final_total_pnl=parse_final_total_pnl(summary_path, process.stdout),
        engine="internal",
    )


def _run_rust_deterministic(
    bot: Path,
    *,
    day: int,
    out_dir: Path,
    data_root: str | Path | None,
    dataset_tag: str | None,
    python_bin: str,
    timeout_seconds: float | None,
    check: bool,
) -> DeterministicRunResult:
    rust_root = prosperity_rust_backtester_root()
    cargo_wrapper = prosperity_rust_backtester_cargo_wrapper()
    local_binary = rust_root / "target_local" / "debug" / "rust_backtester"
    if local_binary.exists():
        binary = str(local_binary)
        command = [
            binary,
            "--trader",
            str(bot),
            "--dataset",
            _resolve_rust_dataset_input(day=day, data_root=data_root, dataset_tag=dataset_tag),
            f"--day={day}",
            "--run-id",
            out_dir.name,
            "--output-root",
            str(out_dir.parent),
            "--artifact-mode",
            "submission",
            "--products",
            "off",
        ]
        cwd = rust_root
        env = None
    elif not cargo_wrapper.exists():
        binary = shutil.which("rust_backtester")
        if binary is None:
            raise FileNotFoundError(
                f"Could not find ProsperityRustBacktester wrapper at {cargo_wrapper} or an installed rust_backtester binary."
            )
        command = [
            binary,
            "--trader",
            str(bot),
            "--dataset",
            _resolve_rust_dataset_input(day=day, data_root=data_root, dataset_tag=dataset_tag),
            f"--day={day}",
            "--run-id",
            out_dir.name,
            "--output-root",
            str(out_dir.parent),
            "--artifact-mode",
            "submission",
            "--products",
            "off",
        ]
        cwd = rust_root
        env = None
    else:
        command = [
            str(cargo_wrapper),
            "run",
            "--",
            "--trader",
            str(bot),
            "--dataset",
            _resolve_rust_dataset_input(day=day, data_root=data_root, dataset_tag=dataset_tag),
            f"--day={day}",
            "--run-id",
            out_dir.name,
            "--output-root",
            str(out_dir.parent),
            "--artifact-mode",
            "submission",
            "--products",
            "off",
        ]
        cwd = rust_root
        env = os.environ.copy()
        env.setdefault("CARGO_TARGET_DIR", str(rust_root / "target_local"))
        env.setdefault("PYO3_PYTHON", python_bin)

    process = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    if check and process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or "Rust deterministic run failed")

    metrics_path = out_dir / "metrics.json"
    submission_log_path = out_dir / "submission.log"
    final_total_pnl = _parse_rust_metrics(metrics_path)
    summary_path = _write_rust_summary(
        out_dir / "summary.txt",
        final_total_pnl=final_total_pnl,
        metrics_path=metrics_path,
        submission_log_path=submission_log_path,
    )
    return DeterministicRunResult(
        bot_path=bot,
        day=day,
        output_dir=out_dir,
        command=command,
        returncode=process.returncode,
        stdout=process.stdout,
        stderr=process.stderr,
        summary_path=summary_path,
        step_log_path=out_dir / "activity.csv",
        fills_path=out_dir / "trades.csv",
        product_log_path=out_dir / "pnl_by_product.csv",
        final_total_pnl=final_total_pnl,
        engine="rust",
        metrics_path=metrics_path,
        submission_log_path=submission_log_path,
    )


def run_deterministic(
    bot_path: str | Path,
    *,
    day: int = -1,
    output_dir: str | Path | None = None,
    data_root: str | Path | None = None,
    dataset_tag: str | None = None,
    engine: DeterministicEngine = "internal",
    python_bin: str = sys.executable,
    timeout_seconds: float | None = None,
    check: bool = True,
) -> DeterministicRunResult:
    bot = Path(bot_path).expanduser().resolve()
    out_dir = Path(output_dir).expanduser().resolve() if output_dir else default_output_dir(bot, day, engine=engine)
    ensure_dir(out_dir)
    if engine == "rust":
        return _run_rust_deterministic(
            bot,
            day=day,
            out_dir=out_dir,
            data_root=data_root,
            dataset_tag=dataset_tag,
            python_bin=python_bin,
            timeout_seconds=timeout_seconds,
            check=check,
        )
    if engine != "internal":
        raise ValueError(f"Unknown deterministic engine: {engine}")
    return _run_internal_deterministic(
        bot,
        day=day,
        out_dir=out_dir,
        data_root=data_root,
        dataset_tag=dataset_tag,
        python_bin=python_bin,
        timeout_seconds=timeout_seconds,
        check=check,
    )
