from __future__ import annotations

import csv
import importlib.util
import io
import json
import math
import random
import re
import statistics
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[3]
BOTS_ROOT = REPO_ROOT / "Bots"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BOTS_ROOT) not in sys.path:
    sys.path.insert(0, str(BOTS_ROOT))

from Bots.datamodel import Listing, Observation, Order, OrderDepth, Trade, TradingState  # noqa: E402


ROUND3_PRODUCTS = [
    "HYDROGEL_PACK",
    "VELVETFRUIT_EXTRACT",
    "VEV_4000",
    "VEV_4500",
    "VEV_5000",
    "VEV_5100",
    "VEV_5200",
    "VEV_5300",
    "VEV_5400",
    "VEV_5500",
    "VEV_6000",
    "VEV_6500",
]

POSITION_LIMITS = {
    "HYDROGEL_PACK": 200,
    "VELVETFRUIT_EXTRACT": 200,
    **{product: 300 for product in ROUND3_PRODUCTS if product.startswith("VEV_")},
}

DEFAULT_FILLABILITY = {
    "aggressive_cross": 0.98,
    "passive_inside": 0.62,
    "passive_touch": 0.36,
    "passive_behind": 0.10,
}

DENOMINATION = "XIRECS"


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _parse_int(value: str) -> Optional[int]:
    value = value.strip()
    if value == "":
        return None
    return int(round(float(value)))


def _parse_float(value: str) -> Optional[float]:
    value = value.strip()
    if value == "":
        return None
    return float(value)


def _display_path(path: Path | str) -> str:
    candidate = Path(path)
    try:
        return str(candidate.resolve().relative_to(REPO_ROOT))
    except Exception:
        return str(path)


def _open_detected_dict_reader(path: Path) -> tuple[object, csv.DictReader]:
    handle = path.open(newline="")
    header = handle.readline()
    delimiter = ";"
    if header.count(",") > header.count(";"):
        delimiter = ","
    handle.seek(0)
    return handle, csv.DictReader(handle, delimiter=delimiter)


@dataclass
class BookSnapshot:
    day: int
    timestamp: int
    product: str
    bids: List[Tuple[int, int]]
    asks: List[Tuple[int, int]]
    mid_price: Optional[float]

    @property
    def best_bid(self) -> Optional[int]:
        return self.bids[0][0] if self.bids else None

    @property
    def best_ask(self) -> Optional[int]:
        return self.asks[0][0] if self.asks else None

    @property
    def spread(self) -> Optional[int]:
        if self.best_bid is None or self.best_ask is None:
            return None
        return self.best_ask - self.best_bid


@dataclass
class TapeTrade:
    day: int
    timestamp: int
    product: str
    price: int
    quantity: int
    buyer: str = ""
    seller: str = ""


@dataclass
class TickFrame:
    day: int
    timestamp: int
    books: Dict[str, BookSnapshot]
    trades: Dict[str, List[TapeTrade]]


@dataclass
class Round3MarketData:
    dataset: str
    tick_step: int
    products: List[str]
    ticks_by_day: Dict[int, List[TickFrame]]
    snapshot_lookup: Dict[Tuple[int, int, str], BookSnapshot]

    @property
    def days(self) -> List[int]:
        return sorted(self.ticks_by_day)


@dataclass
class OfficialLogSummary:
    path: str
    label: str
    day: Optional[int]
    total_pnl: float
    pnl_by_product: Dict[str, float]
    trade_history: List[dict]


