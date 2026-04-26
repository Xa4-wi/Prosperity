from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Tuple

try:
    from datamodel import Order, OrderDepth, TradingState
except ModuleNotFoundError:
    from Bots.datamodel import Order, OrderDepth, TradingState


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


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def load_memory(trader_data: str) -> dict:
    if not trader_data:
        return {}
    try:
        obj = json.loads(trader_data)
    except (json.JSONDecodeError, TypeError, ValueError):
        return {}
    return obj if isinstance(obj, dict) else {}


def dump_memory(memory: dict) -> str:
    return json.dumps(memory, separators=(",", ":"))


class OrderManager:
    def __init__(self, product: str, position: int, limit: int) -> None:
        self.product = product
        self.limit = int(limit)
        self.position = int(position)
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


def stable_mid(od: OrderDepth, levels: int = 2) -> Optional[float]:
    bids = sorted(od.buy_orders.items(), reverse=True)[:levels]
    asks = sorted(od.sell_orders.items())[:levels]
    if not bids or not asks:
        return raw_mid(od)
    bid_notional = sum(price * max(0, volume) for price, volume in bids)
    ask_notional = sum(price * abs(min(0, volume)) for price, volume in asks)
    bid_size = sum(max(0, volume) for _, volume in bids)
    ask_size = sum(abs(min(0, volume)) for _, volume in asks)
    if bid_size <= 0 or ask_size <= 0:
        return raw_mid(od)
    return 0.5 * (bid_notional / bid_size + ask_notional / ask_size)


def micro_price(od: OrderDepth) -> Optional[float]:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None or ba is None or bb >= ba:
        return raw_mid(od)
    bid_vol = max(1, od.buy_orders.get(bb, 0))
    ask_vol = max(1, abs(od.sell_orders.get(ba, 0)))
    return (bb * ask_vol + ba * bid_vol) / float(bid_vol + ask_vol)


def book_imbalance(od: OrderDepth, levels: int = 2) -> float:
    bids = sorted(od.buy_orders.items(), reverse=True)[:levels]
    asks = sorted(od.sell_orders.items())[:levels]
    bid_vol = sum(max(0, volume) for _, volume in bids)
    ask_vol = sum(abs(min(0, volume)) for _, volume in asks)
    total = bid_vol + ask_vol
    if total <= 0:
        return 0.0
    return (bid_vol - ask_vol) / total


def round_down(x: float) -> int:
    return math.floor(x)


def round_up(x: float) -> int:
    return math.ceil(x)


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bs_call(spot: float, strike: float, tte: float, sigma: float) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    if tte <= 0.0 or sigma <= 0.0:
        return max(spot - strike, 0.0)
    root_t = math.sqrt(tte)
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * tte) / (sigma * root_t)
    d2 = d1 - sigma * root_t
    return spot * norm_cdf(d1) - strike * norm_cdf(d2)


def bs_delta_call(spot: float, strike: float, tte: float, sigma: float) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    if tte <= 0.0 or sigma <= 0.0:
        return 1.0 if spot > strike else 0.0
    root_t = math.sqrt(tte)
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * tte) / (sigma * root_t)
    return norm_cdf(d1)


def implied_vol_call(price: float, spot: float, strike: float, tte: float, iterations: int = 60) -> float:
    if spot <= 0.0 or strike <= 0.0 or tte <= 0.0:
        return 1e-4
    intrinsic = max(spot - strike, 0.0)
    target = max(price, intrinsic + 1e-4)
    lo, hi = 1e-4, 3.5
    for _ in range(iterations):
        mid = 0.5 * (lo + hi)
        fair = bs_call(spot, strike, tte, mid)
        if fair < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def fit_quadratic(xs: List[float], ys: List[float], ws: List[float]) -> Optional[Tuple[float, float, float]]:
    if len(xs) < 3 or len(xs) != len(ys) or len(xs) != len(ws):
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
    if abs(det) < 1e-12:
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


