
from __future__ import annotations

import json
import math
from typing import Dict, List, Optional, Tuple

try:
    from datamodel import Order, OrderDepth, TradingState
except ModuleNotFoundError:
    from trader_factory.core.datamodel import Order, OrderDepth, TradingState


HYDRO = "HYDROGEL_PACK"
VEV = "VELVETFRUIT_EXTRACT"
VOUCHERS = [
    "VEV_4000", "VEV_4500", "VEV_5000", "VEV_5100", "VEV_5200",
    "VEV_5300", "VEV_5400", "VEV_5500", "VEV_6000", "VEV_6500",
]
STRIKE = {p: int(p.split("_")[1]) for p in VOUCHERS}
LIMITS = {HYDRO: 200, VEV: 200, **{p: 300 for p in VOUCHERS}}
TTE_DAYS = 5.0

HYDRO_CFG = dict(anchor=10000.0, anchor_w=0.52, stable_w=0.30, micro_w=0.18, imbalance_w=0.85,
                 trend_alpha=0.10, gap_alpha=0.20, trend_entry=0.90, trend_unwind=0.35,
                 soft_limit=90, hard_limit=145, take_size=18, quote_size=16, clear_size=28,
                 inv_skew=7.0, cooldown_bars=5)
VEV_CFG = dict(anchor=5250.0, anchor_w=0.44, stable_w=0.34, micro_w=0.22, imbalance_w=0.80,
               take_size=18, quote_size=16, clear_size=22, inv_skew=5.5, alpha_cap=40,
               hedge_deadband=20, soft_limit=80)
OPT_CFG = dict(iv_alpha=0.18, min_iv=0.05, max_iv=3.0, pair_entry=0.085, pair_exit=0.020,
               outright_entry=0.17, shock_resid=0.11, pair_count_normal=3, pair_count_shock=5,
               max_pos_base=90, max_pos_paired=120, middle_cap=210, strip_delta_soft=140,
               strip_delta_hard=185)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def ema(prev: Optional[float], x: float, alpha: float) -> float:
    return x if prev is None else (1 - alpha) * prev + alpha * x


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bs_call_price(spot: float, strike: float, t_days: float, vol: float) -> float:
    if spot <= 0 or strike <= 0 or t_days <= 0 or vol <= 0:
        return max(0.0, spot - strike)
    t = t_days / 365.0
    srt = vol * math.sqrt(t)
    if srt <= 0:
        return max(0.0, spot - strike)
    d1 = (math.log(spot / strike) + 0.5 * vol * vol * t) / srt
    d2 = d1 - srt
    return spot * norm_cdf(d1) - strike * norm_cdf(d2)


def bs_delta(spot: float, strike: float, t_days: float, vol: float) -> float:
    if spot <= 0 or strike <= 0 or t_days <= 0 or vol <= 0:
        return 1.0 if spot > strike else 0.0
    t = t_days / 365.0
    srt = vol * math.sqrt(t)
    if srt <= 0:
        return 1.0 if spot > strike else 0.0
    d1 = (math.log(spot / strike) + 0.5 * vol * vol * t) / srt
    return norm_cdf(d1)


