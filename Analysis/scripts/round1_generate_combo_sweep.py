from __future__ import annotations

from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / "Bots" / "Round1" / "TradervR1_118.py"
OUT_DIR = ROOT / "Bots" / "Round1"


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"Missing anchor:\n{old[:200]}")
    return text.replace(old, new, 1)


def add_params(text: str, flags: set[int]) -> str:
    extra = []
    if 1 in flags:
        extra.extend(
            [
                '    "MARKOUT_ALPHA": 0.18,\n',
                '    "SOFT_BAD_MARKOUT": -0.45,\n',
                '    "HARD_BAD_MARKOUT": -0.90,\n',
                '    "MARKOUT_EDGE_PENALTY": 0.22,\n',
                '    "MARKOUT_SIZE_PENALTY": 0.18,\n',
            ]
        )
    if 2 in flags:
        extra.extend(
            [
                '    "HIGH_CONVICTION_SWEEP": 0.70,\n',
                '    "SWEEP_EDGE_BUFFER": 0.10,\n',
            ]
        )
    if 4 in flags:
        extra.append('    "CONVICTION_REGIME": 0.78,\n')
    if 5 in flags:
        extra.extend(
            [
                '    "SOFT_RECYCLE_CONVICTION": 0.22,\n',
                '    "SOFT_RECYCLE_POS": 18,\n',
            ]
        )
    if not extra:
        return text
    anchor = '    "ENABLE_TAKE_LADDER": True,\n'
    return replace_once(text, anchor, anchor + "".join(extra))


def add_markout_method(text: str) -> str:
    anchor = """    def _trade_confirmation(self, state: TradingState, book: Book) -> float:\n        flow = 0.0\n        for trade in state.market_trades.get("ASH_COATED_OSMIUM", []):\n            price = int(trade.price)\n            qty = abs(int(trade.quantity))\n            trade_sign = 0\n            if price >= book.best_ask:\n                trade_sign = 1\n            elif price <= book.best_bid:\n                trade_sign = -1\n            elif price > book.mid:\n                trade_sign = 1\n            elif price < book.mid:\n                trade_sign = -1\n            flow += trade_sign * qty\n        return clamp(flow / 20.0, -1.0, 1.0)\n"""
    new = anchor + """
    def _infer_markout_quality(
        self,
        book: Book,
        position: int,
        ash_state: dict,
    ) -> Tuple[float, float]:
        buy_markout = float(ash_state.get("buy_markout_ema", 0.0))
        sell_markout = float(ash_state.get("sell_markout_ema", 0.0))
        last_position = int(ash_state.get("last_position", position))
        prev_mid = ash_state.get("prev_mid")
        if prev_mid is not None:
            delta = position - last_position
            move = book.mid - float(prev_mid)
            if delta > 0:
                buy_markout = ema(buy_markout, move, float(self.p["MARKOUT_ALPHA"]))
            elif delta < 0:
                sell_markout = ema(sell_markout, -move, float(self.p["MARKOUT_ALPHA"]))
        return buy_markout, sell_markout
"""
    return replace_once(text, anchor, new)


