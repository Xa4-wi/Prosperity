# Round 3 VEV + Voucher Research Guide

This guide turns the option papers and our `R3_28 -> R3_45` branch history into one concrete research path for `VELVETFRUIT_EXTRACT` and the voucher strip.

The goal is not to add every academic idea at once.

The goal is to move from:

- Black-Scholes fair + quadratic smile + mostly per-strike logic

to:

- Black-Scholes as coordinate system
- arbitrage-cleaned single-slice smile fitting
- strip-level relative-value trading
- buffered Velvet hedging
- broad surface-shock handling

while keeping the current Hydrogel branch stable.

---

## 1. Current practical read from our branches

### What is already true in our codebase

- `R3_28` is still the best real-log anchor for the overall bot family.
- `R3_42` proved that the connected `VELVET + voucher` architecture is directionally right, but its first activation layer was too strict and effectively switched the complex off.
- `R3_43` fixed the swallowed voucher exception and restored the complex:
  - `VELVETFRUIT_EXTRACT` came back
  - `VEV_4500`, `VEV_5000`, and `VEV_5100` came back
  - the branch became a real research branch again
- `R3_44` showed that extra `VELVET` steering hurt more than the low-strike voucher help.
- So the immediate lesson is:
  - keep Hydrogel stable
  - improve `VELVET + vouchers` together
  - prefer additive strip overlays over supervisory rewrites

### Most important local lesson

The profitable live lane is still:

- `VELVETFRUIT_EXTRACT`
- `VEV_4500`
- `VEV_5000`
- `VEV_5100`

The dangerous lane remains:

- middle strikes when we let the strip become too one-sided without good confirmation

---

## 2. What the papers suggest for our setup

This section keeps only the parts that are directly useful for a single-expiry, many-strike live strip.

### 2.1 Follmer + Schweizer: Black-Scholes is a hedging/regression scheme, not the alpha

Main takeaway:

- treat Black-Scholes as a sequential risk-reduction framework
- do not confuse the model price with the edge
- the edge comes from reducing risk relative to a coherent coordinate system

Implication for us:

- use BS to extract:
  - implied vols
  - delta
  - vega proxy
  - moneyness / log-strike coordinates
- do not trade because `bs_fair - price` is large in raw price space alone

For us, BS should be:

- the coordinate system
- the Greek generator
- the smile input layer

not:

- the whole alpha engine

Source:

- Follmer & Schweizer, *Hedging by Sequential Regression*  
  https://people.math.ethz.ch/~mschweiz/Files/astin.pdf

### 2.2 Gatheral + Jacquier: replace the quadratic smile with arbitrage-aware SVI

Main takeaway:

- fit total implied variance as a smile slice
- ensure no static arbitrage
- explicitly guard against:
  - butterfly arbitrage inside the slice
  - calendar arbitrage across maturities

Implication for our round:

- live Round 3 is basically a single maturity slice at a time
- so the highest-value upgrade is:
  - replace weighted quadratic smile with a single-slice SVI fit
- we do not need full multi-expiry machinery first

Most useful paper implications:

- fit total variance, not raw option price directly
- enforce butterfly-free slice conditions
- optionally prepare for a multi-round SSVI/eSSVI extension later

Source:

- Gatheral & Jacquier, *Arbitrage-Free SVI Volatility Surfaces*  
  https://arxiv.org/pdf/1204.0646

### 2.3 Cohen, Reisinger, Wang: clean the option quotes before fitting

Main takeaway:

- bad or stale option quotes can break smile fitting
- instead of globally smoothing everything, repair only what is necessary
- formulate the repair as minimal changes under no-arbitrage constraints

Implication for us:

Before IV inversion and smile fit, add a quote-cleaning layer:

- discard clearly unusable quotes
- minimally repair inconsistent mids
- respect bid/ask bounds when possible

For our live bot, the practical lightweight version is:

1. compute guarded mids
2. enforce monotonic call price by strike
3. enforce convexity of call prices across strike
4. only change the smallest number of offending quotes

We do not need full LP repair in the first branch, but the paper tells us the correct direction.

Source:

