from __future__ import annotations

import csv
import json
import math
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


CSV_DELIMITER = ";"
DEFAULT_MARKOUT_BARS = (5, 20, 50)


@dataclass
class BookSnapshot:
    day: int
    timestamp: int
    product: str
    bid_prices: list[int]
    bid_volumes: list[int]
    ask_prices: list[int]
    ask_volumes: list[int]
    mid_price: Optional[float]

    @property
    def best_bid(self) -> Optional[int]:
        return self.bid_prices[0] if self.bid_prices else None

    @property
    def best_ask(self) -> Optional[int]:
        return self.ask_prices[0] if self.ask_prices else None

    @property
    def spread(self) -> Optional[float]:
        if self.best_bid is None or self.best_ask is None:
            return None
        return float(self.best_ask - self.best_bid)


@dataclass
class SnapshotSeries:
    timestamps: list[int]
    snapshots: list[BookSnapshot]

    def at_or_before(self, timestamp: int) -> Optional[BookSnapshot]:
        index = bisect_right(self.timestamps, timestamp) - 1
        if index < 0:
            return None
        return self.snapshots[index]

    def at_or_after(self, timestamp: int) -> Optional[BookSnapshot]:
        index = bisect_left(self.timestamps, timestamp)
        if index >= len(self.snapshots):
            return None
        return self.snapshots[index]


@dataclass
class QuantityCluster:
    center: int
    min_qty: int
    max_qty: int
    count: int
    members: list[int]

    def matches(self, quantity: int) -> bool:
        return self.min_qty <= quantity <= self.max_qty


@dataclass
class TradeFeature:
    day: int
    timestamp: int
    product: str
    buyer: str
    seller: str
    price: float
    quantity: int
    inferred_side: str
    best_bid: Optional[float]
    best_ask: Optional[float]
    mid_price: Optional[float]
    distance_to_mid: Optional[float]
    distance_to_best_bid: Optional[float]
    distance_to_best_ask: Optional[float]
    is_new_daily_low_trade: bool
    is_new_daily_high_trade: bool
    markouts: dict[str, Optional[float]]
    persistence_bars: int
    cluster_center: Optional[int] = None
    cluster_min: Optional[int] = None
    cluster_max: Optional[int] = None

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        for horizon, value in self.markouts.items():
            row[f"markout_{horizon}"] = value
        row.pop("markouts", None)
        return row


@dataclass
class CandidateScore:
    product: str
    cluster_center: int
    cluster_min: int
    cluster_max: int
    trade_count: int
    extremum_hit_rate: float
    directional_correctness: float
    persistence: float
    cross_day_repeatability: float
    cross_product_repeatability: float
    candidate_score: float
    recommended_mode: str
    buy_at_lows_precision: float
    sell_at_highs_precision: float
    avg_signal_persistence_bars: float
    signal_proxy_pnl: float = 0.0
    notes: list[str] = field(default_factory=list)

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["notes"] = " | ".join(self.notes)
        return row


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open() as handle:
        return list(csv.DictReader(handle, delimiter=CSV_DELIMITER))


def write_csv_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    if not rows:
        path.write_text("")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False))


def parse_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    return int(float(value))


def parse_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    return float(value)


def round_dir_from_path(path: Path) -> str:
    return path.name if path.is_dir() else path.parent.name


def list_round_files(data_root: Path, round_dir: str) -> tuple[list[Path], list[Path]]:
    base = data_root / round_dir
    prices = sorted(base.glob("prices_*.csv"))
    trades = sorted(base.glob("trades_*.csv"))
    if not prices or not trades:
        raise FileNotFoundError(f"No round files found in {base}")
    return prices, trades


