# Round 3 Advisor Notes — Algorithmic Trading Focus

## What the advisor is really telling us

The advisor notes are not mainly saying “use Black-Scholes because options exist.”
They are saying:

1. **Translate voucher prices into implied volatility (IV)** instead of reasoning from price alone.
2. **Use moneyness as the x-axis** and IV as the y-axis.
3. **Look for structure first, mispricings second.**
4. **Only then decide trade direction and size.**
5. **Volume must scale with conviction, not with hope.**

So the correct workflow is:

```text
Underlying fair -> IV per strike -> IV vs moneyness structure -> outlier detection -> trade sizing
```

---

## 1. Required baseline definitions

### Underlying
Use `VELVETFRUIT_EXTRACT` as the underlying for all `VEV_*` vouchers.
Do not use raw last trade as the underlying input to Black-Scholes.
Use a **robust fair** for the underlying, for example:

```text
underlying_fair = blend(anchor, stable_mid, microprice, last_good_fair)
```

A robust default is:
- stable/market-maker mid when the book is healthy
- guarded / median fair when the book is thin or distorted

### Strike
For each voucher:
- `VEV_4000` -> strike `K = 4000`
- `VEV_4500` -> strike `K = 4500`
- etc.

### Time to expiry
For this round:
- the vouchers have **5 days to expiry** at the start of the round

Use one **consistent time convention** in code.
For a first implementation, using “days” consistently is more important than annualizing perfectly.

### Moneyness
The advisor is clearly pointing you toward a moneyness-based surface view.
Good choices:

```text
log_moneyness = ln(S / K)
```

or simpler:

```text
relative_moneyness = (S - K) / S
```

For fitting and plotting, log-moneyness is usually cleaner.

---

## 2. Core algorithmic workflow

## Step A — build a fair for the underlying
Before touching vouchers, estimate a fair for `VELVETFRUIT_EXTRACT`.

Suggested order:
1. compute raw mid
2. compute stable / popular / wall mid
3. compute microprice
4. detect book health
5. choose fair based on book health

Example logic:

```text
if book_health high:
    S = weighted(stable_mid, microprice)
else:
    S = weighted(anchor, stable_mid, last_good_fair)
```

The quality of `S` matters more than anything else in the voucher engine.

## Step B — compute market IV for each strike
For every voucher at every step:
1. take the observed voucher mid or guarded quote fair
2. invert Black-Scholes to get implied vol
3. discard unusable points:
   - price below intrinsic value
   - absurdly low liquidity
   - inversion failures

Store:
- strike
- voucher fair
- implied vol
- moneyness
- spread
- depth

## Step C — fit the IV surface / smile
The advisor is telling you to look at **structure**.
That means fitting a smooth function to IV vs moneyness.

Good first choices:
- quadratic fit in moneyness
- cubic fit with clipping
- piecewise smooth spline if stable

For v1, use:

```text
iv_fitted = a + b * m + c * m^2
```

where `m` is log-moneyness.

Weight the fit by confidence:
- tighter spread -> higher weight
- more depth -> higher weight
- strikes near the money -> more reliable IV

## Step D — reprice all vouchers from the fitted smile
For each strike:
1. get fitted IV
2. compute Black-Scholes fair
3. compare market price with fitted fair

```text
residual = market_price - fitted_fair
```

This residual is your real trading signal.

## Step E — classify the residual
Do not trade every residual.
First classify it:

```text
small noise
moderate deviation
large deviation
surface break / anomaly
```

Suggested filters:
- spread-adjusted residual
- residual z-score across strikes
- require neighboring strikes to support the structure

---

## 3. What patterns to look for

The advisor notes point to three main pattern families.

## Pattern 1 — smooth smile with one obvious outlier
This is the cleanest trade.

Example:
- all strikes fit a stable smile
- one strike has much higher IV than neighbors
- or much lower IV than neighbors

Interpretation:
- that strike may be mispriced relative to the surface

Action:
- sell rich outlier
- buy cheap outlier
- preferably hedge or pair with neighboring strikes

## Pattern 2 — skew change across moneyness
If IV is systematically higher for OTM or ITM strikes, the market is embedding a skew.

Interpretation:
- that skew may be rational
- or temporarily exaggerated / understated

Action:
- compare current skew with recent skew
- if one wing is too rich relative to history, lean against it

## Pattern 3 — uneven term/shape reaction after underlying move
If the underlying moves and some strikes reprice their IV / option fair slower than others:

Interpretation:
- lagged repricing
- local dislocation

