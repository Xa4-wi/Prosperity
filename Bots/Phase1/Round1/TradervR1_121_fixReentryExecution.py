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
            '        if profile != "defend":\n            join_edge += join_bonus\n',
            '        if profile != "defend":\n            join_edge += join_bonus\n        if buy_reactivation or sell_reactivation:\n            join_edge += 0.20 + (0.05 if micro_nibble else 0.0)\n',
        ),
        (
            "        if profile == \"attack\":\n            front_buy = max(front_buy, book.best_bid + 1)\n            front_sell = min(front_sell, book.best_ask - 1)\n        elif profile == \"press\":\n            front_buy = max(front_buy, book.best_bid)\n            front_sell = min(front_sell, book.best_ask)\n\n        front_buy = min(front_buy, book.best_ask - 1)\n        front_sell = max(front_sell, book.best_bid + 1)\n",
            "        if profile == \"attack\":\n            front_buy = max(front_buy, book.best_bid + 1)\n            front_sell = min(front_sell, book.best_ask - 1)\n        elif profile == \"press\":\n            front_buy = max(front_buy, book.best_bid)\n            front_sell = min(front_sell, book.best_ask)\n\n        if buy_reactivation:\n            if book.best_bid + 1 < book.best_ask:\n                front_buy = max(front_buy, book.best_bid + 1)\n            else:\n                front_buy = max(front_buy, book.best_bid)\n        elif sell_reactivation:\n            if book.best_ask - 1 > book.best_bid:\n                front_sell = min(front_sell, book.best_ask - 1)\n            else:\n                front_sell = min(front_sell, book.best_ask)\n\n        front_buy = min(front_buy, book.best_ask - 1)\n        front_sell = max(front_sell, book.best_bid + 1)\n",
        ),
    ],
    globals(),
)
