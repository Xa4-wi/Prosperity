from __future__ import annotations

import json
from typing import Dict, List, Optional, Tuple

try:
    from datamodel import Order, OrderDepth, Trade, TradingState
except ModuleNotFoundError:
    from trader_factory.core.datamodel import Order, OrderDepth, Trade, TradingState


PRODUCT_LIMITS = {
    "ASH_COATED_OSMIUM": 80,
    "INTARIAN_PEPPER_ROOT": 80,
}

ROUND2_MAF_BID = 25000


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


class Book:
    def __init__(self, depth: Optional[OrderDepth]) -> None:
        self.buy_levels: List[Tuple[int, int]] = []
        self.sell_levels: List[Tuple[int, int]] = []
        self.has_bid = False
        self.has_ask = False
        self.valid = False
        self.best_bid = 0
        self.best_ask = 0
        self.best_bid_vol = 0
        self.best_ask_vol = 0
        self.mid = 0.0
        self.micro = 0.0
        self.spread = 0.0
        self.imbalance = 0.0

        if depth is None:
            return

        self.buy_levels = sorted(
            ((int(price), int(volume)) for price, volume in depth.buy_orders.items()),
            key=lambda level: level[0],
            reverse=True,
        )
        self.sell_levels = sorted(
            ((int(price), abs(int(volume))) for price, volume in depth.sell_orders.items()),
            key=lambda level: level[0],
        )

        if self.buy_levels:
            self.has_bid = True
            self.best_bid, self.best_bid_vol = self.buy_levels[0]
        if self.sell_levels:
            self.has_ask = True
            self.best_ask, self.best_ask_vol = self.sell_levels[0]

        if not self.has_bid and not self.has_ask:
            return
        if not (self.has_bid and self.has_ask):
            visible = self.best_bid if self.has_bid else self.best_ask
            self.mid = float(visible)
            self.micro = self.mid
            return
        if self.best_bid >= self.best_ask:
            return

        self.valid = True
        self.mid = (self.best_bid + self.best_ask) / 2.0
        self.spread = float(self.best_ask - self.best_bid)
        total = self.best_bid_vol + self.best_ask_vol
        if total > 0:
            self.micro = (
                self.best_ask * self.best_bid_vol + self.best_bid * self.best_ask_vol
            ) / total
            self.imbalance = (self.best_bid_vol - self.best_ask_vol) / total
        else:
            self.micro = self.mid

    def stable_mid(self, levels: int = 3) -> float:
        bids = self.buy_levels[:levels]
        asks = self.sell_levels[:levels]
        if not bids or not asks:
            return self.mid
        bid_vol = sum(volume for _, volume in bids)
        ask_vol = sum(volume for _, volume in asks)
        if bid_vol <= 0 or ask_vol <= 0:
            return self.mid
        bid_price = sum(price * volume for price, volume in bids) / bid_vol
        ask_price = sum(price * volume for price, volume in asks) / ask_vol
        return (bid_price + ask_price) / 2.0


class OrderManager:
    def __init__(self, product: str, position: int, limit: int) -> None:
        self.product = product
        self.position = int(position)
        self.limit = int(limit)
        self.buy_cap = max(0, limit - position)
        self.sell_cap = max(0, limit + position)
        self.orders: List[Order] = []

    def projected(self) -> int:
        return self.position + sum(order.quantity for order in self.orders)

    def buy(self, price: int, quantity: int) -> None:
        size = min(max(0, int(quantity)), self.buy_cap)
        if size <= 0:
            return
        self.orders.append(Order(self.product, int(price), size))
        self.buy_cap -= size

    def sell(self, price: int, quantity: int) -> None:
        size = min(max(0, int(quantity)), self.sell_cap)
        if size <= 0:
            return
        self.orders.append(Order(self.product, int(price), -size))
        self.sell_cap -= size