- Cohen, Reisinger, Wang, *Detecting and Repairing Arbitrage in Traded Option Prices*  
  arXiv / Oxford preprint via abstract:
  https://arxiv.org/abs/2008.09454

### 2.4 Stoikov + Saglam: quote the strip using portfolio risk, not only per-strike risk

Main takeaway:

- in a complete market, delta hedging removes inventory risk
- in incomplete markets, quotes should reflect net delta, vega, and gamma risk

Implication for us:

The strip must be managed as one portfolio:

- strip delta
- strip vega proxy
- near-ATM gross
- adjacent same-side concentration

This supports:

- pair-first trading
- hedge-driven `VELVET` role
- risk budgets across the strip, not only per strike

Source:

- Stoikov & Saglam, *Option Market Making Under Inventory Risk*  
  SSRN abstract:
  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1393818

### 2.5 Herrmann + Muhle-Karbe: use buffered hedging

Main takeaway:

- delta-vega hedging naturally emerges under recalibration uncertainty
- in practice, rebalancing needs a buffer

Implication for us:

`VELVETFRUIT_EXTRACT` should not chase every tiny change in strip delta.

We should use:

- hedge deadband
- partial hedge ratio
- hedge decay after residual compression

This is already directionally in our `R3_42/R3_43` family; the paper says that direction is right.

Source:

- Herrmann & Muhle-Karbe, *Model Uncertainty, Recalibration, and the Emergence of Delta-Vega Hedging*  
  https://arxiv.org/pdf/1704.04524

### 2.6 Ciliberti / Bouchaud / Potters: use sticky-strike as the first intraday smile update rule

Main takeaway:

- for short maturities, sticky strike is the stronger first approximation
- sticky delta becomes relatively better only for larger maturities

Implication for our short-dated vouchers:

- when `VELVETFRUIT_EXTRACT` moves intraday, first update the smile under a sticky-strike rule
- do not fully refit / reinterpret the whole strip as if moneyness instantly shifted the correct way every tick

Source:

- Ciliberti, Bouchaud, Potters, *Smile Dynamics – A Theory of the Implied Leverage Effect*  
  https://arxiv.org/pdf/0809.3375

### 2.7 Mingone / eSSVI: useful later, not first

Main takeaway:

- multi-slice arbitrage-free parametrisation can be done globally across maturities

Implication for us:

- useful if we later want to regularize across Round 1 / 2 / 3 historical TTE
- not the first live upgrade for Round 3

Source:

- Mingone, *No Arbitrage Global Parametrization for the eSSVI Volatility Surface*  
  https://arxiv.org/pdf/2204.00312

---

## 3. Strategic conclusion for our codebase

The next upgrade should **not** be:

- another raw Black-Scholes pricing tweak
- another broad loosen-the-strip experiment
- another Hydrogel-side rewrite

The next upgrade **should** be:

1. quote cleaning
2. single-slice SVI smile
3. IV-residual trading in strip space
4. pair-first execution
5. buffered `VELVET` hedge
6. broad strip shock mode

Short version:

**Move from “quadratic smile + per-strike logic” to “cleaned SVI slice + strip-level relative value + buffered Velvet hedge.”**

---

## 4. How this maps onto our current bot structure

Use the `R3_43` family as the base connected-system scaffold, because it already has:

- `VELVET` hedge/alpha split
- strip diagnostics
- pair bias
- `target_velvet_pos`
- low-strike participation restored

### Current code touchpoints

The main functions to evolve are:

- `_build_voucher_surface`
- `_build_voucher_risk_context`
- `_build_velvet_context`
- `_trade_voucher`
- the `VELVET` call path inside `run()`

Hydrogel should stay frozen on the `R3_28` side while we do this.

---

## 5. Research branch order

This is the most important part of the guide.

We should not jump to the final model in one branch.

### Branch A: quote cleaning + diagnostics only

Goal:

- improve smile inputs without changing the trading structure yet

Implementation:

1. in `_build_voucher_surface`, before IV inversion:
   - compute bid/ask/mid
   - derive guarded call price
   - enforce:
     - call price non-increasing in strike
     - simple convexity check across strike
   - minimally repair only violating quotes
