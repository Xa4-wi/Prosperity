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

# Round 3 starts with 5 days to expiry.
TTE_YEARS = 5.0 / 365.0

UNDERLYING_CFG = {
    HYDROGEL: {
        "anchor": 10000.0,
        "anchor_w": 0.54,
        "stable_w": 0.29,
        "micro_w": 0.17,
        "imbalance_w": 1.05,
        "take_edge": 2.2,
        "quote_edge": 3.0,
        "clear_edge": 1.0,
        "soft_limit": 100,
        "take_max": 22,
        "clear_max": 36,
        "quote_size": 24,
        "inv_skew": 8.0,
    },
    VELVET: {
        "anchor": 5250.0,
        "anchor_w": 0.46,
        "stable_w": 0.34,
        "micro_w": 0.20,
        "imbalance_w": 0.85,
        "take_edge": 1.2,
        "quote_edge": 1.5,
        "clear_edge": 0.6,
        "soft_limit": 120,
        "take_max": 34,
        "clear_max": 50,
        "quote_size": 36,
        "inv_skew": 5.0,
    },
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


def black_scholes_vega_proxy(spot: float, strike: float, tte_years: float, sigma: float) -> float:
    if spot <= 0.0 or strike <= 0.0 or tte_years <= 0.0 or sigma <= 0.0:
        return 0.0
    sqrt_t = math.sqrt(tte_years)
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * tte_years) / (sigma * sqrt_t)
    return spot * norm_pdf(d1) * sqrt_t


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


def trade_mid(trade: Trade) -> float:
    return float(trade.price)


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


