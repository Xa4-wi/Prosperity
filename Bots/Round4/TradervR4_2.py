from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Tuple

from datamodel import Order, OrderDepth, TradingState


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
MID_VOUCHERS = {"VEV_5000", "VEV_5100"}
HIGH_VOUCHERS = set(VOUCHER_STRIKES) - LOW_VOUCHERS - MID_VOUCHERS

LIMITS: Dict[str, int] = {
    HYDRO: 200,
    VELVET: 200,
    "VEV_4000": 300,
    "VEV_4500": 300,
    "VEV_5000": 300,
    "VEV_5100": 300,
    "VEV_5200": 300,
    "VEV_5300": 300,
    "VEV_5400": 300,
    "VEV_5500": 300,
    "VEV_6000": 300,
    "VEV_6500": 300,
}

OVERLAY_DECAY = 0.90
OVERLAY_CAP = 2.5
BS_T = 6.0 / 365.0

MARK_POLICIES: Dict[str, Dict[str, float | str]] = {
    "Mark 14": {"mode": "follow", "hydro": 0.06, "velvet": 0.16, "voucher_low": 0.30},
    "Mark 67": {"mode": "follow", "velvet": 0.36},
    "Mark 01": {"mode": "follow", "velvet": 0.04, "voucher_high": 0.08},
    "Mark 22": {"mode": "fade", "velvet": 0.12, "voucher_high": 0.18},
    "Mark 38": {"mode": "fade", "hydro": 0.08, "voucher_low": 0.20},
    "Mark 49": {"mode": "fade", "velvet": 0.22},
    "Mark 55": {"mode": "ignore"},
}


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def sign(x: float) -> float:
    return 1.0 if x > 0 else -1.0 if x < 0 else 0.0


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


def stable_mid(od: OrderDepth, levels: int = 2) -> Optional[float]:
    bids = sorted(od.buy_orders.items(), reverse=True)[:levels]
    asks = sorted(od.sell_orders.items())[:levels]
    if not bids or not asks:
        return mid_price(od)
    bid_vol = sum(max(0, volume) for _, volume in bids)
    ask_vol = sum(abs(min(0, volume)) for _, volume in asks)
    if bid_vol <= 0 or ask_vol <= 0:
        return mid_price(od)
    bid_px = sum(price * max(0, volume) for price, volume in bids) / bid_vol
    ask_px = sum(price * abs(min(0, volume)) for price, volume in asks) / ask_vol
    if bid_px >= ask_px:
        return mid_price(od)
    return 0.5 * (bid_px + ask_px)


def micro_price(od: OrderDepth) -> Optional[float]:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None or ba is None or bb >= ba:
        return mid_price(od)
    bid_vol = max(1, od.buy_orders.get(bb, 0))
    ask_vol = max(1, abs(od.sell_orders.get(ba, 0)))
    return (ba * bid_vol + bb * ask_vol) / float(bid_vol + ask_vol)


def book_imbalance(od: OrderDepth, levels: int = 2) -> float:
    bids = sorted(od.buy_orders.items(), reverse=True)[:levels]
    asks = sorted(od.sell_orders.items())[:levels]
    bid_vol = sum(max(0, volume) for _, volume in bids)
    ask_vol = sum(abs(min(0, volume)) for _, volume in asks)
    total = bid_vol + ask_vol
    if total <= 0:
        return 0.0
    return (bid_vol - ask_vol) / total


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bs_call_price(spot: float, strike: float, t: float, vol: float) -> float:
    if spot <= 0 or strike <= 0:
        return max(0.0, spot - strike)
    if t <= 1e-9 or vol <= 1e-6:
        return max(0.0, spot - strike)
    srt = vol * math.sqrt(t)
    if srt <= 1e-9:
        return max(0.0, spot - strike)
    d1 = (math.log(spot / strike) + 0.5 * vol * vol * t) / srt
    d2 = d1 - srt
    return spot * norm_cdf(d1) - strike * norm_cdf(d2)