2. log:
   - raw_mid
   - repaired_mid
   - repair_amount
   - repaired_flag

Acceptance criteria:

- strip still trades
- fit becomes more stable
- no dead branch behavior like early `R3_42`

### Branch B: replace quadratic smile with single-slice SVI

Goal:

- keep current trading engine mostly intact
- upgrade only the smile model

Implementation:

1. keep BS IV extraction
2. convert to total variance:
   - `w(k) = sigma^2 * T`
3. fit one SVI slice to repaired quotes
4. fall back to quadratic if:
   - too few liquid strikes
   - fit becomes unstable

Important:

- single-slice only
- no multi-expiry eSSVI yet

Acceptance criteria:

- fit remains stable across ticks
- residual ranking is not jumpy
- no-arbitrage violations are reduced

### Branch C: pair-first trading as the default voucher mode

Goal:

- move alpha from outright single-strike bets toward cross-strike relative value

Implementation:

1. compute:
   - `iv_residual = market_iv - fitted_iv`
2. rank:
   - cheapest strikes
   - richest strikes
3. first trade type:
   - buy cheap strike
   - sell rich strike
4. use outright trades only if:
   - residual is extreme
   - neighbors confirm
   - strip delta budget remains

Acceptance criteria:

- lower variance in middle strikes
- `VEV_4500/5000/5100` remain active
- `VEV_5200+` do not reopen recklessly

### Branch D: buffered Velvet hedge refinement

Goal:

- make `VELVETFRUIT_EXTRACT` behave like a clean strip hedge, not a competing directional book

Implementation:

1. keep:
   - hedge target
   - alpha target
2. add:
   - deadband
   - dynamic hedge ratio
   - hedge decay after residual compression
3. hard rule:
   - if strip delta is large, `alpha_target = 0`

Acceptance criteria:

- `VELVET` stays active
- `VELVET` does not dominate the book
- no repeat of `R3_44`, where extra `VELVET` steering hurt the branch

### Branch E: broad strip shock mode

Goal:

- capture the `v7`-style broad move without loosening the whole strip globally

Implementation:

Trigger from:

- average absolute IV residual
- neighboring-strike agreement count
- middle-strike gross still safe
- strip delta still safe

When on:

- lower voucher take edge slightly
- increase size slightly
- give pair bias more weight
- increase hedge ratio slightly

Do **not**:

- remove strip caps
- loosen all strikes equally

Acceptance criteria:

- mode fires rarely but usefully
- not always on
- improves broad dislocation windows

---

## 6. Concrete formulas / rules to use first

### 6.1 Velvet target split

```python
vev_hedge_target = - hedge_ratio * strip_delta

if abs(strip_delta) < delta_deadband:
    vev_hedge_target = 0

if abs(strip_delta) > alpha_block_delta:
    vev_alpha_target = 0
else:
    vev_alpha_target = small_alpha_signal

vev_target = clamp(vev_hedge_target + vev_alpha_target, -140, 140)
```

Suggested starting values:

- `delta_deadband = 20`
- `alpha_block_delta = 60`
- `hedge_ratio = 0.35 / 0.50 / 0.65` by strip state
- `max_abs_vev_alpha = 20 to 40`

### 6.2 Voucher priority order

1. pair trade
2. broad strip shock participation
3. outright trade

### 6.3 Outright voucher permission

Only allow outright when:

- `abs(iv_residual) > outright_threshold`
- neighbors support it
- strip delta is not stressed
- middle cluster is not overloaded

### 6.4 Exit rules

Pair trades:

- exit on residual zero crossing
- or scale out when 50–70% of the residual normalizes

Outright trades:

- reduce when residual falls below a fraction of entry threshold
- do not wait for perfect full reversion

---

## 7. Diagnostics we should log every tick

These should live in `traderData` so later log analysis is possible.

### Strip-level

- `strip_delta`
- `strip_vega_proxy`
- `avg_abs_iv_residual`
- `pair_agreement_count`
- `broad_dislocation`
- `middle_abs`
- `middle_same_side_gross`
- `cheapest_strikes`
- `richest_strikes`

