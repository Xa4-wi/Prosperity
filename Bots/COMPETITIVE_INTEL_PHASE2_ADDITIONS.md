# Competitive Intelligence — Phase 2 Additions

This file is intended as an **appendix** to `COMPETITIVE_INTEL.md`. It adds forward-looking strategy theory, pattern-recognition checklists, stochastic-model selection rules, and a detailed Black-Scholes / implied-volatility playbook for future Prosperity 04 phases.

The existing `COMPETITIVE_INTEL.md` already captures many proven top-team lessons, especially:

- **Take → Clear → Make** execution order.
- Robust fair-value construction using wall/popular/stable mid instead of raw mid.
- Bot exploitation and participant-specific edge detection.
- Basket / ETF synthetic-value trading.
- Conversion arbitrage rules.
- Options / voucher pricing with Black-Scholes and implied-volatility smile fitting.
- Overfitting prevention and code robustness.

This appendix should be used as a second-layer research manual: once the obvious base strategy is built, use these sections to decide which deeper model family fits the product and how to avoid getting trapped in a bad local optimum.

---

# 1. Core meta-lesson from prior Prosperity competitions

The strongest public teams did **not** win by applying one universal model to every product. They won by rapidly classifying each product into a small number of product archetypes, then applying the simplest strategy that matched that archetype.

The most repeated pattern across previous competitions is:

```text
classify product -> build cheap fair -> test edge -> add execution layer -> only then optimize
```

Do **not** start with CMA-ES, Bayesian optimization, or large parameter searches. These tools are useful only after the product family is understood. Otherwise they will optimize noise, website randomness, or accidental simulator artifacts.

The most common top-team product families were:

| Product behavior | Best first model | Best execution style | Examples from prior competitions |
|---|---|---|---|
| Fixed fair / stable anchor | hard-coded anchor + inventory skew | take mispriced levels, market make around anchor | Amethysts / Pearls-style products |
| Slow local random walk | stable/wall/popular mid, market-maker mid | local-fair maker with inventory control | Starfruit / Kelp-style products |
| Mean reverting | O-U, EMA deviation, fixed thresholds | enter on deviation, exit at zero crossing | Kelp, Volcanic Rock, baskets |
| Deterministic drift / carry | time-schedule fair | accumulate early, avoid over-trading | Pepper-like products |
| Basket / ETF | synthetic fair from components | trade basket only or partial hedge | Picnic Basket, Pina/COCO-type products |
| Options / vouchers | Black-Scholes + IV surface | IV scalp, smile arb, gamma/delta logic | Coconut Coupon, Volcanic Rock Vouchers |
| Conversion product | import/export bounds | hard arbitrage, smart-taker quoting, storage-aware | Orchids, Macarons |
| Participant-driven | bot-ID/timing/size pattern | follow or fade known participant | Olivia / hidden takers |

---

# 2. Phase 2 research mindset

Phase 2 should be treated as a **model-selection problem**, not merely a parameter-tuning problem.

For every new product or new mechanic, force the agent to answer these questions before coding:

```text
1. Is the product anchored, drifting, mean-reverting, synthetic, optional, or participant-driven?
2. Does the alpha come from price prediction, execution quality, arbitrage bounds, or volume access?
3. Is the edge robust across randomized visibility / repeated uploads?
4. Does the strategy need inventory, or should inventory be recycled quickly?
5. Is the observed signal structural, or is it just a lucky website seed?
```

If any answer is unclear, build diagnostics before adding strategy complexity.

---

# 3. Pattern-recognition checklist for a new product

Run this checklist in the first research pass.

## 3.1 Basic statistical profile

For each product and day:

```text
mid_t = (best_bid + best_ask) / 2
spread_t = best_ask - best_bid
return_t = mid_t - mid_{t-1}
anchor_dev_t = mid_t - round_or_known_anchor
```

Compute:

- mean spread
- median spread
- top-of-book depth
- mid volatility
- autocorrelation of returns
- autocorrelation of deviations from anchor
- linear drift slope
- residual after drift removal
- position-limit impact if you held max long/short

Classification rules:

