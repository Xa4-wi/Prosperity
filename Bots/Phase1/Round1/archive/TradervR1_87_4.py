from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Tuple

try:
    from datamodel import Order, OrderDepth, TradingState
except ModuleNotFoundError:
    from trader_factory.core.datamodel import Order, OrderDepth, TradingState


PRODUCT_LIMITS = {
    "ASH_COATED_OSMIUM": 80,
    "INTARIAN_PEPPER_ROOT": 80,
}


DEFAULT_ASH_PARAMS = {
    "ENABLED": True,
    "STRATEGY_NAME": "local_fair_inventory_skew",
    "REFERENCE_PRICE": 10000.0,
    "FAIR_MODE": "local",
    "ANCHOR_WEIGHT": 0.45,
    "STABLE_MID_WEIGHT": 0.55,
    "WALL_MID_BLEND": 0.25,
    "LOCAL_MICRO_WEIGHT": 0.25,
    "LOCAL_IMBALANCE_BIAS": 0.12,
    "DEPTH_IMPACT_SCALE": 24.0,
    "DEPTH_FLOOR": 8.0,
    "USE_INVENTORY_SKEW": True,
    "INVENTORY_SKEW": 0.10,
    "QUOTE_HALF_SPREAD": 4.5,
    "JOIN_EDGE": 1.00,
    "FRONT_SIZE": 12,
    "BACK_SIZE": 0,
    "BACK_OFFSET": 2,
    "POSITION_CAP_BUFFER": 4,
    "TAKE_EDGE": 1.20,
    "TAKE_SIZE": 4,
    "TAKE_MAX_POS": 62,
    "TOXIC_WIDEN": 1.50,
    "TOXIC_SIZE_MULT": 0.60,
    "ADVERSE_IMBALANCE": 0.22,
    "WIDE_SPREAD": 18.0,
    "ALLOW_JOIN": False,
    "USE_LAYERED_QUOTES": False,
    "USE_TOXICITY_GATE": False,
    "USE_HYBRID_TAKING": False,
    "USE_WALL_MID_BLEND": True,
    "USE_DEPTH_IMPACT": True,
}


DEFAULT_IPR_PARAMS = {
    "ENABLED": True,
    "DRIFT_PER_TIMESTAMP": 0.0026009226,
    "RESIDUAL_ALPHA": 0.10,
    "SPREAD_ALPHA": 0.08,
    "LOOKAHEAD_BONUS": 4.90,
    "BASE_CARRY": 7.70,
    "EARLY_LONG_BIAS": 43.20,
    "EDGE_TARGET_SCALE": 12.0,
    "ZSCORE_BUY_BONUS": 12.0,
    "ZSCORE_SELL_PENALTY": 8.0,
    "MAX_LONG_TARGET": 76.0,
    "MAX_SHORT_TARGET": 20,
    "EARLY_ACCUM_END": 0.42,
    "INVENTORY_SKEW": 0.078,
    "BASE_TAKE_EDGE": 2.7678379562,
    "BASE_QUOTE_EDGE": 5.351603402,
    "SOFT_LIMIT": 52,
    "PASSIVE_FRONT_SIZE": 9,
    "PASSIVE_BACK_SIZE": 6,
    "PASSIVE_BUY_BUFFER": 18,
    "PASSIVE_SELL_BUFFER": 8,
    "OVEREXTENSION_Z": 1.05,
    "BULLISH_IMBALANCE": 0.05,
    "CHEAP_ACCUM_END": 0.56,
    "CHEAP_ACCUM_TAKE_PENALTY": 0.08,
    "CHEAP_ACCUM_QUOTE_EDGE_BONUS": 0.45,
    "CHEAP_ACCUM_FRONT_SIZE_BONUS": 1,
    "CHEAP_ACCUM_BACK_SIZE_BONUS": 1,
    "CHEAP_ACCUM_Z_RELAX": -0.55,
    "CHEAP_ACCUM_TARGET_BUFFER": 20,
}


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def ema(prev: Optional[float], current: float, alpha: float) -> float:
    if prev is None:
        return current
    return (1.0 - alpha) * prev + alpha * current


