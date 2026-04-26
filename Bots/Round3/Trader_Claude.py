from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict, Optional
import json
import math


# ── Position limits (adjust to match competition rules) ──────────────────────
POSITION_LIMITS: Dict[str, int] = {
    "VELVETFRUIT_EXTRACT": 60,
    "HYDROGEL_PACK":       50,
    "VEV_4000":            20,
    "VEV_4500":            20,
    "VEV_5000":            20,
    "VEV_5100":            20,
    "VEV_5200":            20,
    "VEV_5300":            20,
    "VEV_5400":            20,
    "VEV_5500":            20,
    "VEV_6000":             0,   # worthless — never trade
    "VEV_6500":             0,   # worthless — never trade
}

# ── Historical fair-value anchors (computed from 90 000 price rows) ──────────
FAIR_VALUE: Dict[str, float] = {
    "VELVETFRUIT_EXTRACT": 5250.0,
    "HYDROGEL_PACK":       9990.0,
    "VEV_4000":            1250.0,
    "VEV_4500":             750.0,
    "VEV_5000":             255.0,
    "VEV_5100":             167.0,
    "VEV_5200":              95.5,
    "VEV_5300":              46.8,
    "VEV_5400":              16.0,
    "VEV_5500":               6.6,
}

# ── Market-making half-spread per product ────────────────────────────────────
# Set wide enough to cover transaction risk but narrow enough to get fills.
MM_HALF_SPREAD: Dict[str, float] = {
    "VELVETFRUIT_EXTRACT": 3,
    "HYDROGEL_PACK":       9,
    "VEV_4000":           12,
    "VEV_4500":            9,
    "VEV_5000":            4,
    "VEV_5100":            3,
    "VEV_5200":            2,
    "VEV_5300":            1,
    "VEV_5400":            1,
    "VEV_5500":            1,
}

# Options are calls on VELVETFRUIT_EXTRACT; strike embedded in product name.
VEV_STRIKES: Dict[str, int] = {
    f"VEV_{s}": s for s in [4000, 4500, 5000, 5100, 5200, 5300, 5400, 5500]
}


def mid_price(order_depth: OrderDepth) -> Optional[float]:
    """Best-bid/best-ask midpoint, or None if one side is empty."""
    if not order_depth.buy_orders or not order_depth.sell_orders:
        return None
    best_bid = max(order_depth.buy_orders)
    best_ask = min(order_depth.sell_orders)
    return (best_bid + best_ask) / 2.0


def vev_fair_value(strike: int, underlying_mid: float) -> float:
    """
    Rough call-option fair value.

    Deep ITM  (underlying >> strike): essentially underlying - strike.
    Near/OTM  (underlying ~= strike): use a simple linear interpolation
              between intrinsic and a small time-value premium observed
              in the data (~50 ticks for ATM).
    Far OTM   (underlying << strike): floor at 0.5 (exchange minimum).
    """
    intrinsic = max(0.0, underlying_mid - strike)
    moneyness = underlying_mid - strike          # negative = OTM

    if moneyness >= 500:                         # deep ITM — no time value
        return intrinsic + 0.1
    elif moneyness >= 0:                         # ITM / ATM
        # time value decays linearly from ~50 at ATM to 0 at +500
        time_value = 50.0 * (1.0 - moneyness / 500.0)
        return intrinsic + time_value
    else:                                        # OTM
        # time value decays quickly; use exponential decay
        time_value = 50.0 * math.exp(moneyness / 100.0)
        return max(0.5, intrinsic + time_value)


