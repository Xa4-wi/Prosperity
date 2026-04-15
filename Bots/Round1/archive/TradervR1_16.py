from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Tuple

try:
    from datamodel import Order, OrderDepth, TradingState
except ModuleNotFoundError:
    from trader_factory.core.datamodel import Order, OrderDepth, TradingState

# ── Position limits (official Round 1 limits are 80) ──────────────────────────
PRODUCT_LIMITS = {
    "ASH_COATED_OSMIUM": 80,
    "INTARIAN_PEPPER_ROOT": 80,
}

# ── ASH_COATED_OSMIUM params ───────────────────────────────────────────────────
# Archetype: anchored_mm with tiered takes, join logic, two-level passive ladder
DEFAULT_ASH_PARAMS = {
    "ENABLED": True,
    "REFERENCE_PRICE": 10000.0,
    "IMBALANCE_WEIGHT": 1.0530199689,   # fair += imbalance_weight * book_imbalance
    "MICRO_WEIGHT": 0.35,       # fair += micro_weight * (micro - mid)
    "INVENTORY_SKEW": 0.1197820182,    # reservation -= skew * position
    "BASE_EDGE": 2.0,           # default passive quote edge
    "JOIN_EDGE": 2.0,           # snap quote to existing order when within this
    "FRONT_SIZE": 17.52842512,
    "BACK_SIZE": 5,
    "SOFT_LIMIT": 70.0,           # reduce aggressiveness above this inventory
    # Tiered take: [(min_edge, qty_clip), ...]
    "TAKE_L1_EDGE": 2.0,
    "TAKE_L1_SIZE": 6,
    "TAKE_L2_EDGE": 5.0,
    "TAKE_L2_SIZE": 10,
    "TAKE_L3_EDGE": 8.0,
    "TAKE_L3_SIZE": 16,
    # Toxic-book thresholds
    "ADVERSE_IMBALANCE": 0.20,
    "STRONG_IMBALANCE": 0.16,
}

# ── INTARIAN_PEPPER_ROOT params ────────────────────────────────────────────────
# Archetype: directional_mm with state-based trend + residual tracking
# Key fix: passive quotes anchored to mid (not drift-adjusted fair), so they
# actually land inside the spread and can fill.
DEFAULT_IPR_PARAMS = {
    "ENABLED": True,
    # Trend model
    "DRIFT_PER_TIMESTAMP": 0.0026009226,   # +1 tick / 1000 timestamps → +1000/day
    "RESIDUAL_ALPHA": 0.10,          # EMA alpha for residual tracking
    "SPREAD_ALPHA": 0.08,            # EMA alpha for spread tracking
    "SHORT_MID_ALPHA": 0.18,
    "LONG_MID_ALPHA": 0.05,
    "LOOKAHEAD_BONUS": 4.8849030549,          # constant upward bias in fair value
    # Position targeting
    "NORMAL_TARGET": 48.0,
    "ACCEL_TARGET": 66.0,
    "WEAK_TARGET": 38.0,
    "LATE_TARGET": 28.0,
    "ZSCORE_BUY_BONUS": 10.0,
    "ZSCORE_SELL_PENALTY": 6.0,
    "MAX_LONG_TARGET": 76.0,
    "MAX_SHORT_TARGET": 20,
    "ACCEL_SLOPE_THRESHOLD": 6.0,
    "WEAK_SLOPE_THRESHOLD": 2.0,
    "ACCELERATION_THRESHOLD": 1.0,
    "OVERLAY_BAND": 12.0,
    "LATE_UNWIND_START": 0.80,
    "LATE_UNWIND_Z": 1.15,
    # Execution
    "INVENTORY_SKEW": 0.078,
    "AGGRESSIVE_BUY_EDGE": 2.3,
    "PASSIVE_BUY_EDGE": 4.2,
    "OVERLAY_SELL_EDGE": 3.4,
    "BASE_QUOTE_EDGE": 5.0,
    "SOFT_LIMIT": 52,
    "PASSIVE_FRONT_SIZE": 9,
    "PASSIVE_BACK_SIZE": 6,
    "PASSIVE_BUY_BUFFER": 16,
    "PASSIVE_SELL_BUFFER": 6,
    "OVEREXTENSION_Z": 1.05,
    "BULLISH_IMBALANCE": 0.05,
    "RELOAD_PAUSE_ALPHA": 0.22,
    "RELOAD_COOLDOWN": 3.5,
}