class Book:
    def __init__(self, depth: Optional[OrderDepth]) -> None:
        self.valid = False
        self.buy_levels: List[Tuple[int, int]] = []
        self.sell_levels: List[Tuple[int, int]] = []
        self.best_bid = self.best_ask = 0
        self.best_bid_vol = self.best_ask_vol = 0
        self.mid = self.micro = self.spread_val = self.imbalance = 0.0

        if depth is None:
            return
        self.buy_levels = sorted(
            ((int(p), int(v)) for p, v in depth.buy_orders.items()),
            key=lambda x: x[0],
            reverse=True,
        )
        self.sell_levels = sorted(
            ((int(p), abs(int(v))) for p, v in depth.sell_orders.items()),
            key=lambda x: x[0],
        )
        if not self.buy_levels or not self.sell_levels:
            return
        self.best_bid, self.best_bid_vol = self.buy_levels[0]
        self.best_ask, self.best_ask_vol = self.sell_levels[0]
        if self.best_bid >= self.best_ask:
            return
        self.mid = (self.best_bid + self.best_ask) / 2.0
        self.spread_val = float(self.best_ask - self.best_bid)
        total = self.best_bid_vol + self.best_ask_vol
        if total > 0:
            self.micro = (
                self.best_ask * self.best_bid_vol + self.best_bid * self.best_ask_vol
            ) / total
            self.imbalance = (self.best_bid_vol - self.best_ask_vol) / total
        else:
            self.micro = self.mid
        self.valid = True


class Manager:
    def __init__(self, product: str, position: int, limit: int) -> None:
        self.product = product
        self.position = int(position)
        self.limit = int(limit)
        self.buy_cap = max(0, limit - position)
        self.sell_cap = max(0, limit + position)
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


