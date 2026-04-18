from __future__ import annotations

import csv
import io
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable

from .artifacts import (
    BookLevel,
    GraphPoint,
    MarketTradeRow,
    ParsedArtifact,
    RunExecutionRecord,
    RunSnapshotRecord,
    RunSummaryRecord,
    build_market_state,
)


PRICE_FILE_RE = re.compile(r"^prices_(.+)_day_(-?\d+)\.csv$")
TRADE_FILE_RE = re.compile(r"^trades_(.+)_day_(-?\d+)\.csv$")
ROUND_RE = re.compile(r"round[_-]?(\d+)", re.IGNORECASE)
ROUND_2_PRODUCTS = {"ASH_COATED_OSMIUM", "INTARIAN_PEPPER_ROOT"}


def _parse_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, float):
        return None if math.isnan(value) else value
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    number = float(text)
    return None if math.isnan(number) else number


def _parse_optional_int(value: Any) -> int | None:
    number = _parse_optional_float(value)
    if number is None:
        return None
    return int(number)


def _safe_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _infer_round_name(path: Path, fallback: str = "unknown") -> str:
    match = ROUND_RE.search(path.as_posix())
    if match:
        return f"round_{match.group(1)}"
    return fallback


def _guess_round_name_from_products(products: Iterable[str], fallback: str) -> str:
    product_set = {product for product in products if product}
    if product_set & ROUND_2_PRODUCTS:
        return "round_2"
    return fallback


def _read_semicolon_rows(text: str) -> list[dict[str, str]]:
    text = text.strip()
    if not text:
        return []
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    return [dict(row) for row in reader]


def _extract_graph_points(text: str) -> tuple[GraphPoint, ...]:
    rows = _read_semicolon_rows(text)
    points: list[GraphPoint] = []
    for row in rows:
        timestamp = _parse_optional_int(row.get("timestamp"))
        value = _parse_optional_float(row.get("value"))
        if timestamp is None or value is None:
            continue
        points.append(GraphPoint(timestamp=timestamp, value=value))
    return tuple(points)


def _build_levels(row: dict[str, Any]) -> tuple[tuple[BookLevel, ...], tuple[BookLevel, ...]]:
    bids: list[BookLevel] = []
    asks: list[BookLevel] = []
    for level in ("1", "2", "3"):
        bid_price = _parse_optional_int(row.get(f"bid_price_{level}"))
        bid_volume = _parse_optional_int(row.get(f"bid_volume_{level}"))
        ask_price = _parse_optional_int(row.get(f"ask_price_{level}"))
        ask_volume = _parse_optional_int(row.get(f"ask_volume_{level}"))
        if bid_price is not None and bid_volume is not None and bid_volume > 0:
            bids.append(BookLevel(price=bid_price, volume=bid_volume))
        if ask_price is not None and ask_volume is not None and ask_volume != 0:
            asks.append(BookLevel(price=ask_price, volume=abs(ask_volume)))
    return tuple(bids), tuple(asks)


def _market_state_from_row(row: dict[str, Any], round_name: str, day_override: int | None = None):
    day_value = _parse_optional_int(row.get("day"))
    timestamp = _parse_optional_int(row.get("timestamp"))
    product = _safe_text(row.get("product"))
    if timestamp is None or product is None:
        return None
    day = day_override if day_override is not None else (day_value if day_value is not None else 0)
    bid_levels, ask_levels = _build_levels(row)
    mid_price = _parse_optional_float(row.get("mid_price"))
    pnl = _parse_optional_float(row.get("profit_and_loss"))
    return build_market_state(
        round_name=round_name,
        day=day,
        timestamp=timestamp,
        product=product,
        bid_levels=bid_levels,
        ask_levels=ask_levels,
        mid_price=mid_price,
        profit_and_loss=pnl,
    )


