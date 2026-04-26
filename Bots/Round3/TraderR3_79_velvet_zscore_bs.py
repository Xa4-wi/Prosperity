from __future__ import annotations

import json
import math
from statistics import median
from typing import Dict, List, Optional, Tuple

try:
    from datamodel import Order, OrderDepth, TradingState
except ModuleNotFoundError:
    from Bots.datamodel import Order, OrderDepth, TradingState


HYDROGEL = "HYDROGEL_PACK"
VELVET = "VELVETFRUIT_EXTRACT"
VOUCHER_PREFIX = "VEV_"

# Adjust these if the official limits differ.
LIMITS: Dict[str, int] = {
    HYDROGEL: 200,
    VELVET: 200,
    "VEV_4000": 200,
    "VEV_4500": 200,
    "VEV_5000": 200,
    "VEV_5100": 200,
    "VEV_5200": 200,
    "VEV_5300": 200,
    "VEV_5400": 200,
    "VEV_5500": 200,
    "VEV_6000": 200,
    "VEV_6500": 200,
}

# For the voucher BS model. The exact exchange convention is unknown from the bot file,
# so this is intentionally simple and robust: one round-day is timestamp 0..100000.
DAY_LENGTH = 100_000.0
DAYS_TO_EXPIRY_START = 7.0
TRADING_DAYS_PER_YEAR = 365.0
RISK_FREE_RATE = 0.0


# -----------------------------
# Generic helpers
# -----------------------------

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


def raw_mid(od: OrderDepth) -> Optional[float]:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None or ba is None or bb >= ba:
        return None
    return 0.5 * (bb + ba)


def spread(od: OrderDepth, fallback: float = 4.0) -> float:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None or ba is None or bb >= ba:
        return fallback
    return float(ba - bb)


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
    # Pulls upward when bid volume is heavy, downward when ask volume is heavy.
    return (ba * bid_vol + bb * ask_vol) / total


def top_levels(orders: Dict[int, int], levels: int, reverse: bool) -> List[Tuple[int, int]]:
    return sorted(orders.items(), reverse=reverse)[:levels]


def book_imbalance(od: OrderDepth, levels: int = 2) -> float:
    if not od.buy_orders or not od.sell_orders:
        return 0.0
    bids = top_levels(od.buy_orders, levels, True)
    asks = top_levels(od.sell_orders, levels, False)
    bid_vol = sum(max(0, v) for _, v in bids)
    ask_vol = sum(abs(v) for _, v in asks)
    total = bid_vol + ask_vol
    if total <= 0:
        return 0.0
    return (bid_vol - ask_vol) / total


def parse_strike(product: str) -> Optional[int]:
    if not product.startswith(VOUCHER_PREFIX):
        return None
    try:
        return int(product.split("_", 1)[1])
    except Exception:
        return None


class OrderManager:
    def __init__(self, product: str, position: int, limit: int) -> None:
        self.product = product
        self.position = int(position)
        self.limit = int(limit)
        self.buy_cap = max(0, self.limit - self.position)
        self.sell_cap = max(0, self.limit + self.position)
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

    def flush(self) -> List[Order]:
        return self.orders


# -----------------------------
# Black-Scholes helpers
# -----------------------------

def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bs_call_price(s: float, k: float, t: float, sigma: float, r: float = RISK_FREE_RATE) -> float:
    if s <= 0 or k <= 0:
        return 0.0
    intrinsic = max(0.0, s - k)
    if t <= 1e-8 or sigma <= 1e-8:
        return intrinsic
    vol_sqrt_t = sigma * math.sqrt(t)
    if vol_sqrt_t <= 1e-12:
        return intrinsic
    d1 = (math.log(s / k) + (r + 0.5 * sigma * sigma) * t) / vol_sqrt_t
    d2 = d1 - vol_sqrt_t
    return s * normal_cdf(d1) - k * math.exp(-r * t) * normal_cdf(d2)