class AshCoatedOsmiumTrader:
    def __init__(self, params: dict) -> None:
        self.p = params

    def _stable_mid(self, book: Book) -> float:
        bid_levels = book.buy_levels[:3]
        ask_levels = book.sell_levels[:3]
        bid_vol = sum(vol for _, vol in bid_levels)
        ask_vol = sum(vol for _, vol in ask_levels)
        if bid_vol <= 0 or ask_vol <= 0:
            return book.mid

        popular_bid = sum(px * vol for px, vol in bid_levels) / bid_vol
        popular_ask = sum(px * vol for px, vol in ask_levels) / ask_vol
        popular_mid = (popular_bid + popular_ask) / 2.0

        if not self.p.get("USE_WALL_MID_BLEND", True):
            return popular_mid

        wall_bid = max(bid_levels, key=lambda x: (x[1], x[0]))[0]
        wall_ask = min(ask_levels, key=lambda x: (-x[1], x[0]))[0]
        wall_mid = (wall_bid + wall_ask) / 2.0
        blend = float(self.p["WALL_MID_BLEND"])
        return (1.0 - blend) * popular_mid + blend * wall_mid

    def _local_fair(self, book: Book) -> float:
        stable_mid = self._stable_mid(book)
        base = (
            float(self.p["ANCHOR_WEIGHT"]) * float(self.p["REFERENCE_PRICE"])
            + float(self.p["STABLE_MID_WEIGHT"]) * stable_mid
        )
        depth = max(float(self.p["DEPTH_FLOOR"]), float(book.best_bid_vol + book.best_ask_vol))
        depth_scale = float(self.p["DEPTH_IMPACT_SCALE"]) / depth if self.p.get("USE_DEPTH_IMPACT", True) else 0.0
        return (
            base
            + float(self.p["LOCAL_MICRO_WEIGHT"]) * (book.micro - book.mid)
            + (float(self.p["LOCAL_IMBALANCE_BIAS"]) + depth_scale) * book.imbalance
        )

    def _fair(self, book: Book) -> float:
        if self.p.get("FAIR_MODE") == "anchor":
            return float(self.p["REFERENCE_PRICE"])
        return self._local_fair(book)

    def _reservation(self, fair: float, projected_pos: int) -> float:
        if not self.p.get("USE_INVENTORY_SKEW", False):
            return fair
        return fair - float(self.p["INVENTORY_SKEW"]) * projected_pos

    def _toxic_flags(self, book: Book) -> Tuple[bool, bool, bool]:
        adverse = float(self.p["ADVERSE_IMBALANCE"])
        wide = book.spread_val >= float(self.p["WIDE_SPREAD"])
        bid_toxic = book.imbalance < -adverse and book.micro < book.mid
        ask_toxic = book.imbalance > adverse and book.micro > book.mid
        severe = wide or abs(book.imbalance) >= adverse + 0.10
        return bid_toxic, ask_toxic, severe

    def build_orders(self, state: TradingState, memory: dict) -> Tuple[List[Order], dict]:
        if not self.p.get("ENABLED", True):
            return [], memory

        book = Book(state.order_depths.get("ASH_COATED_OSMIUM"))
        if not book.valid:
            return [], memory

        position = int(state.position.get("ASH_COATED_OSMIUM", 0))
        mgr = Manager("ASH_COATED_OSMIUM", position, PRODUCT_LIMITS["ASH_COATED_OSMIUM"])
        fair = self._fair(book)
        pos = mgr.projected()
        reservation = self._reservation(fair, pos)
        bid_toxic, ask_toxic, severe_toxic = self._toxic_flags(book)
        half_spread = float(self.p["QUOTE_HALF_SPREAD"])
        buy_edge = reservation - book.best_ask
        sell_edge = book.best_bid - reservation

        if self.p.get("USE_HYBRID_TAKING", False):
            take_edge = float(self.p["TAKE_EDGE"])
            take_size = int(self.p["TAKE_SIZE"])
            max_pos = int(self.p["TAKE_MAX_POS"])
            if buy_edge >= take_edge and pos < max_pos and not (bid_toxic and pos > 0):
                mgr.buy(book.best_ask, min(book.best_ask_vol, take_size, max_pos - pos))
            pos = mgr.projected()
            if sell_edge >= take_edge and pos > -max_pos and not (ask_toxic and pos < 0):
                mgr.sell(book.best_bid, min(book.best_bid_vol, take_size, pos + max_pos))

        pos = mgr.projected()
        reservation = self._reservation(fair, pos)
        front_buy = int(round(reservation - half_spread))
        front_sell = int(round(reservation + half_spread))

        if self.p.get("ALLOW_JOIN", True):
            front_buy = max(front_buy, book.best_bid)
            front_sell = min(front_sell, book.best_ask)
            if reservation - book.best_bid > float(self.p["JOIN_EDGE"]):
                front_buy = min(book.best_ask - 1, max(front_buy, book.best_bid + 1))
            if book.best_ask - reservation > float(self.p["JOIN_EDGE"]):
                front_sell = max(book.best_bid + 1, min(front_sell, book.best_ask - 1))

        front_buy = min(front_buy, book.best_ask - 1)
        front_sell = max(front_sell, book.best_bid + 1)
        back_buy = min(front_buy - int(self.p["BACK_OFFSET"]), book.best_ask - 1)
        back_sell = max(front_sell + int(self.p["BACK_OFFSET"]), book.best_bid + 1)

        buy_size = int(self.p["FRONT_SIZE"])
        sell_size = int(self.p["FRONT_SIZE"])
        allow_bid = pos < PRODUCT_LIMITS["ASH_COATED_OSMIUM"] - int(self.p["POSITION_CAP_BUFFER"])
        allow_ask = pos > -PRODUCT_LIMITS["ASH_COATED_OSMIUM"] + int(self.p["POSITION_CAP_BUFFER"])

        if self.p.get("USE_TOXICITY_GATE", False):
            widen = float(self.p["TOXIC_WIDEN"])
            size_mult = float(self.p["TOXIC_SIZE_MULT"])
            if bid_toxic:
                front_buy = int(round(front_buy - widen))
                buy_size = max(1, int(round(buy_size * size_mult)))
                if severe_toxic and pos > 0:
                    allow_bid = False
            if ask_toxic:
                front_sell = int(round(front_sell + widen))
                sell_size = max(1, int(round(sell_size * size_mult)))
                if severe_toxic and pos < 0:
                    allow_ask = False
            front_buy = min(front_buy, book.best_ask - 1)
            front_sell = max(front_sell, book.best_bid + 1)

        if allow_bid and front_buy > 0 and front_buy < book.best_ask:
            mgr.buy(front_buy, buy_size)
            if self.p.get("USE_LAYERED_QUOTES", False):
                back_size = int(self.p["BACK_SIZE"])
                if back_size > 0 and back_buy > 0 and back_buy < book.best_ask:
                    mgr.buy(back_buy, back_size)
        if allow_ask and front_sell > book.best_bid:
            mgr.sell(front_sell, sell_size)
            if self.p.get("USE_LAYERED_QUOTES", False):
                back_size = int(self.p["BACK_SIZE"])
                if back_size > 0 and back_sell > book.best_bid:
                    mgr.sell(back_sell, back_size)

        return mgr.orders, memory