```text
large drift SNR + predictable time slope -> drift/carry product
strong negative return autocorrelation -> mean-reversion product
mid close to fixed level + shallow deviations -> fixed-anchor product
mid noisy but book structure predicts next move -> local-fair MM product
cross-product spread stationary -> pair/basket/stat-arb product
option-like payoff / strike / expiry -> Black-Scholes/IV product
```

## 3.2 Order-book pattern recognition

For every tick, compute:

```text
raw_mid        = (best_bid + best_ask) / 2
microprice     = (best_ask * bid_vol + best_bid * ask_vol) / (bid_vol + ask_vol)
imbalance      = (bid_vol - ask_vol) / (bid_vol + ask_vol)
popular_bid    = volume-weighted top-N bid price
popular_ask    = volume-weighted top-N ask price
stable_mid     = (popular_bid + popular_ask) / 2
wall_mid       = midpoint of largest bid wall and largest ask wall
book_health    = trust score of visible book
```

Useful hidden-pattern tests:

```text
corr(stable_mid - mid, next_mid - mid)
corr(microprice - mid, next_mid - mid)
corr(imbalance, next_mid - mid)
P(sign(next_move) = sign(imbalance) | spread <= threshold)
P(sign(next_move) = sign(stable_mid - mid) | |stable_gap| >= threshold)
P(next_move direction | stable_gap and imbalance agree)
P(next_move direction | stable_gap and imbalance disagree)
```

If stable fair and imbalance agree, test larger size. If they disagree, run an ablation: often imbalance/microprice wins short-horizon, while stable fair is slower.

## 3.3 Trade-tape pattern recognition

Market trades are not always predictive alone. Treat them as confirmation.

Track:

```text
trade_sign = +1 if trade at ask / buyer initiated
trade_sign = -1 if trade at bid / seller initiated
trade_size_bucket
trade_time_cluster
trade_price_relative_to_daily_high_low
```

Test:

```text
trade_sign alone -> next move?
trade_sign + imbalance agreement -> next move?
trade at new daily low/high -> possible Olivia-like participant?
repeated size 14-16 -> possible fixed bot?
repeated timestamp offsets -> possible scripted participant?
```

A trade signal is usually stronger when it confirms book imbalance than when it contradicts it.

---

# 4. Stochastic strategies and when to use them

## 4.1 Random walk / martingale baseline

Use this as the null model.

```text
S_{t+1} = S_t + epsilon_t
E[epsilon_t] = 0
```

If a product is close to this model:

- do not make directional bets
- earn spread only
- control inventory tightly
- avoid overreacting to price history

Best use:

```text
market making with inventory skew
fair = robust local mid
reservation = fair - inventory_penalty
```

Warning: many apparent trends disappear out-of-sample. Always test against a martingale null.

---

## 4.2 Drift process

Model:

```text
S_t = S_0 + drift * t + noise_t
```

Use when:

- residual around a time trend is small
- slope persists across days
- holding directionally has strong expected value

Best strategy:

```text
schedule target inventory over time
buy dips relative to trend
avoid chasing positive shocks
sell only if late/rich/over-positioned
```

Best for:

- Pepper-like products
- deterministic carry products
- products with known time ladder

Main risk:

```text
being right directionally but losing edge through bad entry price
```

---

## 4.3 Ornstein-Uhlenbeck mean reversion

Continuous model:

```text
dX_t = theta * (mu - X_t) dt + sigma dW_t
```

Discrete approximation:

```text
X_{t+1} - X_t = kappa * (mu - X_t) + epsilon_t
```

Use when:

- deviations from mean revert
- return autocorrelation is negative
- price has no deterministic drift but returns to a center

Trading rule:

```text
z = (X_t - mu) / sigma_resid
if z > entry_threshold: sell
if z < -entry_threshold: buy
exit when z crosses 0, not opposite threshold
```

Why exit at zero crossing:

- waiting for opposite threshold adds unnecessary risk
- prior teams found zero-crossing exits reduce variance

Best for:

- mean-reverting underlyings
- basket spread residuals
- option IV deviations

Do not use if:

- product has deterministic drift
- center shifts too fast
- spread is dominated by one-time jumps

---

## 4.4 Kalman filter / latent fair model

Model:

```text
latent_fair_t = latent_fair_{t-1} + process_noise
observed_mid_t = latent_fair_t + observation_noise
```

