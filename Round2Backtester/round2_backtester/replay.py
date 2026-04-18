from __future__ import annotations

import csv
import io
import json
import random
import statistics
from collections import defaultdict
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable

from .access import build_access_stats, augment_snapshot_with_access
from .artifacts import MarketStateRow
from .datamodel_bridge import ensure_bot_imports, load_trader, resolve_bot_path
from .loaders import load_any
from .matching import Fill, RestingOrder, apply_fills, execute_crossing_order, try_fill_pending_order


DEFAULT_LIMITS = {
    "ASH_COATED_OSMIUM": 80,
    "INTARIAN_PEPPER_ROOT": 80,
}


@dataclass(frozen=True)
class BacktestConfig:
    bot_path: Path
    data_root: Path
    output_dir: Path
    day: int | None = None
    mode: str = "no_access"
    queue_model: str = "conservative"
    access_seed: int = 7
    access_seeds: int = 5
    extra_quote_ratio: float = 0.25
    markout_horizon_steps: int = 5
    position_limits: Dict[str, int] | None = None


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _bucket_spread(spread: float) -> str:
    if spread <= 8:
        return "tight"
    if spread <= 16:
        return "normal"
    return "wide"


def _bucket_toxicity(micro_gap: float) -> str:
    gap = abs(micro_gap)
    if gap < 0.35:
        return "low"
    if gap < 0.9:
        return "medium"
    return "high"


def _bucket_conviction(micro_gap: float) -> str:
    gap = abs(micro_gap)
    if gap < 0.5:
        return "mild"
    if gap < 1.25:
        return "strong"
    return "extreme"


def _agreement_state(snapshot: MarketStateRow) -> str:
    micro_sign = 1 if snapshot.microprice > snapshot.mid_price else -1 if snapshot.microprice < snapshot.mid_price else 0
    imbalance_sign = 1 if snapshot.imbalance > 0 else -1 if snapshot.imbalance < 0 else 0
    if micro_sign == 0 or imbalance_sign == 0:
        return "neutral"
    return "agree" if micro_sign == imbalance_sign else "disagree"


