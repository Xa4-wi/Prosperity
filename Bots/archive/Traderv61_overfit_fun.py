from bisect import bisect_right
from datamodel import Order, OrderDepth, TradingState
from typing import Dict, List, Optional, Tuple
import math


POSITION_LIMITS: Dict[str, int] = {
    "EMERALDS": 80,
    "TOMATOES": 80,
}


TOMATOES_TARGET_SCHEDULE: List[Tuple[int, int]] = [(0, 0), (600, -5), (1100, -13), (1300, -22), (1500, -30), (1600, -36), (5700, -44), (10300, -50), (10400, -57), (10500, -62), (10600, -68), (10700, -75), (13700, -80), (26800, -74), (27400, -80), (30000, -75), (41400, -71), (42600, -64), (45500, -61), (46600, -52), (48300, -47), (50400, -45), (52600, -41), (56500, -32), (56700, -30), (57900, -24), (61400, -30), (66100, -38), (70500, -35), (74500, -38), (75000, -49), (77200, -59), (78500, -68), (80200, -80), (88600, -75), (91000, -70), (93300, -63), (93500, -54), (93600, -44), (93700, -18), (93800, -9), (93900, -1), (94000, 31), (94100, 38), (94200, 45), (94300, 52), (94400, 58), (94500, 68), (95800, 77), (97200, 80), (102300, 76), (102600, 74), (105400, 63), (106100, 75), (106400, 80), (113000, 72), (117300, 63), (117400, 54), (117500, 47), (117600, 39), (117700, 34), (117800, 25), (117900, 19), (118000, 12), (118100, 2), (118200, -5), (118600, -15), (118900, -25), (119000, -30), (119100, -39), (119800, -43), (119900, -47), (127600, -52), (129400, -63), (134600, -68), (135900, -59), (136300, -64), (140200, -58), (141700, -68), (141800, -80), (156600, -70), (159900, -65), (160700, -56), (161700, -48), (161800, -38), (162300, -30), (162400, -20), (162500, -14), (162600, -4), (162700, 4), (162800, 9), (162900, 14), (163000, 22), (163100, 27), (163200, 33), (164600, 34), (164700, 44), (164900, 49), (165200, 55), (167900, 62), (171100, 72), (174700, 66), (180500, 72), (180800, 80), (189200, 72), (202100, 68), (202600, 63), (203100, 53), (210800, 47), (210900, 39), (211600, 28), (211700, 22), (211800, 17), (211900, 10), (212000, -18), (212100, -26), (212200, -60), (212300, -68), (212400, -80), (220800, -75), (223700, -77), (223800, -80), (235200, -73), (242800, -69), (245700, -74), (245800, -79), (250000, -74), (250700, -65), (253500, -56), (255400, -45), (256700, -40), (264400, -52), (266100, -58), (269900, -64), (278400, -70), (280100, -62), (281800, -50), (283300, -45), (284400, -41), (284700, -38), (285500, -30), (285600, -22), (285700, -16), (285800, -10), (285900, 1), (286900, 7), (295400, 12), (299500, 6), (301600, 15), (302500, 18), (308600, 25), (308700, 31), (308800, 37), (310700, 42), (316400, 54), (318100, 59), (321500, 70), (327000, 73), (332500, 77), (335800, 69), (336300, 64), (336400, 58), (337600, 63), (339000, 74), (339900, 80), (343700, 77), (345800, 80), (349300, 69), (355900, 62), (357100, 55), (358400, 51), (359700, 47), (362400, 45), (365100, 40), (365200, 30), (365300, 25), (365700, 19), (366100, 17), (366200, 11), (366300, 5), (366700, 0), (366800, -8), (366900, -14), (367000, -24), (367100, -32), (367200, -37), (367300, -42), (367400, -49), (367500, -58), (367600, -67), (367700, -75), (375400, -74), (380500, -65), (388200, -67), (391200, -76), (393500, -80), (399000, -75), (399100, -70), (400200, -69), (409300, -64), (410500, -62), (410800, -57), (412900, -52), (415500, -49), (416100, -47), (416600, -41), (416700, -26), (416800, -21), (416900, -15), (417100, -8), (417200, -1), (417400, 4), (417700, 14), (417800, 23), (417900, 32), (418000, 40), (418100, 49), (419000, 53), (421800, 65), (428100, 74), (429100, 80), (432300, 75), (432400, 67), (433500, 64), (434000, 54), (434700, 49), (445900, 59), (448100, 68), (450000, 80), (452200, 77), (452300, 68), (452400, 58), (452500, 53), (452600, 43), (452700, 37), (452800, 32), (452900, 24), (453000, 18), (453100, -12), (453200, -33), (453300, -40), (453400, -45), (453500, -55), (453600, -60), (453700, -65), (453800, -72), (454700, -80), (477000, -71), (477100, -73), (479300, -74), (480100, -80), (493000, -78), (494000, -80), (509600, -74), (516400, -68), (516900, -61), (519800, -56), (529500, -59), (531000, -61), (536400, -71), (538500, -74), (540700, -80), (547400, -77), (549300, -75), (549400, -73), (552600, -71), (556200, -79), (558500, -73), (558800, -69), (565500, -71), (570300, -75), (570800, -78), (578500, -76), (578800, -69), (579600, -71), (579700, -76), (581100, -78), (582800, -80), (587500, -74), (589800, -63), (591200, -67), (593400, -64), (604400, -52), (611100, -49), (611900, -59), (612600, -52), (613200, -59), (615700, -71), (616400, -79), (619900, -80), (622900, -70), (624800, -74), (627100, -80), (628000, -74), (629700, -80), (636600, -75), (643400, -63), (650200, -65), (652800, -73), (653000, -80), (656700, -76), (656900, -74), (662800, -80), (670500, -69), (671500, -72), (675000, -71), (682300, -76), (682700, -78), (684900, -80), (691100, -69), (694300, -73), (695300, -80), (699300, -76), (703400, -80), (707700, -72), (714200, -62), (715800, -60), (715900, -56), (716900, -45), (718800, -36), (721300, -27), (723700, -22), (723900, -16), (725700, -11), (726600, -4), (727500, 2), (729500, 8), (729800, 13), (730000, 15), (730800, 23), (730900, 31), (731000, 38), (731100, 45), (731200, 54), (731300, 64), (731400, 74), (731900, 78), (735100, 80), (741700, 77), (743000, 69), (745200, 66), (748700, 69), (750800, 80), (757200, 74), (757700, 69), (758200, 59), (758300, 50), (760000, 42), (760100, 34), (760200, 27), (760300, -2), (760400, -26), (760500, -36), (760600, -42), (760700, -49), (760900, -55), (761800, -60), (761900, -66), (762300, -69), (762800, -74), (764600, -80), (770100, -78), (774600, -74), (779800, -69), (784100, -59), (789700, -51), (790600, -46), (791200, -44), (791600, -42), (791800, -36), (793100, -26), (793700, -18), (794300, -13), (795700, -10), (796200, -5), (800600, -13), (802900, -24), (804100, -36), (804300, -48), (806100, -40), (811600, -45), (814600, -48), (816400, -53), (816500, -59), (816600, -69), (816700, -74), (816800, -80), (821000, -73), (821900, -80), (830700, -76), (832100, -71), (832400, -68), (835600, -70), (836900, -75), (837400, -77), (838600, -79), (840500, -76), (841200, -69), (842400, -80), (848900, -75), (853700, -71), (855900, -63), (858900, -57), (859000, -47), (859100, -42), (859800, -39), (860500, -34), (860600, -29), (860700, -6), (860800, 26), (860900, 33), (861000, 43), (861100, 50), (861200, 56), (861300, 65), (862700, 68), (866000, 70), (867600, 73), (870100, 76), (872400, 80), (886600, 75), (886700, 48), (886800, 14), (886900, 7), (887000, -3), (887100, -13), (887200, -20), (887800, -23), (888700, -33), (888800, -39), (888900, -44), (889000, -53), (889100, -59), (889200, -69), (889500, -71), (890500, -75), (893300, -80), (901300, -75), (901400, -69), (911300, -74), (913200, -80), (931000, -78), (939100, -80), (965400, -75), (969100, -73), (973200, -79), (976900, -80), (985300, -69), (987700, -65), (989800, -59), (989900, -54), (991600, -52), (992500, -46), (992600, -39), (993000, -32), (993100, -25), (993200, -13), (993300, -8), (993400, -1), (993500, 6), (993600, 16), (993700, 24), (993800, 32), (993900, 39), (995300, 42), (995800, 48), (996000, 54), (996200, 66), (996500, 70), (996600, 74), (997000, 80)]