def load_price_series(data_root: Path, round_dir: str) -> dict[tuple[int, str], SnapshotSeries]:
    price_files, _ = list_round_files(data_root, round_dir)
    grouped: dict[tuple[int, str], list[BookSnapshot]] = defaultdict(list)
    for path in price_files:
        for row in read_csv_rows(path):
            day = parse_int(row["day"])
            timestamp = parse_int(row["timestamp"])
            product = row["product"]
            bid_prices: list[int] = []
            bid_volumes: list[int] = []
            ask_prices: list[int] = []
            ask_volumes: list[int] = []
            for level in (1, 2, 3):
                bp = parse_int(row.get(f"bid_price_{level}"))
                bv = parse_int(row.get(f"bid_volume_{level}"))
                ap = parse_int(row.get(f"ask_price_{level}"))
                av = parse_int(row.get(f"ask_volume_{level}"))
                if bp is not None and bv not in (None, 0):
                    bid_prices.append(bp)
                    bid_volumes.append(abs(int(bv)))
                if ap is not None and av not in (None, 0):
                    ask_prices.append(ap)
                    ask_volumes.append(abs(int(av)))
            grouped[(day, product)].append(
                BookSnapshot(
                    day=day or 0,
                    timestamp=timestamp or 0,
                    product=product,
                    bid_prices=bid_prices,
                    bid_volumes=bid_volumes,
                    ask_prices=ask_prices,
                    ask_volumes=ask_volumes,
                    mid_price=parse_float(row.get("mid_price")),
                )
            )

    series: dict[tuple[int, str], SnapshotSeries] = {}
    for key, snapshots in grouped.items():
        ordered = sorted(snapshots, key=lambda snap: snap.timestamp)
        series[key] = SnapshotSeries(
            timestamps=[snap.timestamp for snap in ordered],
            snapshots=ordered,
        )
    return series


def load_trade_rows(data_root: Path, round_dir: str) -> dict[tuple[int, str], list[dict[str, Any]]]:
    _, trade_files = list_round_files(data_root, round_dir)
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for path in trade_files:
        day = parse_day_from_filename(path.name)
        for row in read_csv_rows(path):
            product = row["symbol"]
            grouped[(day, product)].append(
                {
                    "day": day,
                    "timestamp": parse_int(row["timestamp"]) or 0,
                    "buyer": row.get("buyer", "") or "",
                    "seller": row.get("seller", "") or "",
                    "product": product,
                    "price": parse_float(row["price"]) or 0.0,
                    "quantity": abs(parse_int(row["quantity"]) or 0),
                }
            )
    for key in grouped:
        grouped[key].sort(key=lambda row: row["timestamp"])
    return grouped


def parse_day_from_filename(name: str) -> int:
    stem = Path(name).stem
    day_token = stem.split("_day_")[-1]
    return int(day_token)


def infer_trade_side(
    price: float,
    snapshot: Optional[BookSnapshot],
    tolerance: float = 0.25,
) -> str:
    if snapshot is None:
        return "UNKNOWN"
    best_bid = snapshot.best_bid
    best_ask = snapshot.best_ask
    mid = snapshot.mid_price
    if best_ask is not None and price >= best_ask - tolerance:
        return "BUY"
    if best_bid is not None and price <= best_bid + tolerance:
        return "SELL"
    if mid is None:
        return "UNKNOWN"
    if price > mid:
        return "BUY"
    if price < mid:
        return "SELL"
    return "UNKNOWN"


def compute_markout(snapshot_series: SnapshotSeries, timestamp: int, horizon_bars: int, fill_price: float) -> Optional[float]:
    target_ts = timestamp + horizon_bars * 100
    future_snapshot = snapshot_series.at_or_after(target_ts)
    if future_snapshot is None or future_snapshot.mid_price is None:
        return None
    return future_snapshot.mid_price - fill_price


def compute_persistence_bars(markouts: dict[str, Optional[float]], inferred_side: str) -> int:
    if inferred_side not in {"BUY", "SELL"}:
        return 0
    sign = 1 if inferred_side == "BUY" else -1
    best = 0
    for horizon, value in markouts.items():
        if value is None:
            continue
        if value * sign > 0:
            try:
                best = max(best, int(horizon))
            except ValueError:
                continue
    return best


