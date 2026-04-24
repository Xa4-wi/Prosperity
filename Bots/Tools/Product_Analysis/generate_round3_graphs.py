from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROOT = REPO_ROOT / "Data" / "ROUND_3"
DEFAULT_OUTPUT = DEFAULT_ROOT / "graphs"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Round 3 product graphs.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Round 3 data directory.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Directory to write PNG graphs into.")
    return parser


def load_prices(root: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(root.glob("prices_round_3_day_*.csv")):
        day_df = pd.read_csv(path, sep=";")
        day_df["source_file"] = path.name
        frames.append(day_df)
    if not frames:
        raise FileNotFoundError(f"No Round 3 price files found in {root}")
    prices = pd.concat(frames, ignore_index=True)
    prices["day"] = prices["day"].astype(int)
    prices["timestamp"] = prices["timestamp"].astype(int)
    return prices


def load_trades(root: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(root.glob("trades_round_3_day_*.csv")):
        day_num = int(path.stem.split("_")[-1])
        day_df = pd.read_csv(path, sep=";")
        day_df["day"] = day_num
        day_df["source_file"] = path.name
        frames.append(day_df)
    if not frames:
        return pd.DataFrame(columns=["timestamp", "buyer", "seller", "symbol", "currency", "price", "quantity", "day"])
    trades = pd.concat(frames, ignore_index=True)
    trades["day"] = trades["day"].astype(int)
    trades["timestamp"] = trades["timestamp"].astype(int)
    return trades


def add_plot_x(df: pd.DataFrame, day_order: list[int], spacing: int = 100_000) -> pd.DataFrame:
    df = df.copy()
    day_offsets = {day: idx * spacing for idx, day in enumerate(day_order)}
    df["plot_x"] = df["timestamp"] + df["day"].map(day_offsets)
    return df


def compute_imbalance(df: pd.DataFrame) -> pd.Series:
    bid_cols = [col for col in ["bid_volume_1", "bid_volume_2", "bid_volume_3"] if col in df.columns]
    ask_cols = [col for col in ["ask_volume_1", "ask_volume_2", "ask_volume_3"] if col in df.columns]
    bid_depth = df[bid_cols].fillna(0).sum(axis=1)
    ask_depth = df[ask_cols].fillna(0).sum(axis=1)
    total = bid_depth + ask_depth
    return (bid_depth - ask_depth) / total.where(total != 0, 1)


def render_product_figure(product: str, prices: pd.DataFrame, trades: pd.DataFrame, output_dir: Path) -> None:
    product_prices = prices.loc[prices["product"] == product].copy()
    product_trades = trades.loc[trades["symbol"] == product].copy()
    if product_prices.empty:
        return

    days = sorted(product_prices["day"].unique())
    product_prices = add_plot_x(product_prices, days)
    product_trades = add_plot_x(product_trades, days) if not product_trades.empty else product_trades
    product_prices["spread"] = product_prices["ask_price_1"] - product_prices["bid_price_1"]
    product_prices["top_depth"] = product_prices[["bid_volume_1", "ask_volume_1"]].fillna(0).sum(axis=1)
    product_prices["imbalance"] = compute_imbalance(product_prices)

    fig, axes = plt.subplots(4, 1, figsize=(16, 12), sharex=True, constrained_layout=True)
    colors = {day: color for day, color in zip(days, ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"])}

    for day in days:
        mask = product_prices["day"] == day
        day_prices = product_prices.loc[mask]
        c = colors[day]
        label = f"day {day}"
        axes[0].plot(day_prices["plot_x"], day_prices["mid_price"], color=c, lw=1.6, label=label)
        axes[0].plot(day_prices["plot_x"], day_prices["bid_price_1"], color=c, lw=0.6, alpha=0.25)
        axes[0].plot(day_prices["plot_x"], day_prices["ask_price_1"], color=c, lw=0.6, alpha=0.25)

        if not product_trades.empty:
            day_trades = product_trades.loc[product_trades["day"] == day]
            if not day_trades.empty:
                sizes = 8 + day_trades["quantity"].clip(lower=1) * 2.5
                axes[0].scatter(day_trades["plot_x"], day_trades["price"], s=sizes, color=c, alpha=0.35, edgecolors="none")

        axes[1].plot(day_prices["plot_x"], day_prices["spread"], color=c, lw=1.2)
        axes[2].plot(day_prices["plot_x"], day_prices["top_depth"], color=c, lw=1.2)
        axes[3].plot(day_prices["plot_x"], day_prices["imbalance"], color=c, lw=1.1)

    # Draw day separators.
    for idx in range(1, len(days)):
        boundary = idx * 100_000
        for ax in axes:
            ax.axvline(boundary, color="#999999", lw=0.8, ls="--", alpha=0.5)

    axes[0].set_title(f"{product} - Mid, touch, and trades")
    axes[0].set_ylabel("Price")
    axes[0].legend(loc="upper left", ncol=min(3, len(days)))

    axes[1].set_title("Best spread")
    axes[1].set_ylabel("Spread")

    axes[2].set_title("Top-of-book depth (bid1 + ask1)")
    axes[2].set_ylabel("Depth")

    axes[3].set_title("Top-3 depth imbalance")
    axes[3].set_ylabel("Imbalance")
    axes[3].axhline(0.0, color="#444444", lw=0.8, alpha=0.6)
    axes[3].set_xlabel("Timestamp with day offsets")

    fig.suptitle(product, fontsize=15, y=1.02)
    out_path = output_dir / f"{product}.png"
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def render_overview(prices: pd.DataFrame, output_dir: Path) -> None:
    products = sorted(prices["product"].unique())
    days = sorted(prices["day"].unique())
    prices = add_plot_x(prices, days)

    ncols = 3
    nrows = (len(products) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(18, 3.3 * nrows), sharex=False, constrained_layout=True)
    axes = axes.ravel()
    colors = {day: color for day, color in zip(days, ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"])}

    for ax, product in zip(axes, products):
        product_prices = prices.loc[prices["product"] == product]
        for day in days:
            day_prices = product_prices.loc[product_prices["day"] == day]
            if not day_prices.empty:
                ax.plot(day_prices["plot_x"], day_prices["mid_price"], color=colors[day], lw=1.1, label=f"day {day}")
        ax.set_title(product, fontsize=10)
        ax.tick_params(axis="both", labelsize=8)
        for idx in range(1, len(days)):
            ax.axvline(idx * 100_000, color="#999999", lw=0.6, ls="--", alpha=0.5)

    for ax in axes[len(products):]:
        ax.axis("off")

    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=len(days), frameon=False)
    fig.suptitle("Round 3 product mid-price overview", fontsize=16, y=1.02)
    fig.savefig(output_dir / "all_products_mid_overview.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def render_vev_chain(prices: pd.DataFrame, output_dir: Path) -> None:
    vev = prices.loc[prices["product"].str.startswith("VEV_")].copy()
    if vev.empty:
        return

    vev["strike"] = vev["product"].str.replace("VEV_", "", regex=False).astype(int)
    mid_grouped = vev.groupby(["day", "strike"], as_index=False).agg(mean_mid=("mid_price", "mean"))
    vev["spread"] = vev["ask_price_1"] - vev["bid_price_1"]
    spread_grouped = vev.groupby(["day", "strike"], as_index=False).agg(mean_spread=("spread", "mean"))

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), constrained_layout=True)
    colors = {day: color for day, color in zip(sorted(mid_grouped["day"].unique()), ["#1f77b4", "#ff7f0e", "#2ca02c"])}

    for day, day_df in mid_grouped.groupby("day"):
        day_df = day_df.sort_values("strike")
        axes[0].plot(day_df["strike"], day_df["mean_mid"], marker="o", color=colors[day], lw=1.5, label=f"day {day}")
    for day, day_df in spread_grouped.groupby("day"):
        day_df = day_df.sort_values("strike")
        axes[1].plot(day_df["strike"], day_df["mean_spread"], marker="o", color=colors[day], lw=1.5, label=f"day {day}")

    axes[0].set_title("VEV option family - mean mid by strike")
    axes[0].set_xlabel("Strike")
    axes[0].set_ylabel("Mean mid")
    axes[0].legend(frameon=False)

    axes[1].set_title("VEV option family - mean spread by strike")
    axes[1].set_xlabel("Strike")
    axes[1].set_ylabel("Mean spread")

    fig.savefig(output_dir / "VEV_option_chain_overview.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    prices = load_prices(args.root)
    trades = load_trades(args.root)

    render_overview(prices, args.output_dir)
    render_vev_chain(prices, args.output_dir)

    for product in sorted(prices["product"].unique()):
        render_product_figure(product, prices, trades, args.output_dir)

    print(f"Wrote graphs to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