def _safe_json(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _safe_json(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_safe_json(inner) for inner in value]
    return value


def _discover_round2_artifacts(data_root: Path, day: int | None = None):
    price_states: Dict[tuple[int, int], Dict[str, MarketStateRow]] = {}
    trades_by_day: Dict[int, Dict[tuple[int, str], list]] = defaultdict(lambda: defaultdict(list))
    all_states: list[MarketStateRow] = []

    for path in sorted(data_root.iterdir()):
        if not path.is_file():
            continue
        if not path.name.startswith(("prices_round_2_day_", "trades_round_2_day_")):
            continue
        artifact = load_any(path)
        if artifact.kind == "public_price_csv":
            for state in artifact.market_states:
                if day is not None and state.day != day:
                    continue
                price_states.setdefault((state.day, state.timestamp), {})[state.product] = state
                all_states.append(state)
        elif artifact.kind == "public_trade_csv":
            for trade in artifact.market_trades:
                if day is not None and trade.day != day:
                    continue
                trades_by_day[trade.day][(trade.timestamp, trade.symbol)].append(trade)

    ordered_keys = sorted(price_states.keys())
    products = sorted({state.product for state in all_states})
    return price_states, trades_by_day, products, ordered_keys, all_states


def _build_order_depth(snapshot: MarketStateRow, OrderDepthClass):
    depth = OrderDepthClass()
    depth.buy_orders = {level.price: level.volume for level in snapshot.bid_levels}
    depth.sell_orders = {level.price: -level.volume for level in snapshot.ask_levels}
    return depth


def _build_trade_rows(rows: Iterable[Any], TradeClass):
    trades = []
    for row in rows:
        trades.append(
            TradeClass(
                symbol=row.symbol,
                price=int(row.price),
                quantity=int(row.quantity),
                buyer=row.buyer,
                seller=row.seller,
                timestamp=int(row.timestamp),
            )
        )
    return trades


def _normalize_trader_return(raw_result):
    orders = raw_result
    conversions = 0
    trader_data = ""
    if isinstance(raw_result, tuple):
        if len(raw_result) == 3:
            orders, conversions, trader_data = raw_result
        elif len(raw_result) == 2:
            orders, second = raw_result
            if isinstance(second, str):
                trader_data = second
            else:
                conversions = int(second)
        elif len(raw_result) == 1:
            orders = raw_result[0]
    if not isinstance(orders, dict):
        orders = {}
    return orders, int(conversions), trader_data if isinstance(trader_data, str) else str(trader_data)


def _format_orders(orders_by_product: dict[str, list]) -> str:
    parts: list[str] = []
    for product in sorted(orders_by_product):
        for order in orders_by_product[product]:
            parts.append(f"{product}:{int(order.price)}@{int(order.quantity)}")
    return " | ".join(parts) if parts else "-"


def _max_drawdown(series: list[float]) -> float:
    peak = float("-inf")
    max_dd = 0.0
    for value in series:
        peak = max(peak, value)
        max_dd = max(max_dd, peak - value)
    return max_dd


def _markout_by_fill(fill_rows: list[dict[str, Any]], future_mid_lookup: dict[tuple[str, int], float], horizon: int):
    buy_markouts: list[float] = []
    sell_markouts: list[float] = []
    for row in fill_rows:
        future_mid = future_mid_lookup.get((row["product"], row["step_index"] + horizon))
        if future_mid is None:
            row["markout"] = None
            continue
        if row["side"] == "BUY":
            markout = (future_mid - row["price"]) * row["quantity"]
            buy_markouts.append(markout)
        else:
            markout = (row["price"] - future_mid) * row["quantity"]
            sell_markouts.append(markout)
        row["markout"] = round(markout, 4)
    return {
        "BUY": round(statistics.mean(buy_markouts), 4) if buy_markouts else None,
        "SELL": round(statistics.mean(sell_markouts), 4) if sell_markouts else None,
    }


def _build_plateau_windows(product_steps: list[dict[str, Any]], threshold: int = 25) -> list[dict[str, Any]]:
    windows: list[dict[str, Any]] = []
    streak_start = None
    for row in product_steps:
        active = (
            row["product"] == "ASH_COATED_OSMIUM"
            and row["submitted_orders"] > 0
            and row["fills"] == 0
            and row["toxicity_bucket"] == "low"
            and row["signal_proxy"] >= 0.5
        )
        if active and streak_start is None:
            streak_start = row
        if not active and streak_start is not None:
            bars = (row["step_index"] - streak_start["step_index"])
            if bars >= threshold:
                windows.append(
                    {
                        "day": streak_start["day"],
                        "start_timestamp": streak_start["timestamp"],
                        "end_timestamp": row["timestamp"],
                        "bars": bars,
                        "reason": "quotes_present_but_no_osmium_fill",
                    }
                )
            streak_start = None
    return windows


def _collect_product_diagnostics(fill_rows: list[dict[str, Any]], product_steps: list[dict[str, Any]]):
    osmium_rows = [row for row in fill_rows if row["product"] == "ASH_COATED_OSMIUM"]
    pepper_rows = [row for row in fill_rows if row["product"] == "INTARIAN_PEPPER_ROOT"]

    osmium_buckets: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in osmium_rows:
        key = (
            row["toxicity_bucket"],
            row["conviction_bucket"],
            row["spread_bucket"],
            row["agreement_state"],
            row["access_source"],
        )
        bucket = osmium_buckets["|".join(key)]
        bucket["fill_count"] += 1
        bucket["edge_sum"] += row["micro_gap"]
        bucket["pnl_sum"] += row["cash_flow_signed"]
        if row.get("markout") is not None:
            bucket["markout_sum"] += row["markout"]

    pepper_buys = [row for row in pepper_rows if row["side"] == "BUY"]
    pepper_sells = [row for row in pepper_rows if row["side"] == "SELL"]
    pepper_diag = {
        "average_entry_price": round(statistics.mean(row["price"] for row in pepper_buys), 4) if pepper_buys else None,
        "buy_count": len(pepper_buys),
        "sell_count": len(pepper_sells),
        "average_fill_residual": round(statistics.mean(row["residual_to_trend"] for row in pepper_rows), 4)
        if pepper_rows
        else None,
        "late_day_trimming_count": sum(1 for row in pepper_sells if row["timestamp"] >= 8000),
    }

    return {
        "osmium_buckets": {
            key: {
                "fill_count": int(values["fill_count"]),
                "mean_edge_at_fill": round(values["edge_sum"] / values["fill_count"], 4) if values["fill_count"] else None,
                "mean_post_fill_markout": round(values["markout_sum"] / values["fill_count"], 4)
                if values["fill_count"]
                else None,
                "realized_cashflow_contribution": round(values["pnl_sum"], 4),
            }
            for key, values in osmium_buckets.items()
        },
        "pepper": pepper_diag,
        "plateau_windows": _build_plateau_windows(product_steps),
    }


def _run_single_mode(config: BacktestConfig, mode: str, access_seed: int) -> dict[str, Any]:
    bot_path = resolve_bot_path(config.bot_path)
    datamodel = ensure_bot_imports(bot_path)
    trader = load_trader(bot_path)

    price_states, trades_by_day, products, ordered_keys, all_states = _discover_round2_artifacts(config.data_root, config.day)
    if not ordered_keys:
        raise FileNotFoundError(f"No Round 2 price data found under {config.data_root}")
    limits = dict(DEFAULT_LIMITS)
    if config.position_limits:
        limits.update(config.position_limits)

    access_stats = build_access_stats(all_states)

    listings = {
        product: datamodel.Listing(symbol=product, product=product, denomination="XIRECS")
        for product in products
    }

    position = {product: 0 for product in products}
    cash = {product: 0.0 for product in products}
    pending_orders: Dict[str, list[RestingOrder]] = {product: [] for product in products}
    last_own_trades = {product: [] for product in products}
    trader_data = ""
    trader_bid = None
    if hasattr(trader, "bid"):
        try:
            trader_bid = trader.bid()
        except Exception:
            trader_bid = None

    fill_events: list[Fill] = []
    fill_rows: list[dict[str, Any]] = []
    step_rows: list[dict[str, Any]] = []
    product_step_rows: list[dict[str, Any]] = []
    total_pnl_series: list[float] = []
    product_final_pnl: dict[str, float] = {}
    future_mid_lookup: dict[tuple[str, int], float] = {}

    step_index = 0
    for day, timestamp in ordered_keys:
        base_snapshots = price_states[(day, timestamp)]
        snapshots: dict[str, MarketStateRow] = {}
        for product, snapshot in base_snapshots.items():
            if mode == "access":
                rng = random.Random(f"{access_seed}:{day}:{timestamp}:{product}")
                snapshots[product] = augment_snapshot_with_access(
                    snapshot,
                    access_stats,
                    rng,
                    extra_quote_ratio=config.extra_quote_ratio,
                )
            else:
                snapshots[product] = snapshot

        fills_between_steps: list[Fill] = []
        for product in products:
            snapshot = snapshots[product]
            day_trades = trades_by_day.get(day, {})
            market_trade_rows = day_trades.get((timestamp, product), [])
            next_pending: list[RestingOrder] = []
            for pending in pending_orders[product]:
                rng = random.Random(f"pending:{mode}:{access_seed}:{day}:{timestamp}:{product}:{pending.price}")
                new_fills = try_fill_pending_order(
                    pending,
                    snapshot,
                    market_trade_rows,
                    config.queue_model,
                    rng,
                    step_index,
                    mode,
                )
                if new_fills:
                    filled_qty = sum(fill.quantity for fill in new_fills)
                    if pending.quantity > filled_qty:
                        next_pending.append(
                            RestingOrder(
                                product=pending.product,
                                side=pending.side,
                                price=pending.price,
                                quantity=pending.quantity - filled_qty,
                                submitted_day=pending.submitted_day,
                                submitted_timestamp=pending.submitted_timestamp,
                                at_touch=pending.at_touch,
                                improved_touch=pending.improved_touch,
                            )
                        )
                    fills_between_steps.extend(new_fills)
                else:
                    next_pending.append(pending)
            pending_orders[product] = next_pending

        if fills_between_steps:
            fill_events.extend(fills_between_steps)
            last_own_trades = apply_fills(fills_between_steps, cash, position, datamodel.Trade)
        else:
            last_own_trades = {product: [] for product in products}

        order_depths = {product: _build_order_depth(snapshots[product], datamodel.OrderDepth) for product in products}
        market_trades = {
            product: _build_trade_rows(trades_by_day.get(day, {}).get((timestamp, product), []), datamodel.Trade)
            for product in products
        }
        state = datamodel.TradingState(
            traderData=trader_data,
            timestamp=timestamp,
            listings=listings,
            order_depths=order_depths,
            own_trades=last_own_trades,
            market_trades=market_trades,
            position=dict(position),
            observations=datamodel.Observation({}, {}),
        )

        stdout_buffer = io.StringIO()
        with redirect_stdout(stdout_buffer):
            raw_result = trader.run(state)
        orders_by_product, conversions, trader_data = _normalize_trader_return(raw_result)
        stdout_text = stdout_buffer.getvalue().strip()

        new_pending_orders: Dict[str, list[RestingOrder]] = {product: [] for product in products}
        step_fills: list[Fill] = []
        product_fill_counts = defaultdict(int)
        product_order_counts = defaultdict(int)

        for product in products:
            snapshot = snapshots[product]
            orders = list(orders_by_product.get(product, []))
            projected_position = position[product]
            limit = limits.get(product, 80)
            for order in orders:
                if not isinstance(order, datamodel.Order):
                    continue
                if int(order.quantity) == 0:
                    continue
                side = "BUY" if int(order.quantity) > 0 else "SELL"
                max_quantity = max(0, (limit - projected_position) if side == "BUY" else (limit + projected_position))
                submit_quantity = min(abs(int(order.quantity)), max_quantity)
                if submit_quantity <= 0:
                    continue
                product_order_counts[product] += 1
                projected_position += submit_quantity if side == "BUY" else -submit_quantity

                class AcceptedOrder:
                    def __init__(self, symbol: str, price: int, quantity: int) -> None:
                        self.symbol = symbol
                        self.price = price
                        self.quantity = quantity

                accepted_order = AcceptedOrder(product, int(order.price), submit_quantity if side == "BUY" else -submit_quantity)
                aggressive_fills, remaining_qty = execute_crossing_order(accepted_order, snapshot, side, step_index, mode)
                step_fills.extend(aggressive_fills)
                if remaining_qty <= 0:
                    continue

                best_bid = snapshot.bid_levels[0].price if snapshot.bid_levels else None
                best_ask = snapshot.ask_levels[0].price if snapshot.ask_levels else None
                at_touch = (side == "BUY" and best_bid is not None and int(order.price) == best_bid) or (
                    side == "SELL" and best_ask is not None and int(order.price) == best_ask
                )
                improved_touch = (side == "BUY" and best_bid is not None and int(order.price) > best_bid) or (
                    side == "SELL" and best_ask is not None and int(order.price) < best_ask
                )
                is_resting = (side == "BUY" and (best_ask is None or int(order.price) < best_ask)) or (
                    side == "SELL" and (best_bid is None or int(order.price) > best_bid)
                )
                if is_resting:
                    new_pending_orders[product].append(
                        RestingOrder(
                            product=product,
                            side=side,
                            price=int(order.price),
                            quantity=remaining_qty,
                            submitted_day=day,
                            submitted_timestamp=timestamp,
                            at_touch=at_touch,
                            improved_touch=improved_touch,
                        )
                    )

        pending_orders = new_pending_orders

        if step_fills:
            fill_events.extend(step_fills)
            own_trades = apply_fills(step_fills, cash, position, datamodel.Trade)
        else:
            own_trades = {product: [] for product in products}
        last_own_trades = own_trades
        for product, trades in own_trades.items():
            product_fill_counts[product] += len(trades)

        total_pnl = 0.0
        for product in products:
            snapshot = snapshots[product]
            mid_price = snapshot.mid_price
            unrealized = position[product] * mid_price
            product_pnl = cash[product] + unrealized
            total_pnl += product_pnl
            product_final_pnl[product] = product_pnl
            signal_proxy = abs(snapshot.microprice - snapshot.mid_price)
            product_step_rows.append(
                {
                    "mode": mode,
                    "step_index": step_index,
                    "day": day,
                    "timestamp": timestamp,
                    "product": product,
                    "submitted_orders": product_order_counts[product],
                    "fills": product_fill_counts[product],
                    "pending_orders_next_step": len(pending_orders[product]),
                    "position": position[product],
                    "cash": round(cash[product], 4),
                    "mid_price": round(mid_price, 4),
                    "microprice": round(snapshot.microprice, 4),
                    "spread": round(snapshot.spread, 4),
                    "imbalance": round(snapshot.imbalance, 6),
                    "source_mode": snapshot.source_mode,
                    "access_added_levels": snapshot.access_added_levels,
                    "signal_proxy": round(signal_proxy, 4),
                    "toxicity_bucket": _bucket_toxicity(snapshot.microprice - snapshot.mid_price),
                    "agreement_state": _agreement_state(snapshot),
                    "product_pnl": round(product_pnl, 4),
                }
            )
            future_mid_lookup[(product, step_index)] = mid_price

        step_rows.append(
            {
                "mode": mode,
                "step_index": step_index,
                "day": day,
                "timestamp": timestamp,
                "submitted_orders": sum(product_order_counts.values()),
                "fills": len(step_fills),
                "pending_orders_next_step": sum(len(values) for values in pending_orders.values()),
                "conversions": conversions,
                "total_pnl": round(total_pnl, 4),
                "orders": _format_orders(orders_by_product),
                "stdout": stdout_text.replace("\n", " | "),
            }
        )
        total_pnl_series.append(total_pnl)
        step_index += 1

    pepper_start_mid = future_mid_lookup.get(("INTARIAN_PEPPER_ROOT", 0), 0.0)
    pepper_end_mid = future_mid_lookup.get(("INTARIAN_PEPPER_ROOT", step_index - 1), pepper_start_mid)
    pepper_slope = ((pepper_end_mid - pepper_start_mid) / max(1, step_index - 1)) if step_index > 1 else 0.0

    for fill in fill_events:
        residual_to_trend = 0.0
        if fill.product == "INTARIAN_PEPPER_ROOT":
            trend_mid = pepper_start_mid + pepper_slope * fill.step_index
            residual_to_trend = (fill.price - trend_mid) * (1 if fill.side == "BUY" else -1)
        fill_rows.append(
            {
                "mode": fill.replay_mode,
                "step_index": fill.step_index,
                "day": fill.day,
                "timestamp": fill.timestamp,
                "abs_timestamp": fill.abs_timestamp,
                "product": fill.product,
                "side": fill.side,
                "price": fill.price,
                "quantity": fill.quantity,
                "fill_type": fill.fill_type,
                "source_order_price": fill.source_order_price,
                "book_origin": fill.book_origin,
                "access_source": "access" if fill.replay_mode == "access" else "no_access",
                "spread": round(fill.spread, 4),
                "imbalance": round(fill.imbalance, 6),
                "micro_gap": round(fill.micro_gap, 4),
                "toxicity_bucket": _bucket_toxicity(fill.micro_gap),
                "conviction_bucket": _bucket_conviction(fill.micro_gap),
                "spread_bucket": _bucket_spread(fill.spread),
                "agreement_state": "agree" if fill.micro_gap == 0 or fill.micro_gap * fill.imbalance >= 0 else "disagree",
                "access_added_levels": fill.access_added_levels,
                "cash_flow_signed": round((-fill.price * fill.quantity) if fill.side == "BUY" else (fill.price * fill.quantity), 4),
                "residual_to_trend": round(residual_to_trend, 4),
            }
        )

    average_markout = _markout_by_fill(fill_rows, future_mid_lookup, config.markout_horizon_steps)
    diagnostics = _collect_product_diagnostics(fill_rows, product_step_rows)

    summary = {
        "bot_path": str(bot_path),
        "mode": mode,
        "queue_model": config.queue_model,
        "access_seed": access_seed,
        "trader_bid": trader_bid,
        "steps": len(step_rows),
        "total_fills": len(fill_rows),
        "total_pnl": round(total_pnl_series[-1], 4) if total_pnl_series else 0.0,
        "best_total_pnl": round(max(total_pnl_series), 4) if total_pnl_series else 0.0,
        "worst_total_pnl": round(min(total_pnl_series), 4) if total_pnl_series else 0.0,
        "max_drawdown": round(_max_drawdown(total_pnl_series), 4) if total_pnl_series else 0.0,
        "per_product_pnl": {product: round(value, 4) for product, value in product_final_pnl.items()},
        "final_positions": position,
        "aggressive_fills": sum(1 for row in fill_rows if row["fill_type"] == "aggressive_cross"),
        "passive_fills": sum(1 for row in fill_rows if row["fill_type"] != "aggressive_cross"),
        "average_markout_by_side": average_markout,
    }
    return {
        "summary": summary,
        "step_rows": step_rows,
        "product_step_rows": product_step_rows,
        "fill_rows": fill_rows,
        "diagnostics": diagnostics,
    }


def _write_mode_output(output_dir: Path, payload: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "step_log.csv", payload["step_rows"])
    _write_csv(output_dir / "product_steps.csv", payload["product_step_rows"])
    _write_csv(output_dir / "fills.csv", payload["fill_rows"])
    (output_dir / "summary.json").write_text(json.dumps(_safe_json(payload["summary"]), indent=2) + "\n")
    (output_dir / "diagnostics.json").write_text(json.dumps(_safe_json(payload["diagnostics"]), indent=2) + "\n")
    summary_lines = [
        "Round 2 backtest summary",
        "========================",
        f"Bot: {payload['summary']['bot_path']}",
        f"Mode: {payload['summary']['mode']}",
        f"Queue model: {payload['summary']['queue_model']}",
        f"Trader bid(): {payload['summary']['trader_bid']}",
        f"Steps: {payload['summary']['steps']}",
        f"Total fills: {payload['summary']['total_fills']}",
        f"Final PnL: {payload['summary']['total_pnl']:.4f}",
        f"Max drawdown: {payload['summary']['max_drawdown']:.4f}",
        "",
        "Per product PnL:",
    ]
    for product, pnl in sorted(payload["summary"]["per_product_pnl"].items()):
        summary_lines.append(f"- {product}: {pnl:.4f}")
    summary_lines.extend(
        [
            "",
            "Approximation notes:",
            "- Aggressive orders sweep visible levels immediately.",
            "- Resting orders use an explicit queue model: conservative or touch_join.",
            "- Access mode augments the public book with synthetic latent quotes sampled from empirical Round 2 structure.",
        ]
    )
    (output_dir / "summary.txt").write_text("\n".join(summary_lines) + "\n")


def run_single_backtest(config: BacktestConfig) -> dict[str, Any]:
    payload = _run_single_mode(config, mode=config.mode, access_seed=config.access_seed)
    _write_mode_output(config.output_dir, payload)
    return payload


def run_compare_backtest(config: BacktestConfig) -> dict[str, Any]:
    compare_root = config.output_dir
    no_access_payload = _run_single_mode(config, mode="no_access", access_seed=config.access_seed)
    _write_mode_output(compare_root / "no_access", no_access_payload)

    access_runs: list[dict[str, Any]] = []
    access_summaries: list[dict[str, Any]] = []
    for seed_offset in range(max(1, config.access_seeds)):
        seed = config.access_seed + seed_offset
        payload = _run_single_mode(config, mode="access", access_seed=seed)
        access_runs.append(payload)
        access_summaries.append(payload["summary"])
        _write_mode_output(compare_root / f"access_seed_{seed}", payload)

    deltas = [round(summary["total_pnl"] - no_access_payload["summary"]["total_pnl"], 4) for summary in access_summaries]
    compare_summary = {
        "bot_path": str(resolve_bot_path(config.bot_path)),
        "queue_model": config.queue_model,
        "baseline_no_access_pnl": no_access_payload["summary"]["total_pnl"],
        "access_runs": access_summaries,
        "delta_access_values": deltas,
        "delta_access_mean": round(statistics.mean(deltas), 4) if deltas else 0.0,
        "delta_access_median": round(statistics.median(deltas), 4) if deltas else 0.0,
        "delta_access_p25": round(sorted(deltas)[max(0, int(len(deltas) * 0.25) - 1)], 4) if deltas else 0.0,
        "delta_access_p10": round(sorted(deltas)[max(0, int(len(deltas) * 0.10) - 1)], 4) if deltas else 0.0,
    }
    compare_root.mkdir(parents=True, exist_ok=True)
    (compare_root / "compare_summary.json").write_text(json.dumps(_safe_json(compare_summary), indent=2) + "\n")
    return compare_summary