def repair_call_rows(rows: List[dict], spot: float) -> List[dict]:
    ordered = sorted(rows, key=lambda row: row["strike"])
    repaired: List[dict] = []
    running_max = float("inf")
    for row in ordered:
        intrinsic = max(spot - float(row["strike"]), 0.0)
        guarded = max(float(row["mid"]), intrinsic + 1e-3)
        clipped = min(guarded, running_max)
        running_max = clipped
        repaired.append({**row, "repaired_mid": clipped})
    if len(repaired) >= 3:
        for i in range(1, len(repaired) - 1):
            left = repaired[i - 1]["repaired_mid"]
            mid = repaired[i]["repaired_mid"]
            right = repaired[i + 1]["repaired_mid"]
            floor = 0.5 * (left + right) - max(0.5, 0.0008 * spot)
            if mid < floor:
                repaired[i]["repaired_mid"] = floor
    return repaired


def voucher_cap(product: str) -> int:
    strike = VOUCHER_STRIKES[product]
    if strike <= 4500:
        return 20
    if strike <= 5400:
        return 34
    if strike <= 5500:
        return 20
    return 8


def voucher_trade_cfg(product: str, fair: float, spread: float) -> dict:
    strike = VOUCHER_STRIKES[product]
    if strike <= 4500:
        return {
            "soft_limit": 10,
            "take_max": 8,
            "clear_max": 14,
            "quote_size": 5,
            "take_edge": max(6.0, 0.0042 * fair + 0.28 * spread),
            "clear_edge": max(4.0, 0.0028 * fair + 0.16 * spread),
            "quote_edge": max(6.0, 0.0048 * fair + 0.32 * spread),
            "inv_skew": 2.6,
        }
    if strike <= 5400:
        return {
            "soft_limit": 16,
            "take_max": 12,
            "clear_max": 20,
            "quote_size": 8,
            "take_edge": max(2.0, 0.0032 * fair + 0.22 * spread),
            "clear_edge": max(1.0, 0.0018 * fair + 0.12 * spread),
            "quote_edge": max(2.0, 0.0038 * fair + 0.26 * spread),
            "inv_skew": 1.9,
        }
    if strike <= 5500:
        return {
            "soft_limit": 14,
            "take_max": 8,
            "clear_max": 14,
            "quote_size": 6,
            "take_edge": max(1.0, 0.0028 * fair + 0.22 * spread),
            "clear_edge": max(1.0, 0.0015 * fair + 0.12 * spread),
            "quote_edge": max(1.0, 0.0032 * fair + 0.24 * spread),
            "inv_skew": 1.8,
        }
    return {
        "soft_limit": 8,
        "take_max": 4,
        "clear_max": 8,
        "quote_size": 3,
        "take_edge": max(1.0, 0.60 * spread),
        "clear_edge": max(1.0, 0.40 * spread),
        "quote_edge": max(1.0, 0.70 * spread),
        "inv_skew": 1.4,
    }