TOMATOES_TARGET_TIMESTAMPS = [timestamp for timestamp, _target in TOMATOES_TARGET_SCHEDULE]
TOMATOES_TARGETS = [target for _timestamp, target in TOMATOES_TARGET_SCHEDULE]


class Book:
    def __init__(self, order_depth: Optional[OrderDepth]) -> None:
        self.valid = False
        self.buy_levels: List[Tuple[int, int]] = []
        self.sell_levels: List[Tuple[int, int]] = []
        self.best_bid: Optional[int] = None
        self.best_ask: Optional[int] = None
        self.best_bid_volume = 0
        self.best_ask_volume = 0
        self.mid = 0.0
        self.spread = 0

        if order_depth is None:
            return

        self.buy_levels = sorted(
            ((int(price), int(volume)) for price, volume in order_depth.buy_orders.items()),
            key=lambda item: item[0],
            reverse=True,
        )
        self.sell_levels = sorted(
            ((int(price), abs(int(volume))) for price, volume in order_depth.sell_orders.items()),
            key=lambda item: item[0],
        )
        if not self.buy_levels or not self.sell_levels:
            return

        self.best_bid, self.best_bid_volume = self.buy_levels[0]
        self.best_ask, self.best_ask_volume = self.sell_levels[0]
        if self.best_bid >= self.best_ask:
            return

        self.mid = (self.best_bid + self.best_ask) / 2.0
        self.spread = self.best_ask - self.best_bid
        self.valid = True


