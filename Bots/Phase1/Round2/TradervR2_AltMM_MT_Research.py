from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Tuple, Any

try:
    from datamodel import Order, OrderDepth, Trade, TradingState
except ModuleNotFoundError:
    from trader_factory.core.datamodel import Order, OrderDepth, Trade, TradingState


# Deliberately different Round 2 research branch.
# Philosophy:
# - ASH_COATED_OSMIUM: Avellaneda-Stoikov / Guéant-style inventory-aware maker
#   with robust fair estimation, queue-health gating, and impulse taking.
# - INTARIAN_PEPPER_ROOT: drift-following optimal-execution engine with schedule,
#   catch-up, and anti-chase rather than the previous residual-heavy maker.
#
# The bid is intentionally not huge. Testing ignores bid(), but for final EV this
# is safer than paying 25k unless the access delta is proven larger.
ROUND2_MAF_BID = 8000

PRODUCT_LIMITS = {
    "ASH_COATED_OSMIUM": 80,
    "INTARIAN_PEPPER_ROOT": 80,
}

ASH = "ASH_COATED_OSMIUM"
PEPPER = "INTARIAN_PEPPER_ROOT"


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def ema(prev: Optional[float], value: float, alpha: float) -> float:
    if prev is None:
        return value
    return (1.0 - alpha) * prev + alpha * value


def sgn(value: float, eps: float = 1e-9) -> int:
    if value > eps:
        return 1
    if value < -eps:
        return -1
    return 0


def median3(a: float, b: float, c: float) -> float:
    return sorted([a, b, c])[1]


class Book:
    def __init__(self, depth: Optional[OrderDepth]) -> None:
        self.buy_levels: List[Tuple[int, int]] = []
        self.sell_levels: List[Tuple[int, int]] = []
        self.has_bid = False
        self.has_ask = False
        self.valid = False
        self.best_bid = 0
        self.best_ask = 0
        self.best_bid_vol = 0
        self.best_ask_vol = 0
        self.mid = 0.0
        self.micro = 0.0
        self.spread = 0.0
        self.imbalance = 0.0

        if depth is None:
            return

        self.buy_levels = sorted(
            ((int(price), int(volume)) for price, volume in depth.buy_orders.items() if int(volume) > 0),
            key=lambda x: x[0],
            reverse=True,
        )
        self.sell_levels = sorted(
            ((int(price), abs(int(volume))) for price, volume in depth.sell_orders.items() if int(volume) < 0),
            key=lambda x: x[0],
        )

        if self.buy_levels:
            self.has_bid = True
            self.best_bid, self.best_bid_vol = self.buy_levels[0]
        if self.sell_levels:
            self.has_ask = True
            self.best_ask, self.best_ask_vol = self.sell_levels[0]

        if not self.has_bid and not self.has_ask:
            return
        if self.has_bid and not self.has_ask:
            self.mid = float(self.best_bid)
            self.micro = self.mid
            return
        if self.has_ask and not self.has_bid:
            self.mid = float(self.best_ask)
            self.micro = self.mid
            return
        if self.best_bid >= self.best_ask:
            return

        self.valid = True
        self.mid = (self.best_bid + self.best_ask) / 2.0
        self.spread = float(self.best_ask - self.best_bid)
        total = self.best_bid_vol + self.best_ask_vol
        if total > 0:
            self.micro = (self.best_ask * self.best_bid_vol + self.best_bid * self.best_ask_vol) / total
            self.imbalance = (self.best_bid_vol - self.best_ask_vol) / total
        else:
            self.micro = self.mid
            self.imbalance = 0.0

    def depth_sum(self, n: int = 3) -> int:
        return sum(v for _, v in self.buy_levels[:n]) + sum(v for _, v in self.sell_levels[:n])

    def stable_mid(self, n: int = 3, wall_blend: float = 0.25) -> float:
        if not self.valid:
            return self.mid
        bids = self.buy_levels[:n]
        asks = self.sell_levels[:n]
        if not bids or not asks:
            return self.mid
        bid_vol = sum(v for _, v in bids)
        ask_vol = sum(v for _, v in asks)
        if bid_vol <= 0 or ask_vol <= 0:
            return self.mid
        pop_bid = sum(px * v for px, v in bids) / bid_vol
        pop_ask = sum(px * v for px, v in asks) / ask_vol
        pop_mid = (pop_bid + pop_ask) / 2.0
        wall_bid = max(bids, key=lambda x: (x[1], x[0]))[0]
        wall_ask = min(asks, key=lambda x: (-x[1], x[0]))[0]
        wall_mid = (wall_bid + wall_ask) / 2.0
        return (1.0 - wall_blend) * pop_mid + wall_blend * wall_mid


