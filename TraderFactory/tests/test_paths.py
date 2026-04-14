from pathlib import Path
import zipfile

from trader_factory.core.paths import detect_prosperity_root
from trader_factory.official.imc_prosperity import _extract_submission_bundle, _submission_artifact_prefix


def _touch_markers(root: Path) -> None:
    for name in ("Bots", "Data", "Analysis"):
        (root / name).mkdir(parents=True, exist_ok=True)


def test_detect_prosperity_root_prefers_merged_repo_root(tmp_path: Path) -> None:
    repo_root = tmp_path / "Prosperity"
    trader_factory_root = repo_root / "TraderFactory"
    trader_factory_root.mkdir(parents=True)
    _touch_markers(repo_root)

    assert detect_prosperity_root(trader_factory_root) == repo_root.resolve()


def test_detect_prosperity_root_falls_back_to_legacy_sibling_repo(tmp_path: Path) -> None:
    trader_factory_root = tmp_path / "TraderFactory"
    trader_factory_root.mkdir(parents=True)
    legacy_root = tmp_path / "Prosperity"
    _touch_markers(legacy_root)

    assert detect_prosperity_root(trader_factory_root) == legacy_root.resolve()


def test_submission_artifact_prefix_uses_submission_id_and_clean_bot_name() -> None:
    assert _submission_artifact_prefix(100232, "170-Traderv39_4.py") == "submission_100232_Traderv39_4"


def test_extract_submission_bundle_renames_files_and_removes_zip(tmp_path: Path) -> None:
    output_dir = tmp_path / "100232"
    zip_path = tmp_path / "download.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("102174.log", '{"activitiesLog":[]}')
        archive.writestr("102174.json", '{"profit": 1}')
        archive.writestr("102174.py", "print('ok')\n")

    bundle = _extract_submission_bundle(
        zip_path,
        output_dir,
        submission_id=100232,
        uploaded_filename="170-Traderv39_4.py",
    )

    expected_prefix = "submission_100232_Traderv39_4"
    assert zip_path.exists() is False
    assert bundle.log_path == (output_dir / f"{expected_prefix}.log").resolve()
    assert bundle.json_path == (output_dir / f"{expected_prefix}.json").resolve()
    assert bundle.python_path == (output_dir / f"{expected_prefix}.py").resolve()
    assert sorted(path.name for path in bundle.extracted_files) == sorted(
        [
            f"{expected_prefix}.json",
            f"{expected_prefix}.log",
            f"{expected_prefix}.py",
        ]
    )