class PepperDriftTrader:
    LIMIT = PRODUCT_LIMITS["INTARIAN_PEPPER_ROOT"]
    DRIFT_SPAN = 1000.0
    MAX_TARGET = 80
    INVENTORY_SKEW = 0.08
    TAKE_EDGE = 2.2
    SELL_RELIEF = 1.2
    QUOTE_EDGE = 4.0
    FRONT_SIZE = 12
    BACK_SIZE = 6
    VACUUM_SIZE = 3
    VACUUM_GAP = 4

    def build_orders(self, state: TradingState, memory: dict) -> Tuple[List[Order], dict]:
        book = Book(state.order_depths.get("INTARIAN_PEPPER_ROOT"))
        if not book.has_bid and not book.has_ask:
            return [], memory

        position = int(state.position.get("INTARIAN_PEPPER_ROOT", 0))
        mgr = OrderManager("INTARIAN_PEPPER_ROOT", position, self.LIMIT)
        timestamp = int(getattr(state, "timestamp", 0))
        progress = clamp(timestamp / 999900.0, 0.0, 1.0)

        pstate = memory.get("PEPPER", {})
        if not isinstance(pstate, dict):
            pstate = {}

        start_mid = float(pstate.get("start_mid", 0.0))
        last_good_fair = float(pstate.get("last_good_fair", 0.0))

        if timestamp == 0 or start_mid <= 0.0:
            seed = book.mid if (book.has_bid or book.has_ask) else 13000.0
            start_mid = float(round(seed / 1000.0) * 1000.0)
            last_good_fair = start_mid

        if not book.valid:
            if book.has_ask and position < self.MAX_TARGET:
                visible_fair = 0.6 * last_good_fair + 0.4 * (book.best_ask - 8.0)
                if book.best_ask <= visible_fair - self.TAKE_EDGE:
                    mgr.buy(book.best_ask, min(self.VACUUM_SIZE, self.MAX_TARGET - position))
            elif book.has_bid and position > 0:
                visible_fair = 0.6 * last_good_fair + 0.4 * (book.best_bid + 8.0)
                ask_price = max(book.best_bid + self.VACUUM_GAP, int(round(visible_fair + self.VACUUM_GAP)))
                mgr.sell(ask_price, min(self.VACUUM_SIZE, position))

            pstate["start_mid"] = start_mid
            pstate["last_good_fair"] = last_good_fair
            memory["PEPPER"] = pstate
            return mgr.orders, memory

        fair = start_mid + self.DRIFT_SPAN * progress
        residual = book.mid - fair
        zscore = residual / max(6.0, book.spread * 0.65)

        schedule_target = clamp(26.0 + 64.0 * min(1.0, progress / 0.58), 0.0, float(self.MAX_TARGET))
        if zscore > 1.25 and progress > 0.60:
            schedule_target -= min(8.0, 5.0 * (zscore - 1.25 + 1.0))
        if progress > 0.97:
            schedule_target = min(schedule_target, 72.0)
        target = int(clamp(schedule_target, 0.0, float(self.MAX_TARGET)))

        reservation = fair - (mgr.projected() - target) * self.INVENTORY_SKEW

        if mgr.projected() < target and book.best_ask <= reservation - self.TAKE_EDGE:
            clip = min(self.FRONT_SIZE, target - mgr.projected(), book.best_ask_vol)
            mgr.buy(book.best_ask, clip)
        elif (
            progress < 0.55
            and mgr.projected() < max(0, target - 10)
            and book.best_ask <= fair - 1.2
        ):
            clip = min(max(4, self.FRONT_SIZE - 2), target - mgr.projected(), book.best_ask_vol)
            mgr.buy(book.best_ask, clip)

        if mgr.projected() > max(0, target + 3):
            sell_edge = self.SELL_RELIEF if (zscore > 1.10 or progress > 0.92) else self.TAKE_EDGE + 1.0
            if book.best_bid >= reservation + sell_edge:
                clip = min(self.FRONT_SIZE, mgr.projected() - target, book.best_bid_vol)
                mgr.sell(book.best_bid, clip)

        pos = mgr.projected()
        if pos < target:
            front_buy = int(round(reservation - self.QUOTE_EDGE))
            if book.best_bid > 0 and front_buy < book.best_bid and book.best_bid < book.best_ask:
                front_buy = book.best_bid
            front_buy = min(front_buy, book.best_ask - 1)
            if front_buy > 0:
                mgr.buy(front_buy, min(self.FRONT_SIZE, target - pos))
                if pos + self.FRONT_SIZE < target:
                    back_buy = max(1, front_buy - 2)
                    if back_buy < book.best_ask:
                        mgr.buy(back_buy, min(self.BACK_SIZE, target - mgr.projected()))

        pos = mgr.projected()
        late_exit = progress > 0.95 or zscore > 1.40
        if pos > 0 and late_exit:
            front_sell = int(round(reservation + self.QUOTE_EDGE - 1.0))
            if book.best_ask > 0 and front_sell > book.best_ask and book.best_ask > book.best_bid:
                front_sell = book.best_ask
            front_sell = max(front_sell, book.best_bid + 1)
            mgr.sell(front_sell, min(self.FRONT_SIZE, pos))

        pstate["start_mid"] = start_mid
        pstate["last_good_fair"] = float(fair)
        memory["PEPPER"] = pstate
        return mgr.orders, memory