class OrderManager:
    def __init__(self, product: str, position: int, limit: int) -> None:
        self.product = product
        self.position = int(position)
        self.limit = int(limit)
        self.buy_cap = max(0, self.limit - self.position)
        self.sell_cap = max(0, self.limit + self.position)
        self.orders: List[Order] = []

    def projected(self) -> int:
        return self.position + sum(order.quantity for order in self.orders)

    def buy(self, price: int, quantity: int) -> None:
        qty = min(max(0, int(quantity)), self.buy_cap)
        if qty <= 0:
            return
        self.orders.append(Order(self.product, int(price), qty))
        self.buy_cap -= qty

    def sell(self, price: int, quantity: int) -> None:
        qty = min(max(0, int(quantity)), self.sell_cap)
        if qty <= 0:
            return
        self.orders.append(Order(self.product, int(price), -qty))
        self.sell_cap -= qty


class AshASController:
    """Alternative Osmium engine: risk-based maker + impulse market-taker.

    This does not try to reproduce the old local-fair/conviction tree. It treats
    Osmium as a noisy anchored asset with endogenous fill intensity. Quotes are
    generated from a reservation price and dynamic half-spread, not static edges.
    """

    LIMIT = PRODUCT_LIMITS[ASH]
    ANCHOR = 10000.0

    def _memory(self, memory: dict) -> dict:
        state = memory.get("ASH_AS_STATE", {})
        return state if isinstance(state, dict) else {}

    def _save(self, memory: dict, state: dict) -> dict:
        memory["ASH_AS_STATE"] = state
        return memory

    def _trade_pressure(self, state: TradingState, book: Book) -> float:
        # Public trades are weak alone, but useful as pressure confirmation.
        trades = []
        try:
            trades = list(state.market_trades.get(ASH, []))
        except Exception:
            return 0.0
        if not trades or not book.valid:
            return 0.0
        signed = 0.0
        total = 0.0
        for tr in trades[-6:]:
            price = float(getattr(tr, "price", book.mid))
            qty = abs(float(getattr(tr, "quantity", 0)))
            if qty <= 0:
                continue
            # Print near ask = buyer-initiated; near bid = seller-initiated.
            if price >= book.mid:
                signed += qty
            else:
                signed -= qty
            total += qty
        if total <= 0:
            return 0.0
        return clamp(signed / total, -1.0, 1.0)

    def _book_health(self, book: Book, last_good_fair: Optional[float]) -> float:
        if not book.has_bid and not book.has_ask:
            return 0.0
        if not book.valid:
            return 0.15
        levels = min(len(book.buy_levels), len(book.sell_levels), 3)
        level_score = levels / 3.0
        spread_score = clamp((24.0 - book.spread) / 10.0, 0.0, 1.0)
        depth_score = clamp(book.depth_sum(3) / 70.0, 0.0, 1.0)
        thin_touch_penalty = 0.0
        if book.best_bid_vol <= 5 or book.best_ask_vol <= 5:
            thin_touch_penalty = 0.12
        jump_penalty = 0.0
        if last_good_fair is not None and abs(book.mid - last_good_fair) > 10.0:
            jump_penalty = 0.20
        health = 0.12 + 0.28 * level_score + 0.35 * spread_score + 0.25 * depth_score
        return clamp(health - thin_touch_penalty - jump_penalty, 0.0, 1.0)

    def _update_state(self, book: Book, memory: dict, timestamp: int) -> Tuple[dict, dict]:
        st = self._memory(memory)
        last_ts = int(st.get("last_ts", -1))
        if last_ts >= 0 and timestamp < last_ts:
            st = {}

        last_mid = st.get("last_mid")
        mid_source = book.mid if book.mid else self.ANCHOR
        mid_ema = ema(st.get("mid_ema"), mid_source, 0.08)

        if last_mid is None:
            var_ema = float(st.get("var_ema", 1.5))
        else:
            move = mid_source - float(last_mid)
            var_ema = ema(st.get("var_ema"), move * move, 0.10)
            var_ema = clamp(var_ema, 0.20, 30.0)

        # Very light markout state: it affects passive width only, not taking.
        pos = None
        try:
            pos = int(memory.get("ASH_LAST_POS", 0))
        except Exception:
            pos = 0
        st["last_mid"] = mid_source
        st["mid_ema"] = round(mid_ema, 6)
        st["var_ema"] = round(var_ema, 6)
        st["last_ts"] = int(timestamp)
        memory["ASH_LAST_POS"] = pos
        return st, memory

    def _fair_and_signals(self, state: TradingState, book: Book, st: dict) -> Tuple[float, float, float, float, float, float]:
        mid_ema = float(st.get("mid_ema", book.mid if book.mid else self.ANCHOR))
        last_good = st.get("last_good_fair")
        stable = book.stable_mid(3, 0.25) if book.valid else mid_ema
        health = self._book_health(book, float(last_good) if last_good is not None else None)

        if book.valid:
            depth = max(8.0, float(book.best_bid_vol + book.best_ask_vol))
            ofi = (30.0 / depth + 0.15) * book.imbalance
            micro_signal = 0.30 * (book.micro - book.mid)
            trade_signal = 0.25 * self._trade_pressure(state, book)
            fast = clamp(ofi + micro_signal + trade_signal, -2.25, 2.25)
        else:
            fast = 0.0

        robust_median = median3(self.ANCHOR, stable, mid_ema)
        high_health_fair = 0.38 * self.ANCHOR + 0.42 * stable + 0.20 * mid_ema + fast
        low_health_fair = 0.60 * robust_median + 0.25 * self.ANCHOR + 0.15 * mid_ema
        fair = health * high_health_fair + (1.0 - health) * low_health_fair

        # Keep fair bounded around anchor during degraded books.
        if health < 0.45:
            fair = clamp(fair, self.ANCHOR - 8.0, self.ANCHOR + 8.0)

        if book.valid and health > 0.35:
            st["last_good_fair"] = round(fair, 6)

        alpha = 0.0
        if book.valid:
            alpha = fair - book.mid
        sigma = math.sqrt(max(0.20, float(st.get("var_ema", 1.5))))
        return fair, alpha, fast, sigma, health, stable

    def _dynamic_quote(self, fair: float, alpha: float, sigma: float, health: float, pos: int, timestamp: int) -> Tuple[float, float, float]:
        inv_ratio = pos / float(self.LIMIT)

        # Avellaneda-Stoikov inspired reservation price:
        # r = S - q * gamma * sigma^2 * horizon, scaled to game ticks.
        progress = clamp(timestamp / 999900.0, 0.0, 1.0)
        horizon = max(0.08, 1.0 - progress)
        gamma = 0.020 + 0.035 * abs(inv_ratio) + 0.020 * (1.0 - health)
        reservation = fair - pos * gamma * max(0.6, sigma) * horizon

        # Arrival intensity proxy: tighter/deeper books -> lower required edge.
        k = 0.85 + 1.65 * health
        as_half = (1.0 / k) + gamma * sigma * sigma * horizon + 1.35 * (1.0 - health)
        half_spread = clamp(as_half + 0.35, 1.65, 5.75)

        # Alpha skews the reservation rather than lowering both sides equally.
        reservation += clamp(alpha * 0.25, -1.25, 1.25)
        return reservation, half_spread, gamma

    def _take_impulses(self, book: Book, mgr: OrderManager, fair: float, alpha: float, sigma: float, health: float) -> None:
        if not book.valid or health < 0.35:
            return
        pos = mgr.projected()
        inv_ratio = abs(pos) / float(self.LIMIT)
        risk_add = 0.30 * inv_ratio + 0.20 * max(0.0, sigma - 1.4)
        base_need = 1.25 + 0.70 * (1.0 - health) + risk_add

        # Market-taking theory: impulse trade only when expected edge clears
        # slippage + adverse-selection buffer. Sweep multiple levels if still valid.
        for level_idx, (ask, vol) in enumerate(book.sell_levels[:3]):
            edge = fair - ask
            need = base_need + 0.35 * level_idx
            if edge < need:
                break
            edge_score = clamp((edge - need) / 3.0, 0.0, 1.0)
            qty = int(round(3 + 7 * edge_score + 3 * health))
            if pos > 55:
                qty = max(0, qty - 4)
            if qty <= 0:
                break
            mgr.buy(ask, min(vol, qty))
            pos = mgr.projected()
            if pos >= self.LIMIT - 4:
                break

        pos = mgr.projected()
        for level_idx, (bid, vol) in enumerate(book.buy_levels[:3]):
            edge = bid - fair
            need = base_need + 0.35 * level_idx
            if edge < need:
                break
            edge_score = clamp((edge - need) / 3.0, 0.0, 1.0)
            qty = int(round(3 + 7 * edge_score + 3 * health))
            if pos < -55:
                qty = max(0, qty - 4)
            if qty <= 0:
                break
            mgr.sell(bid, min(vol, qty))
            pos = mgr.projected()
            if pos <= -self.LIMIT + 4:
                break

    def build_orders(self, state: TradingState, memory: dict) -> Tuple[List[Order], dict]:
        book = Book(state.order_depths.get(ASH))
        position = int(state.position.get(ASH, 0))
        mgr = OrderManager(ASH, position, self.LIMIT)
        timestamp = int(getattr(state, "timestamp", 0))

        st, memory = self._update_state(book, memory, timestamp)
        fair, alpha, fast, sigma, health, stable = self._fair_and_signals(state, book, st)

        # One-sided/vacuum books: tiny fair-repair only. This is intentionally
        # conservative because quote thinning makes one-sided books unreliable.
        if not book.valid:
            last_good = float(st.get("last_good_fair", fair))
            visible = book.best_bid if book.has_bid else book.best_ask if book.has_ask else int(round(last_good))
            if book.has_ask and visible < last_good - 2.5 and mgr.buy_cap > 0:
                mgr.buy(int(visible), min(2, book.best_ask_vol))
            if book.has_bid and visible > last_good + 2.5 and mgr.sell_cap > 0:
                mgr.sell(int(visible), min(2, book.best_bid_vol))
            return mgr.orders, self._save(memory, st)

        self._take_impulses(book, mgr, fair, alpha, sigma, health)

        pos = mgr.projected()
        reservation, half_spread, gamma = self._dynamic_quote(fair, alpha, sigma, health, pos, timestamp)

        # Passive adverse-selection / markout proxy. We do not shut the engine down;
        # we just require a bit more edge in weaker-health books.
        bid_half = half_spread + (0.35 if health < 0.55 else 0.0)
        ask_half = half_spread + (0.35 if health < 0.55 else 0.0)

        # Inventory skew: if long, make ask more attractive and bid less attractive.
        if pos > 45:
            bid_half += 0.80
            ask_half -= 0.35
        elif pos < -45:
            bid_half -= 0.35
            ask_half += 0.80

        # Alpha-side priority: quote one tick more aggressively on signal side.
        if alpha > 0.80 and health > 0.50 and pos < 55:
            bid_half -= 0.35
            ask_half += 0.20
        elif alpha < -0.80 and health > 0.50 and pos > -55:
            ask_half -= 0.35
            bid_half += 0.20

        bid_half = max(1.65, bid_half)
        ask_half = max(1.65, ask_half)
        bid_px = int(round(reservation - bid_half))
        ask_px = int(round(reservation + ask_half))

        # Join/improve logic from a fill-intensity view: improve only if book is healthy.
        if health > 0.70:
            if bid_px <= book.best_bid and reservation - book.best_bid >= bid_half - 0.15:
                bid_px = book.best_bid + 1 if book.best_bid + 1 < book.best_ask else book.best_bid
            if ask_px >= book.best_ask and book.best_ask - reservation >= bid_half - 0.15:
                ask_px = book.best_ask - 1 if book.best_ask - 1 > book.best_bid else book.best_ask
        elif health < 0.45:
            # Do not compete at the touch in low-quality books.
            bid_px = min(bid_px, book.best_bid)
            ask_px = max(ask_px, book.best_ask)

        bid_px = min(bid_px, book.best_ask - 1)
        ask_px = max(ask_px, book.best_bid + 1)
        back_bid = min(bid_px - 2, book.best_ask - 1)
        back_ask = max(ask_px + 2, book.best_bid + 1)

        base_front = int(round(8 + 10 * health))
        base_back = int(round(3 + 4 * health))
        if abs(pos) > 55:
            base_front = max(3, base_front - 4)
            base_back = max(1, base_back - 2)

        if pos < self.LIMIT - 8 and bid_px > 0 and bid_px < book.best_ask:
            mgr.buy(bid_px, base_front)
            if back_bid > 0 and back_bid < book.best_ask and health > 0.45:
                mgr.buy(back_bid, base_back)
        if pos > -self.LIMIT + 8 and ask_px > book.best_bid:
            mgr.sell(ask_px, base_front)
            if back_ask > book.best_bid and health > 0.45:
                mgr.sell(back_ask, base_back)

        return mgr.orders, self._save(memory, st)


