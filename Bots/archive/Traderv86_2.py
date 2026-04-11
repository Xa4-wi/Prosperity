from datamodel import Order, OrderDepth, TradingState
from typing import Dict, List, Optional, Tuple
import json
import math


POSITION_LIMITS: Dict[str, int] = {
    "EMERALDS": 80,
    "TOMATOES": 80,
}


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def ema(previous: Optional[float], current: float, alpha: float) -> float:
    if previous is None:
        return current
    return (1.0 - alpha) * previous + alpha * current


class Book:
    def __init__(self, order_depth: Optional[OrderDepth]) -> None:
        self.valid = False
        self.buy_levels: List[Tuple[int, int]] = []
        self.sell_levels: List[Tuple[int, int]] = []
        self.best_bid: Optional[int] = None
        self.best_ask: Optional[int] = None
        self.best_bid_volume = 0
        self.best_ask_volume = 0
        self.mid = 0.0
        self.micro = 0.0
        self.spread = 0
        self.imbalance = 0.0

        if order_depth is None:
            return

        self.buy_levels = sorted(
            ((int(price), int(volume)) for price, volume in order_depth.buy_orders.items()),
            key=lambda item: item[0],
            reverse=True,
        )
        self.sell_levels = sorted(
            ((int(price), abs(int(volume))) for price, volume in order_depth.sell_orders.items()),
            key=lambda item: item[0],
        )

        if not self.buy_levels or not self.sell_levels:
            return

        self.best_bid, self.best_bid_volume = self.buy_levels[0]
        self.best_ask, self.best_ask_volume = self.sell_levels[0]
        if self.best_bid >= self.best_ask:
            return

        self.mid = (self.best_bid + self.best_ask) / 2.0
        self.spread = self.best_ask - self.best_bid
        total_top = self.best_bid_volume + self.best_ask_volume
        if total_top > 0:
            self.micro = (
                self.best_ask * self.best_bid_volume + self.best_bid * self.best_ask_volume
            ) / total_top
            self.imbalance = (self.best_bid_volume - self.best_ask_volume) / total_top
        else:
            self.micro = self.mid
            self.imbalance = 0.0

        self.valid = True


class OrderManager:
    def __init__(self, product: str, position: int, limit: int) -> None:
        self.product = product
        self.position = int(position)
        self.limit = int(limit)
        self.buy_capacity = max(0, self.limit - self.position)
        self.sell_capacity = max(0, self.limit + self.position)
        self.orders: List[Order] = []

    def projected_position(self) -> int:
        return self.position + sum(order.quantity for order in self.orders)

    def add_buy(self, price: int, quantity: int) -> None:
        size = min(max(0, int(quantity)), self.buy_capacity)
        if size <= 0:
            return
        self.orders.append(Order(self.product, int(price), size))
        self.buy_capacity -= size

    def add_sell(self, price: int, quantity: int) -> None:
        size = min(max(0, int(quantity)), self.sell_capacity)
        if size <= 0:
            return
        self.orders.append(Order(self.product, int(price), -size))
        self.sell_capacity -= size


