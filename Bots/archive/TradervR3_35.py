from __future__ import annotations

import json
import math
from statistics import NormalDist
from typing import Dict, List, Optional, Sequence, Tuple

try:
    from datamodel import Order, OrderDepth, Trade, TradingState
except ModuleNotFoundError:
    from trader_factory.core.datamodel import Order, OrderDepth, Trade, TradingState


_N = NormalDist()

HYDROGEL = "HYDROGEL_PACK"
VELVET = "VELVETFRUIT_EXTRACT"
VOUCHER_STRIKES: Dict[str, int] = {
    "VEV_4000": 4000,
    "VEV_4500": 4500,
    "VEV_5000": 5000,
    "VEV_5100": 5100,
    "VEV_5200": 5200,
    "VEV_5300": 5300,
    "VEV_5400": 5400,
    "VEV_5500": 5500,
    "VEV_6000": 6000,
    "VEV_6500": 6500,
}

LIMITS: Dict[str, int] = {
    HYDROGEL: 200,
    VELVET: 200,
    **{product: 300 for product in VOUCHER_STRIKES},
}

# Round 3 starts with 5 days to expiry.
TTE_YEARS = 5.0 / 365.0

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
        "anchor_w": 0.46,
        "stable_w": 0.34,
        "micro_w": 0.20,
        "imbalance_w": 0.85,
        "take_edge": 1.2,
        "quote_edge": 1.5,
        "clear_edge": 0.6,
        "soft_limit": 120,
        "take_max": 34,
        "clear_max": 50,
        "quote_size": 36,
        "inv_skew": 5.0,
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
        self._orders: List[Order] = []

    def projected(self) -> int:
        return self.position + sum(order.quantity for order in self._orders)

    def buy(self, price: int, qty: int) -> None:
        size = min(max(0, int(qty)), self.buy_cap)
        if size > 0:
            self._orders.append(Order(self.product, int(price), size))
            self.buy_cap -= size

    def sell(self, price: int, qty: int) -> None:
        size = min(max(0, int(qty)), self.sell_cap)
        if size > 0:
            self._orders.append(Order(self.product, int(price), -size))
            self.sell_cap -= size

    def flush(self) -> List[Order]:
        orders = self._orders
        self._orders = []
        return orders


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


def norm_cdf(x: float) -> float:
    return _N.cdf(x)


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def black_scholes_call(spot: float, strike: float, tte_years: float, sigma: float) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    if tte_years <= 0.0 or sigma <= 0.0:
        return max(spot - strike, 0.0)
    sqrt_t = math.sqrt(tte_years)
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * tte_years) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t
    return spot * norm_cdf(d1) - strike * norm_cdf(d2)


def black_scholes_delta_call(spot: float, strike: float, tte_years: float, sigma: float) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    if tte_years <= 0.0 or sigma <= 0.0:
        return 1.0 if spot > strike else 0.0
    sqrt_t = math.sqrt(tte_years)
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * tte_years) / (sigma * sqrt_t)
    return norm_cdf(d1)


def black_scholes_vega_proxy(spot: float, strike: float, tte_years: float, sigma: float) -> float:
    if spot <= 0.0 or strike <= 0.0 or tte_years <= 0.0 or sigma <= 0.0:
        return 0.0
    sqrt_t = math.sqrt(tte_years)
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * tte_years) / (sigma * sqrt_t)
    return spot * norm_pdf(d1) * sqrt_t


def implied_vol_call(price: float, spot: float, strike: float, tte_years: float, iterations: int = 60) -> float:
    intrinsic = max(spot - strike, 0.0)
    if spot <= 0.0 or strike <= 0.0 or tte_years <= 0.0:
        return 1e-6
    if price <= intrinsic + 1e-6:
        return 1e-6

    lo, hi = 1e-6, 3.0
    for _ in range(iterations):
        mid = 0.5 * (lo + hi)
        fair = black_scholes_call(spot, strike, tte_years, mid)
        if fair < price:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def round_down(x: float) -> int:
    return math.floor(x)


def round_up(x: float) -> int:
    return math.ceil(x)


def trade_mid(trade: Trade) -> float:
    return float(trade.price)


def solve_3x3(a: List[List[float]], b: List[float]) -> Optional[List[float]]:
    mat = [row[:] + [rhs] for row, rhs in zip(a, b)]
    n = 3
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(mat[r][col]))
        if abs(mat[pivot][col]) < 1e-12:
            return None
        if pivot != col:
            mat[col], mat[pivot] = mat[pivot], mat[col]
        factor = mat[col][col]
        for j in range(col, n + 1):
            mat[col][j] /= factor
        for row in range(n):
            if row == col:
                continue
            factor = mat[row][col]
            for j in range(col, n + 1):
                mat[row][j] -= factor * mat[col][j]
    return [mat[i][n] for i in range(n)]


