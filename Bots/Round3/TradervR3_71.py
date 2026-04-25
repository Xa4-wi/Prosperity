from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Sequence, Tuple

try:
    from datamodel import Order, OrderDepth, TradingState
except ModuleNotFoundError:
    from Bots.datamodel import Order, OrderDepth, TradingState


HYDRO = "HYDROGEL_PACK"
VELVET = "VELVETFRUIT_EXTRACT"
VOUCHERS: Dict[str, int] = {
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
LIMITS: Dict[str, int] = {HYDRO: 200, VELVET: 200, **{p: 300 for p in VOUCHERS}}
MIDDLE_STRIKES = {5000, 5100, 5200, 5300, 5400}
BASE_STRIKE_CAPS: Dict[int, int] = {
    4000: 110,
    4500: 120,
    5000: 110,
    5100: 85,
    5200: 72,
    5300: 60,
    5400: 54,
    5500: 46,
    6000: 34,
    6500: 24,
}
TTE_YEARS = 5.0 / 365.0
MIDDLE_CLUSTER_CAP = 180
ADJ_SAME_SIDE_CAP = 180
UNPAIRED_MIDDLE_CAP = 45
STRIP_DELTA_SOFT_CAP = 145.0
STRIP_DELTA_HARD_CAP = 185.0
PAIR_DISTANCE_LIMIT = 2
PAIR_LIMIT_NORMAL = 3
PAIR_LIMIT_SHOCK = 5
MIN_IV = 0.02
MAX_IV = 2.80
ROOT_2PI = math.sqrt(2.0 * math.pi)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def sign(x: float) -> int:
    if x > 1e-9:
        return 1
    if x < -1e-9:
        return -1
    return 0


def ema(prev: Optional[float], value: float, alpha: float) -> float:
    if prev is None:
        return float(value)
    return (1.0 - alpha) * float(prev) + alpha * float(value)


def safe_mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / ROOT_2PI


def load_memory(trader_data: str) -> dict:
    if not trader_data:
        return {}
    try:
        obj = json.loads(trader_data)
        return obj if isinstance(obj, dict) else {}
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}


def dump_memory(memory: dict) -> str:
    return json.dumps(memory, separators=(",", ":"))


def best_bid(od: OrderDepth) -> Optional[int]:
    return max(od.buy_orders) if od.buy_orders else None


def best_ask(od: OrderDepth) -> Optional[int]:
    return min(od.sell_orders) if od.sell_orders else None


def bid_volume(od: OrderDepth, price: Optional[int]) -> int:
    if price is None:
        return 0
    return max(0, int(od.buy_orders.get(price, 0)))


def ask_volume(od: OrderDepth, price: Optional[int]) -> int:
    if price is None:
        return 0
    return abs(int(od.sell_orders.get(price, 0)))


def stable_mid(od: OrderDepth) -> Optional[float]:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is not None and ba is not None:
        return 0.5 * (bb + ba)
    if bb is not None:
        return float(bb)
    if ba is not None:
        return float(ba)
    return None


def microprice(od: OrderDepth) -> Optional[float]:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None or ba is None:
        return stable_mid(od)
    bv = bid_volume(od, bb)
    av = ask_volume(od, ba)
    if bv + av <= 0:
        return 0.5 * (bb + ba)
    return (ba * bv + bb * av) / (bv + av)


def book_liquidity(od: OrderDepth) -> float:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None and ba is None:
        return 0.0
    total = 0.0
    for price, volume in od.buy_orders.items():
        total += max(0, int(volume))
    for price, volume in od.sell_orders.items():
        total += abs(int(volume))
    spread = 1.0
    if bb is not None and ba is not None:
        spread = max(1.0, float(ba - bb))
    return total / spread


def bs_call_price(spot: float, strike: float, tte: float, sigma: float) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    intrinsic = max(spot - strike, 0.0)
    if tte <= 0.0 or sigma <= 1e-8:
        return intrinsic
    sqrt_t = math.sqrt(tte)
    vol_t = sigma * sqrt_t
    if vol_t <= 1e-12:
        return intrinsic
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * tte) / vol_t
    d2 = d1 - vol_t
    return spot * norm_cdf(d1) - strike * norm_cdf(d2)


def bs_delta(spot: float, strike: float, tte: float, sigma: float) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    if tte <= 0.0 or sigma <= 1e-8:
        return 1.0 if spot > strike else 0.0
    sqrt_t = math.sqrt(tte)
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * tte) / (sigma * sqrt_t)
    return norm_cdf(d1)


def bs_vega(spot: float, strike: float, tte: float, sigma: float) -> float:
    if spot <= 0.0 or strike <= 0.0 or tte <= 0.0 or sigma <= 1e-8:
        return 0.0
    sqrt_t = math.sqrt(tte)
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * tte) / (sigma * sqrt_t)
    return spot * sqrt_t * norm_pdf(d1)


