from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BOTS_DIR = REPO_ROOT / "Bots"
CANONICAL_DATAMODEL = BOTS_DIR / "datamodel.py"


def resolve_bot_path(bot_argument: str | Path) -> Path:
    candidate = Path(bot_argument)
    search_paths: list[Path] = []
    if candidate.is_absolute():
        search_paths.append(candidate)
    else:
        search_paths.extend(
            [
                Path.cwd() / candidate,
                REPO_ROOT / candidate,
                BOTS_DIR / candidate,
                BOTS_DIR / "archive" / candidate,
                BOTS_DIR / "Round1" / candidate,
                BOTS_DIR / "Round2" / candidate,
            ]
        )
    for path in search_paths:
        if path.exists():
            return path.resolve()
    raise FileNotFoundError(f"Could not find bot file for input: {bot_argument}")


def _load_module_from_path(module_name: str, module_path: Path):
    existing = sys.modules.get(module_name)
    if existing is not None and Path(getattr(existing, "__file__", "")).resolve() == module_path.resolve():
        return existing
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def ensure_bot_imports(bot_path: Path):
    if not CANONICAL_DATAMODEL.exists():
        raise FileNotFoundError(f"Expected canonical datamodel at {CANONICAL_DATAMODEL}")

    for path in (bot_path.parent, BOTS_DIR, REPO_ROOT):
        text = str(path)
        if text not in sys.path:
            sys.path.insert(0, text)

    datamodel = _load_module_from_path("datamodel", CANONICAL_DATAMODEL)
    return datamodel


def load_trader(bot_path: Path):
    ensure_bot_imports(bot_path)
    module_name = f"round2_backtester_bot_{bot_path.stem}"
    module = _load_module_from_path(module_name, bot_path)
    trader_cls = getattr(module, "Trader", None)
    if trader_cls is None:
        raise RuntimeError(f"Bot file {bot_path} does not expose a Trader class")
    return trader_cls()