### Velvet-level

- `vev_hedge_target`
- `vev_alpha_target`
- `vev_target`
- actual `VELVET` position
- hedge ratio
- hedge deadband active

### Voucher-level

- fitted IV by strike
- repaired IV by strike
- market IV by strike
- residual by strike
- pair target by strike
- outright target by strike

---

## 8. What to avoid

Do **not** do these next:

- do not loosen the whole voucher strip globally
- do not let `VELVET` alpha dominate the hedge role
- do not jump to vanna / vanna-volga before the strip-level base is stable
- do not move Hydrogel again while researching this lane
- do not replace the whole live engine with pair-only logic in one branch

---

## 9. Recommended branch sequence

Use this exact order:

1. `R3_46`
   - quote cleaning only
   - no new trading logic
2. `R3_47`
   - single-slice SVI fit
   - keep `R3_43` trading logic
3. `R3_48`
   - pair-first targets
   - outright trades still allowed as fallback
4. `R3_49`
   - buffered `VELVET` hedge refinement
5. `R3_50`
   - broad strip-dislocation mode

This sequence matters because it lets us attribute gains correctly.

Current branch-status read:

- `R3_46` quote cleaning was effectively inert on the current Round 3 quotes.
- `R3_47` single-slice SVI was the only branch in this family that actually improved the real portal log.
- `R3_48` low-strike pair-first overlay looked good locally, but was inert on the real portal log.
- `R3_49` is the first branch that directly bundles the strongest repo-derived ideas on top of the real-log-improved `R3_47` base:
  - hybrid IV fair
  - bid/ask smile bands
  - hedge-feasible sizing
  - buffered / dynamic `VELVET` hedge
- `R3_50` adds a route-aware mode machine on top of `R3_49`:
  - `DISCOVERY`
  - `RV_ACTIVE`
  - `STRIP_SHOCK`
  - `HARVEST`
  The goal is to reproduce the observed good PnL route shape without overtrading the strip all day.

So the live research trunk for the connected `VELVET + voucher` family should currently be:

- `R3_47` as the best real-log paper branch so far
- `R3_49` as the best pure paper-ideas branch
- `R3_50` as the next route-aware branch to validate on the portal

---

## 10. Acceptance criteria for the branch family

A branch is good if it improves at least one of:

- real `VELVET + voucher` participation without killing Hydrogel
- `VEV_4500/5000/5100` PnL stability
- reduced middle-strike same-side concentration
- better hedge efficiency in `VELVET`
- lower giveback after broad strip shocks

Reject branches that:

- deactivate `VELVET + vouchers`
- only look good by local Hydrogel inversion
- reopen `VEV_5200+` risk without confirmation

---

## 11. Bottom line

The next serious research branch should not ask:

- “How do we tweak Black-Scholes?”

It should ask:

- “How do we build an arbitrage-cleaned, strip-aware, pair-first voucher engine on top of the `R3_43` connected scaffold?”

That is the highest-signal next path from both:

- the papers
- and our actual `v28 -> v45` branch history

---

## Sources

- Follmer & Schweizer, *Hedging by Sequential Regression*  
  https://people.math.ethz.ch/~mschweiz/Files/astin.pdf
- Gatheral & Jacquier, *Arbitrage-Free SVI Volatility Surfaces*  
  https://arxiv.org/pdf/1204.0646
- Stoikov & Saglam, *Option Market Making Under Inventory Risk*  
  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1393818
- Herrmann & Muhle-Karbe, *Model Uncertainty, Recalibration, and the Emergence of Delta-Vega Hedging*  
  https://arxiv.org/pdf/1704.04524
- Ciliberti, Bouchaud, Potters, *Smile Dynamics – A Theory of the Implied Leverage Effect*  
  https://arxiv.org/pdf/0809.3375
- Mingone, *No Arbitrage Global Parametrization for the eSSVI Volatility Surface*  
  https://arxiv.org/pdf/2204.00312
- Cohen, Reisinger, Wang, *Detecting and Repairing Arbitrage in Traded Option Prices*  
  https://arxiv.org/abs/2008.09454
