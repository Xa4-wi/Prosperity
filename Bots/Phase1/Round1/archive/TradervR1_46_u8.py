from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_v46_module():
    path = Path(__file__).with_name("TradervR1_46.py")
    spec = importlib.util.spec_from_file_location("tradervr1_46_base", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load base trader from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_v46 = _load_v46_module()

DEFAULT_ASH_PARAMS = dict(_v46.DEFAULT_ASH_PARAMS)
DEFAULT_ASH_PARAMS.update(
    {
        "BASE_EDGE": -1.0,
        "TAKE_L1_EDGE": -1.0,
        "TAKE_L2_EDGE": 1.5,
        "TAKE_L3_EDGE": 4.5,
        "MIN_QUOTE_EDGE": 1.8,
    }
)
DEFAULT_IPR_PARAMS = dict(_v46.DEFAULT_IPR_PARAMS)


class Trader:
    def __init__(self) -> None:
        self.ash = _v46.AggressiveAshCoatedOsmiumTrader(DEFAULT_ASH_PARAMS)
        self.ipr = _v46.PepperTraderBase(DEFAULT_IPR_PARAMS)

    def _load_memory(self, trader_data: str) -> dict:
        if not trader_data:
            return {}
        try:
            parsed = json.loads(trader_data)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    def run(self, state):
        memory = self._load_memory(state.traderData if hasattr(state, "traderData") else "")
        result = {}
        if "ASH_COATED_OSMIUM" in state.order_depths:
            result["ASH_COATED_OSMIUM"] = self.ash.build_orders(state)
        if "INTARIAN_PEPPER_ROOT" in state.order_depths:
            ipr_orders, memory = self.ipr.build_orders(state, memory)
            result["INTARIAN_PEPPER_ROOT"] = ipr_orders
        return result, 0, json.dumps(memory, separators=(",", ":"))
