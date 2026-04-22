from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Tuple

try:
    from datamodel import Order, OrderDepth, TradingState
except ModuleNotFoundError:
    from trader_factory.core.datamodel import Order, OrderDepth, TradingState

# ── Position limits (official Round 1 limits are 80) ──────────────────────────
PRODUCT_LIMITS = {
    "ASH_COATED_OSMIUM": 80,
    "INTARIAN_PEPPER_ROOT": 80,
}

# ── ASH_COATED_OSMIUM params ───────────────────────────────────────────────────
# Archetype: local-fair market maker around the 10000 anchor.
DEFAULT_ASH_PARAMS = {
    "ENABLED": True,
    "REFERENCE_PRICE": 10000.0,
    # Local fair estimation
    "ANCHOR_WEIGHT": 0.32,
    "STABLE_MID_WEIGHT": 0.68,
    "MICRO_WEIGHT": 0.48,
    "IMBALANCE_BIAS": 0.18,
    "DEPTH_IMPACT_SCALE": 62.0,
    "DEPTH_FLOOR": 8.0,
    "LOCAL_FAIR_ALPHA": 0.34,
    "BOOK_LEVELS": 3,
    "WALL_MID_BLEND": 0.35,
    # Reservation / inventory pressure
    "INV_L1": 1.55,
    "INV_L3": 3.25,
    "SOFT_LIMIT": 66,
    "HARD_LIMIT_BUFFER": 10,
    # Passive quoting
    "BASE_HALF_SPREAD": 4.05,
    "VOL_MULT": 0.56,
    "SPREAD_MULT": 0.10,
    "JOIN_EDGE": 2.0,
    "MIN_NET_EDGE": 0.12,
    "FRONT_SIZE": 15,
    "BACK_SIZE": 5,
    # Aggressive stale-book taking
    "TAKE_EDGE": 1.35,
    "DISLOCATION_EDGE": 3.55,
    "DISLOCATION_LEVELS": 2,
    "DISLOCATION_CLIP": 12,
    # Toxicity / fill-quality
    "TOXIC_IMBALANCE": 0.24,
    "STRONG_IMBALANCE": 0.16,
    "THIN_DEPTH_FLOOR": 15.0,
    "PENALTY_TOXIC": 0.72,
    "PENALTY_ALPHA": 0.18,
    "SPREAD_ALPHA": 0.10,
    "VOL_ALPHA": 0.10,
    # Inventory freeing
    "CLEARING_EDGE": 0.18,
    "CLEARING_CLIP": 6,
    "CLEARING_NEUTRAL_IMB": 0.10,
}

# ── INTARIAN_PEPPER_ROOT params ────────────────────────────────────────────────
# Archetype: directional_mm with state-based trend + residual tracking
# Key fix: passive quotes anchored to mid (not drift-adjusted fair), so they
# actually land inside the spread and can fill.
DEFAULT_IPR_PARAMS = {
    "ENABLED": True,
    # Trend model
    "DRIFT_PER_TIMESTAMP": 0.0026009226,   # +1 tick / 1000 timestamps → +1000/day
    "RESIDUAL_ALPHA": 0.10,          # EMA alpha for residual tracking
    "SPREAD_ALPHA": 0.08,            # EMA alpha for spread tracking
    "LOOKAHEAD_BONUS": 4.8849030549,          # constant upward bias in fair value
    # Position targeting
    "BASE_CARRY": 7.7045484383,              # always want at least this many units
    "EARLY_LONG_BIAS": 43.1941331644,         # extra target early in day (fades to 0 by 85%)
    "EDGE_TARGET_SCALE": 12.0,       # target += scale * (fair - mid)
    "ZSCORE_BUY_BONUS": 12.0,
    "ZSCORE_SELL_PENALTY": 8.0,
    "MAX_LONG_TARGET": 76.0,
    "MAX_SHORT_TARGET": 20,
    "EARLY_ACCUM_END": 0.42,         # fraction of day where early accumulation ends
    # Execution
    "INVENTORY_SKEW": 0.078,
    "BASE_TAKE_EDGE": 2.7678379562,
    "BASE_QUOTE_EDGE": 5.351603402,
    "SOFT_LIMIT": 52,
    "PASSIVE_FRONT_SIZE": 9,
    "PASSIVE_BACK_SIZE": 6,
    "PASSIVE_BUY_BUFFER": 18,
    "PASSIVE_SELL_BUFFER": 8,
    "OVEREXTENSION_Z": 1.05,
    "BULLISH_IMBALANCE": 0.05,
    # Cheaper accumulation overlay
    "CHEAP_ACCUM_END": 0.56,
    "CHEAP_ACCUM_TAKE_PENALTY": 0.08,
    "CHEAP_ACCUM_QUOTE_EDGE_BONUS": 0.45,
    "CHEAP_ACCUM_FRONT_SIZE_BONUS": 1,
    "CHEAP_ACCUM_BACK_SIZE_BONUS": 1,
    "CHEAP_ACCUM_Z_RELAX": -0.55,
    "CHEAP_ACCUM_TARGET_BUFFER": 20,
}