Use when:

- visible book is noisy or thinned
- raw mid is unreliable
- there is a latent fair that evolves smoothly

Practical version:

```text
if book_health high:
    trust observation more
else:
    trust previous latent fair more
```

This is useful for Round 2-like randomized quote visibility. It is a more formal version of `last_good_fair` and `medianGuard`.

Trading application:

```text
fair = kalman_latent_fair
quote around fair
reduce size when observation variance is high
```

---

## 4.5 Hidden Markov Model regime filter

Model:

```text
state_t ∈ {calm, trending, toxic, jumpy}
state_t follows a Markov chain
observations: returns, spread, imbalance, markout, volatility
```

Use when:

- the same signal works in one regime and fails in another
- volatility clusters
- fills become toxic in bursts
- drift/volatility parameters switch over time

Practical bot version:

```text
state_score_calm
state_score_toxic
state_score_drift
```

Then map states to execution:

```text
calm: tighter quotes, normal size
trending with signal: one-sided aggression
toxic: widen bad side, reduce size
jumpy: no aggressive taking
```

Use a lightweight version first. Full online HMM/EM is usually too much for competition time unless there is clear regime evidence.

---

## 4.6 Avellaneda-Stoikov market making

Core idea:

```text
reservation_price = fair - inventory_risk_term
optimal_spread = base_spread + volatility_term + inventory_term
```

Practical implementation:

```text
reservation = fair - gamma * sigma^2 * horizon * position
bid = reservation - spread/2
ask = reservation + spread/2
```

Use when:

- product is not directional
- you profit from spread capture
- inventory risk is meaningful
- volatility changes over time

Best for:

- Osmium-like products
- local-fair MM products
- stable-center but noisy books

Add-ons needed in Prosperity:

- book-health gating
- toxicity filter
- queue-position logic
- markout penalty
- position-limit hard caps

The pure textbook model is too smooth. Use it as a skeleton, not as a complete bot.

---

## 4.7 Queue-reactive / order-flow imbalance model

Model idea:

```text
next price move probability depends on queue sizes and order-flow imbalance
```

Use when:

- microprice predicts next move
- imbalance is stronger than raw mid
- book levels appear/disappear often

Signals:

```text
OFI = Δbid_volume_at_best - Δask_volume_at_best
micro_gap = microprice - mid
imbalance = (bid_vol - ask_vol) / total_vol
```

Trading use:

```text
if OFI and micro_gap agree:
    quote tighter on favored side
    widen opposite side
if OFI is adverse:
    avoid passive fill on that side
```

This is one of the best models for products like Osmium.

---

## 4.8 Multi-armed bandit / strategy router

Use when you have multiple strategy modules and do not know which regime dominates.

Example strategies:

```text
A: passive maker
B: aggressive taker
C: inventory recycler
D: no-trade / defend
```

Instead of optimizing one huge parameter vector, track which strategy has good recent markout.

Simple version:

```text
score_i = EMA(realized_pnl_or_markout_i)
choose strategy with highest score, with exploration floor
```

Use only for execution routing, not for product-fair discovery.

---

# 5. Strategy selection matrix

Use this table when a new product appears.

| Observed pattern | Primary model | Execution | Risk control |
|---|---|---|---|
| Fixed center, small noise | fixed anchor | take + two-sided MM | inventory skew |
| Fixed center, noisy book | anchor + stable/wall mid | local-fair MM | book health + median guard |
| Deterministic slope | drift schedule | accumulate, anti-chase | entry-quality gate |
| Negative return autocorr | O-U / EMA mean reversion | enter deviation, exit zero | fixed thresholds, max hold |
| Book imbalance predicts moves | queue-reactive OFI | one-sided MM / L1 take | toxicity, markout |
| One-sided books common | latent fair / vacuum state | tiny repair quotes | cooldown after vacuum |
| Cross-product spread stationary | basket/pair | trade synthetic residual | hedge ratio / zero exit |
| Option with strike/expiry | Black-Scholes + IV smile | IV scalp, cross-voucher | delta/gamma, moneyness filter |
| Conversion bounds visible | import/export arbitrage | take or smart-limit | storage + conversion cap |
| Known participant pattern | bot exploitation | follow/fade | confidence filter |

