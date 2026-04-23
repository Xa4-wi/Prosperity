from __future__ import annotations

from dataclasses import asdict
from typing import Any, Optional

from .signal_state import ProductRuntimeConfig, ProductSignalState, SignalState


class OliviaRuntimeDetector:
    def __init__(self, configs: dict[str, ProductRuntimeConfig]) -> None:
        self.configs = configs
        self.states = {
            product: ProductSignalState(product=product)
            for product in configs
        }

    def get_state(self, product: str) -> ProductSignalState:
        if product not in self.states:
            self.states[product] = ProductSignalState(product=product)
        return self.states[product]

    def reset_day(self, product: str) -> None:
        self.get_state(product).reset_day()

    def _infer_side(
        self,
        price: float,
        prev_best_bid: Optional[float],
        prev_best_ask: Optional[float],
        prev_mid: Optional[float],
        tolerance: float,
    ) -> str:
        if prev_best_ask is not None and price >= prev_best_ask - tolerance:
            return "BUY"
        if prev_best_bid is not None and price <= prev_best_bid + tolerance:
            return "SELL"
        if prev_mid is not None:
            if price > prev_mid:
                return "BUY"
            if price < prev_mid:
                return "SELL"
        return "UNKNOWN"

    def _update_state_from_confidence(self, state: ProductSignalState, entry_conf: float, exit_conf: float) -> None:
        if state.signal > 0:
            if state.confidence >= entry_conf:
                state.signal_state = SignalState.CONFIRMED_BUY
            elif state.confidence >= exit_conf:
                state.signal_state = SignalState.SUSPECT_BUY
            elif state.invalidations > 0:
                state.signal_state = SignalState.INVALIDATED
            else:
                state.signal_state = SignalState.NO_SIGNAL
        elif state.signal < 0:
            if state.confidence >= entry_conf:
                state.signal_state = SignalState.CONFIRMED_SELL
            elif state.confidence >= exit_conf:
                state.signal_state = SignalState.SUSPECT_SELL
            elif state.invalidations > 0:
                state.signal_state = SignalState.INVALIDATED
            else:
                state.signal_state = SignalState.NO_SIGNAL
        else:
            state.signal_state = SignalState.INVALIDATED if state.invalidations > 0 and state.confidence > 0 else SignalState.NO_SIGNAL

    def on_trade(
        self,
        product: str,
        timestamp: int,
        price: float,
        quantity: int,
        *,
        buyer: str = "",
        seller: str = "",
        prev_best_bid: Optional[float] = None,
        prev_best_ask: Optional[float] = None,
        prev_mid: Optional[float] = None,
        trader_id_name: str = "Olivia",
    ) -> ProductSignalState:
        config = self.configs[product]
        state = self.get_state(product)

        if state.last_timestamp is not None and timestamp < state.last_timestamp:
            state.reset_day()

        if state.last_timestamp is not None:
            bars_elapsed = max(0, (timestamp - state.last_timestamp) // 100)
            state.bars_since_signal += bars_elapsed
        state.last_timestamp = timestamp

        if buyer == trader_id_name:
            state.direct_id_mode = True
            state.signal = 1
            state.confidence = 1.0
            state.last_extreme_side = 1
            state.last_extreme_price = price
            state.bars_since_signal = 0
            state.signal_state = SignalState.CONFIRMED_BUY
            state.confidence_history.append({"timestamp": timestamp, "confidence": state.confidence, "signal": state.signal_state.value})
            return state
        if seller == trader_id_name:
            state.direct_id_mode = True
            state.signal = -1
            state.confidence = 1.0
            state.last_extreme_side = -1
            state.last_extreme_price = price
            state.bars_since_signal = 0
            state.signal_state = SignalState.CONFIRMED_SELL
            state.confidence_history.append({"timestamp": timestamp, "confidence": state.confidence, "signal": state.signal_state.value})
            return state

        side = self._infer_side(price, prev_best_bid, prev_best_ask, prev_mid, config.side_tolerance)
        is_new_low = price < state.day_low_trade
        is_new_high = price > state.day_high_trade
        state.day_low_trade = min(state.day_low_trade, price)
        state.day_high_trade = max(state.day_high_trade, price)

        score = 0.0
        if config.quantity_in_cluster(quantity):
            score += 1.0
        if is_new_low and side == "BUY":
            score += 2.0
        if is_new_high and side == "SELL":
            score += 2.0
        if (state.signal > 0 and side == "BUY") or (state.signal < 0 and side == "SELL"):
            score += 0.5
        if prev_mid is not None:
            if is_new_low and price <= prev_mid:
                score += 0.5
            if is_new_high and price >= prev_mid:
                score += 0.5

        contradictory = False
        if state.signal > 0 and is_new_high and side == "SELL" and config.quantity_in_cluster(quantity):
            contradictory = True
        if state.signal < 0 and is_new_low and side == "BUY" and config.quantity_in_cluster(quantity):
            contradictory = True

        if contradictory:
            state.confidence = max(0.0, state.confidence - 2.0)
            state.invalidations += 1
            if state.confidence < config.exit_confidence:
                state.signal = 0
        else:
            state.confidence = 0.7 * state.confidence + 0.3 * score
            if is_new_low and side == "BUY" and config.quantity_in_cluster(quantity):
                state.signal = 1
                state.last_extreme_side = 1
                state.last_extreme_price = price
                state.bars_since_signal = 0
            elif is_new_high and side == "SELL" and config.quantity_in_cluster(quantity):
                state.signal = -1
                state.last_extreme_side = -1
                state.last_extreme_price = price
                state.bars_since_signal = 0

        if state.bars_since_signal > config.max_persistence:
            state.confidence *= 0.85
            if state.confidence < config.exit_confidence:
                state.signal = 0

        self._update_state_from_confidence(state, config.entry_confidence, config.exit_confidence)
        state.confidence_history.append({"timestamp": timestamp, "confidence": round(state.confidence, 4), "signal": state.signal_state.value})
        return state

    def snapshot(self, product: str) -> dict[str, Any]:
        state = self.get_state(product)
        payload = asdict(state)
        payload["signal_state"] = state.signal_state.value
        config = self.configs.get(product)
        if config is not None:
            payload["mode"] = config.mode.value
            payload["lot_cluster"] = {
                "center": config.lot_cluster,
                "min": config.lot_cluster_min,
                "max": config.lot_cluster_max,
            }
        return payload
