from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Tuple

try:
    from datamodel import Order, OrderDepth, TradingState
except ModuleNotFoundError:
    from trader_factory.core.datamodel import Order, OrderDepth, TradingState

PRODUCT_LIMITS = {
    "ASH_COATED_OSMIUM": 80,
    "INTARIAN_PEPPER_ROOT": 80,
}

DEFAULT_ASH_PARAMS = {
    "ENABLED": True,
    "REFERENCE_PRICE": 10000.0,
    # Local-fair layer from the current best trunk
    "ANCHOR_WEIGHT": 0.42,
    "STABLE_MID_WEIGHT": 0.58,
    "WALL_MID_BLEND": 0.32,
    "LOCAL_MICRO_WEIGHT": 0.42,
    "LOCAL_IMBALANCE_BIAS": 0.16,
    "DEPTH_IMPACT_SCALE": 58.0,
    "DEPTH_FLOOR": 8.0,
    # Inventory / quoting
    "INVENTORY_SKEW": 0.104,
    "INVENTORY_CURVE": 2.2,
    "BASE_EDGE": 2.0,
    "JOIN_EDGE": 2.0,
    "FRONT_SIZE": 18,
    "BACK_SIZE": 5,
    "SOFT_LIMIT": 70.0,
    # Taking logic
    "TAKE_L1_EDGE": 2.0,
    "TAKE_L1_SIZE": 6,
    "TAKE_L2_EDGE": 5.0,
    "TAKE_L2_SIZE": 10,
    "TAKE_L3_EDGE": 8.0,
    "TAKE_L3_SIZE": 16,
    # Toxicity thresholds
    "ADVERSE_IMBALANCE": 0.20,
    "STRONG_IMBALANCE": 0.16,
    # Small HMM-style execution state filter
    "P_CALM_INIT": 0.45,
    "P_NORMAL_INIT": 0.40,
    "P_TOXIC_INIT": 0.15,
    "CALM_SIGMA": 1.0,
    "NORMAL_SIGMA": 2.2,
    "TOXIC_SIGMA": 4.0,
    "MARKOUT_ALPHA": 0.16,
    "SPREAD_ALPHA": 0.12,
    "QUOTE_PENALTY_SCALE": 0.75,
    "STATE_TOXIC_WIDEN": 0.90,
    "STATE_CALM_TIGHTEN": 0.20,
    "STRONG_ONE_SIDED_PROB": 0.62,
    "DISLOCATION_EDGE_BONUS": 0.85,
}

DEFAULT_IPR_PARAMS = {
    "ENABLED": True,
    "DRIFT_PER_TIMESTAMP": 0.0026009226,
    "RESIDUAL_ALPHA": 0.10,
    "SPREAD_ALPHA": 0.08,
    "LOOKAHEAD_BONUS": 4.8849030549,
    # Position targeting
    "BASE_CARRY": 7.7045484383,
    "EARLY_LONG_BIAS": 43.1941331644,
    "EDGE_TARGET_SCALE": 12.0,
    "ZSCORE_BUY_BONUS": 12.0,
    "ZSCORE_SELL_PENALTY": 8.0,
    "MAX_LONG_TARGET": 76.0,
    "MAX_SHORT_TARGET": 20,
    "EARLY_ACCUM_END": 0.42,
    # Execution
    "INVENTORY_SKEW": 0.078,
    "BASE_TAKE_EDGE": 2.7678379562,
    "BASE_QUOTE_EDGE": 5.351603402,
    "SOFT_LIMIT": 52,
    "PASSIVE_FRONT_SIZE": 9,
    "PASSIVE_BACK_SIZE": 6,
    "PASSIVE_BUY_BUFFER": 18,
    "PASSIVE_SELL_BUFFER": 8,
    "OVEREXTENSION_Z": 1.05,
    "BULLISH_IMBALANCE": 0.05,
    # Cheaper accumulation overlay from the best trunk
    "CHEAP_ACCUM_END": 0.56,
    "CHEAP_ACCUM_TAKE_PENALTY": 0.08,
    "CHEAP_ACCUM_QUOTE_EDGE_BONUS": 0.45,
    "CHEAP_ACCUM_FRONT_SIZE_BONUS": 1,
    "CHEAP_ACCUM_BACK_SIZE_BONUS": 1,
    "CHEAP_ACCUM_Z_RELAX": -0.55,
    "CHEAP_ACCUM_TARGET_BUFFER": 20,
    # Small innovation gate: buy dips vs expected drift, avoid paying up after positive shocks
    "INNOV_ALPHA": 0.18,
    "NEG_SHOCK_Z": -0.55,
    "POS_SHOCK_Z": 0.85,
    "POS_SHOCK_TAKE_PENALTY": 0.38,
    "POS_SHOCK_QUOTE_WIDEN": 0.55,
    "NEG_SHOCK_TAKE_BONUS": 0.10,
    "NEG_SHOCK_QUOTE_TIGHTEN": 0.18,
}


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


