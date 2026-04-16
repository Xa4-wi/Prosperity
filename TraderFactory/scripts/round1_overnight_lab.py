#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import re
import shutil
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from trader_factory.core.paths import ensure_dir
from trader_factory.optimization import run_cmaes
from trader_factory.simulation import run_deterministic, run_monte_carlo


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUND1_DIR = REPO_ROOT / "Bots" / "Round1"
DATA_ROOT = REPO_ROOT / "Data" / "ROUND_1"
DATASET_TAG = "round_1"
DETERMINISTIC_DAYS = (-2, -1, 0)

DEFAULT_CACHE_ROOT = REPO_ROOT / ".cache" / "overnight_lab"
os.environ.setdefault("MPLCONFIGDIR", str(DEFAULT_CACHE_ROOT / "matplotlib"))
os.environ.setdefault("PYTHONPYCACHEPREFIX", str(DEFAULT_CACHE_ROOT / "pycache"))
ensure_dir(Path(os.environ["MPLCONFIGDIR"]))
ensure_dir(Path(os.environ["PYTHONPYCACHEPREFIX"]))


@dataclass(frozen=True)
class MutationRule:
    container: str
    key: str
    step: float
    lower: float
    upper: float
    int_like: bool = False


@dataclass(frozen=True)
class FamilySpec:
    name: str
    description: str
    strategy_refs: tuple[str, ...]
    rules: tuple[MutationRule, ...]


@dataclass
class CandidateSpec:
    name: str
    parent_bot: Path
    parent_name: str
    families: list[str]
    strategy_refs: list[str]
    notes: list[str]
    bot_path: Path | None = None
    changes: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class CandidateEval:
    candidate: CandidateSpec
    deterministic_total: float
    deterministic_by_day: dict[int, float]
    product_pnl_by_day: dict[int, dict[str, float]]
    own_trades_by_day: dict[int, int]
    delta_vs_safe: float
    delta_vs_attack: float
    min_day_delta_vs_safe: float
    daily_delta_range_vs_safe: float
    deterministic_score: float
    mc_summary: dict[str, float] | None = None
    mc_paths: dict[str, str] | None = None
    composite_score: float | None = None


@dataclass
class SessionState:
    output_dir: Path
    started_at: str
    baseline_bot: Path
    attack_bot: Path
    seed_bots: list[Path]
    family_weights: dict[str, float]
    rounds_completed: int = 0
    candidates_seen: int = 0


FAMILY_SPECS: dict[str, FamilySpec] = {
    "ash_attack_tuning": FamilySpec(
        name="ash_attack_tuning",
        description="Push or soften join/improve spread capture around the local-fair Osmium core.",
        strategy_refs=(
            "1.2 Join / Improve Market Making",
            "1.4 Spread-Capture Only MM",
            "3.3 Queue-Aware Market Making",
        ),
        rules=(
            MutationRule("DEFAULT_ASH_PARAMS", "BASE_EDGE", 0.45, -1.5, 2.5),
            MutationRule("DEFAULT_ASH_PARAMS", "TAKE_L1_EDGE", 0.60, -1.5, 3.0),
            MutationRule("DEFAULT_ASH_PARAMS", "TAKE_L2_EDGE", 0.75, 0.5, 6.5),
            MutationRule("DEFAULT_ASH_PARAMS", "TAKE_L3_EDGE", 1.00, 2.0, 10.0),
            MutationRule("DEFAULT_ASH_PARAMS", "MIN_QUOTE_EDGE", 0.55, 1.4, 5.0),
            MutationRule("DEFAULT_ASH_PARAMS", "JOIN_EDGE", 0.35, 1.0, 3.0),
        ),
    ),
    "ash_quality_guard": FamilySpec(
        name="ash_quality_guard",
        description="Tighten or relax toxicity-sensitive quoting and same-side inventory exposure.",
        strategy_refs=(
            "1.3 Inventory-Skewed Market Making",
            "3.3 Queue-Aware Market Making",
        ),
        rules=(
            MutationRule("DEFAULT_ASH_PARAMS", "ADVERSE_IMBALANCE", 0.03, 0.12, 0.30),
            MutationRule("DEFAULT_ASH_PARAMS", "STRONG_IMBALANCE", 0.03, 0.08, 0.24),
            MutationRule("DEFAULT_ASH_PARAMS", "SOFT_LIMIT", 3.0, 55.0, 75.0),
            MutationRule("DEFAULT_ASH_PARAMS", "FRONT_SIZE", 1.25, 12.0, 22.0),
            MutationRule("DEFAULT_ASH_PARAMS", "BACK_SIZE", 0.75, 2.0, 8.0, int_like=True),
        ),
    ),
    "ash_local_fair_blend": FamilySpec(
        name="ash_local_fair_blend",
        description="Shift Osmium between anchor, stable/wall-mid, microprice, and depth-aware imbalance.",
        strategy_refs=(
            "1.1 Static Fair-Value Market Making",
            "1.2 Join / Improve Market Making",
            "3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)",
        ),
        rules=(
            MutationRule("DEFAULT_ASH_PARAMS", "ANCHOR_WEIGHT", 0.07, 0.15, 0.70),
            MutationRule("DEFAULT_ASH_PARAMS", "WALL_MID_BLEND", 0.08, 0.05, 0.65),
            MutationRule("DEFAULT_ASH_PARAMS", "LOCAL_MICRO_WEIGHT", 0.08, 0.05, 0.85),
            MutationRule("DEFAULT_ASH_PARAMS", "LOCAL_IMBALANCE_BIAS", 0.05, 0.0, 0.35),
            MutationRule("DEFAULT_ASH_PARAMS", "DEPTH_IMPACT_SCALE", 10.0, 20.0, 130.0),
            MutationRule("DEFAULT_ASH_PARAMS", "INVENTORY_SKEW", 0.01, 0.05, 0.16),
            MutationRule("DEFAULT_ASH_PARAMS", "INVENTORY_CURVE", 0.45, 0.2, 5.0),
        ),
    ),
    "pepper_entry_quality": FamilySpec(
        name="pepper_entry_quality",
        description="Refine cheap accumulation and anti-chasing on Pepper without changing the drift thesis.",
        strategy_refs=(
            "2.1 Mean Reversion",
            "2.2 Trend Following / Momentum",
        ),
        rules=(
            MutationRule("DEFAULT_IPR_PARAMS", "CHEAP_ACCUM_END", 0.04, 0.35, 0.68),
            MutationRule("DEFAULT_IPR_PARAMS", "CHEAP_ACCUM_TAKE_PENALTY", 0.04, 0.0, 0.45),
            MutationRule("DEFAULT_IPR_PARAMS", "CHEAP_ACCUM_QUOTE_EDGE_BONUS", 0.12, 0.0, 1.0),
            MutationRule("DEFAULT_IPR_PARAMS", "CHEAP_ACCUM_Z_RELAX", 0.08, -1.20, 0.10),
            MutationRule("DEFAULT_IPR_PARAMS", "CHEAP_ACCUM_TARGET_BUFFER", 2.0, 10.0, 28.0, int_like=True),
        ),
    ),
    "pepper_carry_defense": FamilySpec(
        name="pepper_carry_defense",
        description="Protect or monetize Pepper carry more selectively while keeping the deterministic drift engine.",
        strategy_refs=(
            "2.2 Trend Following / Momentum",
            "1.3 Inventory-Skewed Market Making",
        ),
        rules=(
            MutationRule("DEFAULT_IPR_PARAMS", "EARLY_LONG_BIAS", 2.5, 34.0, 52.0),
            MutationRule("DEFAULT_IPR_PARAMS", "ZSCORE_SELL_PENALTY", 0.8, 4.0, 14.0),
            MutationRule("DEFAULT_IPR_PARAMS", "OVEREXTENSION_Z", 0.10, 0.70, 1.45),
            MutationRule("DEFAULT_IPR_PARAMS", "BULLISH_IMBALANCE", 0.02, 0.0, 0.12),
            MutationRule("DEFAULT_IPR_PARAMS", "BASE_TAKE_EDGE", 0.20, 1.8, 3.6),
            MutationRule("DEFAULT_IPR_PARAMS", "BASE_QUOTE_EDGE", 0.30, 3.8, 6.4),
        ),
    ),
}


