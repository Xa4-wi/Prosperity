from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / "Bots" / "Round1" / "TradervR1_121_13.py"
OUT_DIR = ROOT / "Bots" / "Round1"


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"Missing anchor: {old[:120]!r}")
    return text.replace(old, new, 1)


def make_122_1(text: str) -> str:
    text = replace_once(text, '"MARKOUT_ALPHA": 0.18,', '"MARKOUT_ALPHA": 0.16,')
    text = replace_once(text, '"SOFT_BAD_MARKOUT": -0.45,', '"SOFT_BAD_MARKOUT": -0.50,')
    text = replace_once(text, '"HARD_BAD_MARKOUT": -0.90,', '"HARD_BAD_MARKOUT": -1.00,')
    text = replace_once(text, '"MARKOUT_EDGE_PENALTY": 0.22,', '"MARKOUT_EDGE_PENALTY": 0.18,')
    text = replace_once(text, '"MARKOUT_SIZE_PENALTY": 0.18,', '"MARKOUT_SIZE_PENALTY": 0.14,')
    text = replace_once(text, '            and quote_signal > 0.10', '            and quote_signal > 0.08')
    text = replace_once(text, '            and quote_signal < -0.10', '            and quote_signal < -0.08')
    text = replace_once(text, '            and abs(quote_signal) >= 0.28', '            and abs(quote_signal) >= 0.25')
    text = replace_once(text, '            and abs(quote_signal) >= 0.28', '            and abs(quote_signal) >= 0.25')
    text = replace_once(text, '            extra = min(0.30, 0.05 * max(0, bars_since_buy_fill - 8))', '            extra = min(0.35, 0.06 * max(0, bars_since_buy_fill - 8))')
    text = replace_once(text, '            buy_qe -= 0.15 + extra', '            buy_qe -= 0.18 + extra')
    text = replace_once(text, '            extra = min(0.30, 0.05 * max(0, bars_since_sell_fill - 8))', '            extra = min(0.35, 0.06 * max(0, bars_since_sell_fill - 8))')
    text = replace_once(text, '            sell_qe -= 0.15 + extra', '            sell_qe -= 0.18 + extra')
    return text


def make_122_2(text: str) -> str:
    text = replace_once(text, '"MARKOUT_ALPHA": 0.18,', '"MARKOUT_ALPHA": 0.22,')
    text = replace_once(text, '"SOFT_BAD_MARKOUT": -0.45,', '"SOFT_BAD_MARKOUT": -0.40,')
    text = replace_once(text, '"HARD_BAD_MARKOUT": -0.90,', '"HARD_BAD_MARKOUT": -0.80,')
    text = replace_once(text, '"MARKOUT_EDGE_PENALTY": 0.22,', '"MARKOUT_EDGE_PENALTY": 0.26,')
    text = replace_once(text, '"MARKOUT_SIZE_PENALTY": 0.18,', '"MARKOUT_SIZE_PENALTY": 0.20,')
    return text


def make_122_3(text: str) -> str:
    text = replace_once(text, '            and quote_signal > 0.10', '            and quote_signal > 0.08')
    text = replace_once(text, '            and quote_signal < -0.10', '            and quote_signal < -0.08')
    text = replace_once(text, '            and abs(quote_signal) >= 0.28', '            and abs(quote_signal) >= 0.24')
    text = replace_once(text, '            and abs(quote_signal) >= 0.28', '            and abs(quote_signal) >= 0.24')
    text = replace_once(text, '            if micro_nibble:\n                buy_qe -= 0.05', '            if micro_nibble:\n                buy_qe -= 0.08')
    text = replace_once(text, '            if micro_nibble:\n                sell_qe -= 0.05', '            if micro_nibble:\n                sell_qe -= 0.08')
    text = replace_once(text, '        if profile != "defend":\n            join_edge += join_bonus', '        if profile != "defend":\n            join_edge += join_bonus\n        if buy_reactivation or sell_reactivation:\n            join_edge += 0.10')
    text = replace_once(text, '            buy_front_sz += 1 + int(bars_since_buy_fill >= 12)', '            buy_front_sz += 1 + int(bars_since_buy_fill >= 10)')
    text = replace_once(text, '            sell_front_sz += 1 + int(bars_since_sell_fill >= 12)', '            sell_front_sz += 1 + int(bars_since_sell_fill >= 10)')
    return text