class IntarianPepperRootTrader:
    def __init__(self, params: dict) -> None:
        self.p = params

    def build_orders(self, state: TradingState, memory: dict) -> Tuple[List[Order], dict]:
        if not self.p.get("ENABLED", True):
            return [], memory

        book = Book(state.order_depths.get("INTARIAN_PEPPER_ROOT"))
        if not book.valid:
            return [], memory

        position = int(state.position.get("INTARIAN_PEPPER_ROOT", 0))
        mgr = Manager("INTARIAN_PEPPER_ROOT", position, PRODUCT_LIMITS["INTARIAN_PEPPER_ROOT"])
        timestamp = int(getattr(state, "timestamp", 0))
        progress = clamp(timestamp / 999900.0, 0.0, 1.0)

        ps = memory.get("IPR_STATE", {})
        if not isinstance(ps, dict):
            ps = {}

        initialized = bool(ps.get("initialized", False))
        anchor = float(ps.get("anchor", 0.0))
        residual_ema_val = float(ps.get("residual_ema", 0.0))
        spread_ema_val = float(ps.get("spread_ema", 13.0))
        last_ts = float(ps.get("last_ts", -1.0))

        if last_ts >= 0 and timestamp < last_ts:
            initialized = False
            anchor = 0.0
            residual_ema_val = 0.0
            spread_ema_val = 13.0

        drift = float(self.p["DRIFT_PER_TIMESTAMP"])
        trend_line = anchor + drift * timestamp

        if not initialized:
            anchor = round(book.mid / 1000.0) * 1000.0
            trend_line = anchor
            residual_ema_val = 0.0
            spread_ema_val = float(book.spread_val)
            initialized = True
        else:
            spread_ema_val = ema(spread_ema_val, book.spread_val, float(self.p["SPREAD_ALPHA"]))

        residual = book.mid - trend_line
        residual_ema_val = ema(residual_ema_val, residual, float(self.p["RESIDUAL_ALPHA"]))

        half_spread = max(1.0, book.spread_val / 2.0)
        flow_fair = book.mid + book.imbalance * half_spread
        lookahead = float(self.p["LOOKAHEAD_BONUS"]) * (1.0 - 0.65 * progress)
        fair = (
            0.60 * trend_line
            + 0.12 * book.mid
            + 0.10 * book.micro
            + 0.10 * flow_fair
            + 0.08 * (trend_line + residual)
            + lookahead
        )

        spread_scale = max(4.0, spread_ema_val * 0.45)
        zscore = residual / spread_scale

        edge = fair - book.mid
        target = float(self.p["BASE_CARRY"])
        early_factor = max(0.0, 1.0 - progress / 0.85)
        target += float(self.p["EARLY_LONG_BIAS"]) * early_factor
        target += float(self.p["EDGE_TARGET_SCALE"]) * edge

        if zscore < 0.0:
            target += float(self.p["ZSCORE_BUY_BONUS"]) * min(1.0, abs(zscore) / 1.8)
        if zscore > 0.45:
            target -= float(self.p["ZSCORE_SELL_PENALTY"]) * min(1.0, (zscore - 0.45) / 1.4)
        if book.imbalance < -0.18 and book.micro < book.mid:
            target -= 6.0

        bullish = (
            zscore < float(self.p["OVEREXTENSION_Z"])
            and book.imbalance >= float(self.p["BULLISH_IMBALANCE"])
            and book.micro >= book.mid
        )
        if bullish:
            target += 8.0

        if progress < 0.18 and zscore <= 0.45:
            target = max(target, 32.0)
        elif progress < 0.35 and zscore <= 0.25:
            target = max(target, 24.0)
        if progress > 0.85 and zscore > 1.25:
            target -= 8.0

        target_int = int(clamp(target, -int(self.p["MAX_SHORT_TARGET"]), int(self.p["MAX_LONG_TARGET"])))
        reservation = fair - (mgr.projected() - target_int) * float(self.p["INVENTORY_SKEW"])

        base_take = float(self.p["BASE_TAKE_EDGE"])
        buy_te = base_take
        sell_te = base_take + 0.55
        pos = mgr.projected()
        if pos < target_int:
            buy_te -= 0.35
        if pos > target_int:
            sell_te -= 0.05
        if zscore < -0.45:
            buy_te -= 0.30
        elif zscore > 0.85:
            sell_te -= 0.15
        if bullish:
            buy_te -= 0.10
            sell_te += 0.90
        if progress < 0.55 and pos < target_int:
            sell_te += 0.25
        if pos < max(20, target_int - 10):
            sell_te += 0.55
        if (
            progress < float(self.p["CHEAP_ACCUM_END"])
            and pos < target_int
            and zscore > float(self.p["CHEAP_ACCUM_Z_RELAX"])
        ):
            buy_te += float(self.p["CHEAP_ACCUM_TAKE_PENALTY"])
        buy_te = max(0.35, buy_te)
        sell_te = max(1.05, sell_te)

        if reservation - book.best_ask >= buy_te and mgr.buy_cap > 0:
            qty = min(book.best_ask_vol, 16, max(0, target_int + 16 - mgr.projected()))
            mgr.buy(book.best_ask, qty)

        if book.best_bid - reservation >= sell_te and mgr.sell_cap > 0:
            pos = mgr.projected()
            qty = min(book.best_bid_vol, 16, max(0, pos - (target_int - 4)))
            if bullish and pos < max(26, target_int - 6):
                qty = 0
            elif bullish and pos > 0:
                qty = min(qty, 4)
            mgr.sell(book.best_bid, qty)

        buy_qe = float(self.p["BASE_QUOTE_EDGE"])
        sell_qe = float(self.p["BASE_QUOTE_EDGE"]) + 0.75
        pos = mgr.projected()
        if pos < target_int:
            buy_qe -= 0.55
        if pos > target_int:
            sell_qe -= 0.10
        if zscore < -0.55:
            buy_qe -= 0.30
        elif zscore > 1.00:
            sell_qe -= 0.15

        cheap_accum = (
            progress < float(self.p["CHEAP_ACCUM_END"])
            and pos < target_int
            and zscore > float(self.p["CHEAP_ACCUM_Z_RELAX"])
        )
        if cheap_accum:
            buy_qe -= float(self.p["CHEAP_ACCUM_QUOTE_EDGE_BONUS"])

        front_buy = math.floor(reservation - buy_qe)
        front_sell = math.ceil(reservation + sell_qe)
        if bullish and pos < target_int:
            front_buy = max(front_buy, book.best_bid + 1)
        elif cheap_accum and pos < target_int:
            front_buy = max(front_buy, book.best_bid + 1)
        if bullish and pos > 0:
            front_sell += 2

        front_buy = min(front_buy, book.best_ask - 1)
        front_sell = max(front_sell, book.best_bid + 1)
        back_buy = min(front_buy - 2, book.best_ask - 1)
        back_sell = max(front_sell + 2, book.best_bid + 1)

        allow_sell = True
        if progress < float(self.p["EARLY_ACCUM_END"]) and pos < target_int - 6:
            allow_sell = False
        if bullish and pos < max(24, target_int - 4):
            allow_sell = False

        buy_front_sz = int(self.p["PASSIVE_FRONT_SIZE"]) + (int(self.p["CHEAP_ACCUM_FRONT_SIZE_BONUS"]) if cheap_accum else 0)
        buy_back_sz = int(self.p["PASSIVE_BACK_SIZE"]) + (int(self.p["CHEAP_ACCUM_BACK_SIZE_BONUS"]) if cheap_accum else 0)
        buy_cap_target = target_int + (
            int(self.p["CHEAP_ACCUM_TARGET_BUFFER"]) if cheap_accum else int(self.p["PASSIVE_BUY_BUFFER"])
        )

        quotes: List[Tuple[str, int, int]] = []
        if front_buy > 0 and front_buy < book.best_ask:
            quotes.append(("buy", front_buy, buy_front_sz))
            if back_buy > 0 and back_buy < book.best_ask:
                quotes.append(("buy", back_buy, buy_back_sz))
        if allow_sell and front_sell > book.best_bid:
            sell_front = max(3, int(self.p["PASSIVE_FRONT_SIZE"]) - (3 if bullish else 1))
            sell_back = max(2, int(self.p["PASSIVE_BACK_SIZE"]) - (2 if bullish else 1))
            quotes.append(("sell", front_sell, sell_front))
            if back_sell > book.best_bid:
                quotes.append(("sell", back_sell, sell_back))

        for side, price, size in quotes:
            pos = mgr.projected()
            if side == "buy" and pos < buy_cap_target:
                qty = min(size, mgr.buy_cap, max(0, buy_cap_target - pos))
                mgr.buy(price, qty)
            elif side == "sell" and pos > target_int - int(self.p["PASSIVE_SELL_BUFFER"]):
                qty = min(size, mgr.sell_cap, max(0, pos - (target_int - int(self.p["PASSIVE_SELL_BUFFER"]))))
                mgr.sell(price, qty)

        memory["IPR_STATE"] = {
            "anchor": anchor,
            "residual_ema": residual_ema_val,
            "spread_ema": spread_ema_val,
            "last_ts": float(timestamp),
            "initialized": True,
        }
        return mgr.orders, memory


class Trader:
    def __init__(self) -> None:
        self.ash = AshCoatedOsmiumTrader(DEFAULT_ASH_PARAMS)
        self.ipr = IntarianPepperRootTrader(DEFAULT_IPR_PARAMS)

    def _load_memory(self, trader_data: str) -> dict:
        if not trader_data:
            return {}
        try:
            parsed = json.loads(trader_data)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    def run(self, state: TradingState):
        memory = self._load_memory(state.traderData if hasattr(state, "traderData") else "")
        result: Dict[str, List[Order]] = {}

        if "ASH_COATED_OSMIUM" in state.order_depths:
            ash_orders, memory = self.ash.build_orders(state, memory)
            result["ASH_COATED_OSMIUM"] = ash_orders

        if "INTARIAN_PEPPER_ROOT" in state.order_depths:
            ipr_orders, memory = self.ipr.build_orders(state, memory)
            result["INTARIAN_PEPPER_ROOT"] = ipr_orders

        trader_data = json.dumps(memory, separators=(",", ":"))
        return result, 0, trader_data
