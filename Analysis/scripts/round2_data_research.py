from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "Data" / "ROUND_2"
OUTPUT_DIR = ROOT / "Analysis" / "output" / "round2_data_research"

PEPPER = "INTARIAN_PEPPER_ROOT"
ASH = "ASH_COATED_OSMIUM"
DAYS = (-1, 0, 1)


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def sign(value: float, eps: float = 1e-9) -> int:
    if value > eps:
        return 1
    if value < -eps:
        return -1
    return 0


def load_prices() -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    for day in DAYS:
        frame = pd.read_csv(DATA_DIR / f"prices_round_2_day_{day}.csv", sep=";")
        frame["day"] = day
        frames.append(frame)
    prices = pd.concat(frames, ignore_index=True)
    return prices


def load_trades() -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    for day in DAYS:
        frame = pd.read_csv(DATA_DIR / f"trades_round_2_day_{day}.csv", sep=";")
        frame["day"] = day
        frames.append(frame)
    trades = pd.concat(frames, ignore_index=True)
    return trades


def prepare_prices(prices: pd.DataFrame) -> pd.DataFrame:
    df = prices.copy()
    numeric_cols = [
        "timestamp",
        "bid_price_1",
        "bid_volume_1",
        "bid_price_2",
        "bid_volume_2",
        "bid_price_3",
        "bid_volume_3",
        "ask_price_1",
        "ask_volume_1",
        "ask_price_2",
        "ask_volume_2",
        "ask_price_3",
        "ask_volume_3",
        "mid_price",
        "profit_and_loss",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["progress"] = df["timestamp"] / df["timestamp"].max()
    return df.sort_values(["product", "day", "timestamp"]).reset_index(drop=True)


def stable_mid(frame: pd.DataFrame) -> pd.Series:
    bid_prices = frame[["bid_price_1", "bid_price_2", "bid_price_3"]].to_numpy(dtype=float)
    bid_vols = frame[["bid_volume_1", "bid_volume_2", "bid_volume_3"]].fillna(0.0).to_numpy(dtype=float)
    ask_prices = frame[["ask_price_1", "ask_price_2", "ask_price_3"]].to_numpy(dtype=float)
    ask_vols = frame[["ask_volume_1", "ask_volume_2", "ask_volume_3"]].fillna(0.0).to_numpy(dtype=float)

    bid_vsum = bid_vols.sum(axis=1)
    ask_vsum = ask_vols.sum(axis=1)
    bid_pop = np.divide((np.nan_to_num(bid_prices) * bid_vols).sum(axis=1), bid_vsum, out=np.full(len(frame), np.nan), where=bid_vsum > 0)
    ask_pop = np.divide((np.nan_to_num(ask_prices) * ask_vols).sum(axis=1), ask_vsum, out=np.full(len(frame), np.nan), where=ask_vsum > 0)
    popular_mid = (bid_pop + ask_pop) / 2.0

    bid_candidates = np.where(np.isnan(bid_prices), -np.inf, bid_vols)
    ask_candidates = np.where(np.isnan(ask_prices), -np.inf, ask_vols)
    bid_ix = bid_candidates.argmax(axis=1)
    ask_ix = ask_candidates.argmax(axis=1)
    wall_bid = bid_prices[np.arange(len(frame)), bid_ix]
    wall_ask = ask_prices[np.arange(len(frame)), ask_ix]
    wall_mid = (wall_bid + wall_ask) / 2.0

    out = 0.75 * popular_mid + 0.25 * wall_mid
    return pd.Series(out, index=frame.index)


def deep_micro_and_imbalance(frame: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    bid_prices = frame[["bid_price_1", "bid_price_2", "bid_price_3"]].to_numpy(dtype=float)
    bid_vols = frame[["bid_volume_1", "bid_volume_2", "bid_volume_3"]].fillna(0.0).to_numpy(dtype=float)
    ask_prices = frame[["ask_price_1", "ask_price_2", "ask_price_3"]].to_numpy(dtype=float)
    ask_vols = frame[["ask_volume_1", "ask_volume_2", "ask_volume_3"]].fillna(0.0).to_numpy(dtype=float)

    bid_vsum = bid_vols.sum(axis=1)
    ask_vsum = ask_vols.sum(axis=1)
    bid_vwap = np.divide((np.nan_to_num(bid_prices) * bid_vols).sum(axis=1), bid_vsum, out=np.full(len(frame), np.nan), where=bid_vsum > 0)
    ask_vwap = np.divide((np.nan_to_num(ask_prices) * ask_vols).sum(axis=1), ask_vsum, out=np.full(len(frame), np.nan), where=ask_vsum > 0)
    deep_micro = np.divide(
        ask_vwap * bid_vsum + bid_vwap * ask_vsum,
        bid_vsum + ask_vsum,
        out=np.full(len(frame), np.nan),
        where=(bid_vsum + ask_vsum) > 0,
    )
    deep_imb = np.divide(
        bid_vsum - ask_vsum,
        bid_vsum + ask_vsum,
        out=np.zeros(len(frame)),
        where=(bid_vsum + ask_vsum) > 0,
    )
    return pd.Series(deep_micro, index=frame.index), pd.Series(deep_imb, index=frame.index)


def infer_trade_flow(trades: pd.DataFrame, product_prices: pd.DataFrame, symbol_col: str) -> pd.DataFrame:
    flow_rows: List[Tuple[int, int, float]] = []
    for day in DAYS:
        day_prices = product_prices[product_prices["day"] == day].set_index("timestamp")
        day_trades = trades[(trades["day"] == day) & (trades[symbol_col] == ASH)]
        for row in day_trades.itertuples(index=False):
            ts = int(row.timestamp)
            if ts not in day_prices.index:
                continue
            px_row = day_prices.loc[ts]
            if isinstance(px_row, pd.DataFrame):
                px_row = px_row.iloc[0]
            price = float(row.price)
            qty = abs(float(row.quantity))
            trade_sign = 0.0
            best_ask = px_row["ask_price_1"]
            best_bid = px_row["bid_price_1"]
            mid = px_row["mid_price"]
            if pd.notna(best_ask) and price >= best_ask:
                trade_sign = 1.0
            elif pd.notna(best_bid) and price <= best_bid:
                trade_sign = -1.0
            elif pd.notna(mid):
                trade_sign = float(sign(price - mid, 0.05))
            flow_rows.append((day, ts, trade_sign * qty))
    out = pd.DataFrame(flow_rows, columns=["day", "timestamp", "signed_qty"])
    if out.empty:
        return pd.DataFrame(columns=["day", "timestamp", "trade_flow"])
    out = out.groupby(["day", "timestamp"], as_index=False)["signed_qty"].sum()
    out["trade_flow"] = out["signed_qty"].clip(-20.0, 20.0) / 20.0
    return out[["day", "timestamp", "trade_flow"]]


def add_future_columns(frame: pd.DataFrame, horizons: List[int]) -> pd.DataFrame:
    out = frame.copy()
    grouped = out.groupby("day", sort=False)
    for h in horizons:
        out[f"future_mid_{h}"] = grouped["mid_price"].shift(-h)
        out[f"future_ret_{h}"] = out[f"future_mid_{h}"] - out["mid_price"]
    out["next_mid"] = grouped["mid_price"].shift(-1)
    out["next_ret"] = out["next_mid"] - out["mid_price"]
    out["next_valid"] = grouped["valid"].shift(-1)
    return out


def analyze_pepper(prices: pd.DataFrame, output_dir: Path) -> Dict[str, object]:
    pepper_all = prices[prices["product"] == PEPPER].copy()
    pepper_all["valid"] = pepper_all["bid_price_1"].notna() & pepper_all["ask_price_1"].notna() & (pepper_all["bid_price_1"] < pepper_all["ask_price_1"])
    invalid_rows = int((~pepper_all["valid"]).sum())
    pepper = pepper_all[pepper_all["valid"]].copy()
    pepper = add_future_columns(pepper, [10, 25])

    per_day = []
    pepper["trend"] = np.nan
    for day, part in pepper.groupby("day", sort=False):
        x = part["timestamp"].to_numpy(dtype=float)
        y = part["mid_price"].to_numpy(dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        pepper.loc[part.index, "trend"] = intercept + slope * x
        per_day.append({"day": int(day), "slope_per_ts": float(slope), "start_mid": float(y[0]), "end_mid": float(y[-1])})

    pepper["residual"] = pepper["mid_price"] - pepper["trend"]
    day_std = pepper.groupby("day")["residual"].transform(lambda s: s.std(ddof=0) if s.std(ddof=0) > 0 else 1.0)
    pepper["residual_z"] = pepper["residual"] / day_std
    pepper["imb_sign"] = np.sign(pepper["bid_volume_1"].fillna(0) - pepper["ask_volume_1"].fillna(0))

    valid_future = pepper.dropna(subset=["future_ret_25"]).copy()
    valid_future["residual_bin"] = pd.cut(
        valid_future["residual_z"],
        bins=[-np.inf, -2.0, -1.0, -0.5, 0.5, 1.0, 2.0, np.inf],
        labels=["<=-2", "(-2,-1]", "(-1,-0.5]", "(-0.5,0.5]", "(0.5,1]", "(1,2]", ">2"],
    )
    residual_stats = (
        valid_future.groupby("residual_bin", observed=False)
        .agg(
            count=("future_ret_25", "size"),
            mean_ret_25=("future_ret_25", "mean"),
            hit_rate_25=("future_ret_25", lambda s: float((s > 0).mean())),
        )
        .reset_index()
    )

    cheap_mask = (
        (valid_future["residual_z"] <= -1.0)
        & (valid_future["progress"] <= 0.65)
        & valid_future["valid"]
    )
    cheap_stats = {
        "count": int(cheap_mask.sum()),
        "mean_ret_10": float(valid_future.loc[cheap_mask, "future_ret_10"].mean()),
        "mean_ret_25": float(valid_future.loc[cheap_mask, "future_ret_25"].mean()),
        "hit_rate_25": float((valid_future.loc[cheap_mask, "future_ret_25"] > 0).mean()),
    }

    late_mask = valid_future["progress"] >= 0.85
    late_stats = {
        "count": int(late_mask.sum()),
        "mean_ret_25": float(valid_future.loc[late_mask, "future_ret_25"].mean()),
        "hit_rate_25": float((valid_future.loc[late_mask, "future_ret_25"] > 0).mean()),
    }

    fig, ax = plt.subplots(figsize=(10, 5))
    for day, part in pepper.groupby("day", sort=False):
        ax.plot(part["progress"], part["mid_price"], alpha=0.45, label=f"day {day}")
        ax.plot(part["progress"], part["trend"], linestyle="--", alpha=0.9)
    ax.set_title("Pepper Mid-Price Path And Linear Drift Fit")
    ax.set_xlabel("Session Progress")
    ax.set_ylabel("Mid Price")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(output_dir / "pepper_mid_and_trend.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(residual_stats["residual_bin"].astype(str), residual_stats["mean_ret_25"], color="#2a9d8f")
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_title("Pepper 25-Bar Forward Return By Residual Z-Score")
    ax.set_xlabel("Residual Z-Score Bin")
    ax.set_ylabel("Mean 25-Bar Forward Return")
    fig.tight_layout()
    fig.savefig(output_dir / "pepper_residual_bins.png", dpi=180)
    plt.close(fig)

    return {
        "invalid_rows": invalid_rows,
        "per_day_trend": per_day,
        "cheap_accum_stats": cheap_stats,
        "late_session_stats": late_stats,
        "residual_stats": residual_stats.to_dict(orient="records"),
    }


def analyze_ash(prices: pd.DataFrame, trades: pd.DataFrame, output_dir: Path) -> Dict[str, object]:
    ash = prices[prices["product"] == ASH].copy()
    ash["has_bid"] = ash["bid_price_1"].notna()
    ash["has_ask"] = ash["ask_price_1"].notna()
    ash["valid"] = ash["has_bid"] & ash["has_ask"] & (ash["bid_price_1"] < ash["ask_price_1"])
    ash["spread"] = ash["ask_price_1"] - ash["bid_price_1"]
    total = ash["bid_volume_1"].fillna(0.0) + ash["ask_volume_1"].fillna(0.0)
    ash["imbalance"] = np.where(total > 0, (ash["bid_volume_1"].fillna(0.0) - ash["ask_volume_1"].fillna(0.0)) / total, 0.0)
    ash["micro"] = np.where(
        total > 0,
        (ash["ask_price_1"].fillna(ash["mid_price"]) * ash["bid_volume_1"].fillna(0.0) + ash["bid_price_1"].fillna(ash["mid_price"]) * ash["ask_volume_1"].fillna(0.0)) / total,
        ash["mid_price"],
    )
    ash["stable_mid"] = stable_mid(ash)
    ash["deep_micro"], ash["deep_imbalance"] = deep_micro_and_imbalance(ash)
    ash["stable_gap"] = ash["stable_mid"] - ash["mid_price"]
    ash["micro_gap"] = ash["micro"] - ash["mid_price"]
    ash["deep_micro_gap"] = ash["deep_micro"] - ash["mid_price"]
    half_spread = ash["spread"].clip(lower=6.0, upper=10.0) / 2.0
    depth = (ash["bid_volume_1"].fillna(0.0) + ash["ask_volume_1"].fillna(0.0)).clip(lower=8.0)
    ash["imbalance_signal"] = (
        half_spread * ash["imbalance"]
        + (26.0 / depth) * ash["imbalance"]
        + 0.28 * half_spread * ash["deep_imbalance"]
    )
    ash = add_future_columns(ash, [1, 5, 10])
    ash = ash.merge(infer_trade_flow(trades, ash, "symbol"), on=["day", "timestamp"], how="left")
    ash["trade_flow"] = ash["trade_flow"].fillna(0.0)

    valid = ash[ash["valid"] & ash["next_valid"].fillna(False)].copy()
    valid["next_sign"] = np.sign(valid["next_ret"])
    valid["stable_sign"] = valid["stable_gap"].apply(lambda x: sign(x, 0.20))
    valid["imbalance_sign"] = valid["imbalance_signal"].apply(lambda x: sign(x, 0.12))
    valid["trade_sign"] = valid["trade_flow"].apply(lambda x: sign(x, 0.05))
    valid["agree"] = (valid["stable_sign"] != 0) & (valid["stable_sign"] == valid["imbalance_sign"]) & (valid["stable_gap"].abs() >= 0.50)
    valid["disagree"] = (valid["stable_sign"] != 0) & (valid["imbalance_sign"] != 0) & (valid["stable_sign"] != valid["imbalance_sign"]) & (valid["stable_gap"].abs() >= 0.75)

    corr = {}
    for col in ["stable_gap", "micro_gap", "deep_micro_gap", "imbalance_signal"]:
        corr[col] = float(valid[[col, "next_ret"]].corr().iloc[0, 1])

    agree_05 = valid["agree"] & (valid["stable_gap"].abs() >= 0.50)
    agree_10 = valid["agree"] & (valid["stable_gap"].abs() >= 1.00)
    disagree = valid["disagree"]
    trade_align = (valid["trade_sign"] != 0) & (valid["trade_sign"] == valid["imbalance_sign"])
    trade_oppose = (valid["trade_sign"] != 0) & (valid["trade_sign"] == -valid["imbalance_sign"])

    agreement_stats = {
        "agree_05_count": int(agree_05.sum()),
        "agree_05_hit_rate": float((valid.loc[agree_05, "next_sign"] == valid.loc[agree_05, "imbalance_sign"]).mean()),
        "agree_10_count": int(agree_10.sum()),
        "agree_10_hit_rate": float((valid.loc[agree_10, "next_sign"] == valid.loc[agree_10, "imbalance_sign"]).mean()),
        "disagree_count": int(disagree.sum()),
        "disagree_follow_imbalance": float((valid.loc[disagree, "next_sign"] == valid.loc[disagree, "imbalance_sign"]).mean()),
        "disagree_follow_stable": float((valid.loc[disagree, "next_sign"] == valid.loc[disagree, "stable_sign"]).mean()),
        "trade_align_count": int(trade_align.sum()),
        "trade_align_hit_rate": float((valid.loc[trade_align, "next_sign"] == valid.loc[trade_align, "imbalance_sign"]).mean()),
        "trade_oppose_count": int(trade_oppose.sum()),
        "trade_oppose_hit_rate": float((valid.loc[trade_oppose, "next_sign"] == valid.loc[trade_oppose, "trade_sign"]).mean()),
    }

    tight = valid["spread"] <= 16.0
    tight_micro = tight & (valid["micro_gap"].abs() > 1e-9)
    tight_micro_hit = float((valid.loc[tight_micro, "next_sign"] == np.sign(valid.loc[tight_micro, "micro_gap"])).mean())

    valid["conviction"] = 0.0
    valid.loc[valid["agree"], "conviction"] += 0.35
    valid.loc[valid["agree"] & (valid["stable_gap"].abs() >= 1.0), "conviction"] += 0.25
    valid.loc[valid["agree"] & (valid["stable_gap"].abs() >= 1.25), "conviction"] += 0.15
    valid.loc[(valid["trade_sign"] != 0) & (valid["trade_sign"] == valid["imbalance_sign"]), "conviction"] += 0.15
    valid["quote_signal"] = (
        0.90 * valid["imbalance_signal"] + 0.35 * valid["micro_gap"] + 0.45 * valid["deep_micro_gap"]
    ).clip(-2.0, 2.0) * 0.38

    access_buy = (
        valid["quote_signal"].ge(0.22)
        & valid["conviction"].ge(0.40)
        & valid["stable_gap"].ge(0.65)
        & valid["trade_sign"].ge(0)
    )
    access_sell = (
        valid["quote_signal"].le(-0.22)
        & valid["conviction"].ge(0.40)
        & valid["stable_gap"].le(-0.65)
        & valid["trade_sign"].le(0)
    )

    access_rows = []
    for level in (1, 2, 3):
        ask_col = f"ask_price_{level}"
        bid_col = f"bid_price_{level}"
        buy_markout = (valid["future_mid_5"] - valid[ask_col]).where(access_buy & valid[ask_col].notna())
        sell_markout = (valid[bid_col] - valid["future_mid_5"]).where(access_sell & valid[bid_col].notna())
        access_rows.append(
            {
                "level": level,
                "buy_count": int(buy_markout.notna().sum()),
                "buy_markout_5": float(buy_markout.mean()),
                "sell_count": int(sell_markout.notna().sum()),
                "sell_markout_5": float(sell_markout.mean()),
            }
        )

    vacuum = ash[(~ash["valid"]) & (ash["has_bid"] ^ ash["has_ask"])].copy()
    next_valid_mid_rows = []
    for day, part in ash.groupby("day", sort=False):
        part = part.sort_values("timestamp").copy()
        next_valid_mid = np.full(len(part), np.nan)
        carry = np.nan
        for i in range(len(part) - 1, -1, -1):
            if bool(part.iloc[i]["valid"]):
                carry = float(part.iloc[i]["mid_price"])
            next_valid_mid[i] = carry
        part["next_valid_mid"] = next_valid_mid
        next_valid_mid_rows.append(part[["day", "timestamp", "next_valid_mid"]])
    next_valid_mids = pd.concat(next_valid_mid_rows, ignore_index=True)
    vacuum = vacuum.merge(next_valid_mids, on=["day", "timestamp"], how="left")
    vacuum["vacuum_side"] = np.where(vacuum["has_bid"], "bid_only", "ask_only")
    vacuum["refill_move"] = vacuum["next_valid_mid"] - vacuum["mid_price"]
    vacuum_stats = (
        vacuum.groupby("vacuum_side")
        .agg(count=("refill_move", "size"), mean_refill_move=("refill_move", "mean"))
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    corr_items = list(corr.items())
    ax.bar([k for k, _ in corr_items], [v for _, v in corr_items], color="#264653")
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_title("Osmium Feature Correlation With Next Mid Move")
    ax.set_ylabel("Correlation")
    fig.tight_layout()
    fig.savefig(output_dir / "ash_feature_correlations.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    labels = ["agree |gap|>=0.5", "agree |gap|>=1.0", "disagree->imb", "tight micro"]
    values = [
        agreement_stats["agree_05_hit_rate"],
        agreement_stats["agree_10_hit_rate"],
        agreement_stats["disagree_follow_imbalance"],
        tight_micro_hit,
    ]
    ax.bar(labels, values, color="#e76f51")
    ax.set_ylim(0.0, 1.0)
    ax.set_title("Osmium Next-Move Hit Rates In Key Regimes")
    ax.set_ylabel("Hit Rate")
    fig.tight_layout()
    fig.savefig(output_dir / "ash_regime_hit_rates.png", dpi=180)
    plt.close(fig)

    access_df = pd.DataFrame(access_rows)
    fig, ax = plt.subplots(figsize=(8, 5))
    width = 0.35
    x = np.arange(len(access_df))
    ax.bar(x - width / 2, access_df["buy_markout_5"], width=width, label="Buy markout", color="#2a9d8f")
    ax.bar(x + width / 2, access_df["sell_markout_5"], width=width, label="Sell markout", color="#f4a261")
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels([f"L{level}" for level in access_df["level"]])
    ax.set_title("Osmium 5-Bar Markout By Sweep Level In Strong Access States")
    ax.set_ylabel("Mean 5-Bar Markout")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "ash_access_markout.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(vacuum_stats["vacuum_side"], vacuum_stats["mean_refill_move"], color="#577590")
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_title("Osmium Refill Move After One-Sided Vacuum")
    ax.set_ylabel("Mean Move To Next Valid Mid")
    fig.tight_layout()
    fig.savefig(output_dir / "ash_vacuum_refill.png", dpi=180)
    plt.close(fig)

    return {
        "feature_correlation": corr,
        "agreement_stats": agreement_stats,
        "tight_micro_hit_rate": float(tight_micro_hit),
        "access_markout": access_rows,
        "vacuum_stats": vacuum_stats.to_dict(orient="records"),
    }


def write_report(pepper: Dict[str, object], ash: Dict[str, object], output_dir: Path) -> None:
    cheap = pepper["cheap_accum_stats"]
    late = pepper["late_session_stats"]
    agree = ash["agreement_stats"]
    corr = ash["feature_correlation"]
    access = ash["access_markout"]
    vacuum = ash["vacuum_stats"]

    report = f"""# Round 2 Data Research

## Scope
- Dataset: public Round 2 prices and trades for days `-1`, `0`, and `1`
- Products: `INTARIAN_PEPPER_ROOT`, `ASH_COATED_OSMIUM`
- Goal: extract product-specific structure that can create strategy separation, not just generic tuning

## Pepper Findings

### 1. Pepper is still a drift product, but entry timing matters
- Non-tradable Pepper rows removed from timing study: `{pepper['invalid_rows']}`
- Day trend slopes:
{chr(10).join(f"  - day {row['day']}: slope {row['slope_per_ts']:.6f} per timestamp, start {row['start_mid']:.1f}, end {row['end_mid']:.1f}" for row in pepper['per_day_trend'])}
- This supports keeping Pepper as a carry/schedule engine instead of treating it like a market maker.

### 2. Negative residuals are real cheap-entry windows
- Cheap accumulation regime:
  - count: `{cheap['count']}`
  - mean 10-bar forward return: `{cheap['mean_ret_10']:.3f}`
  - mean 25-bar forward return: `{cheap['mean_ret_25']:.3f}`
  - 25-bar hit rate: `{cheap['hit_rate_25']:.3%}`
- This says Pepper should buy when it is below the drift line, not just whenever schedule says we are behind.

### 3. Late-session carry is weaker than early/mid carry
- Late session (`progress >= 0.85`) 25-bar forward return:
  - count: `{late['count']}`
  - mean: `{late['mean_ret_25']:.3f}`
  - hit rate: `{late['hit_rate_25']:.3%}`
- This supports mild late trimming or less aggressive catch-up once the day is mostly spent.

## Osmium Findings

### 1. The best short-horizon information is still local-book structure
- Correlation with next move:
  - stable gap: `{corr['stable_gap']:.3f}`
  - micro gap: `{corr['micro_gap']:.3f}`
  - deep micro gap: `{corr['deep_micro_gap']:.3f}`
  - imbalance signal: `{corr['imbalance_signal']:.3f}`
- The main takeaway is that a richer top-3 / imbalance-aware local fair is worth more than another anchor constant.

### 2. Agreement states are genuinely special
- Agreement `|stable_gap| >= 0.5`:
  - count: `{agree['agree_05_count']}`
  - hit rate: `{agree['agree_05_hit_rate']:.3%}`
- Agreement `|stable_gap| >= 1.0`:
  - count: `{agree['agree_10_count']}`
  - hit rate: `{agree['agree_10_hit_rate']:.3%}`
- Disagreement states:
  - count: `{agree['disagree_count']}`
  - follow imbalance hit rate: `{agree['disagree_follow_imbalance']:.3%}`
  - follow stable-gap hit rate: `{agree['disagree_follow_stable']:.3%}`
- This is exactly the sort of branching rule that can set us apart: agreement unlocks throughput, disagreement should trust imbalance more than the slower stable-book pull.

### 3. Tight-book microprice is still a strong next-step flag
- Tight-book hit rate when micro gap is nonzero: `{ash['tight_micro_hit_rate']:.3%}`
- This is a very strong case for keeping micro and deep micro in the Ash engine, especially in narrow-spread states.

### 4. Access-style sweep value exists, but it is level-dependent
{chr(10).join(f"  - L{row['level']}: buy count {row['buy_count']}, buy 5-bar markout {row['buy_markout_5']:.3f}; sell count {row['sell_count']}, sell 5-bar markout {row['sell_markout_5']:.3f}" for row in access)}
- The implication is that multi-level sweeping should be selective and usually shallow, not a generic aggression toggle.

### 5. One-sided vacuums still snap back in a directional way
{chr(10).join(f"  - {row['vacuum_side']}: count {row['count']}, mean refill move {row['mean_refill_move']:.3f}" for row in vacuum)}
- This supports explicit vacuum / refill logic instead of treating one-sided books like ordinary fair-value states.

## Highest-Value Implementation Ideas

1. **Pepper drift-residual execution**
- Keep Pepper as a carry engine.
- Make schedule/catch-up depend more on residual-to-drift z-score.
- Be less eager to chase late if the carry window is mostly spent.

2. **Osmium agreement-aware throughput**
- When stable gap, imbalance, and micro align, allow more throughput:
  - easier join
  - +front size
  - shallow L2 sweep only if markout stays positive

3. **Osmium disagreement routing**
- When stable-gap and imbalance disagree, follow imbalance for immediate execution.
- Keep the slower stable-book pull mostly in quoting / reservation, not in taking.

4. **Osmium vacuum/refill controller**
- Keep explicit one-sided-book memory.
- Use it as a separate state machine instead of just dropping to a fallback fair.

## Output Artifacts
- `pepper_mid_and_trend.png`
- `pepper_residual_bins.png`
- `ash_feature_correlations.png`
- `ash_regime_hit_rates.png`
- `ash_access_markout.png`
- `ash_vacuum_refill.png`
"""
    (output_dir / "round2_data_research_report.md").write_text(report)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prices = prepare_prices(load_prices())
    trades = load_trades()

    pepper = analyze_pepper(prices, OUTPUT_DIR)
    ash = analyze_ash(prices, trades, OUTPUT_DIR)

    summary = {"pepper": pepper, "ash": ash}
    (OUTPUT_DIR / "round2_data_research_summary.json").write_text(json.dumps(summary, indent=2))
    write_report(pepper, ash, OUTPUT_DIR)
    print(f"Wrote research outputs to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
