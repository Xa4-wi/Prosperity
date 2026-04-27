from __future__ import annotations

import json
import math
from statistics import NormalDist
from typing import Dict, List, Optional, Tuple

from datamodel import Order, OrderDepth, TradingState

_N = NormalDist()

HYDRO = "HYDROGEL_PACK"
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

LOW_VOUCHERS = {"VEV_4000", "VEV_4500"}
MID_VOUCHERS = {"VEV_5000"}
ACTIVE_VOUCHERS = LOW_VOUCHERS | MID_VOUCHERS
DISABLED_VOUCHERS = set(VOUCHER_STRIKES) - ACTIVE_VOUCHERS

LIMITS: Dict[str, int] = {
    HYDRO: 200,
    VELVET: 200,
    **{p: 300 for p in VOUCHER_STRIKES},
}

# Core-engine safety caps. These are deliberately much smaller than exchange limits.
HYDRO_ENGINE_CAP = 30
VELVET_ENGINE_CAP = 100
VOUCHER_LOW_CAP = 55
VOUCHER_MID_CAP = 16

# Time-to-expiry is intentionally conservative. The engine calibrates IV from current voucher mids,
# so this mostly controls model smoothness rather than acting as a hard view.
BS_T = 5.0 / 365.0
BB_LOOKBACK = 20
SR_LOOKBACK = 120
VELVET_TOTAL_DELTA_CAP = 115.0
VELVET_TOTAL_GAMMA_CAP = 0.12
VELVET_TOTAL_VEGA_CAP = 220.0


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def load_memory(trader_data: str) -> dict:
    if not trader_data:
        return {}
    try:
        obj = json.loads(trader_data)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def dump_memory(memory: dict) -> str:
    return json.dumps(memory, separators=(",", ":"))


def best_bid(od: OrderDepth) -> Optional[int]:
    return max(od.buy_orders) if od.buy_orders else None


def best_ask(od: OrderDepth) -> Optional[int]:
    return min(od.sell_orders) if od.sell_orders else None


def mid_price(od: OrderDepth) -> Optional[float]:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None or ba is None or bb >= ba:
        return None
    return 0.5 * (bb + ba)


def stable_mid(od: OrderDepth, levels: int = 3) -> Optional[float]:
    if not od.buy_orders or not od.sell_orders:
        return mid_price(od)
    bids = sorted(od.buy_orders.items(), reverse=True)[:levels]
    asks = sorted(od.sell_orders.items())[:levels]
    bid_vol = sum(max(0, v) for _, v in bids)
    ask_vol = sum(abs(min(0, v)) for _, v in asks)
    if bid_vol <= 0 or ask_vol <= 0:
        return mid_price(od)
    bid_px = sum(px * max(0, v) for px, v in bids) / bid_vol
    ask_px = sum(px * abs(min(0, v)) for px, v in asks) / ask_vol
    if bid_px >= ask_px:
        return mid_price(od)
    return 0.5 * (bid_px + ask_px)


def micro_price(od: OrderDepth) -> Optional[float]:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None or ba is None or bb >= ba:
        return mid_price(od)
    bid_vol = max(1, int(od.buy_orders.get(bb, 0)))
    ask_vol = max(1, int(abs(od.sell_orders.get(ba, 0))))
    return (ba * bid_vol + bb * ask_vol) / float(bid_vol + ask_vol)


def book_imbalance(od: OrderDepth, levels: int = 2) -> float:
    bids = sorted(od.buy_orders.items(), reverse=True)[:levels]
    asks = sorted(od.sell_orders.items())[:levels]
    bid_vol = sum(max(0, v) for _, v in bids)
    ask_vol = sum(abs(min(0, v)) for _, v in asks)
    total = bid_vol + ask_vol
    if total <= 0:
        return 0.0
    return (bid_vol - ask_vol) / total


def top_depth(od: OrderDepth) -> int:
    bb = best_bid(od)
    ba = best_ask(od)
    depth = 0
    if bb is not None:
        depth += max(0, int(od.buy_orders.get(bb, 0)))
    if ba is not None:
        depth += abs(min(0, int(od.sell_orders.get(ba, 0))))
    return depth


def mean_std(values: List[float]) -> Tuple[float, float]:
    if not values:
        return 0.0, 0.0
    mean = sum(values) / len(values)
    if len(values) < 2:
        return mean, 0.0
    var = sum((x - mean) * (x - mean) for x in values) / len(values)
    return mean, math.sqrt(max(0.0, var))


def norm_cdf(x: float) -> float:
    return _N.cdf(x)


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def bs_d1_d2(spot: float, strike: float, t: float, vol: float) -> Optional[Tuple[float, float]]:
    if spot <= 0.0 or strike <= 0.0 or t <= 1e-9 or vol <= 1e-8:
        return None
    sqrt_t = math.sqrt(t)
    denom = vol * sqrt_t
    if denom <= 1e-9:
        return None
    d1 = (math.log(spot / strike) + 0.5 * vol * vol * t) / denom
    return d1, d1 - denom


def bs_call_price(spot: float, strike: float, t: float, vol: float) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    intrinsic = max(spot - strike, 0.0)
    if t <= 1e-9 or vol <= 1e-8:
        return intrinsic
    sqrt_t = math.sqrt(t)
    denom = vol * sqrt_t
    if denom <= 1e-9:
        return intrinsic
    d1 = (math.log(spot / strike) + 0.5 * vol * vol * t) / denom
    d2 = d1 - denom
    return max(intrinsic, spot * norm_cdf(d1) - strike * norm_cdf(d2))