Action:
- trade the lagging strike(s)
- optionally hedge delta in `VELVETFRUIT_EXTRACT`

---

## 4. How to turn the structure into trades

### A. Outright residual trade
Use only when the residual is very strong and the strike is liquid.

```text
if fitted_fair - ask >> costs:
    buy
if bid - fitted_fair >> costs:
    sell
```

### B. Relative-value spread trade
This should be the preferred mode whenever possible.

Examples:
- buy cheap strike, sell neighboring rich strike
- sell rich middle strike, buy surrounding strikes if convexity is broken

Why better:
- reduces directional exposure
- reduces pure underlying risk
- isolates surface mispricing

### C. Delta-hedged residual trade
If a strike is mispriced but you do not want the underlying exposure:
- trade the voucher
- hedge some delta with `VELVETFRUIT_EXTRACT`

Good for:
- rich/cheap IV views
- cross-surface anomalies

### D. Gamma-scalp style reaction
If vouchers underreact to a move in VEV:
- buy options that should reprice higher
- or sell those that should reprice lower
- optionally trade the underlying against them later

---

## 5. Position sizing guidance from the advisor notes

The advisor is very clear here.

### Size should depend on:
- residual magnitude
- surface consistency
- strike liquidity
- confidence in underlying fair
- hedgeability

### Size should NOT depend on:
- how large the theoretical edge looks in isolation
- how tempting one strike looks without surface confirmation
- how much unused position limit you still have

Use a conviction score like:

```text
conviction =
    0.30 * residual_strength
  + 0.20 * spread_quality
  + 0.20 * depth_quality
  + 0.15 * surface_consistency
  + 0.15 * underlying_fair_confidence
```

Map that into size:

```text
low conviction -> tiny or no trade
medium conviction -> standard size
high conviction -> large size
extreme conviction -> max allowed only if hedged or paired
```

### Practical rule
Never let one voucher become a huge outright bet just because it looks cheap.
That was exactly the kind of failure mode the advisor is warning against.

---

## 6. Black-Scholes implementation notes

### Use BS as an anchor, not as truth
Black-Scholes is useful for:
- IV inversion
- fair comparison
- delta / gamma / vega measurement

It is not useful as a blind command to buy/sell anything that differs from it.

### Minimum required outputs per strike
For each voucher, compute and store:
- market price
- fitted fair price
- residual
- implied vol
- fitted implied vol
- delta
- gamma
- vega
- theta
- moneyness

This creates a full surface state for the trader.

### Important guardrails
Reject or downweight observations where:
- option price < intrinsic
- spread is extremely wide
- order book is one-sided / vacuum-like
- IV inversion fails or explodes
- fitted IV is too far from neighboring strikes

---

## 7. Surface consistency checks

Before trading, run these checks:

### Monotonicity
Call price should decrease as strike rises.

### Convexity
Call surface should be convex in strike.

### Intrinsic floor
Option price should not be below intrinsic value.

### Smile smoothness
IV should not zig-zag wildly strike to strike without a strong reason.

If these conditions fail, the broken region itself may be tradable.

---

## 8. Best first implementations

### Version 1
- robust VEV fair
- IV inversion by strike
- quadratic smile fit
- residual-based outright trades
- hard per-strike caps

### Version 2
- add cross-strike spread trading
- add delta accounting across the whole voucher strip
- partial hedge in VEV

### Version 3
- add surface history
- trade skew shifts and lagged repricing
- add residual mean-reversion model

---

## 9. Common mistakes to avoid

- using raw last trade as underlying fair
- treating each voucher independently
- assuming flat vol
- trusting deep OTM/ITM IVs equally to ATM IVs
- using large size on a single rich/cheap strike without surface confirmation
- ignoring delta / gamma concentration in the strip
- treating BS fair as a direct signal instead of a baseline

---

## 10. Short execution checklist

Before trading vouchers each timestamp:

```text
1. estimate VEV fair
2. compute moneyness for all strikes
3. invert market IV for all usable strikes
4. fit smile
5. reprice all strikes
6. compute residuals
7. reject weak / illiquid / inconsistent points
8. rank trades by residual / spread / confidence
9. apply strip-level delta and size limits
10. trade
```

---

## Final takeaway

The advisor notes are telling you that the correct first lens is:

**“What volatility structure is the market implying across strikes and moneyness?”**

Only after that should you ask:
- which strikes are wrong,
- in which direction,
- and how much to size.

So the algorithmic focus for Round 3 should be:

**robust underlying fair -> implied vol surface -> moneyness pattern recognition -> residual trading with disciplined sizing.**
