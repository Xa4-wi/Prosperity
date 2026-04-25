from __future__ import annotations

import math
from typing import Dict, Optional, Sequence, Tuple

try:
    from datamodel import OrderDepth
except ModuleNotFoundError:
    from Bots.datamodel import OrderDepth


MIN_IV = 0.02
MAX_IV = 2.80
ROOT_2PI = math.sqrt(2.0 * math.pi)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def ema(prev: Optional[float], value: float, alpha: float) -> float:
    if prev is None:
        return float(value)
    return (1.0 - alpha) * float(prev) + alpha * float(value)


def safe_mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def sign(x: float) -> int:
    if x > 1e-9:
        return 1
    if x < -1e-9:
        return -1
    return 0


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


def raw_mid(od: OrderDepth) -> Optional[float]:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None or ba is None or bb >= ba:
        return None
    return 0.5 * (bb + ba)


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
    total = 0.0
    for volume in od.buy_orders.values():
        total += max(0, int(volume))
    for volume in od.sell_orders.values():
        total += abs(int(volume))
    bb = best_bid(od)
    ba = best_ask(od)
    spread = 1.0 if bb is None or ba is None else max(1.0, float(ba - bb))
    return total / spread


def book_imbalance(od: OrderDepth, levels: int = 2) -> float:
    bids = sorted(od.buy_orders.items(), reverse=True)[:levels]
    asks = sorted(od.sell_orders.items())[:levels]
    buy_depth = sum(max(0, int(volume)) for _, volume in bids)
    sell_depth = sum(abs(int(volume)) for _, volume in asks)
    total = buy_depth + sell_depth
    if total <= 0:
        return 0.0
    return (buy_depth - sell_depth) / total


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / ROOT_2PI


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
    if price >= spot:
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