def _trade_rows_from_iterable(
    rows: Iterable[dict[str, Any]],
    *,
    round_name: str,
    day: int,
) -> list[MarketTradeRow]:
    parsed: list[MarketTradeRow] = []
    counts: dict[tuple[int, str], int] = {}
    for row in rows:
        timestamp = _parse_optional_int(row.get("timestamp"))
        symbol = _safe_text(row.get("symbol"))
        price = _parse_optional_float(row.get("price"))
        quantity = _parse_optional_int(row.get("quantity"))
        if timestamp is None or symbol is None or price is None or quantity is None:
            continue
        key = (timestamp, symbol)
        trade_index = counts.get(key, 0)
        counts[key] = trade_index + 1
        parsed.append(
            MarketTradeRow(
                round_name=round_name,
                day=day,
                timestamp=timestamp,
                symbol=symbol,
                trade_index=trade_index,
                buyer=_safe_text(row.get("buyer")),
                seller=_safe_text(row.get("seller")),
                price=price,
                quantity=int(abs(quantity)),
                currency=_safe_text(row.get("currency")) or "XIRECS",
            )
        )
    return parsed


def load_price_csv(path: str | Path) -> ParsedArtifact:
    source_path = Path(path).resolve()
    match = PRICE_FILE_RE.match(source_path.name)
    round_name = _infer_round_name(source_path, fallback=match.group(1) if match else "unknown")
    artifact = ParsedArtifact(
        kind="public_price_csv",
        source_path=source_path,
        metadata={"round_name": round_name},
    )
    with source_path.open() as handle:
        reader = csv.DictReader(handle, delimiter=";")
        for row in reader:
            state = _market_state_from_row(row, round_name=round_name)
            if state is not None:
                artifact.market_states.append(state)
    return artifact


def load_trade_csv(path: str | Path) -> ParsedArtifact:
    source_path = Path(path).resolve()
    match = TRADE_FILE_RE.match(source_path.name)
    round_name = _infer_round_name(source_path, fallback=match.group(1) if match else "unknown")
    day = int(match.group(2)) if match else 0
    with source_path.open() as handle:
        reader = csv.DictReader(handle, delimiter=";")
        trades = _trade_rows_from_iterable(reader, round_name=round_name, day=day)
    return ParsedArtifact(
        kind="public_trade_csv",
        source_path=source_path,
        metadata={"round_name": round_name, "day": day},
        market_trades=trades,
    )


def load_run_json(path: str | Path) -> ParsedArtifact:
    source_path = Path(path).resolve()
    raw = json.loads(source_path.read_text())
    round_field = _safe_text(raw.get("round"))
    round_name = f"round_{round_field}" if round_field and round_field.isdigit() else _infer_round_name(source_path)
    run_id = source_path.stem
    graph_points = _extract_graph_points(raw.get("graphLog", ""))
    positions = {
        _safe_text(item.get("symbol")) or "UNKNOWN": int(item.get("quantity", 0))
        for item in raw.get("positions", [])
        if isinstance(item, dict)
    }

    artifact = ParsedArtifact(
        kind="run_json",
        source_path=source_path,
        metadata={
            "round_name": round_name,
            "status": _safe_text(raw.get("status")),
        },
    )

    summary = RunSummaryRecord(
        run_id=run_id,
        source_file=source_path.name,
        round_name=round_name,
        total_profit=_parse_optional_float(raw.get("profit")),
        final_positions=positions,
        graph_points=graph_points,
        notes={"status": _safe_text(raw.get("status"))},
    )
    artifact.run_summaries.append(summary)

    parsed_products: list[str] = []
    for row in _read_semicolon_rows(raw.get("activitiesLog", "")):
        state = _market_state_from_row(row, round_name=round_name)
        if state is None:
            continue
        parsed_products.append(state.product)
        artifact.run_snapshots.append(
            RunSnapshotRecord(
                run_id=run_id,
                day=state.day,
                timestamp=state.timestamp,
                product=state.product,
                market_state=state,
                product_pnl=state.profit_and_loss,
            )
        )
    guessed_round = _guess_round_name_from_products(parsed_products, round_name)
    artifact.metadata["round_name"] = guessed_round
    if artifact.run_summaries:
        artifact.run_summaries[0] = RunSummaryRecord(
            run_id=artifact.run_summaries[0].run_id,
            source_file=artifact.run_summaries[0].source_file,
            round_name=guessed_round,
            total_profit=artifact.run_summaries[0].total_profit,
            final_positions=artifact.run_summaries[0].final_positions,
            graph_points=artifact.run_summaries[0].graph_points,
            notes=artifact.run_summaries[0].notes,
        )
    return artifact


