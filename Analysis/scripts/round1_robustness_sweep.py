from __future__ import annotations

import ast
import csv
import json
import math
import os
import pprint
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[2]
BASE_BOT = ROOT / "Bots/Round1/TradervR1_54.py"
SAFE_BOT = ROOT / "Bots/Round1/TradervR1_52.py"
ROBUST_DIR = ROOT / "Bots/Round1/robustness"
OUTPUT_ROOT = ROOT / "Analysis/output"
CLI = [
    str(ROOT / ".venv-traderfactory/bin/python"),
    "-m",
    "trader_factory.cli",
    "deterministic",
]

ASH_CLASS_TEMPLATE = '''
class AshCoatedOsmiumTrader:
    """
    Robustness sweep engine for Osmium.
    The defaults replicate the current local-fair / aggressive trunk, while the
    optional flags let us test robustness ideas without changing Pepper.
    """

    def __init__(self, params: dict) -> None:
        self.p = params

    def _stable_mid(self, book: Book) -> float:
        bid_levels = book.buy_levels[:3]
        ask_levels = book.sell_levels[:3]
        bid_vol = sum(v for _, v in bid_levels)
        ask_vol = sum(v for _, v in ask_levels)
        if bid_vol <= 0 or ask_vol <= 0:
            return book.mid
        popular_bid = sum(px * vol for px, vol in bid_levels) / bid_vol
        popular_ask = sum(px * vol for px, vol in ask_levels) / ask_vol
        wall_bid = max(bid_levels, key=lambda x: (x[1], x[0]))[0]
        wall_ask = min(ask_levels, key=lambda x: (-x[1], x[0]))[0]
        popular_mid = (popular_bid + popular_ask) / 2.0
        wall_mid = (wall_bid + wall_ask) / 2.0
        return (
            (1.0 - float(self.p["WALL_MID_BLEND"])) * popular_mid
            + float(self.p["WALL_MID_BLEND"]) * wall_mid
        )

    def _slow_fair(self, book: Book) -> float:
        stable_mid = self._stable_mid(book)
        return (
            float(self.p["ANCHOR_WEIGHT"]) * float(self.p["REFERENCE_PRICE"])
            + float(self.p["STABLE_MID_WEIGHT"]) * stable_mid
        )

    def _fast_signal(self, book: Book) -> float:
        depth = max(float(self.p["DEPTH_FLOOR"]), float(book.best_bid_vol + book.best_ask_vol))
        beta = float(self.p["DEPTH_IMPACT_SCALE"]) / depth
        return (
            float(self.p["LOCAL_MICRO_WEIGHT"]) * (book.micro - book.mid)
            + (beta + float(self.p["LOCAL_IMBALANCE_BIAS"])) * book.imbalance
        )

    def _fair_value(self, book: Book) -> Tuple[float, float, float]:
        slow_fair = self._slow_fair(book)
        fast_signal = self._fast_signal(book)
        split_style = self.p.get("SPLIT_FAIR_STYLE", "none")
        fast_clip = float(self.p.get("FAST_SIGNAL_CLIP", 2.0))
        clipped = clamp(fast_signal, -fast_clip, fast_clip)
        if split_style == "blend":
            reservation_fair = slow_fair + float(self.p.get("FAST_RESERVATION_WEIGHT", 0.35)) * clipped
            take_signal = float(self.p.get("FAST_TAKE_WEIGHT", 1.0)) * clipped
            quote_signal = float(self.p.get("FAST_QUOTE_WEIGHT", 0.6)) * clipped
        elif split_style == "guarded":
            reservation_fair = slow_fair + float(self.p.get("FAST_RESERVATION_WEIGHT", 0.15)) * clipped
            take_signal = float(self.p.get("FAST_TAKE_WEIGHT", 0.9)) * clipped
            quote_signal = float(self.p.get("FAST_QUOTE_WEIGHT", 0.4)) * clipped
        else:
            reservation_fair = slow_fair + fast_signal
            take_signal = 0.0
            quote_signal = 0.0
        return reservation_fair, take_signal, quote_signal

    def _reservation(self, fair: float, projected_pos: int) -> float:
        inv_ratio = projected_pos / float(PRODUCT_LIMITS["ASH_COATED_OSMIUM"])
        inv_shift = float(self.p["INVENTORY_SKEW"]) * projected_pos
        inv_shift += float(self.p["INVENTORY_CURVE"]) * (inv_ratio ** 3)
        return fair - inv_shift

    def _mode(
        self,
        book: Book,
        pos: int,
        soft: int,
        bid_toxic: bool,
        ask_toxic: bool,
        buy_edge: float,
        sell_edge: float,
    ) -> str:
        if self.p.get("REGIME_STYLE", "none") == "none":
            return "normal"

        clear_buffer = int(self.p.get("CLEAR_BUFFER", 6))
        dislocation_edge = float(self.p.get("DISLOCATION_EDGE", 2.6))
        weak_edge = float(self.p.get("CLEAR_EDGE_LIMIT", 0.8))
        healthy_depth = float(self.p.get("CALM_DEPTH_MIN", 24.0))
        normal_spread = float(self.p.get("CALM_SPREAD_MAX", 15.0))

        if abs(pos) >= soft + clear_buffer and max(buy_edge, sell_edge) <= weak_edge:
            return "inventory_clear"
        if bid_toxic or ask_toxic:
            return "toxic_defense"
        if max(buy_edge, sell_edge) >= dislocation_edge:
            return "dislocation_take"
        if (
            book.spread_val <= normal_spread
            and (book.best_bid_vol + book.best_ask_vol) >= healthy_depth
            and abs(book.imbalance) <= float(self.p.get("CALM_IMBALANCE_MAX", 0.14))
        ):
            return "calm_mm"
        return "normal"

    def _size_mult(
        self,
        side: str,
        book: Book,
        pos: int,
        soft: int,
        bid_toxic: bool,
        ask_toxic: bool,
        mode: str,
    ) -> float:
        style = self.p.get("SIZE_STYLE", "none")
        if style == "none":
            return 1.0

        mult = 1.0
        if book.spread_val >= float(self.p.get("WIDE_SPREAD", 18.0)):
            mult -= 0.12
        if side == "buy" and book.imbalance < -float(self.p.get("ADVERSE_IMBALANCE", 0.2)):
            mult -= 0.12
        if side == "sell" and book.imbalance > float(self.p.get("ADVERSE_IMBALANCE", 0.2)):
            mult -= 0.12
        if side == "buy" and bid_toxic:
            mult -= 0.18
        if side == "sell" and ask_toxic:
            mult -= 0.18
        if side == "buy" and pos >= soft:
            mult -= 0.18
        if side == "sell" and pos <= -soft:
            mult -= 0.18
        if mode == "calm_mm":
            mult += 0.10
        elif mode == "inventory_clear":
            if side == "buy" and pos > 0:
                mult -= 0.22
            if side == "sell" and pos < 0:
                mult -= 0.22
        if style == "front_only":
            return clamp(mult, 0.55, 1.15)
        return clamp(mult, 0.50, 1.20)

    def build_orders(self, state: TradingState) -> List[Order]:
        if not self.p.get("ENABLED", True):
            return []
        book = Book(state.order_depths.get("ASH_COATED_OSMIUM"))
        if not book.valid:
            return []
        position = int(state.position.get("ASH_COATED_OSMIUM", 0))
        mgr = Manager("ASH_COATED_OSMIUM", position, PRODUCT_LIMITS["ASH_COATED_OSMIUM"])

        reservation_fair, take_signal, quote_signal = self._fair_value(book)
        reservation = self._reservation(reservation_fair, mgr.projected())

        adverse = float(self.p["ADVERSE_IMBALANCE"])
        strong = float(self.p["STRONG_IMBALANCE"])
        bid_toxic = book.imbalance < -adverse and book.micro < book.mid
        ask_toxic = book.imbalance > adverse and book.micro > book.mid
        buy_edge_needed = float(self.p.get("TOXIC_TAKE_EDGE", 1.8)) if bid_toxic else float(self.p.get("NORMAL_TAKE_EDGE", 1.3))
        sell_edge_needed = float(self.p.get("TOXIC_TAKE_EDGE", 1.8)) if ask_toxic else float(self.p.get("NORMAL_TAKE_EDGE", 1.3))

        take_reservation = reservation + take_signal
        buy_edge = take_reservation - book.best_ask
        sell_edge = book.best_bid - take_reservation
        soft = int(self.p["SOFT_LIMIT"])
        mode = self._mode(book, mgr.projected(), soft, bid_toxic, ask_toxic, buy_edge, sell_edge)

        allow_taking = True
        if self.p.get("REGIME_STYLE", "none") in {"light", "full"} and mode not in {"dislocation_take", "normal", "calm_mm"}:
            allow_taking = False

        take_levels = [
            (float(self.p["TAKE_L1_EDGE"]), int(self.p["TAKE_L1_SIZE"])),
            (float(self.p["TAKE_L2_EDGE"]), int(self.p["TAKE_L2_SIZE"])),
            (float(self.p["TAKE_L3_EDGE"]), int(self.p["TAKE_L3_SIZE"])),
        ]

        if allow_taking:
            take_buy = 0
            for edge_thr, clip in take_levels:
                if buy_edge >= max(edge_thr, buy_edge_needed):
                    take_buy = clip
            if take_buy > 0:
                pos = mgr.projected()
                if pos >= soft:
                    take_buy = max(0, take_buy - 4)
                if mode == "inventory_clear" and pos > 0:
                    take_buy = 0
                mgr.buy(book.best_ask, min(book.best_ask_vol, take_buy))

            take_sell = 0
            for edge_thr, clip in take_levels:
                if sell_edge >= max(edge_thr, sell_edge_needed):
                    take_sell = clip
            if take_sell > 0:
                pos = mgr.projected()
                if pos <= -soft:
                    take_sell = max(0, take_sell - 4)
                if mode == "inventory_clear" and pos < 0:
                    take_sell = 0
                mgr.sell(book.best_bid, min(book.best_bid_vol, take_sell))

        base_edge = float(self.p["BASE_EDGE"])
        buy_qe = sell_qe = base_edge
        if book.spread_val <= 14:
            buy_qe -= 0.7
            sell_qe -= 0.7
        elif book.spread_val >= 18:
            buy_qe += 0.7
            sell_qe += 0.7
        if book.imbalance > strong:
            buy_qe -= 0.4
            sell_qe += 0.2
        elif book.imbalance < -strong:
            buy_qe += 0.2
            sell_qe -= 0.4
        if bid_toxic:
            buy_qe += 1.0
        if ask_toxic:
            sell_qe += 1.0
        pos = mgr.projected()
        if pos >= soft:
            buy_qe += 1.2
            sell_qe -= 0.8
        elif pos <= -soft:
            buy_qe -= 0.8
            sell_qe += 1.2

        if self.p.get("REGIME_STYLE", "none") == "full":
            if mode == "calm_mm":
                buy_qe -= 0.20
                sell_qe -= 0.20
            elif mode == "toxic_defense":
                buy_qe += 0.45
                sell_qe += 0.45
            elif mode == "inventory_clear":
                if pos > 0:
                    buy_qe += 0.60
                    sell_qe -= 0.35
                elif pos < 0:
                    buy_qe -= 0.35
                    sell_qe += 0.60

        buy_qe = max(float(self.p["MIN_QUOTE_EDGE"]), buy_qe)
        sell_qe = max(float(self.p["MIN_QUOTE_EDGE"]), sell_qe)

        quote_mid = reservation + quote_signal
        join_edge = float(self.p["JOIN_EDGE"])
        front_buy = int(round(quote_mid - buy_qe))
        front_sell = int(round(quote_mid + sell_qe))

        if self.p.get("ALLOW_JOIN", True):
            for price, _ in book.buy_levels[:2]:
                if quote_mid - price >= buy_qe:
                    front_buy = price if quote_mid - price <= join_edge else price + 1
                    break
            for price, _ in book.sell_levels[:2]:
                if price - quote_mid >= sell_qe:
                    front_sell = price if price - quote_mid <= join_edge else price - 1
                    break

        front_buy = min(front_buy, book.best_ask - 1)
        front_sell = max(front_sell, book.best_bid + 1)
        back_buy = min(front_buy - 2, book.best_ask - 1)
        back_sell = max(front_sell + 2, book.best_bid + 1)

        allow_bid = not (bid_toxic and pos > 8) and pos < soft + 6
        allow_ask = not (ask_toxic and pos < -8) and pos > -(soft + 6)
        if self.p.get("REGIME_STYLE", "none") in {"light", "full"}:
            if mode == "toxic_defense":
                if bid_toxic:
                    allow_bid = False
                if ask_toxic:
                    allow_ask = False
            elif mode == "inventory_clear":
                if pos > 0:
                    allow_bid = False
                elif pos < 0:
                    allow_ask = False

        front_sz = int(self.p["FRONT_SIZE"])
        back_sz = int(self.p["BACK_SIZE"])
        buy_mult = self._size_mult("buy", book, pos, soft, bid_toxic, ask_toxic, mode)
        sell_mult = self._size_mult("sell", book, pos, soft, bid_toxic, ask_toxic, mode)
        if self.p.get("SIZE_STYLE", "none") == "front_only":
            buy_front_sz = max(2, int(round(front_sz * buy_mult)))
            sell_front_sz = max(2, int(round(front_sz * sell_mult)))
            buy_back_sz = back_sz
            sell_back_sz = back_sz
        else:
            buy_front_sz = max(2, int(round(front_sz * buy_mult)))
            sell_front_sz = max(2, int(round(front_sz * sell_mult)))
            buy_back_sz = max(1, int(round(back_sz * buy_mult)))
            sell_back_sz = max(1, int(round(back_sz * sell_mult)))

        if self.p.get("REGIME_STYLE", "none") == "full" and mode == "calm_mm":
            buy_front_sz += 1
            sell_front_sz += 1

        if allow_bid and front_buy < book.best_ask and front_buy > 0:
            mgr.buy(front_buy, buy_front_sz)
            if back_buy > 0 and back_buy < book.best_ask:
                mgr.buy(back_buy, buy_back_sz)
        if allow_ask and front_sell > book.best_bid:
            mgr.sell(front_sell, sell_front_sz)
            if back_sell > book.best_bid:
                mgr.sell(back_sell, sell_back_sz)

        return mgr.orders
'''


