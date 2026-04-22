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
    "REFERENCE_PRICE": 10000.0,
    "ANCHOR_WEIGHT": 0.50,
    "STABLE_MID_WEIGHT": 0.50,
    "WALL_MID_BLEND": 0.25,
    "LOCAL_MICRO_WEIGHT": 0.30,
    "LOCAL_IMBALANCE_BIAS": 0.15,
    "DEPTH_IMPACT_SCALE": 30.0,
    "DEPTH_FLOOR": 8.0,
    "INVENTORY_SKEW": 0.07,
    "INVENTORY_CURVE": 2.50,
    "BASE_EDGE": -0.25,
    "JOIN_EDGE": 1.45,
    "FRONT_SIZE": 15,
    "BACK_SIZE": 5,
    "SOFT_LIMIT": 60,
    "TAKE_L1_EDGE": 1.05,
    "TAKE_L1_SIZE": 4,
    "TAKE_L2_EDGE": 1.80,
    "TAKE_L2_SIZE": 8,
    "TAKE_L3_EDGE": 3.80,
    "TAKE_L3_SIZE": 14,
    "MIN_QUOTE_EDGE": 2.10,
    "ADVERSE_IMBALANCE": 0.22,
    "STRONG_IMBALANCE": 0.16,
    "NORMAL_TAKE_EDGE": 1.25,
    "TOXIC_TAKE_EDGE": 1.95,
    "SPLIT_FAIR_STYLE": "guarded",
    "FAST_SIGNAL_CLIP": 2.00,
    "FAST_TAKE_WEIGHT": 0.80,
    "FAST_QUOTE_WEIGHT": 0.35,
    "REGIME_STYLE": "full",
    "CALM_DEPTH_MIN": 26.0,
    "CALM_SPREAD_MAX": 15.0,
    "CALM_IMBALANCE_MAX": 0.12,
    "DISLOCATION_EDGE": 2.35,
    "CLEAR_EDGE_LIMIT": 0.75,
    "CLEAR_BUFFER": 6,
    "SIZE_STYLE": "mild",
    "WIDE_SPREAD": 18.0,
    "ALLOW_JOIN": True,
    "USE_WALL_MID_BLEND": True,
    "USE_DEPTH_IMPACT": True,
    "USE_NONLINEAR_INVENTORY": True,
    "ENABLE_TAKE_LADDER": True,
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

    def _slow_fair(self, book: Book) -> float:
        stable_mid = self._stable_mid(book)
        return (
            float(self.p["ANCHOR_WEIGHT"]) * float(self.p["REFERENCE_PRICE"])
            + float(self.p["STABLE_MID_WEIGHT"]) * stable_mid
        )

    def _fast_signal(self, book: Book) -> float:
        depth = max(float(self.p["DEPTH_FLOOR"]), float(book.best_bid_vol + book.best_ask_vol))
        beta = float(self.p["DEPTH_IMPACT_SCALE"]) / depth if self.p.get("USE_DEPTH_IMPACT", True) else 0.0
        return (
            float(self.p["LOCAL_MICRO_WEIGHT"]) * (book.micro - book.mid)
            + (beta + float(self.p["LOCAL_IMBALANCE_BIAS"])) * book.imbalance
        )

    def _signal_components(self, book: Book) -> Tuple[float, float, float]:
        slow_fair = self._slow_fair(book)
        fast_signal = self._fast_signal(book)
        clipped = clamp(fast_signal, -float(self.p["FAST_SIGNAL_CLIP"]), float(self.p["FAST_SIGNAL_CLIP"]))
        style = self.p.get("SPLIT_FAIR_STYLE", "guarded")
        if style == "blend":
            take_signal = float(self.p["FAST_TAKE_WEIGHT"]) * clipped
            quote_signal = float(self.p["FAST_QUOTE_WEIGHT"]) * clipped
        elif style == "guarded":
            take_signal = float(self.p["FAST_TAKE_WEIGHT"]) * clipped
            quote_signal = float(self.p["FAST_QUOTE_WEIGHT"]) * clipped
        else:
            take_signal = 0.0
            quote_signal = 0.0
        return slow_fair, take_signal, quote_signal

    def _reservation(self, slow_fair: float, projected_pos: int) -> float:
        inv_shift = float(self.p["INVENTORY_SKEW"]) * projected_pos
        if self.p.get("USE_NONLINEAR_INVENTORY", True):
            inv_ratio = projected_pos / float(PRODUCT_LIMITS["ASH_COATED_OSMIUM"])
            inv_shift += float(self.p["INVENTORY_CURVE"]) * (inv_ratio ** 3)
        return slow_fair - inv_shift

    def _mode(
        self,
        book: Book,
        pos: int,
        soft: int,
        bid_toxic: bool,
        ask_toxic: bool,
        buy_edge: float,
        sell_edge: float,
        take_signal: float,
    ) -> str:
        if self.p.get("REGIME_STYLE", "none") == "none":
            return "normal"

        clear_buffer = int(self.p["CLEAR_BUFFER"])
        if abs(pos) >= soft + clear_buffer and max(buy_edge, sell_edge) <= float(self.p["CLEAR_EDGE_LIMIT"]):
            return "inventory_clear"

        if bid_toxic or ask_toxic:
            return "toxic_defense"

        if (
            max(buy_edge, sell_edge) >= float(self.p["DISLOCATION_EDGE"])
            and abs(take_signal) >= 0.35
        ):
            return "dislocation_take"

        depth = book.best_bid_vol + book.best_ask_vol
        if (
            book.spread_val <= float(self.p["CALM_SPREAD_MAX"])
            and depth >= float(self.p["CALM_DEPTH_MIN"])
            and abs(book.imbalance) <= float(self.p["CALM_IMBALANCE_MAX"])
            and abs(take_signal) <= 0.9
        ):
            return "calm_mm"

        return "normal"

    def _size_mult(
        self,
        side: str,
        book: Book,
        pos: int,
        soft: int,
        bid_toxic: bool,
        ask_toxic: bool,
        mode: str,
    ) -> float:
        style = self.p.get("SIZE_STYLE", "none")
        if style == "none":
            return 1.0

        mult = 1.0
        if book.spread_val >= float(self.p["WIDE_SPREAD"]):
            mult -= 0.12
        if side == "buy" and book.imbalance < -float(self.p["ADVERSE_IMBALANCE"]):
            mult -= 0.12
        if side == "sell" and book.imbalance > float(self.p["ADVERSE_IMBALANCE"]):
            mult -= 0.12
        if side == "buy" and bid_toxic:
            mult -= 0.18
        if side == "sell" and ask_toxic:
            mult -= 0.18
        if side == "buy" and pos >= soft:
            mult -= 0.18
        if side == "sell" and pos <= -soft:
            mult -= 0.18
        if mode == "calm_mm":
            mult += 0.18
        elif mode == "dislocation_take":
            mult += 0.08
        elif mode == "inventory_clear":
            if side == "buy" and pos > 0:
                mult -= 0.25
            if side == "sell" and pos < 0:
                mult -= 0.25
        return clamp(mult, 0.45, 1.25)

    def build_orders(self, state: TradingState) -> List[Order]:
        if not self.p.get("ENABLED", True):
            return []

        book = Book(state.order_depths.get("ASH_COATED_OSMIUM"))
        if not book.valid:
            return []

        position = int(state.position.get("ASH_COATED_OSMIUM", 0))
        mgr = Manager("ASH_COATED_OSMIUM", position, PRODUCT_LIMITS["ASH_COATED_OSMIUM"])

        slow_fair, take_signal, quote_signal = self._signal_components(book)
        reservation = self._reservation(slow_fair, mgr.projected())

        adverse = float(self.p["ADVERSE_IMBALANCE"])
        strong = float(self.p["STRONG_IMBALANCE"])
        bid_toxic = book.imbalance < -adverse and book.micro < book.mid
        ask_toxic = book.imbalance > adverse and book.micro > book.mid

        take_reservation = reservation + take_signal
        buy_edge = take_reservation - book.best_ask
        sell_edge = book.best_bid - take_reservation
        soft = int(self.p["SOFT_LIMIT"])
        pos = mgr.projected()
        mode = self._mode(book, pos, soft, bid_toxic, ask_toxic, buy_edge, sell_edge, take_signal)

        take_levels = [
            (float(self.p["TAKE_L1_EDGE"]), int(self.p["TAKE_L1_SIZE"])),
            (float(self.p["TAKE_L2_EDGE"]), int(self.p["TAKE_L2_SIZE"])),
            (float(self.p["TAKE_L3_EDGE"]), int(self.p["TAKE_L3_SIZE"])),
        ]

        can_take_buy = True
        can_take_sell = True
        buy_need = float(self.p["NORMAL_TAKE_EDGE"])
        sell_need = float(self.p["NORMAL_TAKE_EDGE"])

        if bid_toxic:
            buy_need = max(buy_need, float(self.p["TOXIC_TAKE_EDGE"]))
        if ask_toxic:
            sell_need = max(sell_need, float(self.p["TOXIC_TAKE_EDGE"]))

        if mode == "normal":
            buy_need += 0.00
            sell_need += 0.00
        elif mode == "dislocation_take":
            buy_need = max(0.90, buy_need - 0.35)
            sell_need = max(0.90, sell_need - 0.35)
        elif mode == "toxic_defense":
            if bid_toxic:
                can_take_buy = False
            if ask_toxic:
                can_take_sell = False
            buy_need += 0.25
            sell_need += 0.25
        elif mode == "inventory_clear":
            if pos > 0:
                can_take_buy = False
            elif pos < 0:
                can_take_sell = False

        if self.p.get("ENABLE_TAKE_LADDER", True) and can_take_buy:
            take_buy = 0
            for edge_thr, clip in take_levels:
                if buy_edge >= max(edge_thr, buy_need):
                    take_buy = clip
            if take_buy > 0:
                if pos >= soft:
                    take_buy = max(0, take_buy - 3)
                mgr.buy(book.best_ask, min(book.best_ask_vol, take_buy))

        if self.p.get("ENABLE_TAKE_LADDER", True) and can_take_sell:
            take_sell = 0
            for edge_thr, clip in take_levels:
                if sell_edge >= max(edge_thr, sell_need):
                    take_sell = clip
            if take_sell > 0:
                if pos <= -soft:
                    take_sell = max(0, take_sell - 3)
                mgr.sell(book.best_bid, min(book.best_bid_vol, take_sell))

        buy_qe = float(self.p["BASE_EDGE"])
        sell_qe = float(self.p["BASE_EDGE"])
        if book.spread_val <= 14:
            buy_qe -= 0.50
            sell_qe -= 0.50
        elif book.spread_val >= 18:
            buy_qe += 0.65
            sell_qe += 0.65
        if book.imbalance > strong:
            buy_qe -= 0.25
            sell_qe += 0.15
        elif book.imbalance < -strong:
            buy_qe += 0.15
            sell_qe -= 0.25
        if bid_toxic:
            buy_qe += 0.90
        if ask_toxic:
            sell_qe += 0.90
        if pos >= soft:
            buy_qe += 1.10
            sell_qe -= 0.35
        elif pos <= -soft:
            buy_qe -= 0.35
            sell_qe += 1.10

        if mode == "calm_mm":
            buy_qe -= 0.45
            sell_qe -= 0.45
        elif mode == "dislocation_take":
            buy_qe -= 0.20
            sell_qe -= 0.20
        elif mode == "toxic_defense":
            if bid_toxic:
                buy_qe += 0.80
            if ask_toxic:
                sell_qe += 0.80
        elif mode == "inventory_clear":
            if pos > 0:
                buy_qe += 1.00
                sell_qe -= 0.40
            elif pos < 0:
                buy_qe -= 0.40
                sell_qe += 1.00

        buy_qe = max(float(self.p["MIN_QUOTE_EDGE"]), buy_qe)
        sell_qe = max(float(self.p["MIN_QUOTE_EDGE"]), sell_qe)

        quote_mid = reservation + quote_signal
        join_edge = float(self.p["JOIN_EDGE"])
        if mode == "calm_mm":
            join_edge += 0.35
        elif mode == "dislocation_take":
            join_edge += 0.15
        front_buy = int(round(quote_mid - buy_qe))
        front_sell = int(round(quote_mid + sell_qe))

        if self.p.get("ALLOW_JOIN", True):
            for price, _ in book.buy_levels[:2]:
                if quote_mid - price < buy_qe:
                    continue
                if mode in {"toxic_defense", "inventory_clear"}:
                    break
                if mode == "calm_mm":
                    front_buy = price if quote_mid - price <= join_edge else price + 1
                else:
                    front_buy = price
                break
            for price, _ in book.sell_levels[:2]:
                if price - quote_mid < sell_qe:
                    continue
                if mode in {"toxic_defense", "inventory_clear"}:
                    break
                if mode == "calm_mm":
                    front_sell = price if price - quote_mid <= join_edge else price - 1
                else:
                    front_sell = price
                break

        front_buy = min(front_buy, book.best_ask - 1)
        front_sell = max(front_sell, book.best_bid + 1)
        back_buy = min(front_buy - 2, book.best_ask - 1)
        back_sell = max(front_sell + 2, book.best_bid + 1)

        allow_bid = pos < soft + 6
        allow_ask = pos > -(soft + 6)
        if mode == "toxic_defense":
            if bid_toxic:
                allow_bid = False
            if ask_toxic:
                allow_ask = False
        elif mode == "inventory_clear":
            if pos > 0:
                allow_bid = False
            elif pos < 0:
                allow_ask = False

        buy_mult = self._size_mult("buy", book, pos, soft, bid_toxic, ask_toxic, mode)
        sell_mult = self._size_mult("sell", book, pos, soft, bid_toxic, ask_toxic, mode)
        front_sz = int(self.p["FRONT_SIZE"])
        back_sz = int(self.p["BACK_SIZE"])
        buy_front_sz = max(2, int(round(front_sz * buy_mult)))
        sell_front_sz = max(2, int(round(front_sz * sell_mult)))
        buy_back_sz = max(1, int(round(back_sz * buy_mult)))
        sell_back_sz = max(1, int(round(back_sz * sell_mult)))
        if mode == "calm_mm":
            buy_front_sz += 2
            sell_front_sz += 2
        elif mode == "dislocation_take":
            buy_front_sz += 1
            sell_front_sz += 1

        if allow_bid and front_buy > 0 and front_buy < book.best_ask:
            mgr.buy(front_buy, buy_front_sz)
            if back_buy > 0 and back_buy < book.best_ask:
                mgr.buy(back_buy, buy_back_sz)
        if allow_ask and front_sell > book.best_bid:
            mgr.sell(front_sell, sell_front_sz)
            if back_sell > book.best_bid:
                mgr.sell(back_sell, sell_back_sz)

        return mgr.orders


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
            result["ASH_COATED_OSMIUM"] = self.ash.build_orders(state)

        if "INTARIAN_PEPPER_ROOT" in state.order_depths:
            ipr_orders, memory = self.ipr.build_orders(state, memory)
            result["INTARIAN_PEPPER_ROOT"] = ipr_orders

        trader_data = json.dumps(memory, separators=(",", ":"))
        return result, 0, trader_data