def build_trade_features(
    data_root: Path,
    round_dir: str,
    markout_bars: Iterable[int] = DEFAULT_MARKOUT_BARS,
) -> list[TradeFeature]:
    price_series = load_price_series(data_root, round_dir)
    trade_rows = load_trade_rows(data_root, round_dir)
    markout_bars = tuple(sorted(int(bar) for bar in markout_bars))
    features: list[TradeFeature] = []

    for key, trades in sorted(trade_rows.items()):
        day, product = key
        series = price_series.get(key)
        if series is None:
            continue
        running_low = math.inf
        running_high = -math.inf
        for trade in trades:
            timestamp = int(trade["timestamp"])
            snapshot = series.at_or_before(timestamp)
            side = infer_trade_side(float(trade["price"]), snapshot)
            is_new_low = float(trade["price"]) < running_low
            is_new_high = float(trade["price"]) > running_high
            running_low = min(running_low, float(trade["price"]))
            running_high = max(running_high, float(trade["price"]))
            markouts = {
                str(horizon): compute_markout(series, timestamp, horizon, float(trade["price"]))
                for horizon in markout_bars
            }
            persistence = compute_persistence_bars(markouts, side)
            best_bid = snapshot.best_bid if snapshot else None
            best_ask = snapshot.best_ask if snapshot else None
            mid = snapshot.mid_price if snapshot else None
            features.append(
                TradeFeature(
                    day=day,
                    timestamp=timestamp,
                    product=product,
                    buyer=str(trade["buyer"]),
                    seller=str(trade["seller"]),
                    price=float(trade["price"]),
                    quantity=int(trade["quantity"]),
                    inferred_side=side,
                    best_bid=float(best_bid) if best_bid is not None else None,
                    best_ask=float(best_ask) if best_ask is not None else None,
                    mid_price=mid,
                    distance_to_mid=(float(trade["price"]) - mid) if mid is not None else None,
                    distance_to_best_bid=(float(trade["price"]) - best_bid) if best_bid is not None else None,
                    distance_to_best_ask=(float(trade["price"]) - best_ask) if best_ask is not None else None,
                    is_new_daily_low_trade=is_new_low,
                    is_new_daily_high_trade=is_new_high,
                    markouts=markouts,
                    persistence_bars=persistence,
                )
            )
    return features


def cluster_quantities(
    quantities: Iterable[int],
    tolerance: int = 1,
    min_occurrences: int = 3,
) -> list[QuantityCluster]:
    counts = Counter(int(q) for q in quantities if int(q) > 0)
    assigned: set[int] = set()
    clusters: list[QuantityCluster] = []
    for quantity, count in counts.most_common():
        if quantity in assigned or count < min_occurrences:
            continue
        members = sorted(q for q in counts if abs(q - quantity) <= tolerance and q not in assigned)
        if not members:
            continue
        for member in members:
            assigned.add(member)
        total = sum(counts[member] for member in members)
        weighted_center = int(round(sum(member * counts[member] for member in members) / max(1, total)))
        clusters.append(
            QuantityCluster(
                center=weighted_center,
                min_qty=min(members),
                max_qty=max(members),
                count=total,
                members=members,
            )
        )
    return sorted(clusters, key=lambda cluster: (-cluster.count, cluster.center))


def assign_quantity_clusters(features: list[TradeFeature], tolerance: int = 1, min_occurrences: int = 3) -> dict[str, list[QuantityCluster]]:
    product_quantities: dict[str, list[int]] = defaultdict(list)
    for feature in features:
        product_quantities[feature.product].append(feature.quantity)
    clusters_by_product = {
        product: cluster_quantities(quantities, tolerance=tolerance, min_occurrences=min_occurrences)
        for product, quantities in product_quantities.items()
    }
    for feature in features:
        cluster = match_cluster(feature.quantity, clusters_by_product.get(feature.product, []))
        if cluster is not None:
            feature.cluster_center = cluster.center
            feature.cluster_min = cluster.min_qty
            feature.cluster_max = cluster.max_qty
    return clusters_by_product


def match_cluster(quantity: int, clusters: list[QuantityCluster]) -> Optional[QuantityCluster]:
    for cluster in clusters:
        if cluster.matches(quantity):
            return cluster
    return None


def directional_markout_correct(feature: TradeFeature, horizon_key: str = "20") -> bool:
    markout = feature.markouts.get(horizon_key)
    if markout is None:
        return False
    if feature.inferred_side == "BUY":
        return markout > 0
    if feature.inferred_side == "SELL":
        return markout < 0
    return False


def extremum_side_match(feature: TradeFeature) -> bool:
    return (
        feature.is_new_daily_low_trade
        and feature.inferred_side == "BUY"
    ) or (
        feature.is_new_daily_high_trade
        and feature.inferred_side == "SELL"
    )


def recommend_mode(candidate_score: float, directional_correctness: float, persistence: float, trade_count: int) -> str:
    if trade_count >= 6 and directional_correctness >= 0.82 and persistence >= 0.60 and candidate_score >= 4.5:
        return "FULL_FOLLOW"
    if trade_count >= 4 and directional_correctness >= 0.72 and persistence >= 0.45 and candidate_score >= 3.5:
        return "FOLLOW_AFTER_TRIGGER"
    if directional_correctness >= 0.60 and candidate_score >= 2.5:
        return "BIAS_ONLY"
    return "IGNORE"