def implied_vol_call(spot: float, strike: float, tte: float, price: float) -> Optional[float]:
    if spot <= 0.0 or strike <= 0.0 or tte <= 0.0:
        return None
    intrinsic = max(spot - strike, 0.0)
    if price <= intrinsic + 1e-6:
        return MIN_IV
    upper_bound = spot
    if price >= upper_bound:
        return None
    lo, hi = MIN_IV, MAX_IV
    plo = bs_call_price(spot, strike, tte, lo)
    phi = bs_call_price(spot, strike, tte, hi)
    if price < plo - 1e-6:
        return lo
    if price > phi + 1e-6:
        return hi
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        pm = bs_call_price(spot, strike, tte, mid)
        if abs(pm - price) <= 1e-6:
            return mid
        if pm > price:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def solve_3x3(a: List[List[float]], b: List[float]) -> Optional[List[float]]:
    m = [row[:] + [rhs] for row, rhs in zip(a, b)]
    n = 3
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-12:
            return None
        if pivot != col:
            m[col], m[pivot] = m[pivot], m[col]
        div = m[col][col]
        for j in range(col, n + 1):
            m[col][j] /= div
        for r in range(n):
            if r == col:
                continue
            factor = m[r][col]
            for j in range(col, n + 1):
                m[r][j] -= factor * m[col][j]
    return [m[i][n] for i in range(n)]


def fit_weighted_quadratic(xs: Sequence[float], ys: Sequence[float], ws: Sequence[float]) -> Tuple[Tuple[float, float, float], float]:
    if not xs:
        return (0.0, 0.0, 0.0), 0.0
    if len(xs) == 1:
        return (ys[0], 0.0, 0.0), 0.0
    s0 = sum(ws)
    s1 = sum(w * x for x, w in zip(xs, ws))
    s2 = sum(w * x * x for x, w in zip(xs, ws))
    s3 = sum(w * x * x * x for x, w in zip(xs, ws))
    s4 = sum(w * x * x * x * x for x, w in zip(xs, ws))
    t0 = sum(w * y for y, w in zip(ys, ws))
    t1 = sum(w * x * y for x, y, w in zip(xs, ys, ws))
    t2 = sum(w * x * x * y for x, y, w in zip(xs, ys, ws))
    coeffs = solve_3x3([[s0, s1, s2], [s1, s2, s3], [s2, s3, s4]], [t0, t1, t2])
    if coeffs is None:
        mean_y = sum(y * w for y, w in zip(ys, ws)) / max(1e-9, sum(ws))
        return (mean_y, 0.0, 0.0), 0.0
    a0, a1, a2 = coeffs
    err = 0.0
    weight = 0.0
    for x, y, w in zip(xs, ys, ws):
        fit = a0 + a1 * x + a2 * x * x
        err += w * (fit - y) * (fit - y)
        weight += w
    rmse = math.sqrt(err / max(weight, 1e-9))
    return (a0, a1, a2), rmse


def quad_eval(coeffs: Tuple[float, float, float], x: float) -> float:
    return coeffs[0] + coeffs[1] * x + coeffs[2] * x * x


def rank_to_size(score: float, hard_cap: int) -> int:
    if score < 0.85:
        base = 8
    elif score < 1.30:
        base = 16
    elif score < 1.85:
        base = 26
    else:
        base = 38
    return min(hard_cap, base)


class OrderAccumulator:
    def __init__(self, product: str, position: int, limit: int):
        self.product = product
        self.position = int(position)
        self.limit = int(limit)
        self.buy_left = max(0, limit - position)
        self.sell_left = max(0, limit + position)
        self.orders: List[Order] = []

    def projected(self) -> int:
        return self.position + sum(order.quantity for order in self.orders)

    def buy(self, price: int, qty: int) -> None:
        size = min(max(0, int(qty)), self.buy_left)
        if size <= 0:
            return
        self.orders.append(Order(self.product, int(price), size))
        self.buy_left -= size

    def sell(self, price: int, qty: int) -> None:
        size = min(max(0, int(qty)), self.sell_left)
        if size <= 0:
            return
        self.orders.append(Order(self.product, int(price), -size))
        self.sell_left -= size

    def flush(self) -> List[Order]:
        return self.orders