def fit_quadratic(xs: Sequence[float], ys: Sequence[float]) -> Tuple[float, float, float]:
    if len(xs) != len(ys) or len(xs) < 3:
        median = sorted(ys)[len(ys) // 2] if ys else 0.18
        return (0.0, 0.0, float(median))

    s0 = float(len(xs))
    s1 = sum(xs)
    s2 = sum(x * x for x in xs)
    s3 = sum(x * x * x for x in xs)
    s4 = sum(x * x * x * x for x in xs)
    t0 = sum(ys)
    t1 = sum(x * y for x, y in zip(xs, ys))
    t2 = sum((x * x) * y for x, y in zip(xs, ys))
    sol = solve_3x3(
        [
            [s4, s3, s2],
            [s3, s2, s1],
            [s2, s1, s0],
        ],
        [t2, t1, t0],
    )
    if sol is None:
        median = sorted(ys)[len(ys) // 2]
        return (0.0, 0.0, float(median))
    return (float(sol[0]), float(sol[1]), float(sol[2]))


def fit_quadratic_weighted(
    xs: Sequence[float], ys: Sequence[float], ws: Sequence[float]
) -> Tuple[float, float, float]:
    if len(xs) != len(ys) or len(xs) != len(ws) or len(xs) < 3:
        return fit_quadratic(xs, ys)

    safe_ws = [max(1e-6, float(w)) for w in ws]
    s0 = sum(safe_ws)
    s1 = sum(w * x for x, w in zip(xs, safe_ws))
    s2 = sum(w * x * x for x, w in zip(xs, safe_ws))
    s3 = sum(w * x * x * x for x, w in zip(xs, safe_ws))
    s4 = sum(w * x * x * x * x for x, w in zip(xs, safe_ws))
    t0 = sum(w * y for y, w in zip(ys, safe_ws))
    t1 = sum(w * x * y for x, y, w in zip(xs, ys, safe_ws))
    t2 = sum(w * x * x * y for x, y, w in zip(xs, ys, safe_ws))
    sol = solve_3x3(
        [
            [s4, s3, s2],
            [s3, s2, s1],
            [s2, s1, s0],
        ],
        [t2, t1, t0],
    )
    if sol is None:
        return fit_quadratic(xs, ys)
    return (float(sol[0]), float(sol[1]), float(sol[2]))


def polyval(coeffs: Tuple[float, float, float], x: float) -> float:
    a, b, c = coeffs
    return a * x * x + b * x + c


class Trader:
    """
    Round 3 v35:
    - Step 1: strict Take -> Clear -> Make on the two underlyings
    - Step 2: Black-Scholes-first voucher engine with weighted IV smile fitting
    - Step 3: keep bot-overlay ideas small and stateful until proven stronger
    - Step 4: make strip exposure explicit before adding more alpha
    - Step 5: enforce lighter strip limits around the dangerous middle strikes
    - Step 6: redesign Hydrogel as a capped confidence-scaled inventory trader
    - Step 7: rebalance Hydrogel and Velvet fair construction toward the
      Phase 1 classification of anchored local-fair market makers
    - Step 8: Hydrogel oracle follow-up:
      move Hydrogel toward a regime-state engine instead of pure anchor-local-fair response
    - Step 9: Hydrogel unwind mode:
      detect regime fade after a strong long/short state and force staged exit with no top-ups
    - Step 10: soften the Hydrogel unwind:
      make exits peak-drawdown driven instead of generic late-session flattening
    - Step 11: split Hydrogel entry vs hold architecture and add absolute danger clearing
    - Step 12: Hydrogel split test C:
      three-target architecture plus fade-score exits
    """

    def _reset_day_if_needed(self, memory: dict, timestamp: int) -> None:
        last_ts = memory.get("last_timestamp")
        if last_ts is not None and timestamp < last_ts:
            memory["velvet_overlay"] = {
                "day_low": 10**18,
                "day_high": -(10**18),
                "signal": 0.0,
                "age": 999,
            }
            memory["hydro_state"] = {
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
            }
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

            # The detector found only a weak useful bias here, so keep it small.
            if 10 <= qty <= 11 and is_new_low:
                overlay["signal"] = min(1.5, float(overlay["signal"]) + 1.0)
                overlay["age"] = 0
                saw_event = True

        if not saw_event:
            overlay["age"] = int(overlay.get("age", 999)) + 1
            overlay["signal"] = float(overlay.get("signal", 0.0)) * 0.96

        # Convert the anonymous-flow hint into a small fair shift only.
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
        fair = (
            cfg["anchor_w"] * anchor
            + cfg["stable_w"] * stable_component
            + cfg["micro_w"] * micro_component
        )
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

        emergency_cap = 70
        if progress > 0.90:
            emergency_cap = 50
        if progress > 0.97:
            emergency_cap = 25

        entry_target = int(round(clamp(200.0 * math.tanh(0.95 * regime_score), -float(entry_cap), float(entry_cap))))
        hold_score = 0.88 * regime_score + 0.12 * trend_score
        hold_target = int(round(clamp(200.0 * math.tanh(0.88 * hold_score), -float(hold_cap), float(hold_cap))))
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

        long_peak_score = float(hydro_state.get("long_peak_score", 0.0))
        short_peak_score = float(hydro_state.get("short_peak_score", 0.0))
        long_peak_mid = hydro_state.get("long_peak_mid")
        short_peak_mid = hydro_state.get("short_peak_mid")
        long_peak_trend = float(hydro_state.get("long_peak_trend", 0.0))
        short_peak_trend = float(hydro_state.get("short_peak_trend", 0.0))
        long_drawdown = 0.0 if long_peak_mid is None else float(long_peak_mid) - float(mid)
        short_drawup = 0.0 if short_peak_mid is None else float(mid) - float(short_peak_mid)
        fair_gap = abs(fair - float(mid))
        signal_fade = fair_gap < max(4.0, 0.55 * spread)
        long_trend_drop = 0.0 if long_peak_trend <= 0.0 else clamp((long_peak_trend - trend_score) / max(0.6, long_peak_trend), 0.0, 2.0)
        short_trend_drop = 0.0 if short_peak_trend >= 0.0 else clamp((trend_score - short_peak_trend) / max(0.6, abs(short_peak_trend)), 0.0, 2.0)
        long_mid_drop = clamp(long_drawdown / max(8.0, 1.8 * spread), 0.0, 3.0)
        short_mid_rise = clamp(short_drawup / max(8.0, 1.8 * spread), 0.0, 3.0)
        long_signal_shrink = 1.0 if signal_fade else clamp((max(0.0, long_peak_score) - abs(signal)) / max(0.8, max(0.0, long_peak_score)), 0.0, 1.0)
        short_signal_shrink = 1.0 if signal_fade else clamp((max(0.0, abs(short_peak_score)) - abs(signal)) / max(0.8, max(0.0, abs(short_peak_score))), 0.0, 1.0)
        long_ret_flip = clamp((-ret_ema) / 0.25, 0.0, 1.5)
        short_ret_flip = clamp(ret_ema / 0.25, 0.0, 1.5)
        fade_score_long = 0.35 * long_trend_drop + 0.30 * long_mid_drop + 0.20 * long_signal_shrink + 0.15 * long_ret_flip
        fade_score_short = 0.35 * short_trend_drop + 0.30 * short_mid_rise + 0.20 * short_signal_shrink + 0.15 * short_ret_flip

        if current_pos > 0:
            emergency_target = min(hold_target, emergency_cap)
        elif current_pos < 0:
            emergency_target = max(hold_target, -emergency_cap)
        else:
            emergency_target = 0

        if current_pos > 0 and fade_score_long > 1.15:
            emergency_target = min(emergency_target, 40 if abs(current_pos) >= 150 else 60)
        if current_pos > 0 and fade_score_long > 1.85:
            emergency_target = min(emergency_target, 0 if progress > 0.88 else 20)
        if current_pos < 0 and fade_score_short > 1.15:
            emergency_target = max(emergency_target, -40 if abs(current_pos) >= 150 else -60)
        if current_pos < 0 and fade_score_short > 1.85:
            emergency_target = max(emergency_target, 0 if progress > 0.88 else -20)

        if abs(current_pos) < hold_zone:
            target = entry_target
        elif abs(current_pos) < 150:
            target = hold_target
        else:
            target = emergency_target

        extreme_hold_bars = int(hydro_state.get("extreme_hold_bars", 0))
        if extreme_hold_bars > 24 and abs(regime_score) < 1.4:
            target = int(round(target * 0.70))
        elif extreme_hold_bars > 12 and abs(regime_score) < 1.0:
            target = int(round(target * 0.85))

        flatten_before_flip = False
        if current_pos * target < 0 and abs(current_pos) > 60:
            target = 0
            flatten_before_flip = True

        unwind_long = current_pos > 120 and (fade_score_long > 1.10 or (progress > 0.90 and fade_score_long > 0.85))
        unwind_long_hard = current_pos > 150 and (fade_score_long > 1.75 or (progress > 0.95 and fade_score_long > 1.10))
        unwind_short = current_pos < -120 and (fade_score_short > 1.10 or (progress > 0.90 and fade_score_short > 0.85))
        unwind_short_hard = current_pos < -150 and (fade_score_short > 1.75 or (progress > 0.95 and fade_score_short > 1.10))

        exit_mode = ""
        if unwind_long_hard:
            exit_mode = "long_hard"
        elif unwind_long:
            exit_mode = "long"
        elif unwind_short_hard:
            exit_mode = "short_hard"
        elif unwind_short:
            exit_mode = "short"
        prev_exit_mode = str(hydro_state.get("exit_mode", ""))
        if exit_mode and exit_mode == prev_exit_mode:
            hydro_state["exit_age"] = int(hydro_state.get("exit_age", 0)) + 1
        elif exit_mode:
            hydro_state["exit_age"] = 1
        else:
            hydro_state["exit_age"] = 0
        hydro_state["exit_mode"] = exit_mode

        if exit_mode == "long":
            target = min(target, 120 if progress < 0.90 else 70)
        elif exit_mode == "long_hard":
            target = min(target, 40 if progress < 0.94 else 0)
        elif exit_mode == "short":
            target = max(target, -120 if progress < 0.90 else -70)
        elif exit_mode == "short_hard":
            target = max(target, -40 if progress < 0.94 else 0)

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
            "emergency_cap": int(emergency_cap),
            "entry_target": int(entry_target),
            "hold_target": int(hold_target),
            "emergency_target": int(emergency_target),
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
            "fade_score_long": float(fade_score_long),
            "fade_score_short": float(fade_score_short),
            "stretch_long": stretch_long,
            "stretch_short": stretch_short,
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
        if same_side_bid_block:
            can_bid = False
        if same_side_ask_block:
            can_ask = False
        if unwind_long:
            can_bid = False
        if unwind_short:
            can_ask = False
        if absolute_danger_long:
            can_bid = False
        if absolute_danger_short:
            can_ask = False

        if can_bid and (ba is None or buy_px < ba):
            mgr.buy(buy_px, quote_size)
        if can_ask and (bb is None or sell_px > bb):
            mgr.sell(sell_px, quote_size)

        return mgr.flush()

    def _trade_underlying(
        self,
        product: str,
        state: TradingState,
        fair: float,
        position_target: float = 0.0,
        take_bias: float = 0.0,
        quote_bias: float = 0.0,
        size_mult: float = 1.0,
    ) -> List[Order]:
        od = state.order_depths[product]
        cfg = UNDERLYING_CFG[product]
        limit = LIMITS[product]
        mgr = OrderManager(product, state.position.get(product, 0), limit)

        bb = best_bid(od)
        ba = best_ask(od)
        spread = (ba - bb) if bb is not None and ba is not None else 2.0

        # Step 1: Take
        for ask, volume in sorted(od.sell_orders.items()):
            edge = (fair + take_bias) - ask
            if edge >= cfg["take_edge"]:
                mgr.buy(ask, min(-volume, cfg["take_max"]))
            else:
                break

        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            edge = bid - (fair + take_bias)
            if edge >= cfg["take_edge"]:
                mgr.sell(bid, min(volume, cfg["take_max"]))
            else:
                break

        # Step 2: Clear
        pos = mgr.projected()
        relative_pos = pos - position_target
        if relative_pos > cfg["soft_limit"] and bb is not None and bb >= fair - cfg["clear_edge"]:
            mgr.sell(bb, min(int(math.ceil(relative_pos - cfg["soft_limit"])), cfg["clear_max"]))
        elif relative_pos < -cfg["soft_limit"] and ba is not None and ba <= fair + cfg["clear_edge"]:
            mgr.buy(ba, min(int(math.ceil((-cfg["soft_limit"]) - relative_pos)), cfg["clear_max"]))

        # Step 3: Make
        pos = mgr.projected()
        relative_pos = pos - position_target
        inv_ratio = relative_pos / limit
        reservation = fair + quote_bias - cfg["inv_skew"] * inv_ratio
        quote_edge = cfg["quote_edge"] + max(0.0, 0.1 * (spread - 4.0))

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

        size_scale = max(0.25, 1.0 - abs(inv_ratio)) * max(0.35, size_mult)
        quote_size = max(6, int(round(cfg["quote_size"] * size_scale)))

        if mgr.buy_cap > 0 and (ba is None or buy_px < ba):
            mgr.buy(buy_px, quote_size)
        if mgr.sell_cap > 0 and (bb is None or sell_px > bb):
            mgr.sell(sell_px, quote_size)

        return mgr.flush()

    def _build_voucher_surface(self, state: TradingState, velvet_fair: float) -> Dict[str, dict]:
        points_m: List[float] = []
        points_iv: List[float] = []
        points_w: List[float] = []
        strike_rows: Dict[str, dict] = {}

        for product, strike in VOUCHER_STRIKES.items():
            od = state.order_depths.get(product)
            if od is None:
                continue

            bb = best_bid(od)
            ba = best_ask(od)
            spread = max(1.0, float((ba - bb) if bb is not None and ba is not None else 4.0))
            liquidity = 0.0
            if bb is not None:
                liquidity += float(max(0, od.buy_orders.get(bb, 0)))
            if ba is not None:
                liquidity += float(abs(od.sell_orders.get(ba, 0)))

            market_mid = raw_mid(od)
            if market_mid is None:
                market_mid = stable_mid(od)
            if market_mid is None:
                continue

            intrinsic = max(velvet_fair - strike, 0.0)
            guarded_price = max(float(market_mid), intrinsic + 1e-3)
            market_iv = implied_vol_call(guarded_price, velvet_fair, strike, TTE_YEARS)
            m = math.log(strike / velvet_fair) / math.sqrt(TTE_YEARS)
            if 1e-6 < market_iv < 3.0:
                strike_rows[product] = {
                    "strike": strike,
                    "moneyness": m,
                    "market_mid": float(market_mid),
                    "guarded_price": guarded_price,
                    "market_iv": market_iv,
                    "spread": spread,
                    "liquidity": liquidity,
                }
                weight = clamp((math.log1p(liquidity) + 0.5) / spread, 0.4, 4.0)
                weight *= clamp(math.exp(-0.55 * abs(m)), 0.45, 1.0)
                points_m.append(m)
                points_iv.append(market_iv)
                points_w.append(weight)

        if points_iv:
            sorted_ivs = sorted(points_iv)
            median_iv = sorted_ivs[len(sorted_ivs) // 2]
            clipped_ivs = [clamp(iv, median_iv - 0.25, median_iv + 0.25) for iv in points_iv]
        else:
            median_iv = 0.18
            clipped_ivs = []

        if len(clipped_ivs) >= 3:
            coeffs = fit_quadratic_weighted(points_m, clipped_ivs, points_w)
        elif clipped_ivs:
            coeffs = (0.0, 0.0, float(sorted(clipped_ivs)[len(clipped_ivs) // 2]))
        else:
            coeffs = (0.0, 0.0, 0.18)

        fitted_sigmas: Dict[str, float] = {}
        for product, strike in VOUCHER_STRIKES.items():
            m = math.log(strike / velvet_fair) / math.sqrt(TTE_YEARS)
            sigma = float(polyval(coeffs, m))
            fitted_sigmas[product] = clamp(sigma, 1e-4, 3.0)

        ordered_products = sorted(VOUCHER_STRIKES, key=VOUCHER_STRIKES.get)
        for idx, product in enumerate(ordered_products):
            sigma = fitted_sigmas[product]
            neighbor_sigmas = [sigma]
            if idx > 0:
                neighbor_sigmas.append(fitted_sigmas[ordered_products[idx - 1]])
            if idx + 1 < len(ordered_products):
                neighbor_sigmas.append(fitted_sigmas[ordered_products[idx + 1]])
            neighbor_center = sorted(neighbor_sigmas)[len(neighbor_sigmas) // 2]
            sigma = 0.75 * sigma + 0.25 * neighbor_center
            row = strike_rows.get(product)
            if row is not None and row["liquidity"] >= 20.0 and row["spread"] <= 6.0:
                sigma = 0.85 * sigma + 0.15 * clamp(float(row["market_iv"]), sigma - 0.10, sigma + 0.10)
            fitted_sigmas[product] = clamp(sigma, 1e-4, 3.0)

        surface: Dict[str, dict] = {}
        provisional_prices: List[Tuple[str, int, float]] = []
        for product, strike in VOUCHER_STRIKES.items():
            row = strike_rows.get(product, {})
            sigma = fitted_sigmas[product]
            fair_price = black_scholes_call(velvet_fair, strike, TTE_YEARS, sigma)
            surface[product] = {
                "sigma": sigma,
                "delta": black_scholes_delta_call(velvet_fair, strike, TTE_YEARS, sigma),
                "vega_proxy": black_scholes_vega_proxy(velvet_fair, strike, TTE_YEARS, sigma),
                "moneyness": math.log(strike / velvet_fair) / math.sqrt(TTE_YEARS),
                "market_mid": row.get("market_mid"),
                "guarded_price": row.get("guarded_price"),
                "market_iv": row.get("market_iv"),
                "spread": float(row.get("spread", 4.0)),
                "liquidity": float(row.get("liquidity", 0.0)),
            }
            provisional_prices.append((product, strike, fair_price))

        prev_price = float("inf")
        for product, _, fair_price in sorted(provisional_prices, key=lambda item: item[1]):
            fair_price = min(prev_price, fair_price)
            prev_price = fair_price
            surface[product]["fair"] = fair_price
            market_price = surface[product]["guarded_price"]
            if market_price is None:
                market_price = fair_price
            market_price = max(float(market_price), max(velvet_fair - VOUCHER_STRIKES[product], 0.0) + 1e-3)
            market_iv = surface[product]["market_iv"]
            if market_iv is None:
                market_iv = implied_vol_call(market_price, velvet_fair, VOUCHER_STRIKES[product], TTE_YEARS)
                surface[product]["market_iv"] = market_iv
            surface[product]["iv_residual"] = float(market_iv) - float(surface[product]["sigma"])
            surface[product]["bs_gap"] = market_price - fair_price
        return surface

    def _build_voucher_risk_context(self, state: TradingState, surface: Dict[str, dict]) -> dict:
        liquid_products = [
            product
            for product, ctx in surface.items()
            if ctx.get("market_mid") is not None and float(ctx["market_mid"]) > 0.5 and float(ctx["liquidity"]) >= 10.0
        ]
        residual_pairs = [(product, float(surface[product]["iv_residual"])) for product in liquid_products]
        resid_scale = max(0.04, sum(abs(resid) for _, resid in residual_pairs) / max(1, len(residual_pairs)))

        pair_bias: Dict[str, int] = {}
        residual_rank: Dict[str, int] = {}
        sorted_products = sorted(VOUCHER_STRIKES, key=VOUCHER_STRIKES.get)
        sorted_residuals = sorted(liquid_products, key=lambda product: float(surface[product]["iv_residual"]))
        for rank, product in enumerate(sorted_residuals):
            centered_rank = rank - (len(sorted_residuals) - 1) / 2.0
            residual_rank[product] = int(round(centered_rank))

        for left, right in zip(sorted_products, sorted_products[1:]):
            left_ctx = surface[left]
            right_ctx = surface[right]
            if left not in liquid_products or right not in liquid_products:
                continue
            gap = float(right_ctx["iv_residual"]) - float(left_ctx["iv_residual"])
            if gap >= 0.07:
                pair_bias[left] = pair_bias.get(left, 0) + 1
                pair_bias[right] = pair_bias.get(right, 0) - 1
            elif gap <= -0.07:
                pair_bias[left] = pair_bias.get(left, 0) - 1
                pair_bias[right] = pair_bias.get(right, 0) + 1

        strip_delta = 0.0
        strip_vega = 0.0
        middle_abs = 0
        middle_net = 0
        low_wing_net = 0
        high_wing_net = 0
        adjacent_same_side_max = 0
        adjacent_same_side_products: List[str] = []
        positions = {product: int(state.position.get(product, 0)) for product in VOUCHER_STRIKES}

        for product, ctx in surface.items():
            pos = positions[product]
            delta = float(ctx["delta"])
            strip_delta += pos * delta
            strip_vega += pos * float(ctx["vega_proxy"])
            if 0.20 <= delta <= 0.80:
                middle_abs += abs(pos)
                middle_net += pos
            strike = VOUCHER_STRIKES[product]
            if strike <= 5000:
                low_wing_net += pos
            elif strike >= 5400:
                high_wing_net += pos

        for left, right in zip(sorted_products, sorted_products[1:]):
            left_pos = positions[left]
            right_pos = positions[right]
            if left_pos == 0 or right_pos == 0:
                continue
            if left_pos * right_pos > 0:
                concentration = abs(left_pos) + abs(right_pos)
                if concentration > adjacent_same_side_max:
                    adjacent_same_side_max = concentration
                    adjacent_same_side_products = [left, right]

        return {
            "resid_scale": resid_scale,
            "resid_threshold": max(0.035, 0.85 * resid_scale),
            "extreme_resid_threshold": max(0.060, 1.50 * resid_scale),
            "pair_bias": pair_bias,
            "residual_rank": residual_rank,
            "strip_delta": strip_delta,
            "strip_vega_proxy": strip_vega,
            "delta_pressure": clamp(strip_delta / 140.0, -2.0, 2.0),
            "target_velvet_pos": int(round(clamp(-0.50 * strip_delta, -100.0, 100.0))),
            "middle_abs": middle_abs,
            "middle_net": middle_net,
            "middle_cap": 170,
            "adjacent_same_side_max": adjacent_same_side_max,
            "adjacent_same_side_products": adjacent_same_side_products,
            "adjacent_cap": 170,
            "low_wing_net": low_wing_net,
            "high_wing_net": high_wing_net,
            "total_delta_cap": 150.0,
            "unconfirmed_outright_cap": 85,
        }

    def _trade_voucher(self, product: str, state: TradingState, voucher_ctx: dict, risk_ctx: dict) -> List[Order]:
        od = state.order_depths[product]
        limit = LIMITS[product]
        mgr = OrderManager(product, state.position.get(product, 0), limit)

        fair = float(voucher_ctx["fair"])
        delta = float(voucher_ctx["delta"])
        vega_proxy = float(voucher_ctx["vega_proxy"])
        iv_residual = float(voucher_ctx["iv_residual"])
        bs_gap = float(voucher_ctx.get("bs_gap", 0.0))
        residual_rank = int(risk_ctx["residual_rank"].get(product, 0))
        bb = best_bid(od)
        ba = best_ask(od)
        spread = (ba - bb) if bb is not None and ba is not None else 2.0

        middle_band = 0.20 <= delta <= 0.80
        pair_bias = int(clamp(float(risk_ctx["pair_bias"].get(product, 0)), -1.0, 1.0))
        confirmed = pair_bias != 0
        resid_threshold = float(risk_ctx["resid_threshold"])
        extreme_resid_threshold = float(risk_ctx["extreme_resid_threshold"])
        cheap_signal = max(0.0, -iv_residual)
        rich_signal = max(0.0, iv_residual)
        buy_confirmed = cheap_signal >= resid_threshold or pair_bias > 0
        sell_confirmed = rich_signal >= resid_threshold or pair_bias < 0
        buy_extreme = cheap_signal >= extreme_resid_threshold
        sell_extreme = rich_signal >= extreme_resid_threshold
        delta_soft = abs(float(risk_ctx["strip_delta"])) > float(risk_ctx["total_delta_cap"])
        delta_hard = abs(float(risk_ctx["strip_delta"])) > 1.25 * float(risk_ctx["total_delta_cap"])
        delta_block_buy = delta_hard and float(risk_ctx["strip_delta"]) > 0.0
        delta_block_sell = delta_hard and float(risk_ctx["strip_delta"]) < 0.0
        adjacent_block = (
            product in risk_ctx["adjacent_same_side_products"]
            and int(risk_ctx["adjacent_same_side_max"]) > int(risk_ctx["adjacent_cap"])
        )
        take_edge = max(0.75, 0.35 * spread) + (0.30 if middle_band else 0.0) + (0.20 if not confirmed else 0.0)
        clear_edge = max(0.35, 0.15 * spread)
        soft_limit = 85 if middle_band else 125
        per_strike_cap = 100 if not middle_band else 80
        take_max = 10 if middle_band else 18

        # Step 1: Take
        for ask, volume in sorted(od.sell_orders.items()):
            edge = fair - ask
            if pair_bias > 0:
                edge += 0.20
            if (edge >= take_edge and buy_confirmed and not delta_block_buy) or (edge >= take_edge + 0.8 and buy_extreme):
                mgr.buy(ask, min(-volume, take_max))
            else:
                break

        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            edge = bid - fair
            if pair_bias < 0:
                edge += 0.20
            if (edge >= take_edge and sell_confirmed and not delta_block_sell) or (edge >= take_edge + 0.8 and sell_extreme):
                mgr.sell(bid, min(volume, take_max))
            else:
                break

        # Step 2: Clear
        pos = mgr.projected()
        if pos > soft_limit and bb is not None and bb >= fair - clear_edge:
            mgr.sell(bb, min(pos - soft_limit, 50))
        elif pos > 0 and not buy_confirmed and bb is not None and bb >= fair - (clear_edge + 0.15):
            mgr.sell(bb, min(pos, 28))
        elif pos < -soft_limit and ba is not None and ba <= fair + clear_edge:
            mgr.buy(ba, min((-soft_limit) - pos, 50))
        elif pos < 0 and not sell_confirmed and ba is not None and ba <= fair + (clear_edge + 0.15):
            mgr.buy(ba, min(-pos, 28))

        # Step 3: Make
        pos = mgr.projected()
        inv_ratio = pos / limit
        inv_penalty = (0.02 * max(25.0, fair) + 2.0) * inv_ratio
        signal_shift = clamp((cheap_signal - rich_signal) / max(resid_threshold, 1e-6), -1.5, 1.5)
        reservation = fair - inv_penalty + 0.30 * signal_shift + 0.12 * pair_bias
        quote_edge = max(1.0, 0.45 * spread, 0.015 * max(20.0, fair))
        if middle_band:
            quote_edge += 0.40
        if not confirmed:
            quote_edge += 0.20
        if not buy_confirmed and not sell_confirmed:
            quote_edge += 0.20
        if risk_ctx["middle_abs"] > risk_ctx["middle_cap"] and middle_band:
            quote_edge += 0.35
        if delta_soft:
            quote_edge += 0.15
        if delta_hard:
            quote_edge += 0.15
        if adjacent_block:
            quote_edge += 0.15
        if abs(bs_gap) > 1.0:
            quote_edge += 0.10

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

        size_scale = max(0.20, 1.0 - abs(inv_ratio))
        if middle_band:
            size_scale *= 0.45
        if not confirmed:
            size_scale *= 0.75
        if abs(iv_residual) > 0.10:
            size_scale *= 0.85
        size_scale *= clamp(1.4 / (1.0 + 0.02 * vega_proxy), 0.35, 1.0)
        if delta_soft:
            size_scale *= 0.82
        if delta_hard:
            size_scale *= 0.80
        if adjacent_block:
            size_scale *= 0.82
        if abs(residual_rank) >= 3:
            size_scale *= 0.90
        base_size = 9 if fair > 100.0 else 14
        quote_size = max(4, int(round(base_size * size_scale)))

        if fair >= 0.5:
            can_bid = mgr.buy_cap > 0 and pos < per_strike_cap and (buy_confirmed or pos < -int(0.35 * soft_limit))
            can_ask = mgr.sell_cap > 0 and pos > -per_strike_cap and (sell_confirmed or pos > int(0.35 * soft_limit))
            if middle_band and risk_ctx["middle_abs"] > risk_ctx["middle_cap"]:
                if risk_ctx["middle_net"] >= 0:
                    can_bid = False
                if risk_ctx["middle_net"] <= 0:
                    can_ask = False
            if not confirmed and pos >= risk_ctx["unconfirmed_outright_cap"]:
                can_bid = False
            if not confirmed and pos <= -risk_ctx["unconfirmed_outright_cap"]:
                can_ask = False
            if delta_block_buy:
                can_bid = False
            if delta_block_sell:
                can_ask = False
            if adjacent_block:
                if pos >= int(0.7 * per_strike_cap) and pair_bias >= 0:
                    can_bid = False
                if pos <= -int(0.7 * per_strike_cap) and pair_bias <= 0:
                    can_ask = False

            if can_bid and (ba is None or buy_px < ba):
                mgr.buy(buy_px, quote_size)
            if can_ask and (bb is None or sell_px > bb):
                mgr.sell(sell_px, quote_size)

        return mgr.flush()

    def run(self, state: TradingState):
        memory = load_memory(state.traderData)
        memory.setdefault("engine_errors", {})
        try:
            self._reset_day_if_needed(memory, state.timestamp)
        except Exception as exc:
            memory["engine_errors"]["reset"] = type(exc).__name__

        result: Dict[str, List[Order]] = {}
        conversions = 0

        velvet_overlay_bias = 0.0
        try:
            velvet_overlay_bias = self._update_velvet_overlay(state, memory)
        except Exception as exc:
            memory["engine_errors"]["velvet_overlay"] = type(exc).__name__

        if HYDROGEL in state.order_depths:
            try:
                hydro_fair = self._underlying_fair(HYDROGEL, state.order_depths[HYDROGEL], 0.0)
                hydro_ctx = self._build_hydrogel_targets(state, hydro_fair, memory)
                memory["hydro_book"] = {
                    "mid": round(float(hydro_ctx["mid"]), 3),
                    "signal": round(float(hydro_ctx["signal"]), 3),
                    "regime_score": round(float(hydro_ctx["regime_score"]), 3),
                    "trend_score": round(float(hydro_ctx["trend_score"]), 3),
                    "anchor_score": round(float(hydro_ctx["anchor_score"]), 3),
                    "flow_score": round(float(hydro_ctx["flow_score"]), 3),
                    "confidence": str(hydro_ctx["confidence"]),
                    "entry_cap": int(hydro_ctx["entry_cap"]),
                    "hold_cap": int(hydro_ctx["hold_cap"]),
                    "emergency_cap": int(hydro_ctx["emergency_cap"]),
                    "entry_target": int(hydro_ctx["entry_target"]),
                    "hold_target": int(hydro_ctx["hold_target"]),
                    "emergency_target": int(hydro_ctx["emergency_target"]),
                    "target": int(hydro_ctx["target"]),
                    "good_book": bool(hydro_ctx["good_book"]),
                    "progress": round(float(hydro_ctx["progress"]), 3),
                    "extreme_hold_bars": int(hydro_ctx["extreme_hold_bars"]),
                    "flatten_before_flip": bool(hydro_ctx["flatten_before_flip"]),
                    "exit_mode": str(hydro_ctx["exit_mode"]),
                    "exit_age": int(hydro_ctx["exit_age"]),
                    "long_peak_score": round(float(hydro_ctx["long_peak_score"]), 3),
                    "short_peak_score": round(float(hydro_ctx["short_peak_score"]), 3),
                    "long_peak_trend": round(float(hydro_ctx["long_peak_trend"]), 3),
                    "short_peak_trend": round(float(hydro_ctx["short_peak_trend"]), 3),
                    "long_drawdown": round(float(hydro_ctx["long_drawdown"]), 3),
                    "short_drawup": round(float(hydro_ctx["short_drawup"]), 3),
                    "fade_score_long": round(float(hydro_ctx["fade_score_long"]), 3),
                    "fade_score_short": round(float(hydro_ctx["fade_score_short"]), 3),
                    "absolute_danger_long": bool(hydro_ctx["absolute_danger_long"]),
                    "absolute_danger_short": bool(hydro_ctx["absolute_danger_short"]),
                    "same_side_bid_block": bool(hydro_ctx["same_side_bid_block"]),
                    "same_side_ask_block": bool(hydro_ctx["same_side_ask_block"]),
                }
                result[HYDROGEL] = self._trade_hydrogel(state, hydro_fair, hydro_ctx)
            except Exception as exc:
                memory["engine_errors"]["hydrogel"] = type(exc).__name__

        velvet_fair = None
        if VELVET in state.order_depths:
            try:
                velvet_fair = self._underlying_fair(VELVET, state.order_depths[VELVET], velvet_overlay_bias)
            except Exception as exc:
                memory["engine_errors"]["velvet_fair"] = type(exc).__name__

        if velvet_fair is not None:
            try:
                voucher_surface = self._build_voucher_surface(state, velvet_fair)
                risk_ctx = self._build_voucher_risk_context(state, voucher_surface)
                memory["strip_monitor"] = {
                    "strip_delta": round(float(risk_ctx["strip_delta"]), 3),
                    "strip_vega_proxy": round(float(risk_ctx["strip_vega_proxy"]), 3),
                    "target_velvet_pos": int(risk_ctx["target_velvet_pos"]),
                    "middle_abs": int(risk_ctx["middle_abs"]),
                    "middle_net": int(risk_ctx["middle_net"]),
                    "middle_cap": int(risk_ctx["middle_cap"]),
                    "adjacent_same_side_max": int(risk_ctx["adjacent_same_side_max"]),
                    "adjacent_cap": int(risk_ctx["adjacent_cap"]),
                    "adjacent_same_side_products": list(risk_ctx["adjacent_same_side_products"]),
                    "low_wing_net": int(risk_ctx["low_wing_net"]),
                    "high_wing_net": int(risk_ctx["high_wing_net"]),
                }
                result[VELVET] = self._trade_underlying(
                    VELVET,
                    state,
                    velvet_fair,
                    position_target=float(risk_ctx["target_velvet_pos"]),
                    quote_bias=-0.15 * float(risk_ctx["delta_pressure"]),
                )
                for product in VOUCHER_STRIKES:
                    if product in state.order_depths:
                        result[product] = self._trade_voucher(product, state, voucher_surface[product], risk_ctx)
            except Exception as exc:
                memory["engine_errors"]["voucher_strip"] = type(exc).__name__

        return result, conversions, dump_memory(memory)
