from __future__ import annotations

import json
import math
from statistics import NormalDist
from typing import Dict, List, Optional, Tuple

try:
    from datamodel import Order, OrderDepth, TradingState
except ModuleNotFoundError:
    from trader_factory.core.datamodel import Order, OrderDepth, TradingState


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

TTE_YEARS = 5.0 / 365.0

# This file is intentionally a restart scaffold. The flags let us test one
# competition-intel idea at a time instead of mutating an overgrown branch.
RESEARCH_FLAGS = {
    "hydrogel_simple_anchor_mm": True,
    "velvet_hedge_book": True,
    "voucher_side_surfaces": True,
    "voucher_hybrid_iv": True,
    "voucher_pair_first": True,
    "voucher_shock_mode": True,
    "voucher_quick_scalp": True,
}

HYDRO_CFG = {
    "anchor": 10000.0,
    "anchor_w": 0.56,
    "stable_w": 0.28,
    "micro_w": 0.16,
    "imbalance_w": 1.0,
    "take_edge": 2.0,
    "quote_edge": 3.0,
    "clear_edge": 1.0,
    "take_max": 20,
    "clear_max": 34,
    "quote_size": 20,
    "soft_limit": 90,
    "inv_skew": 7.0,
}

VELVET_CFG = {
    "anchor": 5250.0,
    "anchor_w": 0.42,
    "stable_w": 0.36,
    "micro_w": 0.22,
    "imbalance_w": 0.80,
    "take_edge": 1.0,
    "quote_edge": 1.4,
    "clear_edge": 0.6,
    "take_max": 28,
    "clear_max": 46,
    "quote_size": 28,
    "soft_limit": 110,
    "inv_skew": 4.5,
}


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def load_memory(trader_data: str) -> dict:
    if not trader_data:
        return {}
    try:
        parsed = json.loads(trader_data)
        return parsed if isinstance(parsed, dict) else {}
    except (json.JSONDecodeError, TypeError, ValueError):
        return {}


def dump_memory(memory: dict) -> str:
    return json.dumps(memory, separators=(",", ":"))


class OrderManager:
    def __init__(self, product: str, position: int, limit: int) -> None:
        self.product = product
        self.position = int(position)
        self.limit = int(limit)
        self.buy_cap = max(0, self.limit - self.position)
        self.sell_cap = max(0, self.limit + self.position)
        self._orders: List[Order] = []

    def projected(self) -> int:
        return self.position + sum(order.quantity for order in self._orders)

    def buy(self, price: int, qty: int) -> None:
        qty = min(max(0, int(qty)), self.buy_cap)
        if qty > 0:
            self._orders.append(Order(self.product, int(price), qty))
            self.buy_cap -= qty

    def sell(self, price: int, qty: int) -> None:
        qty = min(max(0, int(qty)), self.sell_cap)
        if qty > 0:
            self._orders.append(Order(self.product, int(price), -qty))
            self.sell_cap -= qty

    def flush(self) -> List[Order]:
        out = self._orders
        self._orders = []
        return out


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


def wall_mid(od: OrderDepth) -> Optional[float]:
    if not od.buy_orders or not od.sell_orders:
        return raw_mid(od)
    bid_px = max(top_bid_levels(od, 3), key=lambda item: (item[1], item[0]))[0]
    ask_px = min(top_ask_levels(od, 3), key=lambda item: (item[1], item[0]))[0]
    if bid_px >= ask_px:
        return raw_mid(od)
    return 0.5 * (bid_px + ask_px)


def thick_mid(od: OrderDepth, levels: int = 3) -> Optional[float]:
    if not od.buy_orders or not od.sell_orders:
        return raw_mid(od)
    bids = top_bid_levels(od, levels)
    asks = top_ask_levels(od, levels)
    bid_vol = sum(volume for _, volume in bids)
    ask_vol = sum(abs(volume) for _, volume in asks)
    if bid_vol <= 0 or ask_vol <= 0:
        return raw_mid(od)
    bid_px = sum(price * volume for price, volume in bids) / bid_vol
    ask_px = sum(price * abs(volume) for price, volume in asks) / ask_vol
    if bid_px >= ask_px:
        return raw_mid(od)
    return 0.5 * (bid_px + ask_px)


def micro_price(od: OrderDepth) -> Optional[float]:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None or ba is None or bb >= ba:
        return raw_mid(od)
    bid_vol = max(0, od.buy_orders.get(bb, 0))
    ask_vol = abs(od.sell_orders.get(ba, 0))
    total = bid_vol + ask_vol
    if total <= 0:
        return raw_mid(od)
    return (ba * bid_vol + bb * ask_vol) / total


def stable_mid(od: OrderDepth) -> Optional[float]:
    mids = [value for value in (wall_mid(od), thick_mid(od), raw_mid(od)) if value is not None]
    return sum(mids) / len(mids) if mids else None


def book_imbalance(od: OrderDepth, levels: int = 2) -> float:
    if not od.buy_orders or not od.sell_orders:
        return 0.0
    bid_vol = sum(volume for _, volume in top_bid_levels(od, levels))
    ask_vol = sum(abs(volume) for _, volume in top_ask_levels(od, levels))
    total = bid_vol + ask_vol
    if total <= 0:
        return 0.0
    return (bid_vol - ask_vol) / total


def round_down(x: float) -> int:
    return math.floor(x)