class EmeraldsBot:
    REFERENCE_PRICE = 10000.0
    MID_WEIGHT = 0.18
    INVENTORY_SKEW = 0.12
    DEFAULT_EDGE = 7.0
    JOIN_EDGE = 2.0
    BASE_SIZE = 10
    SOFT_LIMIT = 20

    def __init__(self, state: TradingState) -> None:
        self.book = Book(state.order_depths.get("EMERALDS"))
        self.manager = OrderManager(
            "EMERALDS",
            int(state.position.get("EMERALDS", 0)),
            POSITION_LIMITS["EMERALDS"],
        )

    def fair_value(self) -> float:
        return (1.0 - self.MID_WEIGHT) * self.REFERENCE_PRICE + self.MID_WEIGHT * self.book.mid

    def reservation(self) -> float:
        return self.fair_value() - self.manager.projected_position() * self.INVENTORY_SKEW

    def run(self) -> List[Order]:
        if not self.book.valid:
            return []

        reservation = self.reservation()
        buy_edge = reservation - float(self.book.best_ask)
        sell_edge = float(self.book.best_bid) - reservation

        if buy_edge >= 1.0:
            take = 6 if buy_edge < 4.0 else 12 if buy_edge < 8.0 else 20
            if self.manager.projected_position() >= self.SOFT_LIMIT:
                take = max(0, take - 4)
            self.manager.add_buy(self.book.best_ask, min(self.book.best_ask_volume, take))

        if sell_edge >= 1.0:
            take = 6 if sell_edge < 4.0 else 12 if sell_edge < 8.0 else 20
            if self.manager.projected_position() <= -self.SOFT_LIMIT:
                take = max(0, take - 4)
            self.manager.add_sell(self.book.best_bid, min(self.book.best_bid_volume, take))

        position = self.manager.projected_position()
        if position > 0 and self.book.best_bid >= math.ceil(reservation):
            self.manager.add_sell(self.book.best_bid, min(position, self.book.best_bid_volume, self.BASE_SIZE))
        position = self.manager.projected_position()
        if position < 0 and self.book.best_ask <= math.floor(reservation):
            self.manager.add_buy(self.book.best_ask, min(abs(position), self.book.best_ask_volume, self.BASE_SIZE))

        buy_quote = int(round(reservation - self.DEFAULT_EDGE))
        sell_quote = int(round(reservation + self.DEFAULT_EDGE))
        for price, _ in self.book.buy_levels[:2]:
            if price < reservation - self.DEFAULT_EDGE:
                buy_quote = price if reservation - price <= self.JOIN_EDGE else price + 1
                break
        for price, _ in self.book.sell_levels[:2]:
            if price > reservation + self.DEFAULT_EDGE:
                sell_quote = price if price - reservation <= self.JOIN_EDGE else price - 1
                break

        position = self.manager.projected_position()
        if position >= self.SOFT_LIMIT:
            buy_quote -= 1
            sell_quote -= 1
        elif position <= -self.SOFT_LIMIT:
            buy_quote += 1
            sell_quote += 1

        if self.book.spread > 2:
            buy_quote = max(buy_quote, self.book.best_bid + 1)
            sell_quote = min(sell_quote, self.book.best_ask - 1)

        if buy_quote < self.book.best_ask and self.manager.buy_capacity > 0:
            size = self.BASE_SIZE + 4 if self.manager.projected_position() <= -self.SOFT_LIMIT else self.BASE_SIZE
            if self.manager.projected_position() >= self.SOFT_LIMIT:
                size = max(1, size - 6)
            self.manager.add_buy(buy_quote, size)
        if sell_quote > self.book.best_bid and self.manager.sell_capacity > 0:
            size = self.BASE_SIZE + 4 if self.manager.projected_position() >= self.SOFT_LIMIT else self.BASE_SIZE
            if self.manager.projected_position() <= -self.SOFT_LIMIT:
                size = max(1, size - 6)
            self.manager.add_sell(sell_quote, size)

        return self.manager.orders


