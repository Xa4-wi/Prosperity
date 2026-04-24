from __future__ import annotations

import json
import math
from statistics import NormalDist
from typing import Dict, List, Optional, Sequence, Tuple

try:
    from datamodel import Order, OrderDepth, Trade, TradingState
except ModuleNotFoundError:
    from trader_factory.core.datamodel import Order, OrderDepth, Trade, TradingState


_N = NormalDist()

HYDROGEL = "HYDROGEL_PACK"
VELVET = "VELVETFRUIT_EXTRACT"
VOUCHER_STRIKES: Dict[str, int] = {
    "VEV_4000": 4000,
    "VEV_4500": 4500,
    "VEV_5000": 5000,
    "VEV_5100": 5100,
    "VEV_5200": 5200,
    "VEV_5300": 5300,
    "VEV_5400": 5400,
    "VEV_5500": 5500,
    "VEV_6000": 6000,
    "VEV_6500": 6500,
}

LIMITS: Dict[str, int] = {
    HYDROGEL: 200,
    VELVET: 200,
    **{product: 300 for product in VOUCHER_STRIKES},
}

TTE_YEARS = 5.0 / 365.0

HYDROGEL_CFG = {
    "anchor": 10000.0,
    "anchor_w": 0.62,
    "stable_w": 0.25,
    "micro_w": 0.13,
    "imbalance_w": 1.00,
    "take_edge": 2.2,
    "quote_edge": 3.0,
    "clear_edge": 1.0,
    "soft_limit": 120,
    "take_max": 26,
    "clear_max": 40,
    "quote_size": 30,
    "inv_skew": 8.0,
}

VELVET_CFG = {
    "anchor": 5250.0,
    "anchor_w": 0.58,
    "stable_w": 0.26,
    "micro_w": 0.16,
    "imbalance_w": 0.75,
    "take_edge": 1.2,
    "quote_edge": 1.5,
    "clear_edge": 0.6,
    "soft_limit": 120,
    "take_max": 34,
    "clear_max": 50,
    "quote_size": 36,
    "inv_skew": 5.0,
}


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def load_memory(trader_data: str) -> dict:
    if not trader_data:
        return {}
    try:
        obj = json.loads(trader_data)
        return obj if isinstance(obj, dict) else {}
    except (json.JSONDecodeError, TypeError, ValueError):
        return {}


def dump_memory(memory: dict) -> str:
    return json.dumps(memory, separators=(",", ":"))


class OrderManager:
    def __init__(self, product: str, position: int, limit: int) -> None:
        self.product = product
        self.position = int(position)
        self.limit = int(limit)
        self.buy_cap = max(0, limit - position)
        self.sell_cap = max(0, limit + position)
        self._orders: List[Order] = []

    def projected(self) -> int:
        return self.position + sum(order.quantity for order in self._orders)

    def buy(self, price: int, qty: int) -> None:
        size = min(max(0, int(qty)), self.buy_cap)
        if size > 0:
            self._orders.append(Order(self.product, int(price), size))
            self.buy_cap -= size

    def sell(self, price: int, qty: int) -> None:
        size = min(max(0, int(qty)), self.sell_cap)
        if size > 0:
            self._orders.append(Order(self.product, int(price), -size))
            self.sell_cap -= size

    def flush(self) -> List[Order]:
        orders = self._orders
        self._orders = []
        return orders


def best_bid(od: OrderDepth) -> Optional[int]:
    return max(od.buy_orders) if od.buy_orders else None


def best_ask(od: OrderDepth) -> Optional[int]:
    return min(od.sell_orders) if od.sell_orders else None


def raw_mid(od: OrderDepth) -> Optional[float]:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None or ba is None or bb >= ba:
        return None
    return 0.5 * (bb + ba)


def top_bid_levels(od: OrderDepth, levels: int = 3) -> List[Tuple[int, int]]:
    return sorted(od.buy_orders.items(), reverse=True)[:levels]


def top_ask_levels(od: OrderDepth, levels: int = 3) -> List[Tuple[int, int]]:
    return sorted(od.sell_orders.items())[:levels]


