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
        self.spread = 0
        self.micro = 0.0
        self.imbalance = 0.0
        self.depth_micro = 0.0
        self.depth_imbalance = 0.0

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

        bid_weight = 0.0
        bid_price = 0.0
        ask_weight = 0.0
        ask_price = 0.0
        for index, (price, volume) in enumerate(self.buy_levels[:3]):
            weight = float(volume) / (index + 1.0)
            bid_weight += weight
            bid_price += weight * float(price)
        for index, (price, volume) in enumerate(self.sell_levels[:3]):
            weight = float(volume) / (index + 1.0)
            ask_weight += weight
            ask_price += weight * float(price)

        total_depth = bid_weight + ask_weight
        if total_depth > 0:
            bid_vwap = bid_price / max(1e-9, bid_weight)
            ask_vwap = ask_price / max(1e-9, ask_weight)
            self.depth_micro = (ask_vwap * bid_weight + bid_vwap * ask_weight) / total_depth
            self.depth_imbalance = (bid_weight - ask_weight) / total_depth
        else:
            self.depth_micro = self.mid
            self.depth_imbalance = 0.0

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
    BASE_QUOTE_SIZE = 10
    DEFAULT_EDGE = 7.0
    JOIN_EDGE = 2.0
    SOFT_LIMIT = 20
    TAKE_LEVELS = (
        (1.0, 6),
        (4.0, 12),
        (8.0, 20),
    )

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

    def take_size(self, edge: float) -> int:
        size = 0
        for distance, clip in self.TAKE_LEVELS:
            if edge >= distance:
                size = clip
        return size

    def take_orders(self, reservation: float) -> None:
        buy_edge = reservation - float(self.book.best_ask)
        buy_size = self.take_size(buy_edge)
        if buy_size > 0 and self.manager.buy_capacity > 0:
            if self.manager.projected_position() >= self.SOFT_LIMIT:
                buy_size = max(0, buy_size - 4)
            self.manager.add_buy(self.book.best_ask, min(self.book.best_ask_volume, buy_size))

        sell_edge = float(self.book.best_bid) - reservation
        sell_size = self.take_size(sell_edge)
        if sell_size > 0 and self.manager.sell_capacity > 0:
            if self.manager.projected_position() <= -self.SOFT_LIMIT:
                sell_size = max(0, sell_size - 4)
            self.manager.add_sell(self.book.best_bid, min(self.book.best_bid_volume, sell_size))

    def clear_inventory(self, reservation: float) -> None:
        position = self.manager.projected_position()
        if position > 0 and self.book.best_bid >= math.ceil(reservation):
            self.manager.add_sell(self.book.best_bid, min(position, self.book.best_bid_volume, self.BASE_QUOTE_SIZE))
        position = self.manager.projected_position()
        if position < 0 and self.book.best_ask <= math.floor(reservation):
            self.manager.add_buy(self.book.best_ask, min(abs(position), self.book.best_ask_volume, self.BASE_QUOTE_SIZE))

    def passive_quotes(self, reservation: float) -> Tuple[int, int]:
        buy_quote = int(round(reservation - self.DEFAULT_EDGE))
        sell_quote = int(round(reservation + self.DEFAULT_EDGE))

        for price, _volume in self.book.buy_levels[:2]:
            if price < reservation - self.DEFAULT_EDGE:
                buy_quote = price if reservation - price <= self.JOIN_EDGE else price + 1
                break

        for price, _volume in self.book.sell_levels[:2]:
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
        if buy_quote >= self.book.best_ask:
            buy_quote = self.book.best_bid
        if sell_quote <= self.book.best_bid:
            sell_quote = self.book.best_ask
        if buy_quote >= sell_quote:
            return self.book.best_bid, self.book.best_ask
        return buy_quote, sell_quote

    def passive_size(self, side: str) -> int:
        size = self.BASE_QUOTE_SIZE
        position = self.manager.projected_position()
        if side == "BUY":
            if position <= -self.SOFT_LIMIT:
                size += 4
            elif position >= self.SOFT_LIMIT:
                size = max(1, size - 6)
        else:
            if position >= self.SOFT_LIMIT:
                size += 4
            elif position <= -self.SOFT_LIMIT:
                size = max(1, size - 6)
        return size

    def run(self) -> List[Order]:
        if not self.book.valid:
            return []
        reservation = self.reservation()
        self.take_orders(reservation)
        self.clear_inventory(reservation)
        buy_quote, sell_quote = self.passive_quotes(self.reservation())
        if self.manager.buy_capacity > 0 and self.manager.projected_position() < self.SOFT_LIMIT + self.BASE_QUOTE_SIZE:
            self.manager.add_buy(buy_quote, self.passive_size("BUY"))
        if self.manager.sell_capacity > 0 and self.manager.projected_position() > -(self.SOFT_LIMIT + self.BASE_QUOTE_SIZE):
            self.manager.add_sell(sell_quote, self.passive_size("SELL"))
        return self.manager.orders


