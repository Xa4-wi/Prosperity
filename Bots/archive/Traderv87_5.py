from datamodel import OrderDepth, Order, TradingState
from typing import Dict, List, Optional, Tuple
import json
import math


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


DEFAULT_EMERALDS_PARAMS = {
    "REFERENCE_PRICE": 10000.0,
    "REFERENCE_WEIGHT": 0.80,
    "MID_WEIGHT": 0.20,
    "MICRO_WEIGHT": 0.00,
    "INVENTORY_SKEW": 0.0328922991,
    "TAKE_TIER_1_DISTANCE": 1.0,
    "TAKE_TIER_2_DISTANCE": 4.0,
    "TAKE_TIER_3_DISTANCE": 8.0,
    "TAKE_TIER_1_SIZE": 6,
    "TAKE_TIER_2_SIZE": 12,
    "TAKE_TIER_3_SIZE": 20,
    "CLEAR_WIDTH": 0.0,
    "BASE_ORDER_SIZE": 10,
    "DISREGARD_EDGE": 2.0,
    "JOIN_EDGE": 1.0,
    "DEFAULT_EDGE": 8.0,
    "SOFT_LIMIT_RATIO": 0.6357999832,
}


DEFAULT_TOMATOES_PARAMS = {
    "MID_WEIGHT": 0.25,
    "MICRO_WEIGHT": 0.30,
    "HISTORY_WEIGHT": 0.25,
    "REGRESSION_WEIGHT": 0.20,
    "RESIDUAL_REVERT_WEIGHT": 0.12,
    "IMBALANCE_WEIGHT": 0.35,
    "INVENTORY_SKEW": 0.005,
    "BASE_TAKE_EDGE": 0.78,
    "BASE_QUOTE_EDGE": 2.68,
    "MAX_QUOTE_EDGE": 9.0,
    "PASSIVE_SIZE": 8,
    "MAX_TAKE_SIZE": 10,
    "REGRESSION_WINDOW": 8,
    "REGRESSION_HORIZON": 0.5,
    "TREND_EDGE_THRESHOLD": 1.00,
    "STRONG_TREND_EDGE": 2.50,
    "FIT_THRESHOLD": 0.45,
    "TREND_IMBALANCE_THRESHOLD": 0.12,
    "TOXIC_SPREAD_THRESHOLD": 15.0,
    "TOXIC_VOLATILITY_THRESHOLD": 3.2,
    "SOFT_LIMIT_RATIO": 0.56828726,
    "POSITION_BIAS_DIVISOR": 12.0,
    "TREND_FAIR_BONUS": 0.25,
    "TREND_ENTRY_TAKE_BONUS": 3.0,
    "TREND_HOLD_EXIT_BONUS": 0.55,
    "STRONG_TREND_HOLD_EXIT_BONUS": 0.90,
    "TREND_PASSIVE_PUSH": 0.0,
    "TREND_PASSIVE_SIZE_BONUS": 2.0,
    "VOL_CONTROL_WINDOW": 8,
    "TIME_HORIZON_TICKS": 10000.0,
    "GAMMA_RANGE": 0.69283327,
    "GAMMA_TREND": 0.10,
    "GAMMA_VOLATILE": 0.40,
    "RESERVATION_SCALE": 0.02,
    "SPREAD_VOL_COEF": 0.1,
    "SPREAD_INV_COEF": 1.1081637,
    "SPREAD_TIME_COEF": 1.7791177,
    "TREND_RESERVATION_BIAS": 0.04,
    "RANGE_RESERVATION_BIAS": 0.26486122,
    "ALPHA_EDGE_SCALE": 1.4153631,
    "ALPHA_IMBALANCE_SCALE": 0.7,
    "ALPHA_THRESHOLD_SCALE": 1.03,
    "TREND_SELL_HOLD_EXTRA": 0.24,
    "TREND_BUY_TAKE_EXTRA": 0.08,
    "TREND_QUOTE_LIFT_EXTRA": 1.0,
    "HOLD_TIME_COEF": 0.08,
    "HOLD_VOL_COEF": 0.0,
    "ALPHA_REFERENCE_WEIGHT": 0.45,
    "ALPHA_MID_WEIGHT": 0.20,
    "ALPHA_MICRO_WEIGHT": 0.25,
    "ALPHA_FLOW_WEIGHT": 0.10,
    "ALPHA_FLOW_SPREAD_SCALE": 0.50,
    "ALPHA_BLEND_WEIGHT": 0.28,
    "FAIR_ALPHA_WEIGHT": 0.42,
    "ALPHA_CAP": 2.20,
    "RANGE_ALPHA_DAMP": 0.35,
    "CONFLICT_ALPHA_DAMP": 0.45,
    "MOMENTUM_ALPHA_DAMP": 0.70,
    "POSITION_ALPHA_DAMP_START": 14.0,
    "POSITION_ALPHA_DAMP_END": 28.0,
    "WALL_LEVELS": 3,
    "WALL_MIN_SPREAD": 4.0,
    "WALL_MAX_SPREAD": 12.0,
    "WALL_SIZE_FLOOR": 4.0,
    "WALL_ALPHA_WEIGHT": 0.10,
    "WALL_FAIR_WEIGHT": 0.16,
    "WALL_EWMA_ALPHA": 0.22,
    "WALL_PERSISTENCE_FLOOR": 0.35,
    "GAP_CURVE_POWER": 1.60,
    "GAP_FAIR_WEIGHT": 0.40,
    "GAP_RESERVATION_WEIGHT": 0.55,
    "GAP_QUOTE_EDGE_WEIGHT": 0.45,
    "GAP_PASSIVE_SIZE_WEIGHT": 0.18,
    "QUEUE_ALPHA_WEIGHT": 0.08,
    "QUEUE_FAIR_WEIGHT": 0.08,
    "QUEUE_EDGE_SHIFT": 0.08,
    "QUEUE_TAKE_SHIFT": 0.08,
    "QUEUE_SIZE_BONUS": 1.0,
    "QUEUE_SIGNAL_ALPHA": 0.30,
    "LOB_SIGNAL_ALPHA": 0.28,
    "LOB_ALPHA_WEIGHT": 0.07,
    "LOB_FAIR_WEIGHT": 0.06,
    "LOB_EDGE_WEIGHT": 0.12,
    "LOB_TAKE_SHIFT": 0.08,
    "LOB_QUOTE_SHIFT": 0.08,
    "MR_SHORT_WINDOW": 6,
    "MR_LONG_WINDOW": 18,
    "MR_RSI_WINDOW": 10,
    "MR_SIGNAL_CAP": 2.4,
    "MR_RANGE_TARGET_SCALE": 10.0,
    "MR_FAIR_WEIGHT": 0.20,
    "MR_TAKE_SHIFT": 0.10,
    "MR_QUOTE_SHIFT": 0.06,
    "MR_ZSCORE_ACTIVATION": 0.80,
    "MR_RSI_ACTIVATION": 6.0,
    "MR_CONFLICT_DAMP": 0.72,
    "MR_TREND_DAMP": 0.82,
    "ANCHOR_PHI": 0.48,
    "ANCHOR_BETA": 0.14,
    "ANCHOR_CAP_RATIO": 0.24,
    "ANCHOR_TARGET_BLEND": 0.14,
    "ANCHOR_RESERVATION_WEIGHT": 0.08,
    "WRONG_WAY_RESERVATION_MULT": 1.40,
    "ALIGNED_RESERVATION_MULT": 0.78,
}