def size_wall_prices(od: OrderDepth, levels: int = 3) -> Tuple[Optional[int], Optional[int]]:
    if not od.buy_orders or not od.sell_orders:
        return None, None
    bid_levels = top_bid_levels(od, levels)
    ask_levels = top_ask_levels(od, levels)
    # Use the largest visible queues near the touch as the "wall", not the outermost prices.
    bid_px = max(bid_levels, key=lambda x: (x[1], x[0]))[0]
    ask_px = min(ask_levels, key=lambda x: (x[1], x[0]))[0]
    return bid_px, ask_px


def wall_mid(od: OrderDepth) -> Optional[float]:
    bid_wall, ask_wall = size_wall_prices(od, levels=3)
    if bid_wall is None or ask_wall is None or bid_wall >= ask_wall:
        return raw_mid(od)
    return 0.5 * (bid_wall + ask_wall)


def thick_mid(od: OrderDepth, levels: int = 3) -> Optional[float]:
    if not od.buy_orders or not od.sell_orders:
        return raw_mid(od)
    bid_levels = top_bid_levels(od, levels)
    ask_levels = top_ask_levels(od, levels)
    bid_vol = sum(volume for _, volume in bid_levels)
    ask_vol = sum(abs(volume) for _, volume in ask_levels)
    if bid_vol <= 0 or ask_vol <= 0:
        return raw_mid(od)
    bid_px = sum(price * volume for price, volume in bid_levels) / bid_vol
    ask_px = sum(price * abs(volume) for price, volume in ask_levels) / ask_vol
    if bid_px >= ask_px:
        return raw_mid(od)
    return 0.5 * (bid_px + ask_px)


def micro_price(od: OrderDepth) -> Optional[float]:
    bb = best_bid(od)
    ba = best_ask(od)
    if bb is None or ba is None or bb >= ba:
        return raw_mid(od)
    bid_vol = od.buy_orders[bb]
    ask_vol = abs(od.sell_orders[ba])
    total = bid_vol + ask_vol
    if total <= 0:
        return raw_mid(od)
    return (ba * bid_vol + bb * ask_vol) / total


def book_imbalance(od: OrderDepth, levels: int = 2) -> float:
    if not od.buy_orders or not od.sell_orders:
        return 0.0
    bid_levels = top_bid_levels(od, levels)
    ask_levels = top_ask_levels(od, levels)
    bid_vol = sum(volume for _, volume in bid_levels)
    ask_vol = sum(abs(volume) for _, volume in ask_levels)
    total = bid_vol + ask_vol
    if total <= 0:
        return 0.0
    return (bid_vol - ask_vol) / total


def stable_mid(od: OrderDepth) -> Optional[float]:
    mids = [value for value in (wall_mid(od), thick_mid(od), raw_mid(od)) if value is not None]
    return sum(mids) / len(mids) if mids else None


def norm_cdf(x: float) -> float:
    return _N.cdf(x)


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def black_scholes_call(spot: float, strike: float, tte_years: float, sigma: float) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    if tte_years <= 0.0 or sigma <= 0.0:
        return max(spot - strike, 0.0)
    sqrt_t = math.sqrt(tte_years)
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * tte_years) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t
    return spot * norm_cdf(d1) - strike * norm_cdf(d2)


def black_scholes_delta_call(spot: float, strike: float, tte_years: float, sigma: float) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    if tte_years <= 0.0 or sigma <= 0.0:
        return 1.0 if spot > strike else 0.0
    sqrt_t = math.sqrt(tte_years)
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * tte_years) / (sigma * sqrt_t)
    return norm_cdf(d1)


def implied_vol_call(price: float, spot: float, strike: float, tte_years: float, iterations: int = 60) -> float:
    intrinsic = max(spot - strike, 0.0)
    if spot <= 0.0 or strike <= 0.0 or tte_years <= 0.0:
        return 1e-6
    if price <= intrinsic + 1e-6:
        return 1e-6

    lo, hi = 1e-6, 3.0
    for _ in range(iterations):
        mid = 0.5 * (lo + hi)
        fair = black_scholes_call(spot, strike, tte_years, mid)
        if fair < price:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def round_down(x: float) -> int:
    return math.floor(x)