def implied_vol_call(price: float, spot: float, strike: float, t_days: float) -> Optional[float]:
    intrinsic = max(0.0, spot - strike)
    if price < intrinsic - 1e-9:
        return None
    lo, hi = OPT_CFG["min_iv"], OPT_CFG["max_iv"]
    plo = bs_call_price(spot, strike, t_days, lo)
    phi = bs_call_price(spot, strike, t_days, hi)
    if price < plo - 1e-6 or price > phi + 1e-6:
        return None
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        pm = bs_call_price(spot, strike, t_days, mid)
        if pm > price:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def solve_3x3(A: List[List[float]], b: List[float]) -> Optional[List[float]]:
    M = [row[:] + [rhs] for row, rhs in zip(A, b)]
    for col in range(3):
        piv = max(range(col, 3), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-12:
            return None
        M[col], M[piv] = M[piv], M[col]
        fac = M[col][col]
        for j in range(col, 4):
            M[col][j] /= fac
        for r in range(3):
            if r == col:
                continue
            fac = M[r][col]
            for j in range(col, 4):
                M[r][j] -= fac * M[col][j]
    return [M[i][3] for i in range(3)]


def weighted_quad_fit(xs: List[float], ys: List[float], ws: List[float]) -> Optional[Tuple[float, float, float]]:
    if len(xs) < 3:
        return None
    s0 = s1 = s2 = s3 = s4 = t0 = t1 = t2 = 0.0
    for x, y, w in zip(xs, ys, ws):
        s0 += w
        s1 += w * x
        s2 += w * x * x
        s3 += w * x * x * x
        s4 += w * x * x * x * x
        t0 += w * y
        t1 += w * x * y
        t2 += w * x * x * y
    sol = solve_3x3([[s0, s1, s2], [s1, s2, s3], [s2, s3, s4]], [t0, t1, t2])
    return None if sol is None else (sol[0], sol[1], sol[2])


class Book:
    def __init__(self, depth: Optional[OrderDepth]):
        self.valid = False
        self.buy = []
        self.sell = []
        self.best_bid = self.best_ask = self.bb_vol = self.ba_vol = 0
        self.spread = self.mid = self.micro = self.imb = 0.0
        if depth is None:
            return
        self.buy = sorted(((int(p), int(v)) for p, v in depth.buy_orders.items()), reverse=True)
        self.sell = sorted(((int(p), abs(int(v))) for p, v in depth.sell_orders.items()))
        if not self.buy or not self.sell:
            return
        self.best_bid, self.bb_vol = self.buy[0]
        self.best_ask, self.ba_vol = self.sell[0]
        if self.best_bid >= self.best_ask:
            return
        self.spread = float(self.best_ask - self.best_bid)
        self.mid = 0.5 * (self.best_bid + self.best_ask)
        tot = self.bb_vol + self.ba_vol
        self.micro = ((self.best_ask * self.bb_vol) + (self.best_bid * self.ba_vol)) / max(1, tot)
        self.imb = (self.bb_vol - self.ba_vol) / max(1, tot)
        self.valid = True


def thick_mid(book: Book, levels: int = 3) -> float:
    bids = book.buy[:levels]
    asks = book.sell[:levels]
    if not bids or not asks:
        return book.mid
    bv = sum(v for _, v in bids)
    av = sum(v for _, v in asks)
    if bv <= 0 or av <= 0:
        return book.mid
    return 0.5 * (sum(px * v for px, v in bids) / bv + sum(px * v for px, v in asks) / av)


def wall_mid(book: Book, levels: int = 3) -> float:
    bids = book.buy[:levels]
    asks = book.sell[:levels]
    if not bids or not asks:
        return book.mid
    wb = max(bids, key=lambda x: (x[1], x[0]))[0]
    wa = min(asks, key=lambda x: (-x[1], x[0]))[0]
    return 0.5 * (wb + wa)


def stable_mid(book: Book) -> float:
    return (book.mid + thick_mid(book, 3) + wall_mid(book, 3)) / 3.0


class OrderManager:
    def __init__(self, product: str, pos: int, limit: int):
        self.product = product
        self.pos = int(pos)
        self.limit = int(limit)
        self.orders: List[Order] = []
        self.buy_cap = max(0, self.limit - self.pos)
        self.sell_cap = max(0, self.limit + self.pos)

    def projected(self) -> int:
        return self.pos + sum(o.quantity for o in self.orders)

    def buy(self, px: int, qty: int):
        q = max(0, min(int(qty), self.buy_cap))
        if q > 0:
            self.orders.append(Order(self.product, int(px), q))
            self.buy_cap -= q

    def sell(self, px: int, qty: int):
        q = max(0, min(int(qty), self.sell_cap))
        if q > 0:
            self.orders.append(Order(self.product, int(px), -q))
            self.sell_cap -= q


class Trader:
    def _load(self, raw: str) -> dict:
        if not raw:
            return {}
        try:
            obj = json.loads(raw)
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}

    def _save(self, mem: dict) -> str:
        return json.dumps(mem, separators=(",", ":"))

    def _reset_day(self, mem: dict, ts: int):
        if mem.get("_last_ts", -1) > ts:
            mem.clear()
        mem["_last_ts"] = int(ts)

    def _fair(self, book: Book, cfg: dict, overlay: float = 0.0) -> float:
        if not book.valid:
            return cfg["anchor"]
        s_mid = stable_mid(book)
        spread_scale = max(1.0, 0.5 * book.spread)
        return cfg["anchor_w"] * cfg["anchor"] + cfg["stable_w"] * s_mid + cfg["micro_w"] * book.micro + cfg["imbalance_w"] * book.imb * spread_scale + overlay

    # ---------- Hydro ----------
    def _hydro_state(self, mem: dict, book: Book, fair: float) -> dict:
        st = mem.setdefault("hydro", {})
        prev_mid = st.get("prev_mid")
        dmid = 0.0 if prev_mid is None else book.mid - prev_mid
        trend = ema(st.get("trend"), dmid, HYDRO_CFG["trend_alpha"])
        gap = fair - book.mid
        gap_ema = ema(st.get("gap"), gap, HYDRO_CFG["gap_alpha"])
        cooldown = max(0, int(st.get("cooldown", 0)) - 1)
        cool_side = int(st.get("cool_side", 0)) if cooldown > 0 else 0
        score = 0.65 * trend / max(1.0, 0.35 * book.spread) + 0.35 * gap_ema / max(1.0, 0.50 * book.spread)
        if score > HYDRO_CFG["trend_entry"]:
            state = "UP"
        elif score < -HYDRO_CFG["trend_entry"]:
            state = "DOWN"
        elif score > HYDRO_CFG["trend_unwind"]:
            state = "UP_UNWIND"
        elif score < -HYDRO_CFG["trend_unwind"]:
            state = "DOWN_UNWIND"
        else:
            state = "NEUTRAL"
        st.update(prev_mid=book.mid, trend=trend, gap=gap_ema, score=score, state=state, cooldown=cooldown, cool_side=cool_side)
        return st

    def _hydro_target(self, pos: int, st: dict, progress: float) -> int:
        score = float(st["score"])
        state = st["state"]
        if state in ("UP", "DOWN"):
            cap = 140 if abs(score) < 2.2 else 180
        elif "UNWIND" in state:
            cap = 50
        else:
            cap = 20
        if progress > 0.80:
            cap = int(0.75 * cap)
        if progress > 0.92:
            cap = min(cap, 40)
        target = int(round(cap * math.tanh(score)))
        if pos * target < 0 and abs(pos) > 60:
            target = 0
        if st.get("cool_side", 0) != 0 and target * st["cool_side"] > 0:
            target = 0
        return target

    def _trade_hydro(self, state: TradingState, mem: dict) -> List[Order]:
        book = Book(state.order_depths.get(HYDRO))
        if not book.valid:
            return []
        pos = int(state.position.get(HYDRO, 0))
        mgr = OrderManager(HYDRO, pos, LIMITS[HYDRO])
        progress = clamp(int(getattr(state, "timestamp", 0)) / 99900.0, 0.0, 1.0)
        fair = self._fair(book, HYDRO_CFG)
        st = self._hydro_state(mem, book, fair)
        target = self._hydro_target(pos, st, progress)
        rel = mgr.projected() - target
        soft, hard = HYDRO_CFG["soft_limit"], HYDRO_CFG["hard_limit"]
        score = float(st["score"])

        # take
        if score > 0.95 and mgr.projected() < target and mgr.projected() < hard:
            mgr.buy(book.best_ask, min(HYDRO_CFG["take_size"], book.ba_vol, target - mgr.projected()))
        elif score < -0.95 and mgr.projected() > target and mgr.projected() > -hard:
            mgr.sell(book.best_bid, min(HYDRO_CFG["take_size"], book.bb_vol, mgr.projected() - target))

        # clear
        abs_danger = abs(mgr.projected()) >= 150
        if rel > soft or (abs_danger and mgr.projected() > 0):
            qty = HYDRO_CFG["clear_size"] if abs(rel) > hard or abs_danger else HYDRO_CFG["take_size"]
            mgr.sell(book.best_bid, min(qty, mgr.sell_cap))
            if rel > hard or abs_danger:
                st["cooldown"], st["cool_side"] = HYDRO_CFG["cooldown_bars"], 1
        elif rel < -soft or (abs_danger and mgr.projected() < 0):
            qty = HYDRO_CFG["clear_size"] if abs(rel) > hard or abs_danger else HYDRO_CFG["take_size"]
            mgr.buy(book.best_ask, min(qty, mgr.buy_cap))
            if rel < -hard or abs_danger:
                st["cooldown"], st["cool_side"] = HYDRO_CFG["cooldown_bars"], -1

        # make
        reservation = fair - HYDRO_CFG["inv_skew"] * (mgr.projected() / LIMITS[HYDRO])
        bid_edge = 2.0 if abs(mgr.projected()) < 120 else 4.0
        ask_edge = 2.0 if abs(mgr.projected()) < 120 else 4.0
        if mgr.projected() > 130:
            bid_edge += 3.0
            ask_edge -= 0.5
        elif mgr.projected() < -130:
            ask_edge += 3.0
            bid_edge -= 0.5
        bid_px = min(book.best_ask - 1, max(book.best_bid, int(math.floor(reservation - bid_edge))))
        ask_px = max(book.best_bid + 1, min(book.best_ask, int(math.ceil(reservation + ask_edge))))
        if mgr.projected() < 140 and not (st.get("cool_side", 0) == 1):
            mgr.buy(bid_px, HYDRO_CFG["quote_size"])
        if mgr.projected() > -140 and not (st.get("cool_side", 0) == -1):
            mgr.sell(ask_px, HYDRO_CFG["quote_size"])
        return mgr.orders

    # ---------- voucher surface ----------
    def _repair_monotone_convex(self, mids: Dict[str, float], spot: float) -> Dict[str, float]:
        ordered = sorted(mids.items(), key=lambda kv: STRIKE[kv[0]])
        vals, prev = {}, None
        for sym, px in ordered:
            intrinsic = max(0.0, spot - STRIKE[sym])
            v = max(px, intrinsic)
            if prev is not None:
                v = min(v, prev)
            vals[sym] = v
            prev = v
        syms = [s for s, _ in ordered]
        for _ in range(2):
            for i in range(1, len(syms) - 1):
                l, m, r = syms[i - 1], syms[i], syms[i + 1]
                if vals[m] < 0.5 * (vals[l] + vals[r]):
                    vals[m] = 0.5 * (vals[l] + vals[r])
        return vals

    def _fit_surface(self, vev_mid: float, mids: Dict[str, float], mem: dict) -> dict:
        repaired = self._repair_monotone_convex(mids, vev_mid)
        local = mem.setdefault("vev_local_iv", {})
        xs, ys, ws = [], [], []
        for sym in VOUCHERS:
            px = repaired.get(sym)
            if px is None:
                continue
            iv = implied_vol_call(px, vev_mid, STRIKE[sym], TTE_DAYS)
            if iv is None:
                continue
            x = math.log(max(1e-9, STRIKE[sym] / max(1e-9, vev_mid)))
            xs.append(x); ys.append(iv); ws.append(1.0 / (0.4 + abs(x)))
            local[sym] = ema(local.get(sym), iv, OPT_CFG["iv_alpha"])
        fit = weighted_quad_fit(xs, ys, ws)
        conf = clamp(len(xs) / 7.0, 0.0, 1.0)
        if fit is None:
            a, b, c = (sorted(ys)[len(ys) // 2], 0.0, 0.0) if ys else (0.35, 0.0, 0.0)
        else:
            a, b, c = fit

        fair_mid_iv, fair_bid_iv, fair_ask_iv, resid = {}, {}, {}, {}
        abs_resids = []
        cheap, rich = [], []
        for sym in VOUCHERS:
            px = repaired.get(sym)
            if px is None:
                continue
            x = math.log(max(1e-9, STRIKE[sym] / max(1e-9, vev_mid)))
            struct = clamp(a + b * x + c * x * x, OPT_CFG["min_iv"], OPT_CFG["max_iv"])
            loc = local.get(sym, struct)
            w_struct = 0.75 if conf > 0.55 else 0.55
            hybrid = w_struct * struct + (1 - w_struct) * loc
            mkt_iv = implied_vol_call(px, vev_mid, STRIKE[sym], TTE_DAYS)
            if mkt_iv is None:
                continue
            fair_mid_iv[sym] = hybrid
            fair_bid_iv[sym] = max(OPT_CFG["min_iv"], hybrid - 0.015)
            fair_ask_iv[sym] = min(OPT_CFG["max_iv"], hybrid + 0.015)
            r = mkt_iv - hybrid
            resid[sym] = r
            abs_resids.append(abs(r))
            if r < 0:
                cheap.append((r, sym))
            else:
                rich.append((r, sym))

        cheap.sort(key=lambda t: t[0]); rich.sort(key=lambda t: -t[0])
        avg_abs = sum(abs_resids) / max(1, len(abs_resids))
        pair_agree = 0
        for i in range(len(VOUCHERS) - 1):
            r1, r2 = resid.get(VOUCHERS[i]), resid.get(VOUCHERS[i + 1])
            if r1 is not None and r2 is not None and r1 * r2 > 0:
                pair_agree += 1
        prev_avg = mem.get("avg_abs_resid_prev")
        comp = 0.0 if prev_avg is None else avg_abs - prev_avg
        mem["avg_abs_resid_prev"] = avg_abs
        broad = avg_abs > OPT_CFG["shock_resid"] and pair_agree >= 2
        return dict(fair_mid_iv=fair_mid_iv, fair_bid_iv=fair_bid_iv, fair_ask_iv=fair_ask_iv,
                    residuals=resid, avg_abs_resid=avg_abs, pair_agreement=pair_agree,
                    broad_dislocation=broad, resid_compression=comp,
                    cheap=[s for _, s in cheap[:4]], rich=[s for _, s in rich[:4]], fit_conf=conf)

    def _strip_ctx(self, state: TradingState, vev_mid: float, surf: dict) -> dict:
        pos = state.position
        strip_delta = 0.0
        middle_gross = 0
        for sym in VOUCHERS:
            iv = surf["fair_mid_iv"].get(sym)
            if iv is None:
                continue
            p = int(pos.get(sym, 0))
            strip_delta += p * bs_delta(vev_mid, STRIKE[sym], TTE_DAYS, iv)
            if 5100 <= STRIKE[sym] <= 5400:
                middle_gross += abs(p)
        avg_abs = surf["avg_abs_resid"]
        broad = surf["broad_dislocation"]
        comp = surf["resid_compression"]
        hedge_ratio = 0.75 if broad else (0.50 if avg_abs > 0.07 else 0.25)
        if comp < -0.01:
            hedge_ratio *= 0.70
        hedge_target = 0 if abs(strip_delta) < VEV_CFG["hedge_deadband"] else int(round(clamp(-hedge_ratio * strip_delta, -100, 100)))
        return dict(strip_delta=strip_delta, avg_abs_resid=avg_abs, pair_agreement=surf["pair_agreement"],
                    broad_dislocation=broad, resid_compression=comp, middle_gross=middle_gross,
                    hedge_ratio=hedge_ratio, target_velvet_pos=hedge_target)

    def _trade_vev(self, state: TradingState, strip: dict) -> List[Order]:
        book = Book(state.order_depths.get(VEV))
        if not book.valid:
            return []
        pos = int(state.position.get(VEV, 0))
        mgr = OrderManager(VEV, pos, LIMITS[VEV])
        fair = self._fair(book, VEV_CFG)
        gap = (fair - book.mid) / max(1.0, 0.5 * book.spread)
        alpha_cap = 0 if abs(strip["strip_delta"]) >= 60 else (12 if strip["broad_dislocation"] else VEV_CFG["alpha_cap"])
        alpha_target = int(round(clamp(24 * math.tanh(0.8 * gap), -alpha_cap, alpha_cap)))
        final_target = int(clamp(int(strip["target_velvet_pos"]) + alpha_target, -100, 100))
        rel = mgr.projected() - final_target
        if rel > VEV_CFG["soft_limit"]:
            mgr.sell(book.best_bid, min(VEV_CFG["clear_size"], mgr.sell_cap))
        elif rel < -VEV_CFG["soft_limit"]:
            mgr.buy(book.best_ask, min(VEV_CFG["clear_size"], mgr.buy_cap))
        else:
            reservation = fair - VEV_CFG["inv_skew"] * (mgr.projected() - final_target) / LIMITS[VEV]
            if reservation - book.best_ask >= 1.0 and mgr.projected() < final_target:
                mgr.buy(book.best_ask, min(VEV_CFG["take_size"], book.ba_vol, final_target - mgr.projected()))
            if book.best_bid - reservation >= 1.0 and mgr.projected() > final_target:
                mgr.sell(book.best_bid, min(VEV_CFG["take_size"], book.bb_vol, mgr.projected() - final_target))
        reservation = fair - VEV_CFG["inv_skew"] * (mgr.projected() - final_target) / LIMITS[VEV]
        bid_edge = 2.0
        ask_edge = 2.0
        if strip["resid_compression"] < -0.01:
            if mgr.projected() < 0:
                bid_edge -= 0.3; ask_edge += 0.6
            elif mgr.projected() > 0:
                ask_edge -= 0.3; bid_edge += 0.6
        bid_px = min(book.best_ask - 1, max(book.best_bid, int(math.floor(reservation - bid_edge))))
        ask_px = max(book.best_bid + 1, min(book.best_ask, int(math.ceil(reservation + ask_edge))))
        mgr.buy(bid_px, VEV_CFG["quote_size"])
        mgr.sell(ask_px, VEV_CFG["quote_size"])
        return mgr.orders

    def _active_cap(self, sym: str, strip: dict, paired: bool) -> int:
        cap = OPT_CFG["max_pos_paired"] if paired else OPT_CFG["max_pos_base"]
        if 5200 <= STRIKE[sym] <= 5500 and not paired:
            cap = min(cap, 45)
        if strip["broad_dislocation"] and paired:
            cap += 20
        return cap

    def _trade_vouchers(self, state: TradingState, vev_mid: float, surf: dict, strip: dict) -> Dict[str, List[Order]]:
        out = {}
        pos = state.position
        resid = surf["residuals"]
        cheap = surf["cheap"]
        rich = surf["rich"]
        pairs = []
        for c in cheap:
            for r in rich:
                if c == r:
                    continue
                dk = abs(STRIKE[c] - STRIKE[r])
                if dk > 1000:
                    continue
                spread = resid.get(r, 0.0) - resid.get(c, 0.0)
                if spread > OPT_CFG["pair_entry"]:
                    pairs.append((c, r, spread + (0.02 if dk <= 100 else 0.0)))
        pairs.sort(key=lambda x: -x[2])
        max_pairs = OPT_CFG["pair_count_shock"] if strip["broad_dislocation"] else OPT_CFG["pair_count_normal"]
        used = set()
        for c, r, sc in pairs:
            if len(used) >= 2 * max_pairs:
                break
            if c in used or r in used:
                continue
            used.add(c); used.add(r)
            for sym in (c, r):
                out.setdefault(sym, [])
            cb, rb = Book(state.order_depths.get(c)), Book(state.order_depths.get(r))
            if not cb.valid or not rb.valid:
                continue
            cm, rm = OrderManager(c, int(pos.get(c, 0)), LIMITS[c]), OrderManager(r, int(pos.get(r, 0)), LIMITS[r])
            intensity = clamp((sc - OPT_CFG["pair_entry"]) / 0.12, 0.0, 1.0)
            size = 14 + int(round(16 * intensity)) + (4 if strip["broad_dislocation"] else 0)
            ct, rt = min(self._active_cap(c, strip, True), int(pos.get(c, 0)) + size), max(-self._active_cap(r, strip, True), int(pos.get(r, 0)) - size)
            civ, riv = implied_vol_call(cb.mid, vev_mid, STRIKE[c], TTE_DAYS), implied_vol_call(rb.mid, vev_mid, STRIKE[r], TTE_DAYS)
            if civ is not None and civ < surf["fair_bid_iv"].get(c, 9e9) and cm.projected() < ct:
                cm.buy(cb.best_ask, min(size, cb.ba_vol, ct - cm.projected()))
            if riv is not None and riv > surf["fair_ask_iv"].get(r, -9e9) and rm.projected() > rt:
                rm.sell(rb.best_bid, min(size, rb.bb_vol, rm.projected() - rt))
            fc = bs_call_price(vev_mid, STRIKE[c], TTE_DAYS, surf["fair_mid_iv"][c])
            fr = bs_call_price(vev_mid, STRIKE[r], TTE_DAYS, surf["fair_mid_iv"][r])
            cbid = min(cb.best_ask - 1, max(cb.best_bid, int(math.floor(fc - 1))))
            rask = max(rb.best_bid + 1, min(rb.best_ask, int(math.ceil(fr + 1))))
            if cm.projected() < ct:
                cm.buy(cbid, min(10, ct - cm.projected()))
            if rm.projected() > rt:
                rm.sell(rask, min(10, rm.projected() - rt))
            out[c] = cm.orders; out[r] = rm.orders

        for sym in VOUCHERS:
            if sym in out:
                continue
            book = Book(state.order_depths.get(sym))
            if not book.valid:
                out[sym] = []
                continue
            mgr = OrderManager(sym, int(pos.get(sym, 0)), LIMITS[sym])
            r = resid.get(sym)
            if r is None or abs(r) < OPT_CFG["outright_entry"]:
                out[sym] = []
                continue
            if strip["middle_gross"] > OPT_CFG["middle_cap"] and 5100 <= STRIKE[sym] <= 5400:
                out[sym] = []
                continue
            cap = self._active_cap(sym, strip, False)
            fair_p = bs_call_price(vev_mid, STRIKE[sym], TTE_DAYS, surf["fair_mid_iv"][sym])
            miv = implied_vol_call(book.mid, vev_mid, STRIKE[sym], TTE_DAYS)
            if miv is None:
                out[sym] = []
                continue
            if r < 0 and miv < surf["fair_bid_iv"].get(sym, 9e9):
                target = cap
                mgr.buy(book.best_ask, min(8, book.ba_vol, target - mgr.projected()))
                bid = min(book.best_ask - 1, max(book.best_bid, int(math.floor(fair_p - 1))))
                if mgr.projected() < target:
                    mgr.buy(bid, min(6, target - mgr.projected()))
            elif r > 0 and miv > surf["fair_ask_iv"].get(sym, -9e9):
                target = -cap
                mgr.sell(book.best_bid, min(8, book.bb_vol, mgr.projected() - target))
                ask = max(book.best_bid + 1, min(book.best_ask, int(math.ceil(fair_p + 1))))
                if mgr.projected() > target:
                    mgr.sell(ask, min(6, mgr.projected() - target))
            out[sym] = mgr.orders
        return out

    def run(self, state: TradingState):
        mem = self._load(getattr(state, "traderData", ""))
        ts = int(getattr(state, "timestamp", 0))
        self._reset_day(mem, ts)
        result: Dict[str, List[Order]] = {}

        if HYDRO in state.order_depths:
            result[HYDRO] = self._trade_hydro(state, mem)

        vev_book = Book(state.order_depths.get(VEV))
        if vev_book.valid:
            mids = {}
            for sym in VOUCHERS:
                b = Book(state.order_depths.get(sym))
                if b.valid:
                    mids[sym] = b.mid
            surf = self._fit_surface(vev_book.mid, mids, mem)
            strip = self._strip_ctx(state, vev_book.mid, surf)
            result[VEV] = self._trade_vev(state, strip)
            result.update(self._trade_vouchers(state, vev_book.mid, surf, strip))
        else:
            result.setdefault(VEV, [])
            for sym in VOUCHERS:
                result.setdefault(sym, [])

        return result, 0, self._save(mem)