class BaseProductTrader:
    HISTORY_LENGTH = 8

    def __init__(
        self,
        product: str,
        state: TradingState,
        mid_history: Dict[str, List[float]],
        position_limit: int,
    ) -> None:
        self.product = product
        self.state = state
        self.mid_history = mid_history
        self.position_limit = position_limit
        self.orders: List[Order] = []

        self.order_depth: Optional[OrderDepth] = state.order_depths.get(product)
        self.position = state.position.get(product, 0)
        self.buy_capacity = position_limit - self.position
        self.sell_capacity = position_limit + self.position
        self.soft_limit = int(position_limit * 0.55)

        self.buy_levels: List[Tuple[int, int]] = []
        self.sell_levels: List[Tuple[int, int]] = []
        self.best_bid: Optional[int] = None
        self.best_ask: Optional[int] = None
        self.best_bid_volume = 0
        self.best_ask_volume = 0
        self.mid: Optional[float] = None
        self.micro: Optional[float] = None
        self.spread: Optional[int] = None
        self.recent_average: Optional[float] = None
        self.momentum: float = 0.0
        self.imbalance: float = 0.0

        self._load_market_state()

    def _load_market_state(self) -> None:
        if self.order_depth is None:
            return

        self.buy_levels = sorted(
            self.order_depth.buy_orders.items(),
            key=lambda item: item[0],
            reverse=True,
        )
        self.sell_levels = sorted(
            ((price, -volume) for price, volume in self.order_depth.sell_orders.items()),
            key=lambda item: item[0],
        )

        self.best_bid = self.buy_levels[0][0] if self.buy_levels else None
        self.best_ask = self.sell_levels[0][0] if self.sell_levels else None
        if self.best_bid is None or self.best_ask is None:
            return

        self.best_bid_volume = self.buy_levels[0][1]
        self.best_ask_volume = self.sell_levels[0][1]
        self.mid = (self.best_bid + self.best_ask) / 2
        self.spread = self.best_ask - self.best_bid

        total_top_volume = self.best_bid_volume + self.best_ask_volume
        if total_top_volume > 0:
            self.micro = (
                (self.best_bid * self.best_ask_volume) + (self.best_ask * self.best_bid_volume)
            ) / total_top_volume
            self.imbalance = (self.best_bid_volume - self.best_ask_volume) / total_top_volume
        else:
            self.micro = self.mid
            self.imbalance = 0.0

        history = self.mid_history.get(self.product, [])
        self.recent_average = sum(history) / len(history) if history else self.mid
        self.momentum = self.mid - self.recent_average

        history.append(self.mid)
        self.mid_history[self.product] = history[-self.HISTORY_LENGTH :]

    def has_book(self) -> bool:
        return self.best_bid is not None and self.best_ask is not None and self.mid is not None and self.micro is not None

    def projected_position(self) -> int:
        return self.position + sum(order.quantity for order in self.orders)

    def add_buy(self, price: int, quantity: int) -> None:
        quantity = min(max(0, int(quantity)), self.buy_capacity)
        if quantity <= 0:
            return
        self.orders.append(Order(self.product, int(price), quantity))
        self.buy_capacity -= quantity

    def add_sell(self, price: int, quantity: int) -> None:
        quantity = min(max(0, int(quantity)), self.sell_capacity)
        if quantity <= 0:
            return
        self.orders.append(Order(self.product, int(price), -quantity))
        self.sell_capacity -= quantity

    def apply_parameter_overrides(
        self,
        defaults: Dict[str, float],
        overrides: Optional[Dict[str, float]],
    ) -> None:
        for key, value in defaults.items():
            setattr(self, key, value)

        if not overrides:
            return

        for key, value in overrides.items():
            if key in defaults and isinstance(value, (int, float)):
                setattr(self, key, float(value))

    def clamp_inside_spread(
        self,
        buy_quote: Optional[int],
        sell_quote: Optional[int],
    ) -> Tuple[Optional[int], Optional[int]]:
        if not self.has_book():
            return None, None

        best_bid = int(self.best_bid)
        best_ask = int(self.best_ask)

        final_buy = None
        if buy_quote is not None:
            candidate = max(int(buy_quote), best_bid + 1)
            if candidate < best_ask:
                final_buy = candidate

        final_sell = None
        if sell_quote is not None:
            candidate = min(int(sell_quote), best_ask - 1)
            if candidate > best_bid:
                final_sell = candidate

        return final_buy, final_sell

    def run(self) -> List[Order]:
        return self.orders


class EmeraldsTrader(BaseProductTrader):
    PARAMETER_DEFAULTS = DEFAULT_EMERALDS_PARAMS

    def __init__(
        self,
        product: str,
        state: TradingState,
        mid_history: Dict[str, List[float]],
        position_limit: int,
        params: Optional[Dict[str, float]] = None,
    ) -> None:
        super().__init__(product, state, mid_history, position_limit)
        self.apply_parameter_overrides(self.PARAMETER_DEFAULTS, params)
        self.soft_limit = int(position_limit * self.SOFT_LIMIT_RATIO)

    def fair_value(self) -> float:
        return (
            self.REFERENCE_WEIGHT * self.REFERENCE_PRICE
            + self.MID_WEIGHT * float(self.mid)
            + self.MICRO_WEIGHT * float(self.micro)
        )

    def adjusted_fair_value(self) -> float:
        return self.fair_value() - (self.projected_position() * self.INVENTORY_SKEW)

    def take_size_for_distance(self, distance: float) -> int:
        if distance >= self.TAKE_TIER_3_DISTANCE:
            return int(self.TAKE_TIER_3_SIZE)
        if distance >= self.TAKE_TIER_2_DISTANCE:
            return int(self.TAKE_TIER_2_SIZE)
        if distance >= self.TAKE_TIER_1_DISTANCE:
            return int(self.TAKE_TIER_1_SIZE)
        return 0

    def tiered_take_size(self, side: str, adjusted_fair: float) -> int:
        if side == "BUY":
            distance = adjusted_fair - float(self.best_ask)
        else:
            distance = float(self.best_bid) - adjusted_fair

        size = self.take_size_for_distance(distance)
        position = self.projected_position()

        if side == "BUY":
            if position <= -self.soft_limit:
                size += 4
            elif position >= self.soft_limit:
                size = max(0, size - 3)
        else:
            if position >= self.soft_limit:
                size += 4
            elif position <= -self.soft_limit:
                size = max(0, size - 3)

        return min(self.position_limit, size)

    def clear_orders(self, adjusted_fair: float) -> Tuple[bool, bool]:
        cleared_buy = False
        cleared_sell = False
        position = self.projected_position()

        if (
            position > 0
            and self.sell_capacity > 0
            and int(self.best_bid) >= math.ceil(adjusted_fair + self.CLEAR_WIDTH)
        ):
            before = self.sell_capacity
            quantity = min(position, self.best_bid_volume, int(self.BASE_ORDER_SIZE))
            self.add_sell(int(self.best_bid), quantity)
            cleared_sell = self.sell_capacity < before

        position = self.projected_position()
        if (
            position < 0
            and self.buy_capacity > 0
            and int(self.best_ask) <= math.floor(adjusted_fair - self.CLEAR_WIDTH)
        ):
            before = self.buy_capacity
            quantity = min(abs(position), self.best_ask_volume, int(self.BASE_ORDER_SIZE))
            self.add_buy(int(self.best_ask), quantity)
            cleared_buy = self.buy_capacity < before

        return cleared_buy, cleared_sell

    def passive_quotes(self, adjusted_fair: float) -> Tuple[Optional[int], Optional[int]]:
        asks_above_fair = [
            price for price, _volume in self.sell_levels
            if price > adjusted_fair + self.DISREGARD_EDGE
        ]
        bids_below_fair = [
            price for price, _volume in self.buy_levels
            if price < adjusted_fair - self.DISREGARD_EDGE
        ]

        buy_quote = round(adjusted_fair - self.DEFAULT_EDGE)
        sell_quote = round(adjusted_fair + self.DEFAULT_EDGE)

        best_ask_above_fair = min(asks_above_fair) if asks_above_fair else None
        best_bid_below_fair = max(bids_below_fair) if bids_below_fair else None

        if best_ask_above_fair is not None:
            if abs(best_ask_above_fair - adjusted_fair) <= self.JOIN_EDGE:
                sell_quote = best_ask_above_fair
            else:
                sell_quote = best_ask_above_fair - 1

        if best_bid_below_fair is not None:
            if abs(adjusted_fair - best_bid_below_fair) <= self.JOIN_EDGE:
                buy_quote = best_bid_below_fair
            else:
                buy_quote = best_bid_below_fair + 1

        position = self.projected_position()
        if position >= self.soft_limit:
            sell_quote -= 1
            buy_quote -= 1
        elif position <= -self.soft_limit:
            buy_quote += 1
            sell_quote += 1

        return self.clamp_inside_spread(buy_quote, sell_quote)

    def passive_size(self, side: str) -> int:
        size = int(self.BASE_ORDER_SIZE)
        if int(self.spread) >= 16:
            size += 1

        position = self.projected_position()
        if side == "BUY":
            if position <= -self.soft_limit:
                size += 4
            elif position >= self.soft_limit:
                size = max(1, size - 6)
        else:
            if position >= self.soft_limit:
                size += 4
            elif position <= -self.soft_limit:
                size = max(1, size - 6)

        return max(1, size)

    def take_orders(self, adjusted_fair: float) -> Tuple[bool, bool]:
        took_buy = False
        took_sell = False

        buy_take_size = self.tiered_take_size("BUY", adjusted_fair)
        if buy_take_size > 0 and self.buy_capacity > 0:
            before = self.buy_capacity
            self.add_buy(int(self.best_ask), min(self.best_ask_volume, buy_take_size))
            took_buy = self.buy_capacity < before

        sell_take_size = self.tiered_take_size("SELL", adjusted_fair)
        if sell_take_size > 0 and self.sell_capacity > 0:
            before = self.sell_capacity
            self.add_sell(int(self.best_bid), min(self.best_bid_volume, sell_take_size))
            took_sell = self.sell_capacity < before

        return took_buy, took_sell

    def run(self) -> List[Order]:
        if not self.has_book():
            return self.orders

        adjusted_fair = self.adjusted_fair_value()
        took_buy, took_sell = self.take_orders(adjusted_fair)
        cleared_buy, cleared_sell = self.clear_orders(adjusted_fair)
        buy_quote, sell_quote = self.passive_quotes(adjusted_fair)
        position = self.projected_position()

        if (
            not took_buy
            and not cleared_buy
            and buy_quote is not None
            and self.buy_capacity > 0
            and position < self.soft_limit + int(self.BASE_ORDER_SIZE)
        ):
            self.add_buy(buy_quote, self.passive_size("BUY"))

        if (
            not took_sell
            and not cleared_sell
            and sell_quote is not None
            and self.sell_capacity > 0
            and position > -(self.soft_limit + int(self.BASE_ORDER_SIZE))
        ):
            self.add_sell(sell_quote, self.passive_size("SELL"))

        return self.orders