@dataclass
class VariantSpec:
    name: str
    note: str
    ash_updates: Dict[str, object]
    ipr_updates: Dict[str, object]


def _extract_block(source: str, name: str, next_marker: str) -> str:
    pattern = rf"{name} = (\{{.*?\n\}})\n+{re.escape(next_marker)}"
    match = re.search(pattern, source, re.S)
    if not match:
        raise RuntimeError(f"Could not find block for {name}")
    return match.group(1)


def _replace_block(source: str, name: str, next_marker: str, replacement: str) -> str:
    pattern = rf"{name} = \{{.*?\n\}}\n+{re.escape(next_marker)}"
    return re.sub(
        pattern,
        f"{name} = {replacement}\n\n{next_marker}",
        source,
        flags=re.S,
    )


def _replace_ash_class(source: str, replacement: str) -> str:
    pattern = r"class AshCoatedOsmiumTrader:.*?(?=\n\n# ── INTARIAN_PEPPER_ROOT trader)"
    return re.sub(pattern, replacement.strip(), source, flags=re.S)


def format_dict_literal(data: Dict[str, object]) -> str:
    formatted = pprint.pformat(data, width=100, sort_dicts=False)
    return formatted


def load_base_components() -> Tuple[str, Dict[str, object], Dict[str, object]]:
    source = BASE_BOT.read_text()
    ash_block = _extract_block(source, "DEFAULT_ASH_PARAMS", "# ── INTARIAN_PEPPER_ROOT params")
    ipr_block = _extract_block(source, "DEFAULT_IPR_PARAMS", "# ── Shared helpers")
    ash_params = ast.literal_eval(ash_block)
    ipr_params = ast.literal_eval(ipr_block)
    return source, ash_params, ipr_params