class AshCoatedOsmiumTrader:
    """
    Osmium base branch with:
    - local-fair / wall-mid estimator
    - nonlinear inventory pressure
    - small HMM-style execution state filter (calm / normal / toxic)
    - markout-aware quoting: passive quotes are penalized by recent post-fill drift
    - one-sided quoting when the toxic state is dominant
    """

    def __init__(self, params: dict) -> None:
        self.p = params

    def _load_state(self, memory: dict) -> dict:
        raw = memory.get("OSM_STATE", {})
        if not isinstance(raw, dict):
            raw = {}
        return {
            "initialized": bool(raw.get("initialized", False)),
            "prev_mid": float(raw.get("prev_mid", 0.0)),
            "prev_fair": float(raw.get("prev_fair", 0.0)),
            "spread_ema": float(raw.get("spread_ema", 16.0)),
            "p_calm": float(raw.get("p_calm", self.p["P_CALM_INIT"])),
            "p_normal": float(raw.get("p_normal", self.p["P_NORMAL_INIT"])),
            "p_toxic": float(raw.get("p_toxic", self.p["P_TOXIC_INIT"])),
            "bid_markout_ema": float(raw.get("bid_markout_ema", 0.0)),
            "ask_markout_ema": float(raw.get("ask_markout_ema", 0.0)),
            "last_position": int(raw.get("last_position", 0)),
            "last_ts": float(raw.get("last_ts", -1.0)),
        }

    def _gaussian_likelihood(self, value: float, mean: float, sigma: float) -> float:
        sigma = max(1e-6, sigma)
        z = (value - mean) / sigma
        return math.exp(-0.5 * z * z) / sigma

    def _stable_mid(self, book: Book) -> float:
        bid_levels = book.buy_levels[:3]
        ask_levels = book.sell_levels[:3]
        bid_vol = sum(v for _, v in bid_levels)
        ask_vol = sum(v for _, v in ask_levels)
        if bid_vol <= 0 or ask_vol <= 0:
            return book.mid
        popular_bid = sum(px * vol for px, vol in bid_levels) / bid_vol
        popular_ask = sum(px * vol for px, vol in ask_levels) / ask_vol
        wall_bid = max(bid_levels, key=lambda x: (x[1], x[0]))[0]
        wall_ask = min(ask_levels, key=lambda x: (-x[1], x[0]))[0]
        popular_mid = (popular_bid + popular_ask) / 2.0
        wall_mid = (wall_bid + wall_ask) / 2.0
        return (
            (1.0 - float(self.p["WALL_MID_BLEND"])) * popular_mid
            + float(self.p["WALL_MID_BLEND"]) * wall_mid
        )

    def _fair_value(self, book: Book) -> float:
        stable_mid = self._stable_mid(book)
        depth = max(float(self.p["DEPTH_FLOOR"]), float(book.best_bid_vol + book.best_ask_vol))
        beta = float(self.p["DEPTH_IMPACT_SCALE"]) / depth
        return (
            float(self.p["ANCHOR_WEIGHT"]) * float(self.p["REFERENCE_PRICE"])
            + float(self.p["STABLE_MID_WEIGHT"]) * stable_mid
            + float(self.p["LOCAL_MICRO_WEIGHT"]) * (book.micro - book.mid)
            + (beta + float(self.p["LOCAL_IMBALANCE_BIAS"])) * book.imbalance
        )

    def _reservation(self, fair: float, projected_pos: int, p_toxic: float) -> float:
        inv_ratio = projected_pos / float(PRODUCT_LIMITS["ASH_COATED_OSMIUM"])
        inv_shift = float(self.p["INVENTORY_SKEW"]) * projected_pos * (1.0 + 0.35 * p_toxic)
        inv_shift += float(self.p["INVENTORY_CURVE"]) * (inv_ratio ** 3)
        return fair - inv_shift

    def _update_state(self, book: Book, fair: float, position: int, timestamp: int, state: dict) -> dict:
        last_ts = float(state["last_ts"])
        if last_ts >= 0 and timestamp < last_ts:
            state = {
                "initialized": False,
                "prev_mid": 0.0,
                "prev_fair": 0.0,
                "spread_ema": 16.0,
                "p_calm": self.p["P_CALM_INIT"],
                "p_normal": self.p["P_NORMAL_INIT"],
                "p_toxic": self.p["P_TOXIC_INIT"],
                "bid_markout_ema": 0.0,
                "ask_markout_ema": 0.0,
                "last_position": 0,
                "last_ts": -1.0,
            }

        prev_mid = float(state["prev_mid"])
        prev_fair = float(state["prev_fair"])
        prev_pos = int(state["last_position"])
        delta_pos = position - prev_pos

        bid_markout = float(state["bid_markout_ema"])
        ask_markout = float(state["ask_markout_ema"])
        if prev_mid > 0.0:
            if delta_pos > 0:
                # We bought and then observed a lower mid -> adverse for the bid side.
                bid_markout = ema(bid_markout, max(0.0, prev_mid - book.mid), float(self.p["MARKOUT_ALPHA"]))
                ask_markout = ema(ask_markout, 0.0, float(self.p["MARKOUT_ALPHA"]) * 0.5)
            elif delta_pos < 0:
                # We sold and then observed a higher mid -> adverse for the ask side.
                ask_markout = ema(ask_markout, max(0.0, book.mid - prev_mid), float(self.p["MARKOUT_ALPHA"]))
                bid_markout = ema(bid_markout, 0.0, float(self.p["MARKOUT_ALPHA"]) * 0.5)
            else:
                bid_markout = ema(bid_markout, 0.0, float(self.p["MARKOUT_ALPHA"]) * 0.3)
                ask_markout = ema(ask_markout, 0.0, float(self.p["MARKOUT_ALPHA"]) * 0.3)

        spread_ema = ema(float(state["spread_ema"]), book.spread_val, float(self.p["SPREAD_ALPHA"]))
        delta_mid = 0.0 if prev_mid <= 0.0 else (book.mid - prev_mid)
        delta_fair = 0.0 if prev_fair <= 0.0 else (fair - prev_fair)
        innovation = delta_mid - delta_fair
        abs_innov = abs(innovation)

        transition = (
            (0.78, 0.18, 0.04),
            (0.18, 0.68, 0.14),
            (0.10, 0.22, 0.68),
        )
        current_probs = (
            float(state["p_calm"]),
            float(state["p_normal"]),
            float(state["p_toxic"]),
        )
        predicted = [
            current_probs[0] * transition[0][i]
            + current_probs[1] * transition[1][i]
            + current_probs[2] * transition[2][i]
            for i in range(3)
        ]

        calm_like = self._gaussian_likelihood(abs_innov, 0.0, float(self.p["CALM_SIGMA"]))
        calm_like *= self._gaussian_likelihood(book.spread_val, spread_ema, max(1.0, 0.20 * spread_ema))
        normal_like = self._gaussian_likelihood(abs_innov, 1.1, float(self.p["NORMAL_SIGMA"]))
        toxic_like = self._gaussian_likelihood(abs_innov, 3.0, float(self.p["TOXIC_SIGMA"]))

        if abs(book.imbalance) < 0.08:
            calm_like *= 1.05
        if abs(book.imbalance) > 0.16:
            toxic_like *= 1.30
        if book.spread_val > spread_ema + 1.0:
            toxic_like *= 1.20
        if max(bid_markout, ask_markout) > 1.2:
            toxic_like *= 1.25
        if abs(book.imbalance) < 0.10 and abs_innov < 1.0:
            normal_like *= 0.95
            calm_like *= 1.05

        post = [
            predicted[0] * calm_like,
            predicted[1] * normal_like,
            predicted[2] * toxic_like,
        ]
        total_post = sum(post)
        if total_post <= 1e-12:
            p_calm, p_normal, p_toxic = current_probs
        else:
            p_calm = post[0] / total_post
            p_normal = post[1] / total_post
            p_toxic = post[2] / total_post

        return {
            "initialized": True,
            "prev_mid": book.mid,
            "prev_fair": fair,
            "spread_ema": spread_ema,
            "p_calm": p_calm,
            "p_normal": p_normal,
            "p_toxic": p_toxic,
            "bid_markout_ema": bid_markout,
            "ask_markout_ema": ask_markout,
            "last_position": position,
            "last_ts": float(timestamp),
            "innovation": innovation,
            "abs_innov": abs_innov,
        }

    def build_orders(self, state: TradingState, memory: dict) -> Tuple[List[Order], dict]:
        if not self.p.get("ENABLED", True):
            return [], memory
        book = Book(state.order_depths.get("ASH_COATED_OSMIUM"))
        if not book.valid:
            return [], memory

        position = int(state.position.get("ASH_COATED_OSMIUM", 0))
        mgr = Manager("ASH_COATED_OSMIUM", position, PRODUCT_LIMITS["ASH_COATED_OSMIUM"])
        timestamp = int(getattr(state, "timestamp", 0))

        state_mem = self._load_state(memory)
        fair = self._fair_value(book)
        state_mem = self._update_state(book, fair, position, timestamp, state_mem)
        p_calm = float(state_mem["p_calm"])
        p_normal = float(state_mem["p_normal"])
        p_toxic = float(state_mem["p_toxic"])
        bid_penalty = float(state_mem["bid_markout_ema"]) + 0.80 * p_toxic
        ask_penalty = float(state_mem["ask_markout_ema"]) + 0.80 * p_toxic

        reservation = self._reservation(fair, mgr.projected(), p_toxic)

        adverse = float(self.p["ADVERSE_IMBALANCE"])
        strong = float(self.p["STRONG_IMBALANCE"])
        bid_toxic = (book.imbalance < -adverse and book.micro < book.mid) or (p_toxic > 0.62 and book.imbalance < 0.0)
        ask_toxic = (book.imbalance > adverse and book.micro > book.mid) or (p_toxic > 0.62 and book.imbalance > 0.0)
        buy_edge_needed = (1.8 if bid_toxic else 1.3) + self.p["DISLOCATION_EDGE_BONUS"] * p_toxic
        sell_edge_needed = (1.8 if ask_toxic else 1.3) + self.p["DISLOCATION_EDGE_BONUS"] * p_toxic

        # Aggressive takes: stricter in toxic states, but still use the local fair / reservation.
        buy_edge = reservation - book.best_ask - bid_penalty
        take_buy = 0
        for edge_thr, clip in [
            (self.p["TAKE_L1_EDGE"], self.p["TAKE_L1_SIZE"]),
            (self.p["TAKE_L2_EDGE"], self.p["TAKE_L2_SIZE"]),
            (self.p["TAKE_L3_EDGE"], self.p["TAKE_L3_SIZE"]),
        ]:
            if buy_edge >= max(float(edge_thr), buy_edge_needed):
                take_buy = int(clip)
        if p_toxic > 0.45:
            take_buy = max(0, take_buy - 2)
        if take_buy > 0:
            pos = mgr.projected()
            if pos >= self.p["SOFT_LIMIT"]:
                take_buy = max(0, take_buy - 4)
            mgr.buy(book.best_ask, min(book.best_ask_vol, take_buy))

        sell_edge = book.best_bid - reservation - ask_penalty
        take_sell = 0
        for edge_thr, clip in [
            (self.p["TAKE_L1_EDGE"], self.p["TAKE_L1_SIZE"]),
            (self.p["TAKE_L2_EDGE"], self.p["TAKE_L2_SIZE"]),
            (self.p["TAKE_L3_EDGE"], self.p["TAKE_L3_SIZE"]),
        ]:
            if sell_edge >= max(float(edge_thr), sell_edge_needed):
                take_sell = int(clip)
        if p_toxic > 0.45:
            take_sell = max(0, take_sell - 2)
        if take_sell > 0:
            pos = mgr.projected()
            if pos <= -self.p["SOFT_LIMIT"]:
                take_sell = max(0, take_sell - 4)
            mgr.sell(book.best_bid, min(book.best_bid_vol, take_sell))

        base_edge = float(self.p["BASE_EDGE"])
        buy_qe = sell_qe = base_edge
        if book.spread_val <= 14:
            buy_qe -= 0.7
            sell_qe -= 0.7
        elif book.spread_val >= 18:
            buy_qe += 0.7
            sell_qe += 0.7
        if book.imbalance > strong:
            buy_qe -= 0.4
            sell_qe += 0.2
        elif book.imbalance < -strong:
            buy_qe += 0.2
            sell_qe -= 0.4
        if p_calm > 0.55 and abs(book.imbalance) < 0.10:
            buy_qe -= float(self.p["STATE_CALM_TIGHTEN"])
            sell_qe -= float(self.p["STATE_CALM_TIGHTEN"])
        if p_toxic > 0.45:
            buy_qe += float(self.p["STATE_TOXIC_WIDEN"])
            sell_qe += float(self.p["STATE_TOXIC_WIDEN"])
        if bid_toxic:
            buy_qe += 1.0
        if ask_toxic:
            sell_qe += 1.0

        pos = mgr.projected()
        soft = int(self.p["SOFT_LIMIT"])
        if pos >= soft:
            buy_qe += 1.2
            sell_qe -= 0.8
        elif pos <= -soft:
            buy_qe -= 0.8
            sell_qe += 1.2
        buy_qe += float(self.p["QUOTE_PENALTY_SCALE"]) * bid_penalty
        sell_qe += float(self.p["QUOTE_PENALTY_SCALE"]) * ask_penalty
        buy_qe = max(4.6, buy_qe)
        sell_qe = max(4.6, sell_qe)

        join_edge = float(self.p["JOIN_EDGE"])
        front_buy = int(round(reservation - buy_qe))
        front_sell = int(round(reservation + sell_qe))

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

        # Markout-aware gating: only quote if gross edge exceeds the side penalty.
        gross_bid_edge = reservation - front_buy
        gross_ask_edge = front_sell - reservation
        allow_bid = gross_bid_edge > bid_penalty + 0.35
        allow_ask = gross_ask_edge > ask_penalty + 0.35

        if bid_toxic and pos > 8:
            allow_bid = False
        if ask_toxic and pos < -8:
            allow_ask = False
        if pos >= soft + 6:
            allow_bid = False
        if pos <= -(soft + 6):
            allow_ask = False
        if p_toxic > float(self.p["STRONG_ONE_SIDED_PROB"]):
            if book.imbalance < 0.0:
                allow_bid = False
            elif book.imbalance > 0.0:
                allow_ask = False

        front_sz = int(round(float(self.p["FRONT_SIZE"]) * (1.10 if p_calm > 0.58 else 0.85 if p_toxic > 0.52 else 1.0)))
        back_sz = int(round(float(self.p["BACK_SIZE"]) * (1.05 if p_calm > 0.58 else 0.80 if p_toxic > 0.52 else 1.0)))
        front_sz = max(4, front_sz)
        back_sz = max(2, back_sz)

        # Gentle zero-edge inventory clearing: free capacity when inventory is stretched and state is not toxic.
        if p_toxic < 0.40:
            if pos > int(0.75 * soft) and front_sell > book.best_bid:
                front_sell = max(book.best_bid + 1, min(front_sell, int(round(reservation + 4.8))))
            elif pos < -int(0.75 * soft) and front_buy < book.best_ask:
                front_buy = min(book.best_ask - 1, max(front_buy, int(round(reservation - 4.8))))

        if allow_bid and front_buy > 0 and front_buy < book.best_ask:
            mgr.buy(front_buy, min(front_sz, mgr.buy_cap))
            if back_buy > 0 and back_buy < book.best_ask and p_toxic < 0.55:
                mgr.buy(back_buy, min(back_sz, mgr.buy_cap))
        if allow_ask and front_sell > book.best_bid:
            mgr.sell(front_sell, min(front_sz, mgr.sell_cap))
            if back_sell > book.best_bid and p_toxic < 0.55:
                mgr.sell(back_sell, min(back_sz, mgr.sell_cap))

        memory["OSM_STATE"] = {
            "initialized": True,
            "prev_mid": state_mem["prev_mid"],
            "prev_fair": state_mem["prev_fair"],
            "spread_ema": state_mem["spread_ema"],
            "p_calm": state_mem["p_calm"],
            "p_normal": state_mem["p_normal"],
            "p_toxic": state_mem["p_toxic"],
            "bid_markout_ema": state_mem["bid_markout_ema"],
            "ask_markout_ema": state_mem["ask_markout_ema"],
            "last_position": position,
            "last_ts": float(timestamp),
        }
        return mgr.orders, memory