def bs_call_delta(spot: float, strike: float, t: float, vol: float) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    if t <= 1e-9 or vol <= 1e-8:
        return 1.0 if spot > strike else 0.0
    d = bs_d1_d2(spot, strike, t, vol)
    if d is None:
        return 1.0 if spot > strike else 0.0
    d1, _ = d
    return norm_cdf(d1)


def bs_call_gamma(spot: float, strike: float, t: float, vol: float) -> float:
    d = bs_d1_d2(spot, strike, t, vol)
    if d is None or spot <= 0.0 or vol <= 1e-8 or t <= 1e-9:
        return 0.0
    d1, _ = d
    return norm_pdf(d1) / (spot * vol * math.sqrt(t))


def bs_call_vega(spot: float, strike: float, t: float, vol: float) -> float:
    d = bs_d1_d2(spot, strike, t, vol)
    if d is None:
        return 0.0
    d1, _ = d
    return spot * norm_pdf(d1) * math.sqrt(t)


def bs_call_theta(spot: float, strike: float, t: float, vol: float) -> float:
    d = bs_d1_d2(spot, strike, t, vol)
    if d is None:
        return 0.0
    d1, d2 = d
    first = -(spot * norm_pdf(d1) * vol) / (2.0 * math.sqrt(t))
    second = 0.0 * strike * norm_cdf(d2)
    return first - second


def bs_call_prob_exercise(spot: float, strike: float, t: float, vol: float) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    if t <= 1e-9 or vol <= 1e-8:
        return 1.0 if spot > strike else 0.0
    d = bs_d1_d2(spot, strike, t, vol)
    if d is None:
        return 1.0 if spot > strike else 0.0
    _, d2 = d
    return norm_cdf(d2)


def implied_vol_call(price: float, spot: float, strike: float, t: float) -> Optional[float]:
    if spot <= 0.0 or strike <= 0.0 or t <= 0.0:
        return None
    intrinsic = max(spot - strike, 0.0)
    if price < intrinsic - 1e-6:
        return None
    if price <= intrinsic + 1e-6:
        return 1e-4
    lo, hi = 1e-4, 3.0
    for _ in range(45):
        mid = 0.5 * (lo + hi)
        fair = bs_call_price(spot, strike, t, mid)
        if fair < price:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


class OrderManager:
    def __init__(self, product: str, position: int, limit: int) -> None:
        self.product = product
        self.position = int(position)
        self.limit = int(limit)
        self.buy_cap = max(0, self.limit - self.position)
        self.sell_cap = max(0, self.limit + self.position)
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


