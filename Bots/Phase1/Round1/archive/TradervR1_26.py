from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Tuple

try:
    from datamodel import Order, OrderDepth, TradingState
except ModuleNotFoundError:
    from trader_factory.core.datamodel import Order, OrderDepth, TradingState

# Round 1 limits
PRODUCT_LIMITS = {
    "ASH_COATED_OSMIUM": 80,
    "INTARIAN_PEPPER_ROOT": 80,
}

DEFAULT_ASH_PARAMS = {
    "ENABLED": True,
    "REFERENCE_PRICE": 10000.0,
    "IMBALANCE_WEIGHT": 1.0530199689,
    "MICRO_WEIGHT": 0.35,
    "INVENTORY_SKEW": 0.1197820182,
    "BASE_EDGE": 2.0,
    "JOIN_EDGE": 2.0,
    "FRONT_SIZE": 17.52842512,
    "BACK_SIZE": 5,
    "SOFT_LIMIT": 70.0,
    "TAKE_L1_EDGE": 2.0,
    "TAKE_L1_SIZE": 6,
    "TAKE_L2_EDGE": 5.0,
    "TAKE_L2_SIZE": 10,
    "TAKE_L3_EDGE": 8.0,
    "TAKE_L3_SIZE": 16,
    "ADVERSE_IMBALANCE": 0.20,
    "STRONG_IMBALANCE": 0.16,
}

DEFAULT_IPR_PARAMS = {
    "ENABLED": True,
    # Trend backbone
    "DRIFT_PER_TIMESTAMP": 0.0026009226,
    "RESIDUAL_ALPHA": 0.10,
    "SPREAD_ALPHA": 0.08,
    "SHORT_MID_ALPHA": 0.18,
    "LONG_MID_ALPHA": 0.05,
    "LOOKAHEAD_BONUS": 4.8849030549,
    # Carry schedule
    "CORE_TARGET_EARLY": 50.0,
    "CORE_TARGET_MID": 48.0,
    "CORE_TARGET_LATE": 42.0,
    "STRONG_TARGET_BONUS": 14.0,
    "STEADY_TARGET_BONUS": 6.0,
    "NOISY_TARGET_CAP": 5.0,
    "ZSCORE_BUY_BONUS": 10.0,
    "ZSCORE_SELL_PENALTY": 6.0,
    "MAX_LONG_TARGET": 76.0,
    "MAX_SHORT_TARGET": 20,
    "OVERLAY_BAND": 15.0,
    "LATE_UNWIND_START": 0.92,
    "LATE_UNWIND_Z": 1.35,
    # Small HMM-style state filter on drift-adjusted shock
    "STATE_STEADY_MEAN_BONUS": 0.00,
    "STATE_STRONG_MEAN_BONUS": 0.90,
    "STATE_NOISY_MEAN_SCALE": 0.20,
    "STATE_STEADY_SIGMA": 2.3,
    "STATE_STRONG_SIGMA": 3.2,
    "STATE_NOISY_SIGMA": 6.4,
    "P_STEADY_INIT": 0.65,
    "P_STRONG_INIT": 0.23,
    "P_NOISY_INIT": 0.12,
    # Execution
    "INVENTORY_SKEW": 0.078,
    "AGGRESSIVE_BUY_EDGE": 1.9,
    "PASSIVE_BUY_EDGE": 4.1,
    "OVERLAY_SELL_EDGE": 4.4,
    "BASE_QUOTE_EDGE": 5.0,
    "SOFT_LIMIT": 52,
    "PASSIVE_FRONT_SIZE": 9,
    "PASSIVE_BACK_SIZE": 6,
    "PASSIVE_BUY_BUFFER": 16,
    "PASSIVE_SELL_BUFFER": 6,
    "OVEREXTENSION_Z": 1.05,
    "BULLISH_IMBALANCE": 0.05,
    "RELOAD_PAUSE_ALPHA": 0.18,
    "RELOAD_COOLDOWN": 2.0,
    # Shock-to-trend controls
    "NEG_SHOCK_AGGR": -2.2,
    "NEG_SHOCK_PASSIVE": -0.5,
    "POS_SHOCK_STOP": 1.2,
    "SHOCK_BUY_ALPHA": 0.18,
    "AGGRESSIVE_BUY_SIZE": 16,
    "EXTREME_RICH_Z": 1.45,
    "EXTREME_RICH_NOISY": 0.58,
    "EXTREME_RICH_SHOCK": 0.60,
}


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def ema(prev: Optional[float], current: float, alpha: float) -> float:
    if prev is None:
        return current
    return (1.0 - alpha) * prev + alpha * current