def round_up(x: float) -> int:
    return math.ceil(x)


def norm_cdf(x: float) -> float:
    return _N.cdf(x)


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
    return spot * math.exp(-0.5 * d1 * d1) * sqrt_t / math.sqrt(2.0 * math.pi)


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


def fit_quadratic_weighted(xs: List[float], ys: List[float], ws: List[float]) -> Optional[Tuple[float, float, float]]:
    if len(xs) != len(ys) or len(xs) != len(ws) or len(xs) < 3:
        return None
    s_x4 = s_x3 = s_x2 = s_x = s_1 = 0.0
    s_yx2 = s_yx = s_y = 0.0
    for x, y, w in zip(xs, ys, ws):
        x2 = x * x
        s_x4 += w * x2 * x2
        s_x3 += w * x2 * x
        s_x2 += w * x2
        s_x += w * x
        s_1 += w
        s_yx2 += w * y * x2
        s_yx += w * y * x
        s_y += w * y

    a11, a12, a13 = s_x4, s_x3, s_x2
    a21, a22, a23 = s_x3, s_x2, s_x
    a31, a32, a33 = s_x2, s_x, s_1
    b1, b2, b3 = s_yx2, s_yx, s_y

    det = (
        a11 * (a22 * a33 - a23 * a32)
        - a12 * (a21 * a33 - a23 * a31)
        + a13 * (a21 * a32 - a22 * a31)
    )
    if abs(det) < 1e-10:
        return None

    det_a = (
        b1 * (a22 * a33 - a23 * a32)
        - a12 * (b2 * a33 - a23 * b3)
        + a13 * (b2 * a32 - a22 * b3)
    )
    det_b = (
        a11 * (b2 * a33 - a23 * b3)
        - b1 * (a21 * a33 - a23 * a31)
        + a13 * (a21 * b3 - b2 * a31)
    )
    det_c = (
        a11 * (a22 * b3 - b2 * a32)
        - a12 * (a21 * b3 - b2 * a31)
        + b1 * (a21 * a32 - a22 * a31)
    )
    return det_a / det, det_b / det, det_c / det


def polyval(coeffs: Optional[Tuple[float, float, float]], x: float) -> float:
    if coeffs is None:
        return 0.18
    a, b, c = coeffs
    return a * x * x + b * x + c


def repair_call_slice(rows: List[dict], spot: float) -> Tuple[Dict[str, dict], dict]:
    if not rows:
        return {}, {"repair_count": 0}

    ordered = sorted(rows, key=lambda row: row["strike"])
    repaired: List[dict] = []
    repair_count = 0
    running_max = float("inf")
    for row in ordered:
        strike = float(row["strike"])
        intrinsic = max(spot - strike, 0.0)
        guarded = max(float(row["raw_price"]), intrinsic + 1e-3)
        clipped = min(guarded, running_max)
        if abs(clipped - float(row["raw_price"])) > 1e-8:
            repair_count += 1
        running_max = clipped
        repaired.append(
            {
                **row,
                "repaired_price": clipped,
                "repair_amount": clipped - float(row["raw_price"]),
                "repaired_flag": abs(clipped - float(row["raw_price"])) > 1e-8,
            }
        )

    if len(repaired) >= 3:
        for idx in range(1, len(repaired) - 1):
            left = repaired[idx - 1]["repaired_price"]
            mid = repaired[idx]["repaired_price"]
            right = repaired[idx + 1]["repaired_price"]
            floor = 0.5 * (left + right) - max(1.0, 0.001 * spot)
            if mid < floor:
                repaired[idx]["repaired_price"] = floor
                repaired[idx]["repair_amount"] = floor - float(repaired[idx]["raw_price"])
                repaired[idx]["repaired_flag"] = True
                repair_count += 1

    return {row["product"]: row for row in repaired}, {"repair_count": repair_count}


def generic_underlying_fair(product: str, od: OrderDepth, overlay: float, cfg: dict) -> float:
    stable = stable_mid(od)
    mid = raw_mid(od)
    micro = micro_price(od)
    if stable is None:
        stable = mid if mid is not None else cfg["anchor"]
    if mid is None:
        mid = stable
    if micro is None:
        micro = stable
    imbalance = book_imbalance(od)
    fair = (
        cfg["anchor_w"] * cfg["anchor"]
        + cfg["stable_w"] * stable
        + cfg["micro_w"] * micro
        + cfg["imbalance_w"] * imbalance
        + overlay
    )
    return float(fair)