class Trader:
    def _book_context(self, product: str, od: OrderDepth, memory: dict) -> Optional[dict]:
        mid = mid_price(od)
        if mid is None:
            mid = stable_mid(od)
        if mid is None:
            return None
        micro = micro_price(od)
        if micro is None:
            micro = mid
        stable = stable_mid(od)
        if stable is None:
            stable = mid
        bb = best_bid(od)
        ba = best_ask(od)
        spread = float(max(1, (ba if ba is not None else int(mid + 1)) - (bb if bb is not None else int(mid - 1))))

        pm = memory.setdefault("products", {}).setdefault(product, {})
        last_mid = pm.get("last_mid")
        ret = 0.0 if last_mid is None else float(mid) - float(last_mid)
        pm["last_mid"] = float(mid)
        pm["ema_mid"] = float(mid) if pm.get("ema_mid") is None else 0.16 * float(mid) + 0.84 * float(pm["ema_mid"])
        pm["ema_slow"] = float(mid) if pm.get("ema_slow") is None else 0.045 * float(mid) + 0.955 * float(pm["ema_slow"])
        pm["ema_micro"] = float(micro) if pm.get("ema_micro") is None else 0.18 * float(micro) + 0.82 * float(pm["ema_micro"])
        pm["ret_ema"] = 0.18 * ret + 0.82 * float(pm.get("ret_ema", 0.0))
        pm["vol_ema"] = 0.18 * abs(ret) + 0.82 * float(pm.get("vol_ema", 0.0))
        pm["vol_slow"] = 0.05 * abs(ret) + 0.95 * float(pm.get("vol_slow", abs(ret)))

        ema_mid = float(pm["ema_mid"])
        ema_slow = float(pm["ema_slow"])
        ema_micro = float(pm["ema_micro"])
        ret_ema = float(pm["ret_ema"])
        vol_ema = max(0.8, float(pm["vol_ema"]), 0.50 * spread)
        vol_slow = max(0.5, float(pm["vol_slow"]))
        move_unit = max(1.0, vol_ema, 0.55 * spread)
        z = (float(mid) - ema_mid) / move_unit

        return {
            "mid": float(mid),
            "stable": float(stable),
            "micro": float(micro),
            "bb": bb,
            "ba": ba,
            "spread": spread,
            "ema_mid": ema_mid,
            "ema_slow": ema_slow,
            "ema_micro": ema_micro,
            "ret_ema": ret_ema,
            "vol_ema": vol_ema,
            "vol_slow": vol_slow,
            "move_unit": move_unit,
            "z": z,
            "micro_gap": float(micro) - float(mid),
            "imbalance": book_imbalance(od),
            "top_depth": top_depth(od),
        }

    def _hydro_orders(self, state: TradingState, memory: dict) -> List[Order]:
        od = state.order_depths[HYDRO]
        pos = int(state.position.get(HYDRO, 0))
        ctx = self._book_context(HYDRO, od, memory)
        if ctx is None:
            return []

        anchor = 10000.0
        spread = float(ctx["spread"])
        move = float(ctx["move_unit"])
        mid = float(ctx["mid"])
        z_anchor = (mid - anchor) / max(8.0, 1.4 * move)
        trend = (float(ctx["ema_mid"]) - float(ctx["ema_slow"])) / max(5.0, 1.5 * move)

        fair = 0.38 * anchor + 0.42 * float(ctx["stable"]) + 0.20 * float(ctx["micro"])
        fair += 0.18 * float(ctx["imbalance"]) * spread

        # Hydro is currently only a small controlled engine: local fade + tiny flow confirmation.
        target = 0.0
        if z_anchor > 1.3 and trend <= 0.40 and float(ctx["micro_gap"]) <= 0.15 * spread:
            target = -0.65 * HYDRO_ENGINE_CAP
        elif z_anchor < -1.3 and trend >= -0.40 and float(ctx["micro_gap"]) >= -0.15 * spread:
            target = 0.65 * HYDRO_ENGINE_CAP
        else:
            target = clamp(-0.18 * z_anchor * HYDRO_ENGINE_CAP + 0.10 * trend * HYDRO_ENGINE_CAP, -12.0, 12.0)

        target = clamp(target, -HYDRO_ENGINE_CAP, HYDRO_ENGINE_CAP)
        return self._execute_underlying(
            HYDRO,
            od,
            pos,
            LIMITS[HYDRO],
            fair=fair,
            target=target,
            engine_cap=HYDRO_ENGINE_CAP,
            take_edge=max(3.0, 0.28 * spread + 0.30 * move),
            quote_edge=max(2.2, 0.35 * spread + 0.15 * move),
            quote_size=7,
            take_max=9,
        )

    def _velvet_technical_outlook(self, ctx: dict, memory: dict) -> dict:
        pm = memory.setdefault("products", {}).setdefault(VELVET, {})
        hist = list(pm.get("mid_hist", []))
        hist.append(float(ctx["mid"]))
        if len(hist) > SR_LOOKBACK:
            hist = hist[-SR_LOOKBACK:]
        pm["mid_hist"] = hist

        bb_hist = hist[-BB_LOOKBACK:]
        bb_mid, bb_std = mean_std(bb_hist)
        bb_upper = bb_mid + 2.0 * bb_std
        bb_lower = bb_mid - 2.0 * bb_std
        bb_width = max(1.0, bb_upper - bb_lower)
        percent_b = clamp((float(ctx["mid"]) - bb_lower) / bb_width, 0.0, 1.0)
        band_width_rel = bb_width / max(1.0, bb_mid if bb_mid else float(ctx["mid"]))
        rv_proxy = clamp(1.8 * band_width_rel / max(1e-6, math.sqrt(BS_T)), 0.04, 1.20)
        rv_rising = float(ctx["vol_ema"]) > 1.18 * float(ctx["vol_slow"])

        support = min(hist) if hist else float(ctx["mid"])
        resistance = max(hist) if hist else float(ctx["mid"])
        range_width = max(1.0, resistance - support)
        near_support = float(ctx["mid"]) <= support + 0.18 * range_width
        near_resistance = float(ctx["mid"]) >= resistance - 0.18 * range_width

        trend_gap = float(ctx["ema_mid"]) - float(ctx["ema_slow"])
        trend_unit = max(1.0, 0.8 * float(ctx["move_unit"]))
        squeeze = band_width_rel <= 0.0038
        breakout_up = float(ctx["mid"]) > resistance - 0.02 * range_width and trend_gap > 0.55 * trend_unit and float(ctx["micro_gap"]) >= -0.08 * float(ctx["spread"])
        breakout_down = float(ctx["mid"]) < support + 0.02 * range_width and trend_gap < -0.55 * trend_unit and float(ctx["micro_gap"]) <= 0.08 * float(ctx["spread"])
        uptrend = trend_gap > 0.35 * trend_unit and not breakout_down
        downtrend = trend_gap < -0.35 * trend_unit and not breakout_up
        ride_up = percent_b >= 0.88 and uptrend and float(ctx["ret_ema"]) > 0.0
        ride_down = percent_b <= 0.12 and downtrend and float(ctx["ret_ema"]) < 0.0

        mode = "SIDEWAYS"
        if breakout_up:
            mode = "BREAKOUT_UP"
        elif breakout_down:
            mode = "BREAKOUT_DOWN"
        elif squeeze:
            mode = "SQUEEZE"
        elif uptrend:
            mode = "UPTREND"
        elif downtrend:
            mode = "DOWNTREND"

        fair_shift = 0.0
        voucher_bias = 0.0
        block_short = False
        block_long = False
        if mode == "BREAKOUT_UP":
            fair_shift = 0.18 * float(ctx["move_unit"])
            voucher_bias = 0.65
            block_short = True
        elif mode == "BREAKOUT_DOWN":
            fair_shift = -0.18 * float(ctx["move_unit"])
            voucher_bias = -0.65
            block_long = True
        elif mode == "UPTREND":
            fair_shift = 0.10 * float(ctx["move_unit"])
            voucher_bias = 0.35
        elif mode == "DOWNTREND":
            fair_shift = -0.10 * float(ctx["move_unit"])
            voucher_bias = -0.35
        elif mode == "SQUEEZE":
            voucher_bias = 0.0

        return {
            "mode": mode,
            "trend_gap": trend_gap,
            "support": support,
            "resistance": resistance,
            "range_width": range_width,
            "near_support": near_support,
            "near_resistance": near_resistance,
            "bb_mid": bb_mid,
            "bb_std": bb_std,
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "bb_width": bb_width,
            "band_width_rel": band_width_rel,
            "percent_b": percent_b,
            "rv_proxy": rv_proxy,
            "rv_rising": rv_rising,
            "ride_up": ride_up,
            "ride_down": ride_down,
            "squeeze": squeeze,
            "breakout_up": breakout_up,
            "breakout_down": breakout_down,
            "fair_shift": fair_shift,
            "voucher_bias": voucher_bias,
            "block_short": block_short,
            "block_long": block_long,
        }

    def _velvet_orders(self, state: TradingState, memory: dict) -> Tuple[List[Order], Optional[float], Optional[dict]]:
        od = state.order_depths[VELVET]
        pos = int(state.position.get(VELVET, 0))
        ctx = self._book_context(VELVET, od, memory)
        if ctx is None:
            return [], None, None

        spread = float(ctx["spread"])
        move = float(ctx["move_unit"])
        z = float(ctx["z"])
        micro_gap = float(ctx["micro_gap"])
        imbalance = float(ctx["imbalance"])
        ret_ema = float(ctx["ret_ema"])
        outlook = self._velvet_technical_outlook(ctx, memory)

        fair = float(ctx["mid"])
        fair += 0.70 * micro_gap
        fair += 0.45 * imbalance * spread
        fair += 0.18 * ret_ema
        fair -= 0.20 * z * move
        fair += float(outlook["fair_shift"])

        # Main Velvet behavior: local z-score fade when book pressure stops disagreeing.
        target = 0.0
        if z < -1.10 and micro_gap >= -0.20 * spread and not bool(outlook["block_long"]):
            target += 0.60 * VELVET_ENGINE_CAP
        elif z > 1.10 and micro_gap <= 0.20 * spread and not bool(outlook["block_short"]):
            target -= 0.60 * VELVET_ENGINE_CAP

        # Weak trend/microstructure overlay, intentionally smaller than z-fade.
        flow = clamp((micro_gap / max(1.0, 0.5 * spread)) + 0.65 * imbalance + 0.25 * ret_ema / max(1.0, move), -2.0, 2.0)
        target += 0.18 * VELVET_ENGINE_CAP * flow
        target += 0.16 * VELVET_ENGINE_CAP * float(outlook["voucher_bias"])

        if bool(outlook["near_support"]) and not bool(outlook["breakout_down"]):
            target = max(target, -0.10 * VELVET_ENGINE_CAP)
        if bool(outlook["near_resistance"]) and not bool(outlook["breakout_up"]):
            target = min(target, 0.10 * VELVET_ENGINE_CAP)

        # High-volatility reduction and no giant directional inventory.
        if float(ctx["vol_ema"]) > 3.5:
            target *= 0.80
        if bool(outlook["squeeze"]):
            target *= 0.65
        if abs(pos) > 140:
            target *= 0.50
        target = clamp(target, -VELVET_ENGINE_CAP, VELVET_ENGINE_CAP)

        orders = self._execute_underlying(
            VELVET,
            od,
            pos,
            LIMITS[VELVET],
            fair=fair,
            target=target,
            engine_cap=VELVET_ENGINE_CAP,
            take_edge=max(1.3, (0.23 * spread + 0.18 * move) * (1.20 if bool(outlook["squeeze"]) else 1.0)),
            quote_edge=max(1.3, (0.32 * spread + 0.13 * move) * (1.25 if bool(outlook["squeeze"]) or bool(outlook["breakout_up"]) or bool(outlook["breakout_down"]) else 1.0)),
            quote_size=10,
            take_max=14,
        )
        return orders, fair, {**ctx, **outlook}

    def _execute_underlying(
        self,
        product: str,
        od: OrderDepth,
        pos: int,
        limit: int,
        fair: float,
        target: float,
        engine_cap: int,
        take_edge: float,
        quote_edge: float,
        quote_size: int,
        take_max: int,
    ) -> List[Order]:
        mgr = OrderManager(product, pos, limit)
        bb = best_bid(od)
        ba = best_ask(od)

        # Never let a core engine drift beyond its test cap unless already forced by fills.
        target = clamp(target, -float(engine_cap), float(engine_cap))
        target_gap = target - pos

        # Take only when the edge helps move toward target, or when edge is very large.
        for ask, volume in sorted(od.sell_orders.items()):
            edge = fair - ask
            if edge < take_edge:
                break
            if target_gap <= 0 and edge < take_edge + 2.0:
                break
            qty = min(abs(int(volume)), take_max, max(0, int(round(target - mgr.projected())) + take_max // 2))
            if qty <= 0:
                break
            mgr.buy(ask, qty)

        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            edge = bid - fair
            if edge < take_edge:
                break
            if target_gap >= 0 and edge < take_edge + 2.0:
                break
            qty = min(abs(int(volume)), take_max, max(0, int(round(mgr.projected() - target)) + take_max // 2))
            if qty <= 0:
                break
            mgr.sell(bid, qty)

        # Inventory clearing toward target.
        projected = mgr.projected()
        relative = projected - target
        soft = max(8, int(0.45 * engine_cap))
        if relative > soft and bb is not None:
            mgr.sell(bb, min(int(math.ceil(relative - soft)), take_max + 4))
        elif relative < -soft and ba is not None:
            mgr.buy(ba, min(int(math.ceil((-soft) - relative)), take_max + 4))

        projected = mgr.projected()
        relative = projected - target
        inv_ratio = relative / max(1.0, float(engine_cap))
        reservation = fair - 1.8 * quote_edge * inv_ratio
        buy_px = math.floor(reservation - quote_edge)
        sell_px = math.ceil(reservation + quote_edge)
        if bb is not None and ba is not None and bb < ba:
            if ba - bb >= 3:
                buy_px = max(int(buy_px), bb + 1)
                sell_px = min(int(sell_px), ba - 1)
            else:
                buy_px = min(int(buy_px), bb)
                sell_px = max(int(sell_px), ba)
            buy_px = min(buy_px, ba - 1)
            sell_px = max(sell_px, bb + 1)

        scale = max(0.35, 1.0 - abs(relative) / max(1.0, float(engine_cap)))
        q = max(3, int(round(quote_size * scale)))
        if mgr.buy_cap > 0 and pos < engine_cap and (ba is None or buy_px < ba):
            mgr.buy(int(buy_px), min(q, mgr.buy_cap))
        if mgr.sell_cap > 0 and pos > -engine_cap and (bb is None or sell_px > bb):
            mgr.sell(int(sell_px), min(q, mgr.sell_cap))
        return mgr.orders

    def _voucher_cap(self, product: str) -> int:
        if product in LOW_VOUCHERS:
            return VOUCHER_LOW_CAP
        return VOUCHER_MID_CAP

    def _build_voucher_surface(self, state: TradingState, memory: dict, spot: float) -> dict:
        rows: List[Tuple[str, float, float, float, float]] = []  # product, x, iv, weight, mid
        product_mem = memory.setdefault("products", {})
        for product, strike in VOUCHER_STRIKES.items():
            if product in DISABLED_VOUCHERS:
                continue
            od = state.order_depths.get(product)
            if od is None:
                continue
            mid = mid_price(od)
            if mid is None:
                continue
            iv = implied_vol_call(float(mid), max(1.0, spot), float(strike), BS_T)
            if iv is None or iv <= 0.0 or iv >= 3.0:
                continue
            x = math.log(float(strike) / max(1.0, spot))
            bb = best_bid(od)
            ba = best_ask(od)
            spread = float(max(1, (ba if ba is not None else int(mid + 1)) - (bb if bb is not None else int(mid - 1))))
            liq = max(1.0, float(top_depth(od)))
            weight = clamp(math.log1p(liq) / spread, 0.25, 4.0)
            rows.append((product, x, iv, weight, float(mid)))
            saved = product_mem.setdefault(product, {})
            saved["iv_ema"] = iv if saved.get("iv_ema") is None else 0.08 * iv + 0.92 * float(saved["iv_ema"])

        if not rows:
            return {"base_iv": 0.18, "slope": 0.0, "fairs": {}}

        raw_ivs = sorted(iv for _, _, iv, _, _ in rows)
        median_iv = raw_ivs[len(raw_ivs) // 2]
        clipped = [(p, x, clamp(iv, median_iv - 0.35, median_iv + 0.35), w, m) for p, x, iv, w, m in rows]
        sw = sum(w for _, _, _, w, _ in clipped)
        mean_x = sum(x * w for _, x, _, w, _ in clipped) / sw
        mean_iv = sum(iv * w for _, _, iv, w, _ in clipped) / sw
        var_x = sum(w * (x - mean_x) * (x - mean_x) for _, x, _, w, _ in clipped)
        cov = sum(w * (x - mean_x) * (iv - mean_iv) for _, x, iv, w, _ in clipped)
        slope = cov / var_x if var_x > 1e-9 else 0.0
        slope = clamp(slope, -4.0, 4.0)

        fairs = {}
        for product, strike in VOUCHER_STRIKES.items():
            if product in DISABLED_VOUCHERS:
                continue
            x = math.log(float(strike) / max(1.0, spot))
            struct_iv = clamp(mean_iv + slope * (x - mean_x), 0.03, 2.50)
            saved = product_mem.setdefault(product, {})
            iv_ema = float(saved.get("iv_ema", struct_iv))
            fair_iv = clamp(0.82 * struct_iv + 0.18 * iv_ema, 0.03, 2.50)
            fair_px = bs_call_price(max(1.0, spot), float(strike), BS_T, fair_iv)
            gamma = bs_call_gamma(max(1.0, spot), float(strike), BS_T, fair_iv)
            vega = bs_call_vega(max(1.0, spot), float(strike), BS_T, fair_iv)
            theta = bs_call_theta(max(1.0, spot), float(strike), BS_T, fair_iv)
            prob_ex = bs_call_prob_exercise(max(1.0, spot), float(strike), BS_T, fair_iv)
            fairs[product] = {
                "fair_px": fair_px,
                "fair_iv": fair_iv,
                "delta": bs_call_delta(max(1.0, spot), float(strike), BS_T, fair_iv),
                "gamma": gamma,
                "vega": vega,
                "theta": theta,
                "prob_exercise": prob_ex,
                "moneyness": float(strike) / max(1.0, spot),
            }
        return {"base_iv": mean_iv, "slope": slope, "fairs": fairs}

    def _portfolio_velvet_delta(self, state: TradingState, surface: dict) -> float:
        total = float(state.position.get(VELVET, 0))
        for product in ACTIVE_VOUCHERS:
            fair_info = surface.get("fairs", {}).get(product)
            if fair_info is None:
                continue
            total += float(state.position.get(product, 0)) * float(fair_info.get("delta", 0.0))
        return total

    def _portfolio_voucher_risks(self, state: TradingState, surface: dict) -> dict:
        delta_total = float(state.position.get(VELVET, 0))
        gamma_total = 0.0
        vega_total = 0.0
        theta_total = 0.0
        for product in ACTIVE_VOUCHERS:
            fair_info = surface.get("fairs", {}).get(product)
            if fair_info is None:
                continue
            pos = float(state.position.get(product, 0))
            delta_total += pos * float(fair_info.get("delta", 0.0))
            gamma_total += pos * float(fair_info.get("gamma", 0.0))
            vega_total += pos * float(fair_info.get("vega", 0.0))
            theta_total += pos * float(fair_info.get("theta", 0.0))
        return {
            "delta": delta_total,
            "gamma": gamma_total,
            "vega": vega_total,
            "theta": theta_total,
        }

    def _voucher_orders(self, product: str, state: TradingState, surface: dict, outlook: Optional[dict], risk_state: dict) -> List[Order]:
        if product in DISABLED_VOUCHERS:
            return []
        od = state.order_depths[product]
        pos = int(state.position.get(product, 0))
        cap = self._voucher_cap(product)
        fair_info = surface.get("fairs", {}).get(product)
        if fair_info is None:
            return []
        market_mid = mid_price(od)
        if market_mid is None:
            return []
        bb = best_bid(od)
        ba = best_ask(od)
        spread = float(max(1, (ba if ba is not None else int(market_mid + 1)) - (bb if bb is not None else int(market_mid - 1))))
        fair = float(fair_info["fair_px"])
        delta = float(fair_info["delta"])
        gamma = float(fair_info.get("gamma", 0.0))
        vega = float(fair_info.get("vega", 0.0))
        theta = float(fair_info.get("theta", 0.0))
        prob_ex = float(fair_info.get("prob_exercise", delta))
        moneyness = float(fair_info.get("moneyness", 1.0))
        fair_iv = float(fair_info.get("fair_iv", surface.get("base_iv", 0.18)))
        residual = float(market_mid) - fair
        outlook = outlook or {}
        rv_proxy = float(outlook.get("rv_proxy", surface.get("base_iv", 0.18)))
        rv_rising = bool(outlook.get("rv_rising", False))
        mode = str(outlook.get("mode", "SIDEWAYS"))

        gamma_hot = 0.35 <= delta <= 0.75 or 0.30 <= prob_ex <= 0.70
        underlying_like = prob_ex > 0.70 or delta > 0.80 or moneyness < 0.93
        lottery = prob_ex < 0.05 or moneyness > 1.08
        short_ok = mode == "SIDEWAYS" and not bool(outlook.get("squeeze", False)) and not rv_rising and not bool(outlook.get("breakout_up", False))
        long_ok = not bool(outlook.get("breakout_down", False))
        if product in LOW_VOUCHERS:
            short_ok = mode in ("SIDEWAYS", "DOWNTREND") and not bool(outlook.get("squeeze", False)) and not bool(outlook.get("breakout_up", False))
            long_ok = mode in ("SIDEWAYS", "UPTREND", "BREAKOUT_UP") or bool(outlook.get("near_support", False))

        eff_cap = float(cap)
        if gamma_hot:
            eff_cap *= 0.45 if product in MID_VOUCHERS else 0.60
        elif underlying_like:
            eff_cap *= 0.80
        elif lottery:
            eff_cap *= 0.35
        if product == "VEV_4000":
            eff_cap *= 1.20
        if product in MID_VOUCHERS:
            eff_cap *= 1.10
        if bool(outlook.get("squeeze", False)):
            eff_cap *= 0.80
        cap = max(4, int(round(eff_cap)))

        gamma_buffer = 0.55 * gamma * (float(outlook.get("range_width", max(1.0, spread))) * 0.10 + float(outlook.get("rv_proxy", 0.10)) * 18.0) ** 2
        iv_uncertainty = 0.18 * vega * abs(fair_iv - rv_proxy)
        inventory_buffer = 0.35 * spread * (abs(pos) / max(1.0, float(cap)))
        theta_credit = min(0.55 * spread, max(0.0, -theta) * 0.002)
        edge = spread + gamma_buffer + iv_uncertainty + inventory_buffer - theta_credit
        edge = max(edge, 1.10 * spread, 0.030 * max(10.0, fair))
        if gamma_hot:
            edge *= 1.35
        if product in MID_VOUCHERS:
            edge *= 1.00
        if product in LOW_VOUCHERS and underlying_like and not bool(outlook.get("squeeze", False)):
            edge *= 0.82
        if product == "VEV_4000" and underlying_like and not bool(outlook.get("squeeze", False)):
            edge *= 0.90
        if bool(outlook.get("squeeze", False)):
            edge *= 1.18
        if rv_rising:
            edge *= 1.12

        score = residual / edge
        if product in MID_VOUCHERS:
            target = -0.45 * cap * math.tanh(0.80 * score)
            if abs(score) < (1.00 if gamma_hot else 0.80):
                target = 0.0
        else:
            target = -0.78 * cap * math.tanh(0.85 * score)
            threshold = 0.45 if underlying_like else 0.55
            if product == "VEV_4000":
                threshold = 0.32 if underlying_like else 0.45
            if abs(score) < threshold:
                target = 0.0

        if not short_ok:
            target = max(target, 0.0)
        if not long_ok:
            target = min(target, 0.0)

        vbias = float(outlook.get("voucher_bias", 0.0))
        trend_gap = float(outlook.get("trend_gap", 0.0))
        range_width = max(1.0, float(outlook.get("range_width", max(1.0, spread))))
        trend_norm = clamp(trend_gap / max(1.0, 0.18 * range_width), -1.5, 1.5)
        low_entry_bias = clamp(0.80 * vbias + 0.35 * trend_norm, -1.25, 1.25)
        if short_ok and fair_iv > rv_proxy + 0.05 and residual > 0.0:
            target -= 0.18 * cap * clamp((fair_iv - rv_proxy) / 0.20, 0.0, 1.0)
        if long_ok and fair_iv < rv_proxy - 0.04 and residual < 0.0 and not gamma_hot:
            target += 0.12 * cap * clamp((rv_proxy - fair_iv) / 0.15, 0.0, 1.0)
        target += 0.12 * cap * vbias
        if product in LOW_VOUCHERS and underlying_like:
            target += (0.28 if product == "VEV_4000" else 0.22) * cap * low_entry_bias
            if bool(outlook.get("near_support", False)) and residual <= 0.25 * edge:
                target = max(target, (0.30 if product == "VEV_4000" else 0.22) * cap)
            if bool(outlook.get("near_resistance", False)) and residual >= -0.25 * edge:
                target = min(target, (-0.30 if product == "VEV_4000" else -0.22) * cap)

        if outlook:
            if mode in ("UPTREND", "BREAKOUT_UP"):
                target = max(target, 0.0 if product in MID_VOUCHERS else -0.20 * cap)
            elif mode in ("DOWNTREND", "BREAKOUT_DOWN"):
                target = min(target, 0.0 if product in MID_VOUCHERS else 0.20 * cap)
            if bool(outlook.get("near_support", False)) and not bool(outlook.get("breakout_down", False)):
                target = max(target, -0.10 * cap)
            if bool(outlook.get("near_resistance", False)) and not bool(outlook.get("breakout_up", False)):
                target = min(target, 0.10 * cap)
        target = clamp(target, -cap, cap)
        if abs(pos) > int(0.90 * cap):
            target *= 0.55

        delta_without_new = float(risk_state.get("delta", 0.0))
        if target > 0.0 and delta_without_new > VELVET_TOTAL_DELTA_CAP:
            target = min(target, 0.0)
        if target < 0.0 and delta_without_new < -VELVET_TOTAL_DELTA_CAP:
            target = max(target, 0.0)
        if target != 0.0 and abs(float(risk_state.get("gamma", 0.0))) > VELVET_TOTAL_GAMMA_CAP and gamma_hot:
            target *= 0.35
        if target != 0.0 and abs(float(risk_state.get("vega", 0.0))) > VELVET_TOTAL_VEGA_CAP and product in MID_VOUCHERS:
            target *= 0.50

        mgr = OrderManager(product, pos, LIMITS[product])
        take_max = 3 if product in MID_VOUCHERS else 5
        buy_edge = edge
        sell_edge = edge
        if outlook:
            if bool(outlook.get("breakout_up", False)) or bool(outlook.get("ride_up", False)):
                buy_edge *= 0.88
                sell_edge *= 1.22
            elif bool(outlook.get("breakout_down", False)) or bool(outlook.get("ride_down", False)):
                buy_edge *= 1.22
                sell_edge *= 0.88

        # Take only when residual is clear and trade moves toward target.
        for ask, volume in sorted(od.sell_orders.items()):
            trade_edge = fair - ask
            if trade_edge < buy_edge:
                break
            if target <= mgr.projected() and trade_edge < buy_edge + 1.0:
                break
            qty = min(abs(int(volume)), take_max, max(0, int(round(target - mgr.projected())) + 2))
            if qty <= 0:
                break
            mgr.buy(ask, qty)

        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            trade_edge = bid - fair
            if trade_edge < sell_edge:
                break
            if target >= mgr.projected() and trade_edge < sell_edge + 1.0:
                break
            qty = min(abs(int(volume)), take_max, max(0, int(round(mgr.projected() - target)) + 2))
            if qty <= 0:
                break
            mgr.sell(bid, qty)

        # Clear over-cap exposure, but avoid constant mid-strike churn.
        rel = mgr.projected() - target
        soft = int((0.50 if product in MID_VOUCHERS else 0.65) * cap)
        if rel > soft and bb is not None and bb >= fair - 0.50 * edge:
            mgr.sell(bb, min(int(math.ceil(rel - soft)), take_max + 5))
        elif rel < -soft and ba is not None and ba <= fair + 0.50 * edge:
            mgr.buy(ba, min(int(math.ceil((-soft) - rel)), take_max + 5))

        # Passive quote only if residual direction or inventory gives a reason.
        rel = mgr.projected() - target
        reservation = fair - 0.45 * edge * (rel / max(1.0, float(cap)))
        quote_edge = edge + 0.35 * spread
        bid_px = math.floor(reservation - quote_edge)
        ask_px = math.ceil(reservation + quote_edge)
        if bb is not None and ba is not None and bb < ba:
            if ba - bb >= 3:
                bid_px = max(int(bid_px), bb + 1)
                ask_px = min(int(ask_px), ba - 1)
            else:
                bid_px = min(int(bid_px), bb)
                ask_px = max(int(ask_px), ba)
            bid_px = min(bid_px, ba - 1)
            ask_px = max(ask_px, bb + 1)

        q = max(2, min(5 if product in MID_VOUCHERS else 6, int(round(3 + 2 * min(1.0, abs(score))))))
        passive_gate = 0.55 if product in MID_VOUCHERS else 0.35
        if product in LOW_VOUCHERS and underlying_like:
            passive_gate = 0.22
        if product == "VEV_4000":
            passive_gate = 0.18 if underlying_like else 0.24
        if bool(outlook.get("squeeze", False)):
            passive_gate *= 1.15
        allow_bid = long_ok and mgr.buy_cap > 0 and mgr.projected() < cap and (
            residual < -passive_gate * edge
            or mgr.projected() < -0.45 * cap
            or (product in LOW_VOUCHERS and low_entry_bias > 0.25 and mgr.projected() < (0.30 if product == "VEV_4000" else 0.20) * cap)
        )
        allow_ask = short_ok and mgr.sell_cap > 0 and mgr.projected() > -cap and (
            residual > passive_gate * edge
            or mgr.projected() > 0.45 * cap
            or (product in LOW_VOUCHERS and low_entry_bias < -0.25 and mgr.projected() > (-0.30 if product == "VEV_4000" else -0.20) * cap)
        )
        if allow_bid and ba is not None and bid_px < ba:
            mgr.buy(int(bid_px), min(q, mgr.buy_cap))
        if allow_ask and bb is not None and ask_px > bb:
            mgr.sell(int(ask_px), min(q, mgr.sell_cap))
        return mgr.orders

    def run(self, state: TradingState):
        memory = load_memory(state.traderData)
        result: Dict[str, List[Order]] = {p: [] for p in state.order_depths}
        conversions = 0

        if HYDRO in state.order_depths:
            result[HYDRO] = self._hydro_orders(state, memory)

        velvet_fair = None
        velvet_ctx = None
        if VELVET in state.order_depths:
            velvet_orders, velvet_fair, velvet_ctx = self._velvet_orders(state, memory)
            result[VELVET] = velvet_orders
            if velvet_ctx is not None:
                memory["velvet_diag"] = {
                    "mid": round(float(velvet_ctx["mid"]), 3),
                    "z": round(float(velvet_ctx["z"]), 3),
                    "micro_gap": round(float(velvet_ctx["micro_gap"]), 3),
                    "trend_gap": round(float(velvet_ctx["trend_gap"]), 3),
                    "vol": round(float(velvet_ctx["vol_ema"]), 3),
                    "mode": str(velvet_ctx["mode"]),
                    "rv_proxy": round(float(velvet_ctx["rv_proxy"]), 4),
                    "rv_rising": bool(velvet_ctx["rv_rising"]),
                    "band_width_rel": round(float(velvet_ctx["band_width_rel"]), 5),
                    "percent_b": round(float(velvet_ctx["percent_b"]), 3),
                    "fair": round(float(velvet_fair), 3) if velvet_fair is not None else None,
                }

        if velvet_fair is None:
            vmem = memory.setdefault("products", {}).setdefault(VELVET, {})
            velvet_fair = float(vmem.get("ema_mid", 5250.0))

        if any(p in state.order_depths for p in VOUCHER_STRIKES):
            surface = self._build_voucher_surface(state, memory, velvet_fair)
            risk_state = self._portfolio_voucher_risks(state, surface)
            memory["surface_diag"] = {
                "base_iv": round(float(surface.get("base_iv", 0.18)), 4),
                "slope": round(float(surface.get("slope", 0.0)), 4),
                "total_delta": round(float(risk_state["delta"]), 3),
                "net_gamma": round(float(risk_state["gamma"]), 5),
                "net_vega": round(float(risk_state["vega"]), 3),
                "net_theta": round(float(risk_state["theta"]), 3),
            }
            for product in ACTIVE_VOUCHERS:
                if product in state.order_depths:
                    result[product] = self._voucher_orders(product, state, surface, velvet_ctx, risk_state)

        memory["voucher_diag"] = {
            "active": sorted(ACTIVE_VOUCHERS),
            "disabled": sorted(DISABLED_VOUCHERS),
        }

        return result, conversions, dump_memory(memory)