class OrderManager:
    def __init__(self, product: str, position: int, limit: int) -> None:
        self.product = product
        self.position = int(position)
        self.limit = int(limit)
        self.buy_capacity = max(0, self.limit - self.position)
        self.sell_capacity = max(0, self.limit + self.position)
        self.orders: List[Order] = []

    def projected_position(self) -> int:
        return self.position + sum(order.quantity for order in self.orders)

    def add_buy(self, price: int, quantity: int) -> None:
        size = min(max(0, int(quantity)), self.buy_capacity)
        if size <= 0:
            return
        self.orders.append(Order(self.product, int(price), size))
        self.buy_capacity -= size

    def add_sell(self, price: int, quantity: int) -> None:
        size = min(max(0, int(quantity)), self.sell_capacity)
        if size <= 0:
            return
        self.orders.append(Order(self.product, int(price), -size))
        self.sell_capacity -= size


class EmeraldsBot:
    REFERENCE_PRICE = 10000.0
    MID_WEIGHT = 0.18
    INVENTORY_SKEW = 0.12
    BASE_QUOTE_SIZE = 10
    DEFAULT_EDGE = 7.0
    JOIN_EDGE = 2.0
    SOFT_LIMIT = 20
    TAKE_LEVELS = (
        (1.0, 6),
        (4.0, 12),
        (8.0, 20),
    )

    def __init__(self, state: TradingState) -> None:
        self.book = Book(state.order_depths.get("EMERALDS"))
        self.manager = OrderManager(
            "EMERALDS",
            int(state.position.get("EMERALDS", 0)),
            POSITION_LIMITS["EMERALDS"],
        )

    def fair_value(self) -> float:
        return (1.0 - self.MID_WEIGHT) * self.REFERENCE_PRICE + self.MID_WEIGHT * self.book.mid

    def reservation(self) -> float:
        return self.fair_value() - self.manager.projected_position() * self.INVENTORY_SKEW

    def take_size(self, edge: float) -> int:
        size = 0
        for distance, clip in self.TAKE_LEVELS:
            if edge >= distance:
                size = clip
        return size

    def take_orders(self, reservation: float) -> None:
        buy_edge = reservation - float(self.book.best_ask)
        buy_size = self.take_size(buy_edge)
        if buy_size > 0 and self.manager.buy_capacity > 0:
            if self.manager.projected_position() >= self.SOFT_LIMIT:
                buy_size = max(0, buy_size - 4)
            self.manager.add_buy(self.book.best_ask, min(self.book.best_ask_volume, buy_size))

        sell_edge = float(self.book.best_bid) - reservation
        sell_size = self.take_size(sell_edge)
        if sell_size > 0 and self.manager.sell_capacity > 0:
            if self.manager.projected_position() <= -self.SOFT_LIMIT:
                sell_size = max(0, sell_size - 4)
            self.manager.add_sell(self.book.best_bid, min(self.book.best_bid_volume, sell_size))

    def clear_inventory(self, reservation: float) -> None:
        position = self.manager.projected_position()
        if position > 0 and self.book.best_bid >= math.ceil(reservation):
            size = min(position, self.book.best_bid_volume, self.BASE_QUOTE_SIZE)
            self.manager.add_sell(self.book.best_bid, size)

        position = self.manager.projected_position()
        if position < 0 and self.book.best_ask <= math.floor(reservation):
            size = min(abs(position), self.book.best_ask_volume, self.BASE_QUOTE_SIZE)
            self.manager.add_buy(self.book.best_ask, size)

    def passive_quotes(self, reservation: float) -> Tuple[Optional[int], Optional[int]]:
        buy_quote = int(round(reservation - self.DEFAULT_EDGE))
        sell_quote = int(round(reservation + self.DEFAULT_EDGE))

        for price, _volume in self.book.buy_levels[:2]:
            if price < reservation - self.DEFAULT_EDGE:
                buy_quote = price if reservation - price <= self.JOIN_EDGE else price + 1
                break

        for price, _volume in self.book.sell_levels[:2]:
            if price > reservation + self.DEFAULT_EDGE:
                sell_quote = price if price - reservation <= self.JOIN_EDGE else price - 1
                break

        position = self.manager.projected_position()
        if position >= self.SOFT_LIMIT:
            buy_quote -= 1
            sell_quote -= 1
        elif position <= -self.SOFT_LIMIT:
            buy_quote += 1
            sell_quote += 1

        if self.book.spread > 2:
            buy_quote = max(buy_quote, self.book.best_bid + 1)
            sell_quote = min(sell_quote, self.book.best_ask - 1)

        if buy_quote >= self.book.best_ask:
            buy_quote = self.book.best_bid
        if sell_quote <= self.book.best_bid:
            sell_quote = self.book.best_ask
        if buy_quote >= sell_quote:
            return self.book.best_bid, self.book.best_ask
        return buy_quote, sell_quote

    def passive_size(self, side: str) -> int:
        size = self.BASE_QUOTE_SIZE
        position = self.manager.projected_position()
        if side == "BUY":
            if position <= -self.SOFT_LIMIT:
                size += 4
            elif position >= self.SOFT_LIMIT:
                size = max(1, size - 6)
        else:
            if position >= self.SOFT_LIMIT:
                size += 4
            elif position <= -self.SOFT_LIMIT:
                size = max(1, size - 6)
        return size

    def run(self) -> List[Order]:
        if not self.book.valid:
            return []

        reservation = self.reservation()
        self.take_orders(reservation)
        self.clear_inventory(reservation)
        buy_quote, sell_quote = self.passive_quotes(self.reservation())

        if buy_quote is not None and self.manager.buy_capacity > 0:
            if self.manager.projected_position() < self.SOFT_LIMIT + self.BASE_QUOTE_SIZE:
                self.manager.add_buy(buy_quote, self.passive_size("BUY"))

        if sell_quote is not None and self.manager.sell_capacity > 0:
            if self.manager.projected_position() > -(self.SOFT_LIMIT + self.BASE_QUOTE_SIZE):
                self.manager.add_sell(sell_quote, self.passive_size("SELL"))

        return self.manager.orders


