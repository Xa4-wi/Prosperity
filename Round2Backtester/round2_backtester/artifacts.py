from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple


@dataclass(frozen=True)
class BookLevel:
    price: int
    volume: int
    origin: str = "public"


def _merge_origin(existing: str, incoming: str) -> str:
    if existing == incoming:
        return existing
    if existing == "mixed" or incoming == "mixed":
        return "mixed"
    return "mixed"


def normalize_levels(levels: Iterable[BookLevel], reverse: bool) -> Tuple[BookLevel, ...]:
    aggregated: Dict[int, tuple[int, str]] = {}
    for level in levels:
        if level.volume <= 0:
            continue
        previous = aggregated.get(level.price)
        if previous is None:
            aggregated[level.price] = (int(level.volume), level.origin)
            continue
        aggregated[level.price] = (previous[0] + int(level.volume), _merge_origin(previous[1], level.origin))
    ordered = sorted(aggregated.items(), key=lambda item: item[0], reverse=reverse)
    return tuple(BookLevel(price=price, volume=volume, origin=origin) for price, (volume, origin) in ordered)


def compute_book_features(
    bid_levels: Tuple[BookLevel, ...],
    ask_levels: Tuple[BookLevel, ...],
    fallback_mid_price: float | None = None,
) -> tuple[float, float, int, float, float]:
    best_bid = bid_levels[0].price if bid_levels else None
    best_ask = ask_levels[0].price if ask_levels else None
    top_depth = (bid_levels[0].volume if bid_levels else 0) + (ask_levels[0].volume if ask_levels else 0)

    if best_bid is not None and best_ask is not None and best_bid < best_ask:
        mid_price = (best_bid + best_ask) / 2.0
        spread = float(best_ask - best_bid)
        if top_depth > 0:
            microprice = (best_ask * bid_levels[0].volume + best_bid * ask_levels[0].volume) / top_depth
            imbalance = (bid_levels[0].volume - ask_levels[0].volume) / top_depth
        else:
            microprice = mid_price
            imbalance = 0.0
        return mid_price, spread, top_depth, microprice, imbalance

    if fallback_mid_price is not None:
        mid_price = float(fallback_mid_price)
    elif best_bid is not None:
        mid_price = float(best_bid)
    elif best_ask is not None:
        mid_price = float(best_ask)
    else:
        mid_price = 0.0
    return mid_price, 0.0, top_depth, mid_price, 0.0


@dataclass(frozen=True)
class MarketStateRow:
    round_name: str
    day: int
    timestamp: int
    abs_timestamp: int
    product: str
    bid_levels: Tuple[BookLevel, ...]
    ask_levels: Tuple[BookLevel, ...]
    mid_price: float
    spread: float
    top_depth: int
    microprice: float
    imbalance: float
    profit_and_loss: float | None = None
    source_mode: str = "public"
    access_added_levels: int = 0


def build_market_state(
    *,
    round_name: str,
    day: int,
    timestamp: int,
    product: str,
    bid_levels: Iterable[BookLevel],
    ask_levels: Iterable[BookLevel],
    mid_price: float | None = None,
    profit_and_loss: float | None = None,
    source_mode: str = "public",
    access_added_levels: int = 0,
) -> MarketStateRow:
    normalized_bids = normalize_levels(bid_levels, reverse=True)
    normalized_asks = normalize_levels(ask_levels, reverse=False)
    computed_mid, spread, top_depth, microprice, imbalance = compute_book_features(
        normalized_bids,
        normalized_asks,
        fallback_mid_price=mid_price,
    )
    return MarketStateRow(
        round_name=round_name,
        day=day,
        timestamp=timestamp,
        abs_timestamp=day * 1_000_000 + timestamp,
        product=product,
        bid_levels=normalized_bids,
        ask_levels=normalized_asks,
        mid_price=float(mid_price if mid_price is not None else computed_mid),
        spread=spread,
        top_depth=top_depth,
        microprice=microprice,
        imbalance=imbalance,
        profit_and_loss=profit_and_loss,
        source_mode=source_mode,
        access_added_levels=access_added_levels,
    )


@dataclass(frozen=True)
class MarketTradeRow:
    round_name: str
    day: int
    timestamp: int
    symbol: str
    trade_index: int
    buyer: str | None
    seller: str | None
    price: float
    quantity: int
    currency: str = "XIRECS"


@dataclass(frozen=True)
class GraphPoint:
    timestamp: int
    value: float


@dataclass(frozen=True)
class RunSummaryRecord:
    run_id: str
    source_file: str
    round_name: str
    total_profit: float | None
    final_positions: Dict[str, int]
    graph_points: Tuple[GraphPoint, ...]
    notes: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RunExecutionRecord:
    run_id: str
    timestamp: int
    trade_index: int
    symbol: str
    side: str | None
    price: float
    quantity: int
    buyer: str | None = None
    seller: str | None = None


@dataclass(frozen=True)
class RunSnapshotRecord:
    run_id: str
    day: int
    timestamp: int
    product: str
    market_state: MarketStateRow
    product_pnl: float | None = None
    internal_log: str | None = None


@dataclass
class ParsedArtifact:
    kind: str
    source_path: Path
    metadata: Dict[str, Any] = field(default_factory=dict)
    market_states: list[MarketStateRow] = field(default_factory=list)
    market_trades: list[MarketTradeRow] = field(default_factory=list)
    run_summaries: list[RunSummaryRecord] = field(default_factory=list)
    run_executions: list[RunExecutionRecord] = field(default_factory=list)
    run_snapshots: list[RunSnapshotRecord] = field(default_factory=list)

    def counts(self) -> Dict[str, int]:
        return {
            "market_states": len(self.market_states),
            "market_trades": len(self.market_trades),
            "run_summaries": len(self.run_summaries),
            "run_executions": len(self.run_executions),
            "run_snapshots": len(self.run_snapshots),
        }
