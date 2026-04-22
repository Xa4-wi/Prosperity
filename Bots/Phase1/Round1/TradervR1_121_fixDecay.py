from __future__ import annotations

import importlib.util
from pathlib import Path


_LOADER_PATH = Path(__file__).with_name("tradervr1_variant_loader.py")
_SPEC = importlib.util.spec_from_file_location("tradervr1_variant_loader", _LOADER_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("Could not load tradervr1_variant_loader")
_LOADER = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_LOADER)

_LOADER.load_variant(
    "TradervR1_121_13.py",
    [
        (
            '            quiet_non_toxic_ticks=no_fill_ticks if raw_bid_level == 0 and raw_ask_level == 0 else 0,\n',
            '            quiet_non_toxic_ticks=max(0, no_fill_ticks // 100) if raw_bid_level == 0 and raw_ask_level == 0 else 0,\n',
        ),
    ],
    globals(),
)