def trade_underlying(product: str, state: TradingState, fair: float, target: float, cfg: dict, quote_bias: float = 0.0, take_bias: float = 0.0, size_mult: float = 1.0) -> List[Order]:
    od = state.order_depths[product]
    limit = LIMITS[product]
    mgr = OrderManager(product, state.position.get(product, 0), limit)
    bb = best_bid(od)
    ba = best_ask(od)
    spread = float((ba - bb) if bb is not None and ba is not None else 2.0)
    pos = int(state.position.get(product, 0))

    take_edge = cfg["take_edge"] + 0.10 * max(0.0, spread - 2.0)
    clear_edge = cfg["clear_edge"] + 0.05 * max(0.0, spread - 2.0)

    if ba is not None and fair - ba + take_bias >= take_edge and pos < limit:
        mgr.buy(ba, min(-od.sell_orders[ba], cfg["take_max"]))
    if bb is not None and bb - fair - take_bias >= take_edge and pos > -limit:
        mgr.sell(bb, min(od.buy_orders[bb], cfg["take_max"]))

    pos = mgr.projected()
    soft_limit = cfg["soft_limit"]
    if pos > soft_limit and bb is not None and bb >= fair - clear_edge:
        mgr.sell(bb, min(pos - soft_limit, cfg["clear_max"]))
    elif pos < -soft_limit and ba is not None and ba <= fair + clear_edge:
        mgr.buy(ba, min((-soft_limit) - pos, cfg["clear_max"]))

    pos = mgr.projected()
    inv_ratio = pos / float(limit)
    reservation = fair + quote_bias - cfg["inv_skew"] * inv_ratio
    quote_edge = cfg["quote_edge"] + 0.10 * max(0.0, spread - 3.0)
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

    quote_size = max(6, int(round(cfg["quote_size"] * max(0.25, 1.0 - abs(inv_ratio)) * size_mult)))
    if mgr.buy_cap > 0 and (ba is None or buy_px < ba):
        mgr.buy(buy_px, quote_size)
    if mgr.sell_cap > 0 and (bb is None or sell_px > bb):
        mgr.sell(sell_px, quote_size)
    return mgr.flush()


class HydrogelEngine:
    def build(self, state: TradingState, memory: dict) -> Tuple[float, dict]:
        od = state.order_depths[HYDROGEL]
        fair = generic_underlying_fair(HYDROGEL, od, 0.0, HYDRO_CFG)
        mid = raw_mid(od) or stable_mid(od) or fair
        spread = float((best_ask(od) - best_bid(od)) if best_bid(od) is not None and best_ask(od) is not None else 3.0)
        signal = (fair - mid) / max(1.0, 0.5 * spread)
        target = int(round(clamp(140.0 * math.tanh(0.75 * signal), -140.0, 140.0)))
        progress = float(state.timestamp % 100000) / 100000.0
        if progress > 0.85:
            target = int(round(0.75 * target))
        return fair, {"mid": mid, "signal": signal, "target": target, "progress": progress}

    def trade(self, state: TradingState, fair: float, ctx: dict) -> List[Order]:
        return trade_underlying(HYDROGEL, state, fair, ctx["target"], HYDRO_CFG)


class VelvetEngine:
    def build(self, state: TradingState, memory: dict, strip_risk: Optional[dict]) -> Tuple[float, dict]:
        od = state.order_depths[VELVET]
        fair = generic_underlying_fair(VELVET, od, 0.0, VELVET_CFG)
        mid = raw_mid(od) or stable_mid(od) or fair
        spread = float((best_ask(od) - best_bid(od)) if best_bid(od) is not None and best_ask(od) is not None else 2.0)
        alpha_signal = (fair - mid) / max(1.0, 0.5 * spread)

        hedge_ratio = 0.0
        hedge_target = 0
        if strip_risk and RESEARCH_FLAGS["velvet_hedge_book"]:
            strip_delta = float(strip_risk["strip_delta"])
            if abs(strip_delta) < 20.0:
                hedge_ratio = 0.0
                hedge_target = 0
            else:
                hedge_ratio = 0.25
                if bool(strip_risk["broad_dislocation"]):
                    hedge_ratio = 0.75
                elif abs(strip_delta) > 80.0:
                    hedge_ratio = 0.50
                if bool(strip_risk["resid_compression"]):
                    hedge_ratio = min(hedge_ratio, 0.35)
                hedge_target = int(round(clamp(-hedge_ratio * strip_delta, -100.0, 100.0)))

        alpha_cap = 0 if strip_risk and abs(float(strip_risk["strip_delta"])) > 90.0 else 30
        alpha_target = int(round(clamp(30.0 * math.tanh(0.70 * alpha_signal), -float(alpha_cap), float(alpha_cap))))
        target = int(round(clamp(float(hedge_target + alpha_target), -100.0, 100.0)))
        return fair, {
            "mid": mid,
            "alpha_signal": alpha_signal,
            "hedge_ratio": hedge_ratio,
            "hedge_target": hedge_target,
            "alpha_target": alpha_target,
            "target": target,
        }

    def trade(self, state: TradingState, fair: float, ctx: dict) -> List[Order]:
        quote_bias = -0.12 * clamp(ctx["alpha_signal"], -1.0, 1.0)
        take_bias = 0.08 * clamp(ctx["alpha_signal"], -1.0, 1.0)
        size_mult = 1.0 if abs(ctx["hedge_target"]) < 70 else 0.90
        return trade_underlying(VELVET, state, fair, ctx["target"], VELVET_CFG, quote_bias=quote_bias, take_bias=take_bias, size_mult=size_mult)