---

# 6. Phase 2 tactical recommendations

For the current style of Round 2 with randomized quote visibility and access mechanics, the strongest research direction is:

```text
make the bot conditionally aggressive only when the visible book is trustworthy
```

Important layers:

## 6.1 Book health

Compute:

```text
book_health = score from valid bid/ask, spread, depth, one-sided states, fair stability
```

Use:

```text
high health: normal local-fair MM, take allowed
medium health: smaller size, guarded fair
low health: no aggressive takes, repair-only quoting
```

## 6.2 Median-guard fair

When book health is weak:

```text
guarded_fair = median(anchor_fair, stable_mid, last_good_fair)
fair = blend(normal_fair, guarded_fair)
fair = clamp(fair, normal_fair ± max_guard_ticks)
```

This prevents the bot from trusting a distorted top-of-book after quote thinning.

## 6.3 Starvation / reentry

Do not use global no-fill logic only. Track side-specific starvation:

```text
bars_since_buy_fill
bars_since_sell_fill
```

Then:

```text
if buy side is starved and buy signal is safe:
    improve bid by 1 tick or increase join priority
if sell side is starved and sell signal is safe:
    improve ask by 1 tick or increase join priority
```

## 6.4 Passive-only markout

Track post-fill quality, but do not let it throttle every part of the engine.

Use markout to adjust:

```text
passive quote edge
passive quote size
```

Do not use the same markout penalty to also block aggressive takes, reentry, and clearing unless the evidence is overwhelming.

## 6.5 Terminal inventory

For non-carry products:

```text
late session + nonzero inventory = risk
```

Increase flattening pressure after 70%, 85%, and 95% of the session. Do not apply this strongly to deterministic carry products unless the market mechanics require forced liquidation.

---

# 7. Pattern recognition: practical tests to run every round

## 7.1 Drift SNR

```text
drift_slope = linear regression slope of mid on time
noise = std(mid - fitted_line)
drift_snr = total_drift / noise
```

Interpretation:

```text
drift_snr high: schedule/carry model
drift_snr low: do not use directional carry
```

## 7.2 Autocorrelation

Test returns:

```text
acf_lag_1 = corr(return_t, return_{t-1})
acf_lag_2 = corr(return_t, return_{t-2})
```

Interpretation:

```text
negative acf: mean reversion / scalping
positive acf: momentum / trend continuation
near zero: market making only
```

## 7.3 Spread-state performance

Bucket trades by spread:

```text
tight / normal / wide
```

For each bucket:

```text
fill count
avg markout
PnL per fill
inventory after fill
```

If wide-spread fills have bad markout, widen or reduce size. If tight-spread fills have good markout, increase throughput there.

## 7.4 Book-health performance

Bucket fills by health:

```text
high / medium / low
```

If low-health trades lose money, switch low-health mode to repair-only. If medium-health trades are profitable but underfilled, use medianGuard-lite rather than full shutdown.

## 7.5 Plateau classification

A flat PnL region can mean:

```text
A. correct no-trade: book is dangerous
B. missed opportunity: healthy book but no fills
C. inventory blocked: position near limit
D. stale toxicity: book recovered but state stayed defensive
E. signal neutral: no edge exists
```

Different fix for each:

| Plateau class | Fix |
|---|---|
| correct no-trade | leave alone |
| missed opportunity | side-specific reentry |
| inventory blocked | earlier recycler |
| stale toxicity | faster decay when raw toxicity is zero |
| signal neutral | tiny two-sided drip maker |

---

# 8. Black-Scholes theorem and application manual

## 8.1 What Black-Scholes prices

Black-Scholes prices a European option: a contract that pays a known function at expiry.

For a European call:

```text
payoff = max(S_T - K, 0)
```

Where:

- `S_T` = underlying price at expiry
- `K` = strike price

In Prosperity terms, voucher-style products are often call-like claims on an underlying product.

## 8.2 Black-Scholes assumptions

The standard model assumes:

```text
underlying follows geometric Brownian motion
constant volatility sigma
constant risk-free rate r
no arbitrage
frictionless continuous trading
European exercise only
no jumps
```

The underlying process:

```text
dS_t = μ S_t dt + σ S_t dW_t
```