def solve_3x3(a, b):
    m = [row[:] + [rhs] for row, rhs in zip(a, b)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-12:
            return None
        if pivot != col:
            m[col], m[pivot] = m[pivot], m[col]
        div = m[col][col]
        for j in range(col, 4):
            m[col][j] /= div
        for r in range(3):
            if r == col:
                continue
            factor = m[r][col]
            for j in range(col, 4):
                m[r][j] -= factor * m[col][j]
    return [m[i][3] for i in range(3)]


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
        mean_y = sum(y * w for y, w in zip(ys, ws)) / max(sum(ws), 1e-9)
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


def repair_call_slice(strikes: Sequence[int], prices: Sequence[Optional[float]], spot: float):
    repaired = []
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


def _build_spot_fair(od: OrderDepth, memory: dict, anchor: float = 5250.0) -> float:
    state = memory.setdefault("velvet_state", {"ema_fair": None, "open_mid": None})
    mid = raw_mid(od)
    if mid is None:
        mid = stable_mid(od)
    if mid is None:
        mid = anchor
    micro = microprice(od)
    if micro is None:
        micro = mid
    if state["open_mid"] is None:
        state["open_mid"] = mid
    state["ema_fair"] = ema(state["ema_fair"], float(mid), 0.18)
    spread = float(max(1.0, (best_ask(od) or anchor) - (best_bid(od) or anchor)))
    return (
        0.40 * float(mid)
        + 0.28 * float(micro)
        + 0.18 * float(state["ema_fair"])
        + 0.08 * float(state["open_mid"])
        + 0.06 * anchor
        + 0.55 * book_imbalance(od, levels=2) * max(1.0, 0.5 * spread)
    )


def build_r3_bs_fair_surface(
    order_depths: Dict[str, OrderDepth],
    memory: dict,
    underlying_product: str,
    voucher_strikes: Dict[str, int],
    tte_years: float,
) -> Tuple[float, Dict[str, dict], dict]:
    memory.setdefault("local_iv_ema", {})
    memory.setdefault("avg_abs_resid_ema", None)
    memory.setdefault("peak_avg_abs_resid", 0.0)
    od_under = order_depths[underlying_product]
    spot_fair = _build_spot_fair(od_under, memory)

    products = sorted(voucher_strikes, key=voucher_strikes.get)
    strikes = [voucher_strikes[p] for p in products]
    raw_mid_prices = []
    raw_bid_prices = []
    raw_ask_prices = []
    xs = []
    ys = []
    ws = []
    surface: Dict[str, dict] = {}
    suspicious_quotes = 0

    for product, strike in zip(products, strikes):
        od = order_depths.get(product)
        if od is None:
            raw_mid_prices.append(None)
            raw_bid_prices.append(None)
            raw_ask_prices.append(None)
            continue
        bb = best_bid(od)
        ba = best_ask(od)
        mid = stable_mid(od)
        if bb is None or ba is None or mid is None:
            raw_mid_prices.append(None)
            raw_bid_prices.append(float(bb) if bb is not None else None)
            raw_ask_prices.append(float(ba) if ba is not None else None)
            suspicious_quotes += 1
            continue
        raw_mid_prices.append(float(mid))
        raw_bid_prices.append(float(bb))
        raw_ask_prices.append(float(ba))
        m = math.log(strike / spot_fair)
        market_iv = implied_vol_call(spot_fair, strike, tte_years, float(mid))
        bid_iv = implied_vol_call(spot_fair, strike, tte_years, float(bb))
        ask_iv = implied_vol_call(spot_fair, strike, tte_years, float(ba))
        liq = book_liquidity(od)
        spread = max(1.0, float(ba - bb))
        weight = 0.40 + 0.35 * clamp(liq / 45.0, 0.0, 1.0) + 0.25 * clamp(6.0 / spread, 0.0, 1.0)
        surface[product] = {
            "strike": strike,
            "moneyness": m,
            "bid": int(bb),
            "ask": int(ba),
            "mid": float(mid),
            "spread": spread,
            "liq": liq,
            "market_iv": market_iv,
            "bid_iv": bid_iv,
            "ask_iv": ask_iv,
            "weight": weight,
        }
        if market_iv is not None:
            xs.append(m)
            ys.append(float(market_iv))
            ws.append(weight)

    repaired_mid = repair_call_slice(strikes, raw_mid_prices, spot_fair)
    repaired_bid = repair_call_slice(strikes, raw_bid_prices, spot_fair)
    repaired_ask = repair_call_slice(strikes, raw_ask_prices, spot_fair)

    def build_fit(prices, fallback_coeffs=None):
        fit_xs = []
        fit_ys = []
        fit_ws = []
        for product, strike, price in zip(products, strikes, prices):
            if price is None:
                continue
            iv = implied_vol_call(spot_fair, strike, tte_years, price)
            if iv is None:
                continue
            fit_xs.append(math.log(strike / spot_fair))
            fit_ys.append(iv)
            fit_ws.append(float(surface.get(product, {}).get("weight", 0.8)))
        if not fit_ys and ys:
            fit_xs, fit_ys, fit_ws = xs[:], ys[:], ws[:]
        if fit_ys:
            coeffs, rmse = fit_weighted_quadratic(fit_xs, fit_ys, fit_ws)
            return coeffs, rmse, len(fit_ys)
        if fallback_coeffs is not None:
            return fallback_coeffs, 0.0, 0
        return (0.0, 0.0, 0.0), 0.0, 0

    coeffs_mid, rmse, usable = build_fit(repaired_mid)
    coeffs_bid, _, usable_bid = build_fit(repaired_bid, coeffs_mid)
    coeffs_ask, _, usable_ask = build_fit(repaired_ask, coeffs_mid)
    stability = clamp(0.18 * usable + 0.55 - 7.5 * rmse - 0.04 * suspicious_quotes, 0.0, 1.0)

    struct_abs = []
    for product, strike in voucher_strikes.items():
        if product not in surface:
            continue
        row = surface[product]
        struct_iv = clamp(quad_eval(coeffs_mid, row["moneyness"]), MIN_IV, MAX_IV)
        struct_bid_iv = clamp(quad_eval(coeffs_bid, row["moneyness"]), MIN_IV, MAX_IV)
        struct_ask_iv = clamp(quad_eval(coeffs_ask, row["moneyness"]), MIN_IV, MAX_IV)
        local_prev = memory["local_iv_ema"].get(product)
        if row["market_iv"] is not None:
            local_now = ema(local_prev, float(row["market_iv"]), 0.18)
            memory["local_iv_ema"][product] = local_now
        else:
            local_now = local_prev if local_prev is not None else struct_iv
        row["struct_iv"] = struct_iv
        row["struct_bid_iv"] = struct_bid_iv
        row["struct_ask_iv"] = max(struct_ask_iv, struct_bid_iv)
        row["local_iv"] = float(local_now)
        row["hybrid_iv"] = 0.75 * struct_iv + 0.25 * float(local_now)
        row["fair_price"] = bs_call_price(spot_fair, strike, tte_years, row["hybrid_iv"])
        row["delta"] = bs_delta(spot_fair, strike, tte_years, row["hybrid_iv"])
        row["vega"] = bs_vega(spot_fair, strike, tte_years, row["hybrid_iv"])
        row["iv_residual"] = 0.0 if row["market_iv"] is None else float(row["market_iv"]) - struct_iv
        if row["market_iv"] is not None:
            struct_abs.append(abs(row["iv_residual"]))

    avg_struct_abs = safe_mean(struct_abs)
    memory["avg_abs_resid_ema"] = ema(memory.get("avg_abs_resid_ema"), avg_struct_abs, 0.12)
    broad_hint = avg_struct_abs > max(0.0135, 1.06 * float(memory["avg_abs_resid_ema"] or avg_struct_abs))

    final_abs = []
    pair_agreement_count = 0
    ordered = sorted(surface, key=lambda p: voucher_strikes[p])
    for idx, product in enumerate(ordered):
        row = surface[product]
        local_weight = 0.42 if (stability < 0.60 or broad_hint) else 0.22
        row["hybrid_iv"] = (1.0 - local_weight) * row["struct_iv"] + local_weight * row["local_iv"]
        row["fair_price"] = bs_call_price(spot_fair, row["strike"], tte_years, row["hybrid_iv"])
        row["delta"] = bs_delta(spot_fair, row["strike"], tte_years, row["hybrid_iv"])
        row["vega"] = bs_vega(spot_fair, row["strike"], tte_years, row["hybrid_iv"])
        side_width = max(0.003, 0.5 * (row["struct_ask_iv"] - row["struct_bid_iv"]))
        row["fair_bid_iv"] = clamp(row["hybrid_iv"] - side_width, MIN_IV, MAX_IV)
        row["fair_ask_iv"] = clamp(row["hybrid_iv"] + side_width, MIN_IV, MAX_IV)
        row["fair_bid_price"] = bs_call_price(spot_fair, row["strike"], tte_years, row["fair_bid_iv"])
        row["fair_ask_price"] = bs_call_price(spot_fair, row["strike"], tte_years, row["fair_ask_iv"])
        row["iv_residual"] = 0.0 if row["market_iv"] is None else float(row["market_iv"]) - row["hybrid_iv"]
        final_abs.append(abs(row["iv_residual"]))
        neighbor_signs = []
        for j in (idx - 1, idx + 1):
            if 0 <= j < len(ordered):
                other = surface[ordered[j]]
                if abs(other["iv_residual"]) >= 0.010:
                    neighbor_signs.append(sign(other["iv_residual"]))
        row["neighbor_confirmation"] = sum(1 for s in neighbor_signs if s == sign(row["iv_residual"]) and s != 0) / 2.0

    for left, right in zip(ordered, ordered[1:]):
        lres = float(surface[left]["iv_residual"])
        rres = float(surface[right]["iv_residual"])
        if abs(lres) >= 0.012 and abs(rres) >= 0.012 and sign(lres) == sign(rres) and sign(lres) != 0:
            pair_agreement_count += 1

    avg_abs = safe_mean(final_abs)
    peak_abs = float(memory.get("peak_avg_abs_resid", 0.0))
    peak_abs = max(avg_abs, 0.995 * peak_abs)
    memory["peak_avg_abs_resid"] = peak_abs
    resid_compression = 0.0 if peak_abs <= 1e-9 else clamp(1.0 - avg_abs / peak_abs, 0.0, 1.0)
    broad_dislocation = (
        avg_abs > max(0.0135, 1.03 * float(memory["avg_abs_resid_ema"] or avg_abs))
        and pair_agreement_count >= 2
    )
    cheapest = sorted(ordered, key=lambda p: surface[p]["iv_residual"])[:3]
    richest = sorted(ordered, key=lambda p: surface[p]["iv_residual"], reverse=True)[:3]
    meta = {
        "stability": stability,
        "usable": usable,
        "usable_bid": usable_bid,
        "usable_ask": usable_ask,
        "rmse": rmse,
        "avg_abs_iv_residual": avg_abs,
        "pair_agreement_count": pair_agreement_count,
        "broad_dislocation": broad_dislocation,
        "resid_compression": resid_compression,
        "cheapest": cheapest,
        "richest": richest,
    }
    return spot_fair, surface, meta
