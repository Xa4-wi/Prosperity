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

DOWN_TREND = "DOWN_TREND"
DOWN_UNWIND = "DOWN_UNWIND"
NEUTRAL = "NEUTRAL"
UP_UNWIND = "UP_UNWIND"
UP_TREND = "UP_TREND"

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


def solve_2x2(a: List[List[float]], b: List[float]) -> Optional[List[float]]:
    det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    if abs(det) < 1e-12:
        return None
    x0 = (b[0] * a[1][1] - a[0][1] * b[1]) / det
    x1 = (a[0][0] * b[1] - b[0] * a[1][0]) / det
    return [x0, x1]


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


def fit_weighted_line(xs: Sequence[float], ys: Sequence[float], ws: Sequence[float]) -> Optional[Tuple[float, float]]:
    if len(xs) != len(ys) or len(xs) != len(ws) or len(xs) < 2:
        return None
    safe_ws = [max(1e-6, float(w)) for w in ws]
    s0 = sum(safe_ws)
    s1 = sum(w * x for x, w in zip(xs, safe_ws))
    s2 = sum(w * x * x for x, w in zip(xs, safe_ws))
    t0 = sum(w * y for y, w in zip(ys, safe_ws))
    t1 = sum(w * x * y for x, y, w in zip(xs, ys, safe_ws))
    sol = solve_2x2([[s0, s1], [s1, s2]], [t0, t1])
    if sol is None:
        return None
    intercept, slope = float(sol[0]), float(sol[1])
    return intercept, slope


def svi_basis(k: float, m: float, sigma: float, rho: float) -> float:
    x = k - m
    return rho * x + math.sqrt(x * x + sigma * sigma)


def svi_total_variance(k: float, params: Tuple[float, float, float, float, float]) -> float:
    a, b, rho, m, sigma = params
    return a + b * svi_basis(k, m, sigma, rho)


def fit_svi_slice_weighted(
    ks: Sequence[float],
    total_vars: Sequence[float],
    ws: Sequence[float],
) -> Optional[dict]:
    if len(ks) != len(total_vars) or len(ks) != len(ws) or len(ks) < 4:
        return None

    k_min = min(ks)
    k_max = max(ks)
    k_span = max(0.08, k_max - k_min)
    rho_grid = [-0.85, -0.60, -0.35, -0.10, 0.15, 0.40, 0.65, 0.85]
    m_grid = [k_min - 0.15 * k_span + 0.18 * k_span * i for i in range(9)]
    sigma_grid = [0.01, 0.03, 0.06, 0.10, 0.16, 0.24]
    best: Optional[dict] = None

    def evaluate(rho: float, m: float, sigma: float) -> Optional[dict]:
        basis = [svi_basis(k, m, sigma, rho) for k in ks]
        line = fit_weighted_line(basis, total_vars, ws)
        if line is None:
            return None
        a, b = line
        if b <= 1e-8:
            return None
        params = (float(a), float(b), float(rho), float(m), float(sigma))
        fitted = [svi_total_variance(k, params) for k in ks]
        if min(fitted) <= 1e-8:
            return None
        sse = sum(max(1e-6, float(w)) * (fit - target) * (fit - target) for fit, target, w in zip(fitted, total_vars, ws))
        return {"params": params, "sse": float(sse)}

    for rho in rho_grid:
        for m in m_grid:
            for sigma in sigma_grid:
                candidate = evaluate(rho, m, sigma)
                if candidate is None:
                    continue
                if best is None or candidate["sse"] < best["sse"]:
                    best = candidate

    if best is None:
        return None

    _, _, best_rho, best_m, best_sigma = best["params"]
    refine_rho = [clamp(best_rho + delta, -0.95, 0.95) for delta in (-0.15, -0.08, 0.0, 0.08, 0.15)]
    refine_m = [best_m + delta * k_span for delta in (-0.10, -0.05, 0.0, 0.05, 0.10)]
    refine_sigma = [max(0.005, best_sigma * scale) for scale in (0.65, 0.85, 1.0, 1.20, 1.45)]
    for rho in refine_rho:
        for m in refine_m:
            for sigma in refine_sigma:
                candidate = evaluate(rho, m, sigma)
                if candidate is None:
                    continue
                if candidate["sse"] < best["sse"]:
                    best = candidate

    return best


def linear_interp(x0: float, y0: float, x1: float, y1: float, x: float) -> float:
    if abs(x1 - x0) < 1e-12:
        return 0.5 * (y0 + y1)
    weight = (x - x0) / (x1 - x0)
    return (1.0 - weight) * y0 + weight * y1


def repair_call_prices(
    quote_rows: List[dict],
    spot: float,
) -> Tuple[Dict[str, dict], dict]:
    if not quote_rows:
        return {}, {
            "repair_count": 0,
            "total_repair": 0.0,
            "max_repair": 0.0,
            "repaired_products": [],
        }

    rows = [dict(row) for row in sorted(quote_rows, key=lambda item: int(item["strike"]))]

    for row in rows:
        strike = float(row["strike"])
        intrinsic = max(spot - strike, 0.0)
        raw_mid = float(row["raw_mid"])
        guarded_price = max(raw_mid, intrinsic + 1e-3)
        row["intrinsic"] = intrinsic
        row["raw_guarded_price"] = guarded_price
        row["repaired_price"] = guarded_price
        row["repair_reasons"] = []

    # Pass 1: enforce monotonicity of call prices by strike.
    prev_price = float("inf")
    for row in rows:
        capped = min(float(row["repaired_price"]), prev_price)
        floored = max(float(row["intrinsic"]) + 1e-3, capped)
        if floored + 1e-9 < float(row["repaired_price"]):
            row["repaired_price"] = floored
            row["repair_reasons"].append("monotonic")
        prev_price = float(row["repaired_price"])

    # Pass 2: enforce a simple convexity upper bound with minimal downward repair.
    for _ in range(3):
        changed = False
        for idx in range(1, len(rows) - 1):
            left = rows[idx - 1]
            mid = rows[idx]
            right = rows[idx + 1]
            upper = linear_interp(
                float(left["strike"]),
                float(left["repaired_price"]),
                float(right["strike"]),
                float(right["repaired_price"]),
                float(mid["strike"]),
            )
            upper = min(upper, float(left["repaired_price"]))
            lower = max(float(mid["intrinsic"]) + 1e-3, float(right["repaired_price"]))
            if float(mid["repaired_price"]) > upper + 1e-9:
                mid["repaired_price"] = max(lower, upper)
                if "convexity" not in mid["repair_reasons"]:
                    mid["repair_reasons"].append("convexity")
                changed = True
        if not changed:
            break

    # Final monotonic cleanup after convexity clips.
    prev_price = float("inf")
    for row in rows:
        capped = min(float(row["repaired_price"]), prev_price)
        floored = max(float(row["intrinsic"]) + 1e-3, capped)
        row["repaired_price"] = floored
        prev_price = floored

    repaired_rows: Dict[str, dict] = {}
    repaired_products: List[str] = []
    total_repair = 0.0
    max_repair = 0.0
    for row in rows:
        repaired_price = float(row["repaired_price"])
        raw_guarded = float(row["raw_guarded_price"])
        repair_amount = repaired_price - raw_guarded
        row["repair_amount"] = repair_amount
        row["repaired_flag"] = abs(repair_amount) > 1e-9
        if row["repaired_flag"]:
            repaired_products.append(str(row["product"]))
            total_repair += abs(repair_amount)
            max_repair = max(max_repair, abs(repair_amount))
        repaired_rows[str(row["product"])] = row

    diagnostics = {
        "repair_count": len(repaired_products),
        "total_repair": round(total_repair, 6),
        "max_repair": round(max_repair, 6),
        "repaired_products": repaired_products,
    }
    return repaired_rows, diagnostics


