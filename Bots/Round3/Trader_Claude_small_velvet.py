from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict, Optional
import json
import math


POSITION_LIMITS: Dict[str, int] = {
    "VELVETFRUIT_EXTRACT": 90,
    "HYDROGEL_PACK": 50,
    "VEV_4000": 16,
    "VEV_4500": 16,
    "VEV_5000": 18,
    "VEV_5100": 18,
    "VEV_5200": 0,
    "VEV_5300": 0,
    "VEV_5400": 0,
    "VEV_5500": 0,
    "VEV_6000": 0,
    "VEV_6500": 0,
}

FAIR_VALUE: Dict[str, float] = {
    "VELVETFRUIT_EXTRACT": 5250.0,
    "HYDROGEL_PACK": 9990.0,
}

MM_HALF_SPREAD: Dict[str, float] = {
    "VELVETFRUIT_EXTRACT": 3.0,
    "HYDROGEL_PACK": 9.0,
    "VEV_4000": 10.0,
    "VEV_4500": 8.0,
    "VEV_5000": 4.0,
    "VEV_5100": 3.0,
}

TTE_YEARS = 5.0 / 365.0
VEV_STRIKES: Dict[str, int] = {f"VEV_{s}": s for s in [4000, 4500, 5000, 5100]}


def mid_price(order_depth: OrderDepth) -> Optional[float]:
    if not order_depth.buy_orders or not order_depth.sell_orders:
        return None
    best_bid = max(order_depth.buy_orders)
    best_ask = min(order_depth.sell_orders)
    if best_bid >= best_ask:
        return None
    return 0.5 * (best_bid + best_ask)


def stable_mid(order_depth: OrderDepth, levels: int = 2) -> Optional[float]:
    bids = sorted(order_depth.buy_orders.items(), reverse=True)[:levels]
    asks = sorted(order_depth.sell_orders.items())[:levels]
    if not bids or not asks:
        return mid_price(order_depth)
    bid_notional = sum(price * max(0, volume) for price, volume in bids)
    ask_notional = sum(price * abs(min(0, volume)) for price, volume in asks)
    bid_size = sum(max(0, volume) for _, volume in bids)
    ask_size = sum(abs(min(0, volume)) for _, volume in asks)
    if bid_size <= 0 or ask_size <= 0:
        return mid_price(order_depth)
    return 0.5 * (bid_notional / bid_size + ask_notional / ask_size)


def micro_price(order_depth: OrderDepth) -> Optional[float]:
    best_bid = max(order_depth.buy_orders) if order_depth.buy_orders else None
    best_ask = min(order_depth.sell_orders) if order_depth.sell_orders else None
    if best_bid is None or best_ask is None or best_bid >= best_ask:
        return mid_price(order_depth)
    bid_vol = max(1, order_depth.buy_orders.get(best_bid, 0))
    ask_vol = max(1, abs(order_depth.sell_orders.get(best_ask, 0)))
    return (best_ask * bid_vol + best_bid * ask_vol) / float(bid_vol + ask_vol)


def book_imbalance(order_depth: OrderDepth, levels: int = 2) -> float:
    bids = sorted(order_depth.buy_orders.items(), reverse=True)[:levels]
    asks = sorted(order_depth.sell_orders.items())[:levels]
    bid_vol = sum(max(0, volume) for _, volume in bids)
    ask_vol = sum(abs(min(0, volume)) for _, volume in asks)
    total = bid_vol + ask_vol
    if total <= 0:
        return 0.0
    return (bid_vol - ask_vol) / total


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def black_scholes_call(spot: float, strike: float, tte_years: float, sigma: float) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    if tte_years <= 0.0 or sigma <= 0.0:
        return max(spot - strike, 0.0)
    sqrt_t = math.sqrt(tte_years)
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * tte_years) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t
    return spot * norm_cdf(d1) - strike * norm_cdf(d2)