Under risk-neutral pricing, the drift becomes `r`, not the real-world drift `μ`.

Important practical point:

```text
Black-Scholes does not need a forecast of the underlying drift.
It needs spot, strike, time, rate, and volatility.
```

In Prosperity, usually set `r = 0` unless the game provides an interest rate.

## 8.3 Call price formula

For a European call:

```text
C = S * N(d1) - K * exp(-rT) * N(d2)
```

with:

```text
d1 = [ln(S/K) + (r + 0.5*sigma^2)*T] / (sigma*sqrt(T))
d2 = d1 - sigma*sqrt(T)
```

Where:

- `S` = current underlying price
- `K` = strike
- `T` = time to expiry in years or consistent time units
- `sigma` = annualized or game-unit volatility matching `T`
- `r` = risk-free rate
- `N(x)` = standard normal CDF

If `r = 0`, then:

```text
C = S * N(d1) - K * N(d2)
```

## 8.4 Put price formula

For a European put:

```text
P = K * exp(-rT) * N(-d2) - S * N(-d1)
```

Put-call parity:

```text
C - P = S - K * exp(-rT)
```

If both calls and puts exist, parity violations are arbitrage candidates.

## 8.5 Greeks

Greeks describe how option price changes.

### Delta

```text
call_delta = N(d1)
```

Meaning:

```text
for a 1-unit increase in underlying, call price changes by about delta
```

Use:

- hedge underlying exposure
- compare options with different strikes
- size cross-voucher positions

### Gamma

```text
gamma = N'(d1) / (S * sigma * sqrt(T))
```

Meaning:

```text
how quickly delta changes as underlying moves
```

High gamma near ATM and close to expiry.

Use:

- gamma scalping
- avoid large unhedged convexity if spread costs are high

### Vega

```text
vega = S * N'(d1) * sqrt(T)
```

Meaning:

```text
option price sensitivity to volatility
```

Use:

- trade implied-vol mispricing
- normalize option price deviations by volatility sensitivity

### Theta

Theta is time decay.

Long options generally lose value as time passes unless volatility/gamma profits offset decay.

Use:

- avoid holding overpriced options too long
- understand why gamma scalping can be positive or negative net EV

## 8.6 Implied volatility

Market option price implies a volatility:

```text
market_price = BlackScholes(S, K, T, sigma_implied)
```

You solve for `sigma_implied` numerically.

Bisection method:

```python
def implied_vol_call(price, S, K, T, r=0.0):
    lo, hi = 1e-6, 5.0
    for _ in range(60):
        mid = (lo + hi) / 2
        val = black_scholes_call(S, K, T, mid, r)
        if val < price:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
```

Use bisection because it is stable and does not require scipy.

## 8.7 Moneyness

Useful definitions:

```text
absolute_moneyness = S - K
log_moneyness = ln(S/K)
scaled_moneyness = ln(K/S) / sqrt(T)
```

Prior Prosperity teams found that implied volatility should be analyzed against moneyness, not strike alone.

Why:

- the same strike can move from OTM to ATM as underlying changes
- IV smile is usually a function of relative strike
- near-expiry option behavior changes quickly

## 8.8 Volatility smile fitting

Options with different strikes usually have different IVs.

Do not assume one flat volatility.

Fit:

```text
iv_fair(m) = a*m^2 + b*m + c
```

where:

```text
m = log(K/S) / sqrt(T)
```

Then:

```text
iv_deviation_i = iv_market_i - iv_fair(m_i)
```

Trading:

```text
if iv_deviation_i >> 0: option is rich -> sell option
if iv_deviation_i << 0: option is cheap -> buy option
```

Then convert back to price:

```text
fair_price_i = BlackScholes(S, K_i, T, iv_fair(m_i))
price_edge_i = market_price_i - fair_price_i
```

## 8.9 When Black-Scholes is most useful

Use Black-Scholes when:

```text
product has strike and expiry
payoff resembles max(S_T - K, 0)
multiple strikes exist
option price co-moves nonlinearly with underlying
market has volatility-smile pattern
```

Best Prosperity use cases:

- vouchers / coupons
- call-like products
- option baskets
- products where price should depend on underlying, strike, and time

Do not use Black-Scholes for:

