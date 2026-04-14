from pathlib import Path

import pytest

import trader_factory.simulation.internal_backtest as internal_backtest
from trader_factory.simulation.internal_backtest import resolve_dataset_tag


def write_dataset_files(root: Path, tag: str) -> None:
    (root / f"prices_{tag}_day_-1.csv").write_text("header\n")
    (root / f"trades_{tag}_day_-1.csv").write_text("header\n")


def test_resolve_dataset_tag_single_dataset(tmp_path: Path) -> None:
    write_dataset_files(tmp_path, "round_0")
    assert resolve_dataset_tag(tmp_path) == "round_0"


def test_resolve_dataset_tag_multiple_datasets_requires_explicit_tag(tmp_path: Path) -> None:
    write_dataset_files(tmp_path, "round_0")
    write_dataset_files(tmp_path, "round_1")

    with pytest.raises(ValueError):
        resolve_dataset_tag(tmp_path)


def test_resolve_dataset_tag_accepts_explicit_valid_tag(tmp_path: Path) -> None:
    write_dataset_files(tmp_path, "round_0")
    write_dataset_files(tmp_path, "round_1")

    assert resolve_dataset_tag(tmp_path, "round_1") == "round_1"


def test_resolve_dataset_tag_rejects_unknown_tag(tmp_path: Path) -> None:
    write_dataset_files(tmp_path, "round_0")

    with pytest.raises(FileNotFoundError):
        resolve_dataset_tag(tmp_path, "missing")


def test_resolve_data_dir_prefers_merged_prosperity_data_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    local_root = tmp_path / "local_data"
    merged_root = tmp_path / "merged_data"
    legacy_root = tmp_path / "legacy_data"
    write_dataset_files(merged_root, "round_0")

    monkeypatch.setattr(internal_backtest, "LOCAL_DATA_DIR", local_root)
    monkeypatch.setattr(internal_backtest, "MERGED_DATA_DIR", merged_root)
    monkeypatch.setattr(internal_backtest, "LEGACY_DATA_DIR", legacy_root)

    assert internal_backtest.resolve_data_dir() == merged_root.resolve()
