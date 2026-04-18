from __future__ import annotations

import random
import statistics
from dataclasses import dataclass
from typing import Dict

from .artifacts import BookLevel, MarketStateRow, build_market_state


@dataclass(frozen=True)
class ProductAccessStats:
    size_samples: tuple[int, ...]
    level_offset_samples: tuple[int, ...]
    median_touch_depth: float
    median_spread: float


def build_access_stats(states: list[MarketStateRow]) -> Dict[str, ProductAccessStats]:
    grouped: dict[str, dict[str, list[float]]] = {}
    for state in states:
        bucket = grouped.setdefault(
            state.product,
            {"sizes": [], "offsets": [], "touch_depths": [], "spreads": []},
        )
        if state.spread > 0:
            bucket["spreads"].append(state.spread)
        if state.bid_levels:
            bucket["touch_depths"].append(state.bid_levels[0].volume)
        if state.ask_levels:
            bucket["touch_depths"].append(state.ask_levels[0].volume)
        for levels in (state.bid_levels, state.ask_levels):
            if not levels:
                continue
            touch_price = levels[0].price
            for level in levels:
                bucket["sizes"].append(level.volume)
            for level in levels[1:]:
                bucket["offsets"].append(abs(level.price - touch_price))

    stats: Dict[str, ProductAccessStats] = {}
    for product, values in grouped.items():
        size_samples = tuple(int(value) for value in values["sizes"]) or (8, 12, 16, 20)
        offset_samples = tuple(max(1, int(value)) for value in values["offsets"]) or (1, 2, 3)
        median_touch_depth = statistics.median(values["touch_depths"]) if values["touch_depths"] else 16.0
        median_spread = statistics.median(values["spreads"]) if values["spreads"] else 4.0
        stats[product] = ProductAccessStats(
            size_samples=size_samples,
            level_offset_samples=offset_samples,
            median_touch_depth=float(median_touch_depth),
            median_spread=float(median_spread),
        )
    return stats


def _sample_size(stats: ProductAccessStats, rng: random.Random) -> int:
    return max(1, int(rng.choice(stats.size_samples)))


def _sample_offset(stats: ProductAccessStats, rng: random.Random) -> int:
    return max(1, int(rng.choice(stats.level_offset_samples)))


def _add_buy_side_level(snapshot: MarketStateRow, stats: ProductAccessStats, rng: random.Random) -> BookLevel | None:
    if snapshot.bid_levels:
        same_touch = snapshot.bid_levels[0].price
    elif snapshot.ask_levels:
        same_touch = snapshot.ask_levels[0].price - max(2, int(round(stats.median_spread)))
    else:
        return None
    opposite_touch = snapshot.ask_levels[0].price if snapshot.ask_levels else same_touch + max(2, int(round(stats.median_spread)))
    spread = max(1, opposite_touch - same_touch)
    improve = spread > 2 and rng.random() < 0.65
    if improve:
        price = min(opposite_touch - 1, same_touch + 1)
    else:
        price = same_touch - _sample_offset(stats, rng)
    if price <= 0:
        return None
    return BookLevel(price=price, volume=_sample_size(stats, rng), origin="access")


def _add_sell_side_level(snapshot: MarketStateRow, stats: ProductAccessStats, rng: random.Random) -> BookLevel | None:
    if snapshot.ask_levels:
        same_touch = snapshot.ask_levels[0].price
    elif snapshot.bid_levels:
        same_touch = snapshot.bid_levels[0].price + max(2, int(round(stats.median_spread)))
    else:
        return None
    opposite_touch = snapshot.bid_levels[0].price if snapshot.bid_levels else same_touch - max(2, int(round(stats.median_spread)))
    spread = max(1, same_touch - opposite_touch)
    improve = spread > 2 and rng.random() < 0.65
    if improve:
        price = max(opposite_touch + 1, same_touch - 1)
    else:
        price = same_touch + _sample_offset(stats, rng)
    return BookLevel(price=price, volume=_sample_size(stats, rng), origin="access")


def augment_snapshot_with_access(
    snapshot: MarketStateRow,
    stats_by_product: Dict[str, ProductAccessStats],
    rng: random.Random,
    extra_quote_ratio: float = 0.25,
) -> MarketStateRow:
    stats = stats_by_product.get(snapshot.product)
    if stats is None:
        return snapshot

    bid_levels = list(snapshot.bid_levels)
    ask_levels = list(snapshot.ask_levels)
    added_levels = 0

    base_prob = min(0.9, max(0.05, extra_quote_ratio))
    if snapshot.spread >= max(2.0, stats.median_spread):
        base_prob += 0.15
    if snapshot.top_depth <= stats.median_touch_depth:
        base_prob += 0.10

    if rng.random() < min(0.9, base_prob):
        level = _add_buy_side_level(snapshot, stats, rng)
        if level is not None:
            bid_levels.append(level)
            added_levels += 1

    if rng.random() < min(0.9, base_prob):
        level = _add_sell_side_level(snapshot, stats, rng)
        if level is not None:
            ask_levels.append(level)
            added_levels += 1

    if added_levels == 0:
        return snapshot

    return build_market_state(
        round_name=snapshot.round_name,
        day=snapshot.day,
        timestamp=snapshot.timestamp,
        product=snapshot.product,
        bid_levels=bid_levels,
        ask_levels=ask_levels,
        mid_price=None,
        profit_and_loss=snapshot.profit_and_loss,
        source_mode="access",
        access_added_levels=added_levels,
    )