def _format_number(value: float, *, int_like: bool = False) -> str:
    if int_like:
        return str(int(round(value)))
    rounded = round(float(value), 10)
    if math.isfinite(rounded) and abs(rounded - round(rounded)) < 1e-10:
        return f"{int(round(rounded))}.0"
    return repr(rounded)


def _dict_block(source: str, container: str) -> tuple[int, int, str]:
    marker = re.search(rf"{re.escape(container)}\s*=\s*\{{", source)
    if marker is None:
        raise ValueError(f"Could not find dict block {container}")
    brace_start = source.find("{", marker.start())
    if brace_start == -1:
        raise ValueError(f"Could not find opening brace for {container}")
    depth = 0
    end = brace_start
    for index in range(brace_start, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    return marker.start(), end, source[marker.start() : end]


def _get_dict_value(source: str, container: str, key: str) -> float | None:
    _start, _end, block = _dict_block(source, container)
    match = re.search(rf'"{re.escape(key)}":\s*([\d.eE+\-]+)', block)
    if match is None:
        return None
    return float(match.group(1))


def _set_dict_value(source: str, container: str, key: str, value: float, *, int_like: bool = False) -> str:
    start, end, block = _dict_block(source, container)
    pattern = rf'("{re.escape(key)}":\s*)([^,\n]+)'
    replacement = rf'\g<1>{_format_number(value, int_like=int_like)}'
    updated, count = re.subn(pattern, replacement, block, count=1)
    if count != 1:
        raise ValueError(f"Could not replace {container}.{key}")
    return source[:start] + updated + source[end:]


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _default_output_dir() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return ensure_dir(REPO_ROOT / "Analysis" / "output" / "round1_overnight_lab" / stamp)


def _copy_strategy_reference(output_dir: Path) -> Path:
    src = REPO_ROOT / "TraderFactory" / "references" / "Strategies.txt"
    dst = output_dir / "Strategies.txt"
    shutil.copy2(src, dst)
    return dst


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _seed_bots_from_args(args: argparse.Namespace) -> list[Path]:
    if args.seed_bots:
        return [Path(item).expanduser().resolve() for item in args.seed_bots]
    return [
        (ROUND1_DIR / "TradervR1_34_1.py").resolve(),
        (ROUND1_DIR / "TradervR1_47.py").resolve(),
        (ROUND1_DIR / "TradervR1_47_2.py").resolve(),
        (ROUND1_DIR / "TradervR1_39_4.py").resolve(),
        (ROUND1_DIR / "TradervR1_42_O2_1.py").resolve(),
        (ROUND1_DIR / "TradervR1_42_P1_1.py").resolve(),
    ]


def _evaluate_bot(
    bot_path: Path,
    *,
    out_dir: Path,
    days: tuple[int, ...],
) -> tuple[float, dict[int, float], dict[int, dict[str, float]], dict[int, int]]:
    totals: dict[int, float] = {}
    product: dict[int, dict[str, float]] = {}
    trades: dict[int, int] = {}
    total = 0.0
    for day in days:
        result = run_deterministic(
            bot_path,
            day=day,
            output_dir=out_dir / f"day_{day}",
            data_root=DATA_ROOT,
            dataset_tag=DATASET_TAG,
            engine="rust",
            check=True,
        )
        metrics = {}
        if result.metrics_path and result.metrics_path.exists():
            metrics = json.loads(result.metrics_path.read_text())
        day_total = float(result.final_total_pnl or metrics.get("final_pnl_total", 0.0))
        totals[day] = day_total
        product[day] = dict(metrics.get("final_pnl_by_product", {}))
        trades[day] = int(metrics.get("own_trade_count", 0))
        total += day_total
    return total, totals, product, trades


def _deterministic_score(total_delta_vs_safe: float, min_day_delta_vs_safe: float, day_range: float) -> float:
    return total_delta_vs_safe + 0.35 * min_day_delta_vs_safe - 0.08 * day_range


def _composite_score(
    det_score: float,
    mc_summary: dict[str, float] | None,
    *,
    delta_vs_attack: float,
) -> float:
    score = det_score - 0.08 * max(0.0, -delta_vs_attack)
    if not mc_summary:
        return score
    score += 0.18 * mc_summary.get("mean_delta", 0.0)
    score += 0.22 * mc_summary.get("plausible_mean_delta", 0.0)
    score += 0.14 * mc_summary.get("plausible_p10_delta", 0.0)
    score += 35.0 * mc_summary.get("win_rate", 0.0)
    return score


def _mutate_value(current: float, rule: MutationRule, rng: random.Random, radius: float) -> float:
    trial = current + rng.gauss(0.0, rule.step * radius)
    trial = max(rule.lower, min(rule.upper, trial))
    if rule.int_like:
        return float(int(round(trial)))
    return float(trial)


def _apply_family_mutations(
    source_text: str,
    family: FamilySpec,
    rng: random.Random,
    radius: float,
) -> tuple[str, list[dict[str, Any]], list[str]]:
    patched = source_text
    changes: list[dict[str, Any]] = []
    notes: list[str] = []
    for rule in family.rules:
        current = _get_dict_value(patched, rule.container, rule.key)
        if current is None:
            notes.append(f"Skipped {family.name}:{rule.container}.{rule.key} (not present)")
            continue
        trial = _mutate_value(current, rule, rng, radius)
        if rule.key == "ANCHOR_WEIGHT":
            patched = _set_dict_value(patched, rule.container, "ANCHOR_WEIGHT", trial)
            stable_weight = max(0.0, min(0.85, 1.0 - trial))
            if _get_dict_value(patched, rule.container, "STABLE_MID_WEIGHT") is not None:
                patched = _set_dict_value(patched, rule.container, "STABLE_MID_WEIGHT", stable_weight)
                changes.append(
                    {
                        "container": rule.container,
                        "key": "STABLE_MID_WEIGHT",
                        "old": round(_get_dict_value(source_text, rule.container, "STABLE_MID_WEIGHT") or stable_weight, 6),
                        "new": round(stable_weight, 6),
                    }
                )
        else:
            patched = _set_dict_value(patched, rule.container, rule.key, trial, int_like=rule.int_like)
        changes.append(
            {
                "container": rule.container,
                "key": rule.key,
                "old": round(current, 6),
                "new": round(trial, 6),
            }
        )
    return patched, changes, notes


def _choose_families(
    family_weights: dict[str, float],
    rng: random.Random,
    *,
    secondary_prob: float,
    triple_prob: float,
    exploration_mix: float,
) -> list[str]:
    names = list(family_weights)
    uniform = 1.0 / len(names)
    weights = [
        (1.0 - exploration_mix) * family_weights[name] + exploration_mix * uniform
        for name in names
    ]
    primary = rng.choices(names, weights=weights, k=1)[0]
    chosen = [primary]
    if rng.random() < secondary_prob:
        secondary_pool = [name for name in names if name != primary]
        secondary_weights = [
            (1.0 - exploration_mix) * family_weights[name] + exploration_mix * uniform
            for name in secondary_pool
        ]
        if secondary_pool:
            secondary = rng.choices(secondary_pool, weights=secondary_weights, k=1)[0]
            chosen.append(secondary)
            if rng.random() < triple_prob:
                tertiary_pool = [name for name in secondary_pool if name != secondary]
                tertiary_weights = [
                    (1.0 - exploration_mix) * family_weights[name] + exploration_mix * uniform
                    for name in tertiary_pool
                ]
                if tertiary_pool:
                    chosen.append(rng.choices(tertiary_pool, weights=tertiary_weights, k=1)[0])
    return chosen


def _candidate_from_parent(
    *,
    round_index: int,
    candidate_index: int,
    parent_bot: Path,
    family_weights: dict[str, float],
    radius: float,
    rng: random.Random,
    secondary_prob: float,
    triple_prob: float,
    exploration_mix: float,
) -> CandidateSpec:
    source_text = parent_bot.read_text()
    chosen_families = _choose_families(
        family_weights,
        rng,
        secondary_prob=secondary_prob,
        triple_prob=triple_prob,
        exploration_mix=exploration_mix,
    )
    strategy_refs: list[str] = []
    notes: list[str] = []
    changes: list[dict[str, Any]] = []
    patched = source_text
    for family_name in chosen_families:
        family = FAMILY_SPECS[family_name]
        strategy_refs.extend(family.strategy_refs)
        patched, family_changes, family_notes = _apply_family_mutations(patched, family, rng, radius)
        changes.extend(family_changes)
        notes.extend(family_notes)
    if not patched.endswith("\n"):
        patched += "\n"

    slug = "_".join(_slugify(name).replace("ash_", "a_").replace("pepper_", "p_") for name in chosen_families)
    name = f"TradervR1_lab_r{round_index:02d}_{candidate_index:02d}_{slug}"
    candidate = CandidateSpec(
        name=name,
        parent_bot=parent_bot,
        parent_name=parent_bot.stem,
        families=chosen_families,
        strategy_refs=sorted(set(strategy_refs)),
        notes=notes,
        changes=changes,
    )
    return candidate, patched


def _run_candidate_deterministic(
    candidate: CandidateSpec,
    *,
    round_dir: Path,
    safe_baseline_total: float,
    safe_baseline_days: dict[int, float],
    attack_total: float,
) -> CandidateEval:
    det_dir = ensure_dir(round_dir / "deterministic" / candidate.name)
    total, totals_by_day, product_by_day, trades_by_day = _evaluate_bot(
        candidate.bot_path,
        out_dir=det_dir,
        days=DETERMINISTIC_DAYS,
    )
    day_deltas = [totals_by_day[day] - safe_baseline_days[day] for day in DETERMINISTIC_DAYS]
    delta_vs_safe = total - safe_baseline_total
    delta_vs_attack = total - attack_total
    min_day_delta = min(day_deltas)
    day_range = max(day_deltas) - min(day_deltas)
    det_score = _deterministic_score(delta_vs_safe, min_day_delta, day_range)
    return CandidateEval(
        candidate=candidate,
        deterministic_total=total,
        deterministic_by_day=totals_by_day,
        product_pnl_by_day=product_by_day,
        own_trades_by_day=trades_by_day,
        delta_vs_safe=delta_vs_safe,
        delta_vs_attack=delta_vs_attack,
        min_day_delta_vs_safe=min_day_delta,
        daily_delta_range_vs_safe=day_range,
        deterministic_score=det_score,
    )


def _run_mc_for_candidate(
    evaluation: CandidateEval,
    *,
    round_dir: Path,
    baseline_bot: Path,
    samples_per_family: int,
) -> None:
    mc_dir = ensure_dir(round_dir / "monte_carlo" / evaluation.candidate.name)
    result = run_monte_carlo(
        evaluation.candidate.bot_path,
        compare_bot_path=baseline_bot,
        output_dir=mc_dir,
        data_root=DATA_ROOT,
        dataset_tag=DATASET_TAG,
        days=list(DETERMINISTIC_DAYS),
        samples_per_family=samples_per_family,
        quick=True,
        seed=52,
    )
    comparison = result.comparison or {}
    by_profile = comparison.get("by_profile", {})
    plausible = by_profile.get("plausible", {})
    summary = comparison.get("summary", {})
    evaluation.mc_summary = {
        "mean_delta": float(summary.get("mean_delta", 0.0)),
        "p10_delta": float(summary.get("p10_delta", 0.0)),
        "win_rate": float(summary.get("win_rate", 0.0)),
        "plausible_mean_delta": float(plausible.get("mean_delta", 0.0)),
        "plausible_p10_delta": float(plausible.get("p10_delta", 0.0)),
    }
    evaluation.mc_paths = {
        "output_dir": str(result.output_dir),
        "report_json": str(result.report_json_path),
        "report_markdown": str(result.report_markdown_path),
    }
    evaluation.composite_score = _composite_score(
        evaluation.deterministic_score,
        evaluation.mc_summary,
        delta_vs_attack=evaluation.delta_vs_attack,
    )


def _build_cmaes_config(
    *,
    champion: CandidateEval,
    focus_family: str,
    round_dir: Path,
) -> Path | None:
    family = FAMILY_SPECS.get(focus_family)
    if family is None:
        return None
    if not family.rules:
        return None
    config_dir = ensure_dir(round_dir / "cmaes")
    output_dir = round_dir / "cmaes" / f"{champion.candidate.name}_{focus_family}"
    parameters = []
    for rule in family.rules:
        if _get_dict_value(champion.candidate.bot_path.read_text(), rule.container, rule.key) is None:
            continue
        parameters.append(
            {
                "name": f"{rule.container}_{rule.key}",
                "lower": rule.lower,
                "upper": rule.upper,
                "location": {
                    "type": "dict_block",
                    "container": rule.container,
                    "key": rule.key,
                },
            }
        )
    if not parameters:
        return None
    payload = {
        "name": f"{champion.candidate.name} short CMA-ES {focus_family}",
        "source_bot": str(champion.candidate.bot_path),
        "baselines": {str(day): champion.deterministic_by_day[day] for day in DETERMINISTIC_DAYS},
        "search": {
            "max_iter": 2,
            "population": 4,
            "parents": 2,
            "sigma0": 0.08,
            "seed": 4200 + hash((champion.candidate.name, focus_family)) % 1000,
            "timeout_seconds": 240,
        },
        "penalties": {
            "regression": 4.0,
            "imbalance": 1.0,
            "drift": 60.0,
        },
        "output_prefix": f"{_slugify(champion.candidate.name)}_{focus_family}_cmaes",
        "output_dir": str(output_dir),
        "data_root": str(DATA_ROOT),
        "dataset_tag": DATASET_TAG,
        "engine": "rust",
        "parameters": parameters,
    }
    config_path = config_dir / f"{_slugify(champion.candidate.name)}_{focus_family}.json"
    _write_json(config_path, payload)
    return config_path


def _run_cmaes_candidate(
    *,
    champion: CandidateEval,
    focus_family: str,
    round_index: int,
    round_dir: Path,
    safe_baseline_total: float,
    safe_baseline_days: dict[int, float],
    attack_total: float,
) -> CandidateEval | None:
    config_path = _build_cmaes_config(champion=champion, focus_family=focus_family, round_dir=round_dir)
    if config_path is None:
        return None
    result = run_cmaes(config_path)
    candidate = CandidateSpec(
        name=f"{champion.candidate.name}_cmaes_{_slugify(focus_family)}",
        parent_bot=champion.candidate.bot_path,
        parent_name=champion.candidate.name,
        families=[focus_family, "cmaes_refine"],
        strategy_refs=list(champion.candidate.strategy_refs),
        notes=[f"CMA-ES refinement around {focus_family}", f"config={config_path}"],
        bot_path=result.best_bot_path,
        changes=[],
    )
    return _run_candidate_deterministic(
        candidate,
        round_dir=round_dir,
        safe_baseline_total=safe_baseline_total,
        safe_baseline_days=safe_baseline_days,
        attack_total=attack_total,
    )


def _family_feedback(
    evaluations: list[CandidateEval],
    family_weights: dict[str, float],
    *,
    family_weight_floor: float,
    exploration_mix: float,
) -> tuple[dict[str, float], list[str]]:
    notes: list[str] = []
    family_scores: dict[str, list[float]] = {name: [] for name in family_weights}
    for evaluation in evaluations:
        score = evaluation.composite_score if evaluation.composite_score is not None else evaluation.deterministic_score
        for family in evaluation.candidate.families:
            if family in family_scores:
                family_scores[family].append(score)
    updated: dict[str, float] = {}
    for family, old_weight in family_weights.items():
        samples = family_scores[family]
        if samples:
            family_mean = sum(samples) / len(samples)
            bump = 1.0 + max(-0.35, min(0.55, family_mean / 2200.0))
        else:
            family_mean = 0.0
            bump = 0.92
        updated[family] = max(family_weight_floor, old_weight * bump)
        notes.append(f"{family}: mean_score={round(family_mean, 2)} old={round(old_weight, 3)} new={round(updated[family], 3)}")
    total = sum(updated.values())
    normalized = {family: value / total for family, value in updated.items()}
    uniform = 1.0 / len(normalized)
    mixed = {
        family: (1.0 - exploration_mix) * value + exploration_mix * uniform
        for family, value in normalized.items()
    }
    mix_total = sum(mixed.values())
    normalized = {family: value / mix_total for family, value in mixed.items()}
    return normalized, notes


def _leaderboard_rows(evaluations: list[CandidateEval]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rank, evaluation in enumerate(
        sorted(
            evaluations,
            key=lambda item: item.composite_score if item.composite_score is not None else item.deterministic_score,
            reverse=True,
        ),
        start=1,
    ):
        row = {
            "rank": rank,
            "name": evaluation.candidate.name,
            "parent": evaluation.candidate.parent_name,
            "families": ",".join(evaluation.candidate.families),
            "deterministic_total": round(evaluation.deterministic_total, 4),
            "delta_vs_safe": round(evaluation.delta_vs_safe, 4),
            "delta_vs_attack": round(evaluation.delta_vs_attack, 4),
            "min_day_delta_vs_safe": round(evaluation.min_day_delta_vs_safe, 4),
            "daily_delta_range_vs_safe": round(evaluation.daily_delta_range_vs_safe, 4),
            "deterministic_score": round(evaluation.deterministic_score, 4),
            "composite_score": round(
                evaluation.composite_score if evaluation.composite_score is not None else evaluation.deterministic_score,
                4,
            ),
        }
        for day in DETERMINISTIC_DAYS:
            row[f"day_{day}"] = round(evaluation.deterministic_by_day[day], 4)
            row[f"ash_{day}"] = round(evaluation.product_pnl_by_day[day].get("ASH_COATED_OSMIUM", 0.0), 4)
            row[f"pepper_{day}"] = round(evaluation.product_pnl_by_day[day].get("INTARIAN_PEPPER_ROOT", 0.0), 4)
            row[f"trades_{day}"] = evaluation.own_trades_by_day[day]
        if evaluation.mc_summary:
            for key, value in evaluation.mc_summary.items():
                row[f"mc_{key}"] = round(value, 4)
        rows.append(row)
    return rows


def _round_feedback_markdown(
    round_index: int,
    top_evals: list[CandidateEval],
    family_notes: list[str],
) -> str:
    lines = [
        f"# Round {round_index} Feedback",
        "",
        "## Top Candidates",
        "",
    ]
    for evaluation in top_evals:
        score = evaluation.composite_score if evaluation.composite_score is not None else evaluation.deterministic_score
        lines.append(f"### {evaluation.candidate.name}")
        lines.append("")
        lines.append(f"- Parent: `{evaluation.candidate.parent_name}`")
        lines.append(f"- Families: `{', '.join(evaluation.candidate.families)}`")
        lines.append(f"- Strategy refs: `{'; '.join(evaluation.candidate.strategy_refs)}`")
        lines.append(f"- Deterministic total: `{evaluation.deterministic_total:.4f}`")
        lines.append(f"- Delta vs safe baseline: `{evaluation.delta_vs_safe:.4f}`")
        lines.append(f"- Delta vs aggressive anchor: `{evaluation.delta_vs_attack:.4f}`")
        lines.append(f"- Composite score: `{score:.4f}`")
        if evaluation.mc_summary:
            lines.append(f"- MC plausible mean delta: `{evaluation.mc_summary['plausible_mean_delta']:.4f}`")
            lines.append(f"- MC plausible p10 delta: `{evaluation.mc_summary['plausible_p10_delta']:.4f}`")
            lines.append(f"- MC win rate: `{evaluation.mc_summary['win_rate']:.4f}`")
        lines.append("")
    lines.extend(["## Family Weight Update", ""])
    for note in family_notes:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def _summary_markdown(
    state: SessionState,
    best_safe: CandidateEval | None,
    best_robust: CandidateEval | None,
    latest_round_dir: Path | None,
) -> str:
    lines = [
        "# Round 1 Overnight Research Summary",
        "",
        f"- Started: `{state.started_at}`",
        f"- Updated: `{_now()}`",
        f"- Safe baseline: `{state.baseline_bot}`",
        f"- Aggressive anchor: `{state.attack_bot}`",
        f"- Rounds completed: `{state.rounds_completed}`",
        f"- Candidates evaluated: `{state.candidates_seen}`",
        "",
        "## Family Weights",
        "",
    ]
    for family, weight in sorted(state.family_weights.items()):
        lines.append(f"- `{family}`: `{round(weight, 4)}`")
    lines.append("")
    if best_safe is not None:
        lines += [
            "## Best Deterministic Candidate",
            "",
            f"- Name: `{best_safe.candidate.name}`",
            f"- Bot: `{best_safe.candidate.bot_path}`",
            f"- Parent: `{best_safe.candidate.parent_name}`",
            f"- Families: `{', '.join(best_safe.candidate.families)}`",
            f"- Total: `{best_safe.deterministic_total:.4f}`",
            f"- Delta vs safe baseline: `{best_safe.delta_vs_safe:.4f}`",
            f"- Delta vs aggressive anchor: `{best_safe.delta_vs_attack:.4f}`",
            "",
        ]
    if best_robust is not None:
        lines += [
            "## Best Robust Candidate",
            "",
            f"- Name: `{best_robust.candidate.name}`",
            f"- Bot: `{best_robust.candidate.bot_path}`",
            f"- Parent: `{best_robust.candidate.parent_name}`",
            f"- Families: `{', '.join(best_robust.candidate.families)}`",
            f"- Deterministic total: `{best_robust.deterministic_total:.4f}`",
            f"- Delta vs safe baseline: `{best_robust.delta_vs_safe:.4f}`",
            f"- Plausible mean delta: `{best_robust.mc_summary.get('plausible_mean_delta', 0.0) if best_robust.mc_summary else 0.0:.4f}`",
            f"- Plausible p10 delta: `{best_robust.mc_summary.get('plausible_p10_delta', 0.0) if best_robust.mc_summary else 0.0:.4f}`",
            "",
        ]
    if latest_round_dir is not None:
        lines.append(f"- Latest round dir: `{latest_round_dir}`")
        lines.append("")
    return "\n".join(lines)


def _log_error(path: Path, label: str, exc: BaseException) -> None:
    with path.open("a") as handle:
        handle.write(f"[{_now()}] {label}\n")
        handle.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
        handle.write("\n")


def _write_session_outputs(
    state: SessionState,
    all_evaluations: list[CandidateEval],
    best_safe: CandidateEval | None,
    best_robust: CandidateEval | None,
    latest_round_dir: Path | None,
) -> None:
    leaderboard = _leaderboard_rows(all_evaluations)
    _write_csv(state.output_dir / "leaderboard.csv", leaderboard)
    summary = _summary_markdown(state, best_safe, best_robust, latest_round_dir)
    (state.output_dir / "LATEST.md").write_text(summary + "\n")
    _write_json(
        state.output_dir / "session_state.json",
        {
            "started_at": state.started_at,
            "updated_at": _now(),
            "baseline_bot": str(state.baseline_bot),
            "attack_bot": str(state.attack_bot),
            "seed_bots": [str(path) for path in state.seed_bots],
            "family_weights": state.family_weights,
            "rounds_completed": state.rounds_completed,
            "candidates_seen": state.candidates_seen,
            "latest_round_dir": str(latest_round_dir) if latest_round_dir else None,
        },
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Overnight Round 1 research loop for Prosperity bots.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Optional output directory.")
    parser.add_argument("--hours", type=float, default=8.0, help="Wall-clock hours budget.")
    parser.add_argument("--max-rounds", type=int, default=16, help="Maximum rounds to run.")
    parser.add_argument("--candidates-per-round", type=int, default=8, help="Fresh mutated candidates per round.")
    parser.add_argument("--mc-top-k", type=int, default=3, help="How many deterministic survivors get quick Monte Carlo.")
    parser.add_argument("--mc-samples-per-family", type=int, default=2, help="Quick Monte Carlo samples per family.")
    parser.add_argument("--cmaes-every", type=int, default=2, help="Run a short CMA-ES refinement every N rounds. Set 0 to disable.")
    parser.add_argument("--seed", type=int, default=47, help="Random seed.")
    parser.add_argument("--base-radius", type=float, default=1.10, help="Initial mutation radius.")
    parser.add_argument("--min-radius", type=float, default=0.45, help="Minimum mutation radius.")
    parser.add_argument("--radius-decay", type=float, default=0.05, help="Per-round mutation radius decay.")
    parser.add_argument("--secondary-family-prob", type=float, default=0.35, help="Chance to add a second strategy family.")
    parser.add_argument("--triple-family-prob", type=float, default=0.10, help="Chance to add a third strategy family when a second was chosen.")
    parser.add_argument("--family-exploration-mix", type=float, default=0.18, help="How much uniform exploration to mix into family selection and feedback.")
    parser.add_argument("--family-weight-floor", type=float, default=0.20, help="Minimum raw family weight before normalization.")
    parser.add_argument("--seed-parent-prob", type=float, default=0.25, help="Chance to pick a parent from the original seed set instead of the current elite pool.")
    parser.add_argument("--top-parent-count", type=int, default=3, help="How many top candidates feed the next round parent pool.")
    parser.add_argument("--baseline-bot", type=Path, default=ROUND1_DIR / "TradervR1_34_1.py")
    parser.add_argument("--attack-bot", type=Path, default=ROUND1_DIR / "TradervR1_47.py")
    parser.add_argument("--seed-bots", type=Path, nargs="*", default=None, help="Optional explicit seed bot list.")
    parser.add_argument("--smoke", action="store_true", help="Use a tiny budget for a quick local smoke test.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.smoke:
        args.hours = min(args.hours, 0.03)
        args.max_rounds = min(args.max_rounds, 1)
        args.candidates_per_round = min(args.candidates_per_round, 3)
        args.mc_top_k = min(args.mc_top_k, 1)
        args.mc_samples_per_family = min(args.mc_samples_per_family, 1)
        args.cmaes_every = 0
        args.base_radius = max(args.base_radius, 1.15)
        args.family_exploration_mix = max(args.family_exploration_mix, 0.22)

    output_dir = ensure_dir(args.output_dir.expanduser().resolve() if args.output_dir else _default_output_dir())
    _copy_strategy_reference(output_dir)

    baseline_bot = Path(args.baseline_bot).expanduser().resolve()
    attack_bot = Path(args.attack_bot).expanduser().resolve()
    seed_bots = _seed_bots_from_args(args)
    rng = random.Random(args.seed)

    state = SessionState(
        output_dir=output_dir,
        started_at=_now(),
        baseline_bot=baseline_bot,
        attack_bot=attack_bot,
        seed_bots=seed_bots,
        family_weights={name: 1.0 / len(FAMILY_SPECS) for name in FAMILY_SPECS},
    )

    references_dir = ensure_dir(output_dir / "references")
    strategy_map = {
        name: {
            "description": spec.description,
            "strategy_refs": list(spec.strategy_refs),
            "rules": [asdict(rule) for rule in spec.rules],
        }
        for name, spec in FAMILY_SPECS.items()
    }
    _write_json(references_dir / "strategy_family_map.json", strategy_map)

    safe_baseline_total, safe_baseline_days, _, _ = _evaluate_bot(
        baseline_bot,
        out_dir=ensure_dir(output_dir / "baselines" / baseline_bot.stem),
        days=DETERMINISTIC_DAYS,
    )
    attack_total, attack_days, _, _ = _evaluate_bot(
        attack_bot,
        out_dir=ensure_dir(output_dir / "baselines" / attack_bot.stem),
        days=DETERMINISTIC_DAYS,
    )

    all_evaluations: list[CandidateEval] = []
    parent_pool = list(dict.fromkeys(seed_bots))
    best_safe: CandidateEval | None = None
    best_robust: CandidateEval | None = None
    latest_round_dir: Path | None = None
    errors_path = output_dir / "errors.log"

    start = time.time()
    round_index = 0
    while round_index < args.max_rounds and (time.time() - start) < args.hours * 3600.0:
        round_index += 1
        latest_round_dir = ensure_dir(output_dir / f"round_{round_index:02d}")
        candidate_dir = ensure_dir(latest_round_dir / "candidates")
        round_errors: list[str] = []

        round_evaluations: list[CandidateEval] = []
        radius = max(args.min_radius, args.base_radius - args.radius_decay * (round_index - 1))

        for candidate_index in range(1, args.candidates_per_round + 1):
            try:
                if rng.random() < args.seed_parent_prob:
                    parent_bot = rng.choice(seed_bots)
                else:
                    parent_bot = rng.choice(parent_pool)
                candidate, patched = _candidate_from_parent(
                    round_index=round_index,
                    candidate_index=candidate_index,
                    parent_bot=parent_bot,
                    family_weights=state.family_weights,
                    radius=radius,
                    rng=rng,
                    secondary_prob=args.secondary_family_prob,
                    triple_prob=args.triple_family_prob,
                    exploration_mix=args.family_exploration_mix,
                )
                candidate.bot_path = candidate_dir / f"{candidate.name}.py"
                candidate.bot_path.write_text(patched)
                evaluation = _run_candidate_deterministic(
                    candidate,
                    round_dir=latest_round_dir,
                    safe_baseline_total=safe_baseline_total,
                    safe_baseline_days=safe_baseline_days,
                    attack_total=attack_total,
                )
                round_evaluations.append(evaluation)
                all_evaluations.append(evaluation)
                state.candidates_seen += 1
            except Exception as exc:
                label = f"round {round_index} candidate {candidate_index}"
                round_errors.append(f"{label}: {exc}")
                _log_error(errors_path, label, exc)

        det_sorted = sorted(round_evaluations, key=lambda item: item.deterministic_score, reverse=True)
        mc_pool = det_sorted[: max(1, min(args.mc_top_k, len(det_sorted)))]
        for evaluation in mc_pool:
            try:
                _run_mc_for_candidate(
                    evaluation,
                    round_dir=latest_round_dir,
                    baseline_bot=baseline_bot,
                    samples_per_family=args.mc_samples_per_family,
                )
            except Exception as exc:
                label = f"round {round_index} mc {evaluation.candidate.name}"
                round_errors.append(f"{label}: {exc}")
                _log_error(errors_path, label, exc)

        if args.cmaes_every and round_index % args.cmaes_every == 0 and mc_pool:
            try:
                champion = sorted(
                    mc_pool,
                    key=lambda item: item.composite_score if item.composite_score is not None else item.deterministic_score,
                    reverse=True,
                )[0]
                focus_family = champion.candidate.families[0]
                cmaes_eval = _run_cmaes_candidate(
                    champion=champion,
                    focus_family=focus_family,
                    round_index=round_index,
                    round_dir=latest_round_dir,
                    safe_baseline_total=safe_baseline_total,
                    safe_baseline_days=safe_baseline_days,
                    attack_total=attack_total,
                )
                if cmaes_eval is not None:
                    try:
                        _run_mc_for_candidate(
                            cmaes_eval,
                            round_dir=latest_round_dir,
                            baseline_bot=baseline_bot,
                            samples_per_family=args.mc_samples_per_family,
                        )
                    except Exception as exc:
                        label = f"round {round_index} cmaes-mc {cmaes_eval.candidate.name}"
                        round_errors.append(f"{label}: {exc}")
                        _log_error(errors_path, label, exc)
                    round_evaluations.append(cmaes_eval)
                    all_evaluations.append(cmaes_eval)
                    state.candidates_seen += 1
            except Exception as exc:
                label = f"round {round_index} cmaes"
                round_errors.append(f"{label}: {exc}")
                _log_error(errors_path, label, exc)

        if not round_evaluations:
            _write_json(
                latest_round_dir / "feedback.json",
                {
                    "round": round_index,
                    "generated_at": _now(),
                    "family_weights": state.family_weights,
                    "family_notes": [],
                    "errors": round_errors,
                },
            )
            state.rounds_completed = round_index
            _write_session_outputs(state, all_evaluations, best_safe, best_robust, latest_round_dir)
            continue

        ranked_round = sorted(
            round_evaluations,
            key=lambda item: item.composite_score if item.composite_score is not None else item.deterministic_score,
            reverse=True,
        )
        family_weights, family_notes = _family_feedback(
            ranked_round,
            state.family_weights,
            family_weight_floor=args.family_weight_floor,
            exploration_mix=args.family_exploration_mix,
        )
        state.family_weights = family_weights
        state.rounds_completed = round_index

        feedback = _round_feedback_markdown(round_index, ranked_round[:5], family_notes)
        (latest_round_dir / "feedback.md").write_text(feedback + "\n")
        _write_csv(latest_round_dir / "leaderboard.csv", _leaderboard_rows(ranked_round))
        _write_json(
            latest_round_dir / "feedback.json",
            {
                "round": round_index,
                "generated_at": _now(),
                "family_weights": state.family_weights,
                "family_notes": family_notes,
                "errors": round_errors,
            },
        )

        top_for_pool = [
            evaluation.candidate.bot_path
            for evaluation in ranked_round[: max(1, args.top_parent_count)]
            if evaluation.candidate.bot_path
        ]
        parent_pool = list(dict.fromkeys(seed_bots + top_for_pool))

        if best_safe is None or ranked_round[0].deterministic_total > best_safe.deterministic_total:
            best_safe = ranked_round[0]
            shutil.copy2(best_safe.candidate.bot_path, output_dir / "best_deterministic.py")

        robust_candidates = [item for item in ranked_round if item.mc_summary is not None]
        if robust_candidates:
            robust_best = sorted(
                robust_candidates,
                key=lambda item: item.composite_score if item.composite_score is not None else item.deterministic_score,
                reverse=True,
            )[0]
            if best_robust is None or (
                (robust_best.composite_score if robust_best.composite_score is not None else robust_best.deterministic_score)
                > (best_robust.composite_score if best_robust.composite_score is not None else best_robust.deterministic_score)
            ):
                best_robust = robust_best
                shutil.copy2(best_robust.candidate.bot_path, output_dir / "best_robust.py")

        _write_session_outputs(state, all_evaluations, best_safe, best_robust, latest_round_dir)

    final_payload = {
        "started_at": state.started_at,
        "finished_at": _now(),
        "rounds_completed": state.rounds_completed,
        "candidates_seen": state.candidates_seen,
        "output_dir": str(output_dir),
        "best_deterministic_bot": str(best_safe.candidate.bot_path) if best_safe else None,
        "best_robust_bot": str(best_robust.candidate.bot_path) if best_robust else None,
    }
    _write_json(output_dir / "final_summary.json", final_payload)
    print(f"Overnight lab finished. Output dir: {output_dir}")
    if best_safe is not None:
        print(f"Best deterministic: {best_safe.candidate.name} total={best_safe.deterministic_total:.4f}")
    if best_robust is not None:
        print(
            "Best robust: "
            f"{best_robust.candidate.name} composite="
            f"{(best_robust.composite_score if best_robust.composite_score is not None else best_robust.deterministic_score):.4f}"
        )


if __name__ == "__main__":
    main()