def make_122_4(text: str) -> str:
    text = replace_once(text, '            and bars_since_buy_fill >= 8', '            and bars_since_buy_fill >= 10')
    text = replace_once(text, '            and bars_since_sell_fill >= 8', '            and bars_since_sell_fill >= 10')
    text = replace_once(text, '            and quote_signal > 0.10', '            and quote_signal > 0.12')
    text = replace_once(text, '            and quote_signal < -0.10', '            and quote_signal < -0.12')
    text = replace_once(text, '            and abs(quote_signal) >= 0.28', '            and abs(quote_signal) >= 0.32')
    text = replace_once(text, '            and abs(quote_signal) >= 0.28', '            and abs(quote_signal) >= 0.32')
    text = replace_once(text, '            extra = min(0.30, 0.05 * max(0, bars_since_buy_fill - 8))', '            extra = min(0.24, 0.04 * max(0, bars_since_buy_fill - 10))')
    text = replace_once(text, '            extra = min(0.30, 0.05 * max(0, bars_since_sell_fill - 8))', '            extra = min(0.24, 0.04 * max(0, bars_since_sell_fill - 10))')
    return text


def make_122_5(text: str) -> str:
    text = replace_once(text, '"MARKOUT_ALPHA": 0.18,', '"MARKOUT_ALPHA": 0.15,')
    text = replace_once(text, '"SOFT_BAD_MARKOUT": -0.45,', '"SOFT_BAD_MARKOUT": -0.52,')
    text = replace_once(text, '"HARD_BAD_MARKOUT": -0.90,', '"HARD_BAD_MARKOUT": -1.05,')
    text = replace_once(text, '"MARKOUT_EDGE_PENALTY": 0.22,', '"MARKOUT_EDGE_PENALTY": 0.16,')
    text = replace_once(text, '"MARKOUT_SIZE_PENALTY": 0.18,', '"MARKOUT_SIZE_PENALTY": 0.10,')
    return text


def make_122_6(text: str) -> str:
    text = replace_once(text, '"MARKOUT_ALPHA": 0.18,', '"MARKOUT_ALPHA": 0.20,')
    text = replace_once(text, '"SOFT_BAD_MARKOUT": -0.45,', '"SOFT_BAD_MARKOUT": -0.48,')
    text = replace_once(text, '"HARD_BAD_MARKOUT": -0.90,', '"HARD_BAD_MARKOUT": -0.95,')
    text = replace_once(text, '"MARKOUT_EDGE_PENALTY": 0.22,', '"MARKOUT_EDGE_PENALTY": 0.20,')
    text = replace_once(text, '"MARKOUT_SIZE_PENALTY": 0.18,', '"MARKOUT_SIZE_PENALTY": 0.12,')
    text = replace_once(text, '            and quote_signal > 0.10', '            and quote_signal > 0.09')
    text = replace_once(text, '            and quote_signal < -0.10', '            and quote_signal < -0.09')
    text = replace_once(text, '            and abs(quote_signal) >= 0.28', '            and abs(quote_signal) >= 0.26')
    text = replace_once(text, '            and abs(quote_signal) >= 0.28', '            and abs(quote_signal) >= 0.26')
    text = replace_once(text, '            extra = min(0.30, 0.05 * max(0, bars_since_buy_fill - 8))', '            extra = min(0.32, 0.05 * max(0, bars_since_buy_fill - 8))')
    text = replace_once(text, '            extra = min(0.30, 0.05 * max(0, bars_since_sell_fill - 8))', '            extra = min(0.32, 0.05 * max(0, bars_since_sell_fill - 8))')
    return text


VARIANTS = {
    "TradervR1_122_1.py": make_122_1,
    "TradervR1_122_2.py": make_122_2,
    "TradervR1_122_3.py": make_122_3,
    "TradervR1_122_4.py": make_122_4,
    "TradervR1_122_5.py": make_122_5,
    "TradervR1_122_6.py": make_122_6,
}


def main() -> None:
    base = BASE_PATH.read_text()
    for name, fn in VARIANTS.items():
        (OUT_DIR / name).write_text(fn(base))
        print(name)


if __name__ == "__main__":
    main()