class PhysicsTomatoesBot:
    EQ_ALPHA = 0.05
    VEL_ALPHA = 0.32
    ACC_ALPHA = 0.36
    FLOW_ALPHA = 0.28
    PRESSURE_ALPHA = 0.24
    VOL_ALPHA = 0.20

    SPRING_K = 0.42
    DAMP_K = 0.58
    FLOW_K = 1.15
    PRESSURE_K = 0.65
    ACC_K = 0.25
    DRIVE_CAP = 3.2

    BASE_QUOTE_EDGE = 2.30
    BASE_TAKE_EDGE = 0.84
    PASSIVE_SIZE = 8
    MAX_TAKE_SIZE = 10
    SOFT_LIMIT = 26
    INVENTORY_SKEW = 0.045
    POSITION_BIAS_DIV = 14.0
    TREND_SIGNAL = 0.90
    STRONG_SIGNAL = 1.65
    TOXIC_SPREAD = 12
    TOXIC_VOL = 3.0

    def __init__(self, state: TradingState, memory: Dict[str, object]) -> None:
        self.state = state
        self.memory = memory
        self.book = Book(state.order_depths.get("TOMATOES"))
        self.manager = OrderManager(
            "TOMATOES",
            int(state.position.get("TOMATOES", 0)),
            POSITION_LIMITS["TOMATOES"],
        )
        self.product_state = self.load_state()

    def load_state(self) -> Dict[str, float]:
        raw = self.memory.get("tomatoes_physics", {})
        if not isinstance(raw, dict):
            raw = {}
        return {
            "initialized": 1.0 if raw.get("initialized") else 0.0,
            "rest_ema": float(raw.get("rest_ema", 0.0)),
            "vel_ema": float(raw.get("vel_ema", 0.0)),
            "acc_ema": float(raw.get("acc_ema", 0.0)),
            "flow_ema": float(raw.get("flow_ema", 0.0)),
            "pressure_ema": float(raw.get("pressure_ema", 0.0)),
            "vol_ema": float(raw.get("vol_ema", 1.5)),
            "last_mid": float(raw.get("last_mid", 0.0)),
        }

    def save_state(self) -> None:
        self.memory["tomatoes_physics"] = {
            "initialized": 1,
            "rest_ema": float(self.product_state["rest_ema"]),
            "vel_ema": float(self.product_state["vel_ema"]),
            "acc_ema": float(self.product_state["acc_ema"]),
            "flow_ema": float(self.product_state["flow_ema"]),
            "pressure_ema": float(self.product_state["pressure_ema"]),
            "vol_ema": float(self.product_state["vol_ema"]),
            "last_mid": float(self.product_state["last_mid"]),
        }

    def update_state(self) -> None:
        mid = self.book.mid
        half_spread = max(1.0, float(self.book.spread) / 2.0)
        equilibrium_input = 0.65 * mid + 0.35 * self.book.depth_micro
        flow_raw = (self.book.micro - mid) / half_spread + 0.90 * self.book.imbalance
        pressure_raw = 0.55 * self.book.depth_imbalance + 0.45 * ((self.book.depth_micro - mid) / half_spread)

        if self.product_state["initialized"] <= 0.0:
            self.product_state["initialized"] = 1.0
            self.product_state["rest_ema"] = equilibrium_input
            self.product_state["vel_ema"] = 0.0
            self.product_state["acc_ema"] = 0.0
            self.product_state["flow_ema"] = flow_raw
            self.product_state["pressure_ema"] = pressure_raw
            self.product_state["vol_ema"] = half_spread
            self.product_state["last_mid"] = mid
            return

        previous_vel = float(self.product_state["vel_ema"])
        delta_mid = mid - float(self.product_state["last_mid"])
        velocity = ema(previous_vel, delta_mid, self.VEL_ALPHA)
        acceleration = ema(float(self.product_state["acc_ema"]), velocity - previous_vel, self.ACC_ALPHA)
        self.product_state["rest_ema"] = ema(float(self.product_state["rest_ema"]), equilibrium_input, self.EQ_ALPHA)
        self.product_state["vel_ema"] = velocity
        self.product_state["acc_ema"] = acceleration
        self.product_state["flow_ema"] = ema(float(self.product_state["flow_ema"]), flow_raw, self.FLOW_ALPHA)
        self.product_state["pressure_ema"] = ema(float(self.product_state["pressure_ema"]), pressure_raw, self.PRESSURE_ALPHA)
        self.product_state["vol_ema"] = ema(float(self.product_state["vol_ema"]), abs(delta_mid), self.VOL_ALPHA)
        self.product_state["last_mid"] = mid

    def physics_signal(self) -> Dict[str, float]:
        half_spread = max(1.0, float(self.book.spread) / 2.0)
        displacement = (self.book.mid - float(self.product_state["rest_ema"])) / half_spread
        velocity = float(self.product_state["vel_ema"]) / half_spread
        acceleration = float(self.product_state["acc_ema"]) / half_spread
        flow = float(self.product_state["flow_ema"])
        pressure = float(self.product_state["pressure_ema"])

        spring = -self.SPRING_K * displacement
        damping = -self.DAMP_K * velocity
        driving = self.FLOW_K * flow + self.PRESSURE_K * pressure + self.ACC_K * acceleration
        net = clamp(spring + damping + driving, -self.DRIVE_CAP, self.DRIVE_CAP)
        energy = 0.5 * self.SPRING_K * displacement * displacement + 0.5 * velocity * velocity
        return {
            "displacement": displacement,
            "velocity": velocity,
            "acceleration": acceleration,
            "flow": flow,
            "pressure": pressure,
            "spring": spring,
            "damping": damping,
            "driving": driving,
            "net": net,
            "energy": energy,
        }

    def classify_regime(self, signal: Dict[str, float]) -> str:
        if self.book.spread >= self.TOXIC_SPREAD or float(self.product_state["vol_ema"]) >= self.TOXIC_VOL:
            return "toxic"
        if (
            signal["net"] >= self.STRONG_SIGNAL
            and signal["driving"] > 0.40
            and signal["velocity"] > -0.10
        ):
            return "strong_up"
        if (
            signal["net"] <= -self.STRONG_SIGNAL
            and signal["driving"] < -0.40
            and signal["velocity"] < 0.10
        ):
            return "strong_down"
        if signal["net"] >= self.TREND_SIGNAL and signal["driving"] > 0.15:
            return "trend_up"
        if signal["net"] <= -self.TREND_SIGNAL and signal["driving"] < -0.15:
            return "trend_down"
        return "range"

    def target_position(self, signal: Dict[str, float], regime: str) -> int:
        conviction = clamp(abs(signal["net"]) / (1.0 + 0.25 * abs(signal["velocity"])), 0.0, 1.0)
        if regime == "strong_up":
            return int(round((self.SOFT_LIMIT + 10) * conviction))
        if regime == "strong_down":
            return -int(round((self.SOFT_LIMIT + 10) * conviction))
        if regime == "trend_up":
            return int(round((self.SOFT_LIMIT + 4) * conviction))
        if regime == "trend_down":
            return -int(round((self.SOFT_LIMIT + 4) * conviction))
        if regime == "toxic":
            return 0
        return int(round(clamp(signal["spring"] * 10.0, -12.0, 12.0)))

    def fair_value(self, signal: Dict[str, float], regime: str, target: int) -> float:
        half_spread = max(1.0, float(self.book.spread) / 2.0)
        position_bias = (target - self.manager.projected_position()) / self.POSITION_BIAS_DIV
        fair = self.book.mid + half_spread * signal["net"] + half_spread * 0.35 * signal["velocity"] + position_bias
        if regime == "range":
            fair += half_spread * 0.25 * signal["spring"]
        else:
            fair += half_spread * 0.18 * signal["driving"]
        return fair

    def reservation(self, fair: float, target: int) -> float:
        pressure = self.manager.projected_position() - target
        return fair - pressure * self.INVENTORY_SKEW

    def desired_buy_qty(self, target: int) -> int:
        return max(0, target - self.manager.projected_position())

    def desired_sell_qty(self, target: int) -> int:
        return max(0, self.manager.projected_position() - target)

    def take_threshold(self, side: str, regime: str, signal: Dict[str, float], target: int) -> float:
        threshold = self.BASE_TAKE_EDGE + 0.08 * min(3.0, float(self.product_state["vol_ema"]))
        position = self.manager.projected_position()
        aligned = (side == "BUY" and regime in {"trend_up", "strong_up"}) or (side == "SELL" and regime in {"trend_down", "strong_down"})
        if aligned:
            threshold -= 0.28 if regime.startswith("trend") else 0.40
        elif regime in {"trend_up", "strong_up", "trend_down", "strong_down"}:
            threshold += 0.55
        if side == "BUY" and position < target:
            threshold -= 0.10
        if side == "SELL" and position > target:
            threshold -= 0.10
        if regime == "range":
            if side == "BUY" and signal["spring"] > 0:
                threshold -= 0.08
            if side == "SELL" and signal["spring"] < 0:
                threshold -= 0.08
        if regime == "toxic":
            threshold += 0.70
        return max(0.25, threshold)

    def take_size(self, side: str, regime: str, target: int) -> int:
        desired = abs(target - self.manager.projected_position())
        size = min(self.MAX_TAKE_SIZE, max(2, desired))
        if regime in {"strong_up", "strong_down"}:
            size += 2
        if side == "BUY" and target < self.manager.projected_position():
            size = max(2, size - 3)
        if side == "SELL" and target > self.manager.projected_position():
            size = max(2, size - 3)
        return min(self.MAX_TAKE_SIZE, size)

    def take_orders(self, reservation: float, regime: str, signal: Dict[str, float], target: int) -> None:
        buy_threshold = self.take_threshold("BUY", regime, signal, target)
        sell_threshold = self.take_threshold("SELL", regime, signal, target)

        for price, volume in self.book.sell_levels[:2]:
            if self.manager.buy_capacity <= 0:
                break
            edge = reservation - float(price)
            if edge < buy_threshold:
                break
            size = min(volume, self.manager.buy_capacity, self.take_size("BUY", regime, target))
            if regime != "range":
                desired = self.desired_buy_qty(target)
                if desired <= 0:
                    continue
                size = min(size, desired)
            if size > 0:
                self.manager.add_buy(price, size)

        for price, volume in self.book.buy_levels[:2]:
            if self.manager.sell_capacity <= 0:
                break
            edge = float(price) - reservation
            if edge < sell_threshold:
                break
            size = min(volume, self.manager.sell_capacity, self.take_size("SELL", regime, target))
            if regime != "range":
                desired = self.desired_sell_qty(target)
                if desired <= 0:
                    continue
                size = min(size, desired)
            if size > 0:
                self.manager.add_sell(price, size)

    def quote_edge(self, side: str, regime: str, target: int) -> float:
        edge = self.BASE_QUOTE_EDGE + 0.16 * min(4.0, float(self.product_state["vol_ema"]))
        pressure = self.manager.projected_position() - target
        if regime == "range":
            edge -= 0.18
        elif regime in {"strong_up", "strong_down"}:
            edge += 0.12
        elif regime == "toxic":
            edge += 0.90
        if side == "BUY":
            if pressure > 0:
                edge += 0.75 * clamp(pressure / self.SOFT_LIMIT, 0.0, 1.0)
            elif pressure < 0:
                edge -= 0.18 * clamp(abs(pressure) / self.SOFT_LIMIT, 0.0, 1.0)
        else:
            if pressure < 0:
                edge += 0.75 * clamp(abs(pressure) / self.SOFT_LIMIT, 0.0, 1.0)
            elif pressure > 0:
                edge -= 0.18 * clamp(pressure / self.SOFT_LIMIT, 0.0, 1.0)
        return max(1.2, edge)

    def passive_quotes(self, reservation: float, regime: str, target: int) -> Tuple[int, int]:
        buy_quote = math.floor(reservation - self.quote_edge("BUY", regime, target))
        sell_quote = math.ceil(reservation + self.quote_edge("SELL", regime, target))
        if regime in {"trend_up", "strong_up"} and self.manager.projected_position() < target:
            buy_quote = max(buy_quote, self.book.best_bid + 1)
        if regime in {"trend_down", "strong_down"} and self.manager.projected_position() > target:
            sell_quote = min(sell_quote, self.book.best_ask - 1)
        buy_quote = max(buy_quote, self.book.best_bid)
        sell_quote = min(sell_quote, self.book.best_ask)
        if buy_quote >= self.book.best_ask:
            buy_quote = self.book.best_bid
        if sell_quote <= self.book.best_bid:
            sell_quote = self.book.best_ask
        if buy_quote >= sell_quote:
            return self.book.best_bid, self.book.best_ask
        return buy_quote, sell_quote

    def passive_size(self, side: str, regime: str, target: int) -> int:
        size = self.PASSIVE_SIZE
        pressure = self.manager.projected_position() - target
        if regime == "range":
            size += 1
        elif regime == "toxic":
            size = max(2, size - 3)
        if side == "BUY":
            if pressure < 0:
                size += 2
            elif pressure > 0:
                size = max(2, size - 3)
        else:
            if pressure > 0:
                size += 2
            elif pressure < 0:
                size = max(2, size - 3)
        return size

    def allow_passive(self, side: str, regime: str) -> bool:
        position = self.manager.projected_position()
        if regime == "toxic" and abs(position) <= 4:
            return False
        if side == "BUY" and position >= POSITION_LIMITS["TOMATOES"]:
            return False
        if side == "SELL" and position <= -POSITION_LIMITS["TOMATOES"]:
            return False
        return True

    def run(self) -> Tuple[List[Order], Dict[str, object]]:
        if not self.book.valid:
            self.save_state()
            return [], self.memory

        self.update_state()
        signal = self.physics_signal()
        regime = self.classify_regime(signal)
        target = self.target_position(signal, regime)
        fair = self.fair_value(signal, regime, target)
        reservation = self.reservation(fair, target)

        self.take_orders(reservation, regime, signal, target)
        reservation = self.reservation(fair, target)
        buy_quote, sell_quote = self.passive_quotes(reservation, regime, target)

        if self.allow_passive("BUY", regime) and self.manager.buy_capacity > 0:
            size = min(self.passive_size("BUY", regime, target), self.manager.buy_capacity)
            if regime != "range":
                desired = self.desired_buy_qty(target)
                if desired <= 0:
                    size = 0
                else:
                    size = min(size, desired)
            if size > 0:
                self.manager.add_buy(buy_quote, size)

        if self.allow_passive("SELL", regime) and self.manager.sell_capacity > 0:
            size = min(self.passive_size("SELL", regime, target), self.manager.sell_capacity)
            if regime != "range":
                desired = self.desired_sell_qty(target)
                if desired <= 0:
                    size = 0
                else:
                    size = min(size, desired)
            if size > 0:
                self.manager.add_sell(sell_quote, size)

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

        result["EMERALDS"] = EmeraldsBot(state).run()
        tomato_orders, updated_memory = PhysicsTomatoesBot(state, memory).run()
        result["TOMATOES"] = tomato_orders

        for product in state.order_depths:
            if product not in result:
                result[product] = []

        return result, 0, self.dump_memory(updated_memory)