# ── Shared helpers ─────────────────────────────────────────────────────────────

def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def ema(prev: Optional[float], current: float, alpha: float) -> float:
    if prev is None:
        return current
    return (1.0 - alpha) * prev + alpha * current


class Book:
    """Parsed order book snapshot."""

    def __init__(self, depth: Optional[OrderDepth]) -> None:
        self.valid = False
        self.buy_levels: List[Tuple[int, int]] = []
        self.sell_levels: List[Tuple[int, int]] = []
        self.best_bid = self.best_ask = 0
        self.best_bid_vol = self.best_ask_vol = 0
        self.mid = self.micro = self.spread_val = self.imbalance = 0.0

        if depth is None:
            return
        self.buy_levels = sorted(
            ((int(p), int(v)) for p, v in depth.buy_orders.items()),
            key=lambda x: x[0], reverse=True,
        )
        self.sell_levels = sorted(
            ((int(p), abs(int(v))) for p, v in depth.sell_orders.items()),
            key=lambda x: x[0],
        )
        if not self.buy_levels or not self.sell_levels:
            return
        self.best_bid, self.best_bid_vol = self.buy_levels[0]
        self.best_ask, self.best_ask_vol = self.sell_levels[0]
        if self.best_bid >= self.best_ask:
            return
        self.mid = (self.best_bid + self.best_ask) / 2.0
        self.spread_val = float(self.best_ask - self.best_bid)
        total = self.best_bid_vol + self.best_ask_vol
        if total > 0:
            self.micro = (self.best_ask * self.best_bid_vol + self.best_bid * self.best_ask_vol) / total
            self.imbalance = (self.best_bid_vol - self.best_ask_vol) / total
        else:
            self.micro = self.mid
        self.valid = True


class Manager:
    """Capacity-tracking order builder."""

    def __init__(self, product: str, position: int, limit: int) -> None:
        self.product = product
        self.position = int(position)
        self.limit = int(limit)
        self.buy_cap = max(0, limit - position)
        self.sell_cap = max(0, limit + position)
        self.orders: List[Order] = []

    def projected(self) -> int:
        return self.position + sum(o.quantity for o in self.orders)

    def buy(self, price: int, qty: int) -> None:
        size = min(max(0, int(qty)), self.buy_cap)
        if size > 0:
            self.orders.append(Order(self.product, int(price), size))
            self.buy_cap -= size

    def sell(self, price: int, qty: int) -> None:
        size = min(max(0, int(qty)), self.sell_cap)
        if size > 0:
            self.orders.append(Order(self.product, int(price), -size))
            self.sell_cap -= size


# ── ASH_COATED_OSMIUM trader ───────────────────────────────────────────────────