class IntarianPepperRootTrader:
    """
    Keep the currently best Pepper architecture mostly intact.
    Add only a small innovation gate on buys: buy dips relative to the expected drift,
    but avoid paying up after positive shocks.
    """

    def __init__(self, params: dict) -> None:
        self.p = params

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

        ps = memory.get("IPR_STATE", {})
        if not isinstance(ps, dict):
            ps = {}

        initialized = bool(ps.get("initialized", False))
        anchor = float(ps.get("anchor", 0.0))
        residual_ema_val = float(ps.get("residual_ema", 0.0))
        spread_ema_val = float(ps.get("spread_ema", 13.0))
        last_ts = float(ps.get("last_ts", -1.0))
        prev_mid = float(ps.get("prev_mid", 0.0))
        innov_ema = float(ps.get("innov_ema", 0.0))

        if last_ts >= 0 and timestamp < last_ts:
            initialized = False
            anchor = 0.0
            residual_ema_val = 0.0
            spread_ema_val = 13.0
            prev_mid = 0.0
            innov_ema = 0.0

        drift = float(self.p["DRIFT_PER_TIMESTAMP"])
        trend_line = anchor + drift * timestamp

        if not initialized:
            anchor = round(book.mid / 1000.0) * 1000.0
            trend_line = anchor
            residual_ema_val = 0.0
            spread_ema_val = float(book.spread_val)
            initialized = True
        else:
            spread_ema_val = ema(spread_ema_val, book.spread_val, float(self.p["SPREAD_ALPHA"]))

        residual = book.mid - trend_line
        residual_ema_val = ema(residual_ema_val, residual, float(self.p["RESIDUAL_ALPHA"]))

        # Drift-dominant fair
        half_spread = max(1.0, book.spread_val / 2.0)
        flow_fair = book.mid + book.imbalance * half_spread
        lookahead = float(self.p["LOOKAHEAD_BONUS"]) * (1.0 - 0.65 * progress)
        fair = (
            0.60 * trend_line
            + 0.12 * book.mid
            + 0.10 * book.micro
            + 0.10 * flow_fair
            + 0.08 * (trend_line + residual)
            + lookahead
        )

        spread_scale = max(4.0, spread_ema_val * 0.45)
        zscore = residual / spread_scale

        # Small innovation filter around expected drift.
        dt = max(100.0, float(timestamp) - last_ts) if last_ts >= 0.0 else 100.0
        expected_move = drift * dt
        innovation = 0.0 if prev_mid <= 0.0 else (book.mid - prev_mid) - expected_move
        innov_ema = ema(innov_ema, innovation, float(self.p["INNOV_ALPHA"]))
        innov_scale = max(2.0, spread_ema_val * 0.25)
        innov_z = innov_ema / innov_scale

        edge = fair - book.mid
        target = float(self.p["BASE_CARRY"])
        early_factor = max(0.0, 1.0 - progress / 0.85)
        target += float(self.p["EARLY_LONG_BIAS"]) * early_factor
        target += float(self.p["EDGE_TARGET_SCALE"]) * edge

        if zscore < 0.0:
            target += float(self.p["ZSCORE_BUY_BONUS"]) * min(1.0, abs(zscore) / 1.8)
        if zscore > 0.45:
            target -= float(self.p["ZSCORE_SELL_PENALTY"]) * min(1.0, (zscore - 0.45) / 1.4)
        if book.imbalance < -0.18 and book.micro < book.mid:
            target -= 6.0

        bullish = (
            zscore < float(self.p["OVEREXTENSION_Z"])
            and book.imbalance >= float(self.p["BULLISH_IMBALANCE"])
            and book.micro >= book.mid
        )
        if bullish:
            target += 8.0

        if progress < 0.18 and zscore <= 0.45:
            target = max(target, 32.0)
        elif progress < 0.35 and zscore <= 0.25:
            target = max(target, 24.0)
        if progress > 0.85 and zscore > 1.25:
            target -= 8.0

        max_long = int(self.p["MAX_LONG_TARGET"])
        max_short = int(self.p["MAX_SHORT_TARGET"])
        target_int = int(clamp(target, -max_short, max_long))

        skew = float(self.p["INVENTORY_SKEW"])
        reservation = fair - (mgr.projected() - target_int) * skew

        base_take = float(self.p["BASE_TAKE_EDGE"])
        buy_te = base_take
        sell_te = base_take + 0.55
        pos = mgr.projected()
        if pos < target_int:
            buy_te -= 0.35
        if pos > target_int:
            sell_te -= 0.05
        if zscore < -0.45:
            buy_te -= 0.30
        elif zscore > 0.85:
            sell_te -= 0.15
        if bullish:
            buy_te -= 0.10
            sell_te += 0.90
        if progress < 0.55 and pos < target_int:
            sell_te += 0.25
        if pos < max(20, target_int - 10):
            sell_te += 0.55
        if (
            progress < float(self.p["CHEAP_ACCUM_END"])
            and pos < target_int
            and zscore > float(self.p["CHEAP_ACCUM_Z_RELAX"])
        ):
            buy_te += float(self.p["CHEAP_ACCUM_TAKE_PENALTY"])
        if innov_z > float(self.p["POS_SHOCK_Z"]):
            buy_te += float(self.p["POS_SHOCK_TAKE_PENALTY"])
        elif innov_z < float(self.p["NEG_SHOCK_Z"]):
            buy_te -= float(self.p["NEG_SHOCK_TAKE_BONUS"])
        buy_te = max(0.35, buy_te)
        sell_te = max(1.05, sell_te)

        buy_edge_avail = reservation - book.best_ask
        if buy_edge_avail >= buy_te and mgr.buy_cap > 0:
            qty = min(book.best_ask_vol, 16, max(0, target_int + 16 - mgr.projected()))
            mgr.buy(book.best_ask, qty)

        sell_edge_avail = book.best_bid - reservation
        if sell_edge_avail >= sell_te and mgr.sell_cap > 0:
            pos = mgr.projected()
            qty = min(book.best_bid_vol, 16, max(0, pos - (target_int - 4)))
            if bullish and pos < max(26, target_int - 6):
                qty = 0
            elif bullish and pos > 0:
                qty = min(qty, 4)
            mgr.sell(book.best_bid, qty)

        base_qe = float(self.p["BASE_QUOTE_EDGE"])
        buy_qe = base_qe
        sell_qe = base_qe + 0.75
        pos = mgr.projected()
        if pos < target_int:
            buy_qe -= 0.55
        if pos > target_int:
            sell_qe -= 0.10
        if zscore < -0.55:
            buy_qe -= 0.30
        elif zscore > 1.00:
            sell_qe -= 0.15
        cheap_accum = (
            progress < float(self.p["CHEAP_ACCUM_END"])
            and pos < target_int
            and zscore > float(self.p["CHEAP_ACCUM_Z_RELAX"])
        )
        if cheap_accum:
            buy_qe -= float(self.p["CHEAP_ACCUM_QUOTE_EDGE_BONUS"])
        if innov_z > float(self.p["POS_SHOCK_Z"]):
            buy_qe += float(self.p["POS_SHOCK_QUOTE_WIDEN"])
        elif innov_z < float(self.p["NEG_SHOCK_Z"]) and pos < target_int:
            buy_qe -= float(self.p["NEG_SHOCK_QUOTE_TIGHTEN"])

        front_buy = math.floor(reservation - buy_qe)
        front_sell = math.ceil(reservation + sell_qe)

        if bullish and pos < target_int:
            front_buy = max(front_buy, book.best_bid + 1)
        elif cheap_accum and pos < target_int:
            front_buy = max(front_buy, book.best_bid + 1)
        if bullish and pos > 0:
            front_sell += 2

        front_buy = min(front_buy, book.best_ask - 1)
        front_sell = max(front_sell, book.best_bid + 1)
        back_buy = min(front_buy - 2, book.best_ask - 1)
        back_sell = max(front_sell + 2, book.best_bid + 1)

        early_accum = float(self.p["EARLY_ACCUM_END"])
        allow_sell = True
        if progress < early_accum and pos < target_int - 6:
            allow_sell = False
        if bullish and pos < max(24, target_int - 4):
            allow_sell = False

        front_sz = int(self.p["PASSIVE_FRONT_SIZE"])
        back_sz = int(self.p["PASSIVE_BACK_SIZE"])
        buy_buf = int(self.p["PASSIVE_BUY_BUFFER"])
        sell_buf = int(self.p["PASSIVE_SELL_BUFFER"])
        buy_front_sz = front_sz + (int(self.p["CHEAP_ACCUM_FRONT_SIZE_BONUS"]) if cheap_accum else 0)
        buy_back_sz = back_sz + (int(self.p["CHEAP_ACCUM_BACK_SIZE_BONUS"]) if cheap_accum else 0)
        buy_cap_target = target_int + (
            int(self.p["CHEAP_ACCUM_TARGET_BUFFER"]) if cheap_accum else buy_buf
        )

        quotes: List[Tuple[str, int, int]] = []
        if front_buy > 0 and front_buy < book.best_ask:
            quotes.append(("buy", front_buy, buy_front_sz))
            if back_buy > 0 and back_buy < book.best_ask:
                quotes.append(("buy", back_buy, buy_back_sz))
        if allow_sell and front_sell > book.best_bid:
            sell_front = max(3, front_sz - (3 if bullish else 1))
            sell_back = max(2, back_sz - (2 if bullish else 1))
            quotes.append(("sell", front_sell, sell_front))
            if back_sell > book.best_bid:
                quotes.append(("sell", back_sell, sell_back))

        for side, price, size in quotes:
            pos = mgr.projected()
            if side == "buy" and pos < buy_cap_target:
                qty = min(size, mgr.buy_cap, max(0, buy_cap_target - pos))
                mgr.buy(price, qty)
            elif side == "sell" and pos > target_int - sell_buf:
                qty = min(size, mgr.sell_cap, max(0, pos - (target_int - sell_buf)))
                mgr.sell(price, qty)

        memory["IPR_STATE"] = {
            "anchor": anchor,
            "residual_ema": residual_ema_val,
            "spread_ema": spread_ema_val,
            "prev_mid": book.mid,
            "innov_ema": innov_ema,
            "last_ts": float(timestamp),
            "initialized": True,
        }

        return mgr.orders, memory


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
            ash_orders, memory = self.ash.build_orders(state, memory)
            result["ASH_COATED_OSMIUM"] = ash_orders

        if "INTARIAN_PEPPER_ROOT" in state.order_depths:
            ipr_orders, memory = self.ipr.build_orders(state, memory)
            result["INTARIAN_PEPPER_ROOT"] = ipr_orders

        trader_data = json.dumps(memory, separators=(",", ":"))
        return result, 0, trader_data
