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
            "        effective_buy_edge = buy_edge + min(0.0, buy_markout)\n        effective_sell_edge = sell_edge + min(0.0, sell_markout)\n",
            "        effective_buy_edge = buy_edge\n        effective_sell_edge = sell_edge\n",
        ),
        (
            "        if buy_markout < float(self.p[\"SOFT_BAD_MARKOUT\"]) and book.imbalance <= 0.0:\n            buy_need += float(self.p[\"MARKOUT_EDGE_PENALTY\"])\n        if sell_markout < float(self.p[\"SOFT_BAD_MARKOUT\"]) and book.imbalance >= 0.0:\n            sell_need += float(self.p[\"MARKOUT_EDGE_PENALTY\"])\n\n",
            "\n",
        ),
    ],
    globals(),
)