def round_up(x: float) -> int:
    return math.ceil(x)


def solve_3x3(a: List[List[float]], b: List[float]) -> Optional[List[float]]:
    mat = [row[:] + [rhs] for row, rhs in zip(a, b)]
    n = 3
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(mat[r][col]))
        if abs(mat[pivot][col]) < 1e-12:
            return None
        if pivot != col:
            mat[col], mat[pivot] = mat[pivot], mat[col]
        factor = mat[col][col]
        for j in range(col, n + 1):
            mat[col][j] /= factor
        for row in range(n):
            if row == col:
                continue
            factor = mat[row][col]
            for j in range(col, n + 1):
                mat[row][j] -= factor * mat[col][j]
    return [mat[i][n] for i in range(n)]


def fit_quadratic(xs: Sequence[float], ys: Sequence[float]) -> Tuple[float, float, float]:
    if len(xs) != len(ys) or len(xs) < 3:
        median = sorted(ys)[len(ys) // 2] if ys else 0.18
        return (0.0, 0.0, float(median))

    s0 = float(len(xs))
    s1 = sum(xs)
    s2 = sum(x * x for x in xs)
    s3 = sum(x * x * x for x in xs)
    s4 = sum(x * x * x * x for x in xs)
    t0 = sum(ys)
    t1 = sum(x * y for x, y in zip(xs, ys))
    t2 = sum((x * x) * y for x, y in zip(xs, ys))

    sol = solve_3x3(
        [
            [s4, s3, s2],
            [s3, s2, s1],
            [s2, s1, s0],
        ],
        [t2, t1, t0],
    )
    if sol is None:
        median = sorted(ys)[len(ys) // 2]
        return (0.0, 0.0, float(median))
    return (float(sol[0]), float(sol[1]), float(sol[2]))


def polyval(coeffs: Tuple[float, float, float], x: float) -> float:
    a, b, c = coeffs
    return a * x * x + b * x + c


class AnchoredUnderlyingEngine:
    def __init__(self, product: str, cfg: dict) -> None:
        self.product = product
        self.cfg = cfg
        self.limit = LIMITS[product]

    def compute_fair(self, od: OrderDepth, overlay_bias: float = 0.0) -> float:
        cfg = self.cfg
        anchor = cfg["anchor"]
        stable = stable_mid(od)
        micro = micro_price(od)
        bb = best_bid(od)
        ba = best_ask(od)
        spread = (ba - bb) if bb is not None and ba is not None else 2.0

        stable_component = stable if stable is not None else anchor
        micro_component = micro if micro is not None else stable_component
        fair = (
            cfg["anchor_w"] * anchor
            + cfg["stable_w"] * stable_component
            + cfg["micro_w"] * micro_component
        )
        fair += cfg["imbalance_w"] * book_imbalance(od, levels=2) * max(1.0, 0.5 * spread)
        fair += overlay_bias
        return fair

    def trade(
        self,
        state: TradingState,
        fair: float,
        position_target: float = 0.0,
        take_bias: float = 0.0,
        quote_bias: float = 0.0,
        size_mult: float = 1.0,
    ) -> List[Order]:
        od = state.order_depths[self.product]
        cfg = self.cfg
        mgr = OrderManager(self.product, state.position.get(self.product, 0), self.limit)

        bb = best_bid(od)
        ba = best_ask(od)
        spread = (ba - bb) if bb is not None and ba is not None else 2.0

        # Take
        for ask, volume in sorted(od.sell_orders.items()):
            if (fair + take_bias) - ask >= cfg["take_edge"]:
                mgr.buy(ask, min(-volume, cfg["take_max"]))
            else:
                break

        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            if bid - (fair + take_bias) >= cfg["take_edge"]:
                mgr.sell(bid, min(volume, cfg["take_max"]))
            else:
                break

        # Clear
        pos = mgr.projected()
        relative_pos = pos - position_target
        if relative_pos > cfg["soft_limit"] and bb is not None and bb >= fair - cfg["clear_edge"]:
            mgr.sell(bb, min(int(math.ceil(relative_pos - cfg["soft_limit"])), cfg["clear_max"]))
        elif relative_pos < -cfg["soft_limit"] and ba is not None and ba <= fair + cfg["clear_edge"]:
            mgr.buy(ba, min(int(math.ceil((-cfg["soft_limit"]) - relative_pos)), cfg["clear_max"]))

        # Make
        pos = mgr.projected()
        relative_pos = pos - position_target
        inv_ratio = relative_pos / self.limit
        reservation = fair + quote_bias - cfg["inv_skew"] * inv_ratio
        quote_edge = cfg["quote_edge"] + max(0.0, 0.1 * (spread - 4.0))

        buy_px = round_down(reservation - quote_edge)
        sell_px = round_up(reservation + quote_edge)

        if bb is not None and ba is not None and bb < ba:
            if spread >= 3:
                buy_px = max(buy_px, bb + 1)
                sell_px = min(sell_px, ba - 1)
            else:
                buy_px = min(buy_px, bb)
                sell_px = max(sell_px, ba)
            buy_px = min(buy_px, ba - 1)
            sell_px = max(sell_px, bb + 1)

        size_scale = max(0.25, 1.0 - abs(inv_ratio)) * max(0.35, size_mult)
        quote_size = max(6, int(round(cfg["quote_size"] * size_scale)))

        if mgr.buy_cap > 0 and (ba is None or buy_px < ba):
            mgr.buy(buy_px, quote_size)
        if mgr.sell_cap > 0 and (bb is None or sell_px > bb):
            mgr.sell(sell_px, quote_size)

        return mgr.flush()


class HydrogelEngine(AnchoredUnderlyingEngine):
    def __init__(self) -> None:
        super().__init__(HYDROGEL, HYDROGEL_CFG)


class VelvetEngine(AnchoredUnderlyingEngine):
    def __init__(self) -> None:
        super().__init__(VELVET, VELVET_CFG)

    def reset_if_needed(self, memory: dict, timestamp: int) -> None:
        last_ts = memory.get("last_timestamp")
        if last_ts is not None and timestamp < last_ts:
            memory["velvet_engine"] = {
                "day_low": 10**18,
                "day_high": -(10**18),
                "signal": 0.0,
                "age": 999,
            }
        memory["last_timestamp"] = timestamp
        memory.setdefault(
            "velvet_engine",
            {
                "day_low": 10**18,
                "day_high": -(10**18),
                "signal": 0.0,
                "age": 999,
            },
        )

    def update_overlay(self, state: TradingState, memory: dict) -> float:
        overlay = memory["velvet_engine"]
        trades = sorted(state.market_trades.get(VELVET, []), key=lambda t: t.timestamp)
        saw_event = False

        for trade in trades:
            qty = abs(int(trade.quantity))
            price = float(trade.price)
            is_new_low = price < float(overlay["day_low"])
            is_new_high = price > float(overlay["day_high"])

            if is_new_low:
                overlay["day_low"] = price
            if is_new_high:
                overlay["day_high"] = price

            # Keep the anonymous-flow signal mild until stronger evidence appears.
            if 10 <= qty <= 11 and is_new_low:
                overlay["signal"] = min(1.5, float(overlay["signal"]) + 1.0)
                overlay["age"] = 0
                saw_event = True

        if not saw_event:
            overlay["age"] = int(overlay.get("age", 999)) + 1
            overlay["signal"] = float(overlay.get("signal", 0.0)) * 0.96

        return 0.75 * clamp(float(overlay.get("signal", 0.0)), 0.0, 1.0)

    def build_context(self, state: TradingState, memory: dict) -> Optional[dict]:
        if VELVET not in state.order_depths:
            return None
        od = state.order_depths[VELVET]
        overlay_bias = self.update_overlay(state, memory)
        fair = self.compute_fair(od, overlay_bias)
        stable = stable_mid(od)
        micro = micro_price(od)
        bb = best_bid(od)
        ba = best_ask(od)
        spread = (ba - bb) if bb is not None and ba is not None else 2.0
        stable_component = stable if stable is not None else self.cfg["anchor"]
        micro_component = micro if micro is not None else stable_component
        directional_signal = (
            overlay_bias
            + 0.35 * (fair - stable_component) / max(1.0, 0.5 * spread)
            + 0.15 * (micro_component - stable_component) / max(1.0, 0.5 * spread)
        )
        return {
            "fair": fair,
            "overlay_bias": overlay_bias,
            "stable_mid": stable_component,
            "micro_price": micro_component,
            "spread": spread,
            "directional_signal": clamp(directional_signal, -2.0, 2.0),
            "imbalance": book_imbalance(od, levels=2),
        }


class VoucherEngine:
    def __init__(self) -> None:
        self.limit = 300

    def build_surface(self, state: TradingState, velvet_ctx: dict) -> Dict[str, dict]:
        spot_fair = float(velvet_ctx["fair"])
        points_m: List[float] = []
        points_iv: List[float] = []

        for product, strike in VOUCHER_STRIKES.items():
            od = state.order_depths.get(product)
            if od is None:
                continue
            mid = raw_mid(od)
            if mid is None:
                stable = stable_mid(od)
                if stable is None:
                    continue
                mid = stable

            intrinsic = max(spot_fair - strike, 0.0)
            market_price = max(float(mid), intrinsic + 1e-3)
            iv = implied_vol_call(market_price, spot_fair, strike, TTE_YEARS)
            m = math.log(strike / spot_fair) / math.sqrt(TTE_YEARS)
            if 1e-6 < iv < 3.0:
                points_m.append(m)
                points_iv.append(iv)

        if len(points_iv) >= 3:
            coeffs = fit_quadratic(points_m, points_iv)
        elif points_iv:
            median = sorted(points_iv)[len(points_iv) // 2]
            coeffs = (0.0, 0.0, float(median))
        else:
            coeffs = (0.0, 0.0, 0.18)

        surface: Dict[str, dict] = {}
        for product, strike in VOUCHER_STRIKES.items():
            od = state.order_depths.get(product)
            market_mid = None
            if od is not None:
                market_mid = raw_mid(od)
                if market_mid is None:
                    market_mid = stable_mid(od)
            m = math.log(strike / spot_fair) / math.sqrt(TTE_YEARS)
            fair_iv = clamp(float(polyval(coeffs, m)), 1e-4, 3.0)
            fair = black_scholes_call(spot_fair, strike, TTE_YEARS, fair_iv)
            delta = black_scholes_delta_call(spot_fair, strike, TTE_YEARS, fair_iv)
            market_iv = implied_vol_call(max(float(market_mid or fair), max(spot_fair - strike, 0.0) + 1e-3), spot_fair, strike, TTE_YEARS)
            iv_residual = market_iv - fair_iv
            price_edge = fair - float(market_mid or fair)
            surface[product] = {
                "fair": fair,
                "sigma": fair_iv,
                "delta": delta,
                "moneyness": m,
                "market_mid": market_mid,
                "market_iv": market_iv,
                "iv_residual": iv_residual,
                "price_edge": price_edge,
            }
        return surface

    def build_portfolio_context(self, state: TradingState, surface: Dict[str, dict], velvet_ctx: dict) -> dict:
        residual_pairs = [
            (product, ctx["iv_residual"])
            for product, ctx in surface.items()
            if ctx.get("market_mid") is not None and ctx["market_mid"] > 0.5
        ]
        residual_values = [value for _, value in residual_pairs]
        resid_scale = max(0.03, sum(abs(value) for value in residual_values) / max(1, len(residual_values)))

        sorted_under = [product for product, _ in sorted(residual_pairs, key=lambda item: item[1])]
        sorted_over = [product for product, _ in sorted(residual_pairs, key=lambda item: item[1], reverse=True)]
        long_candidates = set(sorted_under[:3])
        short_candidates = set(sorted_over[:3])

        strip_delta = 0.0
        gross_delta = 0.0
        for product, ctx in surface.items():
            pos = float(state.position.get(product, 0))
            product_delta = pos * float(ctx["delta"])
            strip_delta += product_delta
            gross_delta += abs(product_delta)

        hedge_ratio = 0.45
        target_velvet_pos = int(round(clamp(-hedge_ratio * strip_delta, -120.0, 120.0)))
        delta_pressure = clamp(strip_delta / 180.0, -2.0, 2.0)

        return {
            "resid_scale": resid_scale,
            "long_candidates": long_candidates,
            "short_candidates": short_candidates,
            "strip_delta": strip_delta,
            "gross_delta": gross_delta,
            "delta_pressure": delta_pressure,
            "target_velvet_pos": target_velvet_pos,
            "spot_signal": float(velvet_ctx.get("directional_signal", 0.0)),
        }

    def trade_product(
        self,
        product: str,
        state: TradingState,
        voucher_ctx: dict,
        velvet_ctx: dict,
        portfolio_ctx: dict,
    ) -> List[Order]:
        od = state.order_depths[product]
        mgr = OrderManager(product, state.position.get(product, 0), self.limit)

        fair = float(voucher_ctx["fair"])
        delta = float(voucher_ctx["delta"])
        market_mid = float(voucher_ctx.get("market_mid") or fair)
        iv_residual = float(voucher_ctx.get("iv_residual", 0.0))
        price_edge = float(voucher_ctx.get("price_edge", fair - market_mid))
        bb = best_bid(od)
        ba = best_ask(od)
        spread = (ba - bb) if bb is not None and ba is not None else 2.0

        # Explicit link to Velvet and to the whole voucher strip.
        spot_signal = float(portfolio_ctx["spot_signal"])
        delta_pressure = float(portfolio_ctx["delta_pressure"])
        rv_score = clamp(-iv_residual / float(portfolio_ctx["resid_scale"]), -2.5, 2.5)
        linked_shift = 0.30 * delta * spot_signal - 0.22 * delta * delta_pressure
        target_position = 0.0
        if product in portfolio_ctx["long_candidates"] and rv_score > 0.25:
            target_position = 70.0 * min(1.5, rv_score)
        elif product in portfolio_ctx["short_candidates"] and rv_score < -0.25:
            target_position = -70.0 * min(1.5, -rv_score)

        buy_take_edge = max(0.55, max(0.85, 0.40 * spread) - max(0.0, 0.20 * rv_score) + max(0.0, 0.18 * delta * delta_pressure))
        sell_take_edge = max(0.55, max(0.85, 0.40 * spread) - max(0.0, -0.20 * rv_score) - min(0.0, 0.18 * delta * delta_pressure))
        clear_edge = max(0.35, 0.15 * spread)
        soft_limit = 180

        # Take
        for ask, volume in sorted(od.sell_orders.items()):
            if (fair + linked_shift) - ask >= buy_take_edge:
                mgr.buy(ask, min(-volume, 24))
            else:
                break

        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            if bid - (fair + linked_shift) >= sell_take_edge:
                mgr.sell(bid, min(volume, 24))
            else:
                break

        # Clear
        pos = mgr.projected()
        relative_pos = pos - target_position
        if relative_pos > soft_limit and bb is not None and bb >= fair - clear_edge:
            mgr.sell(bb, min(int(math.ceil(relative_pos - soft_limit)), 40))
        elif relative_pos < -soft_limit and ba is not None and ba <= fair + clear_edge:
            mgr.buy(ba, min(int(math.ceil((-soft_limit) - relative_pos)), 40))

        # Make
        pos = mgr.projected()
        relative_pos = pos - target_position
        inv_ratio = relative_pos / self.limit
        inv_penalty = (0.02 * max(25.0, fair) + 2.0) * inv_ratio
        reservation = fair + linked_shift - inv_penalty
        quote_edge = max(1.0, 0.45 * spread, 0.015 * max(20.0, fair))
        if abs(rv_score) < 0.35 and product not in portfolio_ctx["long_candidates"] and product not in portfolio_ctx["short_candidates"]:
            quote_edge += 0.35
        else:
            quote_edge = max(0.8, quote_edge - 0.20 * abs(rv_score))

        buy_px = round_down(reservation - quote_edge)
        sell_px = round_up(reservation + quote_edge)

        if bb is not None and ba is not None and bb < ba:
            if spread >= 3:
                buy_px = max(buy_px, bb + 1)
                sell_px = min(sell_px, ba - 1)
            else:
                buy_px = min(buy_px, bb)
                sell_px = max(sell_px, ba)
            buy_px = min(buy_px, ba - 1)
            sell_px = max(sell_px, bb + 1)

        size_scale = max(0.20, 1.0 - abs(inv_ratio))
        if abs(rv_score) < 0.35 and product not in portfolio_ctx["long_candidates"] and product not in portfolio_ctx["short_candidates"]:
            size_scale *= 0.55
        else:
            size_scale *= min(1.5, 0.9 + 0.20 * abs(rv_score))
        base_size = 10 if fair > 100.0 else 16
        quote_size = max(4, int(round(base_size * size_scale)))

        if fair >= 0.5:
            if mgr.buy_cap > 0 and (ba is None or buy_px < ba):
                mgr.buy(buy_px, quote_size)
            if mgr.sell_cap > 0 and (bb is None or sell_px > bb):
                mgr.sell(sell_px, quote_size)

        return mgr.flush()

    def trade_all(self, state: TradingState, velvet_ctx: dict, surface: Dict[str, dict], portfolio_ctx: dict) -> Dict[str, List[Order]]:
        result: Dict[str, List[Order]] = {}
        for product in VOUCHER_STRIKES:
            if product in state.order_depths:
                result[product] = self.trade_product(product, state, surface[product], velvet_ctx, portfolio_ctx)
        return result


class Trader:
    """
    Round 3 v3:
    - HydrogelEngine: anchored maker/taker for HYDROGEL_PACK
    - VelvetEngine: anchored maker/taker + small overlay for VELVETFRUIT_EXTRACT
    - VoucherEngine: option surface + portfolio-aware execution for all VEV_* products

    The voucher strip now has:
    - explicit smile residual ranking by strike
    - net strip delta accounting
    - a partial hedge target in VELVETFRUIT_EXTRACT
    - engine isolation in run() so one failure does not kill the whole tick
    """

    def __init__(self) -> None:
        self.hydrogel_engine = HydrogelEngine()
        self.velvet_engine = VelvetEngine()
        self.voucher_engine = VoucherEngine()

    def bid(self) -> int:
        return 0

    def run(self, state: TradingState):
        memory = load_memory(state.traderData)
        memory.setdefault("engine_errors", {})

        try:
            self.velvet_engine.reset_if_needed(memory, state.timestamp)
        except Exception as exc:
            memory["engine_errors"]["velvet_reset"] = type(exc).__name__

        result: Dict[str, List[Order]] = {}
        conversions = 0

        if HYDROGEL in state.order_depths:
            try:
                hydro_fair = self.hydrogel_engine.compute_fair(state.order_depths[HYDROGEL], 0.0)
                result[HYDROGEL] = self.hydrogel_engine.trade(state, hydro_fair)
            except Exception as exc:
                memory["engine_errors"]["hydrogel"] = type(exc).__name__

        velvet_ctx = None
        try:
            velvet_ctx = self.velvet_engine.build_context(state, memory)
        except Exception as exc:
            memory["engine_errors"]["velvet_context"] = type(exc).__name__

        if velvet_ctx is not None:
            surface = None
            portfolio_ctx = None
            try:
                surface = self.voucher_engine.build_surface(state, velvet_ctx)
                portfolio_ctx = self.voucher_engine.build_portfolio_context(state, surface, velvet_ctx)
            except Exception as exc:
                memory["engine_errors"]["voucher_context"] = type(exc).__name__

            try:
                velvet_target = float(portfolio_ctx["target_velvet_pos"]) if portfolio_ctx is not None else 0.0
                velvet_quote_bias = -0.20 * float(portfolio_ctx["delta_pressure"]) if portfolio_ctx is not None else 0.0
                result[VELVET] = self.velvet_engine.trade(
                    state,
                    float(velvet_ctx["fair"]),
                    position_target=velvet_target,
                    quote_bias=velvet_quote_bias,
                )
            except Exception as exc:
                memory["engine_errors"]["velvet_trade"] = type(exc).__name__

            if surface is not None and portfolio_ctx is not None:
                try:
                    result.update(self.voucher_engine.trade_all(state, velvet_ctx, surface, portfolio_ctx))
                except Exception as exc:
                    memory["engine_errors"]["voucher_trade"] = type(exc).__name__

        return result, conversions, dump_memory(memory)