def patch_build_orders(text: str, flags: set[int]) -> str:
    if 1 in flags:
        text = replace_once(
            text,
            '        slow_fair, take_signal, quote_signal, signal_conviction = self._signal_components(state, book)\n',
            '        buy_markout, sell_markout = self._infer_markout_quality(book, position, ash_state)\n        slow_fair, take_signal, quote_signal, signal_conviction = self._signal_components(state, book)\n',
        )

    old = """        take_reservation = reservation + take_signal\n        buy_edge = take_reservation - book.best_ask\n        sell_edge = book.best_bid - take_reservation\n        soft = int(self.p["SOFT_LIMIT"])\n        pos = mgr.projected()\n        mode = self._mode(book, pos, soft, bid_toxic, ask_toxic, buy_edge, sell_edge, take_signal)\n"""
    new = """        take_reservation = reservation + take_signal\n        buy_edge = take_reservation - book.best_ask\n        sell_edge = book.best_bid - take_reservation\n"""
    if 1 in flags:
        new += """        effective_buy_edge = buy_edge + min(0.0, buy_markout)\n        effective_sell_edge = sell_edge + min(0.0, sell_markout)\n"""
    new += """        soft = int(self.p["SOFT_LIMIT"])\n        pos = mgr.projected()\n"""
    mode_buy = "effective_buy_edge" if 1 in flags else "buy_edge"
    mode_sell = "effective_sell_edge" if 1 in flags else "sell_edge"
    new += f'        mode = self._mode(book, pos, soft, bid_toxic, ask_toxic, {mode_buy}, {mode_sell}, take_signal)\n'
    text = replace_once(text, old, new)

    old = '        profile, take_bonus, edge_bonus, size_bonus, join_bonus = self._execution_profile(mode, attack)\n'
    new = old
    if 4 in flags:
        new += """        conviction_regime = (
            mode == "normal"
            and signal_conviction >= float(self.p["CONVICTION_REGIME"])
            and max(bid_level, ask_level) <= 1
            and sign(quote_signal, 0.10) == sign(take_signal, 0.10)
            and sign(quote_signal, 0.10) != 0
        )\n"""
    text = replace_once(text, old, new)

    old = """        if profile != "defend":\n            scaled_take_bonus = take_bonus * max(0.5, attack if profile != "balanced" else 1.0)\n            buy_need = max(0.70, buy_need - scaled_take_bonus)\n            sell_need = max(0.70, sell_need - scaled_take_bonus)\n        if signal_conviction > 0.0:\n            if take_signal > 0.0:\n                buy_need = max(0.70, buy_need - 0.15 * signal_conviction)\n            elif take_signal < 0.0:\n                sell_need = max(0.70, sell_need - 0.15 * signal_conviction)\n"""
    new = """        if profile != "defend":\n            scaled_take_bonus = take_bonus * max(0.5, attack if profile != "balanced" else 1.0)\n            buy_need = max(0.70, buy_need - scaled_take_bonus)\n            sell_need = max(0.70, sell_need - scaled_take_bonus)\n        if signal_conviction > 0.0:\n            if take_signal > 0.0:\n                buy_need = max(0.70, buy_need - 0.15 * signal_conviction)\n            elif take_signal < 0.0:\n                sell_need = max(0.70, sell_need - 0.15 * signal_conviction)\n"""
    if 1 in flags:
        new += """        if buy_markout < float(self.p["SOFT_BAD_MARKOUT"]) and book.imbalance <= 0.0:\n            buy_need += float(self.p["MARKOUT_EDGE_PENALTY"])\n        if sell_markout < float(self.p["SOFT_BAD_MARKOUT"]) and book.imbalance >= 0.0:\n            sell_need += float(self.p["MARKOUT_EDGE_PENALTY"])\n"""
    if 4 in flags:
        new += """        if conviction_regime:\n            if take_signal > 0.0:\n                buy_need = max(0.60, buy_need - 0.18)\n            elif take_signal < 0.0:\n                sell_need = max(0.60, sell_need - 0.18)\n"""
    if 5 in flags:
        new += """        soft_recycler = (\n            mode == "normal"\n            and signal_conviction <= float(self.p["SOFT_RECYCLE_CONVICTION"])\n            and max(bid_level, ask_level) <= 1\n            and abs(pos) >= int(self.p["SOFT_RECYCLE_POS"])\n        )\n        if soft_recycler:\n            if pos > 0:\n                buy_need += 0.35\n                sell_need = max(0.55, sell_need - 0.20)\n            elif pos < 0:\n                sell_need += 0.35\n                buy_need = max(0.55, buy_need - 0.20)\n"""
    text = replace_once(text, old, new)

    old = """        reactivation = (\n            no_fill_ticks >= 10\n            and mode == "normal"\n            and max(bid_level, ask_level) == 0\n            and abs(pos) <= max(8, soft - 8)\n            and prev_vacuum_side not in ("bid_only", "ask_only")\n            and book.spread_val <= 16\n        )\n        react_side = sign(quote_signal, 0.10)\n        stale_side_base = (\n            mode == "normal"\n            and max(bid_level, ask_level) == 0\n            and abs(pos) <= max(8, soft - 8)\n            and prev_vacuum_side not in ("bid_only", "ask_only")\n            and book.spread_val <= 16\n        )\n        buy_reactivation = stale_side_base and react_side > 0 and bars_since_buy_fill >= 8\n        sell_reactivation = stale_side_base and react_side < 0 and bars_since_sell_fill >= 8\n        micro_nibble = (\n            reactivation\n            and react_side != 0\n            and abs(quote_signal) >= 0.28\n            and signal_conviction >= 0.35\n        )\n        if micro_nibble:\n            if react_side > 0 and can_take_buy and buy_edge >= max(0.80, buy_need - 0.25):\n                mgr.buy(book.best_ask, min(book.best_ask_vol, 2))\n            elif react_side < 0 and can_take_sell and sell_edge >= max(0.80, sell_need - 0.25):\n                mgr.sell(book.best_bid, min(book.best_bid_vol, 2))\n"""
    if 3 in flags:
        new = """        stale_side_base = (\n            mode == "normal"\n            and abs(pos) <= max(8, soft - 8)\n            and book.spread_val <= 16\n            and prev_vacuum_side not in ("bid_only", "ask_only")\n        )\n        buy_reactivation = (\n            stale_side_base\n            and quote_signal > 0.10\n            and bid_level <= 1\n            and bars_since_buy_fill >= 8\n        )\n        sell_reactivation = (\n            stale_side_base\n            and quote_signal < -0.10\n            and ask_level <= 1\n            and bars_since_sell_fill >= 8\n        )\n        micro_nibble = False\n        if (\n            buy_reactivation\n            and abs(pos) <= max(8, soft - 8)\n            and abs(quote_signal) >= 0.28\n            and signal_conviction >= 0.35\n        ):\n            micro_nibble = True\n            if can_take_buy and buy_edge >= max(0.80, buy_need - 0.25):\n                mgr.buy(book.best_ask, min(book.best_ask_vol, 2))\n        elif (\n            sell_reactivation\n            and abs(pos) <= max(8, soft - 8)\n            and abs(quote_signal) >= 0.28\n            and signal_conviction >= 0.35\n        ):\n            micro_nibble = True\n            if can_take_sell and sell_edge >= max(0.80, sell_need - 0.25):\n                mgr.sell(book.best_bid, min(book.best_bid_vol, 2))\n"""
    else:
        new = old
    text = replace_once(text, old, new)

    old = """        if self.p.get("ENABLE_TAKE_LADDER", True) and can_take_buy:\n            take_buy = 0\n            for edge_thr, clip in take_levels:\n                if buy_edge >= max(edge_thr, buy_need):\n                    take_buy = clip\n            if take_buy > 0:\n                if pos >= soft:\n                    take_buy = max(0, take_buy - 3)\n                mgr.buy(book.best_ask, min(book.best_ask_vol, take_buy))\n\n        if self.p.get("ENABLE_TAKE_LADDER", True) and can_take_sell:\n            take_sell = 0\n            for edge_thr, clip in take_levels:\n                if sell_edge >= max(edge_thr, sell_need):\n                    take_sell = clip\n            if take_sell > 0:\n                if pos <= -soft:\n                    take_sell = max(0, take_sell - 3)\n                mgr.sell(book.best_bid, min(book.best_bid_vol, take_sell))\n"""
    buy_edge_var = "effective_buy_edge" if 1 in flags else "buy_edge"
    sell_edge_var = "effective_sell_edge" if 1 in flags else "sell_edge"
    new = ""
    if 2 in flags:
        new += """        high_conviction_sweep = (
            signal_conviction >= float(self.p["HIGH_CONVICTION_SWEEP"])
            and mode == "normal"
            and max(bid_level, ask_level) <= 1
            and take_signal > 0.20
        )\n\n"""
    new += f"""        if self.p.get("ENABLE_TAKE_LADDER", True) and can_take_buy:\n            take_buy = 0\n            for edge_thr, clip in take_levels:\n                if {buy_edge_var} >= max(edge_thr, buy_need):\n                    take_buy = clip\n            if take_buy > 0:\n                if pos >= soft:\n                    take_buy = max(0, take_buy - 3)\n"""
    if 2 in flags:
        new += """                if high_conviction_sweep:\n                    remaining = take_buy\n                    for price, vol in book.sell_levels[:3]:\n                        if vol <= 0 or remaining <= 0:\n                            continue\n                        level_reservation = self._reservation(slow_fair, mgr.projected()) + take_signal\n                        level_edge = level_reservation - price\n                        if level_edge < max(float(self.p["TAKE_L1_EDGE"]) - float(self.p["SWEEP_EDGE_BUFFER"]), buy_need):\n                            break\n                        clip = min(vol, remaining)\n                        mgr.buy(price, clip)\n                        remaining -= clip\n                else:\n                    mgr.buy(book.best_ask, min(book.best_ask_vol, take_buy))\n\n"""
    else:
        new += """                mgr.buy(book.best_ask, min(book.best_ask_vol, take_buy))\n\n"""
    new += f"""        if self.p.get("ENABLE_TAKE_LADDER", True) and can_take_sell:\n            take_sell = 0\n            for edge_thr, clip in take_levels:\n                if {sell_edge_var} >= max(edge_thr, sell_need):\n                    take_sell = clip\n            if take_sell > 0:\n                if pos <= -soft:\n                    take_sell = max(0, take_sell - 3)\n"""
    if 2 in flags:
        new += """                if high_conviction_sweep and take_signal < -0.20:\n                    remaining = take_sell\n                    for price, vol in book.buy_levels[:3]:\n                        if vol <= 0 or remaining <= 0:\n                            continue\n                        level_reservation = self._reservation(slow_fair, mgr.projected()) + take_signal\n                        level_edge = price - level_reservation\n                        if level_edge < max(float(self.p["TAKE_L1_EDGE"]) - float(self.p["SWEEP_EDGE_BUFFER"]), sell_need):\n                            break\n                        clip = min(vol, remaining)\n                        mgr.sell(price, clip)\n                        remaining -= clip\n                else:\n                    mgr.sell(book.best_bid, min(book.best_bid_vol, take_sell))\n"""
    else:
        new += """                mgr.sell(book.best_bid, min(book.best_bid_vol, take_sell))\n"""
    if 5 in flags:
        new += """        if soft_recycler:\n            if pos > 0 and can_take_sell and sell_edge >= max(0.20, sell_need - 0.15):\n                mgr.sell(book.best_bid, min(book.best_bid_vol, 2))\n            elif pos < 0 and can_take_buy and buy_edge >= max(0.20, buy_need - 0.15):\n                mgr.buy(book.best_ask, min(book.best_ask_vol, 2))\n"""
    text = replace_once(text, old, new)

    old = """        if profile != "defend":\n            scaled_edge_bonus = edge_bonus * max(0.5, attack if profile != "balanced" else 1.0)\n            buy_qe -= scaled_edge_bonus\n            sell_qe -= scaled_edge_bonus\n        if signal_conviction > 0.0:\n            if quote_signal > 0.0:\n                buy_qe -= 0.10 * signal_conviction\n            elif quote_signal < 0.0:\n                sell_qe -= 0.10 * signal_conviction\n\n        if buy_reactivation:\n            extra = min(0.30, 0.05 * max(0, bars_since_buy_fill - 8))\n            buy_qe -= 0.15 + extra\n            if micro_nibble:\n                buy_qe -= 0.05\n        elif sell_reactivation:\n            extra = min(0.30, 0.05 * max(0, bars_since_sell_fill - 8))\n            sell_qe -= 0.15 + extra\n            if micro_nibble:\n                sell_qe -= 0.05\n"""
    new = """        if profile != "defend":\n            scaled_edge_bonus = edge_bonus * max(0.5, attack if profile != "balanced" else 1.0)\n            buy_qe -= scaled_edge_bonus\n            sell_qe -= scaled_edge_bonus\n        if signal_conviction > 0.0:\n            if quote_signal > 0.0:\n                buy_qe -= 0.10 * signal_conviction\n            elif quote_signal < 0.0:\n                sell_qe -= 0.10 * signal_conviction\n"""
    if 1 in flags:
        new += """        if buy_markout < float(self.p["SOFT_BAD_MARKOUT"]) and book.imbalance <= 0.0:\n            buy_qe += float(self.p["MARKOUT_EDGE_PENALTY"])\n        if sell_markout < float(self.p["SOFT_BAD_MARKOUT"]) and book.imbalance >= 0.0:\n            sell_qe += float(self.p["MARKOUT_EDGE_PENALTY"])\n"""
    if 4 in flags:
        new += """        if conviction_regime:\n            if quote_signal > 0.0:\n                buy_qe -= 0.18\n                sell_qe += 0.08\n            elif quote_signal < 0.0:\n                sell_qe -= 0.18\n                buy_qe += 0.08\n"""
    if 5 in flags:
        new += """        if soft_recycler:\n            if pos > 0:\n                buy_qe += 0.55\n                sell_qe -= 0.20\n            elif pos < 0:\n                sell_qe += 0.55\n                buy_qe -= 0.20\n"""
    new += """\n        if buy_reactivation:\n            extra = min(0.30, 0.05 * max(0, bars_since_buy_fill - 8))\n            buy_qe -= 0.15 + extra\n            if micro_nibble:\n                buy_qe -= 0.05\n        elif sell_reactivation:\n            extra = min(0.30, 0.05 * max(0, bars_since_sell_fill - 8))\n            sell_qe -= 0.15 + extra\n            if micro_nibble:\n                sell_qe -= 0.05\n"""
    text = replace_once(text, old, new)

    old = """        join_edge = float(self.p["JOIN_EDGE"])\n        if mode == "normal":\n            join_edge += 0.10\n        if profile != "defend":\n            join_edge += join_bonus\n        front_buy = int(round(quote_mid - buy_qe))\n        front_sell = int(round(quote_mid + sell_qe))\n"""
    new = """        join_edge = float(self.p["JOIN_EDGE"])\n        if mode == "normal":\n            join_edge += 0.10\n        if profile != "defend":\n            join_edge += join_bonus\n"""
    if 4 in flags:
        new += """        if conviction_regime:\n            join_edge += 0.18\n"""
    new += """        front_buy = int(round(quote_mid - buy_qe))\n        front_sell = int(round(quote_mid + sell_qe))\n"""
    text = replace_once(text, old, new)

    old = """        allow_bid = pos < soft + 6\n        allow_ask = pos > -(soft + 6)\n        if mode == "inventory_clear":\n            if pos > 0:\n                allow_bid = False\n            elif pos < 0:\n                allow_ask = False\n        if bid_level >= 2 and pos > 8:\n            allow_bid = False\n        if ask_level >= 2 and pos < -8:\n            allow_ask = False\n"""
    new = """        allow_bid = pos < soft + 6\n        allow_ask = pos > -(soft + 6)\n        if mode == "inventory_clear":\n            if pos > 0:\n                allow_bid = False\n            elif pos < 0:\n                allow_ask = False\n        if bid_level >= 2 and pos > 8:\n            allow_bid = False\n        if ask_level >= 2 and pos < -8:\n            allow_ask = False\n"""
    if 1 in flags:
        new += """        if buy_markout < float(self.p["HARD_BAD_MARKOUT"]) and book.imbalance <= 0.0:\n            allow_bid = False\n        if sell_markout < float(self.p["HARD_BAD_MARKOUT"]) and book.imbalance >= 0.0:\n            allow_ask = False\n"""
    if 5 in flags:
        new += """        if soft_recycler:\n            if pos > 0:\n                allow_bid = allow_bid and pos < soft - 2\n            elif pos < 0:\n                allow_ask = allow_ask and pos > -(soft - 2)\n"""
    text = replace_once(text, old, new)

    old = """        if signal_conviction >= 0.95:\n            if quote_signal > 0.0:\n                buy_front_sz += 1\n            elif quote_signal < 0.0:\n                sell_front_sz += 1\n        if buy_reactivation:\n            buy_front_sz += 1 + int(bars_since_buy_fill >= 12)\n            if micro_nibble:\n                buy_front_sz += 1\n        elif sell_reactivation:\n            sell_front_sz += 1 + int(bars_since_sell_fill >= 12)\n            if micro_nibble:\n                sell_front_sz += 1\n        if pos > 6 and bid_level >= 1:\n            sell_front_sz += 1\n        elif pos < -6 and ask_level >= 1:\n            buy_front_sz += 1\n"""
    new = """        if signal_conviction >= 0.95:\n            if quote_signal > 0.0:\n                buy_front_sz += 1\n            elif quote_signal < 0.0:\n                sell_front_sz += 1\n"""
    if 4 in flags:
        new += """        if conviction_regime:\n            if quote_signal > 0.0:\n                buy_front_sz += 2\n            elif quote_signal < 0.0:\n                sell_front_sz += 2\n"""
    new += """        if buy_reactivation:\n            buy_front_sz += 1 + int(bars_since_buy_fill >= 12)\n            if micro_nibble:\n                buy_front_sz += 1\n        elif sell_reactivation:\n            sell_front_sz += 1 + int(bars_since_sell_fill >= 12)\n            if micro_nibble:\n                sell_front_sz += 1\n        if pos > 6 and bid_level >= 1:\n            sell_front_sz += 1\n        elif pos < -6 and ask_level >= 1:\n            buy_front_sz += 1\n"""
    if 1 in flags:
        new += """        if buy_markout < float(self.p["SOFT_BAD_MARKOUT"]) and book.imbalance <= 0.0:\n            buy_front_sz = max(2, int(round(buy_front_sz * (1.0 - float(self.p["MARKOUT_SIZE_PENALTY"])))))\n            buy_back_sz = max(1, int(round(buy_back_sz * (1.0 - float(self.p["MARKOUT_SIZE_PENALTY"])))))\n        if sell_markout < float(self.p["SOFT_BAD_MARKOUT"]) and book.imbalance >= 0.0:\n            sell_front_sz = max(2, int(round(sell_front_sz * (1.0 - float(self.p["MARKOUT_SIZE_PENALTY"])))))\n            sell_back_sz = max(1, int(round(sell_back_sz * (1.0 - float(self.p["MARKOUT_SIZE_PENALTY"])))))\n"""
    text = replace_once(text, old, new)

    old = """        ash_state["last_good_fair"] = round(slow_fair, 4)\n        ash_state["last_good_bid"] = int(book.best_bid)\n        ash_state["last_good_ask"] = int(book.best_ask)\n        ash_state["last_good_mid"] = round(book.mid, 4)\n        ash_state["last_good_spread"] = round(book.spread_val, 4)\n        ash_state["last_fill_ts"] = int(last_fill_ts)\n        ash_state["no_fill_ticks"] = int(no_fill_ticks)\n        ash_state["last_buy_fill_ts"] = int(last_buy_fill_ts)\n        ash_state["last_sell_fill_ts"] = int(last_sell_fill_ts)\n"""
    new = """        ash_state["last_good_fair"] = round(slow_fair, 4)\n        ash_state["last_good_bid"] = int(book.best_bid)\n        ash_state["last_good_ask"] = int(book.best_ask)\n        ash_state["last_good_mid"] = round(book.mid, 4)\n        ash_state["last_good_spread"] = round(book.spread_val, 4)\n"""
    if 1 in flags:
        new += """        ash_state["prev_mid"] = round(book.mid, 4)\n        ash_state["last_position"] = int(position)\n        ash_state["buy_markout_ema"] = round(buy_markout, 4)\n        ash_state["sell_markout_ema"] = round(sell_markout, 4)\n"""
    new += """        ash_state["last_fill_ts"] = int(last_fill_ts)\n        ash_state["no_fill_ticks"] = int(no_fill_ticks)\n        ash_state["last_buy_fill_ts"] = int(last_buy_fill_ts)\n        ash_state["last_sell_fill_ts"] = int(last_sell_fill_ts)\n"""
    text = replace_once(text, old, new)

    return text


def generate_variant(flags: tuple[int, ...]) -> str:
    text = BASE_PATH.read_text()
    flag_set = set(flags)
    text = add_params(text, flag_set)
    if 1 in flag_set:
        text = add_markout_method(text)
    text = patch_build_orders(text, flag_set)
    return text


def main() -> None:
    for r in range(2, 6):
        for combo in combinations([1, 2, 3, 4, 5], r):
            name = "".join(str(x) for x in combo)
            out_path = OUT_DIR / f"TradervR1_121_{name}.py"
            out_path.write_text(generate_variant(combo))
            print(out_path.name)


if __name__ == "__main__":
    main()