class TomatoesTrader(BaseProductTrader):
    PARAMETER_DEFAULTS = DEFAULT_TOMATOES_PARAMS

    def __init__(
        self,
        product: str,
        state: TradingState,
        mid_history: Dict[str, List[float]],
        position_limit: int,
        memory: Optional[Dict[str, object]] = None,
        params: Optional[Dict[str, float]] = None,
    ) -> None:
        super().__init__(product, state, mid_history, position_limit)
        self.memory = dict(memory) if isinstance(memory, dict) else {}
        self.apply_parameter_overrides(self.PARAMETER_DEFAULTS, params)
        self.soft_limit = int(position_limit * self.SOFT_LIMIT_RATIO)
        self.wall_fair_ewma = float(self.memory.get("wall_fair_ewma", self.mid or 0.0))
        self.wall_strength_ewma = float(self.memory.get("wall_strength_ewma", 0.0))
        self.queue_bias_ema = float(self.memory.get("queue_bias_ema", 0.0))
        self.queue_activity_ema = float(self.memory.get("queue_activity_ema", 0.0))
        self.lob_signal_ema = float(self.memory.get("lob_signal_ema", 0.0))
        self.inventory_anchor = float(self.memory.get("inventory_anchor", 0.0))
        price_window_raw = self.memory.get("mr_price_window", [])
        if isinstance(price_window_raw, list):
            self.mr_price_window = [float(value) for value in price_window_raw[-int(self.MR_LONG_WINDOW) :]]
        else:
            self.mr_price_window = []

    def wall_mid(self) -> Tuple[Optional[float], float]:
        if not self.has_book():
            return None, 0.0

        spread = float(self.spread)
        if spread < self.WALL_MIN_SPREAD or spread > self.WALL_MAX_SPREAD:
            return None, 0.0

        bid_weight = 0.0
        bid_price_sum = 0.0
        ask_weight = 0.0
        ask_price_sum = 0.0

        for index, (price, volume) in enumerate(self.buy_levels[: int(self.WALL_LEVELS)]):
            effective = max(0.0, float(volume) - self.WALL_SIZE_FLOOR)
            if effective <= 0.0:
                continue
            weight = effective / (index + 1.0)
            bid_weight += weight
            bid_price_sum += weight * float(price)

        for index, (price, volume) in enumerate(self.sell_levels[: int(self.WALL_LEVELS)]):
            effective = max(0.0, float(volume) - self.WALL_SIZE_FLOOR)
            if effective <= 0.0:
                continue
            weight = effective / (index + 1.0)
            ask_weight += weight
            ask_price_sum += weight * float(price)

        if bid_weight <= 1e-9 or ask_weight <= 1e-9:
            return None, 0.0

        wall_bid = bid_price_sum / bid_weight
        wall_ask = ask_price_sum / ask_weight
        balance = min(bid_weight, ask_weight) / max(bid_weight, ask_weight)
        depth_strength = min(1.0, (bid_weight + ask_weight) / 18.0)
        strength = max(0.0, min(1.0, balance * depth_strength))
        return (wall_bid + wall_ask) / 2.0, strength

    def blended_wall_fair(self) -> Tuple[Optional[float], float]:
        wall_mid, wall_strength = self.wall_mid()
        alpha = self.WALL_EWMA_ALPHA

        if wall_mid is not None:
            self.wall_fair_ewma = (1.0 - alpha) * self.wall_fair_ewma + alpha * wall_mid
            self.wall_strength_ewma = (1.0 - alpha) * self.wall_strength_ewma + alpha * wall_strength
        else:
            self.wall_strength_ewma = (1.0 - alpha) * self.wall_strength_ewma

        if self.wall_strength_ewma < self.WALL_PERSISTENCE_FLOOR:
            return None, 0.0

        return self.wall_fair_ewma, min(1.0, self.wall_strength_ewma)

    def trade_pressure(self) -> float:
        trades = self.state.market_trades.get(self.product, [])
        if not trades or not self.has_book():
            return 0.0
        total = 0.0
        signed = 0.0
        midpoint = float(self.mid)
        for trade in trades[-8:]:
            quantity = abs(float(trade.quantity))
            if quantity <= 0.0:
                continue
            direction = 1.0 if float(trade.price) >= midpoint else -1.0
            signed += direction * quantity
            total += quantity
        return 0.0 if total <= 1e-9 else signed / total

    def queue_reactive_signal(self) -> Tuple[float, float]:
        if not self.has_book():
            return 0.0, 0.0

        prev = self.memory.get("prev_book", {})
        if not isinstance(prev, dict):
            prev = {}

        if not prev:
            self.queue_bias_ema *= (1.0 - self.QUEUE_SIGNAL_ALPHA)
            self.queue_activity_ema *= (1.0 - self.QUEUE_SIGNAL_ALPHA)
            return self.queue_bias_ema, self.queue_activity_ema

        scale = max(1.0, float(self.spread) / 2.0, float(prev.get("spread", self.spread)) / 2.0)
        bid_up = max(0.0, float(self.best_bid) - float(prev.get("best_bid", self.best_bid))) / scale
        bid_down = max(0.0, float(prev.get("best_bid", self.best_bid)) - float(self.best_bid)) / scale
        ask_up = max(0.0, float(self.best_ask) - float(prev.get("best_ask", self.best_ask))) / scale
        ask_down = max(0.0, float(prev.get("best_ask", self.best_ask)) - float(self.best_ask)) / scale

        prev_bid_volume = max(1.0, float(prev.get("best_bid_volume", self.best_bid_volume)))
        prev_ask_volume = max(1.0, float(prev.get("best_ask_volume", self.best_ask_volume)))

        bid_depletion = 0.0
        bid_refill = 0.0
        if float(self.best_bid) == float(prev.get("best_bid", self.best_bid)):
            bid_depletion = max(0.0, float(prev.get("best_bid_volume", self.best_bid_volume)) - float(self.best_bid_volume)) / prev_bid_volume
            bid_refill = max(0.0, float(self.best_bid_volume) - float(prev.get("best_bid_volume", self.best_bid_volume))) / prev_bid_volume

        ask_depletion = 0.0
        ask_refill = 0.0
        if float(self.best_ask) == float(prev.get("best_ask", self.best_ask)):
            ask_depletion = max(0.0, float(prev.get("best_ask_volume", self.best_ask_volume)) - float(self.best_ask_volume)) / prev_ask_volume
            ask_refill = max(0.0, float(self.best_ask_volume) - float(prev.get("best_ask_volume", self.best_ask_volume))) / prev_ask_volume

        bid_depth = sum(max(0.0, float(volume)) / (index + 1.0) for index, (_price, volume) in enumerate(self.buy_levels[:3]))
        ask_depth = sum(max(0.0, float(volume)) / (index + 1.0) for index, (_price, volume) in enumerate(self.sell_levels[:3]))
        depth_skew = 0.0 if bid_depth + ask_depth <= 1e-9 else (bid_depth - ask_depth) / (bid_depth + ask_depth)
        trade_pressure = self.trade_pressure()

        buy_pressure = 0.45 * (bid_up + ask_up) + 0.35 * ask_depletion + 0.20 * bid_refill
        sell_pressure = 0.45 * (bid_down + ask_down) + 0.35 * bid_depletion + 0.20 * ask_refill
        raw_bias = (buy_pressure - sell_pressure) + (0.35 * depth_skew) + (0.25 * trade_pressure)
        raw_activity = buy_pressure + sell_pressure + abs(depth_skew) + abs(trade_pressure)

        alpha = self.QUEUE_SIGNAL_ALPHA
        self.queue_bias_ema = (1.0 - alpha) * self.queue_bias_ema + alpha * raw_bias
        self.queue_activity_ema = (1.0 - alpha) * self.queue_activity_ema + alpha * raw_activity
        return self.queue_bias_ema, self.queue_activity_ema

    def filtered_lob_signal(self) -> float:
        half_spread = max(1.0, float(self.spread) / 2.0)
        bid_levels = self.buy_levels[:3]
        ask_levels = self.sell_levels[:3]
        bid_weight = 0.0
        ask_weight = 0.0
        bid_distance = 0.0
        ask_distance = 0.0

        for index, (price, volume) in enumerate(bid_levels):
            weight = float(max(0, volume)) / (index + 1.0)
            bid_weight += weight
            bid_distance += weight * (float(self.best_bid) - float(price))
        for index, (price, volume) in enumerate(ask_levels):
            weight = float(max(0, volume)) / (index + 1.0)
            ask_weight += weight
            ask_distance += weight * (float(price) - float(self.best_ask))

        total = bid_weight + ask_weight
        depth_skew = 0.0 if total <= 1e-9 else (bid_weight - ask_weight) / total
        shape_skew = 0.0 if total <= 1e-9 else (ask_distance - bid_distance) / max(1.0, total)
        micro_premium = (float(self.micro) - float(self.mid)) / half_spread
        raw = (
            0.45 * self.imbalance
            + 0.30 * depth_skew
            + 0.20 * micro_premium
            + 0.05 * shape_skew
        )
        raw = max(-1.5, min(1.5, raw))
        alpha = self.LOB_SIGNAL_ALPHA
        self.lob_signal_ema = (1.0 - alpha) * self.lob_signal_ema + alpha * raw
        return self.lob_signal_ema

    def regression_metrics(self) -> Tuple[float, float, float, float]:
        history = self.mid_history.get(self.product, [])
        window = history[-int(self.REGRESSION_WINDOW) :]
        if len(window) < 2:
            return float(self.mid), float(self.mid), 0.0, 0.0

        n = len(window)
        x_mean = (n - 1) / 2.0
        y_mean = sum(window) / n
        var_x = sum((index - x_mean) ** 2 for index in range(n))
        cov_xy = sum((index - x_mean) * (price - y_mean) for index, price in enumerate(window))
        slope = cov_xy / var_x if var_x else 0.0
        intercept = y_mean - slope * x_mean

        fitted = [intercept + slope * index for index in range(n)]
        predicted_now = fitted[-1]
        predicted_next = intercept + slope * ((n - 1) + self.REGRESSION_HORIZON)

        ss_tot = sum((price - y_mean) ** 2 for price in window)
        ss_res = sum((price - fit) ** 2 for price, fit in zip(window, fitted))
        fit_quality = 0.0 if ss_tot <= 1e-9 else max(0.0, min(1.0, 1.0 - (ss_res / ss_tot)))

        diffs = [abs(window[index] - window[index - 1]) for index in range(1, n)]
        volatility = sum(diffs) / len(diffs) if diffs else 0.0
        return predicted_now, predicted_next, fit_quality, volatility

    def update_mean_reversion_window(self) -> None:
        if not self.has_book():
            return
        self.mr_price_window.append(float(self.mid))
        self.mr_price_window = self.mr_price_window[-int(self.MR_LONG_WINDOW) :]

    def mean_reversion_metrics(self) -> Tuple[float, float, float, float, float]:
        window = self.mr_price_window[-int(self.MR_LONG_WINDOW) :]
        if len(window) < max(4, int(self.MR_SHORT_WINDOW)):
            return 0.0, 0.0, 50.0, float(self.mid), 1.0

        short_window = window[-int(self.MR_SHORT_WINDOW) :]
        long_mean = sum(window) / len(window)
        short_mean = sum(short_window) / len(short_window)
        variance = sum((price - long_mean) ** 2 for price in window) / max(1, len(window) - 1)
        std = max(1.0, math.sqrt(max(0.0, variance)))
        zscore = (float(self.mid) - long_mean) / std
        ma_gap = (short_mean - long_mean) / std

        rsi_window = window[-(int(self.MR_RSI_WINDOW) + 1) :]
        gains = 0.0
        losses = 0.0
        for index in range(1, len(rsi_window)):
            change = rsi_window[index] - rsi_window[index - 1]
            if change > 0:
                gains += change
            elif change < 0:
                losses -= change
        if losses <= 1e-9:
            rsi = 100.0 if gains > 0 else 50.0
        else:
            rs = gains / losses
            rsi = 100.0 - (100.0 / (1.0 + rs))

        rsi_signal = (50.0 - rsi) / 18.0
        raw_signal = (-0.58 * zscore) + (-0.22 * ma_gap) + (0.20 * rsi_signal)
        signal = clamp(raw_signal, -self.MR_SIGNAL_CAP, self.MR_SIGNAL_CAP)
        strength = clamp(
            0.50 * min(1.5, abs(zscore)) / 1.5
            + 0.25 * min(1.5, abs(ma_gap)) / 1.5
            + 0.25 * min(30.0, abs(rsi - 50.0)) / 30.0,
            0.0,
            1.0,
        )
        return signal, strength, rsi, long_mean, std

    def refine_mean_reversion_signal(
        self,
        mr_signal: float,
        mr_strength: float,
        rsi: float,
        mr_mean: float,
        mr_std: float,
        provisional_edge: float,
        provisional_regime: str,
    ) -> Tuple[float, float]:
        if mr_strength <= 1e-9:
            return 0.0, 0.0

        zscore = 0.0 if mr_std <= 1e-9 else (float(self.mid) - mr_mean) / mr_std
        z_activation = clamp((abs(zscore) - self.MR_ZSCORE_ACTIVATION) / 0.95, 0.0, 1.0)
        rsi_activation = clamp((abs(rsi - 50.0) - self.MR_RSI_ACTIVATION) / 20.0, 0.0, 1.0)
        activation = 0.60 * z_activation + 0.40 * rsi_activation

        if provisional_regime != "range":
            activation *= self.MR_TREND_DAMP

        queue_bias, _queue_activity = self.queue_reactive_signal()
        lob_signal = self.filtered_lob_signal()
        for signal in (provisional_edge, queue_bias, lob_signal):
            if mr_signal * signal < -0.06:
                activation *= self.MR_CONFLICT_DAMP

        refined_strength = mr_strength * activation
        if refined_strength < 0.08:
            return 0.0, 0.0
        return mr_signal * activation, refined_strength

    def time_fraction_remaining(self) -> float:
        timestamp = float(getattr(self.state, "timestamp", 0))
        remaining_ticks = max(0.0, self.TIME_HORIZON_TICKS - (timestamp / 100.0))
        return remaining_ticks / self.TIME_HORIZON_TICKS

    def hybrid_alpha(self) -> Tuple[float, float]:
        reference_price = float(self.recent_average)
        wall_mid, wall_strength = self.blended_wall_fair()
        if wall_mid is not None:
            reference_price += self.WALL_ALPHA_WEIGHT * wall_strength * (wall_mid - reference_price)
        half_spread = max(1.0, float(self.spread) / 2.0)
        flow_signal = self.imbalance * half_spread * self.ALPHA_FLOW_SPREAD_SCALE
        queue_bias, _queue_activity = self.queue_reactive_signal()
        lob_signal = self.filtered_lob_signal()
        hybrid_fair = (
            self.ALPHA_REFERENCE_WEIGHT * reference_price
            + self.ALPHA_MID_WEIGHT * float(self.mid)
            + self.ALPHA_MICRO_WEIGHT * float(self.micro)
            + self.ALPHA_FLOW_WEIGHT * (float(self.mid) + flow_signal)
            + self.QUEUE_ALPHA_WEIGHT * half_spread * queue_bias
        )
        hybrid_fair += self.LOB_ALPHA_WEIGHT * half_spread * lob_signal
        alpha = hybrid_fair - float(self.mid)
        alpha = max(-self.ALPHA_CAP, min(self.ALPHA_CAP, alpha))
        return hybrid_fair, alpha

    def guarded_hybrid_alpha(self, hybrid_alpha: float, regression_edge: float, regime: str) -> float:
        weight = 1.0
        if regime == "range":
            weight *= self.RANGE_ALPHA_DAMP

        if hybrid_alpha * regression_edge < 0:
            weight *= self.CONFLICT_ALPHA_DAMP

        if hybrid_alpha * self.imbalance < 0:
            weight *= self.CONFLICT_ALPHA_DAMP

        if hybrid_alpha * self.momentum < 0:
            weight *= self.MOMENTUM_ALPHA_DAMP

        position = self.projected_position()
        if hybrid_alpha * position > 0:
            abs_pos = abs(position)
            if abs_pos >= self.POSITION_ALPHA_DAMP_START:
                if abs_pos >= self.POSITION_ALPHA_DAMP_END:
                    weight *= 0.0
                else:
                    span = self.POSITION_ALPHA_DAMP_END - self.POSITION_ALPHA_DAMP_START
                    ratio = (abs_pos - self.POSITION_ALPHA_DAMP_START) / max(1e-9, span)
                    weight *= max(0.0, 1.0 - ratio)

        return hybrid_alpha * weight

    def control_gamma(self, regime: str) -> float:
        if regime == "trend_up" or regime == "trend_down":
            return self.GAMMA_TREND
        if regime == "volatile":
            return self.GAMMA_VOLATILE
        return self.GAMMA_RANGE

    def signal_confidence(self, predicted_edge: float, fit_quality: float) -> float:
        scale = max(1.0, float(self.spread) / 2.0)
        normalized_edge = min(1.0, abs(predicted_edge) / (1.9 * scale))
        queue_bias, _queue_activity = self.queue_reactive_signal()
        lob_signal = self.filtered_lob_signal()
        edge_sign = 0.0
        if predicted_edge > 1e-9:
            edge_sign = 1.0
        elif predicted_edge < -1e-9:
            edge_sign = -1.0
        agreement = 0.0
        if edge_sign != 0.0:
            for signal in (self.imbalance, queue_bias, lob_signal):
                if signal * edge_sign > 0:
                    agreement += min(1.0, abs(signal))
                elif signal * edge_sign < 0:
                    agreement -= min(1.0, abs(signal))
        confidence = 0.55 * fit_quality + 0.25 * normalized_edge + 0.20 * ((agreement + 3.0) / 6.0)
        return max(0.0, min(1.0, confidence))

    def current_anchor_target(self) -> int:
        cap = float(self.soft_limit) * self.ANCHOR_CAP_RATIO
        return int(round(max(-cap, min(cap, self.inventory_anchor))))

    def anchor_target(self, regime: str, predicted_edge: float, fit_quality: float) -> int:
        confidence = self.signal_confidence(predicted_edge, fit_quality)
        scale = max(1.0, float(self.spread) / 2.0)
        signal = max(-1.0, min(1.0, predicted_edge / (2.15 * scale))) * max(0.25, confidence)
        cap = float(self.soft_limit) * self.ANCHOR_CAP_RATIO
        desired = cap * signal
        if regime == "range":
            desired *= 0.42
        elif regime == "volatile":
            desired *= 0.18
        self.inventory_anchor = self.ANCHOR_PHI * self.inventory_anchor + self.ANCHOR_BETA * desired
        return int(round(max(-cap, min(cap, self.inventory_anchor))))

    def inventory_pressure_multiplier(self, predicted_edge: float) -> float:
        position = self.projected_position()
        if predicted_edge > 0:
            if position > 0:
                return self.ALIGNED_RESERVATION_MULT
            if position < 0:
                return self.WRONG_WAY_RESERVATION_MULT
        elif predicted_edge < 0:
            if position < 0:
                return self.ALIGNED_RESERVATION_MULT
            if position > 0:
                return self.WRONG_WAY_RESERVATION_MULT
        return 1.0

    def gap_pressure(
        self,
        target_position: int,
        regime: str,
        volatility: float,
    ) -> float:
        gap = self.projected_position() - target_position
        if gap == 0:
            return 0.0
        normalized = abs(gap) / max(1.0, float(self.soft_limit))
        curved = normalized ** self.GAP_CURVE_POWER
        if regime == "range":
            curved *= 1.12
        elif regime == "volatile":
            curved *= 1.20
        else:
            curved *= 0.90
        curved *= min(1.35, max(0.7, volatility / 1.8))
        return math.copysign(min(2.0, curved), gap)

    def reservation_adjustment(
        self,
        regime: str,
        target_position: int,
        predicted_edge: float,
        volatility: float,
    ) -> float:
        position = self.projected_position()
        inventory_gap = position - target_position
        gamma = self.control_gamma(regime)
        tau = self.time_fraction_remaining()
        reservation_shift = inventory_gap * gamma * max(0.6, volatility) * self.RESERVATION_SCALE * max(0.35, tau)
        reservation_shift += (
            self.GAP_RESERVATION_WEIGHT
            * max(1.0, float(self.spread) / 2.0)
            * self.gap_pressure(target_position, regime, volatility)
        )
        reservation_shift += (
            self.ANCHOR_RESERVATION_WEIGHT
            * self.inventory_pressure_multiplier(predicted_edge)
            * max(1.0, float(self.spread) / 2.0)
            * ((position - self.current_anchor_target()) / max(1.0, float(self.soft_limit)))
        )

        if regime == "trend_up":
            reservation_shift -= self.TREND_RESERVATION_BIAS * max(0.0, predicted_edge)
        elif regime == "trend_down":
            reservation_shift += self.TREND_RESERVATION_BIAS * max(0.0, -predicted_edge)
        elif regime == "range":
            if predicted_edge > 0:
                reservation_shift -= self.RANGE_RESERVATION_BIAS * predicted_edge
            else:
                reservation_shift += self.RANGE_RESERVATION_BIAS * abs(predicted_edge)

        return reservation_shift

    def classify_state(
        self,
        predicted_edge: float,
        fit_quality: float,
        volatility: float,
    ) -> str:
        trend_threshold = self.TREND_EDGE_THRESHOLD * self.ALPHA_THRESHOLD_SCALE
        if float(self.spread) >= self.TOXIC_SPREAD_THRESHOLD and volatility >= self.TOXIC_VOLATILITY_THRESHOLD:
            return "volatile"
        if (
            predicted_edge >= trend_threshold
            and fit_quality >= self.FIT_THRESHOLD
            and self.imbalance >= self.TREND_IMBALANCE_THRESHOLD
            and self.momentum >= 0.75
            and float(self.micro) >= float(self.mid)
        ):
            return "trend_up"
        if (
            predicted_edge <= -trend_threshold
            and fit_quality >= self.FIT_THRESHOLD
            and self.imbalance <= -self.TREND_IMBALANCE_THRESHOLD
            and self.momentum <= -0.75
            and float(self.micro) <= float(self.mid)
        ):
            return "trend_down"
        return "range"

    def target_band(self, regime: str, predicted_edge: float, fit_quality: float) -> Tuple[int, int]:
        conviction = abs(predicted_edge) * max(0.5, fit_quality)
        if regime == "trend_up":
            return (22, 44) if conviction >= self.STRONG_TREND_EDGE else (10, 28)
        if regime == "trend_down":
            return (-44, -22) if conviction >= self.STRONG_TREND_EDGE else (-28, -10)
        if regime == "volatile":
            return -6, 6
        return -14, 14

    def target_position(
        self,
        regime: str,
        predicted_edge: float,
        fit_quality: float,
        mr_signal: float,
        mr_strength: float,
    ) -> int:
        lower, upper = self.target_band(regime, predicted_edge, fit_quality)
        position = self.projected_position()
        if position < lower:
            base_target = lower
        elif position > upper:
            base_target = upper
        elif regime == "trend_up":
            base_target = upper
        elif regime == "trend_down":
            base_target = lower
        else:
            base_target = int(round(self.MR_RANGE_TARGET_SCALE * mr_signal * mr_strength / max(1.0, self.MR_SIGNAL_CAP)))
        anchor_target = self.anchor_target(regime, predicted_edge, fit_quality)
        blended = int(round((1.0 - self.ANCHOR_TARGET_BLEND) * base_target + self.ANCHOR_TARGET_BLEND * anchor_target))
        return max(lower, min(upper, blended))

    def toxicity(self, volatility: float) -> float:
        score = 0.0
        if volatility >= 2.0:
            score += 0.5
        if abs(self.imbalance) >= 0.45:
            score += 0.5
        return score

    def fair_value(
        self,
        regime: str,
        target_position: int,
        predicted_now: float,
        predicted_next: float,
        hybrid_alpha: float,
        mr_signal: float,
        mr_strength: float,
    ) -> float:
        line_gap = predicted_now - float(self.mid)
        wall_mid, wall_strength = self.blended_wall_fair()
        scaled_imbalance = self.imbalance * self.ALPHA_IMBALANCE_SCALE
        half_spread = max(1.0, float(self.spread) / 2.0)
        queue_bias, _queue_activity = self.queue_reactive_signal()
        lob_signal = self.filtered_lob_signal()
        gap_pressure = self.gap_pressure(
            target_position,
            regime,
            max(1.0, abs(predicted_next - predicted_now)),
        )
        fair = (
            self.MID_WEIGHT * float(self.mid)
            + self.MICRO_WEIGHT * float(self.micro)
            + self.HISTORY_WEIGHT * float(self.recent_average)
            + self.REGRESSION_WEIGHT * predicted_next
            + self.IMBALANCE_WEIGHT * scaled_imbalance
            + self.QUEUE_FAIR_WEIGHT * half_spread * queue_bias
        )
        fair += self.FAIR_ALPHA_WEIGHT * hybrid_alpha
        fair += (target_position - self.projected_position()) / self.POSITION_BIAS_DIVISOR
        fair -= self.GAP_FAIR_WEIGHT * half_spread * gap_pressure
        fair += self.LOB_FAIR_WEIGHT * half_spread * lob_signal
        if regime == "range":
            fair += self.MR_FAIR_WEIGHT * half_spread * mr_signal * (0.65 + 0.35 * mr_strength)
        if wall_mid is not None:
            wall_weight = self.WALL_FAIR_WEIGHT * wall_strength
            if regime in {"trend_up", "trend_down"}:
                wall_weight *= 0.60
            fair += wall_weight * (wall_mid - float(self.mid))
        if regime == "range":
            fair += self.RESIDUAL_REVERT_WEIGHT * line_gap
        else:
            fair += (0.10 * line_gap) + (self.TREND_FAIR_BONUS * (predicted_next - float(self.mid)))
        return fair

    def next_memory(self) -> Dict[str, float]:
        return {
            "wall_fair_ewma": float(self.wall_fair_ewma),
            "wall_strength_ewma": float(self.wall_strength_ewma),
            "queue_bias_ema": float(self.queue_bias_ema),
            "queue_activity_ema": float(self.queue_activity_ema),
            "lob_signal_ema": float(self.lob_signal_ema),
            "inventory_anchor": float(self.inventory_anchor),
            "mr_price_window": list(self.mr_price_window)[-int(self.MR_LONG_WINDOW) :],
            "prev_book": {
                "best_bid": float(self.best_bid),
                "best_ask": float(self.best_ask),
                "best_bid_volume": float(self.best_bid_volume),
                "best_ask_volume": float(self.best_ask_volume),
                "spread": float(self.spread),
            },
        }

    def adjusted_fair_value(
        self,
        regime: str,
        target_position: int,
        predicted_now: float,
        predicted_next: float,
        hybrid_alpha: float,
        mr_signal: float,
        mr_strength: float,
    ) -> float:
        fair = self.fair_value(
            regime,
            target_position,
            predicted_now,
            predicted_next,
            hybrid_alpha,
            mr_signal,
            mr_strength,
        )
        return fair - (self.projected_position() * self.INVENTORY_SKEW)

    def take_edge(
        self,
        side: str,
        regime: str,
        predicted_edge: float,
        fit_quality: float,
        volatility: float,
        mr_signal: float,
        mr_strength: float,
    ) -> float:
        edge = self.BASE_TAKE_EDGE
        queue_bias, _queue_activity = self.queue_reactive_signal()
        lob_signal = self.filtered_lob_signal()

        if int(self.spread) >= 14:
            edge += 0.4

        position = self.projected_position()

        if side == "BUY":
            if position <= -20:
                edge -= 0.5
            elif position >= 20:
                edge += 0.5
        else:
            if position >= 20:
                edge -= 0.5
            elif position <= -20:
                edge += 0.5

        edge += 0.20 * self.toxicity(volatility)

        if regime == "trend_up":
            if side == "BUY":
                edge += -0.35 - self.TREND_BUY_TAKE_EXTRA
            else:
                edge += 0.55 + (0.50 * self.TREND_SELL_HOLD_EXTRA)
        elif regime == "trend_down":
            if side == "SELL":
                edge += -0.35 - self.TREND_BUY_TAKE_EXTRA
            else:
                edge += 0.55 + (0.50 * self.TREND_SELL_HOLD_EXTRA)
        elif regime == "volatile":
            edge += 0.50
        else:
            if side == "BUY" and predicted_edge <= -self.TREND_EDGE_THRESHOLD:
                edge += 0.35
            if side == "SELL" and predicted_edge >= self.TREND_EDGE_THRESHOLD:
                edge += 0.35

        if predicted_edge > 0 and side == "BUY":
            edge -= min(0.20, 0.05 * predicted_edge * max(0.5, fit_quality))
        elif predicted_edge < 0 and side == "SELL":
            edge -= min(0.20, 0.05 * abs(predicted_edge) * max(0.5, fit_quality))

        if side == "BUY":
            edge -= self.QUEUE_TAKE_SHIFT * max(0.0, queue_bias)
            edge += self.QUEUE_TAKE_SHIFT * max(0.0, -queue_bias)
        else:
            edge -= self.QUEUE_TAKE_SHIFT * max(0.0, -queue_bias)
            edge += self.QUEUE_TAKE_SHIFT * max(0.0, queue_bias)

        if lob_signal != 0.0:
            aligned = (side == "BUY" and lob_signal > 0) or (side == "SELL" and lob_signal < 0)
            if aligned:
                edge -= self.LOB_TAKE_SHIFT * min(1.0, abs(lob_signal))
            else:
                edge += 0.05 * min(1.0, abs(lob_signal))

        if regime == "range" and mr_strength > 0.0:
            if side == "BUY":
                if mr_signal > 0:
                    edge -= self.MR_TAKE_SHIFT * mr_strength
                elif mr_signal < 0:
                    edge += 0.08 * mr_strength
            else:
                if mr_signal < 0:
                    edge -= self.MR_TAKE_SHIFT * mr_strength
                elif mr_signal > 0:
                    edge += 0.08 * mr_strength

        return max(0.5, edge)

    def quote_edge(
        self,
        regime: str,
        volatility: float,
        fit_quality: float,
        target_position: int,
        mr_strength: float,
    ) -> float:
        tau = self.time_fraction_remaining()
        gamma = self.control_gamma(regime)
        edge = max(self.BASE_QUOTE_EDGE, float(self.spread) / 3.5)
        edge = min(self.MAX_QUOTE_EDGE, edge)
        queue_bias, _queue_activity = self.queue_reactive_signal()
        lob_signal = self.filtered_lob_signal()
        gap_pressure = abs(self.gap_pressure(target_position, regime, volatility))

        if abs(self.projected_position()) >= self.soft_limit:
            edge += 0.5

        if regime == "volatile":
            edge += 1.0
        elif regime in {"trend_up", "trend_down"}:
            edge += 0.15 + (0.10 * fit_quality)

        edge += self.SPREAD_VOL_COEF * min(3.0, volatility)
        edge += self.SPREAD_INV_COEF * gamma * min(self.position_limit, abs(self.projected_position()))
        edge += self.SPREAD_TIME_COEF * gamma * tau
        edge += self.GAP_QUOTE_EDGE_WEIGHT * gap_pressure
        if regime == "trend_up":
            edge -= self.QUEUE_EDGE_SHIFT * max(0.0, queue_bias)
        elif regime == "trend_down":
            edge -= self.QUEUE_EDGE_SHIFT * max(0.0, -queue_bias)
        elif regime == "range":
            edge += 0.05 * abs(queue_bias)
            edge -= self.MR_QUOTE_SHIFT * mr_strength
        if lob_signal != 0.0 and regime != "volatile":
            edge -= self.LOB_QUOTE_SHIFT * min(1.0, abs(lob_signal))
        return min(self.MAX_QUOTE_EDGE, edge)

    def passive_quotes(
        self,
        adjusted_fair: float,
        regime: str,
        target_position: int,
        predicted_edge: float,
        fit_quality: float,
        volatility: float,
        mr_strength: float,
    ) -> Tuple[Optional[int], Optional[int]]:
        edge = self.quote_edge(regime, volatility, fit_quality, target_position, mr_strength)
        buy_quote = math.floor(adjusted_fair - edge)
        sell_quote = math.ceil(adjusted_fair + edge)
        buy_quote, sell_quote = self.clamp_inside_spread(buy_quote, sell_quote)

        position = self.projected_position()
        if regime == "trend_up":
            if buy_quote is not None and position < target_position:
                buy_quote = min(
                    int(self.best_ask) - 1,
                    max(int(self.best_bid) + 1, buy_quote + int(self.TREND_PASSIVE_PUSH)),
                )
            if sell_quote is not None and position > 0:
                lift = 1 if predicted_edge >= self.TREND_EDGE_THRESHOLD else 0
                if predicted_edge >= self.STRONG_TREND_EDGE:
                    lift += 1
                lift += int(self.TREND_QUOTE_LIFT_EXTRA)
                sell_quote += lift
        elif regime == "trend_down":
            if sell_quote is not None and position > target_position:
                sell_quote = max(
                    int(self.best_bid) + 1,
                    min(int(self.best_ask) - 1, sell_quote - int(self.TREND_PASSIVE_PUSH)),
                )
            if buy_quote is not None and position < 0:
                drop = 1 if predicted_edge <= -self.TREND_EDGE_THRESHOLD else 0
                if predicted_edge <= -self.STRONG_TREND_EDGE:
                    drop += 1
                buy_quote -= drop
        elif regime == "volatile" and abs(position) <= 6:
            buy_quote = None
            sell_quote = None

        return self.clamp_inside_spread(buy_quote, sell_quote)

    def passive_size(self, side: str, regime: str, volatility: float) -> int:
        size = self.PASSIVE_SIZE
        queue_bias, _queue_activity = self.queue_reactive_signal()
        if int(self.spread) >= 14:
            size += 1

        if regime == "volatile":
            size = max(1, size - 3)
        elif regime in {"trend_up", "trend_down"}:
            size = max(1, size + int(self.TREND_PASSIVE_SIZE_BONUS))

        size = max(1, int(size - self.toxicity(volatility)))

        position = self.projected_position()
        if side == "BUY":
            if position <= -20:
                size += 1
            elif position >= 20:
                size = max(1, size - 2)
        else:
            if position >= 20:
                size += 1
            elif position <= -20:
                size = max(1, size - 2)

        gap_norm = min(1.0, abs(self.projected_position()) / max(1.0, float(self.soft_limit)))
        size = max(1, int(round(size * (1.0 - self.GAP_PASSIVE_SIZE_WEIGHT * gap_norm))))
        if side == "BUY" and queue_bias > 0:
            size += int(self.QUEUE_SIZE_BONUS)
        elif side == "SELL" and queue_bias < 0:
            size += int(self.QUEUE_SIZE_BONUS)
        return size

    def allow_passive(self, side: str, regime: str) -> bool:
        position = self.projected_position()
        if side == "BUY" and position >= self.soft_limit:
            return False
        if side == "SELL" and position <= -self.soft_limit:
            return False
        if regime == "volatile" and abs(position) <= 6:
            return False
        return True

    def take_orders(
        self,
        regime: str,
        target_position: int,
        adjusted_fair: float,
        predicted_edge: float,
        fit_quality: float,
        volatility: float,
        mr_signal: float,
        mr_strength: float,
    ) -> Tuple[bool, bool]:
        took_buy = False
        took_sell = False

        if (
            int(self.best_ask) <= adjusted_fair - self.take_edge("BUY", regime, predicted_edge, fit_quality, volatility, mr_signal, mr_strength)
            and self.buy_capacity > 0
        ):
            take_limit = self.MAX_TAKE_SIZE + (int(self.TREND_ENTRY_TAKE_BONUS) if regime == "trend_up" else 0)
            if regime != "range" and self.projected_position() >= target_position:
                pass
            else:
                quantity = min(self.best_ask_volume, take_limit)
                if regime != "range":
                    quantity = min(quantity, max(1, target_position - self.projected_position()))
                before = self.buy_capacity
                self.add_buy(int(self.best_ask), quantity)
                took_buy = self.buy_capacity < before

        if (
            int(self.best_bid) >= adjusted_fair + self.take_edge("SELL", regime, predicted_edge, fit_quality, volatility, mr_signal, mr_strength)
            and self.sell_capacity > 0
        ):
            take_limit = self.MAX_TAKE_SIZE + (int(self.TREND_ENTRY_TAKE_BONUS) if regime == "trend_down" else 0)
            required_bonus = 0.0
            if regime == "trend_up" and predicted_edge >= self.TREND_EDGE_THRESHOLD:
                required_bonus += self.TREND_HOLD_EXIT_BONUS + self.TREND_SELL_HOLD_EXTRA
            if regime == "trend_up" and predicted_edge >= self.STRONG_TREND_EDGE:
                required_bonus += self.STRONG_TREND_HOLD_EXIT_BONUS + self.TREND_SELL_HOLD_EXTRA
            required_bonus += self.HOLD_TIME_COEF * self.time_fraction_remaining()
            required_bonus += self.HOLD_VOL_COEF * min(3.0, volatility)
            if regime != "range" and self.projected_position() <= target_position:
                pass
            elif int(self.best_bid) < adjusted_fair + self.take_edge("SELL", regime, predicted_edge, fit_quality, volatility, mr_signal, mr_strength) + required_bonus:
                pass
            else:
                quantity = min(self.best_bid_volume, take_limit)
                if regime != "range":
                    quantity = min(quantity, max(1, self.projected_position() - target_position))
                before = self.sell_capacity
                self.add_sell(int(self.best_bid), quantity)
                took_sell = self.sell_capacity < before

        return took_buy, took_sell

    def run(self) -> List[Order]:
        if not self.has_book():
            return self.orders

        self.update_mean_reversion_window()
        predicted_now, predicted_next, fit_quality, volatility = self.regression_metrics()
        mr_signal, mr_strength, rsi, mr_mean, mr_std = self.mean_reversion_metrics()
        _hybrid_fair, hybrid_alpha = self.hybrid_alpha()
        regression_edge = (predicted_next - float(self.mid)) * self.ALPHA_EDGE_SCALE
        provisional_edge = regression_edge
        provisional_next = float(self.mid) + provisional_edge
        provisional_regime = self.classify_state(provisional_edge, fit_quality, volatility)
        mr_signal, mr_strength = self.refine_mean_reversion_signal(
            mr_signal,
            mr_strength,
            rsi,
            mr_mean,
            mr_std,
            provisional_edge,
            provisional_regime,
        )
        hybrid_alpha = self.guarded_hybrid_alpha(hybrid_alpha, regression_edge, provisional_regime)
        predicted_edge = (
            (1.0 - self.ALPHA_BLEND_WEIGHT) * regression_edge
            + self.ALPHA_BLEND_WEIGHT * hybrid_alpha
        )
        predicted_next = float(self.mid) + predicted_edge
        regime = self.classify_state(predicted_edge, fit_quality, volatility)
        target_position = self.target_position(regime, predicted_edge, fit_quality, mr_signal, mr_strength)
        adjusted_fair = self.adjusted_fair_value(
            regime,
            target_position,
            predicted_now,
            predicted_next,
            hybrid_alpha,
            mr_signal,
            mr_strength,
        ) - self.reservation_adjustment(regime, target_position, predicted_edge, volatility)
        took_buy, took_sell = self.take_orders(
            regime,
            target_position,
            adjusted_fair,
            predicted_edge,
            fit_quality,
            volatility,
            mr_signal,
            mr_strength,
        )

        buy_quote, sell_quote = self.passive_quotes(
            adjusted_fair,
            regime,
            target_position,
            predicted_edge,
            fit_quality,
            volatility,
            mr_strength,
        )
        position = self.projected_position()

        if (
            not took_buy
            and buy_quote is not None
            and self.buy_capacity > 0
            and self.allow_passive("BUY", regime)
        ):
            if regime == "range" or position < target_position:
                quantity = min(self.passive_size("BUY", regime, volatility), self.buy_capacity)
                if regime != "range":
                    quantity = min(quantity, max(1, target_position - position))
                self.add_buy(buy_quote, quantity)

        position = self.projected_position()
        if (
            not took_sell
            and sell_quote is not None
            and self.sell_capacity > 0
            and self.allow_passive("SELL", regime)
        ):
            if regime == "range" or position > target_position:
                quantity = min(self.passive_size("SELL", regime, volatility), self.sell_capacity)
                if regime != "range":
                    quantity = min(quantity, max(1, position - target_position))
                self.add_sell(sell_quote, quantity)

        return self.orders