class Trader:

    # ── EMA state (persisted via traderData JSON) ────────────────────────────
    ALPHA = 0.05          # slow EMA to track drifting fair value

    def _load_state(self, trader_data: str) -> Dict:
        if trader_data:
            try:
                return json.loads(trader_data)
            except Exception:
                pass
        return {}

    def _save_state(self, state_dict: Dict) -> str:
        return json.dumps(state_dict)

    # ── Core order-placement helpers ─────────────────────────────────────────

    def _take_orders(
        self,
        product: str,
        order_depth: OrderDepth,
        fair: float,
        position: int,
        orders: List[Order],
    ) -> None:
        """
        Hit any asks below fair value (buy) and any bids above fair value (sell).
        Respects position limits.
        """
        limit = POSITION_LIMITS.get(product, 0)
        if limit == 0:
            return

        # Buy cheap asks
        for ask_price in sorted(order_depth.sell_orders.keys()):
            if ask_price >= fair:
                break
            ask_vol = -order_depth.sell_orders[ask_price]   # stored negative
            can_buy = limit - position
            if can_buy <= 0:
                break
            qty = min(ask_vol, can_buy)
            orders.append(Order(product, ask_price, qty))
            position += qty

        # Sell expensive bids
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
        """
        Post resting bid/ask around the fair value.
        Skews quotes toward zero when position is large.
        """
        limit = POSITION_LIMITS.get(product, 0)
        if limit == 0:
            return

        half = MM_HALF_SPREAD.get(product, 2)

        # Skew: if long, lower both quotes to encourage selling and vice-versa
        skew = -round((position / limit) * (half * 0.5))

        bid = round(fair - half + skew)
        ask = round(fair + half + skew)

        # Only post if we have room
        can_buy  = limit - position
        can_sell = limit + position

        best_existing_bid = max(order_depth.buy_orders) if order_depth.buy_orders else 0
        best_existing_ask = min(order_depth.sell_orders) if order_depth.sell_orders else 999999

        # Quote tighter than existing best (to be first in queue)
        bid = min(bid, best_existing_bid + 1) if best_existing_bid > 0 else bid
        ask = max(ask, best_existing_ask - 1) if best_existing_ask < 999999 else ask

        if bid >= ask:
            ask = bid + 1

        mm_size = max(1, min(10, limit // 4))

        if can_buy > 0:
            orders.append(Order(product, bid, min(mm_size, can_buy)))
        if can_sell > 0:
            orders.append(Order(product, ask, -min(mm_size, can_sell)))

    # ── Main entry point ─────────────────────────────────────────────────────

    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        saved = self._load_state(state.traderData)
        ema_prices: Dict[str, float] = saved.get("ema", {})

        result: Dict[str, List[Order]] = {}

        # ── Step 1: establish current mid-prices ────────────────────────────
        current_mids: Dict[str, float] = {}
        for product, od in state.order_depths.items():
            m = mid_price(od)
            if m is None:
                m = FAIR_VALUE.get(product, 0.0)
            current_mids[product] = m

            # Update EMA
            if product in ema_prices:
                ema_prices[product] = (
                    self.ALPHA * m + (1 - self.ALPHA) * ema_prices[product]
                )
            else:
                ema_prices[product] = FAIR_VALUE.get(product, m)

        # ── Step 2: derive fair values ───────────────────────────────────────
        fair_values: Dict[str, float] = {}

        # Underlying: use EMA (tracks slow drift) blended with anchor
        for product in ["VELVETFRUIT_EXTRACT", "HYDROGEL_PACK"]:
            if product in ema_prices:
                fair_values[product] = ema_prices[product]
            else:
                fair_values[product] = FAIR_VALUE.get(product, 0.0)

        # Options: derive from VELVETFRUIT_EXTRACT mid-price
        vfe_mid = current_mids.get(
            "VELVETFRUIT_EXTRACT",
            fair_values.get("VELVETFRUIT_EXTRACT", 5250.0),
        )
        for product, strike in VEV_STRIKES.items():
            fair_values[product] = vev_fair_value(strike, vfe_mid)

        # ── Step 3: generate orders ──────────────────────────────────────────
        for product, od in state.order_depths.items():
            if POSITION_LIMITS.get(product, 0) == 0:
                result[product] = []
                continue

            fair = fair_values.get(product, FAIR_VALUE.get(product, 0.0))
            position = state.position.get(product, 0)
            orders: List[Order] = []

            # First take mispriced orders, then provide liquidity
            self._take_orders(product, od, fair, position, orders)

            # Recompute position after taking
            taken_qty = sum(o.quantity for o in orders)
            new_position = position + taken_qty

            self._make_market(product, od, fair, new_position, orders)

            result[product] = orders
            print(
                f"{product}: fair={fair:.1f} pos={position} "
                f"orders={[(o.price, o.quantity) for o in orders]}"
            )

        # ── Persist EMA state ────────────────────────────────────────────────
        trader_data = self._save_state({"ema": ema_prices})
        conversions = 0
        return result, conversions, trader_data
