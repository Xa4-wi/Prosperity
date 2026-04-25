from datamodel import OrderDepth, Order, TradingState
from typing import Dict, List, Tuple, Optional
import json
import math


class Trader:
    """
    Robust Round 3 bot built from cross-day findings:
    - VELVETFRUIT_EXTRACT: local-fair market making; no fixed day anchor.
    - HYDROGEL_PACK: state-aware local fair with inventory flattening; treats it like a noisy random-walk product.
    - VEV vouchers: cross-sectional fair = intrinsic value from VELVETFRUIT_EXTRACT + robust time-value curve.
      The curve is intentionally smooth and conservative instead of hardcoding one day's option mids.
    """

    POSITION_LIMITS: Dict[str, int] = {
        "VELVETFRUIT_EXTRACT": 200,
        "HYDROGEL_PACK": 200,
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

        # Update all local statistics first so voucher fair can use extract fair.
        mids: Dict[str, float] = {}
        micros: Dict[str, float] = {}
        for product, depth in state.order_depths.items():
            mid = self._mid(depth)
            micro = self._microprice(depth)
            if mid is None:
                continue
            mids[product] = mid
            micros[product] = micro if micro is not None else mid
            self._update_ema(data, product, mid)

        extract_fair = None
        if "VELVETFRUIT_EXTRACT" in state.order_depths and "VELVETFRUIT_EXTRACT" in mids:
            extract_fair = self._extract_fair(data, state.order_depths["VELVETFRUIT_EXTRACT"], mids, micros)

        for product, depth in state.order_depths.items():
            if product not in self.POSITION_LIMITS:
                continue

            pos = state.position.get(product, 0)
            orders: List[Order] = []

            if product == "VELVETFRUIT_EXTRACT":
                fair = self._extract_fair(data, depth, mids, micros)
                orders = self._trade_market_maker(
                    product, depth, pos, fair,
                    take_edge=2.0, quote_edge=2.0,
                    passive_size=20, inventory_skew=0.018,
                    min_spread_to_quote=3,
                )

            elif product == "HYDROGEL_PACK":
                fair = self._hydrogel_fair(data, depth, product, mids, micros, pos)
                orders = self._trade_market_maker(
                    product, depth, pos, fair,
                    take_edge=5.0, quote_edge=7.0,
                    passive_size=10, inventory_skew=0.045,
                    min_spread_to_quote=10,
                )

            elif product in self.VOUCHER_STRIKES and extract_fair is not None:
                fair = self._voucher_fair(product, extract_fair, state.timestamp)
                orders = self._trade_voucher(product, depth, pos, fair)

            result[product] = orders

        trader_data = json.dumps(data, separators=(",", ":"))
        conversions = 0
        return result, conversions, trader_data

    # ---------- Fair values ----------

    def _extract_fair(self, data: dict, depth: OrderDepth, mids: Dict[str, float], micros: Dict[str, float]) -> float:
        product = "VELVETFRUIT_EXTRACT"
        mid = mids.get(product)
        micro = micros.get(product, mid)
        ema_fast = data.get("ema", {}).get(product, mid)
        ema_slow = data.get("ema_slow", {}).get(product, mid)

        # Local fair: mostly current book, slightly stabilized by EMA.
        fair = 0.55 * micro + 0.30 * mid + 0.15 * ema_fast

        # Only a tiny trend component. The files show mildly negative return autocorrelation,
        # so this should not chase hard.
        trend = ema_fast - ema_slow
        fair += max(-1.5, min(1.5, 0.25 * trend))

        fair += 0.8 * self._imbalance(depth)
        return fair

    def _hydrogel_fair(self, data: dict, depth: OrderDepth, product: str,
                       mids: Dict[str, float], micros: Dict[str, float], pos: int) -> float:
        mid = mids.get(product)
        micro = micros.get(product, mid)
        ema_fast = data.get("ema", {}).get(product, mid)
        ema_slow = data.get("ema_slow", {}).get(product, mid)

        # Hydrogel looked like a noisy walk with day-to-day shifts, so fixed anchors are dangerous.
        # Use the local book and state; only a weak long-run pull around 10000.
        fair = 0.50 * micro + 0.30 * mid + 0.15 * ema_fast + 0.05 * 10000.0

        # Short-term anti-chase: when fast EMA is above slow EMA, do not keep lifting asks blindly.
        trend = ema_fast - ema_slow
        fair += max(-2.5, min(2.5, -0.18 * trend))

        # Order-book imbalance matters, but cap it to avoid one-tick spoof sensitivity.
        fair += 2.0 * self._imbalance(depth)

        # Extra inventory pull, separate from quote skew, so hydrogel resets faster after runs.
        limit = self.POSITION_LIMITS[product]
        fair -= 4.0 * (pos / limit)
        return fair

    def _voucher_fair(self, product: str, underlying_fair: float, timestamp: int) -> float:
        K = self.VOUCHER_STRIKES[product]
        intrinsic = max(0.0, underlying_fair - K)
        d = K - underlying_fair

        # Smooth premium curve learned from days 0 and 1:
        # - near-zero for deep ITM/OTM
        # - highest around ATM/slightly OTM
        # - conservative floor of 0.5 because 6000/6500 traded at 0.5 in all files
        atm_hump = 49.0 * math.exp(-((d - 0.0) / 118.0) ** 2)
        slight_itm_hump = 5.5 * math.exp(-((d + 245.0) / 80.0) ** 2)
        far_otm_tail = 1.6 * math.exp(-max(0.0, d - 150.0) / 140.0)

        premium = max(0.5, atm_hump + slight_itm_hump + far_otm_tail)

        # Time decay is deliberately mild: in the files the cross-sectional curve dominates.
        # End-of-day timestamp is around 1_000_000.
        time_left = max(0.0, min(1.0, (1_000_000 - timestamp) / 1_000_000))
        if K >= 5300:
            premium *= (0.92 + 0.08 * time_left)
        elif K <= 5000:
            premium *= (0.96 + 0.04 * time_left)

        # Deep ITM options are basically parity; avoid overpricing their tiny premium.
        if d < -450:
            premium = min(premium, 0.75)
        # Very far OTM options should not be accumulated aggressively.
        if d > 550:
            premium = 0.5

        return intrinsic + premium

    # ---------- Trading logic ----------

    def _trade_market_maker(self, product: str, depth: OrderDepth, pos: int, fair: float,
                            take_edge: float, quote_edge: float, passive_size: int,
                            inventory_skew: float, min_spread_to_quote: int) -> List[Order]:
        orders: List[Order] = []
        limit = self.POSITION_LIMITS[product]

        best_bid, bid_vol = self._best_bid(depth)
        best_ask, ask_vol = self._best_ask(depth)

        # Inventory-adjusted fair for passive quotes.
        adjusted_fair = fair - inventory_skew * pos

        buy_cap = limit - pos
        sell_cap = limit + pos

        # Take clear mispricings first.
        if best_ask is not None and buy_cap > 0 and best_ask <= fair - take_edge:
            qty = min(buy_cap, abs(ask_vol), passive_size * 2)
            if qty > 0:
                orders.append(Order(product, int(best_ask), qty))
                buy_cap -= qty

        if best_bid is not None and sell_cap > 0 and best_bid >= fair + take_edge:
            qty = min(sell_cap, abs(bid_vol), passive_size * 2)
            if qty > 0:
                orders.append(Order(product, int(best_bid), -qty))
                sell_cap -= qty

        # Passive market making only when spread can pay for adverse selection.
        if best_bid is not None and best_ask is not None and best_ask - best_bid >= min_spread_to_quote:
            bid_px = min(best_bid + 1, math.floor(adjusted_fair - quote_edge))
            ask_px = max(best_ask - 1, math.ceil(adjusted_fair + quote_edge))

            if bid_px < ask_px:
                buy_size = min(buy_cap, self._scaled_size(passive_size, pos, limit, side=1))
                sell_size = min(sell_cap, self._scaled_size(passive_size, pos, limit, side=-1))

                if buy_size > 0:
                    orders.append(Order(product, int(bid_px), buy_size))
                if sell_size > 0:
                    orders.append(Order(product, int(ask_px), -sell_size))

        return orders

    def _trade_voucher(self, product: str, depth: OrderDepth, pos: int, fair: float) -> List[Order]:
        orders: List[Order] = []
        limit = self.POSITION_LIMITS[product]
        best_bid, bid_vol = self._best_bid(depth)
        best_ask, ask_vol = self._best_ask(depth)
        if best_bid is None or best_ask is None:
            return orders

        spread = best_ask - best_bid
        mid = (best_bid + best_ask) / 2

        # Wider edge for thin/tiny vouchers; tighter for parity-like deep ITM instruments.
        if product in ("VEV_4000", "VEV_4500"):
            take_edge = 1.5
            quote_edge = 1.0
            base_size = 18
        elif product in ("VEV_5000", "VEV_5100", "VEV_5200", "VEV_5300"):
            take_edge = 2.0
            quote_edge = 1.5
            base_size = 14
        else:
            take_edge = 1.2
            quote_edge = 1.0
            base_size = 10

        # Avoid large positions in near-worthless far OTM options.
        if fair <= 1.0 and product in ("VEV_6000", "VEV_6500"):
            base_size = 4
            take_edge = 0.8

        buy_cap = limit - pos
        sell_cap = limit + pos

        if buy_cap > 0 and best_ask <= fair - take_edge:
            qty = min(buy_cap, abs(ask_vol), base_size)
            if qty > 0:
                orders.append(Order(product, int(best_ask), qty))
                buy_cap -= qty

        if sell_cap > 0 and best_bid >= fair + take_edge:
            qty = min(sell_cap, abs(bid_vol), base_size)
            if qty > 0:
                orders.append(Order(product, int(best_bid), -qty))
                sell_cap -= qty

        # Passive quotes. Pull away when inventory is high.
        inv_adj = fair - 0.025 * pos
        if spread >= 2:
            bid_px = min(best_bid + 1, math.floor(inv_adj - quote_edge))
            ask_px = max(best_ask - 1, math.ceil(inv_adj + quote_edge))
            if bid_px < ask_px:
                buy_size = min(buy_cap, self._scaled_size(base_size, pos, limit, side=1))
                sell_size = min(sell_cap, self._scaled_size(base_size, pos, limit, side=-1))
                # Do not bid above model fair for tiny OTM vouchers.
                if buy_size > 0 and bid_px <= fair - 0.5:
                    orders.append(Order(product, int(bid_px), buy_size))
                if sell_size > 0 and ask_px >= fair + 0.5:
                    orders.append(Order(product, int(ask_px), -sell_size))

        return orders

    # ---------- State helpers ----------

    def _load_data(self, trader_data: str) -> dict:
        if not trader_data:
            return {"ema": {}, "ema_slow": {}}
        try:
            data = json.loads(trader_data)
            if "ema" not in data:
                data["ema"] = {}
            if "ema_slow" not in data:
                data["ema_slow"] = {}
            return data
        except Exception:
            return {"ema": {}, "ema_slow": {}}

    def _update_ema(self, data: dict, product: str, mid: float) -> None:
        fast_alpha = 0.18
        slow_alpha = 0.035
        prev = data["ema"].get(product, mid)
        prev_slow = data["ema_slow"].get(product, mid)
        data["ema"][product] = fast_alpha * mid + (1.0 - fast_alpha) * prev
        data["ema_slow"][product] = slow_alpha * mid + (1.0 - slow_alpha) * prev_slow

    # ---------- Order book helpers ----------

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
        bid_sz = abs(bid_vol)
        ask_sz = abs(ask_vol)
        denom = bid_sz + ask_sz
        if denom <= 0:
            return (bid + ask) / 2.0
        # More bid size pushes fair toward ask, more ask size pushes fair toward bid.
        return (bid * ask_sz + ask * bid_sz) / denom

    def _imbalance(self, depth: OrderDepth) -> float:
        bid, bid_vol = self._best_bid(depth)
        ask, ask_vol = self._best_ask(depth)
        if bid is None or ask is None:
            return 0.0
        b = abs(bid_vol)
        a = abs(ask_vol)
        if b + a == 0:
            return 0.0
        return max(-1.0, min(1.0, (b - a) / (b + a)))

    def _scaled_size(self, base: int, pos: int, limit: int, side: int) -> int:
        # side=1 means buy; side=-1 means sell.
        inv = pos / max(1, limit)
        if side == 1:
            factor = 1.0 - max(0.0, inv)
        else:
            factor = 1.0 + min(0.0, inv)
        return max(1, int(round(base * max(0.25, min(1.0, factor)))))