def _infer_execution_side(buyer: str | None, seller: str | None) -> str | None:
    if buyer == "SUBMISSION":
        return "BUY"
    if seller == "SUBMISSION":
        return "SELL"
    return None


def load_submission_log(path: str | Path) -> ParsedArtifact:
    source_path = Path(path).resolve()
    raw = json.loads(source_path.read_text())
    round_name = _infer_round_name(source_path)
    run_id = _safe_text(raw.get("submissionId")) or source_path.stem
    internal_logs = {
        _parse_optional_int(item.get("timestamp")): _safe_text(item.get("sandboxLog")) or _safe_text(item.get("lambdaLog"))
        for item in raw.get("logs", [])
        if isinstance(item, dict)
    }

    artifact = ParsedArtifact(
        kind="submission_log",
        source_path=source_path,
        metadata={"round_name": round_name},
    )

    artifact.run_summaries.append(
        RunSummaryRecord(
            run_id=run_id,
            source_file=source_path.name,
            round_name=round_name,
            total_profit=None,
            final_positions={},
            graph_points=(),
            notes={"submission_id": run_id},
        )
    )

    parsed_products: list[str] = []
    for row in _read_semicolon_rows(raw.get("activitiesLog", "")):
        state = _market_state_from_row(row, round_name=round_name)
        if state is None:
            continue
        parsed_products.append(state.product)
        artifact.run_snapshots.append(
            RunSnapshotRecord(
                run_id=run_id,
                day=state.day,
                timestamp=state.timestamp,
                product=state.product,
                market_state=state,
                product_pnl=state.profit_and_loss,
                internal_log=internal_logs.get(state.timestamp),
            )
        )
    guessed_round = _guess_round_name_from_products(parsed_products, round_name)
    artifact.metadata["round_name"] = guessed_round
    artifact.run_summaries[0] = RunSummaryRecord(
        run_id=artifact.run_summaries[0].run_id,
        source_file=artifact.run_summaries[0].source_file,
        round_name=guessed_round,
        total_profit=artifact.run_summaries[0].total_profit,
        final_positions=artifact.run_summaries[0].final_positions,
        graph_points=artifact.run_summaries[0].graph_points,
        notes=artifact.run_summaries[0].notes,
    )

    trade_rows = raw.get("tradeHistory", [])
    parsed_trades = _trade_rows_from_iterable(trade_rows, round_name=guessed_round, day=0)
    artifact.market_trades.extend(parsed_trades)
    for trade in parsed_trades:
        artifact.run_executions.append(
            RunExecutionRecord(
                run_id=run_id,
                timestamp=trade.timestamp,
                trade_index=trade.trade_index,
                symbol=trade.symbol,
                side=_infer_execution_side(trade.buyer, trade.seller),
                price=trade.price,
                quantity=trade.quantity,
                buyer=trade.buyer,
                seller=trade.seller,
            )
        )
    return artifact


def load_any(path: str | Path) -> ParsedArtifact:
    source_path = Path(path).resolve()
    suffix = source_path.suffix.lower()
    if suffix == ".csv":
        with source_path.open() as handle:
            header = handle.readline().strip().split(";")
        columns = {column.strip() for column in header if column.strip()}
        if {"product", "mid_price"} <= columns:
            return load_price_csv(source_path)
        if {"symbol", "currency", "price", "quantity"} <= columns:
            return load_trade_csv(source_path)
        raise ValueError(f"Unsupported CSV schema in {source_path}")
    if suffix == ".json":
        return load_run_json(source_path)
    if suffix == ".log":
        return load_submission_log(source_path)
    raise ValueError(f"Unsupported file type: {source_path}")
