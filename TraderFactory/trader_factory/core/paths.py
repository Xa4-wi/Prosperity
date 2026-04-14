from __future__ import annotations

from pathlib import Path


def trader_factory_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _looks_like_prosperity_root(path: Path) -> bool:
    return path.exists() and all((path / name).exists() for name in ("Bots", "Data", "Analysis"))


def detect_prosperity_root(tf_root: Path | None = None) -> Path:
    root = (tf_root or trader_factory_root()).resolve()
    candidates = [
        root.parent,
        root.parent / "Prosperity",
    ]
    for candidate in candidates:
        if _looks_like_prosperity_root(candidate):
            return candidate.resolve()
    return candidates[0].resolve()


def prosperity_root() -> Path:
    return detect_prosperity_root()


def generated_root() -> Path:
    return trader_factory_root() / "generated"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def bots_root() -> Path:
    return prosperity_root() / "Bots"


def official_logs_root() -> Path:
    return ensure_dir(bots_root() / "Logs")


def official_run_archives_root() -> Path:
    return ensure_dir(official_logs_root() / "official_runs" / "imc_prosperity")


def prosperity_data_root() -> Path:
    return prosperity_root() / "Data"


def prosperity_rust_backtester_root() -> Path:
    return prosperity_root() / "ProsperityRustBacktester"


def prosperity_rust_backtester_runs_root() -> Path:
    return prosperity_rust_backtester_root() / "runs"


def prosperity_rust_backtester_cargo_wrapper() -> Path:
    return prosperity_rust_backtester_root() / "scripts" / "cargo_local.sh"


def legacy_python_backtester_root() -> Path:
    return prosperity_root() / "Backtest_failed_Python"


def legacy_backtest_script() -> Path:
    return legacy_python_backtester_root() / "run_backtest.py"


def legacy_monte_carlo_root() -> Path:
    return prosperity_root() / "MonteCarloBacktester"


def legacy_analysis_script(script_name: str) -> Path:
    return prosperity_root() / "Analysis" / script_name


def legacy_analysis_output_dir() -> Path:
    return prosperity_root() / "Analysis" / "output"


def internal_backtest_script() -> Path:
    return trader_factory_root() / "trader_factory" / "simulation" / "internal_backtest.py"


def internal_diagnostic_script(script_name: str) -> Path:
    return trader_factory_root() / "trader_factory" / "diagnostics" / script_name