def black_scholes_delta(spot: float, strike: float, tte_years: float, sigma: float) -> float:
    if spot <= 0.0 or strike <= 0.0:
        return 0.0
    if tte_years <= 0.0 or sigma <= 0.0:
        return 1.0 if spot > strike else 0.0
    sqrt_t = math.sqrt(tte_years)
    d1 = (math.log(spot / strike) + 0.5 * sigma * sigma * tte_years) / (sigma * sqrt_t)
    return norm_cdf(d1)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class Trader:
    ALPHA = 0.05

    def _load_state(self, trader_data: str) -> Dict:
        if trader_data:
            try:
                return json.loads(trader_data)
            except Exception:
                pass
        return {}

    def _save_state(self, state_dict: Dict) -> str:
        return json.dumps(state_dict)

    def _take_orders(
        self,
        product: str,
        order_depth: OrderDepth,
        fair: float,
        position: int,
        orders: List[Order],
    ) -> None:
        limit = POSITION_LIMITS.get(product, 0)
        if limit == 0:
            return

        for ask_price in sorted(order_depth.sell_orders.keys()):
            if ask_price >= fair:
                break
            ask_vol = -order_depth.sell_orders[ask_price]
            can_buy = limit - position
            if can_buy <= 0:
                break
            qty = min(ask_vol, can_buy)
            orders.append(Order(product, ask_price, qty))
            position += qty

        for bid_price in sorted(order_depth.buy_orders.keys(), reverse=True):
            if bid_price <= fair:
                break
            bid_vol = order_depth.buy_orders[bid_price]
            can_sell = limit + position
            if can_sell <= 0:
                break
            qty = min(bid_vol, can_sell)
            orders.append(Order(product, bid_price, -qty))
            position -= qty

    def _make_market(
        self,
        product: str,
        order_depth: OrderDepth,
        fair: float,
        position: int,
        orders: List[Order],
    ) -> None:
        limit = POSITION_LIMITS.get(product, 0)
        if limit == 0:
            return

        half = MM_HALF_SPREAD.get(product, 2.0)
        skew = -round((position / limit) * (half * 0.5))
        bid = round(fair - half + skew)
        ask = round(fair + half + skew)
        can_buy = limit - position
        can_sell = limit + position
        best_existing_bid = max(order_depth.buy_orders) if order_depth.buy_orders else 0
        best_existing_ask = min(order_depth.sell_orders) if order_depth.sell_orders else 999999
        bid = min(bid, best_existing_bid + 1) if best_existing_bid > 0 else bid
        ask = max(ask, best_existing_ask - 1) if best_existing_ask < 999999 else ask
        if bid >= ask:
            ask = bid + 1
        mm_size = max(1, min(10, limit // 4))
        if can_buy > 0:
            orders.append(Order(product, bid, min(mm_size, can_buy)))
        if can_sell > 0:
            orders.append(Order(product, ask, -min(mm_size, can_sell)))

    def _build_velvet_context(self, order_depth: OrderDepth, saved: Dict, position: int) -> Dict[str, float]:
        mid = mid_price(order_depth)
        if mid is None:
            mid = stable_mid(order_depth)
        if mid is None:
            mid = FAIR_VALUE["VELVETFRUIT_EXTRACT"]
        stable = stable_mid(order_depth)
        if stable is None:
            stable = mid
        micro = micro_price(order_depth)
        if micro is None:
            micro = mid
        spread = 6.0
        if order_depth.buy_orders and order_depth.sell_orders:
            spread = max(1.0, min(order_depth.sell_orders) - max(order_depth.buy_orders))
        imbalance = book_imbalance(order_depth)
        prev_mid = saved.get("last_mid")
        ret = 0.0 if prev_mid is None else float(mid) - float(prev_mid)
        saved["last_mid"] = float(mid)
        saved["ema_mid"] = float(mid) if saved.get("ema_mid") is None else 0.16 * float(mid) + 0.84 * float(saved["ema_mid"])
        saved["ret_ema"] = 0.22 * ret + 0.78 * float(saved.get("ret_ema", 0.0))
        saved["vol_ema"] = 0.20 * abs(ret) + 0.80 * float(saved.get("vol_ema", 0.0))
        ema_mid = float(saved["ema_mid"])
        vol_ema = max(1.2, float(saved["vol_ema"]), 0.70 * spread)
        micro_gap = float(micro) - float(mid)
        z = (float(mid) - ema_mid) / vol_ema
        fair = float(mid) + 0.45 * micro_gap + 0.30 * imbalance * spread - 0.25 * z * vol_ema

        bull_peak = z > 1.45 and micro_gap <= 0.0 and float(saved["ret_ema"]) <= 0.2
        bear_trough = z < -1.45 and micro_gap >= 0.0 and float(saved["ret_ema"]) >= -0.2

        if bull_peak:
            target = -80.0
            bid_block = position >= -70
            ask_block = False
        elif bear_trough:
            target = 80.0
            bid_block = False
            ask_block = position <= 70
        else:
            target = -24.0 * math.tanh(0.90 * z)
            bid_block = False
            ask_block = False

        if abs(position) > 100:
            target = 0.0

        return {
            "fair": float(fair),
            "z": float(z),
            "vol_ema": float(vol_ema),
            "target": float(target),
            "take_bias": -0.10 * z + 0.06 * micro_gap,
            "quote_bias": -0.18 * z + 0.08 * micro_gap,
            "mode": "bull_peak" if bull_peak else "bear_trough" if bear_trough else "neutral",
            "bid_block": bid_block,
            "ask_block": ask_block,
        }

    def _trade_targeted(
        self,
        product: str,
        order_depth: OrderDepth,
        fair: float,
        position: int,
        target: float,
        take_edge: float,
        clear_edge: float,
        quote_edge: float,
        quote_size: int,
        take_max: int,
        soft_limit: int,
        inv_skew: float,
        take_bias: float = 0.0,
        quote_bias: float = 0.0,
        bid_block: bool = False,
        ask_block: bool = False,
    ) -> List[Order]:
        limit = POSITION_LIMITS.get(product, 0)
        orders: List[Order] = []
        if limit <= 0:
            return orders

        pos = int(position)
        target = clamp(float(target), -float(limit), float(limit))

        for ask_price in sorted(order_depth.sell_orders.keys()):
            if bid_block:
                break
            edge = fair - ask_price + take_bias
            if edge < take_edge:
                break
            ask_vol = -order_depth.sell_orders[ask_price]
            can_buy = limit - pos
            if can_buy <= 0:
                break
            desired = max(0, int(round(target - pos)))
            qty = min(ask_vol, can_buy, max(take_max // 2, desired if desired > 0 else take_max))
            if qty <= 0:
                break
            orders.append(Order(product, ask_price, qty))
            pos += qty

        for bid_price in sorted(order_depth.buy_orders.keys(), reverse=True):
            if ask_block:
                break
            edge = bid_price - fair - take_bias
            if edge < take_edge:
                break
            bid_vol = order_depth.buy_orders[bid_price]
            can_sell = limit + pos
            if can_sell <= 0:
                break
            desired = max(0, int(round(pos - target)))
            qty = min(bid_vol, can_sell, max(take_max // 2, desired if desired > 0 else take_max))
            if qty <= 0:
                break
            orders.append(Order(product, bid_price, -qty))
            pos -= qty

        relative = pos - target
        best_bid = max(order_depth.buy_orders) if order_depth.buy_orders else None
        best_ask = min(order_depth.sell_orders) if order_depth.sell_orders else None

        if relative > soft_limit and best_bid is not None and best_bid >= fair - clear_edge:
            qty = min(int(math.ceil(relative - soft_limit)), take_max + 6, limit + pos)
            if qty > 0:
                orders.append(Order(product, best_bid, -qty))
                pos -= qty
        elif relative < -soft_limit and best_ask is not None and best_ask <= fair + clear_edge:
            qty = min(int(math.ceil((-soft_limit) - relative)), take_max + 6, limit - pos)
            if qty > 0:
                orders.append(Order(product, best_ask, qty))
                pos += qty

        relative = pos - target
        reservation = fair + quote_bias - inv_skew * (relative / max(1.0, float(limit)))
        bid = round(reservation - quote_edge)
        ask = round(reservation + quote_edge)
        if best_bid is not None and best_ask is not None and best_bid < best_ask:
            spread = best_ask - best_bid
            if spread >= 3:
                bid = max(bid, best_bid + 1)
                ask = min(ask, best_ask - 1)
            else:
                bid = min(bid, best_bid)
                ask = max(ask, best_ask)
            if bid >= ask:
                ask = bid + 1

        if not bid_block and limit - pos > 0 and (best_ask is None or bid < best_ask):
            orders.append(Order(product, bid, min(quote_size, limit - pos)))
        if not ask_block and limit + pos > 0 and (best_bid is None or ask > best_bid):
            orders.append(Order(product, ask, -min(quote_size, limit + pos)))
        return orders

    def run(self, state: TradingState):
        saved = self._load_state(state.traderData)
        ema_prices: Dict[str, float] = saved.get("ema", {})
        velvet_state: Dict[str, float] = saved.get("velvet", {})
        result: Dict[str, List[Order]] = {}

        current_mids: Dict[str, float] = {}
        for product, od in state.order_depths.items():
            m = mid_price(od)
            if m is None:
                m = FAIR_VALUE.get(product, 0.0)
            current_mids[product] = m

        hydro_mid = current_mids.get("HYDROGEL_PACK", FAIR_VALUE["HYDROGEL_PACK"])
        if "HYDROGEL_PACK" in ema_prices:
            ema_prices["HYDROGEL_PACK"] = self.ALPHA * hydro_mid + (1 - self.ALPHA) * ema_prices["HYDROGEL_PACK"]
        else:
            ema_prices["HYDROGEL_PACK"] = FAIR_VALUE["HYDROGEL_PACK"]

        hydro_fair = ema_prices["HYDROGEL_PACK"]
        hydro_od = state.order_depths.get("HYDROGEL_PACK")
        if hydro_od is not None:
            hydro_pos = state.position.get("HYDROGEL_PACK", 0)
            hydro_orders: List[Order] = []
            self._take_orders("HYDROGEL_PACK", hydro_od, hydro_fair, hydro_pos, hydro_orders)
            new_hydro_pos = hydro_pos + sum(order.quantity for order in hydro_orders)
            self._make_market("HYDROGEL_PACK", hydro_od, hydro_fair, new_hydro_pos, hydro_orders)
            result["HYDROGEL_PACK"] = hydro_orders

        velvet_od = state.order_depths.get("VELVETFRUIT_EXTRACT")
        velvet_ctx: Optional[Dict[str, float]] = None
        if velvet_od is not None:
            velvet_pos = state.position.get("VELVETFRUIT_EXTRACT", 0)
            velvet_ctx = self._build_velvet_context(velvet_od, velvet_state, velvet_pos)
            result["VELVETFRUIT_EXTRACT"] = self._trade_targeted(
                "VELVETFRUIT_EXTRACT",
                velvet_od,
                velvet_ctx["fair"],
                velvet_pos,
                velvet_ctx["target"],
                take_edge=max(1.0, 0.45 * velvet_ctx["vol_ema"]),
                clear_edge=max(1.0, 0.28 * velvet_ctx["vol_ema"]),
                quote_edge=max(1.5, MM_HALF_SPREAD["VELVETFRUIT_EXTRACT"] + 0.18 * velvet_ctx["vol_ema"]),
                quote_size=10 if velvet_ctx["mode"] != "neutral" else 6,
                take_max=18 if velvet_ctx["mode"] != "neutral" else 10,
                soft_limit=60 if velvet_ctx["mode"] != "neutral" else 34,
                inv_skew=6.2,
                take_bias=velvet_ctx["take_bias"],
                quote_bias=velvet_ctx["quote_bias"],
                bid_block=bool(velvet_ctx["bid_block"]),
                ask_block=bool(velvet_ctx["ask_block"]),
            )

        if velvet_ctx is not None:
            z = float(velvet_ctx["z"])
            sigma_bs = clamp(0.17 + 0.04 * min(2.5, abs(z)), 0.12, 0.30)
            regime = str(velvet_ctx["mode"])
            for product, strike in VEV_STRIKES.items():
                od = state.order_depths.get(product)
                if od is None or POSITION_LIMITS.get(product, 0) <= 0:
                    if product in state.order_depths:
                        result[product] = []
                    continue
                opt_mid = mid_price(od)
                if opt_mid is None:
                    result[product] = []
                    continue
                delta = black_scholes_delta(velvet_ctx["fair"], strike, TTE_YEARS, sigma_bs)
                fair = black_scholes_call(velvet_ctx["fair"], strike, TTE_YEARS, sigma_bs)
                limit = POSITION_LIMITS[product]
                edge_scale = max(2.0, MM_HALF_SPREAD.get(product, 2.0))
                mispricing = fair - opt_mid
                bs_target = 0.35 * limit * math.tanh(mispricing / edge_scale)
                dir_weight = 0.55 + 0.45 * delta
                dir_target = 0.0
                if regime == "bull_peak":
                    dir_target = -limit * dir_weight * (0.75 if strike >= 5000 else 0.55)
                elif regime == "bear_trough":
                    dir_target = limit * dir_weight * (0.75 if strike >= 5000 else 0.55)
                target = clamp(dir_target + bs_target, -float(limit), float(limit))
                take_edge = max(1.0, edge_scale)
                clear_edge = max(1.0, 0.75 * edge_scale)
                quote_edge = max(1.0, edge_scale + 0.5)
                quote_size = 3 if strike >= 5000 else 2
                take_max = 5 if strike >= 5000 else 4
                soft_limit = max(4, int(0.6 * limit))
                take_bias = 0.10 * math.tanh(mispricing / edge_scale) * edge_scale
                quote_bias = 0.08 * math.tanh(mispricing / edge_scale) * edge_scale
                bid_block = regime == "bull_peak"
                ask_block = regime == "bear_trough"
                result[product] = self._trade_targeted(
                    product,
                    od,
                    fair,
                    state.position.get(product, 0),
                    target,
                    take_edge,
                    clear_edge,
                    quote_edge,
                    quote_size,
                    take_max,
                    soft_limit,
                    inv_skew=2.5 if strike >= 5000 else 3.0,
                    take_bias=take_bias,
                    quote_bias=quote_bias,
                    bid_block=bid_block,
                    ask_block=ask_block,
                )

        trader_data = self._save_state({"ema": ema_prices, "velvet": velvet_state})
        conversions = 0
        return result, conversions, trader_data
