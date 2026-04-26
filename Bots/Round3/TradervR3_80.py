from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Tuple

try:
    from datamodel import Order, OrderDepth, Trade, TradingState
except ModuleNotFoundError:
    from Bots.datamodel import Order, OrderDepth, Trade, TradingState


HYDROGEL = "HYDROGEL_PACK"
VELVET = "VELVETFRUIT_EXTRACT"

LIMITS: Dict[str, int] = {
    HYDROGEL: 200,
    VELVET: 200,
}

UNDERLYING_CFG = {
    HYDROGEL: {
        "anchor": 10000.0,
        "anchor_w": 0.54,
        "stable_w": 0.29,
        "micro_w": 0.17,
        "imbalance_w": 1.05,
        "take_edge": 2.2,
        "quote_edge": 3.0,
        "clear_edge": 1.0,
        "soft_limit": 100,
        "take_max": 22,
        "clear_max": 36,
        "quote_size": 24,
        "inv_skew": 8.0,
    },
    VELVET: {
        "anchor": 5250.0,
        "anchor_w": 0.42,
        "stable_w": 0.30,
        "micro_w": 0.18,
        "ema_w": 0.10,
        "open_w": 0.00,
        "imbalance_w": 0.78,
        "take_edge": 1.2,
        "quote_edge": 1.6,
        "clear_edge": 0.7,
        "soft_limit": 82,
        "take_max": 28,
        "clear_max": 46,
        "quote_size": 24,
        "inv_skew": 5.8,
    },
}


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def load_memory(trader_data: str) -> dict:
    if not trader_data:
        return {}
    try:
        obj = json.loads(trader_data)
        return obj if isinstance(obj, dict) else {}
    except (json.JSONDecodeError, TypeError, ValueError):
        return {}


def dump_memory(memory: dict) -> str:
    return json.dumps(memory, separators=(",", ":"))


class OrderManager:
    def __init__(self, product: str, position: int, limit: int) -> None:
        self.product = product
        self.position = int(position)
        self.limit = int(limit)
        self.buy_cap = max(0, limit - position)
        self.sell_cap = max(0, limit + position)
        self.orders: List[Order] = []

    def projected(self) -> int:
        return self.position + sum(order.quantity for order in self.orders)

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

    def flush(self) -> List[Order]:
        return self.orders


def best_bid(od: OrderDepth) -> Optional[int]:
    return max(od.buy_orders) if od.buy_orders else None


def best_ask(od: OrderDepth) -> Optional[int]:
    return min(od.sell_orders) if od.sell_orders else None


def raw_mid(od: OrderDepth) -> Optional[float]:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None or ba is None or bb >= ba:
        return None
    return 0.5 * (bb + ba)


def top_bid_levels(od: OrderDepth, levels: int = 3) -> List[Tuple[int, int]]:
    return sorted(od.buy_orders.items(), reverse=True)[:levels]


def top_ask_levels(od: OrderDepth, levels: int = 3) -> List[Tuple[int, int]]:
    return sorted(od.sell_orders.items())[:levels]


def size_wall_prices(od: OrderDepth, levels: int = 3) -> Tuple[Optional[int], Optional[int]]:
    if not od.buy_orders or not od.sell_orders:
        return None, None
    bid_levels = top_bid_levels(od, levels)
    ask_levels = top_ask_levels(od, levels)
    bid_px = max(bid_levels, key=lambda x: (x[1], x[0]))[0]
    ask_px = min(ask_levels, key=lambda x: (x[1], x[0]))[0]
    return bid_px, ask_px


def wall_mid(od: OrderDepth) -> Optional[float]:
    bid_wall, ask_wall = size_wall_prices(od, levels=3)
    if bid_wall is None or ask_wall is None or bid_wall >= ask_wall:
        return raw_mid(od)
    return 0.5 * (bid_wall + ask_wall)


def thick_mid(od: OrderDepth, levels: int = 3) -> Optional[float]:
    if not od.buy_orders or not od.sell_orders:
        return raw_mid(od)
    bid_levels = top_bid_levels(od, levels)
    ask_levels = top_ask_levels(od, levels)
    bid_vol = sum(volume for _, volume in bid_levels)
    ask_vol = sum(abs(volume) for _, volume in ask_levels)
    if bid_vol <= 0 or ask_vol <= 0:
        return raw_mid(od)
    bid_px = sum(price * volume for price, volume in bid_levels) / bid_vol
    ask_px = sum(price * abs(volume) for price, volume in ask_levels) / ask_vol
    if bid_px >= ask_px:
        return raw_mid(od)
    return 0.5 * (bid_px + ask_px)


def micro_price(od: OrderDepth) -> Optional[float]:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None or ba is None or bb >= ba:
        return raw_mid(od)
    bid_vol = od.buy_orders[bb]
    ask_vol = abs(od.sell_orders[ba])
    total = bid_vol + ask_vol
    if total <= 0:
        return raw_mid(od)
    return (ba * bid_vol + bb * ask_vol) / total


def book_imbalance(od: OrderDepth, levels: int = 2) -> float:
    if not od.buy_orders or not od.sell_orders:
        return 0.0
    bid_levels = top_bid_levels(od, levels)
    ask_levels = top_ask_levels(od, levels)
    bid_vol = sum(volume for _, volume in bid_levels)
    ask_vol = sum(abs(volume) for _, volume in ask_levels)
    total = bid_vol + ask_vol
    if total <= 0:
        return 0.0
    return (bid_vol - ask_vol) / total


def stable_mid(od: OrderDepth) -> Optional[float]:
    mids = [value for value in (wall_mid(od), thick_mid(od), raw_mid(od)) if value is not None]
    return sum(mids) / len(mids) if mids else None


def round_down(x: float) -> int:
    return math.floor(x)


def round_up(x: float) -> int:
    return math.ceil(x)


def trade_mid(trade: Trade) -> float:
    return float(trade.price)