# ── Shared helpers ─────────────────────────────────────────────────────────────

def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def ema(prev: Optional[float], current: float, alpha: float) -> float:
    if prev is None:
        return current
    return (1.0 - alpha) * prev + alpha * current


class Book:
    """Parsed order book snapshot."""

    def __init__(self, depth: Optional[OrderDepth]) -> None:
        self.valid = False
        self.buy_levels: List[Tuple[int, int]] = []
        self.sell_levels: List[Tuple[int, int]] = []
        self.best_bid = self.best_ask = 0
        self.best_bid_vol = self.best_ask_vol = 0
        self.mid = self.micro = self.spread_val = self.imbalance = 0.0

        if depth is None:
            return
        self.buy_levels = sorted(
            ((int(p), int(v)) for p, v in depth.buy_orders.items()),
            key=lambda x: x[0], reverse=True,
        )
        self.sell_levels = sorted(
            ((int(p), abs(int(v))) for p, v in depth.sell_orders.items()),
            key=lambda x: x[0],
        )
        if not self.buy_levels or not self.sell_levels:
            return
        self.best_bid, self.best_bid_vol = self.buy_levels[0]
        self.best_ask, self.best_ask_vol = self.sell_levels[0]
        if self.best_bid >= self.best_ask:
            return
        self.mid = (self.best_bid + self.best_ask) / 2.0
        self.spread_val = float(self.best_ask - self.best_bid)
        total = self.best_bid_vol + self.best_ask_vol
        if total > 0:
            self.micro = (self.best_ask * self.best_bid_vol + self.best_bid * self.best_ask_vol) / total
            self.imbalance = (self.best_bid_vol - self.best_ask_vol) / total
        else:
            self.micro = self.mid
        self.valid = True


class Manager:
    """Capacity-tracking order builder."""

    def __init__(self, product: str, position: int, limit: int) -> None:
        self.product = product
        self.position = int(position)
        self.limit = int(limit)
        self.buy_cap = max(0, limit - position)
        self.sell_cap = max(0, limit + position)
        self.orders: List[Order] = []

    def projected(self) -> int:
        return self.position + sum(o.quantity for o in self.orders)

    def buy(self, price: int, qty: int) -> None:
        size = min(max(0, int(qty)), self.buy_cap)
        if size > 0:
            self.orders.append(Order(self.product, int(price), size))
            self.buy_cap -= size

    def sell(self, price: int, qty: int) -> None:
        size = min(max(0, int(qty)), self.sell_cap)
        if size > 0:
            self.orders.append(Order(self.product, int(price), -size))
            self.sell_cap -= size


# ── ASH_COATED_OSMIUM trader ───────────────────────────────────────────────────