class AshLocalFairTrader:
    LIMIT = PRODUCT_LIMITS["ASH_COATED_OSMIUM"]
    ANCHOR = 10000.0
    ANCHOR_WEIGHT = 0.25
    STABLE_WEIGHT = 0.50
    MICRO_WEIGHT = 0.25
    INVENTORY_SKEW = 0.08
    SOFT_LIMIT = 60
    TAKE_EDGE = 1.00
    QUOTE_EDGE = 1.90
    JOIN_EDGE = 1.30
    FRONT_SIZE = 16
    BACK_SIZE = 7
    VACUUM_SIZE = 3
    VACUUM_GAP = 4

    def build_orders(self, state: TradingState, memory: dict) -> Tuple[List[Order], dict]:
        book = Book(state.order_depths.get("ASH_COATED_OSMIUM"))
        if not book.has_bid and not book.has_ask:
            return [], memory

        position = int(state.position.get("ASH_COATED_OSMIUM", 0))
        mgr = OrderManager("ASH_COATED_OSMIUM", position, self.LIMIT)

        astate = memory.get("ASH", {})
        if not isinstance(astate, dict):
            astate = {}
        last_good_fair = float(astate.get("last_good_fair", self.ANCHOR))

        if not book.valid:
            if book.has_ask and position > 0:
                fair = 0.65 * last_good_fair + 0.35 * (book.best_ask - 8.0)
                ask_price = max(book.best_ask, int(round(fair + self.VACUUM_GAP)))
                mgr.sell(ask_price, min(self.VACUUM_SIZE, position))
            elif book.has_bid and position < 0:
                fair = 0.65 * last_good_fair + 0.35 * (book.best_bid + 8.0)
                bid_price = min(book.best_bid, int(round(fair - self.VACUUM_GAP)))
                if bid_price > 0:
                    mgr.buy(bid_price, min(self.VACUUM_SIZE, -position))

            astate["last_good_fair"] = last_good_fair
            memory["ASH"] = astate
            return mgr.orders, memory

        stable_mid = book.stable_mid()
        local_fair = (
            self.ANCHOR_WEIGHT * self.ANCHOR
            + self.STABLE_WEIGHT * stable_mid
            + self.MICRO_WEIGHT * book.micro
        )
        stable_gap = stable_mid - book.mid
        micro_gap = book.micro - book.mid

        take_alpha = 0.60 * micro_gap + 0.40 * stable_gap
        quote_alpha = 0.35 * micro_gap + 0.25 * stable_gap
        reservation = local_fair - mgr.projected() * self.INVENTORY_SKEW
        take_fair = reservation + take_alpha
        quote_mid = reservation + quote_alpha

        if mgr.projected() < self.LIMIT and book.best_ask <= take_fair - self.TAKE_EDGE:
            edge = take_fair - book.best_ask
            size = 4 if edge < 2.0 else 8
            if mgr.projected() >= self.SOFT_LIMIT:
                size = max(2, size - 3)
            mgr.buy(book.best_ask, min(size, book.best_ask_vol))

        if mgr.projected() > -self.LIMIT and book.best_bid >= take_fair + self.TAKE_EDGE:
            edge = book.best_bid - take_fair
            size = 4 if edge < 2.0 else 8
            if mgr.projected() <= -self.SOFT_LIMIT:
                size = max(2, size - 3)
            mgr.sell(book.best_bid, min(size, book.best_bid_vol))

        pos = mgr.projected()
        buy_edge = self.QUOTE_EDGE
        sell_edge = self.QUOTE_EDGE

        if book.spread >= 18.0:
            buy_edge += 0.50
            sell_edge += 0.50
        if book.imbalance > 0.18:
            buy_edge -= 0.20
            sell_edge += 0.15
        elif book.imbalance < -0.18:
            buy_edge += 0.15
            sell_edge -= 0.20
        if pos >= self.SOFT_LIMIT:
            buy_edge += 0.90
            sell_edge -= 0.20
        elif pos <= -self.SOFT_LIMIT:
            buy_edge -= 0.20
            sell_edge += 0.90

        front_buy = int(round(quote_mid - buy_edge))
        front_sell = int(round(quote_mid + sell_edge))

        if book.best_bid > 0 and (quote_mid - book.best_bid) <= self.JOIN_EDGE:
            front_buy = max(front_buy, book.best_bid)
        elif book.best_bid + 1 < book.best_ask and (quote_mid - book.best_bid) > self.JOIN_EDGE:
            front_buy = max(front_buy, book.best_bid + 1)

        if book.best_ask > 0 and (book.best_ask - quote_mid) <= self.JOIN_EDGE:
            front_sell = min(front_sell, book.best_ask)
        elif book.best_ask - 1 > book.best_bid and (book.best_ask - quote_mid) > self.JOIN_EDGE:
            front_sell = min(front_sell, book.best_ask - 1)

        front_buy = min(front_buy, book.best_ask - 1)
        front_sell = max(front_sell, book.best_bid + 1)
        back_buy = max(1, front_buy - 2)
        back_sell = front_sell + 2

        pos = mgr.projected()
        buy_size = self.FRONT_SIZE
        sell_size = self.FRONT_SIZE
        if book.imbalance < -0.22:
            buy_size = max(4, buy_size - 4)
        if book.imbalance > 0.22:
            sell_size = max(4, sell_size - 4)
        if pos >= self.SOFT_LIMIT:
            buy_size = max(2, buy_size - 6)
            sell_size += 2
        elif pos <= -self.SOFT_LIMIT:
            sell_size = max(2, sell_size - 6)
            buy_size += 2

        allow_bid = pos < self.SOFT_LIMIT + 10
        allow_ask = pos > -(self.SOFT_LIMIT + 10)

        if allow_bid and 0 < front_buy < book.best_ask:
            mgr.buy(front_buy, buy_size)
            if back_buy < book.best_ask and mgr.projected() < self.SOFT_LIMIT + 12:
                mgr.buy(back_buy, self.BACK_SIZE)
        if allow_ask and front_sell > book.best_bid:
            mgr.sell(front_sell, sell_size)
            if back_sell > book.best_bid and mgr.projected() > -(self.SOFT_LIMIT + 12):
                mgr.sell(back_sell, self.BACK_SIZE)

        astate["last_good_fair"] = float(local_fair)
        memory["ASH"] = astate
        return mgr.orders, memory


class Trader:
    def __init__(self) -> None:
        self.pepper = PepperDriftTrader()
        self.ash = AshLocalFairTrader()

    def bid(self):
        return ROUND2_MAF_BID

    def run(self, state: TradingState):
        try:
            memory = json.loads(state.traderData) if state.traderData else {}
            if not isinstance(memory, dict):
                memory = {}
        except Exception:
            memory = {}

        last_ts = int(memory.get("_last_ts", -1))
        if last_ts >= 0 and state.timestamp < last_ts:
            memory = {}

        result: Dict[str, List[Order]] = {}

        pepper_orders, memory = self.pepper.build_orders(state, memory)
        ash_orders, memory = self.ash.build_orders(state, memory)

        result["INTARIAN_PEPPER_ROOT"] = pepper_orders
        result["ASH_COATED_OSMIUM"] = ash_orders

        memory["_last_ts"] = int(state.timestamp)
        trader_data = json.dumps(memory, separators=(",", ":"))
        return result, 0, trader_data