class VoucherStripEngine:
    def build_surface(self, state: TradingState, velvet_fair: float, memory: dict) -> Dict[str, dict]:
        vev_state = memory["voucher"]
        rolling_iv_state = vev_state.setdefault("rolling_iv", {})
        rows_mid: List[dict] = []
        rows_bid: List[dict] = []
        rows_ask: List[dict] = []

        for product, strike in VOUCHER_STRIKES.items():
            od = state.order_depths.get(product)
            if od is None:
                continue
            bb = best_bid(od)
            ba = best_ask(od)
            mid = raw_mid(od)
            if mid is None:
                mid = stable_mid(od)
            if mid is None:
                continue
            spread = float((ba - bb) if bb is not None and ba is not None else 4.0)
            liquidity = 0.0
            if bb is not None:
                liquidity += max(0, od.buy_orders.get(bb, 0))
            if ba is not None:
                liquidity += abs(od.sell_orders.get(ba, 0))
            row = {
                "product": product,
                "strike": strike,
                "raw_price": float(mid),
                "spread": spread,
                "liquidity": float(liquidity),
            }
            rows_mid.append(row)
            if bb is not None:
                rows_bid.append({**row, "raw_price": float(bb)})
            if ba is not None:
                rows_ask.append({**row, "raw_price": float(ba)})

        repaired_mid, repair_mid = repair_call_slice(rows_mid, velvet_fair)
        repaired_bid, repair_bid = repair_call_slice(rows_bid, velvet_fair)
        repaired_ask, repair_ask = repair_call_slice(rows_ask, velvet_fair)

        xs: List[float] = []
        ys_mid: List[float] = []
        ys_bid: List[float] = []
        ys_ask: List[float] = []
        ws: List[float] = []
        strike_rows: Dict[str, dict] = {}

        for product, row in repaired_mid.items():
            strike = float(row["strike"])
            k = math.log(strike / velvet_fair) / math.sqrt(TTE_YEARS)
            mid_iv = implied_vol_call(float(row["repaired_price"]), velvet_fair, strike, TTE_YEARS)
            if not (1e-6 < mid_iv < 3.0):
                continue
            bid_row = repaired_bid.get(product)
            ask_row = repaired_ask.get(product)
            bid_iv = None if bid_row is None else implied_vol_call(float(bid_row["repaired_price"]), velvet_fair, strike, TTE_YEARS)
            ask_iv = None if ask_row is None else implied_vol_call(float(ask_row["repaired_price"]), velvet_fair, strike, TTE_YEARS)
            weight = clamp((math.log1p(float(row["liquidity"])) + 0.5) / max(1.0, float(row["spread"])), 0.4, 4.0)
            xs.append(k)
            ys_mid.append(mid_iv)
            ys_bid.append(mid_iv if bid_iv is None or not (1e-6 < bid_iv < 3.0) else bid_iv)
            ys_ask.append(mid_iv if ask_iv is None or not (1e-6 < ask_iv < 3.0) else ask_iv)
            ws.append(weight)
            strike_rows[product] = {
                "strike": int(strike),
                "moneyness": k,
                "market_mid": float(row["raw_price"]),
                "market_iv": mid_iv,
                "market_bid_iv": None if bid_iv is None or not (1e-6 < bid_iv < 3.0) else bid_iv,
                "market_ask_iv": None if ask_iv is None or not (1e-6 < ask_iv < 3.0) else ask_iv,
                "spread": float(row["spread"]),
                "liquidity": float(row["liquidity"]),
            }

        coeff_mid = fit_quadratic_weighted(xs, ys_mid, ws) if len(xs) >= 3 else None
        coeff_bid = fit_quadratic_weighted(xs, ys_bid, ws) if len(xs) >= 3 else None
        coeff_ask = fit_quadratic_weighted(xs, ys_ask, ws) if len(xs) >= 3 else None
        model = "quadratic" if coeff_mid is not None else "flat"
        fit_resid = 0.0
        if coeff_mid is not None and xs:
            fit_resid = sum(w * (polyval(coeff_mid, x) - y) ** 2 for x, y, w in zip(xs, ys_mid, ws))
        smile_stability = clamp(
            0.50 * clamp(len(xs) / 8.0, 0.0, 1.0)
            + 0.30 * clamp(1.0 - fit_resid / 0.03, 0.0, 1.0)
            + 0.20 * clamp(1.0 - repair_mid["repair_count"] / max(1.0, float(len(xs) or 1)), 0.0, 1.0),
            0.0,
            1.0,
        )

        surface: Dict[str, dict] = {
            "_fit_diag": {
                "model": model,
                "usable_strikes": len(xs),
                "fit_resid": round(float(fit_resid), 8),
                "bid_sparse": len(repaired_bid) < 4,
                "ask_sparse": len(repaired_ask) < 4,
            },
            "_repair_diag": {
                "mid_repair_count": repair_mid["repair_count"],
                "bid_repair_count": repair_bid["repair_count"],
                "ask_repair_count": repair_ask["repair_count"],
            },
            "_smile_stability": smile_stability,
        }

        for product, strike in VOUCHER_STRIKES.items():
            if product not in strike_rows:
                continue
            row = strike_rows[product]
            x = float(row["moneyness"])
            struct_iv = clamp(polyval(coeff_mid, x), 1e-4, 3.0) if coeff_mid is not None else 0.18
            fair_bid_iv = struct_iv if coeff_bid is None else clamp(polyval(coeff_bid, x), 1e-4, 3.0)
            fair_ask_iv = struct_iv if coeff_ask is None else clamp(polyval(coeff_ask, x), 1e-4, 3.0)
            rolling_prev = float(rolling_iv_state.get(product, row["market_iv"]))
            rolling_iv = 0.82 * rolling_prev + 0.18 * float(row["market_iv"])
            rolling_iv_state[product] = rolling_iv

            if RESEARCH_FLAGS["voucher_hybrid_iv"]:
                struct_w = 0.75
                local_w = 0.25
                if smile_stability < 0.65:
                    struct_w = 0.55
                    local_w = 0.45
                hybrid_iv = clamp(struct_w * struct_iv + local_w * rolling_iv, 1e-4, 3.0)
            else:
                hybrid_iv = struct_iv

            surface[product] = {
                **row,
                "struct_iv_fair": struct_iv,
                "fair_mid_iv": hybrid_iv,
                "fair_bid_iv": min(hybrid_iv, fair_bid_iv),
                "fair_ask_iv": max(hybrid_iv, fair_ask_iv),
                "rolling_iv": rolling_iv,
                "fair": black_scholes_call(velvet_fair, strike, TTE_YEARS, hybrid_iv),
                "fair_bid": black_scholes_call(velvet_fair, strike, TTE_YEARS, min(hybrid_iv, fair_bid_iv)),
                "fair_ask": black_scholes_call(velvet_fair, strike, TTE_YEARS, max(hybrid_iv, fair_ask_iv)),
                "delta": black_scholes_delta_call(velvet_fair, strike, TTE_YEARS, hybrid_iv),
                "vega_proxy": black_scholes_vega_proxy(velvet_fair, strike, TTE_YEARS, hybrid_iv),
                "iv_residual": float(row["market_iv"]) - hybrid_iv,
            }
        return surface

    def build_risk(self, state: TradingState, surface: Dict[str, dict], memory: dict) -> dict:
        products = [product for product in VOUCHER_STRIKES if product in surface]
        liquid = [product for product in products if surface[product]["liquidity"] >= 10.0 and surface[product]["market_mid"] > 0.5]
        residuals = sorted(((product, float(surface[product]["iv_residual"])) for product in liquid), key=lambda item: item[1])
        avg_abs_resid = sum(abs(resid) for _, resid in residuals) / max(1, len(residuals))
        last_avg = float(memory["voucher"].get("last_avg_abs_resid", 0.0))
        resid_compression = last_avg > 1e-6 and avg_abs_resid < 0.70 * last_avg
        memory["voucher"]["last_avg_abs_resid"] = avg_abs_resid

        positions = {product: int(state.position.get(product, 0)) for product in VOUCHER_STRIKES}
        strip_delta = 0.0
        middle_abs = 0
        middle_net = 0
        for product in products:
            pos = positions[product]
            delta = float(surface[product]["delta"])
            strip_delta += pos * delta
            if 0.20 <= delta <= 0.80:
                middle_abs += abs(pos)
                middle_net += pos

        pair_targets = {product: 0 for product in VOUCHER_STRIKES}
        pair_bias = {product: 0 for product in VOUCHER_STRIKES}
        pair_candidates: List[dict] = []
        ordered = sorted(VOUCHER_STRIKES, key=VOUCHER_STRIKES.get)
        for idx, left in enumerate(ordered):
            if left not in liquid:
                continue
            for right in ordered[idx + 1 : min(len(ordered), idx + 4)]:
                if right not in liquid:
                    continue
                left_resid = float(surface[left]["iv_residual"])
                right_resid = float(surface[right]["iv_residual"])
                cheap, rich = (left, right) if left_resid <= right_resid else (right, left)
                cheap_resid = float(surface[cheap]["iv_residual"])
                rich_resid = float(surface[rich]["iv_residual"])
                spread = rich_resid - cheap_resid
                if spread <= 0.0:
                    continue
                pair_delta = abs(float(surface[cheap]["delta"]) - float(surface[rich]["delta"]))
                pair_candidates.append(
                    {
                        "cheap": cheap,
                        "rich": rich,
                        "spread": spread,
                        "score": spread - 0.15 * pair_delta,
                    }
                )

        pair_candidates.sort(key=lambda item: item["score"], reverse=True)
        used: set[str] = set()
        for pair in pair_candidates[:2]:
            cheap = str(pair["cheap"])
            rich = str(pair["rich"])
            if cheap in used or rich in used:
                continue
            if float(pair["spread"]) < max(0.075, 1.30 * avg_abs_resid):
                continue
            qty = 22 if VOUCHER_STRIKES[cheap] <= 5000 and VOUCHER_STRIKES[rich] <= 5100 else 16
            pair_targets[cheap] += qty
            pair_targets[rich] -= qty
            pair_bias[cheap] += 1
            pair_bias[rich] -= 1
            used.add(cheap)
            used.add(rich)

        pair_agreement_count = 0
        for left, right in zip(ordered, ordered[1:]):
            if left not in liquid or right not in liquid:
                continue
            left_resid = float(surface[left]["iv_residual"])
            right_resid = float(surface[right]["iv_residual"])
            if left_resid <= 0.0 <= right_resid or right_resid <= 0.0 <= left_resid:
                pair_agreement_count += 1

        broad_dislocation = (
            RESEARCH_FLAGS["voucher_shock_mode"]
            and avg_abs_resid > max(0.070, 1.05 * max(0.04, avg_abs_resid))
            and pair_agreement_count >= 4
            and abs(strip_delta) < 120.0
            and middle_abs < 150
        )

        hedge_feasible_size_score = clamp(
            0.55 * clamp(1.0 - abs(strip_delta) / 150.0, 0.0, 1.0)
            + 0.45 * clamp(1.0 - middle_abs / 170.0, 0.0, 1.0),
            0.0,
            1.0,
        )

        return {
            "strip_delta": strip_delta,
            "middle_abs": middle_abs,
            "middle_net": middle_net,
            "avg_abs_resid": avg_abs_resid,
            "resid_compression": resid_compression,
            "richest_strikes": [product for product, _ in residuals[-3:][::-1]],
            "cheapest_strikes": [product for product, _ in residuals[:3]],
            "pair_targets": pair_targets,
            "pair_bias": pair_bias,
            "pair_agreement_count": pair_agreement_count,
            "pair_candidates": pair_candidates[:5],
            "broad_dislocation": broad_dislocation,
            "hedge_feasible_size_score": hedge_feasible_size_score,
            "resid_threshold": max(0.035, 0.85 * max(0.04, avg_abs_resid)),
            "extreme_threshold": max(0.060, 1.50 * max(0.04, avg_abs_resid)),
            "feasible_caps": {
                product: int(
                    clamp(
                        (85 if VOUCHER_STRIKES[product] <= 5000 else 70) * (0.80 + 0.30 * hedge_feasible_size_score),
                        35.0,
                        90.0,
                    )
                )
                for product in VOUCHER_STRIKES
            },
        }

    def apply_quick_scalp(self, state: TradingState, surface: Dict[str, dict], risk: dict, memory: dict) -> dict:
        # Quick-trading overlay: small low-strike pair scalp with explicit
        # activation, normalization exit, and compact memory.
        scalp_state = memory["voucher"].setdefault(
            "quick_scalp",
            {
                "active": False,
                "cheap": "",
                "rich": "",
                "entry_spread": 0.0,
                "age": 0,
            },
        )
        scalp_targets = {product: 0 for product in VOUCHER_STRIKES}
        low_lane = [product for product in ("VEV_4000", "VEV_4500", "VEV_5000", "VEV_5100") if product in surface]
        liquid_low = [
            product
            for product in low_lane
            if float(surface[product]["liquidity"]) >= 10.0 and float(surface[product]["market_mid"]) > 0.5
        ]
        ranked = sorted(liquid_low, key=lambda product: float(surface[product]["iv_residual"]))
        progress = float(state.timestamp % 100000) / 100000.0
        active = bool(scalp_state.get("active", False))
        cheap = str(scalp_state.get("cheap", ""))
        rich = str(scalp_state.get("rich", ""))
        current_spread = 0.0
        if cheap in surface and rich in surface:
            current_spread = float(surface[rich]["iv_residual"]) - float(surface[cheap]["iv_residual"])

        pair_key = ""
        if ranked:
            pair_key = f"{ranked[0]}->{ranked[-1]}"

        if active and cheap in surface and rich in surface:
            scalp_state["age"] = int(scalp_state.get("age", 0)) + 1
            exit_threshold = max(0.025, 0.45 * float(scalp_state.get("entry_spread", 0.0)))
            signs_ok = float(surface[cheap]["iv_residual"]) <= 0.0 <= float(surface[rich]["iv_residual"])
            if (
                current_spread <= exit_threshold
                or not signs_ok
                or progress > 0.88
                or int(scalp_state.get("age", 0)) > 18
            ):
                scalp_state.update({"active": False, "cheap": "", "rich": "", "entry_spread": 0.0, "age": 0})
            else:
                qty = 14 if VOUCHER_STRIKES[cheap] <= 5000 and VOUCHER_STRIKES[rich] <= 5000 else 10
                scalp_targets[cheap] += qty
                scalp_targets[rich] -= qty
        elif RESEARCH_FLAGS["voucher_quick_scalp"] and len(ranked) >= 2 and progress < 0.84:
            cheapest = ranked[0]
            richest = ranked[-1]
            cheapest_resid = float(surface[cheapest]["iv_residual"])
            richest_resid = float(surface[richest]["iv_residual"])
            spread = richest_resid - cheapest_resid
            liquidity_ok = min(float(surface[cheapest]["liquidity"]), float(surface[richest]["liquidity"])) >= 12.0
            safe_strip = abs(float(risk["strip_delta"])) < 105.0 and int(risk["middle_abs"]) < 145
            if (
                liquidity_ok
                and safe_strip
                and cheapest_resid < -max(0.045, 0.95 * float(risk["resid_threshold"]))
                and richest_resid > max(0.045, 0.95 * float(risk["resid_threshold"]))
                and spread > max(0.11, 1.40 * float(risk["avg_abs_resid"]))
            ):
                scalp_state.update(
                    {
                        "active": True,
                        "cheap": cheapest,
                        "rich": richest,
                        "entry_spread": spread,
                        "age": 0,
                    }
                )
                qty = 14 if VOUCHER_STRIKES[cheapest] <= 5000 and VOUCHER_STRIKES[richest] <= 5000 else 10
                scalp_targets[cheapest] += qty
                scalp_targets[richest] -= qty
                current_spread = spread
                pair_key = f"{cheapest}->{richest}"

        # Merge scalp intent into the existing strip book conservatively.
        for product, qty in scalp_targets.items():
            if qty != 0:
                risk["pair_targets"][product] = int(risk["pair_targets"].get(product, 0)) + int(qty)
                risk["pair_bias"][product] = int(clamp(float(risk["pair_bias"].get(product, 0)) + math.copysign(1.0, qty), -2.0, 2.0))

        risk["scalp_targets"] = scalp_targets
        risk["quick_scalp"] = {
            "active": bool(scalp_state.get("active", False)),
            "pair": pair_key,
            "spread": round(float(current_spread), 4),
            "age": int(scalp_state.get("age", 0)),
        }
        return risk

    def trade_product(self, product: str, state: TradingState, ctx: dict, risk: dict) -> List[Order]:
        od = state.order_depths[product]
        mgr = OrderManager(product, state.position.get(product, 0), LIMITS[product])
        fair = float(ctx["fair"])
        fair_bid = float(ctx["fair_bid"])
        fair_ask = float(ctx["fair_ask"])
        iv_residual = float(ctx["iv_residual"])
        delta = float(ctx["delta"])
        bb = best_bid(od)
        ba = best_ask(od)
        spread = float((ba - bb) if bb is not None and ba is not None else 2.0)
        pair_target = int(risk["pair_targets"].get(product, 0))
        pair_bias = int(risk["pair_bias"].get(product, 0))
        scalp_target = int(risk.get("scalp_targets", {}).get(product, 0))
        scalp_active = bool(risk.get("quick_scalp", {}).get("active", False))
        cap = int(risk["feasible_caps"].get(product, 70))
        middle = 0.20 <= delta <= 0.80
        broad = bool(risk["broad_dislocation"])
        resid_threshold = float(risk["resid_threshold"])
        extreme_threshold = float(risk["extreme_threshold"])
        cheap_signal = max(0.0, -iv_residual)
        rich_signal = max(0.0, iv_residual)
        pair_confirmed = pair_target != 0 or pair_bias != 0 or scalp_target != 0

        take_edge = max(0.70, 0.35 * spread) + (0.25 if middle else 0.0) + (0.20 if not pair_confirmed else 0.0)
        if broad and pair_confirmed:
            take_edge = max(0.55, take_edge - 0.15)
        if scalp_target != 0:
            take_edge = max(0.50, take_edge - 0.12)

        take_max = 10 if middle else 16
        if pair_confirmed:
            take_max += 2
        if broad and pair_confirmed:
            take_max += 2
        if scalp_target != 0:
            take_max += 2

        if ba is not None:
            edge = fair_bid - ba + 0.15 * max(0, pair_bias)
            if pair_target > 0:
                edge += 0.15
            if scalp_target > 0:
                edge += 0.12
            if (pair_confirmed and edge >= take_edge) or (not pair_confirmed and cheap_signal >= extreme_threshold and edge >= take_edge + 0.4):
                mgr.buy(ba, min(-od.sell_orders[ba], take_max))

        if bb is not None:
            edge = bb - fair_ask + 0.15 * max(0, -pair_bias)
            if pair_target < 0:
                edge += 0.15
            if scalp_target < 0:
                edge += 0.12
            if (pair_confirmed and edge >= take_edge) or (not pair_confirmed and rich_signal >= extreme_threshold and edge >= take_edge + 0.4):
                mgr.sell(bb, min(od.buy_orders[bb], take_max))

        pos = mgr.projected()
        soft_limit = 80 if middle else 120
        clear_edge = max(0.35, 0.15 * spread)
        if pos > soft_limit and bb is not None and bb >= fair - clear_edge:
            mgr.sell(bb, min(pos - soft_limit, 32))
        elif pos < -soft_limit and ba is not None and ba <= fair + clear_edge:
            mgr.buy(ba, min((-soft_limit) - pos, 32))

        pos = mgr.projected()
        inv_ratio = pos / float(LIMITS[product])
        reservation = fair - (0.02 * max(25.0, fair) + 2.0) * inv_ratio + 0.10 * pair_bias + 0.004 * pair_target
        quote_edge = max(1.0, 0.45 * spread, 0.015 * max(20.0, fair))
        if middle:
            quote_edge += 0.35
        if not pair_confirmed:
            quote_edge += 0.20
        if broad and pair_confirmed:
            quote_edge = max(0.80, quote_edge - 0.08)
        if scalp_target != 0:
            quote_edge = max(0.78, quote_edge - 0.06)
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
        size_scale *= 0.82 + 0.18 * float(risk["hedge_feasible_size_score"])
        if middle:
            size_scale *= 0.45
        if pair_confirmed:
            size_scale *= 1.10
        if broad and pair_confirmed:
            size_scale *= 1.08
        if scalp_target != 0:
            size_scale *= 1.10
        if not pair_confirmed and abs(iv_residual) < resid_threshold:
            size_scale *= 0.70
        quote_size = max(4, int(round((14 if fair <= 100 else 9) * size_scale)))

        can_bid = mgr.buy_cap > 0 and pos < cap and (pair_confirmed or cheap_signal >= extreme_threshold)
        can_ask = mgr.sell_cap > 0 and pos > -cap and (pair_confirmed or rich_signal >= extreme_threshold)
        if not pair_confirmed and middle and abs(pos) >= 70:
            can_bid = False if pos > 0 else can_bid
            can_ask = False if pos < 0 else can_ask
        if scalp_active and scalp_target == 0:
            # When a scalp is active elsewhere, avoid inventing new unpaired adds
            # in unrelated strikes.
            if not pair_confirmed:
                can_bid = False
                can_ask = False

        if can_bid and (ba is None or buy_px < ba):
            mgr.buy(buy_px, quote_size)
        if can_ask and (bb is None or sell_px > bb):
            mgr.sell(sell_px, quote_size)
        return mgr.flush()