class PepperScheduleTrader:
    """Different Pepper engine: schedule/catch-up optimal execution.

    Instead of treating Pepper as a generic market maker, this explicitly targets
    a time schedule toward max long and only sells when late/rich or badly over
    target. It is intentionally simple and asymmetric.
    """

    LIMIT = PRODUCT_LIMITS[PEPPER]
    DRIFT = 0.0026009226

    def _memory(self, memory: dict) -> dict:
        state = memory.get("PEPPER_SCHED_STATE", {})
        return state if isinstance(state, dict) else {}

    def _save(self, memory: dict, state: dict) -> dict:
        memory["PEPPER_SCHED_STATE"] = state
        return memory

    def build_orders(self, state: TradingState, memory: dict) -> Tuple[List[Order], dict]:
        book = Book(state.order_depths.get(PEPPER))
        position = int(state.position.get(PEPPER, 0))
        mgr = OrderManager(PEPPER, position, self.LIMIT)
        timestamp = int(getattr(state, "timestamp", 0))
        st = self._memory(memory)
        last_ts = int(st.get("last_ts", -1))
        if last_ts >= 0 and timestamp < last_ts:
            st = {}

        if not book.has_bid and not book.has_ask:
            return [], self._save(memory, st)

        if "anchor" not in st:
            start_mid = book.mid if book.mid else (book.best_bid if book.has_bid else book.best_ask)
            st["anchor"] = round(float(start_mid) / 1000.0) * 1000.0
            st["res_ema"] = 0.0
            st["spread_ema"] = book.spread if book.spread else 15.0

        anchor = float(st["anchor"])
        trend = anchor + self.DRIFT * timestamp
        mid = book.mid if book.mid else trend
        spread = book.spread if book.valid else float(st.get("spread_ema", 15.0))
        st["spread_ema"] = ema(st.get("spread_ema"), spread, 0.08)
        residual = mid - trend
        st["res_ema"] = ema(st.get("res_ema"), residual, 0.12)
        res_ema = float(st["res_ema"])
        spread_scale = max(4.0, float(st["spread_ema"]) * 0.45)
        z = residual / spread_scale

        # Fast schedule to max long. Uses timestamp directly, so it works for both
        # short public-style and long hidden-style days.
        schedule = 80.0 * (1.0 - math.exp(-max(0, timestamp) / 14000.0))
        if timestamp < 5000:
            schedule = max(schedule, 32.0)
        if timestamp > 22000:
            schedule = max(schedule, 74.0)

        # Do not chase very rich residuals; catch up harder on dips.
        target = schedule
        if z < -0.40:
            target += min(8.0, abs(z) * 5.0)
        if z > 0.90:
            target -= min(10.0, (z - 0.90) * 6.0)
        target = int(clamp(target, 0, 80))

        # Execution fair: trend plus modest lookahead, but with anti-chase damping.
        lookahead = 4.5 * max(0.25, 1.0 - timestamp / 999900.0)
        fair = 0.70 * trend + 0.15 * mid + 0.10 * book.micro + 0.05 * (trend + res_ema) + lookahead
        if z > 1.1:
            fair -= min(3.0, (z - 1.1) * 1.5)

        # One-sided books: only buy cheap asks or sell absurd bids.
        if not book.valid:
            if book.has_ask and book.best_ask <= fair - 2.0 and mgr.buy_cap > 0:
                mgr.buy(book.best_ask, min(book.best_ask_vol, 4, max(0, target + 8 - mgr.projected())))
            if book.has_bid and book.best_bid >= fair + 5.5 and mgr.sell_cap > 0 and mgr.projected() > target + 8:
                mgr.sell(book.best_bid, min(book.best_bid_vol, 3, max(0, mgr.projected() - target)))
            st["last_ts"] = timestamp
            return mgr.orders, self._save(memory, st)

        pos = mgr.projected()
        behind = max(0, target - pos)
        ahead = max(0, pos - target)

        # Market-taking: buy if behind schedule and not chasing a rich spike.
        buy_need = 2.25 + 0.35 * max(0.0, z)
        if behind > 20:
            buy_need -= 0.50
        if z < -0.35:
            buy_need -= 0.35
        buy_need = max(0.75, buy_need)

        if behind > 0 and fair - book.best_ask >= buy_need:
            qty = min(book.best_ask_vol, 18, behind + 8)
            mgr.buy(book.best_ask, qty)

        # Sells are rare: late/rich or strongly ahead of target.
        pos = mgr.projected()
        sell_need = 4.25
        late = timestamp > 850000
        rich = z > 1.25
        if (late and rich) or pos > target + 14:
            if book.best_bid - fair >= sell_need or pos > target + 18:
                qty = min(book.best_bid_vol, 8, max(0, pos - target + 2))
                mgr.sell(book.best_bid, qty)

        # Passive schedule ladder. It is one-sided while behind; very conservative asks.
        pos = mgr.projected()
        reservation = fair - 0.075 * (pos - target)
        buy_edge = 3.4 - (0.55 if pos < target else 0.0) - (0.25 if z < -0.45 else 0.0)
        sell_edge = 6.0 + (0.75 if pos < target else 0.0)

        front_buy = min(math.floor(reservation - buy_edge), book.best_ask - 1)
        back_buy = min(front_buy - 2, book.best_ask - 1)
        front_sell = max(math.ceil(reservation + sell_edge), book.best_bid + 1)
        back_sell = max(front_sell + 2, book.best_bid + 1)

        buy_cap_target = min(80, target + 16)
        if front_buy > 0 and pos < buy_cap_target:
            mgr.buy(front_buy, min(12, max(0, buy_cap_target - pos)))
            pos = mgr.projected()
            if back_buy > 0 and pos < buy_cap_target:
                mgr.buy(back_buy, min(6, max(0, buy_cap_target - pos)))

        # Small ask ladder only if not behind or very rich.
        pos = mgr.projected()
        if (pos > target + 4 or (z > 1.20 and pos > 30)) and front_sell > book.best_bid:
            mgr.sell(front_sell, min(5, max(0, pos - target + 4)))
            pos = mgr.projected()
            if back_sell > book.best_bid and pos > target + 8:
                mgr.sell(back_sell, min(3, max(0, pos - target)))

        st["last_ts"] = timestamp
        return mgr.orders, self._save(memory, st)


class Trader:
    def __init__(self) -> None:
        self.ash = AshASController()
        self.pepper = PepperScheduleTrader()

    def bid(self):
        return ROUND2_MAF_BID

    def _load_memory(self, trader_data: str) -> dict:
        if not trader_data:
            return {}
        try:
            parsed = json.loads(trader_data)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}

    def run(self, state: TradingState):
        memory = self._load_memory(state.traderData if hasattr(state, "traderData") else "")
        result: Dict[str, List[Order]] = {}

        if ASH in state.order_depths:
            ash_orders, memory = self.ash.build_orders(state, memory)
            result[ASH] = ash_orders

        if PEPPER in state.order_depths:
            pepper_orders, memory = self.pepper.build_orders(state, memory)
            result[PEPPER] = pepper_orders

        trader_data = json.dumps(memory, separators=(",", ":"))
        return result, 0, trader_data