```text
ordinary spot products
fixed-anchor products
pure mean-reverting products without optional payoff
conversion arbitrage products
```

## 8.10 Option strategy families

### A. Single-option fair-value trading

```text
fair = BlackScholes(S, K, T, sigma_estimate)
if market_ask < fair - edge: buy
if market_bid > fair + edge: sell
```

Works only if sigma estimate is good.

### B. IV mean reversion

```text
iv_market = implied_vol(market_price)
iv_mean = rolling_mean(iv_market)
if iv_market > iv_mean + threshold: sell option
if iv_market < iv_mean - threshold: buy option
```

Use when IV deviations mean revert.

### C. Smile residual arbitrage

```text
fit smile across strikes
trade residuals relative to smile
```

Usually stronger than single-option IV mean reversion because it controls for moneyness.

### D. Cross-voucher arbitrage

If two options have similar moneyness but one is rich and the other cheap:

```text
buy cheap IV
sell rich IV
```

This reduces outright underlying delta.

### E. Gamma scalping

If you are long gamma:

```text
buy option
hedge delta with underlying
rebalance after underlying moves
```

Profit source:

```text
convexity gains from underlying movement - theta decay - hedge spread cost
```

In Prosperity, hedge spread cost can be large. Full hedging may reduce expected value too much. Test 0%, 50%, and 100% hedge ratios.

### F. Directional option proxy

Sometimes the option is simply a leveraged way to express underlying mean reversion or momentum.

Use only if:

```text
option delta is high enough
spread is acceptable
IV noise does not dominate
```

Deep ITM options can behave like the underlying but IV estimates can be unstable due to tiny extrinsic value.

## 8.11 Black-Scholes traps

### Trap 1: Wrong time units

If `T` is in days, sigma must be in per-sqrt-day units. If `T` is in years, sigma must be annualized.

Incorrect time scaling ruins IV.

### Trap 2: Deep ITM / OTM IV noise

When extrinsic value is tiny, a one-tick price change can create a huge implied-volatility error.

Filter:

```text
only trade strikes with enough extrinsic value
or cap IV deviation
or switch deep ITM options to delta/underlying-like model
```

### Trap 3: Ignoring spread

Option spread can be large relative to edge.

Trade only if:

```text
abs(price_edge) > spread/2 + safety_margin
```

### Trap 4: Using flat IV when smile exists

Flat IV creates systematic wrong prices across strikes.

Always test smile first.

### Trap 5: Hedging too often

Delta hedging pays spread each time.

Hedge only if:

```text
expected risk reduction > hedge cost
```

Often a partial hedge is better than full hedge.

### Trap 6: Treating IV edge and directional edge as the same

Separate:

```text
vol edge = option rich/cheap relative to IV smile
directional edge = underlying expected move
```

Size them separately.

## 8.12 Python-safe Black-Scholes implementation

```python
import math

SQRT_2PI = math.sqrt(2.0 * math.pi)

def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / SQRT_2PI

def norm_cdf(x: float) -> float:
    # Abramowitz-Stegun approximation
    t = 1.0 / (1.0 + 0.2316419 * abs(x))
    poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
    cdf = 1.0 - norm_pdf(x) * poly
    return cdf if x >= 0 else 1.0 - cdf

def black_scholes_call(S: float, K: float, T: float, sigma: float, r: float = 0.0) -> float:
    if T <= 0.0:
        return max(S - K, 0.0)
    if sigma <= 0.0:
        return max(S - K * math.exp(-r * T), 0.0)
    sqrtT = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    return S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)

def black_scholes_delta_call(S: float, K: float, T: float, sigma: float, r: float = 0.0) -> float:
    if T <= 0.0 or sigma <= 0.0:
        return 1.0 if S > K else 0.0
    sqrtT = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * sqrtT)
    return norm_cdf(d1)

def black_scholes_gamma(S: float, K: float, T: float, sigma: float, r: float = 0.0) -> float:
    if T <= 0.0 or sigma <= 0.0 or S <= 0.0:
        return 0.0
    sqrtT = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * sqrtT)
    return norm_pdf(d1) / (S * sigma * sqrtT)

def black_scholes_vega(S: float, K: float, T: float, sigma: float, r: float = 0.0) -> float:
    if T <= 0.0 or sigma <= 0.0:
        return 0.0
    sqrtT = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * sqrtT)
    return S * norm_pdf(d1) * sqrtT

def implied_vol_call(target_price: float, S: float, K: float, T: float, r: float = 0.0) -> float:
    intrinsic = max(S - K * math.exp(-r * T), 0.0)
    if target_price <= intrinsic + 1e-9:
        return 1e-6
    lo, hi = 1e-6, 5.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        price = black_scholes_call(S, K, T, mid, r)
        if price < target_price:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0
```