class AshCoatedOsmiumTrader:
    """
    Local-fair Osmium engine.
    The long-run anchor stays at 10000, but the live fair is estimated from
    robust book structure, then used for reservation pricing, toxicity-aware
    passive quoting, controlled dislocation taking, and gentle capacity freeing.
    """

    def __init__(self, params: dict) -> None:
        self.p = params

    def _load_state(self, memory: dict) -> dict:
        raw = memory.get("ASH_STATE", {})
        if not isinstance(raw, dict):
            raw = {}
        return {
            "prev_mid": float(raw.get("prev_mid", 0.0)),
            "prev_pos": int(raw.get("prev_pos", 0)),
            "spread_ema": float(raw.get("spread_ema", 14.0)),
            "vol_ema": float(raw.get("vol_ema", 1.5)),
            "buy_penalty_ema": float(raw.get("buy_penalty_ema", 0.35)),
            "sell_penalty_ema": float(raw.get("sell_penalty_ema", 0.35)),
            "fair_ema": float(raw.get("fair_ema", float(self.p["REFERENCE_PRICE"]))),
        }

    def _update_state_from_realized_fills(self, book: Book, position: int, st: dict) -> dict:
        prev_mid = float(st["prev_mid"])
        prev_pos = int(st["prev_pos"])
        move = 0.0 if prev_mid <= 0.0 else (book.mid - prev_mid)
        st["spread_ema"] = ema(float(st["spread_ema"]), book.spread_val, float(self.p["SPREAD_ALPHA"]))
        st["vol_ema"] = ema(float(st["vol_ema"]), abs(move), float(self.p["VOL_ALPHA"]))

        delta_pos = position - prev_pos
        penalty_alpha = float(self.p["PENALTY_ALPHA"])
        if delta_pos > 0:
            st["buy_penalty_ema"] = ema(float(st["buy_penalty_ema"]), max(0.0, -move), penalty_alpha)
        else:
            st["buy_penalty_ema"] = ema(float(st["buy_penalty_ema"]), 0.0, 0.06)
        if delta_pos < 0:
            st["sell_penalty_ema"] = ema(float(st["sell_penalty_ema"]), max(0.0, move), penalty_alpha)
        else:
            st["sell_penalty_ema"] = ema(float(st["sell_penalty_ema"]), 0.0, 0.06)
        return st

    def _stable_mid(self, book: Book) -> float:
        levels = max(1, int(self.p["BOOK_LEVELS"]))
        bid_levels = book.buy_levels[:levels]
        ask_levels = book.sell_levels[:levels]
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

    def _fair_value(self, book: Book, st: dict) -> tuple[float, float]:
        stable_mid = self._stable_mid(book)
        depth = max(float(self.p["DEPTH_FLOOR"]), float(book.best_bid_vol + book.best_ask_vol))
        beta = float(self.p["DEPTH_IMPACT_SCALE"]) / depth
        raw_local = (
            float(self.p["ANCHOR_WEIGHT"]) * float(self.p["REFERENCE_PRICE"])
            + float(self.p["STABLE_MID_WEIGHT"]) * stable_mid
            + float(self.p["MICRO_WEIGHT"]) * (book.micro - book.mid)
            + (beta + float(self.p["IMBALANCE_BIAS"])) * book.imbalance
        )
        local_fair = ema(float(st["fair_ema"]), raw_local, float(self.p["LOCAL_FAIR_ALPHA"]))
        return local_fair, stable_mid

    def _reservation(self, fair: float, projected_pos: int) -> float:
        inv_ratio = projected_pos / float(PRODUCT_LIMITS["ASH_COATED_OSMIUM"])
        inv_pressure = float(self.p["INV_L1"]) * inv_ratio + float(self.p["INV_L3"]) * (inv_ratio ** 3)
        return fair - inv_pressure

    def _toxicity(self, book: Book, st: dict) -> tuple[bool, bool, float, float, bool, bool]:
        tox = float(self.p["TOXIC_IMBALANCE"])
        bid_support = float(sum(v for _, v in book.buy_levels[:2]))
        ask_support = float(sum(v for _, v in book.sell_levels[:2]))
        thin_floor = float(self.p["THIN_DEPTH_FLOOR"])
        bid_thin = bid_support < thin_floor or bid_support < 0.55 * ask_support
        ask_thin = ask_support < thin_floor or ask_support < 0.55 * bid_support

        bid_toxic = book.imbalance < -tox and (book.micro < book.mid or bid_thin)
        ask_toxic = book.imbalance > tox and (book.micro > book.mid or ask_thin)
        bid_penalty = (
            float(st["buy_penalty_ema"])
            + float(self.p["PENALTY_TOXIC"]) * max(0.0, -book.imbalance)
            + max(0.0, book.mid - book.micro)
            + (0.14 if bid_thin else 0.0)
            + 0.08 * float(st["vol_ema"])
        )
        ask_penalty = (
            float(st["sell_penalty_ema"])
            + float(self.p["PENALTY_TOXIC"]) * max(0.0, book.imbalance)
            + max(0.0, book.micro - book.mid)
            + (0.14 if ask_thin else 0.0)
            + 0.08 * float(st["vol_ema"])
        )
        return bid_toxic, ask_toxic, bid_penalty, ask_penalty, bid_thin, ask_thin

    def _quote_half_spreads(
        self,
        book: Book,
        st: dict,
        projected_pos: int,
        fair: float,
        bid_toxic: bool,
        ask_toxic: bool,
    ) -> tuple[float, float]:
        inv_ratio = projected_pos / float(PRODUCT_LIMITS["ASH_COATED_OSMIUM"])
        base_half = (
            float(self.p["BASE_HALF_SPREAD"])
            + float(self.p["VOL_MULT"]) * float(st["vol_ema"])
            + float(self.p["SPREAD_MULT"]) * max(0.0, float(st["spread_ema"]) - 12.0)
        )
        buy_half = base_half
        sell_half = base_half

        if inv_ratio > 0.0:
            buy_half += 1.45 * inv_ratio + 2.9 * (inv_ratio ** 3)
            sell_half -= 0.55 * inv_ratio
        elif inv_ratio < 0.0:
            sell_half += 1.45 * (-inv_ratio) + 2.9 * ((-inv_ratio) ** 3)
            buy_half -= 0.55 * (-inv_ratio)

        strong = float(self.p["STRONG_IMBALANCE"])
        if book.imbalance > strong:
            buy_half -= 0.40
            sell_half += 0.22
        elif book.imbalance < -strong:
            buy_half += 0.22
            sell_half -= 0.40

        fair_stability = abs(fair - float(st["fair_ema"]))
        if fair_stability < 0.55 and abs(inv_ratio) < 0.24 and not bid_toxic and not ask_toxic:
            buy_half -= 0.25
            sell_half -= 0.25

        if bid_toxic:
            buy_half += 0.80
        if ask_toxic:
            sell_half += 0.80

        return max(4.0, buy_half), max(4.0, sell_half)

    def _dislocation_take(
        self,
        mgr: Manager,
        book: Book,
        reservation: float,
        bid_penalty: float,
        ask_penalty: float,
        bid_toxic: bool,
        ask_toxic: bool,
    ) -> None:
        take_edge = float(self.p["TAKE_EDGE"])
        disloc_edge = float(self.p["DISLOCATION_EDGE"])
        max_levels = max(1, int(self.p["DISLOCATION_LEVELS"]))
        clip = int(self.p["DISLOCATION_CLIP"])
        soft = int(self.p["SOFT_LIMIT"])

        if not bid_toxic:
            for idx, (ask_px, ask_vol) in enumerate(book.sell_levels[:max_levels]):
                edge = reservation - ask_px - 0.35 * bid_penalty
                threshold = disloc_edge if idx > 0 else take_edge
                if edge < threshold:
                    break
                qty = min(ask_vol, clip if idx > 0 else min(clip, 8))
                if mgr.projected() >= soft:
                    qty = max(0, qty - 3)
                mgr.buy(ask_px, qty)

        if not ask_toxic:
            for idx, (bid_px, bid_vol) in enumerate(book.buy_levels[:max_levels]):
                edge = bid_px - reservation - 0.35 * ask_penalty
                threshold = disloc_edge if idx > 0 else take_edge
                if edge < threshold:
                    break
                qty = min(bid_vol, clip if idx > 0 else min(clip, 8))
                if mgr.projected() <= -soft:
                    qty = max(0, qty - 3)
                mgr.sell(bid_px, qty)

    def build_orders(self, state: TradingState, memory: dict) -> Tuple[List[Order], dict]:
        if not self.p.get("ENABLED", True):
            return [], memory
        book = Book(state.order_depths.get("ASH_COATED_OSMIUM"))
        if not book.valid:
            return [], memory

        position = int(state.position.get("ASH_COATED_OSMIUM", 0))
        mgr = Manager("ASH_COATED_OSMIUM", position, PRODUCT_LIMITS["ASH_COATED_OSMIUM"])
        st = self._load_state(memory)
        st = self._update_state_from_realized_fills(book, position, st)

        fair, stable_mid = self._fair_value(book, st)
        reservation = self._reservation(fair, mgr.projected())
        bid_toxic, ask_toxic, bid_penalty, ask_penalty, bid_thin, ask_thin = self._toxicity(book, st)

        self._dislocation_take(mgr, book, reservation, bid_penalty, ask_penalty, bid_toxic, ask_toxic)
        reservation = self._reservation(fair, mgr.projected())

        buy_half, sell_half = self._quote_half_spreads(book, st, mgr.projected(), fair, bid_toxic, ask_toxic)
        front_buy = int(math.floor(reservation - buy_half))
        front_sell = int(math.ceil(reservation + sell_half))
        back_buy = front_buy - 2
        back_sell = front_sell + 2

        join_edge = float(self.p["JOIN_EDGE"])
        for price, _ in book.buy_levels[:2]:
            if reservation - price >= buy_half and reservation - price <= buy_half + join_edge:
                front_buy = price
                break
        for price, _ in book.sell_levels[:2]:
            if price - reservation >= sell_half and price - reservation <= sell_half + join_edge:
                front_sell = price
                break

        if (
            not bid_toxic
            and book.spread_val <= 16
            and reservation - (book.best_bid + 1) >= 0.30
        ):
            front_buy = max(front_buy, book.best_bid + 1)
        if (
            not ask_toxic
            and book.spread_val <= 16
            and (book.best_ask - 1) - reservation >= 0.30
        ):
            front_sell = min(front_sell, book.best_ask - 1)

        front_buy = min(front_buy, book.best_ask - 1)
        front_sell = max(front_sell, book.best_bid + 1)
        back_buy = min(back_buy, book.best_ask - 1)
        back_sell = max(back_sell, book.best_bid + 1)

        projected = mgr.projected()
        inv_ratio = projected / float(PRODUCT_LIMITS["ASH_COATED_OSMIUM"])
        soft = int(self.p["SOFT_LIMIT"])
        hard_buf = int(self.p["HARD_LIMIT_BUFFER"])
        gross_bid_edge = reservation - front_buy
        gross_ask_edge = front_sell - reservation
        net_bid_edge = gross_bid_edge - bid_penalty
        net_ask_edge = gross_ask_edge - ask_penalty
        min_net = float(self.p["MIN_NET_EDGE"])

        allow_bid = net_bid_edge >= min_net and not (bid_toxic and projected > 6)
        allow_ask = net_ask_edge >= min_net and not (ask_toxic and projected < -6)
        if projected >= soft + hard_buf:
            allow_bid = False
        if projected <= -(soft + hard_buf):
            allow_ask = False

        # When inventory is stretched and book state is neutral, free capacity near flat edge.
        neutral = abs(book.imbalance) <= float(self.p["CLEARING_NEUTRAL_IMB"])
        fair_not_supporting_long = fair <= stable_mid + 0.8
        fair_not_supporting_short = fair >= stable_mid - 0.8
        allow_clear_sell = (
            projected > soft
            and neutral
            and not bid_toxic
            and fair_not_supporting_long
            and net_ask_edge >= -float(self.p["CLEARING_EDGE"])
        )
        allow_clear_buy = (
            projected < -soft
            and neutral
            and not ask_toxic
            and fair_not_supporting_short
            and net_bid_edge >= -float(self.p["CLEARING_EDGE"])
        )
        if allow_clear_buy:
            allow_bid = True
        if allow_clear_sell:
            allow_ask = True

        front_sz = int(self.p["FRONT_SIZE"])
        back_sz = int(self.p["BACK_SIZE"])
        if book.spread_val <= 12:
            front_sz = max(13, front_sz - 1)
        elif book.spread_val >= 18 and not bid_toxic and not ask_toxic:
            front_sz += 1
        if allow_bid and front_buy > 0 and front_buy < book.best_ask:
            size = front_sz + (3 if inv_ratio < -0.45 else 0)
            if allow_clear_buy:
                size = min(size, int(self.p["CLEARING_CLIP"]))
            mgr.buy(front_buy, size)
            if (
                back_buy > 0
                and back_buy < book.best_ask
                and not bid_toxic
                and not bid_thin
                and net_bid_edge >= min_net + 0.18
            ):
                mgr.buy(back_buy, back_sz)

        if allow_ask and front_sell > book.best_bid:
            size = front_sz + (3 if inv_ratio > 0.45 else 0)
            if allow_clear_sell:
                size = min(size, int(self.p["CLEARING_CLIP"]))
            mgr.sell(front_sell, size)
            if (
                back_sell > book.best_bid
                and not ask_toxic
                and not ask_thin
                and net_ask_edge >= min_net + 0.18
            ):
                mgr.sell(back_sell, back_sz)

        memory["ASH_STATE"] = {
            "prev_mid": float(book.mid),
            "prev_pos": int(position),
            "spread_ema": float(st["spread_ema"]),
            "vol_ema": float(st["vol_ema"]),
            "buy_penalty_ema": float(st["buy_penalty_ema"]),
            "sell_penalty_ema": float(st["sell_penalty_ema"]),
            "fair_ema": float(fair),
        }
        return mgr.orders, memory