class Trader:
    """
    Round 3 restart base:
    - clean split between Hydrogel, Velvet, and voucher strip engines
    - frozen-simple Hydrogel baseline
    - hedge-first Velvet book
    - pair-first voucher strip baseline with simple side surfaces
    - compact diagnostics so we can restart research from competition intel
    """

    def _reset_day_if_needed(self, memory: dict, timestamp: int) -> None:
        current_day = int(timestamp // 1_000_000)
        if memory.get("day") != current_day:
            memory.clear()
            memory["day"] = current_day
            memory["engine_errors"] = {}
            memory["voucher"] = {
                "rolling_iv": {},
                "last_avg_abs_resid": 0.0,
                "quick_scalp": {"active": False, "cheap": "", "rich": "", "entry_spread": 0.0, "age": 0},
            }
            memory["diag"] = {}

    def run(self, state: TradingState):
        memory = load_memory(state.traderData)
        memory.setdefault("engine_errors", {})
        self._reset_day_if_needed(memory, state.timestamp)

        result: Dict[str, List[Order]] = {}
        conversions = 0
        hydro_engine = HydrogelEngine()
        velvet_engine = VelvetEngine()
        voucher_engine = VoucherStripEngine()

        if HYDROGEL in state.order_depths:
            try:
                hydro_fair, hydro_ctx = hydro_engine.build(state, memory)
                result[HYDROGEL] = hydro_engine.trade(state, hydro_fair, hydro_ctx)
                memory["diag"]["hydrogel"] = {
                    "fair": round(float(hydro_fair), 3),
                    "mid": round(float(hydro_ctx["mid"]), 3),
                    "signal": round(float(hydro_ctx["signal"]), 3),
                    "target": int(hydro_ctx["target"]),
                    "progress": round(float(hydro_ctx["progress"]), 3),
                }
            except Exception as exc:
                memory["engine_errors"]["hydrogel"] = type(exc).__name__

        if VELVET in state.order_depths:
            try:
                strip_risk = None
                voucher_surface = None
                velvet_fair, velvet_ctx = velvet_engine.build(state, memory, None)
                if all(product in state.order_depths for product in VOUCHER_STRIKES):
                    voucher_surface = voucher_engine.build_surface(state, velvet_fair, memory)
                    strip_risk = voucher_engine.build_risk(state, voucher_surface, memory)
                    strip_risk = voucher_engine.apply_quick_scalp(state, voucher_surface, strip_risk, memory)
                    velvet_fair, velvet_ctx = velvet_engine.build(state, memory, strip_risk)
                result[VELVET] = velvet_engine.trade(state, velvet_fair, velvet_ctx)
                memory["diag"]["velvet"] = {
                    "fair": round(float(velvet_fair), 3),
                    "target": int(velvet_ctx["target"]),
                    "hedge_ratio": round(float(velvet_ctx["hedge_ratio"]), 3),
                    "hedge_target": int(velvet_ctx["hedge_target"]),
                    "alpha_target": int(velvet_ctx["alpha_target"]),
                }
                if voucher_surface is not None and strip_risk is not None:
                    memory["diag"]["voucher_strip"] = {
                        "surface_model": str(voucher_surface["_fit_diag"]["model"]),
                        "usable_strikes": int(voucher_surface["_fit_diag"]["usable_strikes"]),
                        "smile_stability": round(float(voucher_surface["_smile_stability"]), 4),
                        "avg_abs_resid": round(float(strip_risk["avg_abs_resid"]), 4),
                        "strip_delta": round(float(strip_risk["strip_delta"]), 3),
                        "pair_agreement_count": int(strip_risk["pair_agreement_count"]),
                        "broad_dislocation": bool(strip_risk["broad_dislocation"]),
                        "resid_compression": bool(strip_risk["resid_compression"]),
                        "hedge_feasible_size_score": round(float(strip_risk["hedge_feasible_size_score"]), 4),
                        "richest_strikes": list(strip_risk["richest_strikes"]),
                        "cheapest_strikes": list(strip_risk["cheapest_strikes"]),
                        "pair_candidates": list(strip_risk["pair_candidates"]),
                        "quick_scalp": dict(strip_risk["quick_scalp"]),
                    }
                    memory["diag"]["voucher_targets"] = {
                        product: {
                            "pair_target": int(strip_risk["pair_targets"].get(product, 0)),
                            "pair_bias": int(strip_risk["pair_bias"].get(product, 0)),
                            "iv_residual": round(float(voucher_surface[product]["iv_residual"]), 4),
                            "fair_mid_iv": round(float(voucher_surface[product]["fair_mid_iv"]), 4),
                            "fair_bid_iv": round(float(voucher_surface[product]["fair_bid_iv"]), 4),
                            "fair_ask_iv": round(float(voucher_surface[product]["fair_ask_iv"]), 4),
                            "rolling_iv": round(float(voucher_surface[product]["rolling_iv"]), 4),
                            "delta": round(float(voucher_surface[product]["delta"]), 4),
                            "cap": int(strip_risk["feasible_caps"].get(product, LIMITS[product])),
                        }
                        for product in VOUCHER_STRIKES
                        if product in voucher_surface
                    }
                    for product in VOUCHER_STRIKES:
                        if product in state.order_depths and product in voucher_surface:
                            result[product] = voucher_engine.trade_product(product, state, voucher_surface[product], strip_risk)
            except Exception as exc:
                memory["engine_errors"]["velvet_voucher"] = type(exc).__name__

        return result, conversions, dump_memory(memory)