def score_candidate_clusters(features: list[TradeFeature], clusters_by_product: dict[str, list[QuantityCluster]]) -> list[CandidateScore]:
    cross_product_presence: dict[int, set[str]] = defaultdict(set)
    for product, clusters in clusters_by_product.items():
        for cluster in clusters:
            cross_product_presence[cluster.center].add(product)

    products = {feature.product for feature in features}
    scores: list[CandidateScore] = []
    by_product_cluster: dict[tuple[str, int], list[TradeFeature]] = defaultdict(list)
    for feature in features:
        if feature.cluster_center is None:
            continue
        by_product_cluster[(feature.product, feature.cluster_center)].append(feature)

    for (product, cluster_center), grouped_features in sorted(by_product_cluster.items()):
        cluster = match_cluster(cluster_center, clusters_by_product.get(product, []))
        if cluster is None:
            continue
        trade_count = len(grouped_features)
        extremum_features = [feature for feature in grouped_features if extremum_side_match(feature)]
        buy_low_features = [feature for feature in grouped_features if feature.is_new_daily_low_trade and feature.inferred_side == "BUY"]
        sell_high_features = [feature for feature in grouped_features if feature.is_new_daily_high_trade and feature.inferred_side == "SELL"]
        extremum_hit_rate = len(extremum_features) / trade_count if trade_count else 0.0
        directional_correctness = (
            sum(1 for feature in extremum_features if directional_markout_correct(feature)) / len(extremum_features)
            if extremum_features else 0.0
        )
        persistence = (
            sum(feature.persistence_bars for feature in extremum_features) / max(1, len(extremum_features)) / 50.0
            if extremum_features else 0.0
        )
        active_days = {feature.day for feature in extremum_features}
        all_days = {feature.day for feature in grouped_features}
        cross_day_repeatability = len(active_days) / max(1, len(all_days))
        cross_product_repeatability = len(cross_product_presence[cluster.center]) / max(1, len(products))
        candidate_value = (
            2.0 * extremum_hit_rate
            + 2.0 * directional_correctness
            + 1.0 * persistence
            + 1.0 * cross_day_repeatability
            + 1.0 * cross_product_repeatability
        )
        buy_at_lows_precision = (
            sum(1 for feature in buy_low_features if directional_markout_correct(feature)) / len(buy_low_features)
            if buy_low_features else 0.0
        )
        sell_at_highs_precision = (
            sum(1 for feature in sell_high_features if directional_markout_correct(feature)) / len(sell_high_features)
            if sell_high_features else 0.0
        )
        avg_signal_persistence_bars = (
            sum(feature.persistence_bars for feature in extremum_features) / len(extremum_features)
            if extremum_features else 0.0
        )
        notes: list[str] = []
        if cluster.min_qty != cluster.max_qty:
            notes.append(f"stable lot cluster {cluster.min_qty}-{cluster.max_qty}")
        else:
            notes.append(f"stable lot size {cluster.center}")
        if cross_product_repeatability >= 0.4:
            notes.append("repeats across products")
        if cross_day_repeatability >= 0.6:
            notes.append("repeats across days")
        scores.append(
            CandidateScore(
                product=product,
                cluster_center=cluster.center,
                cluster_min=cluster.min_qty,
                cluster_max=cluster.max_qty,
                trade_count=trade_count,
                extremum_hit_rate=extremum_hit_rate,
                directional_correctness=directional_correctness,
                persistence=persistence,
                cross_day_repeatability=cross_day_repeatability,
                cross_product_repeatability=cross_product_repeatability,
                candidate_score=candidate_value,
                recommended_mode=recommend_mode(candidate_value, directional_correctness, persistence, trade_count),
                buy_at_lows_precision=buy_at_lows_precision,
                sell_at_highs_precision=sell_at_highs_precision,
                avg_signal_persistence_bars=avg_signal_persistence_bars,
                notes=notes,
            )
        )
    return sorted(scores, key=lambda score: (score.product, -score.candidate_score, -score.trade_count))


def features_to_rows(features: list[TradeFeature]) -> list[dict[str, Any]]:
    return [feature.to_row() for feature in features]


def clusters_to_payload(clusters_by_product: dict[str, list[QuantityCluster]]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for product, clusters in sorted(clusters_by_product.items()):
        payload[product] = [asdict(cluster) for cluster in clusters]
    return payload


def scores_to_rows(scores: list[CandidateScore]) -> list[dict[str, Any]]:
    return [score.to_row() for score in scores]