@dataclass
class FillProfile:
    counts: Dict[str, Dict[str, int]]
    median_sizes: Dict[str, Dict[str, int]]

    def fillability(self, product: str, category: str) -> float:
        product_counts = self.counts.get(product, {})
        total = sum(product_counts.values())
        default = DEFAULT_FILLABILITY[category]
        if total <= 0:
            return default
        category_count = product_counts.get(category, 0)
        max_count = max(product_counts.values()) if product_counts else 0
        empirical = category_count / max(1, max_count)
        return clamp(0.35 * default + 0.65 * empirical, 0.05, 0.99)

    def typical_size(self, product: str, category: str) -> int:
        product_sizes = self.median_sizes.get(product, {})
        if category in product_sizes:
            return product_sizes[category]
        if product_sizes:
            return int(statistics.median(product_sizes.values()))
        return 6 if product == "VELVETFRUIT_EXTRACT" else 4

    def to_dict(self) -> dict:
        return {
            "counts": self.counts,
            "median_sizes": self.median_sizes,
        }


@dataclass
class FillEvent:
    day: int
    timestamp: int
    product: str
    side: str
    price: int
    quantity: int
    category: str

    def to_trade(self) -> Trade:
        buyer = "SUBMISSION" if self.side == "buy" else ""
        seller = "SUBMISSION" if self.side == "sell" else ""
        return Trade(
            symbol=self.product,
            price=self.price,
            quantity=self.quantity,
            buyer=buyer,
            seller=seller,
            timestamp=self.timestamp,
        )


@dataclass
class PathResult:
    seed: int
    total_pnl: float
    pnl_by_product: Dict[str, float]
    final_positions: Dict[str, int]
    own_trade_count: int
    max_drawdown: float
    equity_curve: List[Tuple[int, int, float]] = field(default_factory=list)


@dataclass
class MonteCarloSummary:
    bot: str
    dataset: str
    days: List[int]
    simulations: int
    tick_step: int
    carry_state: bool
    mean_total: float
    median_total: float
    stdev_total: float
    p05_total: float
    p95_total: float
    paths: List[PathResult]
    per_product_stats: Dict[str, Dict[str, float]]
    fill_profile: dict
    compared_log: Optional[dict]

    def to_dict(self) -> dict:
        return {
            "bot": self.bot,
            "dataset": self.dataset,
            "days": self.days,
            "simulations": self.simulations,
            "tick_step": self.tick_step,
            "carry_state": self.carry_state,
            "mean_total": self.mean_total,
            "median_total": self.median_total,
            "stdev_total": self.stdev_total,
            "p05_total": self.p05_total,
            "p95_total": self.p95_total,
            "per_product_stats": self.per_product_stats,
            "fill_profile": self.fill_profile,
            "compared_log": self.compared_log,
            "paths": [
                {
                    "seed": path.seed,
                    "total_pnl": path.total_pnl,
                    "pnl_by_product": path.pnl_by_product,
                    "final_positions": path.final_positions,
                    "own_trade_count": path.own_trade_count,
                    "max_drawdown": path.max_drawdown,
                }
                for path in self.paths
            ],
        }


