from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

from .artifacts import BookLevel, MarketStateRow


@dataclass
class RestingOrder:
    product: str
    side: str
    price: int
    quantity: int
    submitted_day: int
    submitted_timestamp: int
    at_touch: bool
    improved_touch: bool


@dataclass
class Fill:
    day: int
    timestamp: int
    abs_timestamp: int
    step_index: int
    product: str
    side: str
    price: int
    quantity: int
    fill_type: str
    source_order_price: int
    book_origin: str
    replay_mode: str
    spread: float
    imbalance: float
    micro_gap: float
    access_added_levels: int


def _origin_for_price(levels: tuple[BookLevel, ...], price: int) -> str:
    origin = None
    for level in levels:
        if level.price != price:
            continue
        origin = level.origin if origin is None else ("mixed" if origin != level.origin else origin)
    return origin or "public"


def execute_crossing_order(order, snapshot: MarketStateRow, side: str, step_index: int, replay_mode: str) -> tuple[List[Fill], int]:
    remaining = abs(int(order.quantity))
    fills: List[Fill] = []
    levels = snapshot.ask_levels if side == "BUY" else snapshot.bid_levels

    for level in levels:
        if remaining <= 0:
            break
        if side == "BUY" and order.price < level.price:
            break
        if side == "SELL" and order.price > level.price:
            break
        fill_qty = min(remaining, level.volume)
        if fill_qty <= 0:
            continue
        fills.append(
            Fill(
                day=snapshot.day,
                timestamp=snapshot.timestamp,
                abs_timestamp=snapshot.abs_timestamp,
                step_index=step_index,
                product=snapshot.product,
                side=side,
                price=level.price,
                quantity=fill_qty,
                fill_type="aggressive_cross",
                source_order_price=int(order.price),
                book_origin=level.origin,
                replay_mode=replay_mode,
                spread=snapshot.spread,
                imbalance=snapshot.imbalance,
                micro_gap=snapshot.microprice - snapshot.mid_price,
                access_added_levels=snapshot.access_added_levels,
            )
        )
        remaining -= fill_qty
    return fills, remaining


def _pending_fill_quantity(order: RestingOrder, snapshot: MarketStateRow, market_trades: list) -> int:
    if order.side == "BUY":
        crossed_volume = sum(level.volume for level in snapshot.ask_levels if level.price <= order.price)
        tape_volume = sum(int(trade.quantity) for trade in market_trades if int(trade.price) <= order.price)
    else:
        crossed_volume = sum(level.volume for level in snapshot.bid_levels if level.price >= order.price)
        tape_volume = sum(int(trade.quantity) for trade in market_trades if int(trade.price) >= order.price)
    return max(crossed_volume, tape_volume)


def _touch_join_fill_quantity(
    order: RestingOrder,
    snapshot: MarketStateRow,
    market_trades: list,
    rng: random.Random,
) -> int:
    same_side_levels = snapshot.bid_levels if order.side == "BUY" else snapshot.ask_levels
    touch_level = same_side_levels[0] if same_side_levels else None
    if touch_level is None:
        return 0
    is_joining_touch = order.price == touch_level.price or order.improved_touch
    if not is_joining_touch:
        return 0

    touch_volume = next((level.volume for level in same_side_levels if level.price == order.price), touch_level.volume)
    if order.side == "BUY":
        directional_tape = sum(int(trade.quantity) for trade in market_trades if float(trade.price) <= snapshot.mid_price)
    else:
        directional_tape = sum(int(trade.quantity) for trade in market_trades if float(trade.price) >= snapshot.mid_price)

    pressure_ratio = directional_tape / max(1.0, touch_volume + order.quantity)
    probability = 0.12 + 0.55 * min(1.0, pressure_ratio)
    if order.improved_touch:
        probability += 0.18
    if snapshot.spread >= 12:
        probability += 0.07
    if rng.random() >= min(0.95, max(0.05, probability)):
        return 0

    candidate = max(1, int(round(max(order.quantity * 0.35, directional_tape * 0.5, touch_volume * 0.2))))
    return min(order.quantity, candidate)


def try_fill_pending_order(
    order: RestingOrder,
    snapshot: MarketStateRow,
    market_trades: list,
    queue_model: str,
    rng: random.Random,
    step_index: int,
    replay_mode: str,
) -> List[Fill]:
    fillable = min(order.quantity, _pending_fill_quantity(order, snapshot, market_trades))
    fill_type = "passive_resting_fill"
    if fillable <= 0 and queue_model == "touch_join":
        fillable = _touch_join_fill_quantity(order, snapshot, market_trades, rng)
        fill_type = "passive_touch_join"
    if fillable <= 0:
        return []

    side_levels = snapshot.bid_levels if order.side == "BUY" else snapshot.ask_levels
    return [
        Fill(
            day=snapshot.day,
            timestamp=snapshot.timestamp,
            abs_timestamp=snapshot.abs_timestamp,
            step_index=step_index,
            product=snapshot.product,
            side=order.side,
            price=order.price,
            quantity=fillable,
            fill_type=fill_type,
            source_order_price=order.price,
            book_origin=_origin_for_price(side_levels, order.price),
            replay_mode=replay_mode,
            spread=snapshot.spread,
            imbalance=snapshot.imbalance,
            micro_gap=snapshot.microprice - snapshot.mid_price,
            access_added_levels=snapshot.access_added_levels,
        )
    ]


def apply_fills(fills: List[Fill], cash: Dict[str, float], position: Dict[str, int], TradeClass) -> Dict[str, List]:
    own_trades: Dict[str, List] = defaultdict(list)
    for fill in fills:
        signed_quantity = fill.quantity if fill.side == "BUY" else -fill.quantity
        position[fill.product] += signed_quantity
        cash[fill.product] -= signed_quantity * fill.price
        own_trades[fill.product].append(
            TradeClass(
                symbol=fill.product,
                price=int(fill.price),
                quantity=int(fill.quantity),
                buyer="SUBMISSION" if fill.side == "BUY" else None,
                seller="SUBMISSION" if fill.side == "SELL" else None,
                timestamp=int(fill.timestamp),
            )
        )
    return own_trades