class TomatoesBot:
    FAST_ALPHA = 0.36
    SLOW_ALPHA = 0.12
    FLOW_ALPHA = 0.24
    VOL_ALPHA = 0.20
    TARGET_ALPHA = 0.18
    WALL_ALPHA = 0.22
    WALL_WEIGHT = 0.20

    BASE_QUOTE_EDGE = 1.95
    TREND_QUOTE_EDGE = 2.35
    STRONG_QUOTE_EDGE = 2.90
    BASE_TAKE_EDGE = 1.10
    HYBRID_TAKE_EDGE = 0.78
    STRONG_TAKE_EDGE = 0.52

    BASE_PASSIVE_SIZE = 9
    TAKE_SIZE = 7
    SOFT_LIMIT = 28
    TARGET_CAP = 28
    INVENTORY_SKEW = 0.050
    TARGET_BIAS_DIVISOR = 16.0

    RANGE_THRESHOLD = 0.60
    TREND_THRESHOLD = 1.20
    STRONG_THRESHOLD = 2.10

    def __init__(self, state: TradingState, memory: Dict[str, object]) -> None:
        self.book = Book(state.order_depths.get("TOMATOES"))
        self.manager = OrderManager(
            "TOMATOES",
            int(state.position.get("TOMATOES", 0)),
            POSITION_LIMITS["TOMATOES"],
        )
        self.memory = memory if isinstance(memory, dict) else {}
        raw = self.memory.get("tomatoes", {})
        if not isinstance(raw, dict):
            raw = {}
        self.fast_fair_ema = float(raw.get("fast_fair_ema", 0.0))
        self.slow_fair_ema = float(raw.get("slow_fair_ema", 0.0))
        self.flow_ema = float(raw.get("flow_ema", 0.0))
        self.vol_ema = float(raw.get("vol_ema", 1.5))
        self.trend_ema = float(raw.get("trend_ema", 0.0))
        self.target_ema = float(raw.get("target_ema", 0.0))
        self.wall_fair_ema = float(raw.get("wall_fair_ema", 0.0))
        self.last_mid = float(raw.get("last_mid", 0.0))
        self.initialized = bool(raw.get("initialized", 0))

    def wall_mid(self) -> float:
        bid_levels = self.book.buy_levels[:3]
        ask_levels = self.book.sell_levels[:3]
        if not bid_levels or not ask_levels:
            return self.book.mid

        bid_weight = 0.0
        bid_sum = 0.0
        ask_weight = 0.0
        ask_sum = 0.0

        for index, (price, volume) in enumerate(bid_levels):
            eff = max(0.0, float(volume) - 2.0)
            if eff <= 0.0:
                continue
            weight = eff / (index + 1.0)
            bid_weight += weight
            bid_sum += weight * float(price)

        for index, (price, volume) in enumerate(ask_levels):
            eff = max(0.0, float(volume) - 2.0)
            if eff <= 0.0:
                continue
            weight = eff / (index + 1.0)
            ask_weight += weight
            ask_sum += weight * float(price)

        if bid_weight <= 1e-9 or ask_weight <= 1e-9:
            return self.book.mid
        return (bid_sum / bid_weight + ask_sum / ask_weight) / 2.0

    def update_state(self) -> None:
        if not self.book.valid:
            return

        half_spread = max(1.0, self.book.spread / 2.0)
        flow = self.book.imbalance * half_spread
        fast_fair = 0.46 * self.book.mid + 0.34 * self.book.micro + 0.20 * (self.book.mid + flow)
        wall_fair = self.wall_mid()

        if not self.initialized:
            self.fast_fair_ema = fast_fair
            self.slow_fair_ema = fast_fair
            self.wall_fair_ema = wall_fair
            self.flow_ema = flow
            self.vol_ema = max(1.0, half_spread)
            self.trend_ema = 0.0
            self.target_ema = 0.0
            self.last_mid = self.book.mid
            self.initialized = True
            return

        ret = self.book.mid - self.last_mid
        self.fast_fair_ema = ema(self.fast_fair_ema, fast_fair, self.FAST_ALPHA)
        self.slow_fair_ema = ema(self.slow_fair_ema, fast_fair, self.SLOW_ALPHA)
        self.wall_fair_ema = ema(self.wall_fair_ema, wall_fair, self.WALL_ALPHA)
        self.flow_ema = ema(self.flow_ema, flow, self.FLOW_ALPHA)
        self.vol_ema = ema(self.vol_ema, abs(ret), self.VOL_ALPHA)
        raw_trend = (
            0.95 * (self.fast_fair_ema - self.slow_fair_ema)
            + 0.50 * (self.fast_fair_ema - self.wall_fair_ema)
            + 0.75 * (self.book.micro - self.book.mid)
            + 0.90 * self.flow_ema
        )
        self.trend_ema = ema(self.trend_ema, raw_trend, 0.30)
        self.last_mid = self.book.mid

    def regime(self) -> str:
        score = self.trend_ema
        vol = self.vol_ema
        if vol >= 3.4 and abs(score) < self.TREND_THRESHOLD:
            return "chaotic"
        if score >= self.STRONG_THRESHOLD:
            return "strong_up"
        if score <= -self.STRONG_THRESHOLD:
            return "strong_down"
        if score >= self.TREND_THRESHOLD:
            return "trend_up"
        if score <= -self.TREND_THRESHOLD:
            return "trend_down"
        return "range"

    def target_position(self, regime: str) -> int:
        score = self.trend_ema
        conviction = clamp(abs(score) / max(1.0, self.STRONG_THRESHOLD), 0.0, 1.0)
        if regime == "strong_up":
            desired = (self.TARGET_CAP + 8) * conviction
        elif regime == "strong_down":
            desired = -(self.TARGET_CAP + 8) * conviction
        elif regime == "trend_up":
            desired = self.TARGET_CAP * conviction
        elif regime == "trend_down":
            desired = -self.TARGET_CAP * conviction
        else:
            mean_revert = clamp((self.slow_fair_ema - self.book.mid) / max(2.0, self.vol_ema * 2.0), -1.0, 1.0)
            desired = 10.0 * mean_revert

        self.target_ema = ema(self.target_ema, desired, self.TARGET_ALPHA)
        return int(round(clamp(self.target_ema, -self.TARGET_CAP - 8, self.TARGET_CAP + 8)))

    def fair_value(self, target: int) -> float:
        fair = (
            0.32 * self.slow_fair_ema
            + 0.28 * self.fast_fair_ema
            + self.WALL_WEIGHT * self.wall_fair_ema
            + 0.12 * self.book.micro
            + 0.08 * (self.book.mid + self.flow_ema)
        )
        fair += (target - self.manager.projected_position()) / self.TARGET_BIAS_DIVISOR
        return fair

    def reservation(self, fair: float, target: int) -> float:
        return fair - (self.manager.projected_position() - target) * self.INVENTORY_SKEW

    def execution_mode(self, regime: str, target: int) -> str:
        position = self.manager.projected_position()
        gap = target - position
        if regime == "chaotic":
            return "defensive"
        if regime in {"strong_up", "strong_down"} and abs(gap) >= 10:
            return "aggressive"
        if regime in {"trend_up", "trend_down"} and abs(gap) >= 4:
            return "hybrid"
        return "market_make"

    def take_threshold(self, side: str, regime: str, mode: str, target: int) -> float:
        threshold = self.BASE_TAKE_EDGE + 0.08 * min(3.0, self.vol_ema)
        position = self.manager.projected_position()
        aligned = (side == "BUY" and target > position) or (side == "SELL" and target < position)

        if mode == "aggressive":
            threshold = self.STRONG_TAKE_EDGE
        elif mode == "hybrid" and aligned:
            threshold = self.HYBRID_TAKE_EDGE

        if regime == "chaotic":
            threshold += 0.45
        if self.book.spread >= 8:
            threshold += 0.10
        if not aligned and regime in {"trend_up", "trend_down", "strong_up", "strong_down"}:
            threshold += 0.45
        return max(0.20, threshold)

    def take_orders(self, reservation: float, regime: str, mode: str, target: int) -> Tuple[bool, bool]:
        took_buy = False
        took_sell = False
        position = self.manager.projected_position()

        for price, volume in self.book.sell_levels[:2]:
            if self.manager.buy_capacity <= 0:
                break
            edge = reservation - float(price)
            if edge < self.take_threshold("BUY", regime, mode, target):
                break
            desired = max(0, target - self.manager.projected_position())
            if mode != "market_make" and desired <= 0:
                break
            size = min(volume, self.manager.buy_capacity, self.TAKE_SIZE)
            if mode != "market_make":
                size = min(size, max(1, desired))
                if mode == "hybrid":
                    size = min(size, 5)
            self.manager.add_buy(price, size)
            took_buy = True
            position = self.manager.projected_position()
            if mode == "aggressive" and position >= target:
                break

        for price, volume in self.book.buy_levels[:2]:
            if self.manager.sell_capacity <= 0:
                break
            edge = float(price) - reservation
            if edge < self.take_threshold("SELL", regime, mode, target):
                break
            desired = max(0, self.manager.projected_position() - target)
            if mode != "market_make" and desired <= 0:
                break
            size = min(volume, self.manager.sell_capacity, self.TAKE_SIZE)
            if mode != "market_make":
                size = min(size, max(1, desired))
                if mode == "hybrid":
                    size = min(size, 5)
            self.manager.add_sell(price, size)
            took_sell = True
            position = self.manager.projected_position()
            if mode == "aggressive" and position <= target:
                break

        return took_buy, took_sell

    def passive_quotes(self, reservation: float, regime: str, mode: str, target: int) -> Tuple[Optional[int], Optional[int], int, int]:
        position = self.manager.projected_position()
        buy_quote: Optional[int] = None
        sell_quote: Optional[int] = None
        buy_size = 0
        sell_size = 0

        if mode == "market_make":
            edge = self.BASE_QUOTE_EDGE + 0.14 * min(3.0, self.vol_ema)
            buy_quote = math.floor(reservation - edge)
            sell_quote = math.ceil(reservation + edge)
            buy_size = self.BASE_PASSIVE_SIZE
            sell_size = self.BASE_PASSIVE_SIZE
        elif mode == "hybrid":
            edge = self.TREND_QUOTE_EDGE + 0.12 * min(3.0, self.vol_ema)
            if regime == "trend_up":
                buy_quote = min(self.book.best_ask - 1, max(self.book.best_bid + 1, math.floor(reservation - edge) + 1))
                sell_quote = math.ceil(reservation + edge + 1.0) if position > max(4, target // 3) else None
                buy_size = self.BASE_PASSIVE_SIZE + 1
                sell_size = max(1, self.BASE_PASSIVE_SIZE - 4)
            elif regime == "trend_down":
                sell_quote = max(self.book.best_bid + 1, min(self.book.best_ask - 1, math.ceil(reservation + edge) - 1))
                buy_quote = math.floor(reservation - edge - 1.0) if position < min(-4, target // 3) else None
                buy_size = max(1, self.BASE_PASSIVE_SIZE - 4)
                sell_size = self.BASE_PASSIVE_SIZE + 1
        elif mode == "aggressive":
            edge = self.STRONG_QUOTE_EDGE + 0.15 * min(3.0, self.vol_ema)
            if regime == "strong_up":
                buy_quote = self.book.best_bid + 1 if position < target else None
                sell_quote = math.ceil(reservation + edge + 1.0) if position > max(6, target // 2) else None
                buy_size = self.BASE_PASSIVE_SIZE + 2
                sell_size = max(1, self.BASE_PASSIVE_SIZE - 5)
            elif regime == "strong_down":
                sell_quote = self.book.best_ask - 1 if position > target else None
                buy_quote = math.floor(reservation - edge - 1.0) if position < min(-6, target // 2) else None
                buy_size = max(1, self.BASE_PASSIVE_SIZE - 5)
                sell_size = self.BASE_PASSIVE_SIZE + 2
        else:
            edge = self.STRONG_QUOTE_EDGE + 0.4
            if position > 0:
                sell_quote = math.ceil(reservation + edge)
                sell_size = max(2, self.BASE_PASSIVE_SIZE - 2)
            elif position < 0:
                buy_quote = math.floor(reservation - edge)
                buy_size = max(2, self.BASE_PASSIVE_SIZE - 2)

        if buy_quote is not None:
            buy_quote = max(self.book.best_bid + 1, min(int(buy_quote), self.book.best_ask - 1))
            if buy_quote >= self.book.best_ask:
                buy_quote = None
        if sell_quote is not None:
            sell_quote = min(self.book.best_ask - 1, max(int(sell_quote), self.book.best_bid + 1))
            if sell_quote <= self.book.best_bid:
                sell_quote = None

        if buy_quote is not None and position >= self.SOFT_LIMIT:
            buy_quote = None
        if sell_quote is not None and position <= -self.SOFT_LIMIT:
            sell_quote = None

        return buy_quote, sell_quote, buy_size, sell_size

    def clear_wrong_way_inventory(self, reservation: float, regime: str, target: int) -> None:
        position = self.manager.projected_position()
        if position > 0 and (regime in {"range", "trend_down", "strong_down", "chaotic"} or position > target):
            if self.book.best_bid >= math.floor(reservation):
                self.manager.add_sell(self.book.best_bid, min(position, self.book.best_bid_volume, self.BASE_PASSIVE_SIZE))
        position = self.manager.projected_position()
        if position < 0 and (regime in {"range", "trend_up", "strong_up", "chaotic"} or position < target):
            if self.book.best_ask <= math.ceil(reservation):
                self.manager.add_buy(self.book.best_ask, min(abs(position), self.book.best_ask_volume, self.BASE_PASSIVE_SIZE))

    def next_memory(self) -> Dict[str, object]:
        return {
            "fast_fair_ema": float(self.fast_fair_ema),
            "slow_fair_ema": float(self.slow_fair_ema),
            "flow_ema": float(self.flow_ema),
            "vol_ema": float(self.vol_ema),
            "trend_ema": float(self.trend_ema),
            "target_ema": float(self.target_ema),
            "wall_fair_ema": float(self.wall_fair_ema),
            "last_mid": float(self.last_mid),
            "initialized": 1,
        }

    def run(self) -> Tuple[List[Order], Dict[str, object]]:
        if not self.book.valid:
            self.memory["tomatoes"] = self.next_memory()
            return [], self.memory

        self.update_state()
        regime = self.regime()
        target = self.target_position(regime)
        fair = self.fair_value(target)
        reservation = self.reservation(fair, target)
        mode = self.execution_mode(regime, target)

        took_buy, took_sell = self.take_orders(reservation, regime, mode, target)
        self.clear_wrong_way_inventory(reservation, regime, target)
        reservation = self.reservation(fair, target)
        buy_quote, sell_quote, buy_size, sell_size = self.passive_quotes(reservation, regime, mode, target)

        position = self.manager.projected_position()
        if not took_buy and buy_quote is not None and self.manager.buy_capacity > 0:
            if mode == "market_make" or position < target or regime == "chaotic":
                if mode != "market_make":
                    buy_size = min(buy_size, max(1, target - position))
                self.manager.add_buy(buy_quote, min(buy_size, self.manager.buy_capacity))

        position = self.manager.projected_position()
        if not took_sell and sell_quote is not None and self.manager.sell_capacity > 0:
            if mode == "market_make" or position > target or regime == "chaotic":
                if mode != "market_make":
                    sell_size = min(sell_size, max(1, position - target))
                self.manager.add_sell(sell_quote, min(sell_size, self.manager.sell_capacity))

        self.memory["tomatoes"] = self.next_memory()
        return self.manager.orders, self.memory


class Trader:
    def load_memory(self, trader_data: str) -> Dict[str, object]:
        if not trader_data:
            return {}
        try:
            parsed = json.loads(trader_data)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def dump_memory(self, memory: Dict[str, object]) -> str:
        return json.dumps(memory, separators=(",", ":"))

    def run(self, state: TradingState):
        memory = self.load_memory(state.traderData)
        result: Dict[str, List[Order]] = {}

        emeralds = EmeraldsBot(state)
        result["EMERALDS"] = emeralds.run()

        tomatoes = TomatoesBot(state, memory)
        tomato_orders, updated_memory = tomatoes.run()
        result["TOMATOES"] = tomato_orders

        for product in state.order_depths:
            if product not in result:
                result[product] = []

        return result, 0, self.dump_memory(updated_memory)