---

# 9. Research process to avoid bad optima

## 9.1 Promote only robust improvements

For every branch, record:

```text
mean score
standard deviation
10th percentile
no-access score
access score
product-level PnL
terminal inventory
max drawdown
```

Promote only if it improves:

```text
mean AND lower tail
```

A single high website score is not enough.

## 9.2 Prefer flat parameter plateaus

For each parameter:

```text
run p * 0.8, p * 0.9, p, p * 1.1, p * 1.2
```

If only one value works, the idea is fragile.

Choose the center of a stable high-performing range, not the peak.

## 9.3 Ablation rule

Every time a new layer improves score, run:

```text
full branch
minus layer A
minus layer B
minus layer C
```

If removing one tiny sub-rule destroys PnL, investigate before trusting it.

## 9.4 Restart triggers

Restart the approach if:

```text
same final inventory but worse PnL -> execution problem
opposite product split than expected -> classification problem
large score variance across seeds -> robustness problem
high mean but bad no-access score -> access overfit
high score with strange terminal inventory -> mark-to-market artifact
```

---

# 10. Suggested agent workflow for Phase 2

## Step 1 — freeze a safe base

Start from the best robust bot, not the most complex experimental branch.

## Step 2 — classify each new product

Use the product archetype table.

## Step 3 — implement the cheapest valid fair

No HMM, ML, or CMA-ES until simple fair fails.

## Step 4 — add Take → Clear → Make

This must exist before advanced alpha.

## Step 5 — run diagnostics

Minimum diagnostics:

```text
PnL by product
PnL by signal bucket
fills by side
markout by side
spread bucket performance
book-health bucket performance
terminal inventory
```

## Step 6 — choose stochastic model only if justified

Examples:

```text
OU if mean-reverting
Kalman if noisy latent fair
HMM if regimes switch
Black-Scholes if option payoff exists
Queue-reactive if order flow predicts next step
```

## Step 7 — optimize last

Use optimization only after:

```text
model family is correct
main signals survive ablation
performance is robust across seeds
```

---

# 11. Short checklist for future rounds

Before writing strategy:

```text
[ ] Plot mid, spread, depth, returns.
[ ] Test drift SNR.
[ ] Test return autocorrelation.
[ ] Test anchor deviation reversion.
[ ] Test book imbalance / microprice prediction.
[ ] Test stable-mid / wall-mid prediction.
[ ] Test public trade confirmation.
[ ] Check one-sided-book frequency.
[ ] Check cross-product synthetic relationships.
[ ] Check option-like payoff, strikes, expiry.
[ ] Check conversion bounds and storage cost.
[ ] Check participant/bot behavior.
```

Before promoting a bot:

```text
[ ] Beats base on mean.
[ ] Beats or matches base on 10th percentile.
[ ] Does not rely on one website seed.
[ ] Product-level PnL improves in intended product.
[ ] Terminal inventory is explainable.
[ ] Ablation confirms the layer is real.
[ ] Parameter surface is not a sharp peak.
```

---

# 12. Practical strategic conclusions

1. **Every new product should first be classified, not optimized.**
2. **Stable-fair products want Take → Clear → Make.**
3. **Noisy local products want robust fair + book health + queue signals.**
4. **Drift products want schedules, not neutral market making.**
5. **Options want implied volatility and smile residuals, not raw price comparison.**
6. **Conversion products want bounds, storage accounting, and smart-taker detection.**
7. **Participant-driven products can dominate all statistical models if the bot is identifiable.**
8. **Stochastic models should be chosen from product evidence, not preference.**
9. **Mean score is not enough under randomized simulation; lower-tail stability matters.**
10. **CMA-ES is useful only after the mechanism is known.**

