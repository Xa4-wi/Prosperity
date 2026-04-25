from datamodel import OrderDepth, Order, TradingState
from typing import Dict, List, Tuple, Optional
import json
import math


class Trader:
    """
    Round 3 robust v2.

    Design goal:
    - avoid day-specific anchors / overfit thresholds
    - use local book fair for HYDROGEL_PACK and VELVETFRUIT_EXTRACT
    - use VELVETFRUIT_EXTRACT as underlying for all VEV vouchers
    - respect actual limits: HYDROGEL_PACK=200, VELVETFRUIT_EXTRACT=200, vouchers=300 each

    The voucher model is intentionally simple and robust:
        fair = intrinsic + smooth volatility/time premium
    It does NOT fit one historical day directly. It only uses strike distance, TTE and local underlying fair.
    """

    POSITION_LIMITS: Dict[str, int] = {
        "HYDROGEL_PACK": 200,
        "VELVETFRUIT_EXTRACT": 200,
        "VEV_4000": 300,
        "VEV_4500": 300,
        "VEV_5000": 300,
        "VEV_5100": 300,
        "VEV_5200": 300,
        "VEV_5300": 300,
        "VEV_5400": 300,
        "VEV_5500": 300,
        "VEV_6000": 300,
        "VEV_6500": 300,
    }

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

    def run(self, state: TradingState):
        data = self._load_data(state.traderData)
        result: Dict[str, List[Order]] = {}

        mids: Dict[str, float] = {}
        micros: Dict[str, float] = {}
        spreads: Dict[str, float] = {}

        for product, depth in state.order_depths.items():
            mid = self._mid(depth)
            if mid is None:
                continue
            micro = self._microprice(depth)
            mids[product] = mid
            micros[product] = micro if micro is not None else mid
            bid, _ = self._best_bid(depth)
            ask, _ = self._best_ask(depth)
            if bid is not None and ask is not None:
                spreads[product] = ask - bid
            self._update_stats(data, product, mid)

        extract_fair = None
        if "VELVETFRUIT_EXTRACT" in mids and "VELVETFRUIT_EXTRACT" in state.order_depths:
            extract_pos = state.position.get("VELVETFRUIT_EXTRACT", 0)
            extract_fair = self._extract_fair(data, state.order_depths["VELVETFRUIT_EXTRACT"], mids, micros, extract_pos)

        # Store extract fair for fallback when the underlying book disappears briefly.
        if extract_fair is not None:
            data["last_extract_fair"] = extract_fair
        else:
            extract_fair = data.get("last_extract_fair")

        for product, depth in state.order_depths.items():
            if product not in self.POSITION_LIMITS:
                continue

            pos = state.position.get(product, 0)
            orders: List[Order] = []

            if product == "VELVETFRUIT_EXTRACT":
                fair = self._extract_fair(data, depth, mids, micros, pos)
                orders = self._trade_local_mm(
                    product, depth, pos, fair,
                    take_edge=2.0,
                    quote_edge=2.0,
                    base_size=24,
                    min_spread_to_quote=3,
                    inv_skew=0.030,
                    max_take_size=42,
                )

            elif product == "HYDROGEL_PACK":
                fair = self._hydrogel_fair(data, depth, mids, micros, pos)
                orders = self._trade_local_mm(
                    product, depth, pos, fair,
                    take_edge=5.0,
                    quote_edge=7.0,
                    base_size=18,
                    min_spread_to_quote=11,
                    inv_skew=0.055,
                    max_take_size=34,
                )

            elif product in self.VOUCHER_STRIKES and extract_fair is not None:
                fair = self._voucher_fair(product, extract_fair, state.timestamp)
                orders = self._trade_voucher(product, depth, pos, fair, extract_fair)

            if orders:
                result[product] = orders
            else:
                result[product] = []

        return result, 0, json.dumps(data, separators=(",", ":"))

    # ---------------- Fair values ----------------

    def _extract_fair(self, data: dict, depth: OrderDepth, mids: Dict[str, float], micros: Dict[str, float], pos: int) -> float:
        p = "VELVETFRUIT_EXTRACT"
        mid = mids.get(p, self._mid(depth))
        micro = micros.get(p, mid)
        fast = data.get("ema_fast", {}).get(p, mid)
        slow = data.get("ema_slow", {}).get(p, mid)
        ret_ema = data.get("ret_ema", {}).get(p, 0.0)

        # Mostly local book. This is deliberate: historical daily means shift, so a fixed anchor overfits.
        fair = 0.50 * micro + 0.28 * mid + 0.17 * fast + 0.05 * slow

        # Weak mean-reverting correction. Do not chase hard because the days show noisy drift.
        trend = fast - slow
        fair += self._clip(-0.20 * trend, -2.0, 2.0)
        fair += self._clip(0.35 * ret_ema, -1.2, 1.2)
        fair += 0.9 * self._imbalance(depth)

        # Inventory penalty directly in fair and again in quote placement.
        fair -= 1.2 * (pos / self.POSITION_LIMITS[p])
        return fair

    def _hydrogel_fair(self, data: dict, depth: OrderDepth, mids: Dict[str, float], micros: Dict[str, float], pos: int) -> float:
        p = "HYDROGEL_PACK"
        mid = mids.get(p, self._mid(depth))
        micro = micros.get(p, mid)
        fast = data.get("ema_fast", {}).get(p, mid)
        slow = data.get("ema_slow", {}).get(p, mid)
        ret_ema = data.get("ret_ema", {}).get(p, 0.0)

        # Hydrogel is treated as local/random-walk with weak stabilization only.
        fair = 0.54 * micro + 0.25 * mid + 0.16 * fast + 0.05 * slow

        # Anti-chase: when recent movement is one-directional, require better prices to follow.
        trend = fast - slow
        fair += self._clip(-0.22 * trend, -3.0, 3.0)
        fair += self._clip(-0.25 * ret_ema, -2.0, 2.0)
        fair += 2.0 * self._imbalance(depth)
        fair -= 3.8 * (pos / self.POSITION_LIMITS[p])
        return fair

    def _voucher_fair(self, product: str, underlying_fair: float, timestamp: int) -> float:
        K = self.VOUCHER_STRIKES[product]
        intrinsic = max(0.0, underlying_fair - K)
        moneyness = underlying_fair - K

        # Actual final simulation starts at TTE=5. During one day it decays only slightly.
        # Keep a floor to avoid end-of-day collapse that was not learned robustly from just 3 files.
        day_progress = self._clip(timestamp / 1_000_000.0, 0.0, 1.0)
        tte = max(4.0, 5.0 - day_progress)
        tscale = math.sqrt(tte / 6.0)

        # Robust smooth premium. Highest near ATM, not directly fitted to one day.
        atm = 42.0 * math.exp(-((moneyness) / 135.0) ** 2)
        slight_otm = 10.0 * math.exp(-((moneyness + 90.0) / 180.0) ** 2)
        far_otm_tail = 2.0 * math.exp(-max(0.0, -moneyness - 170.0) / 230.0)
        premium = (atm + slight_otm + far_otm_tail) * tscale

        # Deep ITM options should trade close to parity, with only tiny premium.
        if moneyness > 450:
            premium = min(premium, 1.0)
        elif moneyness > 250:
            premium = min(premium, 3.0)

        # Very far OTM vouchers are lottery tickets. Do not value them below the observed tick-like floor,
        # but also do not build huge positions from tiny model differences.
        if moneyness < -700:
            premium = 0.5
        else:
            premium = max(0.5, premium)

        return intrinsic + premium

    # ---------------- Execution ----------------

    def _trade_local_mm(self, product: str, depth: OrderDepth, pos: int, fair: float,
                        take_edge: float, quote_edge: float, base_size: int,
                        min_spread_to_quote: int, inv_skew: float, max_take_size: int) -> List[Order]:
        orders: List[Order] = []
        limit = self.POSITION_LIMITS[product]
        best_bid, bid_vol = self._best_bid(depth)
        best_ask, ask_vol = self._best_ask(depth)
        if best_bid is None or best_ask is None:
            return orders

        buy_cap = limit - pos
        sell_cap = limit + pos

        # Take clear edge. Scale with mispricing but cap to avoid one bad book snapshot killing us.
        if buy_cap > 0 and best_ask <= fair - take_edge:
            edge = fair - best_ask
            qty = min(buy_cap, abs(ask_vol), max_take_size, int(base_size + 3 * max(0.0, edge - take_edge)))
            if qty > 0:
                orders.append(Order(product, int(best_ask), qty))
                buy_cap -= qty

        if sell_cap > 0 and best_bid >= fair + take_edge:
            edge = best_bid - fair
            qty = min(sell_cap, abs(bid_vol), max_take_size, int(base_size + 3 * max(0.0, edge - take_edge)))
            if qty > 0:
                orders.append(Order(product, int(best_bid), -qty))
                sell_cap -= qty

        spread = best_ask - best_bid
        if spread >= min_spread_to_quote:
            inventory_pressure = inv_skew * pos
            adj = fair - inventory_pressure
            bid_px = min(best_bid + 1, math.floor(adj - quote_edge))
            ask_px = max(best_ask - 1, math.ceil(adj + quote_edge))

            if bid_px < ask_px:
                buy_size = min(buy_cap, self._inventory_scaled_size(base_size, pos, limit, side=1))
                sell_size = min(sell_cap, self._inventory_scaled_size(base_size, pos, limit, side=-1))

                # Near inventory limit: prioritize flattening, not adding.
                if pos > 0.75 * limit:
                    buy_size = 0
                    sell_size = min(sell_cap, max(sell_size, base_size))
                elif pos < -0.75 * limit:
                    sell_size = 0
                    buy_size = min(buy_cap, max(buy_size, base_size))

                if buy_size > 0:
                    orders.append(Order(product, int(bid_px), int(buy_size)))
                if sell_size > 0:
                    orders.append(Order(product, int(ask_px), -int(sell_size)))

        return orders

    def _trade_voucher(self, product: str, depth: OrderDepth, pos: int, fair: float, underlying_fair: float) -> List[Order]:
        orders: List[Order] = []
        limit = self.POSITION_LIMITS[product]
        best_bid, bid_vol = self._best_bid(depth)
        best_ask, ask_vol = self._best_ask(depth)
        if best_bid is None or best_ask is None:
            return orders

        K = self.VOUCHER_STRIKES[product]
        moneyness = underlying_fair - K
        spread = best_ask - best_bid
        mid = (best_bid + best_ask) / 2.0

        # Capacity is larger here, but do not use the full 300 just because one day favored it.
        if moneyness > 350 or product in ("VEV_4000", "VEV_4500"):
            base_size = 28
            take_edge = 1.2
            quote_edge = 1.0
        elif -220 <= moneyness <= 220:
            base_size = 24
            take_edge = 1.8
            quote_edge = 1.2
        elif moneyness < -650:
            base_size = 6
            take_edge = 0.8
            quote_edge = 0.8
        else:
            base_size = 16
            take_edge = 1.5
            quote_edge = 1.0

        # If the market is basically at the tick floor, only trade when the model edge is clear.
        if fair <= 1.05:
            base_size = min(base_size, 5)
            take_edge = 0.7

        # Inventory skew in price space. Stronger than local products because vouchers can be one-sided.
        inv_adj = fair - 0.018 * pos
        buy_cap = limit - pos
        sell_cap = limit + pos

        if buy_cap > 0 and best_ask <= fair - take_edge:
            edge = fair - best_ask
            qty = min(buy_cap, abs(ask_vol), int(base_size + 2.0 * max(0.0, edge - take_edge)))
            if qty > 0:
                orders.append(Order(product, int(best_ask), int(qty)))
                buy_cap -= qty

        if sell_cap > 0 and best_bid >= fair + take_edge:
            edge = best_bid - fair
            qty = min(sell_cap, abs(bid_vol), int(base_size + 2.0 * max(0.0, edge - take_edge)))
            if qty > 0:
                orders.append(Order(product, int(best_bid), -int(qty)))
                sell_cap -= qty

        # Passive quote only when spread gives protection. Avoid quoting useless far OTM unless spread is wide.
        if spread >= 2 and not (fair <= 1.05 and spread < 3):
            bid_px = min(best_bid + 1, math.floor(inv_adj - quote_edge))
            ask_px = max(best_ask - 1, math.ceil(inv_adj + quote_edge))

            if bid_px < ask_px:
                buy_size = min(buy_cap, self._inventory_scaled_size(base_size, pos, limit, side=1))
                sell_size = min(sell_cap, self._inventory_scaled_size(base_size, pos, limit, side=-1))

                # Do not keep adding to extreme positions; instead quote only the side that reduces risk.
                if pos > 0.70 * limit:
                    buy_size = 0
                    sell_size = min(sell_cap, max(sell_size, base_size))
                elif pos < -0.70 * limit:
                    sell_size = 0
                    buy_size = min(buy_cap, max(buy_size, base_size))

                # Guardrails: do not bid above fair or ask below fair after rounding.
                if buy_size > 0 and bid_px <= fair - 0.3:
                    orders.append(Order(product, int(bid_px), int(buy_size)))
                if sell_size > 0 and ask_px >= fair + 0.3:
                    orders.append(Order(product, int(ask_px), -int(sell_size)))

        return orders

    # ---------------- State/stat helpers ----------------

    def _load_data(self, trader_data: str) -> dict:
        if not trader_data:
            return {"ema_fast": {}, "ema_slow": {}, "last_mid": {}, "ret_ema": {}}
        try:
            data = json.loads(trader_data)
            for k in ("ema_fast", "ema_slow", "last_mid", "ret_ema"):
                if k not in data:
                    data[k] = {}
            return data
        except Exception:
            return {"ema_fast": {}, "ema_slow": {}, "last_mid": {}, "ret_ema": {}}

    def _update_stats(self, data: dict, product: str, mid: float) -> None:
        prev_fast = data["ema_fast"].get(product, mid)
        prev_slow = data["ema_slow"].get(product, mid)
        prev_mid = data["last_mid"].get(product, mid)
        prev_ret = data["ret_ema"].get(product, 0.0)

        # Fast reacts within the current local regime; slow prevents pure tick chasing.
        data["ema_fast"][product] = 0.18 * mid + 0.82 * prev_fast
        data["ema_slow"][product] = 0.035 * mid + 0.965 * prev_slow
        data["ret_ema"][product] = 0.20 * (mid - prev_mid) + 0.80 * prev_ret
        data["last_mid"][product] = mid

    # ---------------- Order book helpers ----------------

    def _best_bid(self, depth: OrderDepth) -> Tuple[Optional[int], int]:
        if not depth.buy_orders:
            return None, 0
        px = max(depth.buy_orders.keys())
        return px, depth.buy_orders[px]

    def _best_ask(self, depth: OrderDepth) -> Tuple[Optional[int], int]:
        if not depth.sell_orders:
            return None, 0
        px = min(depth.sell_orders.keys())
        return px, depth.sell_orders[px]

    def _mid(self, depth: OrderDepth) -> Optional[float]:
        bid, _ = self._best_bid(depth)
        ask, _ = self._best_ask(depth)
        if bid is None or ask is None:
            return None
        return (bid + ask) / 2.0

    def _microprice(self, depth: OrderDepth) -> Optional[float]:
        bid, bid_vol = self._best_bid(depth)
        ask, ask_vol = self._best_ask(depth)
        if bid is None or ask is None:
            return None
        b = abs(bid_vol)
        a = abs(ask_vol)
        if b + a <= 0:
            return (bid + ask) / 2.0
        return (bid * a + ask * b) / (a + b)

    def _imbalance(self, depth: OrderDepth) -> float:
        bid, bid_vol = self._best_bid(depth)
        ask, ask_vol = self._best_ask(depth)
        if bid is None or ask is None:
            return 0.0
        b = abs(bid_vol)
        a = abs(ask_vol)
        if b + a <= 0:
            return 0.0
        return self._clip((b - a) / (b + a), -1.0, 1.0)

    def _inventory_scaled_size(self, base: int, pos: int, limit: int, side: int) -> int:
        inv = pos / max(1, limit)
        if side == 1:
            # If already long, bid smaller. If short, bid larger to flatten.
            factor = 1.0 - 0.75 * max(0.0, inv) + 0.35 * max(0.0, -inv)
        else:
            # If already short, ask smaller. If long, ask larger to flatten.
            factor = 1.0 - 0.75 * max(0.0, -inv) + 0.35 * max(0.0, inv)
        return max(1, int(round(base * self._clip(factor, 0.20, 1.35))))

    def _clip(self, x: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, x))