class TraderAdapter:
    def __init__(self, bot_path: Path) -> None:
        self.bot_path = bot_path.resolve()
        module_name = f"xw_r3_bt_{self.bot_path.stem}_{abs(hash(self.bot_path))}"
        spec = importlib.util.spec_from_file_location(module_name, self.bot_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not import trader from {self.bot_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "Trader"):
            raise AttributeError(f"{self.bot_path} does not define Trader")
        self._trader = module.Trader()

    def run(self, state: TradingState) -> Tuple[Dict[str, List[Order]], int, str]:
        result = self._trader.run(state)
        if isinstance(result, tuple):
            if len(result) == 3:
                orders, conversions, trader_data = result
                return orders, int(conversions), str(trader_data)
            if len(result) == 2:
                orders, conversions = result
                return orders, int(conversions), state.traderData
        raise TypeError("Trader.run must return (orders, conversions, traderData) or (orders, conversions)")


def load_round3_market_data(dataset_dir: Path, days: Optional[Sequence[int]] = None, tick_step: int = 1) -> Round3MarketData:
    price_pattern = re.compile(r"prices_round_3_day_(-?\d+)\.csv$")
    trade_pattern = re.compile(r"trades_round_3_day_(-?\d+)\.csv$")
    wanted_days = set(days) if days is not None else None

    books_by_key: Dict[Tuple[int, int], Dict[str, BookSnapshot]] = {}
    trades_by_key: Dict[Tuple[int, int], Dict[str, List[TapeTrade]]] = {}
    snapshot_lookup: Dict[Tuple[int, int, str], BookSnapshot] = {}
    products = set()

    for path in sorted(dataset_dir.glob("prices_round_3_day_*.csv")):
        match = price_pattern.match(path.name)
        if not match:
            continue
        day = int(match.group(1))
        if wanted_days is not None and day not in wanted_days:
            continue
        handle, reader = _open_detected_dict_reader(path)
        with handle:
            for row in reader:
                timestamp = int(row["timestamp"])
                product = row["product"]
                products.add(product)
                bids: List[Tuple[int, int]] = []
                asks: List[Tuple[int, int]] = []
                for idx in range(1, 4):
                    bid_price = _parse_int(row[f"bid_price_{idx}"])
                    bid_volume = _parse_int(row[f"bid_volume_{idx}"])
                    ask_price = _parse_int(row[f"ask_price_{idx}"])
                    ask_volume = _parse_int(row[f"ask_volume_{idx}"])
                    if bid_price is not None and bid_volume is not None:
                        bids.append((bid_price, bid_volume))
                    if ask_price is not None and ask_volume is not None:
                        asks.append((ask_price, ask_volume))
                snapshot = BookSnapshot(
                    day=day,
                    timestamp=timestamp,
                    product=product,
                    bids=bids,
                    asks=asks,
                    mid_price=_parse_float(row["mid_price"]),
                )
                books_by_key.setdefault((day, timestamp), {})[product] = snapshot
                snapshot_lookup[(day, timestamp, product)] = snapshot

    for path in sorted(dataset_dir.glob("trades_round_3_day_*.csv")):
        match = trade_pattern.match(path.name)
        if not match:
            continue
        day = int(match.group(1))
        if wanted_days is not None and day not in wanted_days:
            continue
        handle, reader = _open_detected_dict_reader(path)
        with handle:
            for row in reader:
                timestamp = int(row["timestamp"])
                product = row["symbol"]
                tape_trade = TapeTrade(
                    day=day,
                    timestamp=timestamp,
                    product=product,
                    price=int(round(float(row["price"]))),
                    quantity=int(round(float(row["quantity"]))),
                    buyer=row.get("buyer", "") or "",
                    seller=row.get("seller", "") or "",
                )
                trades_by_key.setdefault((day, timestamp), {}).setdefault(product, []).append(tape_trade)

    ticks_by_day: Dict[int, List[TickFrame]] = {}
    for day in sorted({day for day, _ in books_by_key}):
        timestamps = sorted(timestamp for data_day, timestamp in books_by_key if data_day == day)
        if tick_step > 1:
            timestamps = timestamps[::tick_step]
        day_ticks: List[TickFrame] = []
        for timestamp in timestamps:
            key = (day, timestamp)
            day_ticks.append(
                TickFrame(
                    day=day,
                    timestamp=timestamp,
                    books=books_by_key.get(key, {}),
                    trades=trades_by_key.get(key, {}),
                )
            )
        ticks_by_day[day] = day_ticks

    return Round3MarketData(
        dataset=_display_path(dataset_dir),
        tick_step=tick_step,
        products=sorted(products),
        ticks_by_day=ticks_by_day,
        snapshot_lookup=snapshot_lookup,
    )


def parse_official_log(log_path: Path) -> OfficialLogSummary:
    payload = json.loads(log_path.read_text())
    activities_log = payload.get("activitiesLog", "")
    pnl_by_product: Dict[str, float] = {}
    day: Optional[int] = None
    if activities_log:
        reader = csv.DictReader(io.StringIO(activities_log), delimiter=";")
        for row in reader:
            day = int(row["day"])
            pnl_by_product[row["product"]] = float(row["profit_and_loss"])
    total_pnl = sum(pnl_by_product.values())
    return OfficialLogSummary(
        path=str(log_path),
        label=log_path.stem,
        day=day,
        total_pnl=total_pnl,
        pnl_by_product=pnl_by_product,
        trade_history=payload.get("tradeHistory", []),
    )


def build_fill_profile(log_paths: Sequence[Path], market: Round3MarketData) -> FillProfile:
    counts: Dict[str, Dict[str, int]] = {}
    sizes: Dict[str, Dict[str, List[int]]] = {}
    for log_path in log_paths:
        summary = parse_official_log(log_path)
        if summary.day is None:
            continue
        for raw_trade in summary.trade_history:
            buyer = raw_trade.get("buyer", "") or ""
            seller = raw_trade.get("seller", "") or ""
            side: Optional[str]
            if buyer == "SUBMISSION":
                side = "buy"
            elif seller == "SUBMISSION":
                side = "sell"
            else:
                continue
            product = raw_trade["symbol"]
            timestamp = int(raw_trade["timestamp"])
            snapshot = market.snapshot_lookup.get((summary.day, timestamp, product))
            if snapshot is None:
                continue
            category = classify_fill_against_book(
                side=side,
                price=int(round(float(raw_trade["price"]))),
                snapshot=snapshot,
            )
            quantity = int(round(float(raw_trade["quantity"])))
            counts.setdefault(product, {}).setdefault(category, 0)
            counts[product][category] += quantity
            sizes.setdefault(product, {}).setdefault(category, []).append(quantity)
    median_sizes = {
        product: {category: int(statistics.median(values)) for category, values in category_sizes.items()}
        for product, category_sizes in sizes.items()
    }
    return FillProfile(counts=counts, median_sizes=median_sizes)


def classify_fill_against_book(side: str, price: int, snapshot: BookSnapshot) -> str:
    best_bid = snapshot.best_bid
    best_ask = snapshot.best_ask
    if side == "buy":
        if best_ask is not None and price >= best_ask:
            return "aggressive_cross"
        if best_bid is not None and best_ask is not None and best_bid < price < best_ask:
            return "passive_inside"
        if best_bid is not None and price == best_bid:
            return "passive_touch"
        return "passive_behind"
    if best_bid is not None and price <= best_bid:
        return "aggressive_cross"
    if best_bid is not None and best_ask is not None and best_bid < price < best_ask:
        return "passive_inside"
    if best_ask is not None and price == best_ask:
        return "passive_touch"
    return "passive_behind"


def infer_trade_aggressor(trade: TapeTrade, snapshot: BookSnapshot) -> Tuple[float, float]:
    if trade.buyer and not trade.seller:
        return float(trade.quantity), 0.0
    if trade.seller and not trade.buyer:
        return 0.0, float(trade.quantity)
    best_bid = snapshot.best_bid
    best_ask = snapshot.best_ask
    if best_ask is not None and trade.price >= best_ask:
        return float(trade.quantity), 0.0
    if best_bid is not None and trade.price <= best_bid:
        return 0.0, float(trade.quantity)
    mid = snapshot.mid_price
    if mid is None and best_bid is not None and best_ask is not None:
        mid = 0.5 * (best_bid + best_ask)
    if mid is None:
        return 0.5 * float(trade.quantity), 0.5 * float(trade.quantity)
    if trade.price > mid:
        return float(trade.quantity), 0.0
    if trade.price < mid:
        return 0.0, float(trade.quantity)
    return 0.5 * float(trade.quantity), 0.5 * float(trade.quantity)


class MonteCarloBacktester:
    def __init__(self, market: Round3MarketData, fill_profile: FillProfile) -> None:
        self.market = market
        self.fill_profile = fill_profile
        self.listings = {
            product: Listing(symbol=product, product=product, denomination=DENOMINATION)
            for product in self.market.products
        }

    def run(
        self,
        bot_path: Path,
        days: Sequence[int],
        simulations: int,
        base_seed: int,
        carry_state: bool,
        compare_log: Optional[Path] = None,
    ) -> MonteCarloSummary:
        paths = [
            self._run_single_path(
                bot_path=bot_path,
                days=days,
                seed=base_seed + idx,
                carry_state=carry_state,
            )
            for idx in range(simulations)
        ]
        totals = [path.total_pnl for path in paths]
        mean_total = statistics.fmean(totals) if totals else 0.0
        median_total = statistics.median(totals) if totals else 0.0
        stdev_total = statistics.pstdev(totals) if len(totals) > 1 else 0.0
        ordered = sorted(totals)
        p05_total = ordered[max(0, int(0.05 * (len(ordered) - 1)))] if ordered else 0.0
        p95_total = ordered[min(len(ordered) - 1, int(0.95 * (len(ordered) - 1)))] if ordered else 0.0

        per_product_stats: Dict[str, Dict[str, float]] = {}
        for product in ROUND3_PRODUCTS:
            series = [path.pnl_by_product.get(product, 0.0) for path in paths]
            per_product_stats[product] = {
                "mean": statistics.fmean(series) if series else 0.0,
                "median": statistics.median(series) if series else 0.0,
                "stdev": statistics.pstdev(series) if len(series) > 1 else 0.0,
                "p05": sorted(series)[max(0, int(0.05 * (len(series) - 1)))] if series else 0.0,
                "p95": sorted(series)[min(len(series) - 1, int(0.95 * (len(series) - 1)))] if series else 0.0,
            }

        compared_log = None
        if compare_log is not None and compare_log.exists():
            log_summary = parse_official_log(compare_log)
            compared_log = {
                "path": _display_path(compare_log),
                "total_pnl": log_summary.total_pnl,
                "pnl_by_product": log_summary.pnl_by_product,
                "delta_vs_mc_mean": log_summary.total_pnl - mean_total,
            }

        return MonteCarloSummary(
            bot=bot_path.name,
            dataset=self.market.dataset,
            days=list(days),
            simulations=simulations,
            tick_step=self.market.tick_step,
            carry_state=carry_state,
            mean_total=mean_total,
            median_total=median_total,
            stdev_total=stdev_total,
            p05_total=p05_total,
            p95_total=p95_total,
            paths=paths,
            per_product_stats=per_product_stats,
            fill_profile=self.fill_profile.to_dict(),
            compared_log=compared_log,
        )

    def _run_single_path(self, bot_path: Path, days: Sequence[int], seed: int, carry_state: bool) -> PathResult:
        rng = random.Random(seed)
        adapter = TraderAdapter(bot_path)
        positions = {product: 0 for product in ROUND3_PRODUCTS}
        cash = {product: 0.0 for product in ROUND3_PRODUCTS}
        own_trade_buffer = {product: [] for product in ROUND3_PRODUCTS}
        trader_data = ""
        own_trade_count = 0
        last_marks = {product: 0.0 for product in ROUND3_PRODUCTS}
        equity_curve: List[Tuple[int, int, float]] = []

        for index, day in enumerate(days):
            if day not in self.market.ticks_by_day:
                continue
            if index > 0 and not carry_state:
                positions = {product: 0 for product in ROUND3_PRODUCTS}
                cash = {product: 0.0 for product in ROUND3_PRODUCTS}
                own_trade_buffer = {product: [] for product in ROUND3_PRODUCTS}
                trader_data = ""

            for tick in self.market.ticks_by_day[day]:
                state = self._build_state(
                    day=day,
                    tick=tick,
                    trader_data=trader_data,
                    positions=positions,
                    own_trade_buffer=own_trade_buffer,
                )
                raw_orders, _, trader_data = adapter.run(state)
                fills = self._match_orders(
                    raw_orders=raw_orders,
                    tick=tick,
                    positions=positions,
                    rng=rng,
                )
                own_trade_buffer = {product: [] for product in ROUND3_PRODUCTS}
                for fill in fills:
                    signed_qty = fill.quantity if fill.side == "buy" else -fill.quantity
                    positions[fill.product] += signed_qty
                    cash_delta = -fill.price * fill.quantity if fill.side == "buy" else fill.price * fill.quantity
                    cash[fill.product] += cash_delta
                    own_trade_buffer[fill.product].append(fill.to_trade())
                    own_trade_count += 1

                total_equity = 0.0
                for product in ROUND3_PRODUCTS:
                    snapshot = tick.books.get(product)
                    if snapshot is not None and snapshot.mid_price is not None:
                        last_marks[product] = float(snapshot.mid_price)
                    total_equity += cash[product] + positions[product] * last_marks[product]
                equity_curve.append((day, tick.timestamp, total_equity))

        pnl_by_product = {
            product: cash[product] + positions[product] * last_marks[product]
            for product in ROUND3_PRODUCTS
        }
        total_pnl = sum(pnl_by_product.values())
        max_drawdown = compute_max_drawdown([equity for _, _, equity in equity_curve])
        return PathResult(
            seed=seed,
            total_pnl=total_pnl,
            pnl_by_product=pnl_by_product,
            final_positions=dict(positions),
            own_trade_count=own_trade_count,
            max_drawdown=max_drawdown,
            equity_curve=equity_curve,
        )

    def _build_state(
        self,
        day: int,
        tick: TickFrame,
        trader_data: str,
        positions: Dict[str, int],
        own_trade_buffer: Dict[str, List[Trade]],
    ) -> TradingState:
        order_depths: Dict[str, OrderDepth] = {}
        market_trades: Dict[str, List[Trade]] = {}
        for product in self.market.products:
            snapshot = tick.books.get(product)
            order_depth = OrderDepth()
            if snapshot is not None:
                order_depth.buy_orders = {price: volume for price, volume in snapshot.bids}
                order_depth.sell_orders = {price: -abs(volume) for price, volume in snapshot.asks}
            order_depths[product] = order_depth
            tape_trades = tick.trades.get(product, [])
            market_trades[product] = [
                Trade(
                    symbol=trade.product,
                    price=trade.price,
                    quantity=trade.quantity,
                    buyer=trade.buyer or None,
                    seller=trade.seller or None,
                    timestamp=trade.timestamp,
                )
                for trade in tape_trades
            ]
        return TradingState(
            traderData=trader_data,
            timestamp=tick.timestamp,
            listings=self.listings,
            order_depths=order_depths,
            own_trades={product: list(own_trade_buffer.get(product, [])) for product in self.market.products},
            market_trades=market_trades,
            position={product: positions.get(product, 0) for product in self.market.products},
            observations=Observation({}, {}),
        )

    def _match_orders(
        self,
        raw_orders: Dict[str, List[Order]],
        tick: TickFrame,
        positions: Dict[str, int],
        rng: random.Random,
    ) -> List[FillEvent]:
        fills: List[FillEvent] = []
        for product, orders in raw_orders.items():
            limit = POSITION_LIMITS.get(product, 0)
            current_position = positions.get(product, 0)
            snapshot = tick.books.get(product)
            if snapshot is None:
                continue
            clipped_orders = clip_orders_to_limits(orders, current_position, limit)
            mutable_bids = list(snapshot.bids)
            mutable_asks = list(snapshot.asks)
            for order in clipped_orders:
                remaining = abs(int(order.quantity))
                if remaining <= 0:
                    continue
                side = "buy" if order.quantity > 0 else "sell"
                if side == "buy":
                    remaining, aggressive_fills = self._match_aggressive_buy(
                        day=tick.day,
                        timestamp=tick.timestamp,
                        product=product,
                        order_price=int(order.price),
                        remaining=remaining,
                        asks=mutable_asks,
                    )
                else:
                    remaining, aggressive_fills = self._match_aggressive_sell(
                        day=tick.day,
                        timestamp=tick.timestamp,
                        product=product,
                        order_price=int(order.price),
                        remaining=remaining,
                        bids=mutable_bids,
                    )
                fills.extend(aggressive_fills)
                if remaining <= 0:
                    continue
                passive_fill = self._sample_passive_fill(
                    day=tick.day,
                    timestamp=tick.timestamp,
                    product=product,
                    side=side,
                    price=int(order.price),
                    remaining=remaining,
                    snapshot=snapshot,
                    trades=tick.trades.get(product, []),
                    rng=rng,
                )
                if passive_fill is not None:
                    fills.append(passive_fill)
        return fills

    def _match_aggressive_buy(
        self,
        day: int,
        timestamp: int,
        product: str,
        order_price: int,
        remaining: int,
        asks: List[Tuple[int, int]],
    ) -> Tuple[int, List[FillEvent]]:
        fills: List[FillEvent] = []
        while remaining > 0 and asks and asks[0][0] <= order_price:
            ask_price, ask_volume = asks[0]
            fill_qty = min(remaining, ask_volume)
            fills.append(
                FillEvent(
                    day=day,
                    timestamp=timestamp,
                    product=product,
                    side="buy",
                    price=ask_price,
                    quantity=fill_qty,
                    category="aggressive_cross",
                )
            )
            remaining -= fill_qty
            ask_volume -= fill_qty
            if ask_volume <= 0:
                asks.pop(0)
            else:
                asks[0] = (ask_price, ask_volume)
        return remaining, fills

    def _match_aggressive_sell(
        self,
        day: int,
        timestamp: int,
        product: str,
        order_price: int,
        remaining: int,
        bids: List[Tuple[int, int]],
    ) -> Tuple[int, List[FillEvent]]:
        fills: List[FillEvent] = []
        while remaining > 0 and bids and bids[0][0] >= order_price:
            bid_price, bid_volume = bids[0]
            fill_qty = min(remaining, bid_volume)
            fills.append(
                FillEvent(
                    day=day,
                    timestamp=timestamp,
                    product=product,
                    side="sell",
                    price=bid_price,
                    quantity=fill_qty,
                    category="aggressive_cross",
                )
            )
            remaining -= fill_qty
            bid_volume -= fill_qty
            if bid_volume <= 0:
                bids.pop(0)
            else:
                bids[0] = (bid_price, bid_volume)
        return remaining, fills

    def _sample_passive_fill(
        self,
        day: int,
        timestamp: int,
        product: str,
        side: str,
        price: int,
        remaining: int,
        snapshot: BookSnapshot,
        trades: Sequence[TapeTrade],
        rng: random.Random,
    ) -> Optional[FillEvent]:
        category = classify_fill_against_book(side=side, price=price, snapshot=snapshot)
        if category == "aggressive_cross":
            return None
        base_fillability = self.fill_profile.fillability(product, category)
        typical_size = self.fill_profile.typical_size(product, category)

        buy_flow = 0.0
        sell_flow = 0.0
        for trade in trades:
            inferred_buy, inferred_sell = infer_trade_aggressor(trade, snapshot)
            buy_flow += inferred_buy
            sell_flow += inferred_sell
        contra_flow = sell_flow if side == "buy" else buy_flow
        queue_bonus = {
            "passive_inside": 1.25,
            "passive_touch": 0.95,
            "passive_behind": 0.30,
        }[category]
        flow_factor = 1.0 - math.exp(-contra_flow / max(1.0, float(remaining)))
        base_prob = 0.02 + 0.20 * base_fillability * queue_bonus
        prob = base_prob + 0.65 * base_fillability * queue_bonus * flow_factor
        if contra_flow <= 0.0:
            prob = 0.01 + 0.08 * base_fillability * queue_bonus
        probability = clamp(prob, 0.0, 0.97)
        if rng.random() > probability:
            return None
        expected = max(1, int(round(typical_size * (0.35 + 0.65 * flow_factor) * queue_bonus)))
        if contra_flow > 0.0:
            expected = min(expected, max(1, int(round(contra_flow * queue_bonus))))
        expected = min(expected, remaining)
        lower = max(1, min(remaining, int(max(1, math.floor(0.5 * expected)))))
        upper = max(lower, min(remaining, int(max(lower, math.ceil(1.5 * expected)))))
        fill_qty = rng.randint(lower, upper)
        return FillEvent(
            day=day,
            timestamp=timestamp,
            product=product,
            side=side,
            price=price,
            quantity=fill_qty,
            category=category,
        )


def clip_orders_to_limits(orders: Sequence[Order], position: int, limit: int) -> List[Order]:
    projected = position
    clipped: List[Order] = []
    for order in orders:
        qty = int(order.quantity)
        if qty > 0:
            allowed = max(0, limit - projected)
            qty = min(qty, allowed)
        elif qty < 0:
            allowed = max(0, limit + projected)
            qty = -min(-qty, allowed)
        if qty != 0:
            clipped.append(Order(order.symbol, int(order.price), qty))
            projected += qty
    return clipped


def compute_max_drawdown(equity_curve: Sequence[float]) -> float:
    peak = float("-inf")
    max_drawdown = 0.0
    for equity in equity_curve:
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
    return max_drawdown


def render_markdown(summary: MonteCarloSummary) -> str:
    lines = [
        f"# Round 3 Monte Carlo Backtest: {summary.bot}",
        "",
        f"- Dataset: `{summary.dataset}`",
        f"- Days: `{summary.days}`",
        f"- Simulations: `{summary.simulations}`",
        f"- Carry state: `{summary.carry_state}`",
        "",
        "## Total PnL Distribution",
        "",
        f"- Mean: `{summary.mean_total:.2f}`",
        f"- Median: `{summary.median_total:.2f}`",
        f"- Std dev: `{summary.stdev_total:.2f}`",
        f"- P05: `{summary.p05_total:.2f}`",
        f"- P95: `{summary.p95_total:.2f}`",
        "",
        "## Product Means",
        "",
        "| Product | Mean | Median | Std dev |",
        "| --- | ---: | ---: | ---: |",
    ]
    for product in ROUND3_PRODUCTS:
        row = summary.per_product_stats[product]
        lines.append(
            f"| {product} | {row['mean']:.2f} | {row['median']:.2f} | {row['stdev']:.2f} |"
        )
    if summary.compared_log:
        lines.extend(
            [
                "",
                "## Compared Official Log",
                "",
                f"- Log: `{summary.compared_log['path']}`",
                f"- Official total: `{summary.compared_log['total_pnl']:.2f}`",
                f"- Delta vs MC mean: `{summary.compared_log['delta_vs_mc_mean']:.2f}`",
            ]
        )
    return "\n".join(lines) + "\n"


def write_summary(output_dir: Path, summary: MonteCarloSummary) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(summary.to_dict(), indent=2) + "\n")
    (output_dir / "report.md").write_text(render_markdown(summary))
    lines = ["seed,total_pnl,max_drawdown,own_trade_count"]
    for path in summary.paths:
        lines.append(f"{path.seed},{path.total_pnl:.6f},{path.max_drawdown:.6f},{path.own_trade_count}")
    (output_dir / "paths.csv").write_text("\n".join(lines) + "\n")


def discover_official_logs(logs_dir: Path) -> List[Path]:
    return sorted(logs_dir.glob("TradervR3_*.log"))