class Trader:
    """
    Round 3 v43:
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
    - Step 12: convert Hydrogel unwind into a harder one-way exit state
      that suppresses same-side refills and steps the hold cap down over time
    - Step 13: keep Hydrogel frozen on the v28 trunk and restart the
      connected Velvet + voucher research with softer activation logic
    - Step 14: quote-clean voucher inputs before IV inversion and log
      the repair layer without changing the trading structure itself
    - Step 15: replace the weighted quadratic smile with a guarded
      single-slice SVI fit, with quadratic fallback if the slice is unstable
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
                "state": NEUTRAL,
                "fast_ema": None,
                "slow_ema": None,
                "local_fair_ema": None,
                "slow_fair_ema": None,
                "ret_ema": 0.0,
                "prev_mid": None,
                "up_peak_trend": 0.0,
                "down_peak_trend": 0.0,
                "up_peak_mid": None,
                "down_peak_mid": None,
                "unwind_cooldown": 0,
            },
        )
        memory.setdefault(
            "vev_voucher_state",
            {
                "last_avg_abs_resid": 0.0,
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

        spread = float((ba - bb) if bb is not None and ba is not None else 6.0)
        top_depth = 0.0
        if bb is not None:
            top_depth += float(max(0, od.buy_orders.get(bb, 0)))
        if ba is not None:
            top_depth += float(abs(od.sell_orders.get(ba, 0)))
        hydro_state = memory["hydro_state"]
        prev_fast = hydro_state.get("fast_ema")
        prev_slow = hydro_state.get("slow_ema")
        prev_local_fair = hydro_state.get("local_fair_ema")
        prev_slow_fair = hydro_state.get("slow_fair_ema")
        prev_last_mid = hydro_state.get("prev_mid")
        prev_ret_ema = float(hydro_state.get("ret_ema", 0.0))

        ema_fast = float(mid) if prev_fast is None else 0.38 * float(mid) + 0.62 * float(prev_fast)
        ema_slow = float(mid) if prev_slow is None else 0.10 * float(mid) + 0.90 * float(prev_slow)
        ret = 0.0 if prev_last_mid is None else float(mid) - float(prev_last_mid)
        ret_ema = 0.20 * ret + 0.80 * prev_ret_ema
        hydro_state["fast_ema"] = ema_fast
        hydro_state["slow_ema"] = ema_slow
        hydro_state["ret_ema"] = ret_ema
        hydro_state["prev_mid"] = float(mid)

        # Build a slower local-fair view, but use it only as an overlay inside the
        # phase engine so it cannot open opposite-side positions on its own.
        bid_wall, ask_wall = size_wall_prices(od, levels=3)
        wall_mid_val = raw_mid(od)
        if bid_wall is not None and ask_wall is not None and bid_wall < ask_wall:
            wall_mid_val = 0.5 * (bid_wall + ask_wall)
        if wall_mid_val is None:
            wall_mid_val = stable

        local_fair = 0.55 * float(stable) + 0.25 * float(wall_mid_val) + 0.20 * float(micro)
        local_fair_ema = float(local_fair) if prev_local_fair is None else 0.30 * float(local_fair) + 0.70 * float(prev_local_fair)
        slow_fair_anchor = 0.78 * float(local_fair_ema) + 0.22 * float(UNDERLYING_CFG[HYDROGEL]["anchor"])
        slow_fair_ema = float(slow_fair_anchor) if prev_slow_fair is None else 0.10 * float(slow_fair_anchor) + 0.90 * float(prev_slow_fair)
        hydro_state["local_fair_ema"] = local_fair_ema
        hydro_state["slow_fair_ema"] = slow_fair_ema

        signal = (fair - float(mid)) / max(1.0, 0.5 * spread)
        good_book = (
            bb is not None
            and ba is not None
            and bb < ba
            and spread <= 8.0
            and top_depth >= 12.0
            and abs(float(stable) - float(mid)) <= 1.4
        )

        anchor_gap = UNDERLYING_CFG[HYDROGEL]["anchor"] - float(mid)
        trend_gap = ema_fast - ema_slow
        micro_gap = float(micro) - float(mid)
        imbalance = book_imbalance(od, levels=2)
        local_gap = float(local_fair_ema) - float(mid)
        slow_gap = float(slow_fair_ema) - float(mid)

        anchor_score = clamp(anchor_gap / max(4.0, 0.80 * spread), -3.0, 3.0)
        trend_score = clamp(trend_gap / max(1.0, 0.55 * spread), -3.0, 3.0)
        flow_score = clamp(micro_gap / max(1.0, 0.5 * spread) + 0.90 * imbalance, -2.0, 2.0)
        fair_gap = (fair - float(mid)) / max(1.0, 0.5 * spread)
        local_score = clamp(local_gap / max(1.0, 0.55 * spread), -3.0, 3.0)
        slow_score = clamp(slow_gap / max(2.0, 0.90 * spread), -2.5, 2.5)
        progress = float(state.timestamp % 100000) / 100000.0
        state_name = str(hydro_state.get("state", NEUTRAL))
        unwind_cooldown = max(0, int(hydro_state.get("unwind_cooldown", 0)) - 1)
        up_peak_trend = float(hydro_state.get("up_peak_trend", 0.0))
        down_peak_trend = float(hydro_state.get("down_peak_trend", 0.0))
        up_peak_mid = float(hydro_state.get("up_peak_mid", mid) if hydro_state.get("up_peak_mid") is not None else mid)
        down_peak_mid = float(hydro_state.get("down_peak_mid", mid) if hydro_state.get("down_peak_mid") is not None else mid)

        if state_name == UP_TREND:
            up_peak_trend = max(up_peak_trend, trend_score)
            up_peak_mid = max(up_peak_mid, float(mid))
        elif state_name == DOWN_TREND:
            down_peak_trend = min(down_peak_trend if down_peak_trend != 0.0 else trend_score, trend_score)
            down_peak_mid = min(down_peak_mid, float(mid))

        long_drawdown = max(0.0, up_peak_mid - float(mid))
        short_drawup = max(0.0, float(mid) - down_peak_mid)
        long_trend_drop = max(0.0, up_peak_trend - trend_score)
        short_trend_rebound = max(0.0, trend_score - down_peak_trend) if down_peak_trend != 0.0 else 0.0

        strong_up = trend_score > 1.6 and ret_ema > 0.0 and fair_gap > 0.35 and good_book
        strong_down = trend_score < -1.6 and ret_ema < 0.0 and fair_gap < -0.35 and good_book
        strong_reconfirm_up = trend_score > 2.2 and ret_ema > 0.05 and fair_gap > 0.55 and good_book
        strong_reconfirm_down = trend_score < -2.2 and ret_ema < -0.05 and fair_gap < -0.55 and good_book
        neutral_zone = abs(trend_score) < 0.45 and abs(fair_gap) < 0.40
        # Local-fair is only allowed to help in the direction of the current state,
        # or to trigger an earlier unwind when the local deviation collapses.
        trend_pullback_up = local_score > 0.40 and ret_ema <= 0.15 and float(mid) <= ema_fast + 0.8
        trend_pullback_down = local_score < -0.40 and ret_ema >= -0.15 and float(mid) >= ema_fast - 0.8
        local_unwind_up = local_score < -0.10 or slow_score < -0.10
        local_unwind_down = local_score > 0.10 or slow_score > 0.10

        if state_name == UP_TREND:
            if (
                long_trend_drop > max(0.55, 0.30 * max(1.0, abs(up_peak_trend)))
                or ret_ema < -0.05
                or fair_gap < 0.15
                or (progress > 0.68 and local_unwind_up)
                or progress > 0.90
            ):
                state_name = UP_UNWIND
                unwind_cooldown = 6
        elif state_name == DOWN_TREND:
            if (
                short_trend_rebound > max(0.55, 0.30 * max(1.0, abs(down_peak_trend)))
                or ret_ema > 0.05
                or fair_gap > -0.15
                or (progress > 0.68 and local_unwind_down)
                or progress > 0.90
            ):
                state_name = DOWN_UNWIND
                unwind_cooldown = 6
        elif state_name == UP_UNWIND:
            if strong_reconfirm_up and unwind_cooldown == 0 and float(mid) >= up_peak_mid - 0.5:
                state_name = UP_TREND
                up_peak_trend = max(up_peak_trend, trend_score)
                up_peak_mid = max(up_peak_mid, float(mid))
            elif strong_down and unwind_cooldown == 0:
                state_name = DOWN_TREND
                down_peak_trend = trend_score
                down_peak_mid = float(mid)
            elif neutral_zone:
                state_name = NEUTRAL
        elif state_name == DOWN_UNWIND:
            if strong_reconfirm_down and unwind_cooldown == 0 and float(mid) <= down_peak_mid + 0.5:
                state_name = DOWN_TREND
                down_peak_trend = min(down_peak_trend if down_peak_trend != 0.0 else trend_score, trend_score)
                down_peak_mid = min(down_peak_mid, float(mid))
            elif strong_up and unwind_cooldown == 0:
                state_name = UP_TREND
                up_peak_trend = trend_score
                up_peak_mid = float(mid)
            elif neutral_zone:
                state_name = NEUTRAL
        else:
            if strong_up:
                state_name = UP_TREND
                up_peak_trend = trend_score
                up_peak_mid = float(mid)
            elif strong_down:
                state_name = DOWN_TREND
                down_peak_trend = trend_score
                down_peak_mid = float(mid)
            else:
                state_name = NEUTRAL

        hydro_state["state"] = state_name
        hydro_state["up_peak_trend"] = up_peak_trend
        hydro_state["down_peak_trend"] = down_peak_trend
        hydro_state["up_peak_mid"] = up_peak_mid
        hydro_state["down_peak_mid"] = down_peak_mid
        hydro_state["unwind_cooldown"] = unwind_cooldown

        current_pos = int(state.position.get(HYDROGEL, 0))
        target = 0
        state_bias = 0.0
        same_side_bid_block = False
        same_side_ask_block = False
        confidence = "neutral"
        entry_cap = 0
        hold_cap = 0
        buy_take_extra = 0.0
        sell_take_extra = 0.0

        if state_name == UP_TREND:
            confidence = "trend_up"
            cap = 100
            if trend_score > 2.0 and fair_gap > 0.45:
                cap = 120
            if trend_score > 2.5 and fair_gap > 0.70 and good_book:
                cap = 140
            if trend_score > 3.1 and fair_gap > 0.95 and good_book and progress < 0.72:
                cap = 170
            strength = clamp((0.65 * abs(trend_score) + 0.35 * abs(fair_gap)) / 2.8, 0.45, 1.0)
            target = int(round(cap * strength))
            if trend_pullback_up:
                target = min(cap, target + 18)
            entry_cap = cap
            hold_cap = min(cap, 120 if current_pos > 120 else cap)
            state_bias = 0.18
            same_side_ask_block = True
            sell_take_extra = 0.25
        elif state_name == DOWN_TREND:
            confidence = "trend_down"
            cap = 100
            if trend_score < -2.0 and fair_gap < -0.45:
                cap = 120
            if trend_score < -2.5 and fair_gap < -0.70 and good_book:
                cap = 140
            if trend_score < -3.1 and fair_gap < -0.95 and good_book and progress < 0.72:
                cap = 170
            strength = clamp((0.65 * abs(trend_score) + 0.35 * abs(fair_gap)) / 2.8, 0.45, 1.0)
            target = -int(round(cap * strength))
            if trend_pullback_down:
                target = max(-cap, target - 18)
            entry_cap = cap
            hold_cap = min(cap, 120 if current_pos < -120 else cap)
            state_bias = -0.18
            same_side_bid_block = True
            buy_take_extra = 0.25
        elif state_name == UP_UNWIND:
            confidence = "up_unwind"
            fade_score = (
                0.40 * clamp(long_trend_drop / max(0.80, 0.30 * max(1.0, abs(up_peak_trend))), 0.0, 1.5)
                + 0.25 * clamp(long_drawdown / 8.0, 0.0, 1.5)
                + 0.20 * clamp((0.15 - fair_gap) / 0.80, 0.0, 1.5)
                + 0.15 * clamp((-ret_ema) / 1.0, 0.0, 1.5)
            )
            target = 0 if (fade_score > 1.25 or progress > 0.94) else 30 if (fade_score > 0.80 or progress > 0.88) else 60
            entry_cap = 60
            hold_cap = 40
            state_bias = -0.10
            same_side_bid_block = True
            buy_take_extra = 0.45
            sell_take_extra = -0.10
        elif state_name == DOWN_UNWIND:
            confidence = "down_unwind"
            fade_score = (
                0.40 * clamp(short_trend_rebound / max(0.80, 0.30 * max(1.0, abs(down_peak_trend))), 0.0, 1.5)
                + 0.25 * clamp(short_drawup / 8.0, 0.0, 1.5)
                + 0.20 * clamp((fair_gap + 0.15) / 0.80, 0.0, 1.5)
                + 0.15 * clamp(ret_ema / 1.0, 0.0, 1.5)
            )
            target = 0 if (fade_score > 1.25 or progress > 0.94) else -30 if (fade_score > 0.80 or progress > 0.88) else -60
            entry_cap = 60
            hold_cap = 40
            state_bias = 0.10
            same_side_ask_block = True
            buy_take_extra = -0.10
            sell_take_extra = 0.45

        flatten_before_flip = False
        if current_pos * target < 0 and abs(current_pos) > 60:
            target = 0
            flatten_before_flip = True

        # Let the local-fair overlay nudge reservation price in-trend, but keep it
        # too small to become a standalone reversal driver.
        local_overlay = 0.0
        if state_name == UP_TREND and trend_pullback_up:
            local_overlay = clamp(3.0 * local_score, 0.0, 6.0)
        elif state_name == DOWN_TREND and trend_pullback_down:
            local_overlay = clamp(3.0 * local_score, -6.0, 0.0)

        fair_shift = clamp(10.0 * fair_gap + 6.0 * state_bias + local_overlay, -24.0, 24.0)
        size_mult = 0.95 if good_book else 0.70
        if state_name in {UP_UNWIND, DOWN_UNWIND}:
            size_mult *= 0.80
        elif state_name == NEUTRAL:
            size_mult *= 0.65
        if progress > 0.90:
            size_mult *= 0.88
        if trend_pullback_up or trend_pullback_down:
            size_mult *= 1.05

        return {
            "mid": float(mid),
            "signal": float(signal),
            "regime_score": float(0.55 * trend_score + 0.25 * anchor_score + 0.20 * flow_score),
            "trend_score": float(trend_score),
            "anchor_score": float(anchor_score),
            "flow_score": float(flow_score),
            "confidence": confidence,
            "entry_cap": int(entry_cap),
            "hold_cap": int(hold_cap),
            "entry_target": int(target),
            "hold_target": int(target),
            "target": int(clamp(float(target), -170.0, 170.0)),
            "good_book": good_book,
            "progress": progress,
            "extreme_hold_bars": 0,
            "flatten_before_flip": flatten_before_flip,
            "exit_mode": state_name if "UNWIND" in state_name else "",
            "exit_age": int(unwind_cooldown),
            "long_peak_score": float(up_peak_trend),
            "short_peak_score": float(down_peak_trend),
            "long_peak_trend": float(up_peak_trend),
            "short_peak_trend": float(down_peak_trend),
            "long_drawdown": float(long_drawdown),
            "short_drawup": float(short_drawup),
            "stretch_long": current_pos > 140,
            "stretch_short": current_pos < -140,
            "absolute_danger_long": current_pos >= 160,
            "absolute_danger_short": current_pos <= -160,
            "same_side_bid_block": same_side_bid_block,
            "same_side_ask_block": same_side_ask_block,
            "buy_take_extra": float(max(0.0, buy_take_extra)),
            "sell_take_extra": float(max(0.0, sell_take_extra)),
            "quote_bias": float(state_bias),
            "fair_shift": float(fair_shift),
            "size_mult": float(size_mult),
            "state": state_name,
            "unwind_cooldown": int(unwind_cooldown),
            "ret_ema": float(ret_ema),
            "local_fair": float(local_fair_ema),
            "slow_fair": float(slow_fair_ema),
            "local_score": float(local_score),
            "trend_pullback_up": bool(trend_pullback_up),
            "trend_pullback_down": bool(trend_pullback_down),
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
        state_name = str(hydro_ctx.get("state", NEUTRAL))
        unwind_long = state_name == UP_UNWIND
        unwind_short = state_name == DOWN_UNWIND
        same_side_bid_block = bool(hydro_ctx.get("same_side_bid_block", False))
        same_side_ask_block = bool(hydro_ctx.get("same_side_ask_block", False))
        absolute_danger_long = bool(hydro_ctx.get("absolute_danger_long", False))
        absolute_danger_short = bool(hydro_ctx.get("absolute_danger_short", False))
        trend_pullback_up = bool(hydro_ctx.get("trend_pullback_up", False))
        trend_pullback_down = bool(hydro_ctx.get("trend_pullback_down", False))
        buy_take_allowed = not (same_side_bid_block or current_pos >= 150)
        sell_take_allowed = not (same_side_ask_block or current_pos <= -150)

        buy_take_edge = cfg["take_edge"] + float(hydro_ctx["buy_take_extra"])
        sell_take_edge = cfg["take_edge"] + float(hydro_ctx["sell_take_extra"])
        if state_name == UP_TREND:
            buy_take_edge -= 0.20
            sell_take_edge += 0.25
            if trend_pullback_up:
                buy_take_edge -= 0.15
        elif state_name == DOWN_TREND:
            sell_take_edge -= 0.20
            buy_take_edge += 0.25
            if trend_pullback_down:
                sell_take_edge -= 0.15
        elif state_name == UP_UNWIND:
            buy_take_edge += 0.45
            sell_take_edge -= 0.10
        elif state_name == DOWN_UNWIND:
            sell_take_edge += 0.45
            buy_take_edge -= 0.10
        elif state_name == NEUTRAL:
            buy_take_edge += 0.10
            sell_take_edge += 0.10

        for ask, volume in sorted(od.sell_orders.items()):
            edge = fair - ask
            if not buy_take_allowed:
                break
            if edge >= buy_take_edge:
                mgr.buy(ask, min(-volume, cfg["take_max"]))
            else:
                break

        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            edge = bid - fair
            if not sell_take_allowed:
                break
            if edge >= sell_take_edge:
                mgr.sell(bid, min(volume, cfg["take_max"]))
            else:
                break

        pos = mgr.projected()
        relative_pos = pos - target
        soft_limit = 90
        clear_edge = cfg["clear_edge"]
        clear_max = cfg["clear_max"]
        if state_name in (UP_UNWIND, DOWN_UNWIND):
            soft_limit = 35
            clear_edge += 0.25
            clear_max = max(clear_max, 56)
        elif state_name == NEUTRAL:
            soft_limit = 55

        if relative_pos > soft_limit and bb is not None and (bb >= fair - clear_edge or unwind_long or absolute_danger_long):
            mgr.sell(bb, min(int(math.ceil(relative_pos - soft_limit)), clear_max))

        pos = mgr.projected()
        relative_pos = pos - target
        if relative_pos < -soft_limit and ba is not None and (ba <= fair + clear_edge or unwind_short or absolute_danger_short):
            mgr.buy(ba, min(int(math.ceil((-soft_limit) - relative_pos)), clear_max))

        pos = mgr.projected()
        relative_pos = pos - target
        inv_ratio = relative_pos / LIMITS[HYDROGEL]
        reservation = fair + float(hydro_ctx["quote_bias"]) - (cfg["inv_skew"] + 2.0) * inv_ratio
        quote_edge = cfg["quote_edge"] + max(0.0, 0.10 * (spread - 4.0))
        if state_name in (UP_UNWIND, DOWN_UNWIND):
            quote_edge += 0.15
        elif state_name == NEUTRAL:
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

        size_scale = max(0.20, 1.0 - abs(inv_ratio)) * max(0.35, float(hydro_ctx["size_mult"]))
        quote_size = cfg["quote_size"]
        if state_name in (UP_UNWIND, DOWN_UNWIND):
            quote_size = max(8, int(round(0.70 * quote_size)))
        elif state_name == NEUTRAL:
            quote_size = max(8, int(round(0.60 * quote_size)))
        quote_size = max(6, int(round(quote_size * size_scale)))

        can_bid = mgr.buy_cap > 0 and pos < target + max(20, quote_size)
        can_ask = mgr.sell_cap > 0 and pos > target - max(20, quote_size)
        if same_side_bid_block:
            can_bid = False
        if same_side_ask_block:
            can_ask = False
        if state_name == UP_TREND:
            can_ask = can_ask and pos > max(20, target - 35)
        elif state_name == DOWN_TREND:
            can_bid = can_bid and pos < min(-20, target + 35)

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
        points_k: List[float] = []
        strike_rows: Dict[str, dict] = {}
        raw_quote_rows: List[dict] = []

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

            raw_quote_rows.append(
                {
                    "product": product,
                    "strike": strike,
                    "raw_mid": float(market_mid),
                    "spread": spread,
                    "liquidity": liquidity,
                    "best_bid": float(bb) if bb is not None else None,
                    "best_ask": float(ba) if ba is not None else None,
                }
            )

        repaired_rows, repair_diag = repair_call_prices(raw_quote_rows, velvet_fair)
        for product, row in repaired_rows.items():
            k = math.log(float(row["strike"]) / velvet_fair)
            m = k / math.sqrt(TTE_YEARS)
            repaired_price = float(row["repaired_price"])
            market_iv = implied_vol_call(repaired_price, velvet_fair, float(row["strike"]), TTE_YEARS)
            if 1e-6 < market_iv < 3.0:
                strike_rows[product] = {
                    "strike": int(row["strike"]),
                    "log_moneyness": k,
                    "moneyness": m,
                    "market_mid": float(row["raw_mid"]),
                    "raw_guarded_price": float(row["raw_guarded_price"]),
                    "guarded_price": repaired_price,
                    "repaired_price": repaired_price,
                    "repair_amount": float(row["repair_amount"]),
                    "repaired_flag": bool(row["repaired_flag"]),
                    "repair_reasons": list(row["repair_reasons"]),
                    "market_iv": market_iv,
                    "spread": float(row["spread"]),
                    "liquidity": float(row["liquidity"]),
                }
                weight = clamp((math.log1p(float(row["liquidity"])) + 0.5) / float(row["spread"]), 0.4, 4.0)
                weight *= clamp(math.exp(-0.55 * abs(m)), 0.45, 1.0)
                weight *= 1.0 if not row["repaired_flag"] else 0.90
                points_k.append(k)
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

        fit_diag = {"model": "quadratic", "sse": None}
        coeffs = None
        svi_fit = None
        if clipped_ivs:
            total_vars = [iv * iv * TTE_YEARS for iv in clipped_ivs]
            if len(clipped_ivs) >= 4:
                svi_fit = fit_svi_slice_weighted(points_k, total_vars, points_w)
            if len(clipped_ivs) >= 3:
                coeffs = fit_quadratic_weighted(points_m, clipped_ivs, points_w)
            elif clipped_ivs:
                coeffs = (0.0, 0.0, float(sorted(clipped_ivs)[len(clipped_ivs) // 2]))
            else:
                coeffs = (0.0, 0.0, 0.18)

            if svi_fit is not None:
                params = svi_fit["params"]
                fitted_sigmas_svi = [math.sqrt(max(1e-8, svi_total_variance(k, params) / TTE_YEARS)) for k in points_k]
                svi_sse_sigma = sum(
                    max(1e-6, float(w)) * (fit - actual) * (fit - actual)
                    for fit, actual, w in zip(fitted_sigmas_svi, clipped_ivs, points_w)
                )
                fit_diag = {
                    "model": "svi",
                    "sse": round(float(svi_sse_sigma), 8),
                    "params": {
                        "a": round(float(params[0]), 8),
                        "b": round(float(params[1]), 8),
                        "rho": round(float(params[2]), 6),
                        "m": round(float(params[3]), 6),
                        "sigma": round(float(params[4]), 6),
                    },
                }
        else:
            coeffs = (0.0, 0.0, 0.18)

        fitted_sigmas: Dict[str, float] = {}
        for product, strike in VOUCHER_STRIKES.items():
            k = math.log(strike / velvet_fair)
            m = k / math.sqrt(TTE_YEARS)
            if svi_fit is not None:
                sigma = math.sqrt(max(1e-8, svi_total_variance(k, svi_fit["params"]) / TTE_YEARS))
            else:
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
                "raw_guarded_price": row.get("raw_guarded_price"),
                "guarded_price": row.get("guarded_price"),
                "repaired_price": row.get("repaired_price"),
                "repair_amount": float(row.get("repair_amount", 0.0)),
                "repaired_flag": bool(row.get("repaired_flag", False)),
                "repair_reasons": list(row.get("repair_reasons", [])),
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
        surface["_repair_diag"] = repair_diag
        surface["_fit_diag"] = fit_diag
        return surface

    def _build_voucher_risk_context(self, state: TradingState, surface: Dict[str, dict], memory: dict) -> dict:
        liquid_products = [
            product
            for product in VOUCHER_STRIKES
            if product in surface
            and surface[product].get("market_mid") is not None
            and float(surface[product]["market_mid"]) > 0.5
            and float(surface[product]["liquidity"]) >= 10.0
        ]
        residual_pairs = [(product, float(surface[product]["iv_residual"])) for product in liquid_products]
        resid_scale = max(0.04, sum(abs(resid) for _, resid in residual_pairs) / max(1, len(residual_pairs)))
        avg_abs_resid = sum(abs(resid) for _, resid in residual_pairs) / max(1, len(residual_pairs))

        pair_bias: Dict[str, int] = {}
        residual_rank: Dict[str, int] = {}
        pair_targets: Dict[str, int] = {product: 0 for product in VOUCHER_STRIKES}
        sorted_products = sorted(VOUCHER_STRIKES, key=VOUCHER_STRIKES.get)
        sorted_residuals = sorted(liquid_products, key=lambda product: float(surface[product]["iv_residual"]))
        for rank, product in enumerate(sorted_residuals):
            centered_rank = rank - (len(sorted_residuals) - 1) / 2.0
            residual_rank[product] = int(round(centered_rank))

        pair_agreement_count = 0
        for left, right in zip(sorted_products, sorted_products[1:]):
            left_ctx = surface[left]
            right_ctx = surface[right]
            if left not in liquid_products or right not in liquid_products:
                continue
            gap = float(right_ctx["iv_residual"]) - float(left_ctx["iv_residual"])
            if gap >= 0.07:
                pair_agreement_count += 1
                pair_bias[left] = pair_bias.get(left, 0) + 1
                pair_bias[right] = pair_bias.get(right, 0) - 1
                pair_targets[left] += 14 if 0.20 <= float(left_ctx["delta"]) <= 0.80 else 18
                pair_targets[right] -= 14 if 0.20 <= float(right_ctx["delta"]) <= 0.80 else 18
            elif gap <= -0.07:
                pair_agreement_count += 1
                pair_bias[left] = pair_bias.get(left, 0) - 1
                pair_bias[right] = pair_bias.get(right, 0) + 1
                pair_targets[left] -= 14 if 0.20 <= float(left_ctx["delta"]) <= 0.80 else 18
                pair_targets[right] += 14 if 0.20 <= float(right_ctx["delta"]) <= 0.80 else 18

        strip_delta = 0.0
        strip_vega = 0.0
        middle_abs = 0
        middle_net = 0
        middle_long_gross = 0
        middle_short_gross = 0
        low_wing_net = 0
        high_wing_net = 0
        adjacent_same_side_max = 0
        adjacent_same_side_products: List[str] = []
        positions = {product: int(state.position.get(product, 0)) for product in VOUCHER_STRIKES}

        for product in VOUCHER_STRIKES:
            ctx = surface.get(product)
            if ctx is None:
                continue
            pos = positions[product]
            delta = float(ctx["delta"])
            strip_delta += pos * delta
            strip_vega += pos * float(ctx["vega_proxy"])
            if 0.20 <= delta <= 0.80:
                middle_abs += abs(pos)
                middle_net += pos
                if pos > 0:
                    middle_long_gross += pos
                elif pos < 0:
                    middle_short_gross += abs(pos)
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

        middle_cap = 170
        total_delta_cap = 150.0
        broad_dislocation = (
            avg_abs_resid > max(0.07, 1.05 * resid_scale)
            and pair_agreement_count >= 4
            and abs(strip_delta) < 0.80 * total_delta_cap
            and middle_abs < 0.80 * middle_cap
        )
        vev_state = memory["vev_voucher_state"]
        last_avg_abs_resid = float(vev_state.get("last_avg_abs_resid", 0.0))
        resid_compression = last_avg_abs_resid > 1e-6 and avg_abs_resid < 0.70 * last_avg_abs_resid
        vev_state["last_avg_abs_resid"] = avg_abs_resid
        cheapest = list(sorted_residuals[:3])
        richest = list(sorted_residuals[-3:][::-1])

        return {
            "resid_scale": resid_scale,
            "avg_abs_resid": avg_abs_resid,
            "resid_threshold": max(0.035, 0.85 * resid_scale),
            "extreme_resid_threshold": max(0.060, 1.50 * resid_scale),
            "pair_bias": pair_bias,
            "pair_targets": pair_targets,
            "pair_agreement_count": pair_agreement_count,
            "residual_rank": residual_rank,
            "strip_delta": strip_delta,
            "strip_vega_proxy": strip_vega,
            "delta_pressure": clamp(strip_delta / 140.0, -2.0, 2.0),
            "target_velvet_pos": int(round(clamp(-0.50 * strip_delta, -100.0, 100.0))),
            "middle_abs": middle_abs,
            "middle_net": middle_net,
            "middle_long_gross": middle_long_gross,
            "middle_short_gross": middle_short_gross,
            "middle_same_side_gross": max(middle_long_gross, middle_short_gross),
            "middle_cap": middle_cap,
            "adjacent_same_side_max": adjacent_same_side_max,
            "adjacent_same_side_products": adjacent_same_side_products,
            "adjacent_cap": 170,
            "low_wing_net": low_wing_net,
            "high_wing_net": high_wing_net,
            "total_delta_cap": total_delta_cap,
            "unconfirmed_outright_cap": 85,
            "broad_dislocation": broad_dislocation,
            "resid_compression": resid_compression,
            "cheapest_strikes": cheapest,
            "richest_strikes": richest,
        }

    def _build_velvet_context(self, state: TradingState, velvet_fair: float, risk_ctx: dict) -> dict:
        od = state.order_depths[VELVET]
        bb = best_bid(od)
        ba = best_ask(od)
        mid = raw_mid(od)
        if mid is None:
            mid = stable_mid(od)
        if mid is None:
            mid = velvet_fair
        spread = float((ba - bb) if bb is not None and ba is not None else 2.0)
        stable = stable_mid(od)
        if stable is None:
            stable = mid
        top_depth = 0.0
        if bb is not None:
            top_depth += float(max(0, od.buy_orders.get(bb, 0)))
        if ba is not None:
            top_depth += float(abs(od.sell_orders.get(ba, 0)))
        book_good = (
            bb is not None
            and ba is not None
            and bb < ba
            and spread <= 6.0
            and top_depth >= 12.0
            and abs(float(stable) - float(mid)) <= 1.2
        )
        strip_delta = float(risk_ctx["strip_delta"])
        hedge_target = int(risk_ctx["target_velvet_pos"])
        alpha_signal = (velvet_fair - float(mid)) / max(1.0, 0.5 * spread)
        alpha_cap = 0
        if abs(strip_delta) < 60.0 and book_good:
            alpha_cap = 40
        elif abs(strip_delta) < 100.0 and book_good:
            alpha_cap = 20
        if bool(risk_ctx["resid_compression"]) and abs(strip_delta) < 80.0:
            alpha_cap = min(alpha_cap, 20)
        alpha_target = int(round(clamp(35.0 * math.tanh(0.75 * alpha_signal), -float(alpha_cap), float(alpha_cap))))
        final_target = int(round(clamp(float(hedge_target + alpha_target), -140.0, 140.0)))
        quote_bias = -0.15 * float(risk_ctx["delta_pressure"])
        if alpha_cap > 0:
            quote_bias += 0.05 * clamp(alpha_signal, -1.0, 1.0)
        take_bias = 0.0 if alpha_cap <= 0 else 0.12 * clamp(alpha_signal, -1.0, 1.0)
        size_mult = 1.0
        if abs(strip_delta) > 100.0:
            size_mult *= 0.85
        if bool(risk_ctx["broad_dislocation"]):
            size_mult *= 0.90
        return {
            "hedge_target": hedge_target,
            "alpha_target": alpha_target,
            "target": final_target,
            "alpha_signal": float(alpha_signal),
            "quote_bias": quote_bias,
            "take_bias": take_bias,
            "size_mult": size_mult,
            "book_good": book_good,
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

        strike = VOUCHER_STRIKES[product]
        low_strike = strike <= 5100
        middle_band = 0.20 <= delta <= 0.80
        pair_bias = int(clamp(float(risk_ctx["pair_bias"].get(product, 0)), -1.0, 1.0))
        pair_target = int(risk_ctx["pair_targets"].get(product, 0))
        confirmed = pair_bias != 0
        resid_threshold = float(risk_ctx["resid_threshold"])
        extreme_resid_threshold = float(risk_ctx["extreme_resid_threshold"])
        cheap_signal = max(0.0, -iv_residual)
        rich_signal = max(0.0, iv_residual)
        low_strike_live = low_strike and abs(float(risk_ctx["strip_delta"])) < 1.10 * float(risk_ctx["total_delta_cap"])
        low_strike_threshold = 0.82 * resid_threshold if low_strike_live else resid_threshold
        buy_confirmed = cheap_signal >= low_strike_threshold or pair_bias > 0
        sell_confirmed = rich_signal >= low_strike_threshold or pair_bias < 0
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
        broad_dislocation = bool(risk_ctx["broad_dislocation"])
        take_edge = max(0.75, 0.35 * spread) + (0.30 if middle_band else 0.0) + (0.20 if not confirmed else 0.0)
        if broad_dislocation:
            take_edge -= 0.15
        if low_strike_live and (confirmed or abs(bs_gap) >= 0.75):
            take_edge -= 0.10
        clear_edge = max(0.35, 0.15 * spread)
        soft_limit = 85 if middle_band else 125
        per_strike_cap = 100 if not middle_band else 80
        take_max = 10 if middle_band else 18
        if broad_dislocation:
            take_max += 2
        if low_strike_live and (confirmed or abs(bs_gap) >= 0.75):
            take_max += 2

        # Step 1: Take
        for ask, volume in sorted(od.sell_orders.items()):
            edge = fair - ask
            if pair_bias > 0:
                edge += 0.20
            if pair_target > 0:
                edge += 0.10
            if low_strike_live and cheap_signal >= low_strike_threshold:
                edge += 0.08
            if (edge >= take_edge and buy_confirmed and not delta_block_buy) or (edge >= take_edge + 0.8 and buy_extreme):
                mgr.buy(ask, min(-volume, take_max))
            else:
                break

        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            edge = bid - fair
            if pair_bias < 0:
                edge += 0.20
            if pair_target < 0:
                edge += 0.10
            if low_strike_live and rich_signal >= low_strike_threshold:
                edge += 0.08
            if (edge >= take_edge and sell_confirmed and not delta_block_sell) or (edge >= take_edge + 0.8 and sell_extreme):
                mgr.sell(bid, min(volume, take_max))
            else:
                break

        # Step 2: Clear
        pos = mgr.projected()
        if pos > soft_limit and bb is not None and bb >= fair - clear_edge:
            mgr.sell(bb, min(pos - soft_limit, 50))
        elif pos > 0 and abs(iv_residual) < (0.40 if low_strike_live else 0.55) * resid_threshold and bb is not None and bb >= fair - (clear_edge + 0.20):
            mgr.sell(bb, min(pos, 28))
        elif pos > 0 and not buy_confirmed and bb is not None and bb >= fair - (clear_edge + 0.15):
            mgr.sell(bb, min(pos, 28))
        elif pos < -soft_limit and ba is not None and ba <= fair + clear_edge:
            mgr.buy(ba, min((-soft_limit) - pos, 50))
        elif pos < 0 and abs(iv_residual) < (0.40 if low_strike_live else 0.55) * resid_threshold and ba is not None and ba <= fair + (clear_edge + 0.20):
            mgr.buy(ba, min(-pos, 28))
        elif pos < 0 and not sell_confirmed and ba is not None and ba <= fair + (clear_edge + 0.15):
            mgr.buy(ba, min(-pos, 28))

        # Step 3: Make
        pos = mgr.projected()
        inv_ratio = pos / limit
        inv_penalty = (0.02 * max(25.0, fair) + 2.0) * inv_ratio
        signal_shift = clamp((cheap_signal - rich_signal) / max(resid_threshold, 1e-6), -1.5, 1.5)
        reservation = fair - inv_penalty + 0.30 * signal_shift + 0.12 * pair_bias + 0.004 * pair_target
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
        if broad_dislocation and pair_target != 0:
            quote_edge = max(0.85, quote_edge - 0.10)
        if low_strike_live and (confirmed or abs(bs_gap) >= 0.75):
            quote_edge = max(0.80, quote_edge - 0.08)

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
        if pair_target != 0:
            size_scale *= 1.08
        if broad_dislocation:
            size_scale *= 1.06
        if low_strike_live and (confirmed or abs(bs_gap) >= 0.75):
            size_scale *= 1.15
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
                    "entry_target": int(hydro_ctx["entry_target"]),
                    "hold_target": int(hydro_ctx["hold_target"]),
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
                    "absolute_danger_long": bool(hydro_ctx["absolute_danger_long"]),
                    "absolute_danger_short": bool(hydro_ctx["absolute_danger_short"]),
                    "same_side_bid_block": bool(hydro_ctx["same_side_bid_block"]),
                    "same_side_ask_block": bool(hydro_ctx["same_side_ask_block"]),
                    "state": str(hydro_ctx.get("state", "")),
                    "unwind_cooldown": int(hydro_ctx.get("unwind_cooldown", hydro_ctx.get("same_side_cooldown", 0))),
                    "local_fair": round(float(hydro_ctx.get("local_fair", hydro_ctx["mid"])), 3),
                    "slow_fair": round(float(hydro_ctx.get("slow_fair", hydro_ctx["mid"])), 3),
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
                risk_ctx = self._build_voucher_risk_context(state, voucher_surface, memory)
                velvet_ctx = self._build_velvet_context(state, velvet_fair, risk_ctx)
                memory["strip_monitor"] = {
                    "strip_delta": round(float(risk_ctx["strip_delta"]), 3),
                    "strip_vega_proxy": round(float(risk_ctx["strip_vega_proxy"]), 3),
                    "avg_abs_resid": round(float(risk_ctx["avg_abs_resid"]), 4),
                    "pair_agreement_count": int(risk_ctx["pair_agreement_count"]),
                    "broad_dislocation": bool(risk_ctx["broad_dislocation"]),
                    "resid_compression": bool(risk_ctx["resid_compression"]),
                    "target_velvet_pos": int(velvet_ctx["target"]),
                    "target_velvet_hedge_pos": int(risk_ctx["target_velvet_pos"]),
                    "velvet_alpha_target": int(velvet_ctx["alpha_target"]),
                    "middle_abs": int(risk_ctx["middle_abs"]),
                    "middle_net": int(risk_ctx["middle_net"]),
                    "middle_same_side_gross": int(risk_ctx["middle_same_side_gross"]),
                    "middle_cap": int(risk_ctx["middle_cap"]),
                    "adjacent_same_side_max": int(risk_ctx["adjacent_same_side_max"]),
                    "adjacent_cap": int(risk_ctx["adjacent_cap"]),
                    "adjacent_same_side_products": list(risk_ctx["adjacent_same_side_products"]),
                    "low_wing_net": int(risk_ctx["low_wing_net"]),
                    "high_wing_net": int(risk_ctx["high_wing_net"]),
                    "cheapest_strikes": list(risk_ctx["cheapest_strikes"]),
                    "richest_strikes": list(risk_ctx["richest_strikes"]),
                }
                memory["voucher_targets"] = {
                    product: {
                        "pair_target": int(risk_ctx["pair_targets"].get(product, 0)),
                        "pair_bias": int(risk_ctx["pair_bias"].get(product, 0)),
                        "iv_residual": round(float(voucher_surface[product]["iv_residual"]), 4),
                        "delta": round(float(voucher_surface[product]["delta"]), 4),
                        "raw_guarded_price": round(float(voucher_surface[product].get("raw_guarded_price", 0.0)), 4),
                        "repaired_price": round(float(voucher_surface[product].get("repaired_price", 0.0)), 4),
                        "repair_amount": round(float(voucher_surface[product].get("repair_amount", 0.0)), 6),
                        "repaired_flag": bool(voucher_surface[product].get("repaired_flag", False)),
                        "repair_reasons": list(voucher_surface[product].get("repair_reasons", [])),
                    }
                    for product in VOUCHER_STRIKES
                }
                memory["voucher_quote_repairs"] = dict(voucher_surface.get("_repair_diag", {}))
                result[VELVET] = self._trade_underlying(
                    VELVET,
                    state,
                    velvet_fair,
                    position_target=float(velvet_ctx["target"]),
                    take_bias=float(velvet_ctx["take_bias"]),
                    quote_bias=float(velvet_ctx["quote_bias"]),
                    size_mult=float(velvet_ctx["size_mult"]),
                )
                for product in VOUCHER_STRIKES:
                    if product in state.order_depths:
                        result[product] = self._trade_voucher(product, state, voucher_surface[product], risk_ctx)
            except Exception as exc:
                memory["engine_errors"]["voucher_strip"] = type(exc).__name__

        return result, conversions, dump_memory(memory)