def bs_call_delta(spot: float, strike: float, t: float, vol: float) -> float:
    if spot <= 0 or strike <= 0:
        return 0.0
    if t <= 1e-9 or vol <= 1e-6:
        return 1.0 if spot > strike else 0.0
    srt = vol * math.sqrt(t)
    if srt <= 1e-9:
        return 1.0 if spot > strike else 0.0
    d1 = (math.log(spot / strike) + 0.5 * vol * vol * t) / srt
    return norm_cdf(d1)


def implied_vol_call(price: float, spot: float, strike: float, t: float) -> Optional[float]:
    intrinsic = max(0.0, spot - strike)
    if spot <= 0 or strike <= 0 or price < intrinsic - 1e-6:
        return None
    lo, hi = 1e-4, 3.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        fair = bs_call_price(spot, strike, t, mid)
        if fair > price:
            hi = mid
        else:
            lo = mid
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
    def _limit(self, product: str) -> int:
        return int(LIMITS.get(product, 0))

    def _basic_book_context(self, od: OrderDepth, saved: dict) -> Optional[dict]:
        mid = mid_price(od)
        if mid is None:
            mid = stable_mid(od)
        if mid is None:
            return None
        micro = micro_price(od)
        if micro is None:
            micro = mid
        bb = best_bid(od)
        ba = best_ask(od)
        spread = float(max(1, (ba or int(round(mid + 1))) - (bb or int(round(mid - 1)))))
        prev_mid = saved.get("last_mid")
        ret = 0.0 if prev_mid is None else float(mid) - float(prev_mid)
        saved["last_mid"] = float(mid)
        saved["ema_mid"] = float(mid) if saved.get("ema_mid") is None else 0.18 * float(mid) + 0.82 * float(saved["ema_mid"])
        saved["ema_micro"] = float(micro) if saved.get("ema_micro") is None else 0.18 * float(micro) + 0.82 * float(saved["ema_micro"])
        saved["ret_ema"] = 0.22 * ret + 0.78 * float(saved.get("ret_ema", 0.0))
        saved["vol_ema"] = 0.20 * abs(ret) + 0.80 * float(saved.get("vol_ema", 0.0))
        ema_mid = float(saved["ema_mid"])
        ema_micro = float(saved["ema_micro"])
        ret_ema = float(saved["ret_ema"])
        vol_ema = max(1.0, float(saved["vol_ema"]), 0.60 * spread)
        imbalance = book_imbalance(od)
        micro_gap = float(micro) - float(mid)
        move_unit = max(1.0, vol_ema, 0.60 * spread)
        z = (float(mid) - ema_mid) / move_unit
        return {
            "mid": float(mid),
            "micro": float(micro),
            "spread": spread,
            "ema_mid": ema_mid,
            "ema_micro": ema_micro,
            "ret_ema": ret_ema,
            "vol_ema": vol_ema,
            "imbalance": imbalance,
            "micro_gap": micro_gap,
            "move_unit": move_unit,
            "z": z,
        }

    def _overlay_scope(self, product: str) -> str:
        if product == HYDRO:
            return "hydro"
        if product == VELVET:
            return "velvet"
        if product in LOW_VOUCHERS:
            return "voucher_low"
        if product in MID_VOUCHERS:
            return "voucher_mid"
        return "voucher_high"

    def _decay_overlay(self, overlay_state: dict) -> None:
        for key in ("hydro", "velvet", "voucher_low", "voucher_mid", "voucher_high"):
            overlay_state[key] = OVERLAY_DECAY * float(overlay_state.get(key, 0.0))

    def _apply_mark_policy(self, overlay_state: dict, mark: Optional[str], product: str, signed_qty: float) -> None:
        if not mark:
            return
        policy = MARK_POLICIES.get(mark)
        if not policy or str(policy.get("mode", "ignore")) == "ignore":
            return
        scope = self._overlay_scope(product)
        weight = float(policy.get(scope, 0.0))
        if weight <= 0.0:
            return
        impact = clamp(abs(signed_qty) / 40.0, 0.20, 1.50)
        direction = sign(signed_qty)
        if str(policy.get("mode")) == "fade":
            direction = -direction
        overlay_state[scope] = clamp(float(overlay_state.get(scope, 0.0)) + weight * impact * direction, -OVERLAY_CAP, OVERLAY_CAP)

    def _update_overlay(self, state: TradingState, memory: dict) -> dict:
        overlay_state = memory.setdefault("overlay", {})
        self._decay_overlay(overlay_state)
        seen = overlay_state.setdefault("seen", {})
        for product, trades in state.market_trades.items():
            last_key = seen.get(product)
            for trade in trades:
                key = f"{trade.timestamp}|{trade.price}|{trade.quantity}|{trade.buyer}|{trade.seller}"
                if key == last_key:
                    continue
                qty = abs(int(trade.quantity))
                self._apply_mark_policy(overlay_state, trade.buyer, product, qty)
                self._apply_mark_policy(overlay_state, trade.seller, product, -qty)
                last_key = key
            if trades:
                seen[product] = last_key
        overlay_state["summary"] = {
            "hydro": round(float(overlay_state.get("hydro", 0.0)), 3),
            "velvet": round(float(overlay_state.get("velvet", 0.0)), 3),
            "voucher_low": round(float(overlay_state.get("voucher_low", 0.0)), 3),
            "voucher_mid": round(float(overlay_state.get("voucher_mid", 0.0)), 3),
            "voucher_high": round(float(overlay_state.get("voucher_high", 0.0)), 3),
        }
        return overlay_state

    def _generic_trade(self, product: str, od: OrderDepth, position: int, limit: int, ctx: dict) -> List[Order]:
        mgr = OrderManager(product, position, limit)
        fair = float(ctx["fair"])
        target = float(ctx["target"])
        spread = float(ctx["spread"])
        move_unit = float(ctx["move_unit"])
        take_bias = float(ctx.get("take_bias", 0.0))
        quote_bias = float(ctx.get("quote_bias", 0.0))
        size_boost = float(ctx.get("size_boost", 0.0))
        take_edge_mult = float(ctx.get("take_edge_mult", 1.0))
        quote_edge_mult = float(ctx.get("quote_edge_mult", 1.0))
        bb = best_bid(od)
        ba = best_ask(od)

        take_edge = max(0.75, (0.45 * spread + 0.10 * move_unit) * take_edge_mult)
        clear_edge = max(0.50, 0.18 * spread)
        quote_edge = max(1.0, (0.55 * spread + 0.12 * move_unit) * quote_edge_mult)
        quote_size = max(1, int(round(clamp(3.0 + size_boost, 1.0, max(1.0, limit / 4.0)))))
        take_max = max(1, int(round(clamp(quote_size + 2.0 + 2.0 * size_boost, 1.0, max(2.0, limit / 3.0)))))
        soft_limit = max(3, int(0.55 * limit))
        inv_skew = max(1.0, 2.5 * (10.0 / max(1.0, float(limit))))

        for ask, volume in sorted(od.sell_orders.items()):
            edge = fair - ask + take_bias
            if edge < take_edge:
                break
            desired = max(0, int(round(target - mgr.projected())))
            qty = min(-volume, max(max(1, take_max // 2), desired if desired > 0 else take_max), mgr.buy_cap)
            if qty <= 0:
                break
            mgr.buy(ask, qty)

        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            edge = bid - fair - take_bias
            if edge < take_edge:
                break
            desired = max(0, int(round(mgr.projected() - target)))
            qty = min(volume, max(max(1, take_max // 2), desired if desired > 0 else take_max), mgr.sell_cap)
            if qty <= 0:
                break
            mgr.sell(bid, qty)

        relative = mgr.projected() - target
        if relative > soft_limit and bb is not None and bb >= fair - clear_edge:
            mgr.sell(bb, min(int(math.ceil(relative - soft_limit)), take_max + 2))
        elif relative < -soft_limit and ba is not None and ba <= fair + clear_edge:
            mgr.buy(ba, min(int(math.ceil((-soft_limit) - relative)), take_max + 2))

        relative = mgr.projected() - target
        reservation = fair + quote_bias - inv_skew * (relative / max(1.0, float(limit)))
        bid_px = int(math.floor(reservation - quote_edge))
        ask_px = int(math.ceil(reservation + quote_edge))
        if bb is not None and ba is not None and bb < ba:
            if (ba - bb) >= 3:
                bid_px = max(bid_px, bb + 1)
                ask_px = min(ask_px, ba - 1)
            else:
                bid_px = min(bid_px, bb)
                ask_px = max(ask_px, ba)
            if bid_px >= ask_px:
                ask_px = bid_px + 1

        if mgr.buy_cap > 0 and (ba is None or bid_px < ba):
            mgr.buy(bid_px, min(quote_size, mgr.buy_cap))
        if mgr.sell_cap > 0 and (bb is None or ask_px > bb):
            mgr.sell(ask_px, min(quote_size, mgr.sell_cap))
        return mgr.orders

    def _hydro_context(self, base: dict, overlay_bias: float, position: int, limit: int) -> dict:
        local_stretch = base["mid"] - base["ema_mid"]
        fair = 0.60 * base["mid"] + 0.25 * base["ema_mid"] + 0.15 * base["ema_micro"]
        fair += 0.40 * base["micro_gap"] + 0.35 * base["imbalance"] * base["spread"]
        fair += 0.20 * overlay_bias * base["move_unit"]
        target = 0.0
        if local_stretch > 1.7 * base["move_unit"] and base["micro_gap"] <= 0.0:
            target = -0.18 * limit
        elif local_stretch < -1.7 * base["move_unit"] and base["micro_gap"] >= 0.0:
            target = 0.18 * limit
        target += 0.10 * limit * clamp(overlay_bias, -1.0, 1.0)
        if abs(position) > int(0.85 * limit):
            target *= 0.4
        return {
            "fair": fair,
            "target": clamp(target, -0.35 * limit, 0.35 * limit),
            "spread": base["spread"],
            "move_unit": base["move_unit"],
            "take_bias": 0.04 * base["micro_gap"] + 0.03 * overlay_bias * base["move_unit"],
            "quote_bias": 0.06 * local_stretch + 0.04 * overlay_bias * base["move_unit"],
            "size_boost": 0.30 * abs(overlay_bias),
            "take_edge_mult": 1.0 - 0.05 * abs(overlay_bias),
            "quote_edge_mult": 1.0,
        }

    def _velvet_context(self, base: dict, overlay_bias: float, position: int, limit: int) -> dict:
        local_stretch = base["mid"] - base["ema_mid"]
        fair = 0.52 * base["mid"] + 0.30 * base["ema_mid"] + 0.18 * base["ema_micro"]
        fair += 0.75 * base["micro_gap"] + 0.65 * base["imbalance"] * base["spread"]
        fair -= 0.18 * base["z"] * base["move_unit"]
        fair += 0.45 * overlay_bias * base["move_unit"]
        target = 0.0
        if local_stretch > 2.1 * base["move_unit"] and base["micro_gap"] <= 0.0 and base["ret_ema"] <= 0.0:
            target = -0.28 * limit
        elif local_stretch < -2.1 * base["move_unit"] and base["micro_gap"] >= 0.0 and base["ret_ema"] >= 0.0:
            target = 0.28 * limit
        target += 0.22 * limit * clamp(overlay_bias, -1.25, 1.25)
        if abs(position) > int(0.80 * limit):
            target *= 0.5
        return {
            "fair": fair,
            "target": clamp(target, -0.45 * limit, 0.45 * limit),
            "spread": base["spread"],
            "move_unit": base["move_unit"],
            "take_bias": 0.08 * base["micro_gap"] + 0.10 * overlay_bias * base["move_unit"],
            "quote_bias": 0.08 * local_stretch + 0.08 * overlay_bias * base["move_unit"],
            "size_boost": 0.55 * abs(overlay_bias),
            "take_edge_mult": clamp(1.0 - 0.10 * abs(overlay_bias), 0.75, 1.05),
            "quote_edge_mult": clamp(1.0 - 0.06 * abs(overlay_bias), 0.80, 1.05),
        }

    def _build_voucher_surface(self, state: TradingState, memory: dict, spot_fair: float) -> dict:
        surface = {"fairs": {}, "meta": {"base_iv": 0.18, "slope": 0.0, "mean_x": 0.0}}
        pts: List[Tuple[float, float, float]] = []
        prod_mem = memory.setdefault("products", {})
        for product, strike in VOUCHER_STRIKES.items():
            od = state.order_depths.get(product)
            if od is None:
                continue
            mid = mid_price(od)
            if mid is None:
                continue
            iv = implied_vol_call(float(mid), max(1.0, spot_fair), float(strike), BS_T)
            if iv is None:
                continue
            x = math.log(float(strike) / max(1.0, spot_fair))
            w = 1.0 / max(1.0, float((best_ask(od) or 0) - (best_bid(od) or 0)))
            pts.append((x, iv, w))
            saved = prod_mem.setdefault(product, {})
            saved["iv_ema"] = iv if saved.get("iv_ema") is None else 0.16 * iv + 0.84 * float(saved["iv_ema"])
        if not pts:
            return surface
        total_w = sum(w for _, _, w in pts)
        mean_x = sum(x * w for x, _, w in pts) / total_w
        mean_iv = sum(iv * w for _, iv, w in pts) / total_w
        var_x = sum(w * (x - mean_x) * (x - mean_x) for x, _, w in pts)
        cov = sum(w * (x - mean_x) * (iv - mean_iv) for x, iv, w in pts)
        slope = cov / var_x if var_x > 1e-9 else 0.0
        surface["meta"] = {"base_iv": mean_iv, "slope": slope, "mean_x": mean_x}
        for product, strike in VOUCHER_STRIKES.items():
            x = math.log(float(strike) / max(1.0, spot_fair))
            struct_iv = clamp(mean_iv + slope * (x - mean_x), 0.03, 2.00)
            saved = prod_mem.setdefault(product, {})
            iv_ema = float(saved.get("iv_ema", struct_iv))
            fair_iv = clamp(0.75 * struct_iv + 0.25 * iv_ema, 0.03, 2.00)
            fair_px = bs_call_price(max(1.0, spot_fair), float(strike), BS_T, fair_iv)
            delta = bs_call_delta(max(1.0, spot_fair), float(strike), BS_T, fair_iv)
            surface["fairs"][product] = {"fair_iv": fair_iv, "fair_px": fair_px, "delta": delta}
        return surface

    def _voucher_context(self, product: str, od: OrderDepth, saved: dict, position: int, limit: int, surface: dict, overlay_bias: float) -> Optional[dict]:
        mid = mid_price(od)
        if mid is None:
            return None
        fair_info = surface.get("fairs", {}).get(product)
        if fair_info is None:
            return None
        spread = float(max(1, (best_ask(od) or int(round(mid + 1))) - (best_bid(od) or int(round(mid - 1)))))
        prev_mid = saved.get("last_mid")
        ret = 0.0 if prev_mid is None else float(mid) - float(prev_mid)
        saved["last_mid"] = float(mid)
        saved["ret_ema"] = 0.22 * ret + 0.78 * float(saved.get("ret_ema", 0.0))
        fair_px = float(fair_info["fair_px"])
        residual = float(mid) - fair_px
        edge_unit = max(1.0, spread, 0.20 * abs(fair_px))
        score = residual / edge_unit
        target = -0.18 * limit * clamp(score, -1.5, 1.5)
        target += 0.14 * limit * clamp(overlay_bias, -1.25, 1.25)
        if product in LOW_VOUCHERS:
            target += 0.05 * limit * clamp(overlay_bias, -1.0, 1.0)
        if product in HIGH_VOUCHERS and overlay_bias < 0.0:
            target += 0.06 * limit * abs(overlay_bias)
        if abs(position) > int(0.80 * limit):
            target *= 0.5
        return {
            "fair": fair_px,
            "target": clamp(target, -0.55 * limit, 0.55 * limit),
            "spread": spread,
            "move_unit": max(1.0, spread, abs(saved["ret_ema"])),
            "take_bias": -0.10 * residual + 0.06 * overlay_bias * max(1.0, spread),
            "quote_bias": -0.04 * residual,
            "size_boost": 0.30 * abs(score) + 0.35 * abs(overlay_bias),
            "take_edge_mult": clamp(1.0 - 0.10 * abs(overlay_bias), 0.72, 1.08),
            "quote_edge_mult": 1.0,
        }

    def run(self, state: TradingState):
        memory = load_memory(state.traderData)
        product_mem = memory.setdefault("products", {})
        overlay_state = self._update_overlay(state, memory)
        result: Dict[str, List[Order]] = {}

        hydro_od = state.order_depths.get(HYDRO)
        if hydro_od is not None:
            saved = product_mem.setdefault(HYDRO, {})
            position = int(state.position.get(HYDRO, 0))
            base = self._basic_book_context(hydro_od, saved)
            if base is None:
                result[HYDRO] = []
            else:
                ctx = self._hydro_context(base, float(overlay_state.get("hydro", 0.0)), position, self._limit(HYDRO))
                result[HYDRO] = self._generic_trade(HYDRO, hydro_od, position, self._limit(HYDRO), ctx)

        velvet_spot_fair = None
        velvet_move = 2.0
        velvet_od = state.order_depths.get(VELVET)
        if velvet_od is not None:
            saved = product_mem.setdefault(VELVET, {})
            position = int(state.position.get(VELVET, 0))
            base = self._basic_book_context(velvet_od, saved)
            if base is None:
                result[VELVET] = []
            else:
                ctx = self._velvet_context(base, float(overlay_state.get("velvet", 0.0)), position, self._limit(VELVET))
                velvet_spot_fair = float(ctx["fair"])
                velvet_move = float(ctx["move_unit"])
                result[VELVET] = self._generic_trade(VELVET, velvet_od, position, self._limit(VELVET), ctx)

        if velvet_spot_fair is None:
            velvet_saved = product_mem.get(VELVET, {})
            velvet_spot_fair = float(velvet_saved.get("ema_mid", 5250.0))

        surface = self._build_voucher_surface(state, memory, velvet_spot_fair)
        memory["voucher_surface"] = {
            "base_iv": round(float(surface["meta"]["base_iv"]), 4),
            "slope": round(float(surface["meta"]["slope"]), 4),
            "mean_x": round(float(surface["meta"]["mean_x"]), 4),
        }

        for product in VOUCHER_STRIKES:
            od = state.order_depths.get(product)
            if od is None:
                continue
            saved = product_mem.setdefault(product, {})
            position = int(state.position.get(product, 0))
            scope = self._overlay_scope(product)
            overlay_bias = float(overlay_state.get(scope, 0.0))
            if product in MID_VOUCHERS:
                overlay_bias += 0.20 * float(overlay_state.get("velvet", 0.0))
            if product in HIGH_VOUCHERS:
                overlay_bias += 0.10 * float(overlay_state.get("velvet", 0.0))
            ctx = self._voucher_context(product, od, saved, position, self._limit(product), surface, overlay_bias)
            if ctx is None:
                result[product] = []
                continue
            result[product] = self._generic_trade(product, od, position, self._limit(product), ctx)

        memory["overlay_report"] = overlay_state.get("summary", {})
        return result, 0, dump_memory(memory)
