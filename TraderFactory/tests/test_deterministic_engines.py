from pathlib import Path

from trader_factory.simulation.deterministic import (
    _parse_rust_metrics,
    _resolve_rust_dataset_input,
    default_output_dir,
)


def write_dataset_files(root: Path, tag: str, day: int) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / f"prices_{tag}_day_{day}.csv").write_text("header\n")
    (root / f"trades_{tag}_day_{day}.csv").write_text("header\n")


def test_default_output_dir_separates_rust_engine(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    bot_path = tmp_path / "Bots" / "Traderv90.py"
    bot_path.parent.mkdir(parents=True, exist_ok=True)
    bot_path.write_text("class Trader: pass\n")

    rust_dir = default_output_dir(bot_path, -1, engine="rust")

    assert "deterministic/rust" in str(rust_dir)


def test_resolve_rust_dataset_input_uses_explicit_price_file(tmp_path: Path) -> None:
    write_dataset_files(tmp_path, "round_0", -1)

    dataset = _resolve_rust_dataset_input(day=-1, data_root=tmp_path, dataset_tag="round_0")

    assert dataset.endswith("prices_round_0_day_-1.csv")


def test_parse_rust_metrics_reads_final_total_pnl(tmp_path: Path) -> None:
    metrics_path = tmp_path / "metrics.json"
    metrics_path.write_text('{"final_pnl_total": 1234.5}')

    assert _parse_rust_metrics(metrics_path) == 1234.5
