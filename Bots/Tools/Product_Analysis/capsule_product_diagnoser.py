
#!/usr/bin/env python3
"""
Capsule Product Diagnoser

Load Prosperity data-capsule CSVs (prices/trades), infer product archetypes from
historical behavior, and recommend strategy families based on Competitive Intelligence.

Supports:
- Auto-discovery of price/trade CSVs inside a directory
- Semicolon/comma delimiter detection
- Product-level profiling and archetype classification
- Optional use of a Competitive Intelligence markdown file as context metadata
- Markdown + JSON outputs

Typical usage:
    python capsule_product_diagnoser.py --root /path/to/capsule --out-md report.md --out-json summary.json

You can also pass explicit files:
    python capsule_product_diagnoser.py --prices prices_round_1_day_-1.csv prices_round_1_day_0.csv --trades trades_round_1_day_-1.csv

This tool is intentionally heuristic. It is designed to narrow the search space
for a new round before heavy strategy coding begins.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_ROOT = REPO_ROOT / "Data"
DEFAULT_INTEL_PATH = REPO_ROOT / "Bots" / "Research" / "COMPETITIVE_INTEL.md"


# ----------------------------- IO / discovery ----------------------------- #

STANDARD_PRICE_COLUMNS = {
    "day",
    "timestamp",
    "product",
    "bid_price_1",
    "bid_volume_1",
    "ask_price_1",
    "ask_volume_1",
    "mid_price",
}

STANDARD_TRADE_COLUMNS = {
    "timestamp",
    "symbol",
    "price",
    "quantity",
}


def sniff_delimiter(path: Path) -> str:
    sample = path.read_text(encoding="utf-8", errors="ignore")[:4096]
    if ";" in sample and sample.count(";") >= sample.count(","):
        return ";"
    try:
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter
    except csv.Error:
        return ","


def read_csv_auto(path: Path) -> pd.DataFrame:
    sep = sniff_delimiter(path)
    df = pd.read_csv(path, sep=sep)
    # Handle malformed read where separator wasn't inferred correctly.
    if len(df.columns) == 1 and ";" in df.columns[0]:
        df = pd.read_csv(path, sep=";")
    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def classify_file_kind(path: Path, df: pd.DataFrame) -> str:
    cols = set(df.columns)
    name = path.name.lower()
    if "price" in name or "prices_" in name:
        return "prices"
    if "trade" in name or "trades_" in name:
        return "trades"
    if STANDARD_PRICE_COLUMNS.issubset(cols):
        return "prices"
    if STANDARD_TRADE_COLUMNS.issubset(cols):
        return "trades"
    return "unknown"


def discover_files(
    root: Optional[Path],
    explicit_prices: Optional[Sequence[Path]],
    explicit_trades: Optional[Sequence[Path]],
) -> Tuple[List[Path], List[Path]]:
    price_files: List[Path] = []
    trade_files: List[Path] = []

    if explicit_prices:
        price_files.extend(explicit_prices)
    if explicit_trades:
        trade_files.extend(explicit_trades)

    if root is not None:
        for path in sorted(root.rglob("*.csv")):
            try:
                kind = classify_file_kind(path, normalize_columns(read_csv_auto(path)))
            except Exception:
                # Fall back to filename convention if the file can't be read now.
                lowered = path.name.lower()
                kind = "prices" if "prices_" in lowered else "trades" if "trades_" in lowered else "unknown"
            if kind == "prices" and path not in price_files:
                price_files.append(path)
            elif kind == "trades" and path not in trade_files:
                trade_files.append(path)

    return sorted(price_files), sorted(trade_files)


# ----------------------------- data models ----------------------------- #

@dataclass
class ProductMetrics:
    product: str
    rounds_seen: List[int] = field(default_factory=list)
    days_seen: List[int] = field(default_factory=list)
    n_price_rows: int = 0
    n_valid_rows: int = 0
    n_trade_rows: int = 0

    mean_mid: float = math.nan
    mid_std_valid: float = math.nan
    mean_spread: float = math.nan
    one_sided_ratio: float = math.nan
    avg_top_depth: float = math.nan

    trend_snr: float = math.nan
    trend_r2: float = math.nan
    mean_slope: float = math.nan
    slope_sign_consistency: float = math.nan

    anchor_candidate: Optional[float] = None
    anchor_step: Optional[int] = None
    anchor_strength: float = math.nan

    trend_resid_next_corr: float = math.nan
    rolling_dev_next_corr: float = math.nan
    imbalance_next_corr: float = math.nan
    trade_autocorr_1: float = math.nan

    common_trade_sizes: List[Tuple[int, int]] = field(default_factory=list)
    daily_extrema_size_hits: List[Tuple[int, int]] = field(default_factory=list)
    recurring_large_trade_timestamps: List[Tuple[int, int]] = field(default_factory=list)

    option_family: Optional[str] = None
    strike: Optional[float] = None
    basket_candidate_with: List[str] = field(default_factory=list)
    conversion_feature_columns: List[str] = field(default_factory=list)

    archetype_scores: Dict[str, float] = field(default_factory=dict)
    primary_archetype: str = "unknown"
    secondary_archetypes: List[str] = field(default_factory=list)
    recommended_approaches: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class AnalysisSummary:
    root: Optional[str]
    price_files: List[str]
    trade_files: List[str]
    products: Dict[str, ProductMetrics]
    notes: List[str] = field(default_factory=list)


# ----------------------------- helpers ----------------------------- #

def safe_corr(a: Sequence[float], b: Sequence[float]) -> float:
    a_arr = np.asarray(a, dtype=float)
    b_arr = np.asarray(b, dtype=float)
    mask = np.isfinite(a_arr) & np.isfinite(b_arr)
    if mask.sum() < 3:
        return math.nan
    a_f = a_arr[mask]
    b_f = b_arr[mask]
    if float(np.std(a_f)) == 0.0 or float(np.std(b_f)) == 0.0:
        return math.nan
    return float(np.corrcoef(a_f, b_f)[0, 1])


def round_to_step(value: float, step: int) -> float:
    return round(value / step) * step


def choose_anchor(valid_mid: pd.Series, mean_spread: float) -> Tuple[Optional[float], Optional[int], float]:
    """
    Detect whether the product lives around a stable anchor.
    We search coarse steps because Prosperity anchor products usually center on clean round numbers.
    """
    mids = valid_mid.dropna().astype(float)
    if len(mids) < 50:
        return None, None, math.nan

    candidate_steps = [10, 25, 50, 100, 250, 500, 1000]
    median_mid = float(mids.median())
    best_anchor = None
    best_step = None
    best_strength = -math.inf

    # Strength should reward small deviations relative to spread and overall std.
    spread_scale = max(1.0, float(mean_spread) if math.isfinite(mean_spread) else 1.0)
    overall_std = max(1e-6, float(mids.std(ddof=0)))

    for step in candidate_steps:
        anchor = round_to_step(median_mid, step)
        resid = mids - anchor
        mad = float(np.median(np.abs(resid)))
        resid_std = float(np.std(resid))
        strength = 1.0 / (1.0 + mad / spread_scale + resid_std / overall_std)
        # Prefer coarser anchors slightly, to avoid calling any small oscillation a "10-tick anchor".
        strength *= 1.0 + 0.05 * math.log10(step)
        if strength > best_strength:
            best_strength = strength
            best_anchor = anchor
            best_step = step

    return best_anchor, best_step, float(best_strength)


def linear_trend_metrics(ts: pd.Series, y: pd.Series) -> Dict[str, float]:
    x = ts.astype(float).to_numpy()
    vals = y.astype(float).to_numpy()
    if len(vals) < 5:
        return {"slope": math.nan, "r2": math.nan, "drift": math.nan, "resid_std": math.nan}
    x_mean = x.mean()
    y_mean = vals.mean()
    denom = ((x - x_mean) ** 2).sum()
    if denom == 0:
        return {"slope": math.nan, "r2": math.nan, "drift": math.nan, "resid_std": math.nan}
    slope = float(((x - x_mean) * (vals - y_mean)).sum() / denom)
    intercept = y_mean - slope * x_mean
    y_hat = intercept + slope * x
    ssr = float(((y_hat - y_mean) ** 2).sum())
    sst = float(((vals - y_mean) ** 2).sum())
    r2 = ssr / sst if sst > 0 else math.nan
    drift = float(vals[-1] - vals[0])
    resid_std = float(np.std(vals - y_hat))
    return {"slope": slope, "r2": r2, "drift": drift, "resid_std": resid_std}


def infer_round_and_day_from_name(path: Path) -> Tuple[Optional[int], Optional[int]]:
    name = path.name
    m = re.search(r"round_(\d+)_day_(-?\d+)", name)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def parse_strike_and_option_family(product: str) -> Tuple[Optional[str], Optional[float]]:
    # Example support:
    # VOLCANIC_ROCK_VOUCHER_9500 -> family VOLCANIC_ROCK_VOUCHER, strike 9500
    # COCONUT_COUPON_10000 -> family COCONUT_COUPON, strike 10000
    m = re.match(r"(.+?)_(\d+(?:\.\d+)?)$", product)
    if not m:
        return None, None
    prefix, strike = m.groups()
    return prefix, float(strike)


def stable_mid_from_row(row: pd.Series) -> float:
    bids: List[Tuple[float, float]] = []
    asks: List[Tuple[float, float]] = []
    for level in (1, 2, 3):
        bp = row.get(f"bid_price_{level}")
        bv = row.get(f"bid_volume_{level}")
        ap = row.get(f"ask_price_{level}")
        av = row.get(f"ask_volume_{level}")
        if pd.notna(bp) and pd.notna(bv):
            bids.append((float(bp), float(bv)))
        if pd.notna(ap) and pd.notna(av):
            asks.append((float(ap), float(av)))
    if not bids or not asks:
        return float(row["mid_price"])
    bid_vol = sum(v for _, v in bids)
    ask_vol = sum(v for _, v in asks)
    if bid_vol <= 0 or ask_vol <= 0:
        return float(row["mid_price"])
    bid_price = sum(p * v for p, v in bids) / bid_vol
    ask_price = sum(p * v for p, v in asks) / ask_vol
    popular_mid = (bid_price + ask_price) / 2.0
    wall_bid = max(bids, key=lambda x: (x[1], x[0]))[0]
    wall_ask = min(asks, key=lambda x: (-x[1], x[0]))[0]
    wall_mid = (wall_bid + wall_ask) / 2.0
    return 0.75 * popular_mid + 0.25 * wall_mid


def timestamp_cluster_scores(trades: pd.DataFrame) -> List[Tuple[int, int]]:
    if trades.empty:
        return []
    ts_counts = Counter(int(ts) for ts in trades["timestamp"].dropna().astype(int))
    # Interesting clusters are timestamps that appear repeatedly relative to the number of days.
    return sorted(ts_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]


def daily_extrema_hits(product_trades: pd.DataFrame) -> List[Tuple[int, int]]:
    """
    Count how often a trade size occurs at a new daily high or low trade price.
    Useful for spotting Olivia-style or other extremum bots.
    """
    if product_trades.empty:
        return []
    hits = Counter()
    if "day" not in product_trades.columns:
        # Try to infer pseudo-day from filename-merged metadata if already present;
        # otherwise treat everything as a single day.
        product_trades = product_trades.copy()
        product_trades["day"] = 0

    for _, g in product_trades.groupby("day"):
        g = g.sort_values("timestamp")
        low = math.inf
        high = -math.inf
        for _, row in g.iterrows():
            px = float(row["price"])
            qty = int(abs(row["quantity"]))
            if px < low:
                low = px
                hits[qty] += 1
            if px > high:
                high = px
                hits[qty] += 1
    return hits.most_common(10)


# ----------------------------- profiling ----------------------------- #

def load_price_data(paths: Sequence[Path]) -> pd.DataFrame:
    dfs = []
    for path in paths:
        df = normalize_columns(read_csv_auto(path))
        round_id, day_from_name = infer_round_and_day_from_name(path)
        if "day" not in df.columns and day_from_name is not None:
            df["day"] = day_from_name
        if "round" not in df.columns and round_id is not None:
            df["round"] = round_id
        df["_source_file"] = path.name
        dfs.append(df)
    if not dfs:
        return pd.DataFrame()
    out = pd.concat(dfs, ignore_index=True, sort=False)
    # force numeric where sensible
    for col in out.columns:
        if col.startswith(("bid_price_", "ask_price_", "bid_volume_", "ask_volume_")) or col in {"day", "timestamp", "mid_price", "profit_and_loss"}:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def load_trade_data(paths: Sequence[Path]) -> pd.DataFrame:
    dfs = []
    for path in paths:
        df = normalize_columns(read_csv_auto(path))
        round_id, day_from_name = infer_round_and_day_from_name(path)
        if "day" not in df.columns and day_from_name is not None:
            df["day"] = day_from_name
        if "round" not in df.columns and round_id is not None:
            df["round"] = round_id
        if "product" not in df.columns and "symbol" in df.columns:
            df["product"] = df["symbol"]
        df["_source_file"] = path.name
        dfs.append(df)
    if not dfs:
        return pd.DataFrame()
    out = pd.concat(dfs, ignore_index=True, sort=False)
    for col in ["day", "timestamp", "price", "quantity"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def profile_product(price_df: pd.DataFrame, trade_df: pd.DataFrame, product: str) -> ProductMetrics:
    df = price_df.loc[price_df["product"] == product].copy()
    trades = trade_df.loc[trade_df["product"] == product].copy() if not trade_df.empty else pd.DataFrame()
    metrics = ProductMetrics(product=product)
    metrics.n_price_rows = len(df)
    metrics.n_trade_rows = len(trades)

    if "round" in df.columns:
        metrics.rounds_seen = sorted({int(x) for x in df["round"].dropna().astype(int)})
    if "day" in df.columns:
        metrics.days_seen = sorted({int(x) for x in df["day"].dropna().astype(int)})

    if df.empty:
        metrics.warnings.append("No price rows found for product.")
        return metrics

    # Detect conversion-style extra columns.
    known_cols = {c for c in df.columns if c.startswith(("bid_", "ask_")) or c in {"day", "timestamp", "product", "mid_price", "profit_and_loss", "round", "_source_file"}}
    extra_cols = [c for c in df.columns if c not in known_cols]
    conversion_cols = [c for c in extra_cols if re.search(r"(tariff|fee|sunlight|humidity|shipping|transport|export|import|observation|conversion)", c, flags=re.I)]
    metrics.conversion_feature_columns = sorted(conversion_cols)

    # Valid rows = both sides present and non-crossed.
    has_valid = (
        df.get("bid_price_1").notna()
        & df.get("ask_price_1").notna()
        & (df.get("bid_price_1") < df.get("ask_price_1"))
    )
    valid = df.loc[has_valid].copy()
    metrics.n_valid_rows = len(valid)
    metrics.one_sided_ratio = float(1.0 - len(valid) / max(1, len(df)))

    if valid.empty:
        metrics.warnings.append("No valid two-sided rows. Classification will be weak.")
        return metrics

    valid = valid.sort_values(["day", "timestamp"])
    valid["spread"] = valid["ask_price_1"] - valid["bid_price_1"]
    valid["top_depth"] = valid["bid_volume_1"].fillna(0) + valid["ask_volume_1"].fillna(0)

    metrics.mean_mid = float(valid["mid_price"].mean())
    metrics.mid_std_valid = float(valid["mid_price"].std(ddof=0))
    metrics.mean_spread = float(valid["spread"].mean())
    metrics.avg_top_depth = float(valid["top_depth"].mean())

    # Anchor detection
    anchor_candidate, anchor_step, anchor_strength = choose_anchor(valid["mid_price"], metrics.mean_spread)
    metrics.anchor_candidate = anchor_candidate
    metrics.anchor_step = anchor_step
    metrics.anchor_strength = anchor_strength

    # Daily trend stats
    day_stats = []
    resid_series: List[float] = []
    next_returns: List[float] = []
    for _, g in valid.groupby("day"):
        g = g.sort_values("timestamp")
        stat = linear_trend_metrics(g["timestamp"], g["mid_price"])
        if all(math.isfinite(v) for v in stat.values()):
            day_stats.append(stat)
            # trend residuals for mean-reversion-to-trend
            x = g["timestamp"].to_numpy(dtype=float)
            y = g["mid_price"].to_numpy(dtype=float)
            slope = stat["slope"]
            intercept = y.mean() - slope * x.mean()
            resid = y - (intercept + slope * x)
            nr = np.diff(y, append=np.nan)
            resid_series.extend(resid[:-1].tolist())
            next_returns.extend(nr[:-1].tolist())

    if day_stats:
        day_df = pd.DataFrame(day_stats)
        metrics.mean_slope = float(day_df["slope"].mean())
        metrics.trend_r2 = float(day_df["r2"].mean())
        snr_terms = day_df.apply(
            lambda row: abs(float(row["drift"])) / max(1e-6, float(row["resid_std"])),
            axis=1,
        )
        metrics.trend_snr = float(snr_terms.mean())
        slope_signs = np.sign(day_df["slope"].to_numpy(dtype=float))
        metrics.slope_sign_consistency = float(np.mean(slope_signs == statistics.median(slope_signs)))
    metrics.trend_resid_next_corr = safe_corr(resid_series, next_returns)

    # Rolling deviation + imbalance / micro diagnostics
    valid["rolling_mean_200"] = valid["mid_price"].rolling(200, min_periods=50).mean()
    valid["rolling_dev"] = valid["mid_price"] - valid["rolling_mean_200"]
    valid["next_return"] = valid["mid_price"].shift(-1) - valid["mid_price"]
    metrics.rolling_dev_next_corr = safe_corr(valid["rolling_dev"], valid["next_return"])

    total_depth = valid["top_depth"].replace(0, np.nan)
    valid["imbalance"] = (valid["bid_volume_1"].fillna(0) - valid["ask_volume_1"].fillna(0)) / total_depth
    metrics.imbalance_next_corr = safe_corr(valid["imbalance"], valid["next_return"])

    # Simple trade autocorr on valid price series
    returns = valid["mid_price"].diff().dropna()
    metrics.trade_autocorr_1 = float(returns.autocorr(lag=1)) if len(returns) > 2 else math.nan

    # Trade patterns
    if not trades.empty:
        trades = trades.copy()
        trades["quantity"] = pd.to_numeric(trades["quantity"], errors="coerce")
        qty_counter = Counter(int(abs(q)) for q in trades["quantity"].dropna().astype(int))
        metrics.common_trade_sizes = qty_counter.most_common(10)
        metrics.daily_extrema_size_hits = daily_extrema_hits(trades)
        large_trade_thresh = max(10, int(np.nanquantile(np.abs(trades["quantity"]), 0.75))) if len(trades) else 10
        recurring_ts = timestamp_cluster_scores(trades.loc[np.abs(trades["quantity"]) >= large_trade_thresh])
        metrics.recurring_large_trade_timestamps = recurring_ts

    option_family, strike = parse_strike_and_option_family(product)
    metrics.option_family = option_family
    metrics.strike = strike

    return metrics


# ----------------------------- classification ----------------------------- #

APPROACH_LIBRARY: Dict[str, List[str]] = {
    "anchored_market_maker": [
        "Use Take → Clear → Make every tick.",
        "Build fair from anchor + wall/stable mid; skew quotes by inventory.",
        "Add toxicity / markout-aware quoting and a near-zero-EV recycler.",
    ],
    "local_fair_microstructure": [
        "Use wall/stable mid, microprice, imbalance, and short-horizon local fair.",
        "Quote conditionally on book health; avoid trusting sparse visible touch.",
        "Research passive-fill markout and side-specific reentry.",
    ],
    "trending_drift_carry": [
        "Use a schedule/catch-up carry engine, not plain market making.",
        "Track drift line, buy cheap dips vs expected drift, avoid chasing rich moves.",
        "Keep a protected core position and trim only late / clearly rich states.",
    ],
    "mean_reverting_ou": [
        "Fit an Ornstein–Uhlenbeck style fair: theta, mu, sigma from history.",
        "Fade deviations from fair, preferably using zero-cross exits.",
        "Do not regress on raw prices; use deviations / returns instead.",
    ],
    "slow_random_walk": [
        "Avoid raw mid; use wall mid, maker-mid, or filtered VWAP touch.",
        "Look for stale market-makers and short-horizon filtered fair.",
        "Keep thresholds simple and robust; dynamic z-score windows overfit easily.",
    ],
    "basket_or_etf_candidate": [
        "Estimate synthetic fair from components, but trade only the basket first.",
        "Use fixed thresholds before trying dynamic z-score normalization.",
        "Start with a partial hedge ratio (~50%) if hedging is truly needed.",
    ],
    "option_family": [
        "Fit implied-vol smile across strikes; Black–Scholes with smile-adjusted IV.",
        "Research IV mean-reversion, cross-voucher spreads, and cautious delta hedging.",
        "Do not use flat volatility unless validated very strongly.",
    ],
    "conversion_candidate": [
        "Immediately test import/export arbitrage, fees, and storage-cost breakevens.",
        "Search for a smart taker before paying spread with naive two-sided arb.",
        "Respect per-tick conversion limits and inventory storage bleed.",
    ],
    "bot_driven_overlay": [
        "Cluster repeated trade sizes and timestamp patterns; build a confidence-based detector.",
        "Check daily-extrema trades for Olivia-like or other informed-bot signatures.",
        "Use bot behavior as an overlay on top of the base product model.",
    ],
    "unknown": [
        "Start with profiling and simple robust baselines before optimizing.",
        "Submit a safe baseline that ignores the product if confidence is low.",
        "Stage complexity: simple → diagnose → targeted fix → optimize last.",
    ],
}


def classify_product(metrics: ProductMetrics) -> None:
    scores: Dict[str, float] = defaultdict(float)

    # Structural family detection
    if metrics.conversion_feature_columns:
        scores["conversion_candidate"] += 4.0

    if metrics.option_family is not None:
        scores["option_family"] += 4.0

    # Anchored market maker
    if math.isfinite(metrics.anchor_strength):
        scores["anchored_market_maker"] += 3.0 * metrics.anchor_strength
    if math.isfinite(metrics.trend_snr) and metrics.trend_snr < 8.0:
        scores["anchored_market_maker"] += 1.0
    if math.isfinite(metrics.mean_spread) and metrics.mean_spread > 0:
        scores["anchored_market_maker"] += 0.5

    # Trend / carry
    if math.isfinite(metrics.trend_snr):
        scores["trending_drift_carry"] += min(4.0, metrics.trend_snr / 40.0)
    if math.isfinite(metrics.trend_r2):
        scores["trending_drift_carry"] += min(3.0, metrics.trend_r2 * 3.0)
    if math.isfinite(metrics.slope_sign_consistency) and metrics.slope_sign_consistency > 0.66:
        scores["trending_drift_carry"] += 1.0

    # Mean reversion
    if math.isfinite(metrics.trend_resid_next_corr):
        scores["mean_reverting_ou"] += max(0.0, -metrics.trend_resid_next_corr * 3.0)
    if math.isfinite(metrics.rolling_dev_next_corr):
        scores["mean_reverting_ou"] += max(0.0, -metrics.rolling_dev_next_corr * 2.0)
    if math.isfinite(metrics.trend_snr) and metrics.trend_snr < 20.0:
        scores["mean_reverting_ou"] += 0.5

    # Slow random walk vs local microstructure
    if math.isfinite(metrics.imbalance_next_corr):
        scores["local_fair_microstructure"] += max(0.0, abs(metrics.imbalance_next_corr) * 4.0)
    if math.isfinite(metrics.one_sided_ratio) and metrics.one_sided_ratio > 0.03:
        scores["local_fair_microstructure"] += 0.5
    if math.isfinite(metrics.anchor_strength):
        scores["slow_random_walk"] += max(0.0, 2.0 * (1.0 - metrics.anchor_strength))
    if math.isfinite(metrics.trend_snr) and 3.0 <= metrics.trend_snr <= 30.0:
        scores["slow_random_walk"] += 0.8
    if math.isfinite(metrics.trend_r2) and metrics.trend_r2 < 0.6:
        scores["slow_random_walk"] += 0.7

    # Bot-driven overlay
    if metrics.common_trade_sizes:
        top_qty, top_count = metrics.common_trade_sizes[0]
        if top_count >= 10:
            scores["bot_driven_overlay"] += 0.8
    if metrics.daily_extrema_size_hits:
        top_qty, top_hits = metrics.daily_extrema_size_hits[0]
        if top_hits >= max(4, len(metrics.days_seen)):
            scores["bot_driven_overlay"] += 1.6
    if metrics.recurring_large_trade_timestamps:
        top_ts, top_freq = metrics.recurring_large_trade_timestamps[0]
        if top_freq >= max(2, len(metrics.days_seen)):
            scores["bot_driven_overlay"] += 0.8

    # Basket candidate (very light heuristic)
    if metrics.basket_candidate_with:
        scores["basket_or_etf_candidate"] += 2.0

    # Resolve some contradictory states.
    # Very strong trend should dominate OU/anchored labels.
    if math.isfinite(metrics.trend_r2) and metrics.trend_r2 > 0.95 and math.isfinite(metrics.trend_snr) and metrics.trend_snr > 50:
        scores["trending_drift_carry"] += 3.0
        scores["mean_reverting_ou"] *= 0.5
        scores["anchored_market_maker"] *= 0.5

    # Strong anchor + low trend should favor anchored local MM over OU.
    if math.isfinite(metrics.anchor_strength) and metrics.anchor_strength > 0.7 and math.isfinite(metrics.trend_r2) and metrics.trend_r2 < 0.2:
        scores["anchored_market_maker"] += 2.0
        scores["mean_reverting_ou"] *= 0.8

    if not scores:
        scores["unknown"] = 1.0

    metrics.archetype_scores = {k: round(float(v), 4) for k, v in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))}
    sorted_labels = [k for k, _ in sorted(metrics.archetype_scores.items(), key=lambda kv: (-kv[1], kv[0]))]
    metrics.primary_archetype = sorted_labels[0]
    metrics.secondary_archetypes = sorted_labels[1:4]

    # Approaches = union of top two meaningful archetypes.
    advice: List[str] = []
    for label in [metrics.primary_archetype] + metrics.secondary_archetypes[:1]:
        for line in APPROACH_LIBRARY.get(label, APPROACH_LIBRARY["unknown"]):
            if line not in advice:
                advice.append(line)
    # Universal checklist from Competitive Intel
    universal = [
        "Profile first; do not tune on raw website randomness.",
        "Prefer robust plateaus over sharp parameter peaks.",
        "Keep state in traderData / serialized memory, not class variables.",
    ]
    for line in universal:
        if line not in advice:
            advice.append(line)
    metrics.recommended_approaches = advice

    # Warnings
    if metrics.primary_archetype == "trending_drift_carry" and math.isfinite(metrics.one_sided_ratio) and metrics.one_sided_ratio > 0.1:
        metrics.warnings.append("Book is often one-sided; use vacuum/last-good-fair handling for execution, not just touch prices.")
    if metrics.primary_archetype == "anchored_market_maker" and math.isfinite(metrics.one_sided_ratio) and metrics.one_sided_ratio > 0.08:
        metrics.warnings.append("Quote thinning / sparse-book risk is non-trivial; guard fair with wall/median/last-good variants.")
    if metrics.primary_archetype == "option_family":
        metrics.warnings.append("Do not use flat-vol Black–Scholes without validating an IV smile.")
    if metrics.primary_archetype == "conversion_candidate":
        metrics.warnings.append("Storage/holding costs can erase apparent spread profit very quickly.")
    if "bot_driven_overlay" in metrics.archetype_scores and metrics.archetype_scores["bot_driven_overlay"] >= 1.5:
        metrics.warnings.append("Repeated lot-size / extrema patterns detected; consider an Olivia-/bot-style detector overlay.")


# ----------------------------- cross-product analysis ----------------------------- #

def build_product_cross_signals(price_df: pd.DataFrame, products: Dict[str, ProductMetrics]) -> None:
    if price_df.empty or len(products) < 2:
        return

    valid = price_df.loc[
        price_df["bid_price_1"].notna()
        & price_df["ask_price_1"].notna()
        & (price_df["bid_price_1"] < price_df["ask_price_1"])
    ].copy()
    if valid.empty:
        return

    pivot = valid.pivot_table(index=["round", "day", "timestamp"], columns="product", values="mid_price", aggfunc="last").sort_index()
    rets = pivot.diff()

    prod_names = list(products.keys())
    corr = rets.corr(min_periods=100)

    # Very light basket candidate: if one product has strong linear correlation to 2+ others,
    # flag it for manual basket investigation.
    for p in prod_names:
        if p not in corr.columns:
            continue
        related = [q for q in prod_names if q != p and q in corr.columns and pd.notna(corr.loc[p, q]) and abs(float(corr.loc[p, q])) > 0.85]
        if len(related) >= 2:
            products[p].basket_candidate_with = related[:4]

    # Option family grouping by strike suffix
    families: Dict[str, List[str]] = defaultdict(list)
    for p, m in products.items():
        if m.option_family is not None:
            families[m.option_family].append(p)
    for family, members in families.items():
        if len(members) < 2:
            # Single strike-like symbol could be a false match.
            for p in members:
                products[p].option_family = None
                products[p].strike = None


# ----------------------------- reporting ----------------------------- #

def format_float(x: Optional[float], digits: int = 4) -> str:
    if x is None or not math.isfinite(float(x)):
        return "n/a"
    return f"{float(x):.{digits}f}"


def render_markdown(summary: AnalysisSummary, intel_path: Optional[Path]) -> str:
    lines: List[str] = []
    lines.append("# Capsule Product Diagnosis Report")
    lines.append("")
    if summary.root:
        lines.append(f"- Root scanned: `{summary.root}`")
    lines.append(f"- Price files: {len(summary.price_files)}")
    lines.append(f"- Trade files: {len(summary.trade_files)}")
    if intel_path is not None:
        lines.append(f"- Competitive intel reference: `{intel_path}`")
    lines.append("")
    lines.append("## Product Table")
    lines.append("")
    lines.append("| Product | Primary Archetype | Secondary | Mean Mid | Mean Spread | Trend SNR | Trend R² | Anchor | One-Sided |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|")
    for product, m in summary.products.items():
        second = ", ".join(m.secondary_archetypes[:2]) if m.secondary_archetypes else "n/a"
        anchor_text = f"{m.anchor_candidate:g} ({m.anchor_step})" if m.anchor_candidate is not None and m.anchor_step is not None else "n/a"
        lines.append(
            f"| {product} | {m.primary_archetype} | {second} | {format_float(m.mean_mid,1)} | {format_float(m.mean_spread,2)} | {format_float(m.trend_snr,2)} | {format_float(m.trend_r2,3)} | {anchor_text} | {format_float(m.one_sided_ratio,3)} |"
        )

    for product, m in summary.products.items():
        lines.append("")
        lines.append(f"## {product}")
        lines.append("")
        lines.append("### Classification")
        lines.append("")
        lines.append(f"- Primary archetype: **{m.primary_archetype}**")
        if m.secondary_archetypes:
            lines.append(f"- Secondary archetypes: {', '.join(m.secondary_archetypes)}")
        lines.append(f"- Rounds seen: {m.rounds_seen or ['n/a']}")
        lines.append(f"- Days seen: {m.days_seen or ['n/a']}")
        lines.append("")
        lines.append("### Metrics")
        lines.append("")
        lines.append(f"- Valid rows / total rows: **{m.n_valid_rows} / {m.n_price_rows}**")
        lines.append(f"- Trade rows: **{m.n_trade_rows}**")
        lines.append(f"- Mean mid: **{format_float(m.mean_mid, 2)}**")
        lines.append(f"- Mid std on valid rows: **{format_float(m.mid_std_valid, 3)}**")
        lines.append(f"- Mean spread: **{format_float(m.mean_spread, 3)}**")
        lines.append(f"- Avg top-of-book depth: **{format_float(m.avg_top_depth, 2)}**")
        lines.append(f"- One-sided row ratio: **{format_float(m.one_sided_ratio, 3)}**")
        lines.append(f"- Trend SNR: **{format_float(m.trend_snr, 3)}**")
        lines.append(f"- Trend R²: **{format_float(m.trend_r2, 4)}**")
        lines.append(f"- Mean daily slope: **{format_float(m.mean_slope, 8)}**")
        lines.append(f"- Trend-residual vs next-return corr: **{format_float(m.trend_resid_next_corr, 3)}**")
        lines.append(f"- Rolling-deviation vs next-return corr: **{format_float(m.rolling_dev_next_corr, 3)}**")
        lines.append(f"- Imbalance vs next-return corr: **{format_float(m.imbalance_next_corr, 3)}**")
        if m.anchor_candidate is not None:
            lines.append(f"- Anchor candidate: **{m.anchor_candidate:g}** (step {m.anchor_step}, strength {format_float(m.anchor_strength, 3)})")
        if m.option_family:
            lines.append(f"- Option family: **{m.option_family}**, strike **{m.strike:g}**")
        if m.basket_candidate_with:
            lines.append(f"- Basket-like correlation cluster: **{', '.join(m.basket_candidate_with)}**")
        if m.conversion_feature_columns:
            lines.append(f"- Conversion-style extra columns: **{', '.join(m.conversion_feature_columns)}**")

        if m.common_trade_sizes:
            lines.append("")
            lines.append("### Trade Pattern Clues")
            lines.append("")
            lines.append(f"- Common trade sizes: {m.common_trade_sizes[:6]}")
            if m.daily_extrema_size_hits:
                lines.append(f"- Sizes often hitting new daily highs/lows: {m.daily_extrema_size_hits[:6]}")
            if m.recurring_large_trade_timestamps:
                lines.append(f"- Recurring large-trade timestamps: {m.recurring_large_trade_timestamps[:8]}")

        lines.append("")
        lines.append("### Strategy Directions")
        lines.append("")
        for line in m.recommended_approaches:
            lines.append(f"- {line}")

        if m.warnings:
            lines.append("")
            lines.append("### Warnings")
            lines.append("")
            for warning in m.warnings:
                lines.append(f"- {warning}")

        lines.append("")
        lines.append("### Archetype Scores")
        lines.append("")
        for k, v in m.archetype_scores.items():
            lines.append(f"- `{k}`: {v:.3f}")

    if summary.notes:
        lines.append("")
        lines.append("## Notes")
        lines.append("")
        for note in summary.notes:
            lines.append(f"- {note}")

    return "\n".join(lines) + "\n"


# ----------------------------- top-level orchestrator ----------------------------- #

def analyze_capsule(
    price_files: Sequence[Path],
    trade_files: Sequence[Path],
    root: Optional[Path],
    intel_path: Optional[Path],
) -> AnalysisSummary:
    price_df = load_price_data(price_files)
    trade_df = load_trade_data(trade_files)

    products: Dict[str, ProductMetrics] = {}
    product_names = sorted(set(price_df.get("product", pd.Series(dtype=str)).dropna().astype(str)))
    if not product_names and not trade_df.empty:
        product_names = sorted(set(trade_df.get("product", pd.Series(dtype=str)).dropna().astype(str)))

    for product in product_names:
        products[product] = profile_product(price_df, trade_df, product)

    build_product_cross_signals(price_df, products)

    for metrics in products.values():
        classify_product(metrics)

    notes: List[str] = []
    if intel_path is not None and intel_path.exists():
        notes.append(
            "Advice rules were selected to align with Competitive Intelligence themes: "
            "Take → Clear → Make, wall/stable mid over raw mid, O-U for mean reversion, "
            "Black–Scholes + smile for option families, and bot-detection overlays."
        )

    if not products:
        notes.append("No products detected. Check CSV separators and column names.")

    return AnalysisSummary(
        root=str(root) if root is not None else None,
        price_files=[str(p) for p in price_files],
        trade_files=[str(p) for p in trade_files],
        products=products,
        notes=notes,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profile Prosperity data-capsule CSVs and classify product archetypes.")
    parser.add_argument("--root", type=Path, default=DEFAULT_DATA_ROOT, help="Directory to scan for price/trade CSVs.")
    parser.add_argument("--prices", type=Path, nargs="*", default=None, help="Explicit price CSV files.")
    parser.add_argument("--trades", type=Path, nargs="*", default=None, help="Explicit trade CSV files.")
    parser.add_argument("--intel-md", type=Path, default=DEFAULT_INTEL_PATH, help="Optional Competitive Intelligence markdown file.")
    parser.add_argument("--out-md", type=Path, default=Path("capsule_product_diagnosis_report.md"), help="Markdown output path.")
    parser.add_argument("--out-json", type=Path, default=Path("capsule_product_diagnosis_summary.json"), help="JSON output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    price_files, trade_files = discover_files(args.root, args.prices, args.trades)

    if not price_files:
        raise SystemExit("No price CSV files found. Pass --root or --prices.")
    summary = analyze_capsule(price_files, trade_files, args.root, args.intel_md)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(summary, args.intel_md), encoding="utf-8")
    payload = {
        "generated_at": datetime.now().isoformat(),
        "root": summary.root,
        "intel_md": str(args.intel_md) if args.intel_md is not None else None,
        "price_files": summary.price_files,
        "trade_files": summary.trade_files,
        "products": {k: asdict(v) for k, v in summary.products.items()},
        "notes": summary.notes,
    }
    args.out_json.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print(f"Wrote markdown report to {args.out_md}")
    print(f"Wrote JSON summary to {args.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
