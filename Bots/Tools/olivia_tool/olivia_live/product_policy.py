from __future__ import annotations

from dataclasses import dataclass

from .signal_state import ProductRuntimeConfig, ProductSignalState, SignalState, UsageMode


@dataclass
class PolicyDecision:
    product: str
    mode: str
    direction: int
    confidence: float
    position_bias: float
    quote_bias: float
    aggression: str
    reason: str


def policy_from_state(config: ProductRuntimeConfig, state: ProductSignalState) -> PolicyDecision:
    direction = 0
    if state.signal_state in {SignalState.SUSPECT_BUY, SignalState.CONFIRMED_BUY}:
        direction = 1
    elif state.signal_state in {SignalState.SUSPECT_SELL, SignalState.CONFIRMED_SELL}:
        direction = -1

    if config.mode == UsageMode.IGNORE or direction == 0:
        return PolicyDecision(
            product=config.product,
            mode=config.mode.value,
            direction=0,
            confidence=state.confidence,
            position_bias=0.0,
            quote_bias=0.0,
            aggression="none",
            reason="No active insider-style signal for this product.",
        )

    if config.mode == UsageMode.BIAS_ONLY:
        return PolicyDecision(
            product=config.product,
            mode=config.mode.value,
            direction=direction,
            confidence=state.confidence,
            position_bias=direction * config.basket_bias_weight,
            quote_bias=direction * 0.15,
            aggression="light",
            reason="Bias-only mode: use the signal to tilt thresholds or basket bias, not replace baseline trading.",
        )

    if config.mode == UsageMode.FOLLOW_AFTER_TRIGGER:
        aggression = "moderate" if state.signal_state in {SignalState.CONFIRMED_BUY, SignalState.CONFIRMED_SELL} else "light"
        return PolicyDecision(
            product=config.product,
            mode=config.mode.value,
            direction=direction,
            confidence=state.confidence,
            position_bias=direction * min(1.0, state.confidence),
            quote_bias=direction * 0.25,
            aggression=aggression,
            reason="Follow-after-trigger mode: keep baseline logic until the signal is present, then trade in the signaled direction.",
        )

    return PolicyDecision(
        product=config.product,
        mode=config.mode.value,
        direction=direction,
        confidence=state.confidence,
        position_bias=direction * min(1.5, 0.5 + state.confidence),
        quote_bias=direction * 0.35,
        aggression="high" if state.signal_state in {SignalState.CONFIRMED_BUY, SignalState.CONFIRMED_SELL} else "moderate",
        reason="Full-follow mode: treat the signal as the dominant intraday regime for this product.",
    )