class AshCoatedOsmiumTrader:
    """
    Anchored MM around 10000.
    - Fair value: reference + imbalance_weight*imbalance + micro_weight*(micro-mid)
    - Reservation: fair - inventory_skew * position
    - Tiered takes: three edge levels
    - Passive: two-level ladder with market-join logic, toxic-book suppression
    """

    def __init__(self, params: dict) -> None:
        self.p = params

    def build_orders(self, state: TradingState) -> List[Order]:
        if not self.p.get("ENABLED", True):
            return []
        book = Book(state.order_depths.get("ASH_COATED_OSMIUM"))
        if not book.valid:
            return []
        position = int(state.position.get("ASH_COATED_OSMIUM", 0))
        mgr = Manager("ASH_COATED_OSMIUM", position, PRODUCT_LIMITS["ASH_COATED_OSMIUM"])

        ref = float(self.p["REFERENCE_PRICE"])
        fair = ref + self.p["IMBALANCE_WEIGHT"] * book.imbalance \
                   + self.p["MICRO_WEIGHT"] * (book.micro - book.mid)
        reservation = fair - mgr.projected() * self.p["INVENTORY_SKEW"]

        # Toxic book detection
        adverse = float(self.p["ADVERSE_IMBALANCE"])
        strong = float(self.p["STRONG_IMBALANCE"])
        bid_toxic = book.imbalance < -adverse and book.micro < book.mid
        ask_toxic = book.imbalance > adverse and book.micro > book.mid
        buy_edge_needed = 1.8 if bid_toxic else 1.3
        sell_edge_needed = 1.8 if ask_toxic else 1.3

        # Tiered takes
        buy_edge = reservation - book.best_ask
        take_buy = 0
        for edge_thr, clip in [
            (self.p["TAKE_L1_EDGE"], self.p["TAKE_L1_SIZE"]),
            (self.p["TAKE_L2_EDGE"], self.p["TAKE_L2_SIZE"]),
            (self.p["TAKE_L3_EDGE"], self.p["TAKE_L3_SIZE"]),
        ]:
            if buy_edge >= max(float(edge_thr), buy_edge_needed):
                take_buy = int(clip)
        if take_buy > 0:
            pos = mgr.projected()
            if pos >= self.p["SOFT_LIMIT"]:
                take_buy = max(0, take_buy - 4)
            mgr.buy(book.best_ask, min(book.best_ask_vol, take_buy))

        sell_edge = book.best_bid - reservation
        take_sell = 0
        for edge_thr, clip in [
            (self.p["TAKE_L1_EDGE"], self.p["TAKE_L1_SIZE"]),
            (self.p["TAKE_L2_EDGE"], self.p["TAKE_L2_SIZE"]),
            (self.p["TAKE_L3_EDGE"], self.p["TAKE_L3_SIZE"]),
        ]:
            if sell_edge >= max(float(edge_thr), sell_edge_needed):
                take_sell = int(clip)
        if take_sell > 0:
            pos = mgr.projected()
            if pos <= -self.p["SOFT_LIMIT"]:
                take_sell = max(0, take_sell - 4)
            mgr.sell(book.best_bid, min(book.best_bid_vol, take_sell))

        # Dynamic quote edges (spread + imbalance + toxicity adjustments)
        base_edge = float(self.p["BASE_EDGE"])
        buy_qe = sell_qe = base_edge
        if book.spread_val <= 14:
            buy_qe -= 0.7; sell_qe -= 0.7
        elif book.spread_val >= 18:
            buy_qe += 0.7; sell_qe += 0.7
        if book.imbalance > strong:
            buy_qe -= 0.4; sell_qe += 0.2
        elif book.imbalance < -strong:
            buy_qe += 0.2; sell_qe -= 0.4
        if bid_toxic:
            buy_qe += 1.0
        if ask_toxic:
            sell_qe += 1.0
        pos = mgr.projected()
        soft = int(self.p["SOFT_LIMIT"])
        if pos >= soft:
            buy_qe += 1.2; sell_qe -= 0.8
        elif pos <= -soft:
            buy_qe -= 0.8; sell_qe += 1.2
        buy_qe = max(4.8, buy_qe)
        sell_qe = max(4.8, sell_qe)

        join_edge = float(self.p["JOIN_EDGE"])
        front_buy = int(round(reservation - buy_qe))
        front_sell = int(round(reservation + sell_qe))

        # Market-join: snap to existing resting order if it's at a good edge
        for price, _ in book.buy_levels[:2]:
            if reservation - price >= buy_qe:
                front_buy = price if reservation - price <= join_edge else price + 1
                break
        for price, _ in book.sell_levels[:2]:
            if price - reservation >= sell_qe:
                front_sell = price if price - reservation <= join_edge else price - 1
                break

        front_buy = min(front_buy, book.best_ask - 1)
        front_sell = max(front_sell, book.best_bid + 1)
        back_buy = min(front_buy - 2, book.best_ask - 1)
        back_sell = max(front_sell + 2, book.best_bid + 1)

        allow_bid = not (bid_toxic and pos > 8) and pos < soft + 6
        allow_ask = not (ask_toxic and pos < -8) and pos > -(soft + 6)

        front_sz = int(self.p["FRONT_SIZE"])
        back_sz = int(self.p["BACK_SIZE"])
        if allow_bid and front_buy < book.best_ask and front_buy > 0:
            mgr.buy(front_buy, front_sz)
            if back_buy > 0 and back_buy < book.best_ask:
                mgr.buy(back_buy, back_sz)
        if allow_ask and front_sell > book.best_bid:
            mgr.sell(front_sell, front_sz)
            if back_sell > book.best_bid:
                mgr.sell(back_sell, back_sz)

        return mgr.orders