class Trader:
    POSITION_LIMITS: Dict[str, int] = {
        "EMERALDS": 80,
        "TOMATOES": 80,
    }

    PRODUCT_TRADERS = {
        "EMERALDS": EmeraldsTrader,
        "TOMATOES": TomatoesTrader,
    }

    def load_trader_data(self, trader_data: str) -> Tuple[Dict[str, List[float]], Dict[str, Dict[str, object]]]:
        if not trader_data:
            return {}, {}
        try:
            parsed = json.loads(trader_data)
        except json.JSONDecodeError:
            return {}, {}

        raw_history = parsed.get("mid_history", {})
        cleaned: Dict[str, List[float]] = {}
        if isinstance(raw_history, dict):
            for product, values in raw_history.items():
                if isinstance(values, list):
                    cleaned[product] = [float(value) for value in values[-BaseProductTrader.HISTORY_LENGTH :]]

        raw_memory = parsed.get("memory", {})
        memory: Dict[str, Dict[str, object]] = {}
        if isinstance(raw_memory, dict):
            for product, value in raw_memory.items():
                if isinstance(value, dict):
                    memory[product] = value
        return cleaned, memory

    def build_trader_data(self, mid_history: Dict[str, List[float]], memory: Dict[str, Dict[str, object]]) -> str:
        return json.dumps({"mid_history": mid_history, "memory": memory}, separators=(",", ":"))

    def run(self, state: TradingState):
        result: Dict[str, List[Order]] = {}
        mid_history, memory = self.load_trader_data(state.traderData)
        next_memory: Dict[str, Dict[str, object]] = dict(memory)

        for product in state.order_depths:
            if product not in self.PRODUCT_TRADERS:
                result[product] = []
                continue

            trader_class = self.PRODUCT_TRADERS[product]
            trader_kwargs = {}
            if product == "TOMATOES":
                trader_kwargs["memory"] = memory.get(product, {})
            trader = trader_class(product, state, mid_history, self.POSITION_LIMITS[product], **trader_kwargs)
            result[product] = trader.run()
            if product == "TOMATOES":
                next_memory[product] = trader.next_memory()

        conversions = 0
        trader_data = self.build_trader_data(mid_history, next_memory)
        return result, conversions, trader_data
