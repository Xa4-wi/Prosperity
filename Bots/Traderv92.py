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
    "BOOTSTRAP_MIN_SAMPLES": 8,
    "MR_READY_SAMPLES": 18,
    "MR_SHORT_WINDOW": 6,
    "MR_RSI_WINDOW": 10,
    "ENTRY_Z": 0.90,
    "AGGRESSIVE_Z": 1.35,
    "EXIT_Z": 0.28,
    "TREND_BLOCK": 0.70,
    "TREND_ALLOW": 0.35,
    "TOXIC_SPREAD": 14.0,
    "TOXIC_VOL": 3.0,
    "BOOTSTRAP_MID_WEIGHT": 0.65,
    "BOOTSTRAP_MICRO_WEIGHT": 0.35,
    "MR_MID_WEIGHT": 0.22,
    "MR_MICRO_WEIGHT": 0.20,
    "MR_LONG_WEIGHT": 0.58,
    "MR_SHORT_WEIGHT": 0.10,
    "AGGR_MID_WEIGHT": 0.16,
    "AGGR_MICRO_WEIGHT": 0.22,
    "AGGR_LONG_WEIGHT": 0.62,
    "AGGR_SHORT_WEIGHT": 0.14,
    "BASE_QUOTE_EDGE": 2.35,
    "BOOTSTRAP_QUOTE_EDGE": 3.10,
    "AGGR_QUOTE_EDGE": 1.65,
    "BASE_TAKE_EDGE": 0.95,
    "AGGR_TAKE_EDGE": 0.55,
    "BOOTSTRAP_PASSIVE_SIZE": 3,
    "BASE_PASSIVE_SIZE": 6,
    "AGGR_PASSIVE_SIZE": 9,
    "BOOTSTRAP_MAX_TAKE": 3,
    "BASE_MAX_TAKE": 8,
    "AGGR_MAX_TAKE": 12,
    "INVENTORY_SKEW": 0.050,
    "SOFT_LIMIT_RATIO": 0.56,
    "ZONE_LEAN": 20,
    "ZONE_UNWIND": 35,
    "ZONE_EMERGENCY": 50,
    "ZONE_HARD": 65,
    "CAP_WEAK": 12,
    "CAP_MEDIUM": 22,
    "CAP_STRONG": 34,
    "CAP_AGGRESSIVE": 46,
    "CAP_MAX": 56,
    "UNWIND_TARGET": 14,
    "MICRO_ALIGN_BONUS": 0.35,
    "TREND_PENALTY": 0.45,
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
        self.current_day = self.get_day_marker()
        self.handle_day_reset()
        window_raw = self.memory.get("price_window", [])
        if isinstance(window_raw, list):
            self.price_window = [float(value) for value in window_raw[-int(self.MR_READY_SAMPLES):]]
        else:
            self.price_window = []
        self.append_price()

    def get_day_marker(self) -> Optional[int]:
        raw = getattr(self.state, "trading_day", None)
        if raw is None:
            raw = getattr(self.state, "day", None)
        try:
            return int(raw) if raw is not None else None
        except (TypeError, ValueError):
            return None

    def handle_day_reset(self) -> None:
        previous_day = self.memory.get("day")
        if self.current_day is None or previous_day is None:
            return
        try:
            previous_day_int = int(previous_day)
        except (TypeError, ValueError):
            return
        if previous_day_int != self.current_day:
            self.memory = {}
            self.mid_history[self.product] = []

    def append_price(self) -> None:
        if not self.has_book():
            return
        self.price_window.append(float(self.mid))
        self.price_window = self.price_window[-int(self.MR_READY_SAMPLES):]

    def next_memory(self) -> Dict[str, object]:
        data: Dict[str, object] = {
            "price_window": list(self.price_window)[-int(self.MR_READY_SAMPLES):],
        }
        if self.current_day is not None:
            data["day"] = int(self.current_day)
        return data

    def readiness(self) -> float:
        return clamp(len(self.price_window) / max(1.0, float(self.MR_READY_SAMPLES)), 0.0, 1.0)

    def bootstrap_mode(self) -> bool:
        return len(self.price_window) < int(self.BOOTSTRAP_MIN_SAMPLES)

    def market_stats(self) -> Tuple[float, float, float, float, float]:
        window = self.price_window
        if not window:
            return float(self.mid), float(self.mid), 0.0, 50.0, 1.0

        short_window = window[-int(self.MR_SHORT_WINDOW):]
        long_mean = sum(window) / len(window)
        short_mean = sum(short_window) / len(short_window)
        variance = sum((price - long_mean) ** 2 for price in window) / max(1, len(window) - 1)
        std = max(1.0, math.sqrt(max(0.0, variance)))
        zscore = (float(self.mid) - long_mean) / std

        rsi_window = window[-(int(self.MR_RSI_WINDOW) + 1):]
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

        half_spread = max(1.0, float(self.spread) / 2.0)
        micro_premium = (float(self.micro) - float(self.mid)) / half_spread
        trend_score = (
            0.50 * ((short_mean - long_mean) / std)
            + 0.25 * micro_premium
            + 0.25 * self.imbalance
        )
        return long_mean, short_mean, zscore, rsi, trend_score

    def volatility(self) -> float:
        window = self.price_window[-8:]
        if len(window) < 2:
            return max(1.0, float(self.spread) / 2.0)
        diffs = [abs(window[i] - window[i - 1]) for i in range(1, len(window))]
        return sum(diffs) / len(diffs) if diffs else max(1.0, float(self.spread) / 2.0)

    def inventory_mode(self) -> str:
        abs_pos = abs(self.projected_position())
        if abs_pos >= int(self.ZONE_HARD):
            return "hard"
        if abs_pos >= int(self.ZONE_EMERGENCY):
            return "emergency"
        if abs_pos >= int(self.ZONE_UNWIND):
            return "unwind"
        if abs_pos >= int(self.ZONE_LEAN):
            return "lean"
        return "neutral"

    def classify_phase(self, zscore: float, trend_score: float, vol: float) -> str:
        if self.bootstrap_mode():
            return "bootstrap"
        if float(self.spread) >= self.TOXIC_SPREAD or vol >= self.TOXIC_VOL:
            return "cautious"
        fade_blocked = zscore * trend_score > self.TREND_BLOCK
        if abs(zscore) >= self.AGGRESSIVE_Z and not fade_blocked:
            return "aggressive_mr"
        return "mr"

    def target_cap(self, phase: str, zscore: float) -> int:
        strength = abs(zscore)
        if strength < self.ENTRY_Z:
            cap = int(self.CAP_WEAK)
        elif strength < self.AGGRESSIVE_Z:
            cap = int(self.CAP_MEDIUM)
        elif phase == "aggressive_mr":
            cap = int(self.CAP_AGGRESSIVE)
        else:
            cap = int(self.CAP_STRONG)
        return min(self.position_limit, cap, int(self.CAP_MAX))

    def target_position(
        self,
        phase: str,
        zscore: float,
        rsi: float,
        trend_score: float,
    ) -> int:
        if phase == "bootstrap":
            return 0

        if abs(zscore) < self.EXIT_Z:
            return 0

        fade_signal = -zscore
        if abs(rsi - 50.0) > 6.0:
            fade_signal += (50.0 - rsi) / 45.0

        strength = clamp((abs(zscore) - self.ENTRY_Z) / max(0.25, self.AGGRESSIVE_Z - self.ENTRY_Z), 0.0, 1.0)
        if phase == "aggressive_mr":
            strength = max(0.45, strength)

        if zscore * trend_score > self.TREND_ALLOW:
            strength *= max(0.15, 1.0 - self.TREND_PENALTY * min(1.0, abs(trend_score)))
        elif zscore * trend_score < -0.10:
            strength *= 1.0 + 0.15 * min(1.0, abs(trend_score))

        if fade_signal > 0:
            direction = 1
        elif fade_signal < 0:
            direction = -1
        else:
            direction = 0

        if direction == 0:
            return 0

        cap = self.target_cap(phase, zscore)
        return int(round(direction * cap * strength))

    def apply_inventory_policy(
        self,
        target_position: int,
        phase: str,
        zscore: float,
        trend_score: float,
    ) -> Tuple[int, bool, bool, float]:
        position = self.projected_position()
        mode = self.inventory_mode()
        block_buy = False
        block_sell = False
        flatten_bias = 0.0
        half_spread = max(1.0, float(self.spread) / 2.0)

        if mode == "neutral":
            return target_position, block_buy, block_sell, flatten_bias

        if mode == "lean":
            if position > 0 and target_position >= position:
                block_buy = True
            if position < 0 and target_position <= position:
                block_sell = True
            if position > 0 and zscore > 0 and trend_score > 0:
                target_position = min(target_position, max(0, int(round(0.60 * position))))
                flatten_bias += 0.20 * half_spread
            if position < 0 and zscore < 0 and trend_score < 0:
                target_position = max(target_position, min(0, int(round(0.60 * position))))
                flatten_bias -= 0.20 * half_spread
            return target_position, block_buy, block_sell, flatten_bias

        if mode == "unwind":
            if position > 0:
                block_buy = True
                target_position = min(target_position, int(self.UNWIND_TARGET))
                flatten_bias += 0.45 * half_spread
            else:
                block_sell = True
                target_position = max(target_position, -int(self.UNWIND_TARGET))
                flatten_bias -= 0.45 * half_spread
            return target_position, block_buy, block_sell, flatten_bias

        if mode == "emergency":
            if position > 0:
                block_buy = True
                target_position = min(target_position, 0)
                flatten_bias += 0.85 * half_spread
            else:
                block_sell = True
                target_position = max(target_position, 0)
                flatten_bias -= 0.85 * half_spread
            return target_position, block_buy, block_sell, flatten_bias

        # hard
        if position > 0:
            block_buy = True
            target_position = 0
            flatten_bias += 1.20 * half_spread
        else:
            block_sell = True
            target_position = 0
            flatten_bias -= 1.20 * half_spread
        return target_position, block_buy, block_sell, flatten_bias

    def fair_value(
        self,
        phase: str,
        long_mean: float,
        short_mean: float,
        zscore: float,
        trend_score: float,
        target_position: int,
    ) -> float:
        if phase == "bootstrap":
            fair = self.BOOTSTRAP_MID_WEIGHT * float(self.mid) + self.BOOTSTRAP_MICRO_WEIGHT * float(self.micro)
        elif phase == "aggressive_mr":
            fair = (
                self.AGGR_MID_WEIGHT * float(self.mid)
                + self.AGGR_MICRO_WEIGHT * float(self.micro)
                + self.AGGR_LONG_WEIGHT * long_mean
                + self.AGGR_SHORT_WEIGHT * short_mean
            )
        else:
            fair = (
                self.MR_MID_WEIGHT * float(self.mid)
                + self.MR_MICRO_WEIGHT * float(self.micro)
                + self.MR_LONG_WEIGHT * long_mean
                + self.MR_SHORT_WEIGHT * short_mean
            )

        if zscore * trend_score < -0.05:
            fair += self.MICRO_ALIGN_BONUS * max(1.0, float(self.spread) / 2.0) * math.copysign(1.0, -zscore)

        fair -= (self.projected_position() - target_position) * self.INVENTORY_SKEW
        return fair

    def quote_edge(self, phase: str, mode: str, trend_score: float) -> float:
        if phase == "bootstrap":
            edge = self.BOOTSTRAP_QUOTE_EDGE
        elif phase == "aggressive_mr":
            edge = self.AGGR_QUOTE_EDGE
        else:
            edge = self.BASE_QUOTE_EDGE

        edge += 0.10 * max(0.0, float(self.spread) - 6.0)
        if mode == "lean":
            edge += 0.20
        elif mode == "unwind":
            edge += 0.50
        elif mode in {"emergency", "hard"}:
            edge += 0.90
        if abs(trend_score) > 0.9:
            edge += 0.20
        return min(9.0, max(1.2, edge))

    def take_edge(self, phase: str, zscore: float, trend_score: float) -> float:
        edge = self.AGGR_TAKE_EDGE if phase == "aggressive_mr" else self.BASE_TAKE_EDGE
        if zscore * trend_score > self.TREND_ALLOW:
            edge += 0.20
        elif zscore * trend_score < -0.08:
            edge -= 0.10
        if float(self.spread) >= self.TOXIC_SPREAD:
            edge += 0.15
        return max(0.35, edge)

    def passive_size(self, phase: str, mode: str, target_position: int) -> int:
        if phase == "bootstrap":
            size = int(self.BOOTSTRAP_PASSIVE_SIZE)
        elif phase == "aggressive_mr":
            size = int(self.AGGR_PASSIVE_SIZE)
        else:
            size = int(self.BASE_PASSIVE_SIZE)

        if mode == "lean":
            size = max(1, int(round(0.75 * size)))
        elif mode == "unwind":
            size = max(1, int(round(0.55 * size)))
        elif mode in {"emergency", "hard"}:
            size = 1

        if phase == "bootstrap":
            size = max(1, min(size, 3))

        desired = abs(target_position - self.projected_position())
        if desired > 0:
            size = min(size, max(1, desired))
        return max(1, size)

    def max_take_size(self, phase: str, mode: str) -> int:
        if phase == "bootstrap":
            size = int(self.BOOTSTRAP_MAX_TAKE)
        elif phase == "aggressive_mr":
            size = int(self.AGGR_MAX_TAKE)
        else:
            size = int(self.BASE_MAX_TAKE)

        if mode == "lean":
            size = max(1, int(round(0.80 * size)))
        elif mode == "unwind":
            size = max(1, int(round(0.60 * size)))
        elif mode in {"emergency", "hard"}:
            size = max(1, int(round(0.40 * size)))
        return size

    def one_sided_quotes(
        self,
        phase: str,
        target_position: int,
        fair: float,
        qedge: float,
        mode: str,
    ) -> Tuple[Optional[int], Optional[int]]:
        position = self.projected_position()
        buy_quote = math.floor(fair - qedge)
        sell_quote = math.ceil(fair + qedge)
        buy_quote, sell_quote = self.clamp_inside_spread(buy_quote, sell_quote)

        if phase == "bootstrap":
            return buy_quote, sell_quote

        if mode in {"unwind", "emergency", "hard"}:
            if position > 0:
                return None, sell_quote
            if position < 0:
                return buy_quote, None

        if target_position > position:
            if phase == "aggressive_mr" and position <= 0:
                return buy_quote, None
            if position > 0:
                return buy_quote, sell_quote
            return buy_quote, None

        if target_position < position:
            if phase == "aggressive_mr" and position >= 0:
                return None, sell_quote
            if position < 0:
                return buy_quote, sell_quote
            return None, sell_quote

        return buy_quote, sell_quote

    def take_orders(
        self,
        fair: float,
        phase: str,
        target_position: int,
        zscore: float,
        trend_score: float,
        block_buy: bool,
        block_sell: bool,
        mode: str,
    ) -> None:
        tedge = self.take_edge(phase, zscore, trend_score)
        max_take = self.max_take_size(phase, mode)
        position = self.projected_position()
        buy_desired = max(0, target_position - position)
        sell_desired = max(0, position - target_position)

        if not block_buy and buy_desired > 0 and int(self.best_ask) <= fair - tedge and self.buy_capacity > 0:
            qty = min(self.best_ask_volume, self.buy_capacity, max_take, buy_desired)
            if qty > 0:
                self.add_buy(int(self.best_ask), qty)

        position = self.projected_position()
        sell_desired = max(0, position - target_position)
        if not block_sell and sell_desired > 0 and int(self.best_bid) >= fair + tedge and self.sell_capacity > 0:
            qty = min(self.best_bid_volume, self.sell_capacity, max_take, sell_desired)
            if qty > 0:
                self.add_sell(int(self.best_bid), qty)

        # inventory-reducing opportunistic take
        position = self.projected_position()
        if position > 0 and self.sell_capacity > 0 and int(self.best_bid) >= math.ceil(fair):
            qty = min(position, self.best_bid_volume, max(1, max_take // 2))
            self.add_sell(int(self.best_bid), qty)
        elif position < 0 and self.buy_capacity > 0 and int(self.best_ask) <= math.floor(fair):
            qty = min(abs(position), self.best_ask_volume, max(1, max_take // 2))
            self.add_buy(int(self.best_ask), qty)

    def place_passive(
        self,
        buy_quote: Optional[int],
        sell_quote: Optional[int],
        phase: str,
        mode: str,
        target_position: int,
        block_buy: bool,
        block_sell: bool,
    ) -> None:
        position = self.projected_position()
        size = self.passive_size(phase, mode, target_position)
        buy_desired = max(0, target_position - position)
        sell_desired = max(0, position - target_position)

        if buy_quote is not None and not block_buy and self.buy_capacity > 0:
            if phase == "bootstrap":
                if position < int(0.35 * self.soft_limit):
                    self.add_buy(buy_quote, min(size, self.buy_capacity))
            elif buy_desired > 0:
                self.add_buy(buy_quote, min(size, self.buy_capacity, buy_desired))
            elif mode in {"neutral", "lean"} and position < 0:
                self.add_buy(buy_quote, min(size, self.buy_capacity, abs(position)))

        position = self.projected_position()
        sell_desired = max(0, position - target_position)
        if sell_quote is not None and not block_sell and self.sell_capacity > 0:
            if phase == "bootstrap":
                if position > -int(0.35 * self.soft_limit):
                    self.add_sell(sell_quote, min(size, self.sell_capacity))
            elif sell_desired > 0:
                self.add_sell(sell_quote, min(size, self.sell_capacity, sell_desired))
            elif mode in {"neutral", "lean"} and position > 0:
                self.add_sell(sell_quote, min(size, self.sell_capacity, position))

    def run(self) -> List[Order]:
        if not self.has_book():
            return self.orders

        long_mean, short_mean, zscore, rsi, trend_score = self.market_stats()
        vol = self.volatility()
        phase = self.classify_phase(zscore, trend_score, vol)
        mode = self.inventory_mode()
        target_position = self.target_position(phase, zscore, rsi, trend_score)
        target_position, block_buy, block_sell, flatten_bias = self.apply_inventory_policy(
            target_position, phase, zscore, trend_score
        )
        fair = self.fair_value(phase, long_mean, short_mean, zscore, trend_score, target_position) + flatten_bias
        qedge = self.quote_edge(phase, mode, trend_score)
        buy_quote, sell_quote = self.one_sided_quotes(phase, target_position, fair, qedge, mode)
        self.take_orders(fair, phase, target_position, zscore, trend_score, block_buy, block_sell, mode)
        self.place_passive(buy_quote, sell_quote, phase, mode, target_position, block_buy, block_sell)
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
                    cleaned[product] = [float(value) for value in values[-BaseProductTrader.HISTORY_LENGTH:]]

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