def build_source(base_source: str, ash_params: Dict[str, object], ipr_params: Dict[str, object]) -> str:
    source = _replace_block(
        base_source,
        "DEFAULT_ASH_PARAMS",
        "# ── INTARIAN_PEPPER_ROOT params",
        format_dict_literal(ash_params),
    )
    source = _replace_block(
        source,
        "DEFAULT_IPR_PARAMS",
        "# ── Shared helpers",
        format_dict_literal(ipr_params),
    )
    source = _replace_ash_class(source, ASH_CLASS_TEMPLATE)
    return source


def candidate_path(name: str) -> Path:
    return ROBUST_DIR / f"{name}.py"


def write_variant(name: str, source: str) -> Path:
    path = candidate_path(name)
    path.write_text(source)
    return path


def run_deterministic(bot_path: Path, day: int) -> Path:
    subprocess.run(
        CLI
        + [
            str(bot_path),
            "--day",
            str(day),
            "--data-root",
            "Data/ROUND_1",
            "--dataset-tag",
            "round_1",
            "--engine",
            "rust",
        ],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": "TraderFactory"},
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return ROOT / f"TraderFactory/generated/runs/deterministic/rust/{bot_path.stem}_day_{day}"


def parse_submission_log(run_dir: Path) -> Dict[str, object]:
    data = json.loads((run_dir / "submission.log").read_text())
    activities = data["activitiesLog"]
    trades = data.get("tradeHistory", [])

    product_series: Dict[str, List[Tuple[int, float]]] = {
        "ASH_COATED_OSMIUM": [],
        "INTARIAN_PEPPER_ROOT": [],
    }
    for line in activities.splitlines()[1:]:
        parts = line.split(";")
        if len(parts) < 18:
            continue
        timestamp = int(parts[1])
        product = parts[2]
        pnl = float(parts[-1])
        if product in product_series:
            product_series[product].append((timestamp, pnl))

    timestamps = sorted({ts for rows in product_series.values() for ts, _ in rows})
    total_series: List[Tuple[int, float]] = []
    by_product = {prod: dict(rows) for prod, rows in product_series.items()}
    for ts in timestamps:
        total = sum(by_product[prod].get(ts, 0.0) for prod in by_product)
        total_series.append((ts, total))

    def max_drawdown(series: List[Tuple[int, float]]) -> float:
        peak = -10**18
        worst = 0.0
        for _, value in series:
            peak = max(peak, value)
            worst = max(worst, peak - value)
        return worst

    def first_positive(series: List[Tuple[int, float]]) -> Optional[int]:
        for ts, value in series:
            if value > 0:
                return ts
        return None

    early_cutoff = 250000
    early_series = [(ts, value) for ts, value in total_series if ts <= early_cutoff]
    positions = {"ASH_COATED_OSMIUM": 0, "INTARIAN_PEPPER_ROOT": 0}
    pepper_buy_qty = pepper_buy_notional = 0.0
    for trade in trades:
        symbol = trade.get("symbol")
        qty = int(trade.get("quantity", 0))
        price = float(trade.get("price", 0))
        if symbol not in positions:
            continue
        if trade.get("buyer") == "SUBMISSION":
            positions[symbol] += qty
            if symbol == "INTARIAN_PEPPER_ROOT":
                pepper_buy_qty += qty
                pepper_buy_notional += qty * price
        if trade.get("seller") == "SUBMISSION":
            positions[symbol] -= qty

    pepper_avg_buy = pepper_buy_notional / pepper_buy_qty if pepper_buy_qty else None
    return {
        "early_drawdown": max_drawdown(early_series or total_series),
        "max_drawdown": max_drawdown(total_series),
        "time_to_positive_total": first_positive(total_series),
        "time_to_positive_ash": first_positive(product_series["ASH_COATED_OSMIUM"]),
        "time_to_positive_pepper": first_positive(product_series["INTARIAN_PEPPER_ROOT"]),
        "final_positions": positions,
        "pepper_avg_buy": pepper_avg_buy,
    }


def evaluate_bot(bot_path: Path) -> Dict[str, object]:
    totals = {
        "name": bot_path.stem,
        "path": str(bot_path),
        "total": 0.0,
        "ash_total": 0.0,
        "pepper_total": 0.0,
        "trade_count": 0,
        "worst_early_drawdown": 0.0,
        "worst_drawdown": 0.0,
        "day_rows": [],
    }
    pepper_avg_prices: List[float] = []
    for day in [-2, -1, 0]:
        run_dir = run_deterministic(bot_path, day)
        metrics = json.loads((run_dir / "metrics.json").read_text())
        extra = parse_submission_log(run_dir)
        final_total = float(metrics["final_pnl_total"])
        final_pnl = metrics["final_pnl_by_product"]
        trade_count = int(metrics["own_trade_count"])
        day_row = {
            "day": day,
            "total": final_total,
            "ash": float(final_pnl["ASH_COATED_OSMIUM"]),
            "pepper": float(final_pnl["INTARIAN_PEPPER_ROOT"]),
            "trade_count": trade_count,
            "early_drawdown": float(extra["early_drawdown"]),
            "max_drawdown": float(extra["max_drawdown"]),
            "time_to_positive_ash": extra["time_to_positive_ash"],
            "time_to_positive_pepper": extra["time_to_positive_pepper"],
            "final_pos_ash": int(extra["final_positions"]["ASH_COATED_OSMIUM"]),
            "final_pos_pepper": int(extra["final_positions"]["INTARIAN_PEPPER_ROOT"]),
            "pepper_avg_buy": extra["pepper_avg_buy"],
        }
        totals["day_rows"].append(day_row)
        totals["total"] += day_row["total"]
        totals["ash_total"] += day_row["ash"]
        totals["pepper_total"] += day_row["pepper"]
        totals["trade_count"] += day_row["trade_count"]
        totals["worst_early_drawdown"] = max(totals["worst_early_drawdown"], day_row["early_drawdown"])
        totals["worst_drawdown"] = max(totals["worst_drawdown"], day_row["max_drawdown"])
        if day_row["pepper_avg_buy"] is not None:
            pepper_avg_prices.append(day_row["pepper_avg_buy"])
    totals["pepper_avg_buy"] = sum(pepper_avg_prices) / len(pepper_avg_prices) if pepper_avg_prices else None
    return totals


def choose_stage_winner(rows: List[Dict[str, object]], base_row: Dict[str, object]) -> Dict[str, object]:
    eligible = [
        row
        for row in rows
        if row["pepper_total"] >= base_row["pepper_total"] - 10.0
        and row["total"] >= base_row["total"] - 300.0
    ]
    pool = eligible or rows
    return sorted(pool, key=lambda row: (row["total"], -row["worst_early_drawdown"]), reverse=True)[0]


def round_values_clean(params: Dict[str, object], keys: Iterable[str]) -> Dict[str, object]:
    rounded = dict(params)
    for key in keys:
        value = params[key]
        if isinstance(value, float):
            rounded[key] = round(value, 2)
    return rounded


def round_values_coarse(params: Dict[str, object]) -> Dict[str, object]:
    rounded = dict(params)
    replacements = {
        "ANCHOR_WEIGHT": 0.5,
        "STABLE_MID_WEIGHT": 0.5,
        "WALL_MID_BLEND": 0.25,
        "DEPTH_IMPACT_SCALE": 35.0,
        "INVENTORY_SKEW": 0.07,
        "INVENTORY_CURVE": 2.5,
        "JOIN_EDGE": 1.25,
        "SOFT_LIMIT": 64,
    }
    rounded.update(replacements)
    return rounded


def make_stage_a_specs(base_ash: Dict[str, object]) -> List[VariantSpec]:
    clean = round_values_clean(
        base_ash,
        [
            "ANCHOR_WEIGHT",
            "STABLE_MID_WEIGHT",
            "WALL_MID_BLEND",
            "DEPTH_IMPACT_SCALE",
            "INVENTORY_SKEW",
            "INVENTORY_CURVE",
            "JOIN_EDGE",
            "SOFT_LIMIT",
        ],
    )
    return [
        VariantSpec(
            "TradervR1_R55_OA1_light",
            "De-risk Osmium aggression lightly",
            {
                "BASE_EDGE": -0.5,
                "MIN_QUOTE_EDGE": float(base_ash["MIN_QUOTE_EDGE"]) + 0.25,
                "FRONT_SIZE": max(2, int(round(float(base_ash["FRONT_SIZE"]) - 1))),
                "SOFT_LIMIT": max(20, int(round(float(base_ash["SOFT_LIMIT"]) - 4))),
            },
            {},
        ),
        VariantSpec(
            "TradervR1_R55_OA2_medium",
            "De-risk Osmium aggression more materially",
            {
                "BASE_EDGE": -0.25,
                "MIN_QUOTE_EDGE": float(base_ash["MIN_QUOTE_EDGE"]) + 0.5,
                "FRONT_SIZE": max(2, int(round(float(base_ash["FRONT_SIZE"]) - 2))),
                "SOFT_LIMIT": max(20, int(round(float(base_ash["SOFT_LIMIT"]) - 6))),
            },
            {},
        ),
        VariantSpec(
            "TradervR1_R55_OA3_shape_only",
            "Keep aggression shape but soften thresholds",
            {
                "BASE_EDGE": -0.75,
                "MIN_QUOTE_EDGE": float(base_ash["MIN_QUOTE_EDGE"]) + 0.15,
                "TAKE_L1_EDGE": max(float(base_ash["TAKE_L1_EDGE"]), 1.2),
                "TAKE_L2_EDGE": max(float(base_ash["TAKE_L2_EDGE"]), 1.0),
                "TAKE_L3_EDGE": max(float(base_ash["TAKE_L3_EDGE"]), 4.2),
            },
            {},
        ),
        VariantSpec(
            "TradervR1_R56_OC1_clean",
            "Clean rounding pass on Osmium constants",
            clean,
            {},
        ),
        VariantSpec(
            "TradervR1_R56_OC2_coarse",
            "Coarse rounding pass on Osmium constants",
            round_values_coarse(base_ash),
            {},
        ),
        VariantSpec(
            "TradervR1_R57_OL1_soft",
            "Soft monotonic take ladder",
            {
                "TAKE_L1_EDGE": 1.0,
                "TAKE_L2_EDGE": 1.8,
                "TAKE_L3_EDGE": 4.2,
                "TAKE_L1_SIZE": 6,
                "TAKE_L2_SIZE": 10,
                "TAKE_L3_SIZE": 16,
            },
            {},
        ),
        VariantSpec(
            "TradervR1_R57_OL2_balanced",
            "Balanced monotonic take ladder",
            {
                "TAKE_L1_EDGE": 1.1,
                "TAKE_L2_EDGE": 2.3,
                "TAKE_L3_EDGE": 4.8,
                "TAKE_L1_SIZE": 5,
                "TAKE_L2_SIZE": 10,
                "TAKE_L3_SIZE": 15,
            },
            {},
        ),
        VariantSpec(
            "TradervR1_R57_OL3_safe",
            "Safer monotonic take ladder",
            {
                "TAKE_L1_EDGE": 1.4,
                "TAKE_L2_EDGE": 2.8,
                "TAKE_L3_EDGE": 5.2,
                "TAKE_L1_SIZE": 4,
                "TAKE_L2_SIZE": 8,
                "TAKE_L3_SIZE": 12,
            },
            {},
        ),
        VariantSpec(
            "TradervR1_R59_OR1_light",
            "Light regime gating on side shutdowns and take permission",
            {
                "REGIME_STYLE": "light",
                "DISLOCATION_EDGE": 2.4,
                "CLEAR_EDGE_LIMIT": 0.9,
                "CLEAR_BUFFER": 6,
                "CALM_DEPTH_MIN": 24.0,
                "CALM_SPREAD_MAX": 15.0,
            },
            {},
        ),
        VariantSpec(
            "TradervR1_R60_OS1_mild",
            "Mild state-dependent size scaling",
            {
                "SIZE_STYLE": "mild",
                "WIDE_SPREAD": 18.0,
            },
            {},
        ),
    ]


def make_stage_b_specs(base_ash: Dict[str, object]) -> List[VariantSpec]:
    return [
        VariantSpec(
            "TradervR1_R58_OF1_blend",
            "Slow fair with bounded fast signal blend",
            {
                "SPLIT_FAIR_STYLE": "blend",
                "FAST_SIGNAL_CLIP": 2.0,
                "FAST_RESERVATION_WEIGHT": 0.35,
                "FAST_TAKE_WEIGHT": 1.0,
                "FAST_QUOTE_WEIGHT": 0.6,
            },
            {},
        ),
        VariantSpec(
            "TradervR1_R58_OF2_guarded",
            "Slow fair dominant with guarded fast signal",
            {
                "SPLIT_FAIR_STYLE": "guarded",
                "FAST_SIGNAL_CLIP": 1.8,
                "FAST_RESERVATION_WEIGHT": 0.15,
                "FAST_TAKE_WEIGHT": 0.9,
                "FAST_QUOTE_WEIGHT": 0.4,
            },
            {},
        ),
        VariantSpec(
            "TradervR1_R59_OR2_full",
            "Full but lightweight regime gating",
            {
                "REGIME_STYLE": "full",
                "DISLOCATION_EDGE": 2.5,
                "CLEAR_EDGE_LIMIT": 0.9,
                "CLEAR_BUFFER": 6,
                "CALM_DEPTH_MIN": 24.0,
                "CALM_SPREAD_MAX": 15.0,
            },
            {},
        ),
        VariantSpec(
            "TradervR1_R60_OS2_front_only",
            "State-dependent front-size only",
            {
                "SIZE_STYLE": "front_only",
                "WIDE_SPREAD": 18.0,
            },
            {},
        ),
    ]


def make_stage_c_specs(base_ash: Dict[str, object], base_ipr: Dict[str, object]) -> List[VariantSpec]:
    return [
        VariantSpec(
            "TradervR1_R61_PC1_light",
            "Light Pepper parameter coarsening",
            {},
            {
                "LOOKAHEAD_BONUS": round(float(base_ipr["LOOKAHEAD_BONUS"]), 2),
                "BASE_CARRY": round(float(base_ipr["BASE_CARRY"]), 2),
                "EARLY_LONG_BIAS": round(float(base_ipr["EARLY_LONG_BIAS"]), 2),
                "CHEAP_ACCUM_END": round(float(base_ipr["CHEAP_ACCUM_END"]), 2),
                "CHEAP_ACCUM_TAKE_PENALTY": round(float(base_ipr["CHEAP_ACCUM_TAKE_PENALTY"]), 2),
                "CHEAP_ACCUM_QUOTE_EDGE_BONUS": round(float(base_ipr["CHEAP_ACCUM_QUOTE_EDGE_BONUS"]), 2),
                "CHEAP_ACCUM_Z_RELAX": round(float(base_ipr["CHEAP_ACCUM_Z_RELAX"]), 2),
                "CHEAP_ACCUM_TARGET_BUFFER": int(round(float(base_ipr["CHEAP_ACCUM_TARGET_BUFFER"]))),
            },
        ),
        VariantSpec(
            "TradervR1_R61_PC2_coarse",
            "Coarser Pepper parameter cleanup",
            {},
            {
                "LOOKAHEAD_BONUS": 5.0,
                "BASE_CARRY": 8.0,
                "EARLY_LONG_BIAS": 43.0,
                "CHEAP_ACCUM_END": 0.55,
                "CHEAP_ACCUM_TAKE_PENALTY": 0.1,
                "CHEAP_ACCUM_QUOTE_EDGE_BONUS": 0.45,
                "CHEAP_ACCUM_Z_RELAX": -0.55,
                "CHEAP_ACCUM_TARGET_BUFFER": 20,
            },
        ),
        VariantSpec(
            "TradervR1_ABL_wall_mid_off",
            "Ablation: remove wall-mid blend",
            {"WALL_MID_BLEND": 0.0},
            {},
        ),
        VariantSpec(
            "TradervR1_ABL_depth_impact_off",
            "Ablation: remove depth-impact scale",
            {"DEPTH_IMPACT_SCALE": 0.0},
            {},
        ),
        VariantSpec(
            "TradervR1_ABL_linear_inventory",
            "Ablation: linearize inventory curve",
            {"INVENTORY_CURVE": 0.0},
            {},
        ),
        VariantSpec(
            "TradervR1_ABL_pepper_cheap_accum_off",
            "Ablation: disable Pepper cheap accumulation overlay",
            {},
            {
                "CHEAP_ACCUM_END": 0.0,
                "CHEAP_ACCUM_TAKE_PENALTY": 0.0,
                "CHEAP_ACCUM_QUOTE_EDGE_BONUS": 0.0,
                "CHEAP_ACCUM_FRONT_SIZE_BONUS": 0,
                "CHEAP_ACCUM_BACK_SIZE_BONUS": 0,
                "CHEAP_ACCUM_TARGET_BUFFER": int(base_ipr["PASSIVE_BUY_BUFFER"]),
            },
        ),
        VariantSpec(
            "TradervR1_ABL_join_off",
            "Ablation: disable aggressive join behavior",
            {"ALLOW_JOIN": False},
            {},
        ),
    ]


def make_sensitivity_specs(base_ash: Dict[str, object], base_ipr: Dict[str, object]) -> List[VariantSpec]:
    return [
        VariantSpec(
            "TradervR1_SENS_up",
            "Tiny aggression-up perturbation around winner",
            {
                "BASE_EDGE": float(base_ash["BASE_EDGE"]) - 0.08,
                "MIN_QUOTE_EDGE": max(0.5, float(base_ash["MIN_QUOTE_EDGE"]) - 0.08),
                "TAKE_L1_EDGE": max(0.25, float(base_ash["TAKE_L1_EDGE"]) - 0.10),
            },
            {},
        ),
        VariantSpec(
            "TradervR1_SENS_down",
            "Tiny aggression-down perturbation around winner",
            {
                "BASE_EDGE": float(base_ash["BASE_EDGE"]) + 0.08,
                "MIN_QUOTE_EDGE": float(base_ash["MIN_QUOTE_EDGE"]) + 0.08,
                "TAKE_L1_EDGE": float(base_ash["TAKE_L1_EDGE"]) + 0.10,
            },
            {},
        ),
        VariantSpec(
            "TradervR1_SENS_rounded",
            "Rounded winner sensitivity check",
            round_values_clean(
                base_ash,
                [
                    "ANCHOR_WEIGHT",
                    "STABLE_MID_WEIGHT",
                    "WALL_MID_BLEND",
                    "DEPTH_IMPACT_SCALE",
                    "INVENTORY_SKEW",
                    "INVENTORY_CURVE",
                    "JOIN_EDGE",
                    "SOFT_LIMIT",
                    "BASE_EDGE",
                    "MIN_QUOTE_EDGE",
                    "TAKE_L1_EDGE",
                    "TAKE_L2_EDGE",
                    "TAKE_L3_EDGE",
                ],
            ),
            {
                "LOOKAHEAD_BONUS": round(float(base_ipr["LOOKAHEAD_BONUS"]), 2),
                "BASE_CARRY": round(float(base_ipr["BASE_CARRY"]), 2),
                "EARLY_LONG_BIAS": round(float(base_ipr["EARLY_LONG_BIAS"]), 2),
            },
        ),
    ]


def apply_updates(base_ash: Dict[str, object], base_ipr: Dict[str, object], spec: VariantSpec) -> Tuple[Dict[str, object], Dict[str, object]]:
    ash = dict(base_ash)
    ipr = dict(base_ipr)
    ash.update(spec.ash_updates)
    ipr.update(spec.ipr_updates)
    return ash, ipr


def write_stage_variants(
    base_source: str,
    base_ash: Dict[str, object],
    base_ipr: Dict[str, object],
    specs: List[VariantSpec],
) -> List[Path]:
    paths = []
    for spec in specs:
        ash, ipr = apply_updates(base_ash, base_ipr, spec)
        source = build_source(base_source, ash, ipr)
        paths.append(write_variant(spec.name, source))
    return paths


def rows_to_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def flatten_row(row: Dict[str, object], base_row: Dict[str, object], safe_row: Dict[str, object], stage: str) -> Dict[str, object]:
    flat = {
        "stage": stage,
        "name": row["name"],
        "path": row["path"],
        "total": round(float(row["total"]), 4),
        "delta_vs_v54": round(float(row["total"]) - float(base_row["total"]), 4),
        "delta_vs_v52": round(float(row["total"]) - float(safe_row["total"]), 4),
        "ash_total": round(float(row["ash_total"]), 4),
        "pepper_total": round(float(row["pepper_total"]), 4),
        "trade_count": int(row["trade_count"]),
        "worst_early_drawdown": round(float(row["worst_early_drawdown"]), 4),
        "worst_drawdown": round(float(row["worst_drawdown"]), 4),
        "pepper_avg_buy": round(float(row["pepper_avg_buy"]), 6) if row["pepper_avg_buy"] is not None else None,
    }
    for day_row in row["day_rows"]:
        suffix = str(day_row["day"]).replace("-", "m")
        flat[f"day_{suffix}_total"] = round(float(day_row["total"]), 4)
        flat[f"day_{suffix}_ash"] = round(float(day_row["ash"]), 4)
        flat[f"day_{suffix}_pepper"] = round(float(day_row["pepper"]), 4)
        flat[f"day_{suffix}_trades"] = int(day_row["trade_count"])
        flat[f"day_{suffix}_early_dd"] = round(float(day_row["early_drawdown"]), 4)
        flat[f"day_{suffix}_ttp_ash"] = day_row["time_to_positive_ash"]
        flat[f"day_{suffix}_ttp_pepper"] = day_row["time_to_positive_pepper"]
        flat[f"day_{suffix}_final_pos_ash"] = int(day_row["final_pos_ash"])
        flat[f"day_{suffix}_final_pos_pepper"] = int(day_row["final_pos_pepper"])
    return flat


def write_summary(
    out_dir: Path,
    base_row: Dict[str, object],
    safe_row: Dict[str, object],
    stage_winners: List[Tuple[str, Dict[str, object]]],
    final_row: Dict[str, object],
    sensitivity_rows: List[Dict[str, object]],
) -> None:
    lines = [
        "# Round 1 Robustness Sweep",
        "",
        f"Base trunk: `{base_row['name']}` total `{base_row['total']:.1f}`",
        f"Safe control: `{safe_row['name']}` total `{safe_row['total']:.1f}`",
        "",
        "## Stage Winners",
    ]
    for stage, row in stage_winners:
        lines.append(
            f"- `{stage}`: `{row['name']}` total `{row['total']:.1f}`, "
            f"Osmium `{row['ash_total']:.1f}`, Pepper `{row['pepper_total']:.1f}`, "
            f"worst early drawdown `{row['worst_early_drawdown']:.1f}`"
        )
    lines.extend(
        [
            "",
            "## Final Candidate",
            f"- `{final_row['name']}` total `{final_row['total']:.1f}`",
            f"- delta vs `v54`: `{final_row['total'] - base_row['total']:.1f}`",
            f"- delta vs `v52`: `{final_row['total'] - safe_row['total']:.1f}`",
            f"- Osmium `{final_row['ash_total']:.1f}`, Pepper `{final_row['pepper_total']:.1f}`",
            f"- worst early drawdown `{final_row['worst_early_drawdown']:.1f}`",
            f"- Pepper average buy `{final_row['pepper_avg_buy']:.6f}`" if final_row["pepper_avg_buy"] is not None else "- Pepper average buy `n/a`",
            "",
            "## Sensitivity",
        ]
    )
    for row in sensitivity_rows:
        lines.append(
            f"- `{row['name']}` total `{row['total']:.1f}`, delta vs final `{row['total'] - final_row['total']:.1f}`"
        )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    ROBUST_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUTPUT_ROOT / f"round1_robustness_sweep_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    base_source, base_ash, base_ipr = load_base_components()
    base_row = evaluate_bot(BASE_BOT)
    safe_row = evaluate_bot(SAFE_BOT)

    stage_rows: List[Dict[str, object]] = []
    stage_winners: List[Tuple[str, Dict[str, object]]] = []

    current_ash = dict(base_ash)
    current_ipr = dict(base_ipr)

    stages = [
        ("StageA", make_stage_a_specs(current_ash)),
        ("StageB", make_stage_b_specs(current_ash)),
        ("StageC", make_stage_c_specs(current_ash, current_ipr)),
    ]

    current_best_row = base_row
    current_best_source = base_source

    for stage_name, specs in stages:
        if stage_name != "StageA":
            specs = (
                make_stage_b_specs(current_ash)
                if stage_name == "StageB"
                else make_stage_c_specs(current_ash, current_ipr)
            )
        paths = write_stage_variants(current_best_source, current_ash, current_ipr, specs)
        rows = [evaluate_bot(path) for path in paths]
        stage_rows.extend(flatten_row(row, base_row, safe_row, stage_name) for row in rows)
        winner = choose_stage_winner(rows, base_row)
        stage_winners.append((stage_name, winner))
        current_best_row = winner
        current_best_source = Path(winner["path"]).read_text()
        current_ash, current_ipr = apply_updates(current_ash, current_ipr, next(spec for spec in specs if spec.name == winner["name"]))

    sensitivity_specs = make_sensitivity_specs(current_ash, current_ipr)
    sensitivity_paths = write_stage_variants(current_best_source, current_ash, current_ipr, sensitivity_specs)
    sensitivity_rows = [evaluate_bot(path) for path in sensitivity_paths]
    stage_rows.extend(flatten_row(row, base_row, safe_row, "Sensitivity") for row in sensitivity_rows)

    all_candidates = [current_best_row] + sensitivity_rows
    final_row = choose_stage_winner(all_candidates, base_row)

    final_path = Path(final_row["path"])
    promoted = ROOT / "Bots/Round1/TradervR1_55.py"
    shutil.copyfile(final_path, promoted)

    rows_to_csv(out_dir / "leaderboard.csv", sorted(stage_rows, key=lambda row: row["total"], reverse=True))
    write_summary(out_dir, base_row, safe_row, stage_winners, final_row, sensitivity_rows)

    manifest = {
        "base": base_row["name"],
        "safe": safe_row["name"],
        "stage_winners": [(stage, row["name"]) for stage, row in stage_winners],
        "final": final_row["name"],
        "promoted": str(promoted),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