class Trader:
    """
    Round 3 v9:
    - Step 1: strict Take -> Clear -> Make on the two underlyings
    - Step 2: option surface from cross-sectional implied vols, not flat vol
    - Step 3: keep bot-overlay ideas small and stateful until proven stronger
    - Step 4: make strip exposure explicit before adding more alpha
    - Step 5: enforce hard strip limits around the dangerous middle strikes
    - Step 6: rebalance Hydrogel and Velvet fair construction toward the
      Phase 1 classification of anchored local-fair market makers
    """

    def _reset_day_if_needed(self, memory: dict, timestamp: int) -> None:
        last_ts = memory.get("last_timestamp")
        if last_ts is not None and timestamp < last_ts:
            memory["velvet_overlay"] = {
                "day_low": 10**18,
                "day_high": -(10**18),
                "signal": 0.0,
                "age": 999,
            }
        memory["last_timestamp"] = timestamp
        memory.setdefault(
            "velvet_overlay",
            {
                "day_low": 10**18,
                "day_high": -(10**18),
                "signal": 0.0,
                "age": 999,
            },
        )

    def _update_velvet_overlay(self, state: TradingState, memory: dict) -> float:
        overlay = memory["velvet_overlay"]
        trades = sorted(state.market_trades.get(VELVET, []), key=lambda t: t.timestamp)
        saw_event = False

        for trade in trades:
            qty = abs(int(trade.quantity))
            price = trade_mid(trade)
            is_new_low = price < float(overlay["day_low"])
            is_new_high = price > float(overlay["day_high"])

            if is_new_low:
                overlay["day_low"] = price
            if is_new_high:
                overlay["day_high"] = price

            # The detector found only a weak useful bias here, so keep it small.
            if 10 <= qty <= 11 and is_new_low:
                overlay["signal"] = min(1.5, float(overlay["signal"]) + 1.0)
                overlay["age"] = 0
                saw_event = True

        if not saw_event:
            overlay["age"] = int(overlay.get("age", 999)) + 1
            overlay["signal"] = float(overlay.get("signal", 0.0)) * 0.96

        # Convert the anonymous-flow hint into a small fair shift only.
        return 0.75 * max(0.0, min(1.0, float(overlay["signal"])))

    def _underlying_fair(self, product: str, od: OrderDepth, overlay_bias: float = 0.0) -> float:
        cfg = UNDERLYING_CFG[product]
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

    def _trade_underlying(
        self,
        product: str,
        state: TradingState,
        fair: float,
        position_target: float = 0.0,
        take_bias: float = 0.0,
        quote_bias: float = 0.0,
        size_mult: float = 1.0,
    ) -> List[Order]:
        od = state.order_depths[product]
        cfg = UNDERLYING_CFG[product]
        limit = LIMITS[product]
        mgr = OrderManager(product, state.position.get(product, 0), limit)

        bb = best_bid(od)
        ba = best_ask(od)
        spread = (ba - bb) if bb is not None and ba is not None else 2.0

        # Step 1: Take
        for ask, volume in sorted(od.sell_orders.items()):
            edge = (fair + take_bias) - ask
            if edge >= cfg["take_edge"]:
                mgr.buy(ask, min(-volume, cfg["take_max"]))
            else:
                break

        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            edge = bid - (fair + take_bias)
            if edge >= cfg["take_edge"]:
                mgr.sell(bid, min(volume, cfg["take_max"]))
            else:
                break

        # Step 2: Clear
        pos = mgr.projected()
        relative_pos = pos - position_target
        if relative_pos > cfg["soft_limit"] and bb is not None and bb >= fair - cfg["clear_edge"]:
            mgr.sell(bb, min(int(math.ceil(relative_pos - cfg["soft_limit"])), cfg["clear_max"]))
        elif relative_pos < -cfg["soft_limit"] and ba is not None and ba <= fair + cfg["clear_edge"]:
            mgr.buy(ba, min(int(math.ceil((-cfg["soft_limit"]) - relative_pos)), cfg["clear_max"]))

        # Step 3: Make
        pos = mgr.projected()
        relative_pos = pos - position_target
        inv_ratio = relative_pos / limit
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

    def _build_voucher_surface(self, state: TradingState, velvet_fair: float) -> Dict[str, dict]:
        points_m = []
        points_iv = []
        raw_points: List[Tuple[str, float, float, float]] = []

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

            intrinsic = max(velvet_fair - strike, 0.0)
            market_price = max(float(mid), intrinsic + 1e-3)
            iv = implied_vol_call(market_price, velvet_fair, strike, TTE_YEARS)
            m = math.log(strike / velvet_fair) / math.sqrt(TTE_YEARS)
            if 1e-6 < iv < 3.0:
                raw_points.append((product, m, iv, market_price))

        if raw_points:
            sorted_ivs = sorted(iv for _, _, iv, _ in raw_points)
            median_iv = sorted_ivs[len(sorted_ivs) // 2]
            for _, m, iv, _ in raw_points:
                points_m.append(m)
                points_iv.append(clamp(iv, median_iv - 0.35, median_iv + 0.35))

        if len(points_iv) >= 3:
            coeffs = fit_quadratic(points_m, points_iv)
        elif points_iv:
            median = sorted(points_iv)[len(points_iv) // 2]
            coeffs = (0.0, 0.0, float(median))
        else:
            coeffs = (0.0, 0.0, 0.18)

        surface: Dict[str, dict] = {}
        provisional_prices: List[Tuple[str, int, float]] = []
        for product, strike in VOUCHER_STRIKES.items():
            od = state.order_depths.get(product)
            market_mid = None
            liquidity = 0.0
            spread = 3.0
            if od is not None:
                market_mid = raw_mid(od)
                if market_mid is None:
                    market_mid = stable_mid(od)
                bb = best_bid(od)
                ba = best_ask(od)
                if bb is not None and ba is not None:
                    spread = max(1.0, float(ba - bb))
                    liquidity = float(max(0, od.buy_orders.get(bb, 0)) + abs(od.sell_orders.get(ba, 0)))
            m = math.log(strike / velvet_fair) / math.sqrt(TTE_YEARS)
            sigma = float(polyval(coeffs, m))
            sigma = min(3.0, max(1e-4, sigma))
            surface[product] = {
                "sigma": sigma,
                "delta": black_scholes_delta_call(velvet_fair, strike, TTE_YEARS, sigma),
                "vega_proxy": black_scholes_vega_proxy(velvet_fair, strike, TTE_YEARS, sigma),
                "moneyness": m,
                "market_mid": market_mid,
                "spread": spread,
                "liquidity": liquidity,
            }
            provisional_prices.append((product, strike, black_scholes_call(velvet_fair, strike, TTE_YEARS, sigma)))

        prev_price = float("inf")
        for product, _, fair_price in sorted(provisional_prices, key=lambda item: item[1]):
            fair_price = min(prev_price, fair_price)
            prev_price = fair_price
            surface[product]["fair"] = fair_price
            market_mid = float(surface[product]["market_mid"] or fair_price)
            market_mid = max(market_mid, max(velvet_fair - VOUCHER_STRIKES[product], 0.0) + 1e-3)
            market_iv = implied_vol_call(market_mid, velvet_fair, VOUCHER_STRIKES[product], TTE_YEARS)
            surface[product]["market_iv"] = market_iv
            surface[product]["iv_residual"] = market_iv - float(surface[product]["sigma"])
        return surface

    def _build_voucher_risk_context(self, state: TradingState, surface: Dict[str, dict]) -> dict:
        liquid_products = [
            product
            for product, ctx in surface.items()
            if ctx.get("market_mid") is not None and float(ctx["market_mid"]) > 0.5 and float(ctx["liquidity"]) >= 10.0
        ]
        residual_pairs = [(product, float(surface[product]["iv_residual"])) for product in liquid_products]
        resid_scale = max(0.04, sum(abs(resid) for _, resid in residual_pairs) / max(1, len(residual_pairs)))

        pair_bias: Dict[str, int] = {}
        residual_rank: Dict[str, int] = {}
        sorted_products = sorted(VOUCHER_STRIKES, key=VOUCHER_STRIKES.get)
        sorted_residuals = sorted(liquid_products, key=lambda product: float(surface[product]["iv_residual"]))
        for rank, product in enumerate(sorted_residuals):
            centered_rank = rank - (len(sorted_residuals) - 1) / 2.0
            residual_rank[product] = int(round(centered_rank))

        for left, right in zip(sorted_products, sorted_products[1:]):
            left_ctx = surface[left]
            right_ctx = surface[right]
            if left not in liquid_products or right not in liquid_products:
                continue
            gap = float(right_ctx["iv_residual"]) - float(left_ctx["iv_residual"])
            if gap >= 0.07:
                pair_bias[left] = pair_bias.get(left, 0) + 1
                pair_bias[right] = pair_bias.get(right, 0) - 1
            elif gap <= -0.07:
                pair_bias[left] = pair_bias.get(left, 0) - 1
                pair_bias[right] = pair_bias.get(right, 0) + 1

        strip_delta = 0.0
        strip_vega = 0.0
        middle_abs = 0
        middle_net = 0
        low_wing_net = 0
        high_wing_net = 0
        adjacent_same_side_max = 0
        adjacent_same_side_products: List[str] = []
        positions = {product: int(state.position.get(product, 0)) for product in VOUCHER_STRIKES}

        for product, ctx in surface.items():
            pos = positions[product]
            delta = float(ctx["delta"])
            strip_delta += pos * delta
            strip_vega += pos * float(ctx["vega_proxy"])
            if 0.20 <= delta <= 0.80:
                middle_abs += abs(pos)
                middle_net += pos
            strike = VOUCHER_STRIKES[product]
            if strike <= 5000:
                low_wing_net += pos
            elif strike >= 5400:
                high_wing_net += pos

        for left, right in zip(sorted_products, sorted_products[1:]):
            left_pos = positions[left]
            right_pos = positions[right]
            if left_pos == 0 or right_pos == 0:
                continue
            if left_pos * right_pos > 0:
                concentration = abs(left_pos) + abs(right_pos)
                if concentration > adjacent_same_side_max:
                    adjacent_same_side_max = concentration
                    adjacent_same_side_products = [left, right]

        return {
            "resid_scale": resid_scale,
            "pair_bias": pair_bias,
            "residual_rank": residual_rank,
            "strip_delta": strip_delta,
            "strip_vega_proxy": strip_vega,
            "delta_pressure": clamp(strip_delta / 140.0, -2.0, 2.0),
            "target_velvet_pos": int(round(clamp(-0.50 * strip_delta, -100.0, 100.0))),
            "middle_abs": middle_abs,
            "middle_net": middle_net,
            "middle_cap": 150,
            "adjacent_same_side_max": adjacent_same_side_max,
            "adjacent_same_side_products": adjacent_same_side_products,
            "adjacent_cap": 140,
            "low_wing_net": low_wing_net,
            "high_wing_net": high_wing_net,
            "total_delta_cap": 115.0,
            "unconfirmed_outright_cap": 65,
        }

    def _trade_voucher(self, product: str, state: TradingState, voucher_ctx: dict, risk_ctx: dict) -> List[Order]:
        od = state.order_depths[product]
        limit = LIMITS[product]
        mgr = OrderManager(product, state.position.get(product, 0), limit)

        fair = float(voucher_ctx["fair"])
        delta = float(voucher_ctx["delta"])
        iv_residual = float(voucher_ctx["iv_residual"])
        residual_rank = int(risk_ctx["residual_rank"].get(product, 0))
        bb = best_bid(od)
        ba = best_ask(od)
        spread = (ba - bb) if bb is not None and ba is not None else 2.0

        middle_band = 0.20 <= delta <= 0.80
        pair_bias = int(clamp(float(risk_ctx["pair_bias"].get(product, 0)), -1.0, 1.0))
        confirmed = pair_bias != 0
        delta_over = abs(float(risk_ctx["strip_delta"])) > float(risk_ctx["total_delta_cap"])
        delta_block_buy = delta_over and float(risk_ctx["strip_delta"]) > 0.0
        delta_block_sell = delta_over and float(risk_ctx["strip_delta"]) < 0.0
        adjacent_block = (
            product in risk_ctx["adjacent_same_side_products"]
            and int(risk_ctx["adjacent_same_side_max"]) > int(risk_ctx["adjacent_cap"])
        )
        take_edge = max(0.75, 0.35 * spread) + (0.30 if middle_band else 0.0) + (0.20 if not confirmed else 0.0)
        clear_edge = max(0.35, 0.15 * spread)
        soft_limit = 80 if middle_band else 120
        per_strike_cap = 95 if not middle_band else 75
        take_max = 10 if middle_band else 18

        # Step 1: Take
        for ask, volume in sorted(od.sell_orders.items()):
            edge = fair - ask
            if pair_bias > 0:
                edge += 0.20
            if edge >= take_edge and not delta_block_buy and not (adjacent_block and pair_bias >= 0):
                mgr.buy(ask, min(-volume, take_max))
            else:
                break

        for bid, volume in sorted(od.buy_orders.items(), reverse=True):
            edge = bid - fair
            if pair_bias < 0:
                edge += 0.20
            if edge >= take_edge and not delta_block_sell and not (adjacent_block and pair_bias <= 0):
                mgr.sell(bid, min(volume, take_max))
            else:
                break

        # Step 2: Clear
        pos = mgr.projected()
        if pos > soft_limit and bb is not None and bb >= fair - clear_edge:
            mgr.sell(bb, min(pos - soft_limit, 50))
        elif pos < -soft_limit and ba is not None and ba <= fair + clear_edge:
            mgr.buy(ba, min((-soft_limit) - pos, 50))

        # Step 3: Make
        pos = mgr.projected()
        inv_ratio = pos / limit
        inv_penalty = (0.02 * max(25.0, fair) + 2.0) * inv_ratio
        reservation = fair - inv_penalty + 0.12 * pair_bias
        quote_edge = max(1.0, 0.45 * spread, 0.015 * max(20.0, fair))
        if middle_band:
            quote_edge += 0.40
        if not confirmed:
            quote_edge += 0.20
        if risk_ctx["middle_abs"] > risk_ctx["middle_cap"] and middle_band:
            quote_edge += 0.35
        if delta_over:
            quote_edge += 0.25
        if adjacent_block:
            quote_edge += 0.25

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
        if middle_band:
            size_scale *= 0.45
        if not confirmed:
            size_scale *= 0.75
        if abs(iv_residual) > 0.10:
            size_scale *= 0.85
        if delta_over:
            size_scale *= 0.65
        if adjacent_block:
            size_scale *= 0.65
        if abs(residual_rank) >= 3:
            size_scale *= 0.90
        base_size = 9 if fair > 100.0 else 14
        quote_size = max(4, int(round(base_size * size_scale)))

        if fair >= 0.5:
            can_bid = mgr.buy_cap > 0 and pos < per_strike_cap
            can_ask = mgr.sell_cap > 0 and pos > -per_strike_cap
            if middle_band and risk_ctx["middle_abs"] > risk_ctx["middle_cap"]:
                if risk_ctx["middle_net"] >= 0:
                    can_bid = False
                if risk_ctx["middle_net"] <= 0:
                    can_ask = False
            if not confirmed and pos >= risk_ctx["unconfirmed_outright_cap"]:
                can_bid = False
            if not confirmed and pos <= -risk_ctx["unconfirmed_outright_cap"]:
                can_ask = False
            if delta_block_buy:
                can_bid = False
            if delta_block_sell:
                can_ask = False
            if adjacent_block:
                if pos >= 0 and pair_bias >= 0:
                    can_bid = False
                if pos <= 0 and pair_bias <= 0:
                    can_ask = False

            if can_bid and (ba is None or buy_px < ba):
                mgr.buy(buy_px, quote_size)
            if can_ask and (bb is None or sell_px > bb):
                mgr.sell(sell_px, quote_size)

        return mgr.flush()

    def run(self, state: TradingState):
        memory = load_memory(state.traderData)
        memory.setdefault("engine_errors", {})
        try:
            self._reset_day_if_needed(memory, state.timestamp)
        except Exception as exc:
            memory["engine_errors"]["reset"] = type(exc).__name__

        result: Dict[str, List[Order]] = {}
        conversions = 0

        velvet_overlay_bias = 0.0
        try:
            velvet_overlay_bias = self._update_velvet_overlay(state, memory)
        except Exception as exc:
            memory["engine_errors"]["velvet_overlay"] = type(exc).__name__

        if HYDROGEL in state.order_depths:
            try:
                hydro_fair = self._underlying_fair(HYDROGEL, state.order_depths[HYDROGEL], 0.0)
                result[HYDROGEL] = self._trade_underlying(HYDROGEL, state, hydro_fair)
            except Exception as exc:
                memory["engine_errors"]["hydrogel"] = type(exc).__name__

        velvet_fair = None
        if VELVET in state.order_depths:
            try:
                velvet_fair = self._underlying_fair(VELVET, state.order_depths[VELVET], velvet_overlay_bias)
            except Exception as exc:
                memory["engine_errors"]["velvet_fair"] = type(exc).__name__

        if velvet_fair is not None:
            try:
                voucher_surface = self._build_voucher_surface(state, velvet_fair)
                risk_ctx = self._build_voucher_risk_context(state, voucher_surface)
                memory["strip_monitor"] = {
                    "strip_delta": round(float(risk_ctx["strip_delta"]), 3),
                    "strip_vega_proxy": round(float(risk_ctx["strip_vega_proxy"]), 3),
                    "target_velvet_pos": int(risk_ctx["target_velvet_pos"]),
                    "middle_abs": int(risk_ctx["middle_abs"]),
                    "middle_net": int(risk_ctx["middle_net"]),
                    "middle_cap": int(risk_ctx["middle_cap"]),
                    "adjacent_same_side_max": int(risk_ctx["adjacent_same_side_max"]),
                    "adjacent_cap": int(risk_ctx["adjacent_cap"]),
                    "adjacent_same_side_products": list(risk_ctx["adjacent_same_side_products"]),
                    "low_wing_net": int(risk_ctx["low_wing_net"]),
                    "high_wing_net": int(risk_ctx["high_wing_net"]),
                }
                result[VELVET] = self._trade_underlying(
                    VELVET,
                    state,
                    velvet_fair,
                    position_target=float(risk_ctx["target_velvet_pos"]),
                    quote_bias=-0.15 * float(risk_ctx["delta_pressure"]),
                )
                for product in VOUCHER_STRIKES:
                    if product in state.order_depths:
                        result[product] = self._trade_voucher(product, state, voucher_surface[product], risk_ctx)
            except Exception as exc:
                memory["engine_errors"]["voucher_strip"] = type(exc).__name__

        return result, conversions, dump_memory(memory)