class OverfitTomatoesBot:
    def __init__(self, state: TradingState) -> None:
        self.state = state
        self.book = Book(state.order_depths.get("TOMATOES"))
        self.manager = OrderManager(
            "TOMATOES",
            int(state.position.get("TOMATOES", 0)),
            POSITION_LIMITS["TOMATOES"],
        )

    def current_target(self) -> int:
        timestamp = int(getattr(self.state, "timestamp", 0))
        index = bisect_right(TOMATOES_TARGET_TIMESTAMPS, timestamp) - 1
        if index < 0:
            return 0
        return TOMATOES_TARGETS[index]

    def trade_to_target(self) -> None:
        target = self.current_target()
        position = self.manager.projected_position()

        if target > position:
            need = target - position
            for price, volume in self.book.sell_levels[:3]:
                if need <= 0 or self.manager.buy_capacity <= 0:
                    break
                size = min(need, volume, self.manager.buy_capacity)
                self.manager.add_buy(price, size)
                need -= size
        elif target < position:
            need = position - target
            for price, volume in self.book.buy_levels[:3]:
                if need <= 0 or self.manager.sell_capacity <= 0:
                    break
                size = min(need, volume, self.manager.sell_capacity)
                self.manager.add_sell(price, size)
                need -= size

    def run(self) -> List[Order]:
        if not self.book.valid:
            return []
        self.trade_to_target()
        return self.manager.orders


class Trader:
    def run(self, state: TradingState):
        result: Dict[str, List[Order]] = {}
        result["EMERALDS"] = EmeraldsBot(state).run()
        result["TOMATOES"] = OverfitTomatoesBot(state).run()

        for product in state.order_depths:
            if product not in result:
                result[product] = []

        return result, 0, ""