class Trader:
    def _reset_day_if_needed(self, memory: dict, timestamp: int) -> None:
        last_ts = memory.get("last_timestamp")
        if last_ts is not None and timestamp < last_ts:
            memory.clear()
        memory["last_timestamp"] = timestamp
        memory.setdefault(
            "velvet_overlay",
            {
                "day_low": 10**18,
                "day_high": -(10**18),
                "signal": 0.0,
                "age": 999,
            },
        )
        memory.setdefault(
            "hydro_state",
            {
                "extreme_side": 0,
                "extreme_hold_bars": 0,
                "ema_fast": None,
                "ema_slow": None,
                "ret_ema": 0.0,
                "last_mid": None,
                "long_peak_score": 0.0,
                "short_peak_score": 0.0,
                "long_peak_mid": None,
                "short_peak_mid": None,
                "long_peak_trend": 0.0,
                "short_peak_trend": 0.0,
                "exit_mode": "",
                "exit_age": 0,
            },
        )
        memory.setdefault(
            "velvet_state",
            {
                "ema_fast": None,
                "ema_slow": None,
                "ema_mid": None,
                "ema_micro": None,
                "ema_fair": None,
                "ret_ema": 0.0,
                "vol_ema": 0.0,
                "last_mid": None,
                "open_mid": None,
                "long_peak_mid": None,
                "short_peak_mid": None,
                "long_peak_score": 0.0,
                "short_peak_score": 0.0,
                "mode": "NEUTRAL",
                "exit_mode": "",
                "exit_age": 0,
            },
        )

    def _update_velvet_overlay(self, state: TradingState, memory: dict) -> float:
        overlay = memory["velvet_overlay"]
        trades = sorted(state.market_trades.get(VELVET, []), key=lambda t: t.timestamp)
        saw_event = False
        for trade in trades:
            qty = abs(int(trade.quantity))
            price = trade_mid(trade)
            is_new_low = price < float(overlay["day_low"])
            is_new_high = price > float(overlay["day_high"])
            if is_new_low:
                overlay["day_low"] = price
            if is_new_high:
                overlay["day_high"] = price
            if 10 <= qty <= 11 and is_new_low:
                overlay["signal"] = min(1.5, float(overlay["signal"]) + 1.0)
                overlay["age"] = 0
                saw_event = True
        if not saw_event:
            overlay["age"] = int(overlay.get("age", 999)) + 1
            overlay["signal"] = float(overlay.get("signal", 0.0)) * 0.96
        return 0.75 * max(0.0, min(1.0, float(overlay["signal"])))

    def _underlying_fair(self, product: str, od: OrderDepth, overlay_bias: float = 0.0) -> float:
        cfg = UNDERLYING_CFG[product]
        anchor = cfg["anchor"]
        stable = stable_mid(od)
        micro = micro_price(od)
        bb = best_bid(od)
        ba = best_ask(od)
        spread = (ba - bb) if bb is not None and ba is not None else 2.0
        stable_component = stable if stable is not None else anchor
        micro_component = micro if micro is not None else stable_component
        fair = cfg["anchor_w"] * anchor + cfg["stable_w"] * stable_component + cfg["micro_w"] * micro_component
        fair += cfg["imbalance_w"] * book_imbalance(od, levels=2) * max(1.0, 0.5 * spread)
        fair += overlay_bias
        return fair

    def _build_hydrogel_targets(self, state: TradingState, fair: float, memory: dict) -> dict:
        od = state.order_depths[HYDROGEL]
        bb = best_bid(od)
        ba = best_ask(od)
        mid = raw_mid(od)
        if mid is None:
            mid = stable_mid(od)
        if mid is None:
            mid = fair
        stable = stable_mid(od)
        if stable is None:
            stable = mid
        micro = micro_price(od)
        if micro is None:
            micro = mid
        spread = float((ba - bb) if bb is not None and ba is not None else 8.0)
        top_depth = 0.0
        if bb is not None:
            top_depth += float(max(0, od.buy_orders.get(bb, 0)))
        if ba is not None:
            top_depth += float(abs(od.sell_orders.get(ba, 0)))
        hydro_state = memory["hydro_state"]
        prev_fast = hydro_state.get("ema_fast")
        prev_slow = hydro_state.get("ema_slow")
        prev_last_mid = hydro_state.get("last_mid")
        prev_ret_ema = float(hydro_state.get("ret_ema", 0.0))
        ema_fast = float(mid) if prev_fast is None else 0.16 * float(mid) + 0.84 * float(prev_fast)
        ema_slow = float(mid) if prev_slow is None else 0.035 * float(mid) + 0.965 * float(prev_slow)
        ret = 0.0 if prev_last_mid is None else float(mid) - float(prev_last_mid)
        ret_ema = 0.12 * ret + 0.88 * prev_ret_ema
        hydro_state["ema_fast"] = ema_fast
        hydro_state["ema_slow"] = ema_slow
        hydro_state["ret_ema"] = ret_ema
        hydro_state["last_mid"] = float(mid)
        signal = (fair - float(mid)) / max(1.0, 0.5 * spread)
        good_book = (
            bb is not None
            and ba is not None
            and bb < ba
            and spread <= 18.0
            and top_depth >= 20.0
            and abs(float(stable) - float(mid)) <= 1.1
        )
        anchor_gap = float(mid) - UNDERLYING_CFG[HYDROGEL]["anchor"]
        trend_gap = ema_fast - ema_slow
        micro_gap = float(micro) - float(mid)
        imbalance = book_imbalance(od, levels=2)
        anchor_score = clamp(anchor_gap / 35.0, -3.0, 3.0)
        trend_score = clamp(trend_gap / 7.5, -3.0, 3.0)
        micro_score = clamp(micro_gap / max(1.0, 0.5 * spread), -1.5, 1.5)
        flow_score = clamp(micro_score + 0.75 * imbalance + 0.35 * clamp(ret_ema / 3.0, -2.0, 2.0), -2.0, 2.0)
        regime_score = 0.60 * trend_score + 0.30 * anchor_score + 0.10 * flow_score
        strength = abs(regime_score)
        if not good_book:
            confidence = "guarded"
            target_cap = 60
        elif strength < 0.75:
            confidence = "neutral"
            target_cap = 0
        elif strength < 1.30:
            confidence = "weak"
            target_cap = 80
        elif strength < 2.00:
            confidence = "medium"
            target_cap = 140
        else:
            confidence = "strong"
            target_cap = 200
        progress = clamp(state.timestamp / 3_000_000.0, 0.0, 1.0)
        current_pos = int(state.position.get(HYDROGEL, 0))
        entry_cap = target_cap
        if progress > 0.78:
            entry_cap = int(round(entry_cap * 0.88))
        if progress > 0.90:
            entry_cap = int(round(entry_cap * 0.65))
        if progress > 0.97:
            entry_cap = min(entry_cap, 50)
        hold_cap = entry_cap
        hold_zone = 110
        if abs(current_pos) > 120 and abs(trend_score) < 1.8:
            hold_cap = min(hold_cap, 100)
        if abs(current_pos) > 120 and abs(trend_score) < 1.2:
            hold_cap = min(hold_cap, 60)
        if abs(current_pos) > 160 and abs(trend_score) < 1.6:
            hold_cap = min(hold_cap, 80)
        if abs(current_pos) > 160 and abs(regime_score) < 1.2:
            hold_cap = min(hold_cap, 50)
        if abs(current_pos) > 140 and abs(trend_score) < 1.9:
            hold_cap = min(hold_cap, 90)
        if abs(current_pos) > 140 and abs(regime_score) < 1.1:
            hold_cap = min(hold_cap, 45)
        if progress > 0.94:
            hold_cap = min(hold_cap, 70)
        if progress > 0.98:
            hold_cap = min(hold_cap, 40)
        entry_target = int(round(clamp(200.0 * math.tanh(0.95 * regime_score), -float(entry_cap), float(entry_cap))))
        hold_score = 0.88 * regime_score + 0.12 * trend_score
        hold_target = int(round(clamp(200.0 * math.tanh(0.88 * hold_score), -float(hold_cap), float(hold_cap))))
        target = entry_target if abs(current_pos) < hold_zone else hold_target
        if current_pos > 80:
            hydro_state["long_peak_score"] = max(float(hydro_state.get("long_peak_score", 0.0)), float(regime_score))
            prev_peak_mid = hydro_state.get("long_peak_mid")
            hydro_state["long_peak_mid"] = float(mid) if prev_peak_mid is None else max(float(prev_peak_mid), float(mid))
            hydro_state["long_peak_trend"] = max(float(hydro_state.get("long_peak_trend", 0.0)), float(trend_score))
            hydro_state["short_peak_score"] = 0.0
            hydro_state["short_peak_mid"] = None
            hydro_state["short_peak_trend"] = 0.0
        elif current_pos < -80:
            hydro_state["short_peak_score"] = min(float(hydro_state.get("short_peak_score", 0.0)), float(regime_score))
            prev_peak_mid = hydro_state.get("short_peak_mid")
            hydro_state["short_peak_mid"] = float(mid) if prev_peak_mid is None else min(float(prev_peak_mid), float(mid))
            hydro_state["short_peak_trend"] = min(float(hydro_state.get("short_peak_trend", 0.0)), float(trend_score))
            hydro_state["long_peak_score"] = 0.0
            hydro_state["long_peak_mid"] = None
            hydro_state["long_peak_trend"] = 0.0
        elif abs(current_pos) < 40:
            hydro_state["long_peak_score"] = 0.0
            hydro_state["short_peak_score"] = 0.0
            hydro_state["long_peak_mid"] = None
            hydro_state["short_peak_mid"] = None
            hydro_state["long_peak_trend"] = 0.0
            hydro_state["short_peak_trend"] = 0.0
            hydro_state["exit_mode"] = ""
            hydro_state["exit_age"] = 0
        side = 1 if current_pos > 120 else -1 if current_pos < -120 else 0
        if side == 0:
            hydro_state["extreme_side"] = 0
            hydro_state["extreme_hold_bars"] = 0
        elif side == int(hydro_state.get("extreme_side", 0)):
            hydro_state["extreme_hold_bars"] = int(hydro_state.get("extreme_hold_bars", 0)) + 1
        else:
            hydro_state["extreme_side"] = side
            hydro_state["extreme_hold_bars"] = 1
        extreme_hold_bars = int(hydro_state.get("extreme_hold_bars", 0))
        if extreme_hold_bars > 24 and abs(regime_score) < 1.4:
            target = int(round(target * 0.70))
        elif extreme_hold_bars > 12 and abs(regime_score) < 1.0:
            target = int(round(target * 0.85))
        flatten_before_flip = False
        if current_pos * target < 0 and abs(current_pos) > 60:
            target = 0
            flatten_before_flip = True
        long_peak_score = float(hydro_state.get("long_peak_score", 0.0))
        short_peak_score = float(hydro_state.get("short_peak_score", 0.0))
        long_peak_mid = hydro_state.get("long_peak_mid")
        short_peak_mid = hydro_state.get("short_peak_mid")
        long_peak_trend = float(hydro_state.get("long_peak_trend", 0.0))
        short_peak_trend = float(hydro_state.get("short_peak_trend", 0.0))
        long_drawdown = 0.0 if long_peak_mid is None else float(long_peak_mid) - float(mid)
        short_drawup = 0.0 if short_peak_mid is None else float(mid) - float(short_peak_mid)
        trend_fade_long = long_peak_trend > 0.0 and trend_score < 0.70 * long_peak_trend
        trend_fade_short = short_peak_trend < 0.0 and trend_score > 0.70 * short_peak_trend
        fair_gap = abs(fair - float(mid))
        signal_fade = fair_gap < max(4.0, 0.55 * spread)
        unwind_long = current_pos > 150 and (
            (long_peak_score >= 1.35 and long_drawdown >= 12.0 and regime_score < max(0.70, 0.65 * long_peak_score) and trend_score < 1.25)
            or (trend_fade_long and long_drawdown >= 8.0)
            or (ret_ema < 0.0 and long_drawdown >= 8.0)
            or (signal_fade and long_drawdown >= 10.0 and current_pos > 140)
            or (long_drawdown >= 18.0 and ret_ema < -0.12)
            or (progress > 0.90 and long_drawdown >= 10.0 and trend_score < 0.95)
        )
        unwind_long_hard = current_pos > 170 and (
            (trend_fade_long and long_drawdown >= 16.0 and ret_ema < -0.05)
            or (long_drawdown >= 28.0 and ret_ema < -0.18)
            or (progress > 0.94 and long_drawdown >= 12.0)
        )
        unwind_short = current_pos < -150 and (
            (short_peak_score <= -1.35 and short_drawup >= 12.0 and regime_score > min(-0.70, 0.65 * short_peak_score) and trend_score > -1.25)
            or (trend_fade_short and short_drawup >= 8.0)
            or (ret_ema > 0.0 and short_drawup >= 8.0)
            or (signal_fade and short_drawup >= 10.0 and current_pos < -140)
            or (short_drawup >= 18.0 and ret_ema > 0.12)
            or (progress > 0.90 and short_drawup >= 10.0 and trend_score > -0.95)
        )
        unwind_short_hard = current_pos < -170 and (
            (trend_fade_short and short_drawup >= 16.0 and ret_ema > 0.05)
            or (short_drawup >= 28.0 and ret_ema > 0.18)
            or (progress > 0.94 and short_drawup >= 12.0)
        )
        prev_exit_mode = str(hydro_state.get("exit_mode", ""))
        prev_exit_age = int(hydro_state.get("exit_age", 0))
        strong_long_reconfirm = (
            current_pos > 60 and long_peak_trend > 0.0 and trend_score > max(1.90, 0.94 * long_peak_trend)
            and regime_score > max(1.65, 0.85 * long_peak_score) and ret_ema > 0.10 and long_drawdown < 6.0
            and fair_gap > max(4.0, 0.55 * spread)
        )
        strong_short_reconfirm = (
            current_pos < -60 and short_peak_trend < 0.0 and trend_score < min(-1.90, 0.94 * short_peak_trend)
            and regime_score < min(-1.65, 0.85 * short_peak_score) and ret_ema < -0.10 and short_drawup < 6.0
            and fair_gap > max(4.0, 0.55 * spread)
        )
        exit_mode = ""
        if prev_exit_mode.startswith("long") and current_pos > 60:
            if strong_long_reconfirm:
                exit_mode = ""
            elif unwind_long_hard or prev_exit_mode == "long_hard" or (prev_exit_age >= 8 and long_drawdown >= 12.0):
                exit_mode = "long_hard"
            else:
                exit_mode = "long"
        elif prev_exit_mode.startswith("short") and current_pos < -60:
            if strong_short_reconfirm:
                exit_mode = ""
            elif unwind_short_hard or prev_exit_mode == "short_hard" or (prev_exit_age >= 8 and short_drawup >= 12.0):
                exit_mode = "short_hard"
            else:
                exit_mode = "short"
        elif unwind_long_hard:
            exit_mode = "long_hard"
        elif unwind_long:
            exit_mode = "long"
        elif unwind_short_hard:
            exit_mode = "short_hard"
        elif unwind_short:
            exit_mode = "short"
        if exit_mode:
            hydro_state["exit_age"] = prev_exit_age + 1 if exit_mode == prev_exit_mode else 1
        else:
            hydro_state["exit_age"] = 0
        hydro_state["exit_mode"] = exit_mode
        exit_age = int(hydro_state.get("exit_age", 0))
        if exit_mode == "long":
            if exit_age <= 3:
                target = min(target, 120)
            elif exit_age <= 8:
                target = min(target, 80)
            elif exit_age <= 14:
                target = min(target, 40 if progress < 0.95 else 20)
            else:
                target = min(target, 0 if progress > 0.90 or long_drawdown >= 16.0 else 20)
        elif exit_mode == "long_hard":
            if exit_age <= 2:
                target = min(target, 80)
            elif exit_age <= 6:
                target = min(target, 40)
            else:
                target = min(target, 0 if progress > 0.88 or long_drawdown >= 14.0 else 20)
        elif exit_mode == "short":
            if exit_age <= 3:
                target = max(target, -120)
            elif exit_age <= 8:
                target = max(target, -80)
            elif exit_age <= 14:
                target = max(target, -40 if progress < 0.95 else -20)
            else:
                target = max(target, 0 if progress > 0.90 or short_drawup >= 16.0 else -20)
        elif exit_mode == "short_hard":
            if exit_age <= 2:
                target = max(target, -80)
            elif exit_age <= 6:
                target = max(target, -40)
            else:
                target = max(target, 0 if progress > 0.88 or short_drawup >= 14.0 else -20)
        stretch_long = current_pos > 150
        stretch_short = current_pos < -150
        absolute_danger_long = current_pos >= 150
        absolute_danger_short = current_pos <= -150
        exceptional_buy = regime_score >= 2.5 and progress < 0.88
        exceptional_sell = regime_score <= -2.5 and progress < 0.88
        quote_bias = 0.0 if abs(regime_score) < 0.75 else -0.06 * signal
        fair_shift = clamp(12.0 * regime_score, -48.0, 48.0)
        if exit_mode.startswith("long"):
            fair_shift -= 5.0
        elif exit_mode.startswith("short"):
            fair_shift += 5.0
        size_mult = 0.75 if confidence == "guarded" else 1.0
        if confidence == "neutral":
            size_mult *= 0.45
        if progress > 0.90 and abs(regime_score) < 1.6:
            size_mult *= 0.80
        if extreme_hold_bars > 20 and abs(regime_score) < 1.5:
            size_mult *= 0.85
        if exit_mode:
            size_mult *= 0.85
        if absolute_danger_long or absolute_danger_short:
            size_mult *= 0.75
        return {
            "mid": float(mid),
            "signal": float(signal),
            "regime_score": float(regime_score),
            "trend_score": float(trend_score),
            "anchor_score": float(anchor_score),
            "flow_score": float(flow_score),
            "confidence": confidence,
            "entry_cap": int(entry_cap),
            "hold_cap": int(hold_cap),
            "entry_target": int(entry_target),
            "hold_target": int(hold_target),
            "target": int(clamp(float(target), -200.0, 200.0)),
            "good_book": good_book,
            "progress": progress,
            "extreme_hold_bars": extreme_hold_bars,
            "flatten_before_flip": flatten_before_flip,
            "exit_mode": exit_mode,
            "exit_age": exit_age,
            "long_peak_score": long_peak_score,
            "short_peak_score": short_peak_score,
            "long_peak_trend": long_peak_trend,
            "short_peak_trend": short_peak_trend,
            "long_drawdown": long_drawdown,
            "short_drawup": short_drawup,
            "absolute_danger_long": absolute_danger_long,
            "absolute_danger_short": absolute_danger_short,
            "same_side_bid_block": exit_mode.startswith("long") or absolute_danger_long or (stretch_long and not exceptional_buy),
            "same_side_ask_block": exit_mode.startswith("short") or absolute_danger_short or (stretch_short and not exceptional_sell),
            "buy_take_extra": 3.0 if exit_mode.startswith("long") else 2.5 if absolute_danger_long else 2.0 if stretch_long and not exceptional_buy else 0.0,
            "sell_take_extra": 3.0 if exit_mode.startswith("short") else 2.5 if absolute_danger_short else 2.0 if stretch_short and not exceptional_sell else 0.0,
            "quote_bias": quote_bias,
            "fair_shift": fair_shift,
            "size_mult": size_mult,
        }

    def _build_velvet_context(self, state: TradingState, memory: dict, overlay_bias: float) -> dict:
        od = state.order_depths[VELVET]
        bb = best_bid(od)
        ba = best_ask(od)
        mid = raw_mid(od)
        if mid is None:
            mid = stable_mid(od)
        if mid is None:
            mid = memory.get("velvet_state", {}).get("last_mid")
        if mid is None:
            mid = UNDERLYING_CFG[VELVET]["anchor"]
        stable = stable_mid(od)
        if stable is None:
            stable = mid
        micro = micro_price(od)
        if micro is None:
            micro = mid
        spread = float((ba - bb) if bb is not None and ba is not None else 6.0)
        top_depth = 0.0
        if bb is not None:
            top_depth += float(max(0, od.buy_orders.get(bb, 0)))
        if ba is not None:
            top_depth += float(abs(od.sell_orders.get(ba, 0)))
        state_mem = memory["velvet_state"]
        if state_mem.get("open_mid") is None:
            state_mem["open_mid"] = float(mid)
        prev_mid = state_mem.get("last_mid")
        ret = 0.0 if prev_mid is None else float(mid) - float(prev_mid)
        state_mem["ret_ema"] = 0.16 * ret + 0.84 * float(state_mem.get("ret_ema", 0.0))
        state_mem["vol_ema"] = 0.18 * abs(ret) + 0.82 * float(state_mem.get("vol_ema", 0.0))
        state_mem["last_mid"] = float(mid)
        state_mem["ema_mid"] = float(mid) if state_mem.get("ema_mid") is None else 0.14 * float(mid) + 0.86 * float(state_mem["ema_mid"])
        state_mem["ema_micro"] = float(micro) if state_mem.get("ema_micro") is None else 0.18 * float(micro) + 0.82 * float(state_mem["ema_micro"])
        state_mem["ema_fast"] = float(mid) if state_mem.get("ema_fast") is None else 0.18 * float(mid) + 0.82 * float(state_mem["ema_fast"])
        state_mem["ema_slow"] = float(mid) if state_mem.get("ema_slow") is None else 0.05 * float(mid) + 0.95 * float(state_mem["ema_slow"])
        realized_vol = max(0.5, float(state_mem["vol_ema"]))
        trend_gap = float(state_mem["ema_fast"]) - float(state_mem["ema_slow"])
        move_unit = max(1.0, 0.45 * spread + 0.35 * realized_vol)
        trend_score = clamp(trend_gap / max(2.6, 1.8 + 0.55 * realized_vol), -3.0, 3.0)
        micro_gap = (float(micro) - float(mid)) / max(1.0, 0.5 * spread)
        imbalance = book_imbalance(od, levels=2)
        momentum_score = clamp(float(state_mem["ret_ema"]) / max(1.0, 0.7 + 0.30 * realized_vol), -3.0, 3.0)
        local_stretch = (float(mid) - float(state_mem["ema_mid"])) / move_unit
        fair = 0.55 * float(mid) + 0.30 * float(state_mem["ema_mid"]) + 0.15 * float(state_mem["ema_micro"])
        fair += 0.45 * imbalance * move_unit
        fair += 0.30 * momentum_score * move_unit
        fair += 0.22 * trend_score * move_unit
        fair += 0.15 * clamp(overlay_bias, 0.0, 1.5) * move_unit
        state_mem["ema_fair"] = float(fair) if state_mem.get("ema_fair") is None else 0.16 * float(fair) + 0.84 * float(state_mem["ema_fair"])
        signal = (float(fair) - float(mid)) / move_unit
        fair_ema_gap = (float(state_mem["ema_fair"]) - float(mid)) / move_unit
        flow_score = clamp(0.80 * micro_gap + 0.70 * imbalance + 0.35 * momentum_score, -3.0, 3.0)
        directional_signal = 0.38 * trend_score + 0.20 * momentum_score + 0.17 * imbalance + 0.25 * micro_gap
        conviction = 0.42 * signal + 0.20 * directional_signal + 0.18 * fair_ema_gap + 0.20 * flow_score
        good_book = bb is not None and ba is not None and bb < ba and spread <= 14.0 and top_depth >= 18.0 and abs(float(stable) - float(mid)) <= 1.4
        progress = clamp(state.timestamp / 100000.0, 0.0, 1.0)
        pos = int(state.position.get(VELVET, 0))
        if pos > 30:
            prev_peak_mid = state_mem.get("long_peak_mid")
            state_mem["long_peak_mid"] = float(mid) if prev_peak_mid is None else max(float(prev_peak_mid), float(mid))
            state_mem["long_peak_score"] = max(float(state_mem.get("long_peak_score", 0.0)), float(conviction))
            state_mem["short_peak_mid"] = None
            state_mem["short_peak_score"] = 0.0
        elif pos < -30:
            prev_peak_mid = state_mem.get("short_peak_mid")
            state_mem["short_peak_mid"] = float(mid) if prev_peak_mid is None else min(float(prev_peak_mid), float(mid))
            state_mem["short_peak_score"] = min(float(state_mem.get("short_peak_score", 0.0)), float(conviction))
            state_mem["long_peak_mid"] = None
            state_mem["long_peak_score"] = 0.0
        elif abs(pos) < 15:
            state_mem["long_peak_mid"] = None
            state_mem["short_peak_mid"] = None
            state_mem["long_peak_score"] = 0.0
            state_mem["short_peak_score"] = 0.0
            state_mem["exit_mode"] = ""
            state_mem["exit_age"] = 0
        mode = "NEUTRAL"
        burst_long = directional_signal > 1.10 and momentum_score > 0.28 and micro_gap > 0.08 and flow_score > 0.35
        burst_short = directional_signal < -1.10 and momentum_score < -0.28 and micro_gap < -0.08 and flow_score < -0.35
        fade_long = local_stretch <= -2.25 and micro_gap >= -0.05 and momentum_score > -0.45
        fade_short = local_stretch >= 2.25 and micro_gap <= 0.05 and momentum_score < 0.45
        if good_book:
            if fade_long:
                mode = "FADE_LONG"
            elif fade_short:
                mode = "FADE_SHORT"
            elif burst_long:
                mode = "BURST_LONG"
            elif burst_short:
                mode = "BURST_SHORT"
            else:
                mode = "MARKET_MAKE"
        entry_cap = 0
        vol_scale = clamp(1.15 - 0.12 * realized_vol, 0.50, 1.10)
        if mode == "MARKET_MAKE":
            entry_cap = int(round(36 * vol_scale))
        elif mode in ("FADE_LONG", "FADE_SHORT"):
            entry_cap = int(round((80 if abs(conviction) < 2.0 else 102) * vol_scale))
        elif mode in ("BURST_LONG", "BURST_SHORT"):
            entry_cap = int(round((88 if abs(conviction) < 2.0 else 118) * vol_scale))
        if not good_book:
            entry_cap = 20
        aligned_carry = (
            (pos > 12 and flow_score > 0.25 and momentum_score > 0.15 and micro_gap > 0.05)
            or (pos < -12 and flow_score < -0.25 and momentum_score < -0.15 and micro_gap < -0.05)
        )
        if progress > 0.80:
            entry_cap = int(round(entry_cap * (0.95 if aligned_carry else 0.85)))
        if progress > 0.92:
            entry_cap = int(round(entry_cap * (0.78 if aligned_carry else 0.60)))
        if progress > 0.97:
            entry_cap = min(entry_cap, 36 if aligned_carry else 25)
        target = 0
        if mode == "MARKET_MAKE":
            target = int(round(clamp(28.0 * math.tanh(0.90 * signal + 0.50 * micro_gap), -float(entry_cap), float(entry_cap))))
        elif mode == "FADE_LONG":
            target = int(round(clamp(92.0 * math.tanh(max(0.0, -0.64 * local_stretch + 0.35 * micro_gap)), 0.0, float(entry_cap))))
        elif mode == "FADE_SHORT":
            target = int(round(clamp(92.0 * math.tanh(max(0.0, 0.64 * local_stretch - 0.35 * micro_gap)), 0.0, float(entry_cap)))) * -1
        elif mode == "BURST_LONG":
            target = int(round(clamp(108.0 * math.tanh(max(0.0, 0.72 * conviction + 0.20 * flow_score)), 0.0, float(entry_cap))))
        elif mode == "BURST_SHORT":
            target = int(round(clamp(108.0 * math.tanh(max(0.0, -0.72 * conviction - 0.20 * flow_score)), 0.0, float(entry_cap)))) * -1
        long_drawdown = 0.0 if state_mem.get("long_peak_mid") is None else float(state_mem["long_peak_mid"]) - float(mid)
        short_drawup = 0.0 if state_mem.get("short_peak_mid") is None else float(mid) - float(state_mem["short_peak_mid"])
        exit_mode = ""
        long_carry = pos > 12 and flow_score > 0.25 and momentum_score > 0.15 and micro_gap > 0.05
        short_carry = pos < -12 and flow_score < -0.25 and momentum_score < -0.15 and micro_gap < -0.05
        if pos > 70 and ((directional_signal < (-0.05 if long_carry else 0.10) and signal < (0.10 if long_carry else 0.20)) or long_drawdown >= max(4.8 if long_carry else 4.0, (2.4 if long_carry else 2.1) * realized_vol) or (progress > 0.88 and long_drawdown >= (4.2 if long_carry else 3.5))):
            exit_mode = "long"
        elif pos < -70 and ((directional_signal > (0.05 if short_carry else -0.10) and signal > (-0.10 if short_carry else -0.20)) or short_drawup >= max(4.8 if short_carry else 4.0, (2.4 if short_carry else 2.1) * realized_vol) or (progress > 0.88 and short_drawup >= (4.2 if short_carry else 3.5))):
            exit_mode = "short"
        prev_exit_mode = str(state_mem.get("exit_mode", ""))
        if exit_mode:
            state_mem["exit_age"] = int(state_mem.get("exit_age", 0)) + 1 if prev_exit_mode == exit_mode else 1
        else:
            state_mem["exit_age"] = 0
        state_mem["exit_mode"] = exit_mode
        if exit_mode == "long":
            target = min(target, 30 if int(state_mem["exit_age"]) <= 4 else 0)
        elif exit_mode == "short":
            target = max(target, -30 if int(state_mem["exit_age"]) <= 4 else 0)
        if pos * target < 0 and abs(pos) > 35:
            target = 0
        inventory_pressure = pos / LIMITS[VELVET]
        quote_bias = 0.32 * signal * move_unit + 0.18 * directional_signal * move_unit + 0.10 * clamp(overlay_bias, 0.0, 1.0) * move_unit
        if long_carry:
            quote_bias += 0.10 * move_unit
        elif short_carry:
            quote_bias -= 0.10 * move_unit
        quote_bias -= 1.15 * inventory_pressure * move_unit
        take_bias = 0.15 * directional_signal * move_unit + 0.10 * flow_score * move_unit + 0.06 * signal * move_unit
        if long_carry:
            take_bias += 0.08 * move_unit
        elif short_carry:
            take_bias -= 0.08 * move_unit
        if exit_mode == "long":
            take_bias -= 0.22 * move_unit
        elif exit_mode == "short":
            take_bias += 0.22 * move_unit
        size_mult = 0.55 if not good_book else 1.0
        if mode in ("NEUTRAL", "MARKET_MAKE"):
            size_mult *= 0.50
        if realized_vol > 2.5:
            size_mult *= 0.85
        if realized_vol > 4.5:
            size_mult *= 0.72
        if progress > 0.90:
            size_mult *= 0.82
        if exit_mode:
            size_mult *= 0.85
        same_side_bid_block = exit_mode == "long" or (mode == "BURST_SHORT" and pos < -80)
        same_side_ask_block = exit_mode == "short" or (mode == "BURST_LONG" and pos > 80)
        return {
            "mid": float(mid),
            "fair": float(fair),
            "signal": float(signal),
            "momentum_score": float(momentum_score),
            "trend_score": float(trend_score),
            "flow_score": float(flow_score),
            "directional_signal": float(directional_signal),
            "conviction": float(conviction),
            "realized_vol": float(realized_vol),
            "local_stretch": float(local_stretch),
            "micro_gap": float(micro_gap),
            "move_unit": float(move_unit),
            "mode": mode,
            "target": int(clamp(float(target), -120.0, 120.0)),
            "progress": float(progress),
            "good_book": bool(good_book),
            "long_carry": bool(long_carry),
            "short_carry": bool(short_carry),
            "exit_mode": exit_mode,
            "exit_age": int(state_mem.get("exit_age", 0)),
            "long_drawdown": float(long_drawdown),
            "short_drawup": float(short_drawup),
            "quote_bias": float(quote_bias),
            "take_bias": float(take_bias),
            "size_mult": float(size_mult),
            "same_side_bid_block": bool(same_side_bid_block),
            "same_side_ask_block": bool(same_side_ask_block),
        }

    def _trade_hydrogel(self, state: TradingState, fair: float, hydro_ctx: dict) -> List[Order]:
        od = state.order_depths[HYDROGEL]
        cfg = UNDERLYING_CFG[HYDROGEL]
        mgr = OrderManager(HYDROGEL, state.position.get(HYDROGEL, 0), LIMITS[HYDROGEL])
        bb = best_bid(od)
        ba = best_ask(od)
        spread = (ba - bb) if bb is not None and ba is not None else 2.0
        fair = fair + float(hydro_ctx.get("fair_shift", 0.0))
        target = float(hydro_ctx["target"])
        current_pos = int(state.position.get(HYDROGEL, 0))
        unwind_long = str(hydro_ctx.get("exit_mode", "")).startswith("long")
        unwind_short = str(hydro_ctx.get("exit_mode", "")).startswith("short")
        same_side_bid_block = bool(hydro_ctx.get("same_side_bid_block", False))
        same_side_ask_block = bool(hydro_ctx.get("same_side_ask_block", False))
        absolute_danger_long = bool(hydro_ctx.get("absolute_danger_long", False))
        absolute_danger_short = bool(hydro_ctx.get("absolute_danger_short", False))
        buy_take_allowed = not (same_side_bid_block or unwind_long or absolute_danger_long or current_pos >= 140)
        sell_take_allowed = not (same_side_ask_block or unwind_short or absolute_danger_short or current_pos <= -140)
        buy_take_edge = cfg["take_edge"] + float(hydro_ctx["buy_take_extra"])
        sell_take_edge = cfg["take_edge"] + float(hydro_ctx["sell_take_extra"])
        for ask, volume in sorted(od.sell_orders.items()):
            edge = fair - ask
            if not buy_take_allowed:
                break
            if edge >= buy_take_edge:
                mgr.buy(ask, min(-volume, cfg["take_max"]))
            elif edge >= cfg["take_edge"] + 2.5:
                mgr.buy(ask, min(-volume, cfg["take_max"]))
            else:
                break
        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            edge = bid - fair
            if not sell_take_allowed:
                break
            if edge >= sell_take_edge:
                mgr.sell(bid, min(volume, cfg["take_max"]))
            elif edge >= cfg["take_edge"] + 2.5:
                mgr.sell(bid, min(volume, cfg["take_max"]))
            else:
                break
        pos = mgr.projected()
        relative_pos = pos - target
        soft_limit = 80
        hard_zone = 130
        clear_edge = cfg["clear_edge"]
        hard_clear_edge = clear_edge + 1.5
        soft_clear_max = cfg["clear_max"]
        hard_clear_max = max(cfg["clear_max"], 56)
        if unwind_long or unwind_short:
            soft_limit = 25
            hard_zone = 45
            clear_edge += 2.0
            hard_clear_edge += 3.0
            soft_clear_max = max(cfg["clear_max"], 72)
            hard_clear_max = max(cfg["clear_max"], 96)
        elif absolute_danger_long or absolute_danger_short:
            soft_limit = 30
            hard_zone = 55
            clear_edge += 1.6
            hard_clear_edge += 2.6
            soft_clear_max = max(cfg["clear_max"], 64)
            hard_clear_max = max(cfg["clear_max"], 84)
        if relative_pos > hard_zone and bb is not None and (bb >= fair - hard_clear_edge or unwind_long or absolute_danger_long):
            mgr.sell(bb, min(int(math.ceil(relative_pos - soft_limit)), hard_clear_max))
        elif relative_pos > soft_limit and bb is not None and (bb >= fair - clear_edge or unwind_long or absolute_danger_long):
            mgr.sell(bb, min(int(math.ceil(relative_pos - soft_limit)), soft_clear_max))
        pos = mgr.projected()
        relative_pos = pos - target
        if relative_pos < -hard_zone and ba is not None and (ba <= fair + hard_clear_edge or unwind_short or absolute_danger_short):
            mgr.buy(ba, min(int(math.ceil((-soft_limit) - relative_pos)), hard_clear_max))
        elif relative_pos < -soft_limit and ba is not None and (ba <= fair + clear_edge or unwind_short or absolute_danger_short):
            mgr.buy(ba, min(int(math.ceil((-soft_limit) - relative_pos)), soft_clear_max))
        pos = mgr.projected()
        relative_pos = pos - target
        inv_ratio = relative_pos / LIMITS[HYDROGEL]
        reservation = fair + float(hydro_ctx["quote_bias"]) - (cfg["inv_skew"] + 4.0) * inv_ratio
        quote_edge = cfg["quote_edge"] + max(0.0, 0.12 * (spread - 4.0))
        buy_px = round_down(reservation - quote_edge)
        sell_px = round_up(reservation + quote_edge)
        if bb is not None and ba is not None and bb < ba:
            if spread >= 3:
                buy_px = max(buy_px, bb + 1)
                sell_px = min(sell_px, ba - 1)
            else:
                buy_px = min(buy_px, bb)
                sell_px = max(sell_px, ba)
            buy_px = min(buy_px, ba - 1)
            sell_px = max(sell_px, bb + 1)
        size_scale = max(0.20, 1.0 - abs(inv_ratio)) * max(0.35, float(hydro_ctx["size_mult"]))
        if same_side_bid_block or same_side_ask_block:
            size_scale *= 0.85
        quote_size = max(6, int(round(cfg["quote_size"] * size_scale)))
        can_bid = mgr.buy_cap > 0
        can_ask = mgr.sell_cap > 0
        if same_side_bid_block or unwind_long or absolute_danger_long:
            can_bid = False
        if same_side_ask_block or unwind_short or absolute_danger_short:
            can_ask = False
        if can_bid and (ba is None or buy_px < ba):
            mgr.buy(buy_px, quote_size)
        if can_ask and (bb is None or sell_px > bb):
            mgr.sell(sell_px, quote_size)
        return mgr.flush()

    def _trade_velvet(self, state: TradingState, fair: float, velvet_ctx: dict) -> List[Order]:
        od = state.order_depths[VELVET]
        cfg = UNDERLYING_CFG[VELVET]
        mgr = OrderManager(VELVET, state.position.get(VELVET, 0), LIMITS[VELVET])
        bb = best_bid(od)
        ba = best_ask(od)
        spread = float((ba - bb) if bb is not None and ba is not None else 4.0)
        fair = float(fair)
        target = int(velvet_ctx["target"])
        pos = int(state.position.get(VELVET, 0))
        buy_take_allowed = not bool(velvet_ctx["same_side_bid_block"])
        sell_take_allowed = not bool(velvet_ctx["same_side_ask_block"])
        realized_vol = float(velvet_ctx.get("realized_vol", 1.0))
        mode = str(velvet_ctx.get("mode", "NEUTRAL"))
        buy_take_edge = cfg["take_edge"] + 0.10 * realized_vol
        sell_take_edge = cfg["take_edge"] + 0.10 * realized_vol
        if mode in ("BURST_LONG", "FADE_LONG"):
            buy_take_edge -= 0.18
        elif mode in ("BURST_SHORT", "FADE_SHORT"):
            sell_take_edge -= 0.18
        if mode == "MARKET_MAKE":
            buy_take_edge += 0.12
            sell_take_edge += 0.12
        for ask, volume in sorted(od.sell_orders.items()):
            edge = fair - ask + float(velvet_ctx["take_bias"])
            if not buy_take_allowed:
                break
            if edge >= buy_take_edge:
                mgr.buy(ask, min(-volume, cfg["take_max"]))
            else:
                break
        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            edge = bid - fair - float(velvet_ctx["take_bias"])
            if not sell_take_allowed:
                break
            if edge >= sell_take_edge:
                mgr.sell(bid, min(volume, cfg["take_max"]))
            else:
                break
        pos = mgr.projected()
        relative_pos = pos - target
        clear_edge = cfg["clear_edge"] + 0.08 * realized_vol
        soft_limit = int(round(cfg["soft_limit"] * clamp(1.08 - 0.09 * realized_vol, 0.45, 1.0)))
        clear_max = int(round(cfg["clear_max"] * clamp(1.00 + 0.05 * realized_vol, 1.0, 1.35)))
        if velvet_ctx["exit_mode"]:
            soft_limit = 24
            clear_edge += 0.7
            clear_max = max(clear_max, 56)
        elif velvet_ctx["progress"] > 0.88:
            soft_limit = 40
        if relative_pos > soft_limit and bb is not None and bb >= fair - clear_edge:
            mgr.sell(bb, min(int(math.ceil(relative_pos - soft_limit)), clear_max))
        elif relative_pos < -soft_limit and ba is not None and ba <= fair + clear_edge:
            mgr.buy(ba, min(int(math.ceil((-soft_limit) - relative_pos)), clear_max))
        pos = mgr.projected()
        relative_pos = pos - target
        inv_ratio = relative_pos / LIMITS[VELVET]
        reservation = fair + float(velvet_ctx["quote_bias"]) - cfg["inv_skew"] * (1.25 + 0.10 * realized_vol) * inv_ratio
        quote_edge = cfg["quote_edge"] + 0.16 * realized_vol + max(0.0, 0.10 * (spread - 3.0))
        if mode == "MARKET_MAKE":
            quote_edge *= 0.92
        elif mode in ("BURST_LONG", "BURST_SHORT"):
            quote_edge *= 1.05
        elif mode in ("FADE_LONG", "FADE_SHORT"):
            quote_edge *= 0.98
        buy_px = round_down(reservation - quote_edge)
        sell_px = round_up(reservation + quote_edge)
        if bb is not None and ba is not None and bb < ba:
            if spread >= 3:
                buy_px = max(buy_px, bb + 1)
                sell_px = min(sell_px, ba - 1)
            else:
                buy_px = min(buy_px, bb)
                sell_px = max(sell_px, ba)
            buy_px = min(buy_px, ba - 1)
            sell_px = max(sell_px, bb + 1)
        size_scale = max(0.25, 1.0 - abs(inv_ratio)) * max(0.35, float(velvet_ctx["size_mult"]))
        quote_size = max(4, int(round(cfg["quote_size"] * size_scale)))
        if mgr.buy_cap > 0 and not bool(velvet_ctx["same_side_bid_block"]) and (ba is None or buy_px < ba):
            mgr.buy(buy_px, quote_size)
        if mgr.sell_cap > 0 and not bool(velvet_ctx["same_side_ask_block"]) and (bb is None or sell_px > bb):
            mgr.sell(sell_px, quote_size)
        return mgr.flush()

    def run(self, state: TradingState):
        memory = load_memory(state.traderData)
        self._reset_day_if_needed(memory, state.timestamp)
        result: Dict[str, List[Order]] = {product: [] for product in state.order_depths}
        conversions = 0

        if HYDROGEL in state.order_depths:
            hydro_fair = self._underlying_fair(HYDROGEL, state.order_depths[HYDROGEL], 0.0)
            hydro_ctx = self._build_hydrogel_targets(state, hydro_fair, memory)
            result[HYDROGEL] = self._trade_hydrogel(state, hydro_fair, hydro_ctx)
            memory["hydro_book"] = {
                "mid": round(float(hydro_ctx["mid"]), 3),
                "signal": round(float(hydro_ctx["signal"]), 3),
                "regime_score": round(float(hydro_ctx["regime_score"]), 3),
                "trend_score": round(float(hydro_ctx["trend_score"]), 3),
                "flow_score": round(float(hydro_ctx["flow_score"]), 3),
                "target": int(hydro_ctx["target"]),
                "confidence": str(hydro_ctx["confidence"]),
                "exit_mode": str(hydro_ctx["exit_mode"]),
            }

        if VELVET in state.order_depths:
            overlay_bias = self._update_velvet_overlay(state, memory)
            velvet_ctx = self._build_velvet_context(state, memory, overlay_bias)
            result[VELVET] = self._trade_velvet(state, float(velvet_ctx["fair"]), velvet_ctx)
            memory["velvet_book"] = {
                "fair": round(float(velvet_ctx["fair"]), 3),
                "mid": round(float(velvet_ctx["mid"]), 3),
                "signal": round(float(velvet_ctx["signal"]), 3),
                "momentum_score": round(float(velvet_ctx["momentum_score"]), 3),
                "trend_score": round(float(velvet_ctx["trend_score"]), 3),
                "flow_score": round(float(velvet_ctx["flow_score"]), 3),
                "directional_signal": round(float(velvet_ctx["directional_signal"]), 3),
                "conviction": round(float(velvet_ctx["conviction"]), 3),
                "realized_vol": round(float(velvet_ctx["realized_vol"]), 3),
                "local_stretch": round(float(velvet_ctx["local_stretch"]), 3),
                "micro_gap": round(float(velvet_ctx["micro_gap"]), 3),
                "mode": str(velvet_ctx["mode"]),
                "target": int(velvet_ctx["target"]),
                "long_carry": bool(velvet_ctx["long_carry"]),
                "short_carry": bool(velvet_ctx["short_carry"]),
                "exit_mode": str(velvet_ctx["exit_mode"]),
                "overlay_bias": round(float(overlay_bias), 3),
                "good_book": bool(velvet_ctx["good_book"]),
            }

        return result, conversions, dump_memory(memory)
