from datamodel import Order, OrderDepth, TradingState
from typing import Dict, List, Optional, Tuple
import json
import math


POSITION_LIMITS: Dict[str, int] = {
    "ASH_COATED_OSMIUM": 80,
    "INTARIAN_PEPPER_ROOT": 80,
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
        self.spread = 0
        self.micro = 0.0
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


class AshCoatedOsmiumBot:
    REFERENCE_PRICE = 10000.0
    IMBALANCE_FAIR_WEIGHT = 3.4
    MICRO_FAIR_WEIGHT = 0.35
    INVENTORY_SKEW = 0.08
    DEFAULT_EDGE = 7.5
    JOIN_EDGE = 2.0
    BASE_ORDER_SIZE = 12
    SOFT_LIMIT = 28
    TAKE_LEVELS = (
        (2.0, 6),
        (5.0, 10),
        (8.0, 16),
    )

    def __init__(self, state: TradingState) -> None:
        self.book = Book(state.order_depths.get("ASH_COATED_OSMIUM"))
        self.manager = OrderManager(
            "ASH_COATED_OSMIUM",
            int(state.position.get("ASH_COATED_OSMIUM", 0)),
            POSITION_LIMITS["ASH_COATED_OSMIUM"],
        )

    def fair_value(self) -> float:
        book_skew = self.IMBALANCE_FAIR_WEIGHT * self.book.imbalance
        micro_skew = self.MICRO_FAIR_WEIGHT * (self.book.micro - self.book.mid)
        return self.REFERENCE_PRICE + book_skew + micro_skew

    def reservation(self) -> float:
        return self.fair_value() - self.manager.projected_position() * self.INVENTORY_SKEW

    def take_orders(self, reservation: float) -> None:
        if not self.book.valid:
            return

        buy_edge = reservation - float(self.book.best_ask)
        buy_size = 0
        for distance, clip in self.TAKE_LEVELS:
            if buy_edge >= distance:
                buy_size = clip
        if buy_size > 0:
            if self.manager.projected_position() >= self.SOFT_LIMIT:
                buy_size = max(0, buy_size - 4)
            self.manager.add_buy(self.book.best_ask, min(self.book.best_ask_volume, buy_size))

        sell_edge = float(self.book.best_bid) - reservation
        sell_size = 0
        for distance, clip in self.TAKE_LEVELS:
            if sell_edge >= distance:
                sell_size = clip
        if sell_size > 0:
            if self.manager.projected_position() <= -self.SOFT_LIMIT:
                sell_size = max(0, sell_size - 4)
            self.manager.add_sell(self.book.best_bid, min(self.book.best_bid_volume, sell_size))

    def passive_quotes(self, reservation: float) -> Tuple[Optional[int], Optional[int]]:
        if not self.book.valid:
            return None, None

        buy_quote = int(round(reservation - self.DEFAULT_EDGE))
        sell_quote = int(round(reservation + self.DEFAULT_EDGE))

        for price, _volume in self.book.buy_levels[:2]:
            if reservation - price >= self.DEFAULT_EDGE:
                buy_quote = price if reservation - price <= self.JOIN_EDGE else price + 1
                break
        for price, _volume in self.book.sell_levels[:2]:
            if price - reservation >= self.DEFAULT_EDGE:
                sell_quote = price if price - reservation <= self.JOIN_EDGE else price - 1
                break

        position = self.manager.projected_position()
        if position >= self.SOFT_LIMIT:
            buy_quote -= 1
            sell_quote -= 1
        elif position <= -self.SOFT_LIMIT:
            buy_quote += 1
            sell_quote += 1

        buy_quote = min(buy_quote, self.book.best_ask - 1)
        sell_quote = max(sell_quote, self.book.best_bid + 1)
        if buy_quote >= sell_quote:
            return self.book.best_bid, self.book.best_ask
        return buy_quote, sell_quote

    def run(self) -> List[Order]:
        if not self.book.valid:
            return []

        reservation = self.reservation()
        self.take_orders(reservation)
        buy_quote, sell_quote = self.passive_quotes(reservation)

        position = self.manager.projected_position()
        if buy_quote is not None and position < self.SOFT_LIMIT + self.BASE_ORDER_SIZE:
            buy_size = self.BASE_ORDER_SIZE
            if position >= self.SOFT_LIMIT:
                buy_size = max(2, buy_size - 6)
            self.manager.add_buy(buy_quote, buy_size)

        position = self.manager.projected_position()
        if sell_quote is not None and position > -(self.SOFT_LIMIT + self.BASE_ORDER_SIZE):
            sell_size = self.BASE_ORDER_SIZE
            if position <= -self.SOFT_LIMIT:
                sell_size = max(2, sell_size - 6)
            self.manager.add_sell(sell_quote, sell_size)

        return self.manager.orders


class IntarianPepperRootBot:
    DRIFT_PER_TIMESTAMP = 0.001
    RESIDUAL_ALPHA = 0.10
    SPREAD_ALPHA = 0.08
    BASE_CARRY = 12.0
    EARLY_LONG_BIAS = 30.0
    EDGE_TARGET_SCALE = 12.0
    ZSCORE_BUY_BONUS = 12.0
    ZSCORE_SELL_PENALTY = 8.0
    MAX_LONG_TARGET = 68
    MAX_SHORT_TARGET = 20
    INVENTORY_SKEW = 0.078
    BASE_TAKE_EDGE = 1.00
    BASE_QUOTE_EDGE = 2.40
    SOFT_LIMIT = 52
    PASSIVE_SIZE = 12
    MAX_TAKE_SIZE = 16
    BULLISH_IMBALANCE = 0.05
    OVEREXTENSION_Z = 1.05
    EARLY_ACCUM_END = 0.42
    LOOKAHEAD_BONUS = 4.5
    PASSIVE_BUY_BUFFER = 16
    PASSIVE_SELL_BUFFER = 10

    def __init__(self, state: TradingState, memory: Dict[str, object]) -> None:
        self.state = state
        self.book = Book(state.order_depths.get("INTARIAN_PEPPER_ROOT"))
        self.manager = OrderManager(
            "INTARIAN_PEPPER_ROOT",
            int(state.position.get("INTARIAN_PEPPER_ROOT", 0)),
            POSITION_LIMITS["INTARIAN_PEPPER_ROOT"],
        )
        self.memory = memory
        self.product_state = self.load_state()

    def timestamp(self) -> int:
        raw = getattr(self.state, "timestamp", 0)
        return int(raw if isinstance(raw, (int, float)) else 0)

    def progress(self) -> float:
        return clamp(self.timestamp() / 999900.0, 0.0, 1.0)

    def early_bias_factor(self) -> float:
        return max(0.0, 1.0 - self.progress() / 0.85)

    def load_state(self) -> Dict[str, float]:
        raw = self.memory.get("INTARIAN_PEPPER_ROOT", {})
        if not isinstance(raw, dict):
            raw = {}
        return {
            "anchor": float(raw.get("anchor", 0.0)),
            "residual_ema": float(raw.get("residual_ema", 0.0)),
            "spread_ema": float(raw.get("spread_ema", 13.0)),
            "last_timestamp": float(raw.get("last_timestamp", -1.0)),
            "initialized": 1.0 if raw.get("initialized") else 0.0,
        }

    def reset_if_new_day(self) -> None:
        now = float(self.timestamp())
        last = float(self.product_state["last_timestamp"])
        if last >= 0.0 and now < last:
            self.product_state = {
                "anchor": 0.0,
                "residual_ema": 0.0,
                "spread_ema": 13.0,
                "last_timestamp": now,
                "initialized": 0.0,
            }

    def save_state(self) -> None:
        self.product_state["last_timestamp"] = float(self.timestamp())
        self.memory["INTARIAN_PEPPER_ROOT"] = {
            "anchor": float(self.product_state["anchor"]),
            "residual_ema": float(self.product_state["residual_ema"]),
            "spread_ema": float(self.product_state["spread_ema"]),
            "last_timestamp": float(self.product_state["last_timestamp"]),
            "initialized": 1,
        }

    def update_state(self) -> None:
        if not self.book.valid:
            return

        self.reset_if_new_day()
        if self.product_state["initialized"] <= 0.0:
            self.product_state["anchor"] = round(self.book.mid / 1000.0) * 1000.0
            self.product_state["residual_ema"] = 0.0
            self.product_state["spread_ema"] = float(self.book.spread)
            self.product_state["initialized"] = 1.0
        else:
            self.product_state["spread_ema"] = ema(
                float(self.product_state["spread_ema"]),
                float(self.book.spread),
                self.SPREAD_ALPHA,
            )

        residual = self.book.mid - self.trend_line()
        self.product_state["residual_ema"] = ema(
            float(self.product_state["residual_ema"]),
            residual,
            self.RESIDUAL_ALPHA,
        )

    def trend_line(self) -> float:
        return float(self.product_state["anchor"]) + self.DRIFT_PER_TIMESTAMP * float(self.timestamp())

    def residual_metrics(self) -> Tuple[float, float]:
        residual = self.book.mid - self.trend_line()
        spread_scale = max(4.0, float(self.product_state["spread_ema"]) * 0.45)
        zscore = residual / spread_scale
        return residual, zscore

    def fair_value(self) -> float:
        trend = self.trend_line()
        residual, _zscore = self.residual_metrics()
        half_spread = max(1.0, self.book.spread / 2.0)
        flow_fair = self.book.mid + self.book.imbalance * half_spread
        trend_premium = self.LOOKAHEAD_BONUS * (1.0 - 0.65 * self.progress())
        return (
            0.60 * trend
            + 0.12 * self.book.mid
            + 0.10 * self.book.micro
            + 0.10 * flow_fair
            + 0.08 * (trend + residual)
            + trend_premium
        )

    def bullish_state(self, zscore: float) -> bool:
        return (
            zscore < self.OVEREXTENSION_Z
            and self.book.imbalance >= self.BULLISH_IMBALANCE
            and self.book.micro >= self.book.mid
        )

    def target_position(self, fair: float) -> int:
        _residual, zscore = self.residual_metrics()
        edge = fair - self.book.mid
        target = self.BASE_CARRY
        target += self.EARLY_LONG_BIAS * self.early_bias_factor()
        target += self.EDGE_TARGET_SCALE * edge

        if zscore < 0.0:
            target += self.ZSCORE_BUY_BONUS * min(1.0, abs(zscore) / 1.8)
        if zscore > 0.45:
            target -= self.ZSCORE_SELL_PENALTY * min(1.0, (zscore - 0.45) / 1.4)
        if self.book.imbalance < -0.18 and self.book.micro < self.book.mid:
            target -= 6.0
        if self.bullish_state(zscore):
            target += 6.0

        progress = self.progress()
        if progress < 0.18 and zscore <= 0.45:
            target = max(target, 28.0)
        elif progress < 0.35 and zscore <= 0.25:
            target = max(target, 20.0)
        if progress > 0.82 and zscore > 1.25:
            target -= 8.0

        return int(clamp(target, -self.MAX_SHORT_TARGET, self.MAX_LONG_TARGET))

    def reservation(self, fair: float, target: int) -> float:
        return fair - (self.manager.projected_position() - target) * self.INVENTORY_SKEW

    def take_edges(self, target: int, zscore: float) -> Tuple[float, float]:
        buy_edge = self.BASE_TAKE_EDGE
        sell_edge = self.BASE_TAKE_EDGE + 0.45
        position = self.manager.projected_position()

        if position < target:
            buy_edge -= 0.30
        if position > target:
            sell_edge -= 0.10

        if zscore < -0.45:
            buy_edge -= 0.30
        elif zscore > 0.85:
            sell_edge -= 0.05

        if self.bullish_state(zscore) and position > 0:
            sell_edge += 0.60
        if self.progress() < 0.55 and position < target:
            sell_edge += 0.15

        return max(0.40, buy_edge), max(0.80, sell_edge)

    def take_orders(self, reservation: float, target: int, zscore: float) -> None:
        buy_edge_needed, sell_edge_needed = self.take_edges(target, zscore)

        buy_edge = reservation - float(self.book.best_ask)
        if buy_edge >= buy_edge_needed and self.manager.buy_capacity > 0:
            quantity = min(
                self.book.best_ask_volume,
                self.MAX_TAKE_SIZE,
                max(0, target + 14 - self.manager.projected_position()),
            )
            self.manager.add_buy(self.book.best_ask, quantity)

        sell_edge = float(self.book.best_bid) - reservation
        if sell_edge >= sell_edge_needed and self.manager.sell_capacity > 0:
            quantity = min(
                self.book.best_bid_volume,
                self.MAX_TAKE_SIZE,
                max(0, self.manager.projected_position() - (target - 6)),
            )
            if self.bullish_state(zscore) and self.manager.projected_position() > 0:
                quantity = min(quantity, 5)
            self.manager.add_sell(self.book.best_bid, quantity)

    def passive_quotes(self, reservation: float, target: int, zscore: float) -> Tuple[Optional[int], Optional[int]]:
        buy_edge = self.BASE_QUOTE_EDGE
        sell_edge = self.BASE_QUOTE_EDGE + 0.60
        position = self.manager.projected_position()

        if position < target:
            buy_edge -= 0.50
        if position > target:
            sell_edge -= 0.10

        if zscore < -0.55:
            buy_edge -= 0.35
        elif zscore > 1.00:
            sell_edge -= 0.20

        buy_quote = math.floor(reservation - buy_edge)
        sell_quote = math.ceil(reservation + sell_edge)

        if self.bullish_state(zscore) and position < target:
            buy_quote = max(buy_quote, self.book.best_bid + 1)
        if self.bullish_state(zscore) and position > 0:
            sell_quote += 1

        buy_quote = min(buy_quote, self.book.best_ask - 1)
        sell_quote = max(sell_quote, self.book.best_bid + 1)

        if buy_quote >= sell_quote:
            buy_quote = self.book.best_bid
            sell_quote = self.book.best_ask

        if self.progress() < self.EARLY_ACCUM_END and position < target - 8:
            return buy_quote, None
        if self.bullish_state(zscore) and position < target - 6:
            return buy_quote, None
        return buy_quote, sell_quote

    def passive_sizes(self, target: int) -> Tuple[int, int]:
        buy_size = self.PASSIVE_SIZE
        sell_size = max(4, self.PASSIVE_SIZE - 2)
        position = self.manager.projected_position()

        if position < target:
            buy_size += 2
        if position > 0:
            sell_size = max(3, sell_size - 2)
        if self.progress() < self.EARLY_ACCUM_END and position < target:
            buy_size += 2
            sell_size = max(2, sell_size - 2)

        if position >= self.SOFT_LIMIT:
            buy_size = max(2, buy_size - 6)
            sell_size += 2
        if position <= -self.SOFT_LIMIT:
            sell_size = max(2, sell_size - 6)
            buy_size += 2
        return buy_size, sell_size

    def run(self) -> Tuple[List[Order], Dict[str, object]]:
        if not self.book.valid:
            self.save_state()
            return [], self.memory

        self.update_state()
        fair = self.fair_value()
        _residual, zscore = self.residual_metrics()
        target = self.target_position(fair)
        reservation = self.reservation(fair, target)

        self.take_orders(reservation, target, zscore)
        buy_quote, sell_quote = self.passive_quotes(reservation, target, zscore)
        buy_size, sell_size = self.passive_sizes(target)

        position = self.manager.projected_position()
        if buy_quote is not None and self.manager.buy_capacity > 0 and position < target + self.PASSIVE_BUY_BUFFER:
            quantity = min(buy_size, self.manager.buy_capacity, max(0, target + self.PASSIVE_BUY_BUFFER - position))
            self.manager.add_buy(buy_quote, quantity)

        position = self.manager.projected_position()
        if sell_quote is not None and self.manager.sell_capacity > 0 and position > target - self.PASSIVE_SELL_BUFFER:
            quantity = min(sell_size, self.manager.sell_capacity, max(0, position - (target - self.PASSIVE_SELL_BUFFER)))
            self.manager.add_sell(sell_quote, quantity)

        self.save_state()
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

        osmium = AshCoatedOsmiumBot(state)
        result["ASH_COATED_OSMIUM"] = osmium.run()

        pepper = IntarianPepperRootBot(state, memory)
        pepper_orders, updated_memory = pepper.run()
        result["INTARIAN_PEPPER_ROOT"] = pepper_orders

        for product in state.order_depths:
            if product not in result:
                result[product] = []

        return result, 0, self.dump_memory(updated_memory)