def implied_vol_call(price: float, s: float, k: float, t: float) -> Optional[float]:
    """Binary-search IV. Returns None if the option mid is outside robust bounds."""
    if s <= 0 or k <= 0 or t <= 1e-8:
        return None
    intrinsic = max(0.0, s - k)
    # Market data can be crossed/noisy. Give a little tolerance for deep ITM quotes.
    if price < intrinsic - 3.0 or price > s + 3.0:
        return None
    lo, hi = 1e-4, 3.0
    for _ in range(55):
        mid = 0.5 * (lo + hi)
        model = bs_call_price(s, k, t, mid)
        if model < price:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def time_to_expiry(timestamp: int) -> float:
    # Keeps the model stable near the end. This is a test bot, not a final expiry-calibrated bot.
    day_progress = clamp(float(timestamp) / DAY_LENGTH, 0.0, 1.0)
    days_left = max(0.25, DAYS_TO_EXPIRY_START - day_progress)
    return days_left / TRADING_DAYS_PER_YEAR


# -----------------------------
# Trader
# -----------------------------

class Trader:
    def _init_memory(self, memory: dict, timestamp: int) -> None:
        last_ts = memory.get("last_timestamp")
        if last_ts is not None and timestamp < last_ts:
            memory.clear()
        memory["last_timestamp"] = timestamp

        memory.setdefault("velvet_z", {
            "ema": None,
            "var": 9.0,
            "ret_ema": 0.0,
            "last_mid": None,
            "last_z": 0.0,
        })
        memory.setdefault("bs", {
            "iv": {},       # strike -> smoothed IV
            "resid_var": {}, # product -> smoothed residual variance
        })
        memory.setdefault("hydro", {
            "ema": None,
            "last_mid": None,
        })

    # -------------------------
    # Simple Velvet z-score mean reversion
    # -------------------------
    def _velvet_context(self, state: TradingState, memory: dict) -> Optional[dict]:
        od = state.order_depths.get(VELVET)
        if od is None:
            return None
        mid = raw_mid(od)
        if mid is None:
            mid = memory["velvet_z"].get("last_mid")
        if mid is None:
            return None

        mp = micro_price(od)
        if mp is None:
            mp = mid
        spr = spread(od, 5.0)
        imb = book_imbalance(od, levels=2)

        mem = memory["velvet_z"]
        prev_ema = mem.get("ema")
        prev_mid = mem.get("last_mid")
        prev_var = float(mem.get("var", 9.0))
        prev_ret_ema = float(mem.get("ret_ema", 0.0))

        # Use the previous EMA for the signal so we do not instantly absorb the move.
        ema_for_signal = float(mid) if prev_ema is None else float(prev_ema)
        dev = float(mid) - ema_for_signal
        vol = math.sqrt(max(1.0, prev_var))
        z = dev / vol

        ret = 0.0 if prev_mid is None else float(mid) - float(prev_mid)
        ret_ema = 0.18 * ret + 0.82 * prev_ret_ema

        # Update after signal computation.
        alpha = 0.075
        new_ema = float(mid) if prev_ema is None else (1.0 - alpha) * float(prev_ema) + alpha * float(mid)
        new_dev = float(mid) - new_ema
        new_var = (1.0 - alpha) * prev_var + alpha * (new_dev * new_dev)
        mem["ema"] = new_ema
        mem["var"] = clamp(new_var, 1.0, 400.0)
        mem["ret_ema"] = ret_ema
        mem["last_mid"] = float(mid)
        mem["last_z"] = float(z)

        micro_gap = (float(mp) - float(mid)) / max(1.0, 0.5 * spr)
        trend_filter = ret_ema / max(1.0, vol)

        # z high = price stretched above local mean -> sell/fade.
        # z low  = price stretched below local mean -> buy/fade.
        entry_z = 1.35
        exit_z = 0.35
        max_target = 85
        target = 0
        reason = "FLAT"

        if z <= -entry_z and micro_gap >= -0.20 and trend_filter > -1.10:
            strength = clamp((abs(z) - entry_z) / 1.35, 0.0, 1.0)
            target = int(round(35 + 50 * strength))
            reason = "Z_LONG"
        elif z >= entry_z and micro_gap <= 0.20 and trend_filter < 1.10:
            strength = clamp((abs(z) - entry_z) / 1.35, 0.0, 1.0)
            target = -int(round(35 + 50 * strength))
            reason = "Z_SHORT"
        elif abs(z) <= exit_z:
            target = 0
            reason = "Z_EXIT"
        else:
            # Small residual position in weak/noisy zones; avoids forcing unnecessary crosses.
            target = 0
            reason = "WAIT"

        # Reduce exposure when volatility is unusually high.
        if vol > 4.5:
            target = int(round(target * 0.75))
        if vol > 7.0:
            target = int(round(target * 0.55))

        return {
            "mid": float(mid),
            "ema": float(ema_for_signal),
            "z": float(z),
            "vol": float(vol),
            "micro": float(mp),
            "micro_gap": float(micro_gap),
            "imbalance": float(imb),
            "ret_ema": float(ret_ema),
            "target": int(clamp(target, -max_target, max_target)),
            "reason": reason,
            "spread": float(spr),
        }

    def _trade_velvet_z(self, state: TradingState, ctx: dict) -> List[Order]:
        od = state.order_depths[VELVET]
        pos = int(state.position.get(VELVET, 0))
        mgr = OrderManager(VELVET, pos, LIMITS[VELVET])
        bb = best_bid(od)
        ba = best_ask(od)
        if bb is None or ba is None or bb >= ba:
            return []

        mid = float(ctx["mid"])
        ema = float(ctx["ema"])
        z = float(ctx["z"])
        vol = float(ctx["vol"])
        micro_gap = float(ctx["micro_gap"])
        target = int(ctx["target"])
        spr = float(ctx["spread"])

        # Mean-reversion fair: mostly local EMA, with a small microprice correction.
        fair = ema + 0.45 * micro_gap * max(1.0, 0.5 * spr)
        target_delta = target - pos

        # If target needs a change and current top-of-book is not terrible, take a little.
        take_size = min(18, max(4, int(abs(target_delta) * 0.35)))
        take_edge = max(0.4, 0.15 * vol)
        if target_delta > 0 and ba <= fair + take_edge:
            mgr.buy(ba, min(take_size, -od.sell_orders[ba]))
        elif target_delta < 0 and bb >= fair - take_edge:
            mgr.sell(bb, min(take_size, od.buy_orders[bb]))

        # Recompute projected position after taking.
        projected = mgr.projected()
        rel = projected - target

        # Passive quote around reservation. Push the quote toward the side needed to reach target.
        inv_skew = 5.5
        reservation = fair - inv_skew * (rel / LIMITS[VELVET])
        quote_edge = 1.25 + 0.10 * vol + max(0.0, 0.08 * (spr - 4.0))

        bid_px = math.floor(reservation - quote_edge)
        ask_px = math.ceil(reservation + quote_edge)

        # Join/improve inside spread, but keep the market non-crossed.
        if spr >= 3:
            if target_delta > 0:
                bid_px = max(bid_px, bb + 1)
            else:
                bid_px = max(bid_px, bb)
            if target_delta < 0:
                ask_px = min(ask_px, ba - 1)
            else:
                ask_px = min(ask_px, ba)
        bid_px = min(int(bid_px), ba - 1)
        ask_px = max(int(ask_px), bb + 1)

        # Avoid sending our own crossed pair of passive orders.
        if bid_px >= ask_px:
            if target_delta > 0:
                ask_px = ba
            elif target_delta < 0:
                bid_px = bb
            else:
                bid_px, ask_px = bb, ba

        # Size larger on the side that moves us toward target.
        base = 12
        if abs(z) > 1.8:
            base = 18
        if abs(z) > 2.4:
            base = 24
        buy_size = base if target_delta >= 0 else max(4, base // 2)
        sell_size = base if target_delta <= 0 else max(4, base // 2)

        # Block same-side accumulation if already beyond target.
        if mgr.buy_cap > 0 and projected < target + 20 and bid_px < ba:
            mgr.buy(bid_px, buy_size)
        if mgr.sell_cap > 0 and projected > target - 20 and ask_px > bb:
            mgr.sell(ask_px, sell_size)

        return mgr.flush()

    # -------------------------
    # Simple BS voucher residual interpretation
    # -------------------------
    def _voucher_products(self, state: TradingState) -> List[str]:
        products = []
        for p in state.order_depths:
            if parse_strike(p) is not None:
                products.append(p)
        return sorted(products, key=lambda x: parse_strike(x) or 0)

    def _update_iv_smile(self, state: TradingState, memory: dict, s: float, t: float) -> None:
        bs_mem = memory["bs"]
        iv_mem = bs_mem.setdefault("iv", {})
        fresh_ivs: List[float] = []

        # First pass: compute current IVs from voucher mids.
        current: Dict[str, float] = {}
        for product in self._voucher_products(state):
            od = state.order_depths[product]
            k = parse_strike(product)
            mid = raw_mid(od)
            if k is None or mid is None:
                continue
            iv = implied_vol_call(float(mid), s, float(k), t)
            if iv is None or not math.isfinite(iv):
                continue
            # Ignore pathological near-zero IV from deep ITM quotes below intrinsic.
            iv = clamp(iv, 0.03, 1.50)
            current[product] = iv
            fresh_ivs.append(iv)

        fallback_iv = median(fresh_ivs) if fresh_ivs else 0.22

        # Second pass: smooth per strike/product. Use previous value in trading, update here for next tick.
        for product in self._voucher_products(state):
            old = iv_mem.get(product)
            new_raw = current.get(product, fallback_iv)
            if old is None:
                iv_mem[product] = float(new_raw)
            else:
                iv_mem[product] = float(0.92 * float(old) + 0.08 * float(new_raw))

    def _trade_voucher_bs(self, state: TradingState, memory: dict, product: str, s: float, t: float) -> List[Order]:
        od = state.order_depths[product]
        k = parse_strike(product)
        if k is None:
            return []
        bb = best_bid(od)
        ba = best_ask(od)
        mid = raw_mid(od)
        if bb is None or ba is None or bb >= ba or mid is None:
            return []

        pos = int(state.position.get(product, 0))
        limit = LIMITS.get(product, 200)
        mgr = OrderManager(product, pos, limit)

        bs_mem = memory["bs"]
        iv_mem = bs_mem.setdefault("iv", {})
        resid_var_mem = bs_mem.setdefault("resid_var", {})

        # Use smoothed IV as the model, not same-tick IV, so residual can exist.
        sigma = float(iv_mem.get(product, 0.22))
        model = bs_call_price(s, float(k), t, sigma)
        residual = float(mid) - model  # positive = market expensive, negative = cheap

        old_var = float(resid_var_mem.get(product, 9.0))
        resid_vol = math.sqrt(max(1.0, old_var))
        resid_z = residual / resid_vol
        resid_var_mem[product] = float(0.94 * old_var + 0.06 * residual * residual)

        spr = float(ba - bb)
        intrinsic = max(0.0, s - float(k))
        extrinsic = max(0.0, float(mid) - intrinsic)

        # Avoid the dead far OTM contracts unless there is a very clear edge.
        if float(mid) <= 1.0 and model <= 1.2:
            return []

        # Avoid crossing very wide quotes unless residual is huge.
        min_edge = max(1.0, 0.55 * spr, 0.65 * resid_vol)
        entry_z = 1.55
        target = 0
        if residual <= -min_edge and resid_z <= -entry_z:
            # Cheap call: buy.
            strength = clamp((abs(resid_z) - entry_z) / 1.5, 0.0, 1.0)
            target = int(round(20 + 35 * strength))
        elif residual >= min_edge and resid_z >= entry_z:
            # Expensive call: sell.
            strength = clamp((abs(resid_z) - entry_z) / 1.5, 0.0, 1.0)
            target = -int(round(20 + 35 * strength))
        elif abs(resid_z) < 0.35:
            target = 0
        else:
            # Hold small current inventory unless clearly wrong.
            target = int(clamp(pos, -25, 25))

        target = int(clamp(target, -60, 60))
        delta = target - pos

        # Take only if the executable price is also mispriced versus model.
        take_qty = min(12, max(3, int(abs(delta) * 0.40)))
        if delta > 0 and ba <= model - min_edge * 0.45:
            mgr.buy(ba, min(take_qty, -od.sell_orders[ba]))
        elif delta < 0 and bb >= model + min_edge * 0.45:
            mgr.sell(bb, min(take_qty, od.buy_orders[bb]))

        projected = mgr.projected()
        rel = projected - target

        # Passive one-sided quote around model. This keeps it simple and lets us test BS residual quality.
        quote_edge = max(1.0, 0.45 * spr, 0.45 * resid_vol)
        if projected < target + 10 and mgr.buy_cap > 0:
            bid_px = min(ba - 1, max(bb, math.floor(model - quote_edge)))
            if bid_px < ba:
                mgr.buy(int(bid_px), 8)
        if projected > target - 10 and mgr.sell_cap > 0:
            ask_px = max(bb + 1, min(ba, math.ceil(model + quote_edge)))
            if ask_px > bb:
                mgr.sell(int(ask_px), 8)

        # Store compact debug; only a few fields to avoid traderData bloat.
        bs_mem["last_" + product] = {
            "iv": round(sigma, 4),
            "model": round(model, 2),
            "res": round(residual, 2),
            "z": round(resid_z, 2),
            "ext": round(extrinsic, 2),
        }
        return mgr.flush()

    # -------------------------
    # Small Hydrogel placeholder
    # -------------------------
    def _trade_hydrogel_simple(self, state: TradingState, memory: dict) -> List[Order]:
        od = state.order_depths.get(HYDROGEL)
        if od is None:
            return []
        bb = best_bid(od)
        ba = best_ask(od)
        mid = raw_mid(od)
        if bb is None or ba is None or bb >= ba or mid is None:
            return []

        pos = int(state.position.get(HYDROGEL, 0))
        mgr = OrderManager(HYDROGEL, pos, LIMITS[HYDROGEL])
        imb = book_imbalance(od, 2)
        spr = float(ba - bb)
        # Very simple anchor-local blend, not meant to be the main experiment.
        fair = 0.55 * 10000.0 + 0.45 * float(mid) + 0.70 * imb * max(1.0, 0.5 * spr)
        reservation = fair - 8.0 * (pos / LIMITS[HYDROGEL])
        edge = 2.5 + max(0.0, 0.08 * (spr - 4.0))

        if ba <= fair - 2.0:
            mgr.buy(ba, min(14, -od.sell_orders[ba]))
        if bb >= fair + 2.0:
            mgr.sell(bb, min(14, od.buy_orders[bb]))

        bid_px = min(ba - 1, max(bb + 1 if spr >= 3 else bb, math.floor(reservation - edge)))
        ask_px = max(bb + 1, min(ba - 1 if spr >= 3 else ba, math.ceil(reservation + edge)))
        if bid_px >= ask_px:
            bid_px, ask_px = bb, ba

        if bid_px < ba:
            mgr.buy(int(bid_px), 16)
        if ask_px > bb:
            mgr.sell(int(ask_px), 16)
        return mgr.flush()

    def run(self, state: TradingState):
        memory = load_memory(state.traderData)
        self._init_memory(memory, state.timestamp)
        result: Dict[str, List[Order]] = {product: [] for product in state.order_depths}
        conversions = 0

        # 1) Standalone Velvet z-score mean reversion test.
        velvet_ctx = self._velvet_context(state, memory) if VELVET in state.order_depths else None
        if velvet_ctx is not None:
            result[VELVET] = self._trade_velvet_z(state, velvet_ctx)
            memory["velvet_debug"] = {
                "mid": round(velvet_ctx["mid"], 2),
                "ema": round(velvet_ctx["ema"], 2),
                "z": round(velvet_ctx["z"], 3),
                "vol": round(velvet_ctx["vol"], 3),
                "micro_gap": round(velvet_ctx["micro_gap"], 3),
                "ret_ema": round(velvet_ctx["ret_ema"], 3),
                "target": int(velvet_ctx["target"]),
                "reason": str(velvet_ctx["reason"]),
            }

        # 2) Black-Scholes voucher interpretation, using Velvet spot as the underlying.
        if velvet_ctx is not None:
            s = float(velvet_ctx["mid"])
            t = time_to_expiry(state.timestamp)
            self._update_iv_smile(state, memory, s, t)
            for product in self._voucher_products(state):
                result[product] = self._trade_voucher_bs(state, memory, product, s, t)
            memory["bs_debug"] = {
                "S": round(s, 2),
                "T": round(t, 5),
            }

        # 3) Small placeholder so Hydrogel is not ignored completely. Remove this if you want a pure Velvet/VEV test.
        if HYDROGEL in state.order_depths:
            result[HYDROGEL] = self._trade_hydrogel_simple(state, memory)

        return result, conversions, dump_memory(memory)