class Trader:
    def _reset_if_new_day(self, memory: dict, timestamp: int) -> None:
        last_ts = int(memory.get("_last_timestamp", -1))
        if timestamp < last_ts:
            memory.clear()
        memory["_last_timestamp"] = timestamp
        memory.setdefault(HYDRO, {"ema_fair": None, "open_mid": None})
        memory.setdefault(VELVET, {"ema_fair": None, "open_mid": None})
        memory.setdefault(
            "voucher",
            {
                "local_iv_ema": {},
                "avg_abs_resid_ema": None,
                "peak_avg_abs_resid": 0.0,
                "mode": "PAIR",
            },
        )

    def _book_snapshot(self, od: OrderDepth) -> dict:
        bb = best_bid(od)
        ba = best_ask(od)
        mid = stable_mid(od)
        micro = microprice(od)
        spread = 999.0
        if bb is not None and ba is not None:
            spread = float(max(1, ba - bb))
        return {
            "best_bid": bb,
            "best_ask": ba,
            "mid": mid,
            "micro": micro if micro is not None else mid,
            "spread": spread,
            "liq": book_liquidity(od),
            "bid_size": bid_volume(od, bb),
            "ask_size": ask_volume(od, ba),
        }

    def _robust_underlying_fair(self, product: str, od: OrderDepth, memory: dict) -> float:
        snap = self._book_snapshot(od)
        state = memory[product]
        fallback = 10000.0 if product == HYDRO else 5250.0
        raw_mid = snap["mid"] if snap["mid"] is not None else snap["micro"]
        mid = float(raw_mid if raw_mid is not None else fallback)
        micro = float(snap["micro"] if snap["micro"] is not None else mid)
        if state["open_mid"] is None:
            state["open_mid"] = mid
        state["ema_fair"] = ema(state["ema_fair"], mid, 0.16 if product == HYDRO else 0.18)
        open_mid = float(state["open_mid"])
        if product == HYDRO:
            return 0.48 * mid + 0.28 * micro + 0.14 * float(state["ema_fair"]) + 0.10 * open_mid
        return 0.42 * mid + 0.30 * micro + 0.18 * float(state["ema_fair"]) + 0.10 * open_mid

    def _repair_call_slice(self, strikes: Sequence[int], prices: Sequence[Optional[float]], spot: float) -> List[Optional[float]]:
        repaired: List[Optional[float]] = []
        for strike, price in zip(strikes, prices):
            if price is None:
                repaired.append(None)
                continue
            intrinsic = max(spot - strike, 0.0) + 1e-4
            repaired.append(max(float(price), intrinsic))
        prev = None
        for idx, price in enumerate(repaired):
            if price is None:
                continue
            if prev is not None and price > prev:
                repaired[idx] = prev
            prev = repaired[idx]
        for _ in range(2):
            for idx in range(1, len(repaired) - 1):
                left = repaired[idx - 1]
                mid = repaired[idx]
                right = repaired[idx + 1]
                if left is None or mid is None or right is None:
                    continue
                repaired[idx] = min(mid, 0.5 * (left + right))
            prev = None
            for idx, price in enumerate(repaired):
                if price is None:
                    continue
                if prev is not None and price > prev:
                    repaired[idx] = prev
                prev = repaired[idx]
        return repaired

    def _build_voucher_surface(self, state: TradingState, spot_fair: float, memory: dict) -> Tuple[Dict[str, dict], dict]:
        voucher_memory = memory["voucher"]
        products = sorted(VOUCHERS, key=VOUCHERS.get)
        strikes = [VOUCHERS[p] for p in products]
        raw_prices: List[Optional[float]] = []
        xs: List[float] = []
        ys: List[float] = []
        ws: List[float] = []
        surface: Dict[str, dict] = {}
        suspicious_quotes = 0

        for product, strike in zip(products, strikes):
            od = state.order_depths.get(product)
            if od is None:
                raw_prices.append(None)
                continue
            snap = self._book_snapshot(od)
            bb = snap["best_bid"]
            ba = snap["best_ask"]
            mid = snap["mid"]
            if mid is None or bb is None or ba is None:
                raw_prices.append(None)
                suspicious_quotes += 1
                continue
            raw_prices.append(float(mid))
            m = math.log(strike / spot_fair)
            market_iv = implied_vol_call(spot_fair, strike, TTE_YEARS, float(mid))
            liquidity_quality = clamp(float(snap["liq"]) / 45.0, 0.0, 1.0)
            spread_quality = clamp(6.0 / max(1.0, float(snap["spread"])), 0.0, 1.0)
            weight = 0.40 + 0.35 * liquidity_quality + 0.25 * spread_quality
            surface[product] = {
                "strike": strike,
                "moneyness": m,
                "bid": int(bb),
                "ask": int(ba),
                "mid": float(mid),
                "spread": float(snap["spread"]),
                "liq": float(snap["liq"]),
                "market_iv": market_iv,
                "weight": weight,
            }
            if market_iv is not None:
                xs.append(m)
                ys.append(float(market_iv))
                ws.append(weight)

        repaired_prices = self._repair_call_slice(strikes, raw_prices, spot_fair)
        fit_xs: List[float] = []
        fit_ys: List[float] = []
        fit_ws: List[float] = []
        for product, strike, rep_price in zip(products, strikes, repaired_prices):
            if rep_price is None:
                continue
            rep_iv = implied_vol_call(spot_fair, strike, TTE_YEARS, rep_price)
            if rep_iv is None:
                continue
            m = math.log(strike / spot_fair)
            fit_xs.append(m)
            fit_ys.append(rep_iv)
            fit_ws.append(float(surface.get(product, {}).get("weight", 0.8)))

        if not fit_ys and ys:
            fit_xs, fit_ys, fit_ws = xs[:], ys[:], ws[:]

        coeffs, rmse = fit_weighted_quadratic(fit_xs, fit_ys, fit_ws)
        usable = len(fit_ys)
        stability = clamp(0.18 * usable + 0.55 - 7.5 * rmse - 0.04 * suspicious_quotes, 0.0, 1.0)

        struct_resids: List[float] = []
        for product, strike in VOUCHERS.items():
            if product not in surface:
                continue
            row = surface[product]
            struct_iv = clamp(quad_eval(coeffs, row["moneyness"]), MIN_IV, MAX_IV)
            local_prev = voucher_memory["local_iv_ema"].get(product)
            market_iv = row["market_iv"]
            if market_iv is not None:
                local_now = ema(local_prev, float(market_iv), 0.18)
                voucher_memory["local_iv_ema"][product] = local_now
            else:
                local_now = local_prev if local_prev is not None else struct_iv
            row["struct_iv"] = struct_iv
            row["local_iv"] = float(local_now)
            row["hybrid_iv"] = 0.75 * struct_iv + 0.25 * float(local_now)
            row["fair_price"] = bs_call_price(spot_fair, strike, TTE_YEARS, row["hybrid_iv"])
            row["delta"] = bs_delta(spot_fair, strike, TTE_YEARS, row["hybrid_iv"])
            row["vega"] = bs_vega(spot_fair, strike, TTE_YEARS, row["hybrid_iv"])
            row["iv_residual"] = 0.0 if market_iv is None else float(market_iv) - struct_iv
            if market_iv is not None:
                struct_resids.append(abs(row["iv_residual"]))

        avg_struct_abs = safe_mean(struct_resids)
        avg_abs_ema = voucher_memory.get("avg_abs_resid_ema")
        voucher_memory["avg_abs_resid_ema"] = ema(avg_abs_ema, avg_struct_abs, 0.12)
        broad_hint = avg_struct_abs > max(0.015, 1.12 * float(voucher_memory["avg_abs_resid_ema"] or avg_struct_abs))

        final_resids: List[float] = []
        pair_agreement_count = 0
        ordered = sorted(surface, key=lambda p: VOUCHERS[p])
        for idx, product in enumerate(ordered):
            row = surface[product]
            local_weight = 0.45 if (stability < 0.60 or broad_hint) else 0.25
            row["hybrid_iv"] = (1.0 - local_weight) * row["struct_iv"] + local_weight * row["local_iv"]
            row["fair_price"] = bs_call_price(spot_fair, row["strike"], TTE_YEARS, row["hybrid_iv"])
            row["delta"] = bs_delta(spot_fair, row["strike"], TTE_YEARS, row["hybrid_iv"])
            row["vega"] = bs_vega(spot_fair, row["strike"], TTE_YEARS, row["hybrid_iv"])
            row["iv_residual"] = 0.0 if row["market_iv"] is None else float(row["market_iv"]) - row["hybrid_iv"]
            final_resids.append(abs(row["iv_residual"]))
            neighbor_signs = []
            for j in (idx - 1, idx + 1):
                if 0 <= j < len(ordered):
                    other = surface[ordered[j]]
                    if abs(other["iv_residual"]) >= 0.010:
                        neighbor_signs.append(sign(other["iv_residual"]))
            own_sign = sign(row["iv_residual"])
            row["neighbor_confirmation"] = sum(1 for s in neighbor_signs if s == own_sign and s != 0) / 2.0

        for left, right in zip(ordered, ordered[1:]):
            lres = float(surface[left]["iv_residual"])
            rres = float(surface[right]["iv_residual"])
            if abs(lres) >= 0.012 and abs(rres) >= 0.012 and sign(lres) == sign(rres) and sign(lres) != 0:
                pair_agreement_count += 1

        avg_abs = safe_mean(final_resids)
        peak_abs = float(voucher_memory.get("peak_avg_abs_resid", 0.0))
        peak_abs = max(avg_abs, 0.995 * peak_abs)
        voucher_memory["peak_avg_abs_resid"] = peak_abs
        resid_compression = 0.0 if peak_abs <= 1e-9 else clamp(1.0 - avg_abs / peak_abs, 0.0, 1.0)
        broad_dislocation = (
            avg_abs > max(0.016, 1.08 * float(voucher_memory["avg_abs_resid_ema"] or avg_abs))
            and pair_agreement_count >= 3
        )
        cheapest = sorted(ordered, key=lambda p: surface[p]["iv_residual"])[:3]
        richest = sorted(ordered, key=lambda p: surface[p]["iv_residual"], reverse=True)[:3]
        meta = {
            "stability": stability,
            "usable": usable,
            "rmse": rmse,
            "avg_abs_iv_residual": avg_abs,
            "pair_agreement_count": pair_agreement_count,
            "broad_dislocation": broad_dislocation,
            "resid_compression": resid_compression,
            "cheapest": cheapest,
            "richest": richest,
        }
        voucher_memory["mode"] = "SHOCK" if broad_dislocation else "PAIR"
        return surface, meta

    def _build_strip_context(self, state: TradingState, surface: Dict[str, dict], meta: dict) -> dict:
        current_delta = 0.0
        vega_proxy = 0.0
        middle_gross = 0
        adjacent_same_side_max = 0
        ordered = sorted(surface, key=lambda p: VOUCHERS[p])
        positions = {p: int(state.position.get(p, 0)) for p in ordered}
        for product in ordered:
            row = surface[product]
            pos = positions[product]
            current_delta += pos * float(row["delta"])
            vega_proxy += abs(pos) * float(row["vega"])
            if row["strike"] in MIDDLE_STRIKES:
                middle_gross += abs(pos)
        for left, right in zip(ordered, ordered[1:]):
            p1 = positions[left]
            p2 = positions[right]
            if sign(p1) != 0 and sign(p1) == sign(p2):
                adjacent_same_side_max = max(adjacent_same_side_max, abs(p1) + abs(p2))

        hedge_ratio = 0.75 if meta["broad_dislocation"] else (0.50 if meta["avg_abs_iv_residual"] > 0.013 else 0.25)
        if meta["resid_compression"] > 0.35:
            hedge_ratio *= 0.55
        if meta["resid_compression"] > 0.60:
            hedge_ratio = 0.0
        if abs(current_delta) < 20.0:
            hedge_ratio = 0.0
        target_velvet = int(round(clamp(-hedge_ratio * current_delta, -120.0, 120.0)))
        velvet_pos = int(state.position.get(VELVET, 0))
        hedge_gap = abs(target_velvet - velvet_pos)
        hedge_feasible = clamp(
            1.0
            - 0.38 * abs(current_delta) / STRIP_DELTA_SOFT_CAP
            - 0.28 * middle_gross / MIDDLE_CLUSTER_CAP
            - 0.20 * hedge_gap / 120.0
            - 0.12 * adjacent_same_side_max / ADJ_SAME_SIDE_CAP,
            0.20,
            1.0,
        )
        return {
            "positions": positions,
            "strip_delta": current_delta,
            "strip_vega_proxy": vega_proxy,
            "middle_gross": middle_gross,
            "adjacent_same_side_max": adjacent_same_side_max,
            "hedge_ratio": hedge_ratio,
            "target_velvet": target_velvet,
            "hedge_feasible": hedge_feasible,
            "shock_mode": bool(meta["broad_dislocation"]),
        }

    def _select_pairs_and_targets(self, state: TradingState, surface: Dict[str, dict], meta: dict, strip: dict) -> Tuple[Dict[str, int], Dict[str, str], List[str]]:
        ordered = sorted(surface, key=lambda p: VOUCHERS[p])
        entry_threshold = max(0.012, 0.95 * meta["avg_abs_iv_residual"])
        shock_entry_threshold = max(0.010, 0.75 * entry_threshold)
        outright_threshold = max(0.038, 2.40 * entry_threshold)
        active_entry = shock_entry_threshold if strip["shock_mode"] else entry_threshold
        max_vega = max((float(surface[p]["vega"]) for p in ordered), default=1.0)
        candidates: List[dict] = []
        for i, cheap in enumerate(ordered):
            row_c = surface[cheap]
            if row_c["market_iv"] is None or row_c["iv_residual"] >= -active_entry:
                continue
            for j in range(i + 1, min(len(ordered), i + PAIR_DISTANCE_LIMIT + 2)):
                rich = ordered[j]
                row_r = surface[rich]
                if row_r["market_iv"] is None or row_r["iv_residual"] <= active_entry:
                    continue
                spread = float(row_r["iv_residual"] - row_c["iv_residual"])
                if spread <= active_entry:
                    continue
                liq = min(row_c["liq"], row_r["liq"])
                liq_score = clamp(liq / 55.0, 0.0, 1.0)
                vega_score = clamp(min(float(row_c["vega"]), float(row_r["vega"])) / max(max_vega, 1e-6), 0.25, 1.0)
                neigh = 0.5 * (row_c["neighbor_confirmation"] + row_r["neighbor_confirmation"])
                pair_delta = float(row_c["delta"] - row_r["delta"])
                delta_penalty = abs(strip["strip_delta"] + pair_delta) - abs(strip["strip_delta"])
                delta_score = 1.0 - clamp(max(0.0, delta_penalty) / 0.25, 0.0, 1.0)
                fit_score = meta["stability"]
                residual_strength = spread / max(active_entry, 1e-6)
                confidence = (
                    0.36 * residual_strength
                    + 0.22 * fit_score
                    + 0.18 * neigh
                    + 0.16 * liq_score
                    + 0.08 * strip["hedge_feasible"]
                ) * delta_score * vega_score
                score = confidence - 0.10 * max(0, VOUCHERS[rich] - 5300) / 400.0
                candidates.append(
                    {
                        "cheap": cheap,
                        "rich": rich,
                        "spread": spread,
                        "score": score,
                        "confidence": confidence,
                        "pair_delta": pair_delta,
                    }
                )

        candidates.sort(key=lambda row: (row["score"], row["spread"]), reverse=True)
        pair_limit = PAIR_LIMIT_SHOCK if strip["shock_mode"] else PAIR_LIMIT_NORMAL
        selected: List[dict] = []
        used = set()
        for row in candidates:
            if row["cheap"] in used or row["rich"] in used:
                continue
            selected.append(row)
            used.add(row["cheap"])
            used.add(row["rich"])
            if len(selected) >= pair_limit:
                break

        target_bias = {p: 0 for p in ordered}
        source = {p: "flat" for p in ordered}
        selected_pairs: List[str] = []

        for row in selected:
            cheap = row["cheap"]
            rich = row["rich"]
            selected_pairs.append(f"{cheap}->{rich}")
            cheap_strike = surface[cheap]["strike"]
            rich_strike = surface[rich]["strike"]
            cheap_cap = BASE_STRIKE_CAPS[cheap_strike]
            rich_cap = BASE_STRIKE_CAPS[rich_strike]
            if strip["shock_mode"]:
                cheap_cap = int(round(1.10 * cheap_cap))
                rich_cap = int(round(1.10 * rich_cap))
            size_cap = min(cheap_cap, rich_cap, 52)
            size = rank_to_size(row["confidence"] * strip["hedge_feasible"], size_cap)
            target_bias[cheap] += size
            target_bias[rich] -= size
            source[cheap] = "pair"
            source[rich] = "pair"

        outright_candidates: List[dict] = []
        for product in ordered:
            if source[product] == "pair":
                continue
            row = surface[product]
            resid = float(row["iv_residual"])
            if abs(resid) < outright_threshold:
                continue
            if row["neighbor_confirmation"] < 0.5:
                continue
            strike = row["strike"]
            if strike <= 4500 or strike >= 6000:
                cap = 10
            elif strike in MIDDLE_STRIKES:
                cap = min(BASE_STRIKE_CAPS[strike], UNPAIRED_MIDDLE_CAP)
            else:
                cap = max(14, int(round(0.35 * BASE_STRIKE_CAPS[strike])))
            liq_score = clamp(row["liq"] / 55.0, 0.0, 1.0)
            vega_score = clamp(float(row["vega"]) / max(max_vega, 1e-6), 0.18, 1.0)
            score = (
                0.42 * abs(resid) / max(outright_threshold, 1e-6)
                + 0.26 * meta["stability"]
                + 0.16 * row["neighbor_confirmation"]
                + 0.16 * liq_score
            ) * strip["hedge_feasible"] * vega_score
            outright_candidates.append(
                {
                    "product": product,
                    "score": score,
                    "cap": cap,
                    "sign": -1 if resid > 0.0 else 1,
                }
            )

        outright_candidates.sort(key=lambda row: row["score"], reverse=True)
        outright_used_signs = set()
        for row in outright_candidates:
            if row["score"] < 1.05:
                continue
            if row["sign"] in outright_used_signs and not strip["shock_mode"]:
                continue
            product = row["product"]
            size = rank_to_size(row["score"], row["cap"])
            target_bias[product] += row["sign"] * size
            source[product] = "outright"
            outright_used_signs.add(row["sign"])
            if len(outright_used_signs) >= 2:
                break

        middle_target_gross = sum(abs(target_bias[p]) for p in ordered if surface[p]["strike"] in MIDDLE_STRIKES)
        if middle_target_gross > MIDDLE_CLUSTER_CAP:
            scale = MIDDLE_CLUSTER_CAP / middle_target_gross
            for product in ordered:
                if surface[product]["strike"] in MIDDLE_STRIKES:
                    target_bias[product] = int(round(target_bias[product] * scale))

        for left, right in zip(ordered, ordered[1:]):
            l = target_bias[left]
            r = target_bias[right]
            if sign(l) != 0 and sign(l) == sign(r):
                gross = abs(l) + abs(r)
                if gross > ADJ_SAME_SIDE_CAP:
                    scale = ADJ_SAME_SIDE_CAP / gross
                    target_bias[left] = int(round(l * scale))
                    target_bias[right] = int(round(r * scale))

        target_delta = strip["strip_delta"]
        for product in ordered:
            current_pos = int(state.position.get(product, 0))
            target_delta += (target_bias[product] - current_pos) * float(surface[product]["delta"])
        if abs(target_delta) > STRIP_DELTA_HARD_CAP:
            scale = STRIP_DELTA_HARD_CAP / max(abs(target_delta), 1e-6)
            for product in ordered:
                target_bias[product] = int(round(target_bias[product] * scale))

        return target_bias, source, selected_pairs

    def _build_velvet_plan(self, state: TradingState, spot_fair: float, strip: dict, meta: dict) -> dict:
        od = state.order_depths[VELVET]
        snap = self._book_snapshot(od)
        mid = float(snap["mid"] if snap["mid"] is not None else spot_fair)
        spread = float(snap["spread"] if snap["spread"] < 900 else 6.0)
        fair_gap = spot_fair - mid
        alpha_signal = fair_gap / max(1.5, 0.5 * spread)
        alpha_target = 18.0 * math.tanh(0.70 * alpha_signal)
        if abs(strip["strip_delta"]) > 65.0:
            alpha_target *= 0.25
        if meta["resid_compression"] > 0.35:
            alpha_target *= 0.55
        if meta["resid_compression"] > 0.60:
            alpha_target = 0.0
        hedge_target = float(strip["target_velvet"])
        final_target = int(round(clamp(hedge_target + alpha_target, -120.0, 120.0)))
        quote_bias = 0.0
        if hedge_target > state.position.get(VELVET, 0):
            quote_bias -= 0.4
        elif hedge_target < state.position.get(VELVET, 0):
            quote_bias += 0.4
        if meta["resid_compression"] > 0.35:
            quote_bias *= 0.6
        return {
            "hedge_ratio": strip["hedge_ratio"],
            "vev_hedge_target": int(round(hedge_target)),
            "vev_alpha_target": int(round(alpha_target)),
            "vev_final_target": final_target,
            "quote_bias": quote_bias,
            "mid": mid,
        }

    def _trade_hydro(self, state: TradingState, fair: float) -> List[Order]:
        od = state.order_depths.get(HYDRO)
        if od is None:
            return []
        mgr = OrderAccumulator(HYDRO, int(state.position.get(HYDRO, 0)), LIMITS[HYDRO])
        snap = self._book_snapshot(od)
        bb = snap["best_bid"]
        ba = snap["best_ask"]
        spread = float(snap["spread"] if snap["spread"] < 900 else 8.0)
        take_edge = 2.5
        clear_edge = 1.0
        quote_edge = max(3.0, 0.45 * spread + 2.0)
        pos = mgr.projected()
        inv_ratio = pos / LIMITS[HYDRO]
        reservation = fair - 9.0 * inv_ratio

        if ba is not None:
            for ask, vol in sorted(od.sell_orders.items()):
                if ask <= fair - take_edge:
                    mgr.buy(ask, min(-int(vol), 18))
                else:
                    break
        if bb is not None:
            for bid, vol in sorted(od.buy_orders.items(), reverse=True):
                if bid >= fair + take_edge:
                    mgr.sell(bid, min(int(vol), 18))
                else:
                    break

        pos = mgr.projected()
        if pos > 90 and bb is not None and bb >= fair - clear_edge:
            mgr.sell(bb, min(pos - 90, 32))
        if pos < -90 and ba is not None and ba <= fair + clear_edge:
            mgr.buy(ba, min(-90 - pos, 32))

        buy_px = int(math.floor(reservation - quote_edge))
        sell_px = int(math.ceil(reservation + quote_edge))
        if bb is not None and ba is not None and bb < ba:
            buy_px = min(max(buy_px, bb + 1), ba - 1)
            sell_px = max(min(sell_px, ba - 1), bb + 1)
        buy_px = max(0, buy_px)
        sell_px = max(buy_px + 1, sell_px)
        quote_size = max(8, int(round(18 * clamp(1.0 - 0.65 * abs(inv_ratio), 0.35, 1.0))))
        if mgr.projected() < 150:
            mgr.buy(buy_px, quote_size)
        if mgr.projected() > -150:
            mgr.sell(sell_px, quote_size)
        return mgr.flush()

    def _trade_velvet(self, state: TradingState, fair: float, plan: dict) -> List[Order]:
        od = state.order_depths.get(VELVET)
        if od is None:
            return []
        mgr = OrderAccumulator(VELVET, int(state.position.get(VELVET, 0)), LIMITS[VELVET])
        snap = self._book_snapshot(od)
        bb = snap["best_bid"]
        ba = snap["best_ask"]
        spread = float(snap["spread"] if snap["spread"] < 900 else 6.0)
        target = int(plan["vev_final_target"])
        take_edge = 1.1
        quote_edge = max(1.5, 0.35 * spread + 0.8)
        clear_edge = 0.7
        pos = mgr.projected()

        if target > pos and ba is not None:
            for ask, vol in sorted(od.sell_orders.items()):
                if ask <= fair - take_edge or ask <= fair + 0.1 and pos < target:
                    qty = min(target - pos, -int(vol), 26)
                    mgr.buy(ask, qty)
                    pos = mgr.projected()
                else:
                    break
        if target < pos and bb is not None:
            for bid, vol in sorted(od.buy_orders.items(), reverse=True):
                if bid >= fair + take_edge or bid >= fair - 0.1 and pos > target:
                    qty = min(pos - target, int(vol), 26)
                    mgr.sell(bid, qty)
                    pos = mgr.projected()
                else:
                    break

        pos = mgr.projected()
        if pos > target and bb is not None and bb >= fair - clear_edge:
            mgr.sell(bb, min(pos - target, 24))
        if pos < target and ba is not None and ba <= fair + clear_edge:
            mgr.buy(ba, min(target - pos, 24))

        pos = mgr.projected()
        inv_ratio = (pos - target) / LIMITS[VELVET]
        reservation = fair + float(plan["quote_bias"]) - 6.0 * inv_ratio
        buy_px = int(math.floor(reservation - quote_edge))
        sell_px = int(math.ceil(reservation + quote_edge))
        if bb is not None and ba is not None and bb < ba:
            buy_px = min(max(buy_px, bb + 1), ba - 1)
            sell_px = max(min(sell_px, ba - 1), bb + 1)
        buy_px = max(0, buy_px)
        sell_px = max(buy_px + 1, sell_px)
        quote_size = max(6, int(round(22 * clamp(1.0 - 0.60 * abs(inv_ratio), 0.25, 1.0))))
        if pos < target:
            mgr.buy(buy_px, quote_size)
        if pos > target:
            mgr.sell(sell_px, quote_size)
        return mgr.flush()

    def _trade_voucher(self, product: str, state: TradingState, row: dict, target: int, source: str, meta: dict, strip: dict) -> List[Order]:
        od = state.order_depths.get(product)
        if od is None:
            return []
        mgr = OrderAccumulator(product, int(state.position.get(product, 0)), LIMITS[product])
        pos = mgr.projected()
        fair_price = float(row["fair_price"])
        fair_iv = float(row["hybrid_iv"])
        market_iv = row["market_iv"]
        if market_iv is None:
            return []
        bb = row["bid"]
        ba = row["ask"]
        spread = float(row["spread"])
        strike = row["strike"]
        mid_band = max(0.75, 0.22 * spread)
        iv_band = max(0.010, 0.55 * max(0.012, 0.95 * meta["avg_abs_iv_residual"]))
        if strip["shock_mode"] and source == "pair":
            mid_band *= 0.75
            iv_band *= 0.80
        if source == "outright":
            mid_band *= 1.20
            iv_band *= 1.20

        if target > pos:
            for ask, vol in sorted(od.sell_orders.items()):
                if ask <= fair_price - mid_band or market_iv <= fair_iv - iv_band:
                    mgr.buy(ask, min(target - mgr.projected(), -int(vol), 28))
                else:
                    break
        if target < pos:
            for bid, vol in sorted(od.buy_orders.items(), reverse=True):
                if bid >= fair_price + mid_band or market_iv >= fair_iv + iv_band:
                    mgr.sell(bid, min(mgr.projected() - target, int(vol), 28))
                else:
                    break

        pos = mgr.projected()
        clear_band = max(0.40, 0.15 * spread)
        if pos > target and bb is not None and bb >= fair_price - clear_band:
            mgr.sell(bb, min(pos - target, 22))
        if pos < target and ba is not None and ba <= fair_price + clear_band:
            mgr.buy(ba, min(target - pos, 22))

        pos = mgr.projected()
        inv_ratio = (pos - target) / LIMITS[product]
        reservation = fair_price - 1.8 * inv_ratio
        quote_edge = max(1.0, 0.38 * spread + 0.3)
        bid_quote = int(math.floor(reservation - quote_edge))
        ask_quote = int(math.ceil(reservation + quote_edge))
        if bb is not None and ba is not None and bb < ba:
            bid_quote = min(max(bid_quote, bb + 1), ba - 1)
            ask_quote = max(min(ask_quote, ba - 1), bb + 1)
        bid_quote = max(0, bid_quote)
        ask_quote = max(bid_quote + 1, ask_quote)
        base_quote = 10 if strike <= 5000 else 7
        quote_size = max(4, int(round(base_quote * clamp(1.0 - 0.70 * abs(inv_ratio), 0.25, 1.0))))
        if pos < target:
            mgr.buy(bid_quote, quote_size)
        if pos > target:
            mgr.sell(ask_quote, quote_size)
        return mgr.flush()

    def run(self, state: TradingState):
        memory = load_memory(state.traderData)
        self._reset_if_new_day(memory, state.timestamp)
        result: Dict[str, List[Order]] = {product: [] for product in state.order_depths}

        if HYDRO in state.order_depths:
            hydro_fair = self._robust_underlying_fair(HYDRO, state.order_depths[HYDRO], memory)
            result[HYDRO] = self._trade_hydro(state, hydro_fair)
        else:
            hydro_fair = None

        strip_monitor = {}
        if VELVET in state.order_depths:
            spot_fair = self._robust_underlying_fair(VELVET, state.order_depths[VELVET], memory)
            surface, meta = self._build_voucher_surface(state, spot_fair, memory)
            strip = self._build_strip_context(state, surface, meta)
            target_bias, source_map, selected_pairs = self._select_pairs_and_targets(state, surface, meta, strip)
            velvet_plan = self._build_velvet_plan(state, spot_fair, strip, meta)
            result[VELVET] = self._trade_velvet(state, spot_fair, velvet_plan)
            for product, row in surface.items():
                target = int(target_bias.get(product, 0))
                result[product] = self._trade_voucher(product, state, row, target, source_map.get(product, "flat"), meta, strip)
            strip_monitor = {
                "spot_fair": round(float(spot_fair), 3),
                "mode": "BROAD_SHOCK" if strip["shock_mode"] else "STEADY_PAIR_SCALP",
                "stability": round(float(meta["stability"]), 4),
                "avg_abs_iv_residual": round(float(meta["avg_abs_iv_residual"]), 4),
                "pair_agreement_count": int(meta["pair_agreement_count"]),
                "resid_compression": round(float(meta["resid_compression"]), 4),
                "strip_delta": round(float(strip["strip_delta"]), 3),
                "strip_vega_proxy": round(float(strip["strip_vega_proxy"]), 3),
                "hedge_ratio": round(float(velvet_plan["hedge_ratio"]), 3),
                "hedge_feasible": round(float(strip["hedge_feasible"]), 3),
                "vev_hedge_target": int(velvet_plan["vev_hedge_target"]),
                "vev_alpha_target": int(velvet_plan["vev_alpha_target"]),
                "vev_final_target": int(velvet_plan["vev_final_target"]),
                "cheapest": list(meta["cheapest"]),
                "richest": list(meta["richest"]),
                "selected_pairs": selected_pairs,
                "pair_trade_count": sum(1 for product in source_map if source_map[product] == "pair"),
                "outright_trade_count": sum(1 for product in source_map if source_map[product] == "outright"),
            }

        memory["monitor"] = strip_monitor
        conversions = 0
        return result, conversions, dump_memory(memory)
