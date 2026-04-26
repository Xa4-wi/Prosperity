from __future__ import annotations

import json
import math
from typing import Dict, List, Optional

from datamodel import Order, OrderDepth, TradingState


DEFAULT_LIMIT = 10
DEFAULT_QUOTE_SIZE = 4
DEFAULT_HALF_SPREAD = 2.0
LIMITS: Dict[str, int] = {}


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


class Trader:
    def _limit(self, product: str) -> int:
        return int(LIMITS.get(product, DEFAULT_LIMIT))

    def _context(self, product: str, od: OrderDepth, saved: dict, position: int) -> Optional[dict]:
        limit = self._limit(product)
        if limit <= 0:
            return None
        mid = mid_price(od)
        if mid is None:
            mid = stable_mid(od)
        if mid is None:
            return None
        micro = micro_price(od)
        if micro is None:
            micro = mid
        spread = float(max(1, (best_ask(od) or int(round(mid + 1))) - (best_bid(od) or int(round(mid - 1)))))
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
        fair = 0.55 * float(mid) + 0.30 * ema_mid + 0.15 * ema_micro
        fair += 0.80 * micro_gap
        fair += 0.70 * imbalance * spread
        fair -= 0.20 * z * move_unit

        local_stretch = float(mid) - ema_mid
        mode = "MARKET_MAKE"
        target = 0.0
        if local_stretch > 2.2 * move_unit and micro_gap <= 0.0 and ret_ema <= 0.0:
            mode = "FADE_SHORT"
            target = -0.35 * limit
        elif local_stretch < -2.2 * move_unit and micro_gap >= 0.0 and ret_ema >= 0.0:
            mode = "FADE_LONG"
            target = 0.35 * limit

        if abs(position) > max(6, int(0.8 * limit)):
            target = 0.0

        quote_bias = 0.0 if mode == "MARKET_MAKE" else 0.10 * local_stretch
        take_bias = 0.06 * micro_gap - 0.04 * ret_ema
        return {
            "fair": fair,
            "target": float(target),
            "mode": mode,
            "spread": spread,
            "move_unit": move_unit,
            "take_bias": take_bias,
            "quote_bias": quote_bias,
        }

    def _trade(self, product: str, od: OrderDepth, position: int, limit: int, ctx: dict) -> List[Order]:
        mgr = OrderManager(product, position, limit)
        fair = float(ctx["fair"])
        target = float(ctx["target"])
        mode = str(ctx["mode"])
        spread = float(ctx["spread"])
        move_unit = float(ctx["move_unit"])
        take_bias = float(ctx["take_bias"])
        quote_bias = float(ctx["quote_bias"])
        bb = best_bid(od)
        ba = best_ask(od)

        take_edge = max(1.0, 0.40 * spread + (0.15 * move_unit if mode == "MARKET_MAKE" else 0.0))
        clear_edge = max(0.75, 0.18 * spread)
        quote_edge = max(DEFAULT_HALF_SPREAD, 0.55 * spread + 0.15 * move_unit)
        quote_size = max(1, min(DEFAULT_QUOTE_SIZE, limit // 2 if limit > 1 else 1))
        take_max = max(1, min(max(2, quote_size + 2), limit))
        soft_limit = max(2, int(0.55 * limit))
        inv_skew = max(1.5, 3.0 * (DEFAULT_LIMIT / max(1.0, float(limit))))

        for ask, volume in sorted(od.sell_orders.items()):
            edge = fair - ask + take_bias
            if edge < take_edge:
                break
            desired = max(0, int(round(target - mgr.projected())))
            qty = min(-volume, max(take_max // 2, desired if desired > 0 else take_max), mgr.buy_cap)
            if qty <= 0:
                break
            mgr.buy(ask, qty)

        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            edge = bid - fair - take_bias
            if edge < take_edge:
                break
            desired = max(0, int(round(mgr.projected() - target)))
            qty = min(volume, max(take_max // 2, desired if desired > 0 else take_max), mgr.sell_cap)
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
        return mgr.flush()

    def run(self, state: TradingState):
        memory = load_memory(state.traderData)
        product_state = memory.setdefault("products", {})
        result: Dict[str, List[Order]] = {}

        for product, od in state.order_depths.items():
            limit = self._limit(product)
            if limit <= 0:
                result[product] = []
                continue
            saved = product_state.setdefault(product, {})
            position = int(state.position.get(product, 0))
            ctx = self._context(product, od, saved, position)
            if ctx is None:
                result[product] = []
                continue
            result[product] = self._trade(product, od, position, limit, ctx)

        return result, 0, dump_memory(memory)
