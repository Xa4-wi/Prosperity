from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SignalState(str, Enum):
    NO_SIGNAL = "NO_SIGNAL"
    SUSPECT_BUY = "SUSPECT_BUY"
    CONFIRMED_BUY = "CONFIRMED_BUY"
    SUSPECT_SELL = "SUSPECT_SELL"
    CONFIRMED_SELL = "CONFIRMED_SELL"
    INVALIDATED = "INVALIDATED"


class UsageMode(str, Enum):
    FULL_FOLLOW = "FULL_FOLLOW"
    FOLLOW_AFTER_TRIGGER = "FOLLOW_AFTER_TRIGGER"
    BIAS_ONLY = "BIAS_ONLY"
    IGNORE = "IGNORE"


@dataclass
class ProductRuntimeConfig:
    product: str
    lot_cluster: int
    lot_cluster_min: int
    lot_cluster_max: int
    mode: UsageMode
    entry_confidence: float = 0.75
    exit_confidence: float = 0.35
    max_persistence: int = 600
    side_tolerance: float = 0.25
    basket_bias_weight: float = 0.0

    def quantity_in_cluster(self, quantity: int) -> bool:
        return self.lot_cluster_min <= int(quantity) <= self.lot_cluster_max


@dataclass
class ProductSignalState:
    product: str
    day_low_trade: float = float("inf")
    day_high_trade: float = float("-inf")
    signal: int = 0
    confidence: float = 0.0
    bars_since_signal: int = 0
    last_extreme_side: int = 0
    last_extreme_price: Optional[float] = None
    invalidations: int = 0
    signal_state: SignalState = SignalState.NO_SIGNAL
    last_timestamp: Optional[int] = None
    direct_id_mode: bool = False
    confidence_history: list[dict] = field(default_factory=list)

    def reset_day(self) -> None:
        self.day_low_trade = float("inf")
        self.day_high_trade = float("-inf")
        self.signal = 0
        self.confidence = 0.0
        self.bars_since_signal = 0
        self.last_extreme_side = 0
        self.last_extreme_price = None
        self.invalidations = 0
        self.signal_state = SignalState.NO_SIGNAL
        self.last_timestamp = None
        self.confidence_history.clear()
