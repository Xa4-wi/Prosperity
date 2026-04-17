#!/usr/bin/env python3
"""Invest & Expand optimizer.

Usage examples:
  python invest_expand_optimizer.py --speeds "70,70,70,50,40,40,30"
  python invest_expand_optimizer.py --scenarios "0.5|70,70,70,50,40,40,30;0.3|95,20,10;0.2|60,60,60,60"

The script computes the exact best response when opponent Speed bids are known,
and the exact best fixed strategy when you have weighted scenarios.
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence

LN101 = math.log(101)


@dataclass(frozen=True)
class Strategy:
    speed: float
    research_pct: float
    scale_pct: float
    multiplier: float
    rank: int | None
    gross_pnl: float
    net_pnl: float


@dataclass(frozen=True)
class Scenario:
    weight: float
    speeds: List[float]


def research_value(x: float) -> float:
    return 200_000 * math.log(1 + x) / LN101


def scale_value(y: float) -> float:
    return 7 * y / 100


def parse_speed_list(text: str) -> List[float]:
    text = text.strip()
    if not text:
        return []
    parts = [p for p in text.replace(";", ",").replace(" ", ",").split(",") if p]
    values = [float(p) for p in parts]
    if any(v < 0 or v > 100 for v in values):
        raise ValueError("All speeds must be between 0 and 100.")
    return values


def candidate_speeds(opponent_speeds: Sequence[float]) -> List[float]:
    return sorted({0.0, *opponent_speeds})


def rank_and_multiplier(speed: float, opponent_speeds: Sequence[float]) -> tuple[int, float]:
    total_players = len(opponent_speeds) + 1
    rank = 1 + sum(1 for s in opponent_speeds if s > speed)
    if total_players == 1:
        return 1, 0.9
    multiplier = 0.9 - 0.8 * (rank - 1) / (total_players - 1)
    return rank, multiplier


def best_research_split(remaining_budget_pct: float) -> float:
    """Return x* where x is Research % and y = B - x is Scale %.

    Solves u * (1 + ln u) = B + 1 for u = 1 + x using binary search.
    """
    if remaining_budget_pct <= 0:
        return 0.0
    lo, hi = 1.0, remaining_budget_pct + 1.0
    for _ in range(120):
        mid = (lo + hi) / 2
        if mid * (1 + math.log(mid)) > remaining_budget_pct + 1:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2 - 1


def evaluate_full_budget(speed: float, multiplier: float, rank: int | None = None) -> Strategy:
    remaining = 100 - speed
    research_pct = best_research_split(remaining)
    scale_pct = remaining - research_pct
    gross_pnl = multiplier * research_value(research_pct) * scale_value(scale_pct)
    net_pnl = gross_pnl - 50_000  # full budget used: 100% of 50,000 XIRECs
    return Strategy(
        speed=speed,
        research_pct=research_pct,
        scale_pct=scale_pct,
        multiplier=multiplier,
        rank=rank,
        gross_pnl=gross_pnl,
        net_pnl=net_pnl,
    )


def best_response(opponent_speeds: Sequence[float]) -> tuple[Strategy, List[Strategy]]:
    rows: List[Strategy] = []
    for speed in candidate_speeds(opponent_speeds):
        rank, multiplier = rank_and_multiplier(speed, opponent_speeds)
        rows.append(evaluate_full_budget(speed, multiplier, rank=rank))
    rows.sort(key=lambda r: (-r.net_pnl, r.speed))
    return rows[0], rows


def parse_scenarios(text: str) -> List[Scenario]:
    scenarios: List[Scenario] = []
    for raw in [x.strip() for x in text.split(";") if x.strip()]:
        if "|" in raw:
            w_str, speeds_str = raw.split("|", 1)
            weight = float(w_str.strip())
        else:
            weight = 1.0
            speeds_str = raw
        if weight <= 0:
            raise ValueError("Scenario weights must be positive.")
        scenarios.append(Scenario(weight=weight, speeds=parse_speed_list(speeds_str)))
    if not scenarios:
        raise ValueError("Provide at least one scenario.")
    total_weight = sum(s.weight for s in scenarios)
    return [Scenario(weight=s.weight / total_weight, speeds=s.speeds) for s in scenarios]


def best_fixed_strategy_for_scenarios(scenarios: Sequence[Scenario]) -> tuple[Strategy, List[Strategy]]:
    all_candidates = sorted({0.0, *(s for sc in scenarios for s in sc.speeds)})
    rows: List[Strategy] = []
    for speed in all_candidates:
        expected_multiplier = 0.0
        for scenario in scenarios:
            _, multiplier = rank_and_multiplier(speed, scenario.speeds)
            expected_multiplier += scenario.weight * multiplier
        rows.append(evaluate_full_budget(speed, expected_multiplier, rank=None))
    rows.sort(key=lambda r: (-r.net_pnl, r.speed))
    return rows[0], rows


def format_strategy(strategy: Strategy) -> str:
    rank_text = f"#{strategy.rank}" if strategy.rank is not None else "expected"
    return (
        f"Speed={strategy.speed:.2f}% | Research={strategy.research_pct:.4f}% | "
        f"Scale={strategy.scale_pct:.4f}% | Multiplier={strategy.multiplier:.6f} | "
        f"Rank={rank_text} | Gross={strategy.gross_pnl:,.2f} | Net={strategy.net_pnl:,.2f}"
    )


def print_table(rows: Iterable[Strategy], limit: int = 20) -> None:
    rows = list(rows)[:limit]
    print("\nTop candidates:")
    print("-" * 110)
    print(f"{'Speed %':>8} {'Research %':>12} {'Scale %':>10} {'Mult':>8} {'Rank':>8} {'Gross':>14} {'Net':>14}")
    print("-" * 110)
    for row in rows:
        rank_text = f"#{row.rank}" if row.rank is not None else "exp"
        print(
            f"{row.speed:8.2f} {row.research_pct:12.4f} {row.scale_pct:10.4f} "
            f"{row.multiplier:8.4f} {rank_text:>8} {row.gross_pnl:14,.2f} {row.net_pnl:14,.2f}"
        )
    print("-" * 110)


def main() -> None:
    parser = argparse.ArgumentParser(description="Optimize the Invest & Expand challenge.")
    parser.add_argument("--speeds", help="Comma-separated opponent Speed bids for exact best response.")
    parser.add_argument(
        "--scenarios",
        help=(
            "Semicolon-separated weighted scenarios. Example: "
            '"0.5|70,70,70,50,40,40,30;0.3|95,20,10;0.2|60,60,60,60"'
        ),
    )
    args = parser.parse_args()

    if args.scenarios:
        scenarios = parse_scenarios(args.scenarios)
        best, rows = best_fixed_strategy_for_scenarios(scenarios)
        print("Best fixed strategy across weighted scenarios:")
        print(format_strategy(best))
        print_table(rows)
        return

    if args.speeds is None:
        args.speeds = input("Enter opponent Speed bids (comma-separated): ").strip()

    opponent_speeds = parse_speed_list(args.speeds)
    best, rows = best_response(opponent_speeds)
    print("Best exact response:")
    print(format_strategy(best))
    print_table(rows)


if __name__ == "__main__":
    main()