class Book:
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

        fair = float(self.p["REFERENCE_PRICE"]) \
             + float(self.p["IMBALANCE_WEIGHT"]) * book.imbalance \
             + float(self.p["MICRO_WEIGHT"]) * (book.micro - book.mid)
        reservation = fair - mgr.projected() * float(self.p["INVENTORY_SKEW"])

        adverse = float(self.p["ADVERSE_IMBALANCE"])
        strong = float(self.p["STRONG_IMBALANCE"])
        bid_toxic = book.imbalance < -adverse and book.micro < book.mid
        ask_toxic = book.imbalance > adverse and book.micro > book.mid
        buy_edge_needed = 1.8 if bid_toxic else 1.3
        sell_edge_needed = 1.8 if ask_toxic else 1.3

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
            if pos >= float(self.p["SOFT_LIMIT"]):
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
            if pos <= -float(self.p["SOFT_LIMIT"]):
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
        buy_qe = max(4.8, buy_qe)
        sell_qe = max(4.8, sell_qe)

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


class IntarianPepperRootTrader:
    """
    Pepper is treated as a carry product.
    This branch changes carry capture itself by making buy aggression depend on
    negative shocks relative to the known drift, while positive shocks mostly stop
    chasing and overlay sells become rare/high-quality events.
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
            "p_steady": float(raw.get("p_steady", self.p["P_STEADY_INIT"])),
            "p_strong": float(raw.get("p_strong", self.p["P_STRONG_INIT"])),
            "p_noisy": float(raw.get("p_noisy", self.p["P_NOISY_INIT"])),
            "prev_mid": float(raw.get("prev_mid", 0.0)),
            "shock_ema": float(raw.get("shock_ema", 0.0)),
            "reload_ema": float(raw.get("reload_ema", 0.0)),
            "last_ts": float(raw.get("last_ts", -1.0)),
        }

    def _core_target(self, progress: float) -> float:
        if progress < 0.35:
            return float(self.p["CORE_TARGET_EARLY"])
        if progress < float(self.p["LATE_UNWIND_START"]):
            return float(self.p["CORE_TARGET_MID"])
        return float(self.p["CORE_TARGET_LATE"])

    def _carry_bounds(self, progress: float, very_late_unwind: bool) -> Tuple[int, int, int]:
        core_target = int(round(self._core_target(progress)))
        overlay_top = core_target + int(self.p["OVERLAY_BAND"])
        sell_floor = core_target - 6 if very_late_unwind else core_target
        return core_target, overlay_top, sell_floor

    def _gaussian_likelihood(self, value: float, mean: float, sigma: float) -> float:
        sigma = max(1e-6, sigma)
        z = (value - mean) / sigma
        return math.exp(-0.5 * z * z) / sigma

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

        prev_mid = float(state["prev_mid"])
        last_ts = float(state["last_ts"])
        dt = max(100.0, float(timestamp) - last_ts) if last_ts >= 0.0 else 100.0
        observed_return = 0.0 if prev_mid <= 0.0 else (book.mid - prev_mid)
        base_return = drift * dt
        shock = observed_return - base_return
        shock_ema = ema(float(state["shock_ema"]), shock, float(self.p["SHOCK_BUY_ALPHA"]))
        slope = short_gap + drift * 1000.0

        transition = (
            (0.82, 0.13, 0.05),
            (0.20, 0.70, 0.10),
            (0.22, 0.08, 0.70),
        )
        current_probs = (
            float(state["p_steady"]),
            float(state["p_strong"]),
            float(state["p_noisy"]),
        )
        predicted = [
            current_probs[0] * transition[0][i]
            + current_probs[1] * transition[1][i]
            + current_probs[2] * transition[2][i]
            for i in range(3)
        ]

        # Filter on drift-adjusted shock rather than raw return.
        steady_mean = float(self.p["STATE_STEADY_MEAN_BONUS"]) + 0.02 * short_gap
        strong_mean = float(self.p["STATE_STRONG_MEAN_BONUS"]) + 0.06 * max(0.0, short_gap)
        noisy_mean = max(0.0, base_return * float(self.p["STATE_NOISY_MEAN_SCALE"]))

        steady_like = self._gaussian_likelihood(shock, steady_mean, float(self.p["STATE_STEADY_SIGMA"]))
        strong_like = self._gaussian_likelihood(shock, strong_mean, float(self.p["STATE_STRONG_SIGMA"]))
        noisy_like = self._gaussian_likelihood(shock, noisy_mean, float(self.p["STATE_NOISY_SIGMA"]))

        if zscore > 0.70:
            noisy_like *= 1.0 + min(1.6, zscore - 0.70)
            strong_like *= 0.90
        elif zscore < -0.30:
            steady_like *= 1.08
            strong_like *= 1.06
        if shock < float(self.p["NEG_SHOCK_AGGR"]):
            steady_like *= 1.10
            strong_like *= 1.08
        if shock > float(self.p["POS_SHOCK_STOP"]):
            noisy_like *= 1.18

        post = [
            predicted[0] * steady_like,
            predicted[1] * strong_like,
            predicted[2] * noisy_like,
        ]
        total_post = sum(post)
        if total_post <= 1e-12:
            p_steady, p_strong, p_noisy = current_probs
        else:
            p_steady = post[0] / total_post
            p_strong = post[1] / total_post
            p_noisy = post[2] / total_post

        half_spread = max(1.0, book.spread_val / 2.0)
        lookahead = float(self.p["LOOKAHEAD_BONUS"]) * (1.0 - 0.65 * progress) * (0.72 + 0.45 * p_strong)
        fair = trend_line + 0.22 * residual_ema + 0.02 * (book.micro - book.mid) + 0.03 * book.imbalance * half_spread + lookahead

        return {
            "trend_line": trend_line,
            "residual": residual,
            "residual_ema": residual_ema,
            "spread_ema": spread_ema,
            "short_mid_ema": short_mid,
            "long_mid_ema": long_mid,
            "short_gap_ema": short_gap,
            "reload_ema": float(state["reload_ema"]),
            "observed_return": observed_return,
            "base_return": base_return,
            "shock": shock,
            "shock_ema": shock_ema,
            "slope": slope,
            "acceleration": acceleration,
            "zscore": zscore,
            "p_steady": p_steady,
            "p_strong": p_strong,
            "p_noisy": p_noisy,
            "fair": fair,
        }

    def _target_inventory(self, progress: float, book: Book, features: dict) -> Tuple[int, bool]:
        core_target = self._core_target(progress)
        p_steady = float(features["p_steady"])
        p_strong = float(features["p_strong"])
        p_noisy = float(features["p_noisy"])
        shock = float(features["shock"])

        target = core_target
        target += float(self.p["STEADY_TARGET_BONUS"]) * p_steady
        target += float(self.p["STRONG_TARGET_BONUS"]) * p_strong

        if features["zscore"] < -0.35:
            target += float(self.p["ZSCORE_BUY_BONUS"]) * min(1.0, abs(float(features["zscore"])) / 1.8)
        elif features["zscore"] > 0.85:
            target -= float(self.p["ZSCORE_SELL_PENALTY"]) * min(1.0, (float(features["zscore"]) - 0.55) / 1.3)

        bullish = (
            float(features["zscore"]) < float(self.p["OVEREXTENSION_Z"])
            and book.imbalance >= float(self.p["BULLISH_IMBALANCE"])
            and book.micro >= book.mid
        )
        if bullish and p_noisy < 0.45:
            target += 4.0
        # Buy more after negative drift-adjusted shock; do not enlarge target on positive shock.
        if shock <= float(self.p["NEG_SHOCK_PASSIVE"]) and p_steady + p_strong >= 0.60:
            target += 3.0
        if shock > float(self.p["POS_SHOCK_STOP"]):
            target = min(target, core_target + 3.0)
        if p_noisy > 0.45:
            target = min(target, core_target + float(self.p["NOISY_TARGET_CAP"]))
        if progress < 0.18:
            target = max(target, core_target)
        if p_noisy >= 0.55 and progress < float(self.p["LATE_UNWIND_START"]):
            target = max(target, core_target)

        target = max(target, core_target)
        target_int = int(clamp(target, -int(self.p["MAX_SHORT_TARGET"]), int(self.p["MAX_LONG_TARGET"])))
        return target_int, bullish

    def _execution_mode(
        self,
        position: int,
        target: int,
        core_target: int,
        overlay_top: int,
        book: Book,
        features: dict,
        bullish: bool,
    ) -> str:
        trend_prob = float(features["p_steady"]) + float(features["p_strong"])
        shock = float(features["shock"])
        zscore = float(features["zscore"])
        p_noisy = float(features["p_noisy"])

        # Rare, high-quality overlay sell only.
        if position > overlay_top and zscore >= float(self.p["EXTREME_RICH_Z"]) and p_noisy >= float(self.p["EXTREME_RICH_NOISY"]) and shock >= float(self.p["EXTREME_RICH_SHOCK"]):
            return "overlay_sell"

        # Positive shock => do not chase. Let passive bids rest or just hold.
        if shock > float(self.p["POS_SHOCK_STOP"]):
            return "hold"

        if position < target - 10:
            cheap = book.best_ask <= features["fair"] - float(self.p["AGGRESSIVE_BUY_EDGE"])
            if cheap and shock <= float(self.p["NEG_SHOCK_AGGR"]) and trend_prob >= 0.60 and p_noisy <= 0.36 and float(features["reload_ema"]) < float(self.p["RELOAD_COOLDOWN"]):
                return "aggressive_buy"
            if shock <= float(self.p["NEG_SHOCK_PASSIVE"]) and trend_prob >= 0.48:
                return "passive_buy"
        if bullish and position < max(core_target + 2, target - 4) and shock <= 0.35 and trend_prob >= 0.52:
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

        very_late_unwind = (
            progress >= float(self.p["LATE_UNWIND_START"])
            and float(features["p_noisy"]) >= 0.58
            and float(features["zscore"]) >= float(self.p["LATE_UNWIND_Z"])
        )
        core_target, overlay_top, sell_floor = self._carry_bounds(progress, very_late_unwind)
        action = self._execution_mode(mgr.projected(), target_int, core_target, overlay_top, book, features, bullish)

        if action == "aggressive_buy":
            shock_bonus = min(6, max(0, int(round(-(float(features["shock"]) - float(self.p["NEG_SHOCK_AGGR"]))))))
            qty = min(
                book.best_ask_vol,
                int(self.p["AGGRESSIVE_BUY_SIZE"]) + shock_bonus,
                max(0, target_int + 14 - mgr.projected()),
            )
            mgr.buy(book.best_ask, qty)
            ps["reload_ema"] = ema(float(ps["reload_ema"]), 8.0, float(self.p["RELOAD_PAUSE_ALPHA"]))
        else:
            ps["reload_ema"] = ema(float(ps["reload_ema"]), 0.0, float(self.p["RELOAD_PAUSE_ALPHA"]))

        if action == "overlay_sell":
            sell_edge = float(book.best_bid) - reservation
            if sell_edge >= float(self.p["OVERLAY_SELL_EDGE"]) and mgr.sell_cap > 0:
                qty = min(book.best_bid_vol, 4, max(0, mgr.projected() - overlay_top))
                mgr.sell(book.best_bid, qty)

        base_qe = float(self.p["BASE_QUOTE_EDGE"])
        buy_qe = float(self.p["PASSIVE_BUY_EDGE"])
        sell_qe = base_qe + 1.05

        if action == "hold":
            buy_qe = base_qe - (0.10 if bullish else 0.0)
        if float(features["p_strong"]) > 0.45:
            buy_qe -= 0.35
            sell_qe += 1.10
        elif float(features["p_steady"]) > 0.55:
            buy_qe -= 0.15
            sell_qe += 0.45
        if float(features["p_noisy"]) > 0.45:
            buy_qe += 0.45
            sell_qe -= 0.20
        if float(features["shock"]) <= float(self.p["NEG_SHOCK_PASSIVE"]):
            buy_qe -= 0.35
        elif float(features["shock"]) > float(self.p["POS_SHOCK_STOP"]):
            buy_qe += 0.85
        if float(features["zscore"]) > 1.05:
            sell_qe -= 0.20
        if mgr.projected() < target_int:
            buy_qe -= 0.20
        if bullish:
            sell_qe += 0.80

        front_buy = math.floor(reservation - buy_qe)
        front_sell = math.ceil(reservation + sell_qe)
        front_buy = min(front_buy, book.best_ask - 1)
        front_sell = max(front_sell, book.best_bid + 1)
        back_buy = min(front_buy - 2, book.best_ask - 1)

        front_sz = int(self.p["PASSIVE_FRONT_SIZE"])
        back_sz = int(self.p["PASSIVE_BACK_SIZE"])
        buy_buf = int(self.p["PASSIVE_BUY_BUFFER"])

        # Only rest passive buy orders when the shock is not strongly positive.
        allow_front_buy = action == "passive_buy" or (
            action == "hold"
            and float(features["shock"]) <= 0.20
            and float(features["p_steady"]) + float(features["p_strong"]) >= 0.58
            and mgr.projected() < core_target + 8
        )
        if allow_front_buy and front_buy > 0 and front_buy < book.best_ask:
            qty = min(front_sz, mgr.buy_cap, max(0, target_int + buy_buf - mgr.projected()))
            mgr.buy(front_buy, qty)
            deep_shock = float(features["shock"]) <= float(self.p["NEG_SHOCK_PASSIVE"])
            if deep_shock and back_buy > 0 and back_buy < book.best_ask:
                qty = min(back_sz, mgr.buy_cap, max(0, target_int + buy_buf - mgr.projected()))
                mgr.buy(back_buy, qty)

        allow_overlay_sell = action == "overlay_sell" or (very_late_unwind and mgr.projected() > sell_floor)
        if allow_overlay_sell and front_sell > book.best_bid:
            sell_front = max(2, front_sz - 5 if bullish else front_sz - 3)
            qty = min(sell_front, mgr.sell_cap, max(0, mgr.projected() - sell_floor))
            mgr.sell(front_sell, qty)

        memory["IPR_STATE"] = {
            "anchor": anchor,
            "residual_ema": float(features["residual_ema"]),
            "spread_ema": float(features["spread_ema"]),
            "short_mid_ema": float(features["short_mid_ema"]),
            "long_mid_ema": float(features["long_mid_ema"]),
            "short_gap_ema": float(features["short_gap_ema"]),
            "p_steady": float(features["p_steady"]),
            "p_strong": float(features["p_strong"]),
            "p_noisy": float(features["p_noisy"]),
            "prev_mid": float(book.mid),
            "shock_ema": float(features["shock_ema"]),
            "reload_ema": float(ps["reload_ema"]),
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
            result["ASH_COATED_OSMIUM"] = self.ash.build_orders(state)

        if "INTARIAN_PEPPER_ROOT" in state.order_depths:
            ipr_orders, memory = self.ipr.build_orders(state, memory)
            result["INTARIAN_PEPPER_ROOT"] = ipr_orders

        trader_data = json.dumps(memory, separators=(",", ":"))
        return result, 0, trader_data