# ── INTARIAN_PEPPER_ROOT trader ────────────────────────────────────────────────

class IntarianPepperRootTrader:
    """
    Directional MM for strongly trending asset (+1000 ticks/day).
    - State: anchor price + residual EMA persisted in traderData
    - Fair value: weighted blend of trend-line, mid, micro, flow + lookahead bonus
    - Position target: BASE_CARRY + early long bias (fades) + edge/zscore signals
    - Passive quotes anchored to RESERVATION (near mid), NOT to drift-adjusted fair
      → quotes land inside the spread and actually fill
    - Sell suppression in bullish state to stay long through the trend
    """

    def __init__(self, params: dict) -> None:
        self.p = params

    def _load_state(self, memory: dict) -> dict:
        raw = memory.get("IPR_STATE", {})
        if not isinstance(raw, dict):
            raw = {}
        return {
            "initialized": bool(raw.get("initialized", False)),
            "anchor": float(raw.get("anchor", 0.0)),
            "residual_ema": float(raw.get("residual_ema", 0.0)),
            "spread_ema": float(raw.get("spread_ema", 13.0)),
            "short_mid_ema": float(raw.get("short_mid_ema", 0.0)),
            "long_mid_ema": float(raw.get("long_mid_ema", 0.0)),
            "short_gap_ema": float(raw.get("short_gap_ema", 0.0)),
            "reload_ema": float(raw.get("reload_ema", 0.0)),
            "last_ts": float(raw.get("last_ts", -1.0)),
        }

    def _trend_features(self, book: Book, timestamp: int, progress: float, state: dict) -> dict:
        drift = float(self.p["DRIFT_PER_TIMESTAMP"])
        trend_line = float(state["anchor"]) + drift * timestamp
        residual = book.mid - trend_line

        short_mid = ema(float(state["short_mid_ema"]), book.mid, float(self.p["SHORT_MID_ALPHA"]))
        long_mid = ema(float(state["long_mid_ema"]), book.mid, float(self.p["LONG_MID_ALPHA"]))
        short_gap = short_mid - long_mid
        acceleration = short_gap - float(state["short_gap_ema"])
        spread_ema = ema(float(state["spread_ema"]), book.spread_val, float(self.p["SPREAD_ALPHA"]))
        residual_ema = ema(float(state["residual_ema"]), residual, float(self.p["RESIDUAL_ALPHA"]))
        spread_scale = max(4.0, spread_ema * 0.45)
        zscore = residual / spread_scale
        slope = short_gap + drift * 1000.0

        if slope >= float(self.p["ACCEL_SLOPE_THRESHOLD"]) and acceleration >= float(self.p["ACCELERATION_THRESHOLD"]):
            regime = "accelerating"
        elif slope <= float(self.p["WEAK_SLOPE_THRESHOLD"]) or acceleration <= -float(self.p["ACCELERATION_THRESHOLD"]):
            regime = "weakening"
        else:
            regime = "normal"
        if progress >= float(self.p["LATE_UNWIND_START"]) and zscore >= float(self.p["LATE_UNWIND_Z"]):
            regime = "late_rich"

        half_spread = max(1.0, book.spread_val / 2.0)
        flow_fair = book.mid + book.imbalance * half_spread
        lookahead = float(self.p["LOOKAHEAD_BONUS"]) * (1.0 - 0.65 * progress)
        fair = 0.62 * trend_line + 0.14 * short_mid + 0.08 * long_mid + 0.08 * book.micro + 0.08 * flow_fair + lookahead

        return {
            "trend_line": trend_line,
            "residual": residual,
            "residual_ema": residual_ema,
            "spread_ema": spread_ema,
            "short_mid_ema": short_mid,
            "long_mid_ema": long_mid,
            "short_gap_ema": short_gap,
            "reload_ema": float(state["reload_ema"]),
            "slope": slope,
            "acceleration": acceleration,
            "zscore": zscore,
            "regime": regime,
            "fair": fair,
        }

    def _target_inventory(self, progress: float, book: Book, features: dict) -> Tuple[int, bool]:
        regime = str(features["regime"])
        if regime == "accelerating":
            target = float(self.p["ACCEL_TARGET"])
        elif regime == "weakening":
            target = float(self.p["WEAK_TARGET"])
        elif regime == "late_rich":
            target = float(self.p["LATE_TARGET"])
        else:
            target = float(self.p["NORMAL_TARGET"])

        if features["zscore"] < -0.35:
            target += float(self.p["ZSCORE_BUY_BONUS"]) * min(1.0, abs(float(features["zscore"])) / 1.8)
        elif features["zscore"] > 0.55:
            target -= float(self.p["ZSCORE_SELL_PENALTY"]) * min(1.0, (float(features["zscore"]) - 0.55) / 1.3)

        bullish = (
            float(features["zscore"]) < float(self.p["OVEREXTENSION_Z"])
            and book.imbalance >= float(self.p["BULLISH_IMBALANCE"])
            and book.micro >= book.mid
        )
        if bullish and regime != "late_rich":
            target += 6.0
        if progress < 0.18 and regime != "late_rich":
            target = max(target, float(self.p["WEAK_TARGET"]))

        target_int = int(clamp(target, -int(self.p["MAX_SHORT_TARGET"]), int(self.p["MAX_LONG_TARGET"])))
        return target_int, bullish

    def _execution_mode(self, position: int, target: int, book: Book, features: dict, bullish: bool) -> str:
        if position > target + int(self.p["OVERLAY_BAND"]) and float(features["zscore"]) >= 0.85:
            return "overlay_sell"
        if position < target - 12:
            cheap = book.best_ask <= features["fair"] - float(self.p["AGGRESSIVE_BUY_EDGE"])
            if cheap and float(features["reload_ema"]) < float(self.p["RELOAD_COOLDOWN"]):
                return "aggressive_buy"
            return "passive_buy"
        if bullish and position < target - 4:
            return "passive_buy"
        return "hold"

    def build_orders(self, state: TradingState, memory: dict) -> Tuple[List[Order], dict]:
        if not self.p.get("ENABLED", True):
            return [], memory

        book = Book(state.order_depths.get("INTARIAN_PEPPER_ROOT"))
        if not book.valid:
            return [], memory

        position = int(state.position.get("INTARIAN_PEPPER_ROOT", 0))
        mgr = Manager("INTARIAN_PEPPER_ROOT", position, PRODUCT_LIMITS["INTARIAN_PEPPER_ROOT"])
        timestamp = int(getattr(state, "timestamp", 0))
        progress = clamp(timestamp / 999900.0, 0.0, 1.0)

        # ── Load / init persistent state ──────────────────────────────────────
        ps = self._load_state(memory)
        initialized = ps["initialized"]
        anchor = float(ps["anchor"])
        last_ts = float(ps["last_ts"])

        if last_ts >= 0 and timestamp < last_ts:
            initialized = False
            anchor = 0.0

        if not initialized:
            anchor = round(book.mid / 1000.0) * 1000.0
            initialized = True
        ps["anchor"] = anchor
        features = self._trend_features(book, timestamp, progress, ps)
        target_int, bullish = self._target_inventory(progress, book, features)
        reservation = float(features["fair"]) - (mgr.projected() - target_int) * float(self.p["INVENTORY_SKEW"])
        action = self._execution_mode(mgr.projected(), target_int, book, features, bullish)
        overlay_floor = max(0, target_int - int(self.p["OVERLAY_BAND"]))

        if action == "aggressive_buy":
            qty = min(book.best_ask_vol, 16, max(0, target_int + 12 - mgr.projected()))
            mgr.buy(book.best_ask, qty)
            ps["reload_ema"] = ema(float(ps["reload_ema"]), 8.0, float(self.p["RELOAD_PAUSE_ALPHA"]))
        else:
            ps["reload_ema"] = ema(float(ps["reload_ema"]), 0.0, float(self.p["RELOAD_PAUSE_ALPHA"]))

        if action == "overlay_sell":
            sell_edge = float(book.best_bid) - reservation
            if sell_edge >= float(self.p["OVERLAY_SELL_EDGE"]) and mgr.sell_cap > 0:
                qty = min(book.best_bid_vol, 4, max(0, mgr.projected() - overlay_floor))
                mgr.sell(book.best_bid, qty)

        base_qe = float(self.p["BASE_QUOTE_EDGE"])
        buy_qe = base_qe
        sell_qe = base_qe + 0.95
        if action == "passive_buy":
            buy_qe -= 0.85
        elif action == "hold":
            buy_qe -= 0.20 if bullish else 0.0
        if float(features["zscore"]) > 0.95:
            sell_qe -= 0.20
        if bullish:
            sell_qe += 0.90

        front_buy = math.floor(reservation - buy_qe)
        front_sell = math.ceil(reservation + sell_qe)
        front_buy = min(front_buy, book.best_ask - 1)
        front_sell = max(front_sell, book.best_bid + 1)
        back_buy = min(front_buy - 2, book.best_ask - 1)

        front_sz = int(self.p["PASSIVE_FRONT_SIZE"])
        back_sz = int(self.p["PASSIVE_BACK_SIZE"])
        buy_buf = int(self.p["PASSIVE_BUY_BUFFER"])
        sell_buf = int(self.p["PASSIVE_SELL_BUFFER"])

        if action in {"passive_buy", "hold"} and front_buy > 0 and front_buy < book.best_ask:
            qty = min(front_sz, mgr.buy_cap, max(0, target_int + buy_buf - mgr.projected()))
            mgr.buy(front_buy, qty)
            if action == "passive_buy" and back_buy > 0 and back_buy < book.best_ask:
                qty = min(back_sz, mgr.buy_cap, max(0, target_int + buy_buf - mgr.projected()))
                mgr.buy(back_buy, qty)

        allow_overlay_sell = action == "overlay_sell"
        if not allow_overlay_sell:
            allow_overlay_sell = str(features["regime"]) == "late_rich" and mgr.projected() > overlay_floor
        if allow_overlay_sell and front_sell > book.best_bid:
            sell_front = max(2, front_sz - 5 if bullish else front_sz - 3)
            qty = min(sell_front, mgr.sell_cap, max(0, mgr.projected() - max(overlay_floor, target_int - sell_buf)))
            mgr.sell(front_sell, qty)

        # ── Save state ────────────────────────────────────────────────────────
        memory["IPR_STATE"] = {
            "anchor": anchor,
            "residual_ema": float(features["residual_ema"]),
            "spread_ema": float(features["spread_ema"]),
            "short_mid_ema": float(features["short_mid_ema"]),
            "long_mid_ema": float(features["long_mid_ema"]),
            "short_gap_ema": float(features["short_gap_ema"]),
            "reload_ema": float(ps["reload_ema"]),
            "last_ts": float(timestamp),
            "initialized": True,
        }

        return mgr.orders, memory


# ── Top-level Trader ───────────────────────────────────────────────────────────

class Trader:
    def __init__(self) -> None:
        self.ash = AshCoatedOsmiumTrader(DEFAULT_ASH_PARAMS)
        self.ipr = IntarianPepperRootTrader(DEFAULT_IPR_PARAMS)

    def _load_memory(self, trader_data: str) -> dict:
        if not trader_data:
            return {}
        try:
            parsed = json.loads(trader_data)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    def run(self, state: TradingState):
        memory = self._load_memory(state.traderData if hasattr(state, "traderData") else "")
        result: Dict[str, List[Order]] = {}

        if "ASH_COATED_OSMIUM" in state.order_depths:
            result["ASH_COATED_OSMIUM"] = self.ash.build_orders(state)

        if "INTARIAN_PEPPER_ROOT" in state.order_depths:
            ipr_orders, memory = self.ipr.build_orders(state, memory)
            result["INTARIAN_PEPPER_ROOT"] = ipr_orders

        trader_data = json.dumps(memory, separators=(",", ":"))
        return result, 0, trader_data