def trade_book(
    product: str,
    od: OrderDepth,
    position: int,
    fair: float,
    target: float,
    limit: int,
    cfg: dict,
    take_bias: float = 0.0,
    quote_bias: float = 0.0,
    size_mult: float = 1.0,
) -> List[Order]:
    mgr = OrderManager(product, position, limit)
    bb = best_bid(od)
    ba = best_ask(od)
    target_i = int(round(clamp(target, -float(limit), float(limit))))

    for ask, volume in sorted(od.sell_orders.items()):
        if mgr.projected() >= target_i:
            break
        edge = fair - ask + take_bias
        if edge >= cfg["take_edge"]:
            need = max(0, target_i - mgr.projected())
            mgr.buy(ask, min(-volume, cfg["take_max"], max(need, cfg["take_max"] // 2)))
        else:
            break

    for bid, volume in sorted(od.buy_orders.items(), reverse=True):
        if mgr.projected() <= target_i:
            break
        edge = bid - fair - take_bias
        if edge >= cfg["take_edge"]:
            need = max(0, mgr.projected() - target_i)
            mgr.sell(bid, min(volume, cfg["take_max"], max(need, cfg["take_max"] // 2)))
        else:
            break

    relative = mgr.projected() - target_i
    if relative > cfg["soft_limit"] and bb is not None and bb >= fair - cfg["clear_edge"]:
        mgr.sell(bb, min(int(math.ceil(relative - cfg["soft_limit"])), cfg["clear_max"]))
    elif relative < -cfg["soft_limit"] and ba is not None and ba <= fair + cfg["clear_edge"]:
        mgr.buy(ba, min(int(math.ceil((-cfg["soft_limit"]) - relative)), cfg["clear_max"]))

    relative = mgr.projected() - target_i
    inv_ratio = relative / float(max(1, limit))
    reservation = fair + quote_bias - cfg["inv_skew"] * inv_ratio
    buy_px = round_down(reservation - cfg["quote_edge"])
    sell_px = round_up(reservation + cfg["quote_edge"])
    if bb is not None and ba is not None and bb < ba:
        spread = ba - bb
        if spread >= 3:
            buy_px = max(buy_px, bb + 1)
            sell_px = min(sell_px, ba - 1)
        else:
            buy_px = min(buy_px, bb)
            sell_px = max(sell_px, ba)
        buy_px = min(buy_px, ba - 1)
        sell_px = max(sell_px, bb + 1)
    quote_size = max(1, int(round(cfg["quote_size"] * max(0.25, size_mult) * max(0.30, 1.0 - abs(inv_ratio)))))
    if mgr.buy_cap > 0 and (ba is None or buy_px < ba):
        mgr.buy(buy_px, quote_size)
    if mgr.sell_cap > 0 and (bb is None or sell_px > bb):
        mgr.sell(sell_px, quote_size)
    return mgr.flush()


class Trader:
    def _reset_if_new_day(self, memory: dict, timestamp: int) -> None:
        last_ts = int(memory.get("last_ts", -1))
        if last_ts >= 0 and timestamp < last_ts:
            memory.clear()
        memory["last_ts"] = int(timestamp)
        memory.setdefault("hydro", {})
        memory.setdefault("velvet", {})
        memory.setdefault("voucher", {"local_iv": {}})
        memory.setdefault("diag", {})

    def _build_hydro_context(self, state: TradingState, memory: dict) -> dict:
        od = state.order_depths[HYDROGEL]
        bb = best_bid(od)
        ba = best_ask(od)
        mid = raw_mid(od)
        if mid is None:
            mid = stable_mid(od)
        if mid is None:
            mid = 10000.0
        stable = stable_mid(od)
        if stable is None:
            stable = mid
        micro = micro_price(od)
        if micro is None:
            micro = mid
        spread = float((ba - bb) if bb is not None and ba is not None else 2.0)
        hydro = memory["hydro"]
        hydro["ema_mid"] = float(mid) if hydro.get("ema_mid") is None else 0.10 * float(mid) + 0.90 * float(hydro["ema_mid"])
        book_fair = 0.60 * float(hydro["ema_mid"]) + 0.25 * float(stable) + 0.15 * float(micro)
        dev = abs(float(mid) - float(book_fair))
        hydro["dev_ema"] = dev if hydro.get("dev_ema") is None else 0.12 * dev + 0.88 * float(hydro["dev_ema"])
        sigma = max(1.6, float(hydro["dev_ema"]) * 1.25, 0.85 * spread)
        z = (float(mid) - float(book_fair)) / sigma
        cap = 122.0 if spread <= 20.0 else 90.0
        target = -cap * math.tanh(0.82 * z)
        take_bias = -0.18 * z
        quote_bias = -0.35 * z
        return {
            "fair": float(book_fair),
            "mid": float(mid),
            "z": float(z),
            "sigma": float(sigma),
            "target": float(target),
            "take_bias": float(take_bias),
            "quote_bias": float(quote_bias),
        }

    def _build_velvet_hft_context(self, state: TradingState, memory: dict) -> dict:
        od = state.order_depths[VELVET]
        bb = best_bid(od)
        ba = best_ask(od)
        mid = raw_mid(od)
        if mid is None:
            mid = stable_mid(od)
        if mid is None:
            mid = 5250.0
        stable = stable_mid(od)
        if stable is None:
            stable = mid
        micro = micro_price(od)
        if micro is None:
            micro = mid
        spread = float((ba - bb) if bb is not None and ba is not None else 6.0)
        imbalance = book_imbalance(od)
        velvet = memory["velvet"]
        prev_mid = velvet.get("last_mid")
        ret = 0.0 if prev_mid is None else float(mid) - float(prev_mid)
        velvet["last_mid"] = float(mid)
        velvet["ema_mid"] = float(mid) if velvet.get("ema_mid") is None else 0.20 * float(mid) + 0.80 * float(velvet["ema_mid"])
        velvet["ret_ema"] = 0.24 * ret + 0.76 * float(velvet.get("ret_ema", 0.0))
        velvet["vol_ema"] = 0.22 * abs(ret) + 0.78 * float(velvet.get("vol_ema", 0.0))
        micro_gap_raw = float(micro) - float(mid)
        micro_gap = micro_gap_raw / max(1.0, 0.5 * spread)
        realized_vol = max(1.0, float(velvet["vol_ema"]), 0.55 * spread)
        z = (float(mid) - float(velvet["ema_mid"])) / realized_vol
        fair = float(mid)
        fair += 0.45 * micro_gap_raw
        fair += 0.30 * imbalance * spread
        fair -= 0.25 * z * realized_vol
        ret_ema = float(velvet["ret_ema"])
        toxic_up = micro_gap > 0.80 and imbalance > 0.35 and ret_ema > 0.0
        toxic_down = micro_gap < -0.80 and imbalance < -0.35 and ret_ema < 0.0
        wide_spread = spread >= 5.0
        if z > 1.5 and micro_gap_raw <= 0.0:
            target = -50.0
            mode = "FADE_SHORT"
        elif z < -1.5 and micro_gap_raw >= 0.0:
            target = 50.0
            mode = "FADE_LONG"
        elif toxic_up:
            target = 12.0
            mode = "TOXIC_UP"
        elif toxic_down:
            target = -12.0
            mode = "TOXIC_DOWN"
        elif wide_spread:
            target = 0.0
            mode = "WIDE_SPREAD"
        else:
            target = 0.0
            mode = "CALM"
        take_bias = 0.08 * micro_gap_raw + 0.05 * imbalance * spread - 0.12 * z
        quote_bias = 0.10 * micro_gap_raw + 0.08 * imbalance * spread - 0.16 * z
        return {
            "fair": float(fair),
            "mid": float(mid),
            "spread": float(spread),
            "imbalance": float(imbalance),
            "sigma": float(realized_vol),
            "z": float(z),
            "target": float(target),
            "take_bias": float(take_bias),
            "quote_bias": float(quote_bias),
            "micro_gap": float(micro_gap),
            "micro_gap_raw": float(micro_gap_raw),
            "ret_ema": float(ret_ema),
            "toxic_up": bool(toxic_up),
            "toxic_down": bool(toxic_down),
            "wide_spread": bool(wide_spread),
            "mode": mode,
        }

    def _build_voucher_surface(self, state: TradingState, memory: dict, spot_fair: float) -> dict:
        rows: List[dict] = []
        for product, strike in VOUCHER_STRIKES.items():
            od = state.order_depths.get(product)
            if od is None:
                continue
            bb = best_bid(od)
            ba = best_ask(od)
            if bb is None or ba is None or bb >= ba:
                continue
            mid = 0.5 * (bb + ba)
            spread = float(ba - bb)
            depth = float(max(0, od.buy_orders.get(bb, 0)) + abs(min(0, od.sell_orders.get(ba, 0))))
            rows.append({
                "product": product,
                "strike": float(strike),
                "mid": float(mid),
                "bid": float(bb),
                "ask": float(ba),
                "spread": float(spread),
                "depth": float(depth),
            })
        if not rows:
            return {}

        repaired = repair_call_rows(rows, spot_fair)
        xs: List[float] = []
        ys: List[float] = []
        ws: List[float] = []
        strike_rows: Dict[str, dict] = {}
        for row in repaired:
            strike = float(row["strike"])
            market_iv = implied_vol_call(float(row["repaired_mid"]), spot_fair, strike, TTE_YEARS)
            x = math.log(strike / max(1.0, spot_fair)) / max(1e-6, math.sqrt(TTE_YEARS))
            weight = clamp(float(row["depth"]) / 25.0, 0.4, 2.2) * clamp(3.0 / max(1.0, float(row["spread"])), 0.35, 1.5)
            xs.append(x)
            ys.append(market_iv)
            ws.append(weight)
            strike_rows[row["product"]] = {**row, "x": x, "market_iv": market_iv}

        fit = fit_quadratic(xs, ys, ws)
        fit_conf = 0.30
        if fit is not None:
            a, b, c = fit
            mae = sum(abs(y - (a * x * x + b * x + c)) for x, y in zip(xs, ys)) / len(xs)
            fit_conf = clamp(0.95 - mae / 0.08 + 0.04 * (len(xs) - 5), 0.25, 1.0)
        else:
            a = b = 0.0
            c = sum(ys) / len(ys)

        local_iv_mem = memory["voucher"]["local_iv"]
        surface: Dict[str, dict] = {}
        residuals: List[Tuple[str, float]] = []
        for product, row in strike_rows.items():
            struct_iv = max(0.03, a * row["x"] * row["x"] + b * row["x"] + c)
            prev_local = local_iv_mem.get(product)
            local_iv = row["market_iv"] if prev_local is None else 0.22 * row["market_iv"] + 0.78 * float(prev_local)
            local_iv_mem[product] = float(local_iv)
            local_w = 0.30 if fit_conf >= 0.60 else 0.42
            hybrid_iv = max(0.03, (1.0 - local_w) * struct_iv + local_w * local_iv)
            fair_price = bs_call(spot_fair, float(row["strike"]), TTE_YEARS, hybrid_iv)
            delta = bs_delta_call(spot_fair, float(row["strike"]), TTE_YEARS, hybrid_iv)
            iv_residual = float(row["market_iv"]) - float(hybrid_iv)
            liq_score = clamp((float(row["depth"]) / 24.0) * (2.5 / max(1.0, float(row["spread"]))), 0.20, 1.0)
            band = 0.010 + 0.006 * (1.0 - fit_conf)
            signal = -iv_residual / band
            confidence = clamp(0.35 + 0.45 * fit_conf + 0.20 * liq_score, 0.20, 1.0)
            cap = voucher_cap(product)
            if VOUCHER_STRIKES[product] >= 6000:
                confidence *= 0.55
            if abs(signal) < 0.35:
                signal = 0.0
            target = cap * confidence * math.tanh(0.82 * signal)
            surface[product] = {
                "product": product,
                "strike": int(row["strike"]),
                "mid": float(row["mid"]),
                "bid": float(row["bid"]),
                "ask": float(row["ask"]),
                "spread": float(row["spread"]),
                "depth": float(row["depth"]),
                "market_iv": float(row["market_iv"]),
                "struct_iv": float(struct_iv),
                "local_iv": float(local_iv),
                "hybrid_iv": float(hybrid_iv),
                "iv_residual": float(iv_residual),
                "fair": float(fair_price),
                "delta": float(delta),
                "target": float(target),
                "confidence": float(confidence),
            }
            residuals.append((product, iv_residual))

        target_strip_delta = sum(float(row["target"]) * float(row["delta"]) for row in surface.values())
        if abs(target_strip_delta) > 160.0:
            scale = 160.0 / abs(target_strip_delta)
            for row in surface.values():
                row["target"] *= scale

        surface["_diag"] = {
            "fit_conf": float(fit_conf),
            "usable_strikes": int(len(xs)),
            "avg_abs_resid": float(sum(abs(v) for _, v in residuals) / max(1, len(residuals))),
            "richest": [p for p, _ in sorted(residuals, key=lambda item: item[1], reverse=True)[:3]],
            "cheapest": [p for p, _ in sorted(residuals, key=lambda item: item[1])[:3]],
        }
        return surface

    def _trade_hydrogel(self, state: TradingState, hydro_ctx: dict) -> List[Order]:
        od = state.order_depths[HYDROGEL]
        fair = float(hydro_ctx["fair"])
        sigma = float(hydro_ctx["sigma"])
        cfg = {
            "soft_limit": 18,
            "take_max": 20,
            "clear_max": 34,
            "quote_size": 18,
            "take_edge": max(2.0, 0.45 * sigma),
            "clear_edge": max(1.0, 0.30 * sigma),
            "quote_edge": max(2.5, 0.65 * sigma),
            "inv_skew": 6.5,
        }
        return trade_book(
            HYDROGEL,
            od,
            state.position.get(HYDROGEL, 0),
            fair,
            hydro_ctx["target"],
            LIMITS[HYDROGEL],
            cfg,
            take_bias=float(hydro_ctx["take_bias"]),
            quote_bias=float(hydro_ctx["quote_bias"]),
            size_mult=1.0,
        )

    def _trade_velvet(self, state: TradingState, spot_ctx: dict) -> List[Order]:
        od = state.order_depths[VELVET]
        mgr = OrderManager(VELVET, state.position.get(VELVET, 0), LIMITS[VELVET])
        bb = best_bid(od)
        ba = best_ask(od)
        fair = float(spot_ctx["fair"])
        sigma = float(spot_ctx["sigma"])
        z = float(spot_ctx["z"])
        target = float(spot_ctx["target"])
        pos = int(state.position.get(VELVET, 0))
        toxic_up = bool(spot_ctx["toxic_up"])
        toxic_down = bool(spot_ctx["toxic_down"])
        wide_spread = bool(spot_ctx["wide_spread"])
        take_bias = float(spot_ctx["take_bias"])
        quote_bias = float(spot_ctx["quote_bias"])
        spread = float(spot_ctx["spread"])
        take_edge = max(1.0, 0.22 * sigma + 0.18 * spread)
        clear_edge = max(1.0, 0.16 * sigma + 0.12 * spread)
        quote_edge = max(1.0, 0.28 * sigma + (1.0 if wide_spread else 0.6))
        take_max = 20 if wide_spread else 14
        quote_size = 8 if wide_spread else 6
        soft_limit = 40
        signal_limit = 80
        emergency_limit = 110
        target = clamp(target, -float(signal_limit), float(signal_limit))
        buy_take_allowed = not toxic_down or pos < 0
        sell_take_allowed = not toxic_up or pos > 0

        for ask, volume in sorted(od.sell_orders.items()):
            if not buy_take_allowed:
                break
            if mgr.projected() >= target:
                break
            edge = fair - ask + take_bias
            if edge >= take_edge:
                need = max(0, int(round(target - mgr.projected())))
                mgr.buy(ask, min(-volume, take_max, max(need, take_max // 2)))
            else:
                break

        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            if not sell_take_allowed:
                break
            if mgr.projected() <= target:
                break
            edge = bid - fair - take_bias
            if edge >= take_edge:
                need = max(0, int(round(mgr.projected() - target)))
                mgr.sell(bid, min(volume, take_max, max(need, take_max // 2)))
            else:
                break

        projected = mgr.projected()
        relative = projected - target
        active_soft_limit = 60 if abs(target) > 0 else soft_limit
        if abs(projected) > emergency_limit:
            active_soft_limit = 18
            clear_edge += 0.9
        if relative > active_soft_limit and bb is not None and bb >= fair - clear_edge:
            mgr.sell(bb, min(int(math.ceil(relative - active_soft_limit)), 30))
        elif relative < -active_soft_limit and ba is not None and ba <= fair + clear_edge:
            mgr.buy(ba, min(int(math.ceil((-active_soft_limit) - relative)), 30))

        projected = mgr.projected()
        relative = projected - target
        inv_ratio = relative / float(LIMITS[VELVET])
        reservation = fair + quote_bias - 7.0 * inv_ratio
        buy_px = round_down(reservation - quote_edge)
        sell_px = round_up(reservation + quote_edge)
        if bb is not None and ba is not None and bb < ba:
            if wide_spread and ba - bb >= 3:
                buy_px = max(buy_px, bb + 1)
                sell_px = min(sell_px, ba - 1)
            else:
                buy_px = min(buy_px, bb)
                sell_px = max(sell_px, ba)
            buy_px = min(buy_px, ba - 1)
            sell_px = max(sell_px, bb + 1)

        bid_quote_allowed = not toxic_down or projected < target
        ask_quote_allowed = not toxic_up or projected > target
        if mgr.buy_cap > 0 and bid_quote_allowed and (ba is None or buy_px < ba):
            mgr.buy(buy_px, quote_size)
        if mgr.sell_cap > 0 and ask_quote_allowed and (bb is None or sell_px > bb):
            mgr.sell(sell_px, quote_size)
        return mgr.flush()

    def _trade_voucher(self, state: TradingState, row: dict) -> List[Order]:
        product = row["product"]
        od = state.order_depths[product]
        fair = float(row["fair"])
        spread = float(row["spread"])
        cfg = voucher_trade_cfg(product, fair, spread)
        target = row["target"]
        sig = clamp((fair - float(row["mid"])) / max(1.0, spread), -3.0, 3.0)
        take_bias = 0.12 * sig * max(1.0, spread)
        quote_bias = 0.08 * sig * max(1.0, spread)
        size_mult = clamp(0.45 + 0.65 * float(row["confidence"]), 0.35, 1.0)
        return trade_book(
            product,
            od,
            state.position.get(product, 0),
            fair,
            target,
            LIMITS[product],
            cfg,
            take_bias=take_bias,
            quote_bias=quote_bias,
            size_mult=size_mult,
        )

    def run(self, state: TradingState):
        memory = load_memory(state.traderData)
        self._reset_if_new_day(memory, state.timestamp)
        result: Dict[str, List[Order]] = {product: [] for product in state.order_depths}
        conversions = 0

        if HYDROGEL in state.order_depths:
            hydro_ctx = self._build_hydro_context(state, memory)
            result[HYDROGEL] = self._trade_hydrogel(state, hydro_ctx)
            memory["diag"]["hydro"] = {
                "fair": round(float(hydro_ctx["fair"]), 3),
                "mid": round(float(hydro_ctx["mid"]), 3),
                "z": round(float(hydro_ctx["z"]), 3),
                "sigma": round(float(hydro_ctx["sigma"]), 3),
                "target": int(round(float(hydro_ctx["target"]))),
            }

        if VELVET in state.order_depths:
            spot_ctx = self._build_velvet_hft_context(state, memory)
            surface = self._build_voucher_surface(state, memory, float(spot_ctx["fair"]))
            if surface:
                result[VELVET] = self._trade_velvet(state, spot_ctx)
                for product, row in surface.items():
                    if product.startswith("_") or product not in state.order_depths:
                        continue
                    result[product] = self._trade_voucher(state, row)
                memory["diag"]["surface"] = {
                    "fit_conf": round(float(surface["_diag"]["fit_conf"]), 3),
                    "usable_strikes": int(surface["_diag"]["usable_strikes"]),
                    "avg_abs_resid": round(float(surface["_diag"]["avg_abs_resid"]), 4),
                    "richest": list(surface["_diag"]["richest"]),
                    "cheapest": list(surface["_diag"]["cheapest"]),
                    "strip_delta": round(
                        float(sum(float(state.position.get(product, 0)) * float(row["delta"]) for product, row in surface.items() if not product.startswith("_"))),
                        3,
                    ),
                }
            else:
                result[VELVET] = self._trade_velvet(state, spot_ctx)
                memory["diag"]["surface"] = {
                    "fit_conf": 0.0,
                    "usable_strikes": 0,
                    "avg_abs_resid": 0.0,
                    "richest": [],
                    "cheapest": [],
                    "strip_delta": 0.0,
                }
            memory["diag"]["velvet"] = {
                "fair": round(float(spot_ctx["fair"]), 3),
                "mid": round(float(spot_ctx["mid"]), 3),
                "z": round(float(spot_ctx["z"]), 3),
                "sigma": round(float(spot_ctx["sigma"]), 3),
                "target": int(round(float(spot_ctx["target"]))),
                "micro_gap": round(float(spot_ctx["micro_gap"]), 3),
                "ret_ema": round(float(spot_ctx["ret_ema"]), 3),
                "mode": str(spot_ctx["mode"]),
                "toxic_up": bool(spot_ctx["toxic_up"]),
                "toxic_down": bool(spot_ctx["toxic_down"]),
            }

        return result, conversions, dump_memory(memory)