# ── INTARIAN_PEPPER_ROOT trader ────────────────────────────────────────────────

class IntarianPepperRootTrader:
    """
    Directional MM for strongly trending asset (+1000 ticks/day).
    - State: anchor price + residual EMA persisted in traderData
    - Fair value: weighted blend of trend-line, mid, micro, flow + lookahead bonus
    - Position target: BASE_CARRY + early long bias (fades) + edge/zscore signals
    - Passive quotes anchored to RESERVATION (near mid), NOT to drift-adjusted fair
      → quotes land inside the spread and actually fill
    - Sell suppression in bullish state to stay long through the trend
    """

    def __init__(self, params: dict) -> None:
        self.p = params

    def build_orders(self, state: TradingState, memory: dict) -> Tuple[List[Order], dict]:
        if not self.p.get("ENABLED", True):
            return [], memory

        book = Book(state.order_depths.get("INTARIAN_PEPPER_ROOT"))
        if not book.valid:
            return [], memory

        position = int(state.position.get("INTARIAN_PEPPER_ROOT", 0))
        mgr = Manager("INTARIAN_PEPPER_ROOT", position, PRODUCT_LIMITS["INTARIAN_PEPPER_ROOT"])
        timestamp = int(getattr(state, "timestamp", 0))
        progress = clamp(timestamp / 999900.0, 0.0, 1.0)

        # ── Load / init persistent state ──────────────────────────────────────
        ps = memory.get("IPR_STATE", {})
        if not isinstance(ps, dict):
            ps = {}

        initialized = bool(ps.get("initialized", False))
        anchor = float(ps.get("anchor", 0.0))
        residual_ema_val = float(ps.get("residual_ema", 0.0))
        spread_ema_val = float(ps.get("spread_ema", 13.0))
        last_ts = float(ps.get("last_ts", -1.0))

        # Day reset
        if last_ts >= 0 and timestamp < last_ts:
            initialized = False
            anchor = 0.0
            residual_ema_val = 0.0
            spread_ema_val = 13.0

        drift = float(self.p["DRIFT_PER_TIMESTAMP"])
        trend_line = anchor + drift * timestamp

        if not initialized:
            anchor = round(book.mid / 1000.0) * 1000.0
            trend_line = anchor
            residual_ema_val = 0.0
            spread_ema_val = float(book.spread_val)
            initialized = True
        else:
            spread_ema_val = ema(spread_ema_val, book.spread_val, float(self.p["SPREAD_ALPHA"]))

        residual = book.mid - trend_line
        residual_ema_val = ema(residual_ema_val, residual, float(self.p["RESIDUAL_ALPHA"]))

        # ── Fair value ────────────────────────────────────────────────────────
        half_spread = max(1.0, book.spread_val / 2.0)
        flow_fair = book.mid + book.imbalance * half_spread
        lookahead = float(self.p["LOOKAHEAD_BONUS"]) * (1.0 - 0.65 * progress)
        fair = (
            0.60 * trend_line
            + 0.12 * book.mid
            + 0.10 * book.micro
            + 0.10 * flow_fair
            + 0.08 * (trend_line + residual)
            + lookahead
        )

        # ── z-score of residual ───────────────────────────────────────────────
        spread_scale = max(4.0, spread_ema_val * 0.45)
        zscore = residual / spread_scale

        # ── Target position ───────────────────────────────────────────────────
        edge = fair - book.mid
        target = float(self.p["BASE_CARRY"])
        early_factor = max(0.0, 1.0 - progress / 0.85)
        target += float(self.p["EARLY_LONG_BIAS"]) * early_factor
        target += float(self.p["EDGE_TARGET_SCALE"]) * edge

        if zscore < 0.0:
            target += float(self.p["ZSCORE_BUY_BONUS"]) * min(1.0, abs(zscore) / 1.8)
        if zscore > 0.45:
            target -= float(self.p["ZSCORE_SELL_PENALTY"]) * min(1.0, (zscore - 0.45) / 1.4)
        if book.imbalance < -0.18 and book.micro < book.mid:
            target -= 6.0

        bullish = (
            zscore < float(self.p["OVEREXTENSION_Z"])
            and book.imbalance >= float(self.p["BULLISH_IMBALANCE"])
            and book.micro >= book.mid
        )
        if bullish:
            target += 8.0

        if progress < 0.18 and zscore <= 0.45:
            target = max(target, 32.0)
        elif progress < 0.35 and zscore <= 0.25:
            target = max(target, 24.0)
        if progress > 0.85 and zscore > 1.25:
            target -= 8.0

        max_long = int(self.p["MAX_LONG_TARGET"])
        max_short = int(self.p["MAX_SHORT_TARGET"])
        target_int = int(clamp(target, -max_short, max_long))

        # ── Reservation price ─────────────────────────────────────────────────
        skew = float(self.p["INVENTORY_SKEW"])
        reservation = fair - (mgr.projected() - target_int) * skew

        # ── Take orders ───────────────────────────────────────────────────────
        base_take = float(self.p["BASE_TAKE_EDGE"])
        buy_te = base_take
        sell_te = base_take + 0.55
        pos = mgr.projected()
        if pos < target_int:
            buy_te -= 0.35
        if pos > target_int:
            sell_te -= 0.05
        if zscore < -0.45:
            buy_te -= 0.30
        elif zscore > 0.85:
            sell_te -= 0.15
        if bullish:
            buy_te -= 0.10
            sell_te += 0.90
        if progress < 0.55 and pos < target_int:
            sell_te += 0.25
        if pos < max(20, target_int - 10):
            sell_te += 0.55
        if (
            progress < float(self.p["CHEAP_ACCUM_END"])
            and pos < target_int
            and zscore > float(self.p["CHEAP_ACCUM_Z_RELAX"])
        ):
            buy_te += float(self.p["CHEAP_ACCUM_TAKE_PENALTY"])
        buy_te = max(0.35, buy_te)
        sell_te = max(1.05, sell_te)

        buy_edge_avail = reservation - book.best_ask
        if buy_edge_avail >= buy_te and mgr.buy_cap > 0:
            qty = min(book.best_ask_vol, 16, max(0, target_int + 16 - mgr.projected()))
            mgr.buy(book.best_ask, qty)

        sell_edge_avail = book.best_bid - reservation
        if sell_edge_avail >= sell_te and mgr.sell_cap > 0:
            pos = mgr.projected()
            qty = min(book.best_bid_vol, 16, max(0, pos - (target_int - 4)))
            if bullish and pos < max(26, target_int - 6):
                qty = 0
            elif bullish and pos > 0:
                qty = min(qty, 4)
            mgr.sell(book.best_bid, qty)

        # ── Passive quotes ────────────────────────────────────────────────────
        # Anchored to RESERVATION (near actual mid), NOT to drift-adjusted fair.
        # This places quotes inside the spread where they can actually fill.
        base_qe = float(self.p["BASE_QUOTE_EDGE"])
        buy_qe = base_qe
        sell_qe = base_qe + 0.75
        pos = mgr.projected()
        if pos < target_int:
            buy_qe -= 0.55
        if pos > target_int:
            sell_qe -= 0.10
        if zscore < -0.55:
            buy_qe -= 0.30
        elif zscore > 1.00:
            sell_qe -= 0.15
        cheap_accum = (
            progress < float(self.p["CHEAP_ACCUM_END"])
            and pos < target_int
            and zscore > float(self.p["CHEAP_ACCUM_Z_RELAX"])
        )
        if cheap_accum:
            buy_qe -= float(self.p["CHEAP_ACCUM_QUOTE_EDGE_BONUS"])

        front_buy = math.floor(reservation - buy_qe)
        front_sell = math.ceil(reservation + sell_qe)

        if bullish and pos < target_int:
            front_buy = max(front_buy, book.best_bid + 1)
        elif cheap_accum and pos < target_int:
            front_buy = max(front_buy, book.best_bid + 1)
        if bullish and pos > 0:
            front_sell += 2

        front_buy = min(front_buy, book.best_ask - 1)
        front_sell = max(front_sell, book.best_bid + 1)
        back_buy = min(front_buy - 2, book.best_ask - 1)
        back_sell = max(front_sell + 2, book.best_bid + 1)

        # Sell suppression: don't sell when accumulating / bullish
        early_accum = float(self.p["EARLY_ACCUM_END"])
        allow_sell = True
        if progress < early_accum and pos < target_int - 6:
            allow_sell = False
        if bullish and pos < max(24, target_int - 4):
            allow_sell = False

        front_sz = int(self.p["PASSIVE_FRONT_SIZE"])
        back_sz = int(self.p["PASSIVE_BACK_SIZE"])
        buy_buf = int(self.p["PASSIVE_BUY_BUFFER"])
        sell_buf = int(self.p["PASSIVE_SELL_BUFFER"])
        buy_front_sz = front_sz + (int(self.p["CHEAP_ACCUM_FRONT_SIZE_BONUS"]) if cheap_accum else 0)
        buy_back_sz = back_sz + (int(self.p["CHEAP_ACCUM_BACK_SIZE_BONUS"]) if cheap_accum else 0)
        buy_cap_target = target_int + (
            int(self.p["CHEAP_ACCUM_TARGET_BUFFER"]) if cheap_accum else buy_buf
        )

        quotes: List[Tuple[str, int, int]] = []
        if front_buy > 0 and front_buy < book.best_ask:
            quotes.append(("buy", front_buy, buy_front_sz))
            if back_buy > 0 and back_buy < book.best_ask:
                quotes.append(("buy", back_buy, buy_back_sz))
        if allow_sell and front_sell > book.best_bid:
            sell_front = max(3, front_sz - (3 if bullish else 1))
            sell_back = max(2, back_sz - (2 if bullish else 1))
            quotes.append(("sell", front_sell, sell_front))
            if back_sell > book.best_bid:
                quotes.append(("sell", back_sell, sell_back))

        for side, price, size in quotes:
            pos = mgr.projected()
            if side == "buy" and pos < buy_cap_target:
                qty = min(size, mgr.buy_cap, max(0, buy_cap_target - pos))
                mgr.buy(price, qty)
            elif side == "sell" and pos > target_int - sell_buf:
                qty = min(size, mgr.sell_cap, max(0, pos - (target_int - sell_buf)))
                mgr.sell(price, qty)

        # ── Save state ────────────────────────────────────────────────────────
        memory["IPR_STATE"] = {
            "anchor": anchor,
            "residual_ema": residual_ema_val,
            "spread_ema": spread_ema_val,
            "last_ts": float(timestamp),
            "initialized": True,
        }

        return mgr.orders, memory


# ── Top-level Trader ───────────────────────────────────────────────────────────

class Trader:
    def __init__(self) -> None:
        self.ash = AshCoatedOsmiumTrader(DEFAULT_ASH_PARAMS)
        self.ipr = IntarianPepperRootTrader(DEFAULT_IPR_PARAMS)

    def _load_memory(self, trader_data: str) -> dict:
        if not trader_data:
            return {}
        try:
            parsed = json.loads(trader_data)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    def run(self, state: TradingState):
        memory = self._load_memory(state.traderData if hasattr(state, "traderData") else "")
        result: Dict[str, List[Order]] = {}

        if "ASH_COATED_OSMIUM" in state.order_depths:
            ash_orders, memory = self.ash.build_orders(state, memory)
            result["ASH_COATED_OSMIUM"] = ash_orders

        if "INTARIAN_PEPPER_ROOT" in state.order_depths:
            ipr_orders, memory = self.ipr.build_orders(state, memory)
            result["INTARIAN_PEPPER_ROOT"] = ipr_orders

        trader_data = json.dumps(memory, separators=(",", ":"))
        return result, 0, trader_data
