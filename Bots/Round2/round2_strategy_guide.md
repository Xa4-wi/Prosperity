# Round 2 strategy guide: Market Access Fee, budget allocation, and product playbook

## 1. What the uploaded data says

### 1.1 Round 1 baseline
From the strongest uploaded Round 1 runs:

- `219864.json`: total PnL `10431.125`
  - Pepper PnL: `7586.0`
  - Osmium PnL: `2845.125`
- `229934.json`: total PnL `10415.53125`
  - Pepper PnL: `7586.0`
  - Osmium PnL: `2829.53125`

Interpretation:
- Pepper is already very close to saturation in the current family.
- The major Round 2 upside is almost certainly in Osmium and in the Market Access Fee decision.

### 1.2 JSON and log file structure we can reuse
The run JSON files in this workspace have this practical structure:

```text
{
  "round": "1",
  "status": "FINISHED",
  "profit": 10431.125,
  "activitiesLog": "<semicolon-separated market snapshot log>",
  "graphLog": "<timestamp;value pnl curve>",
  "positions": [{"symbol": "...", "quantity": ...}, ...]
}
```

The `.log` files are one-line JSON objects with:

```text
{
  "submissionId": "...",
  "activitiesLog": "<same semicolon-separated market snapshot log>",
  "logs": [{"sandboxLog": "", "lambdaLog": "", "timestamp": 0}, ...],
  "tradeHistory": [
    {"timestamp": 0, "buyer": "...", "seller": "...", "symbol": "...", "price": ..., "quantity": ...},
    ...
  ]
}
```

That means the agent should treat:
- `activitiesLog` as a replayable market-state + PnL table
- `graphLog` as the aggregate equity curve
- `positions` as final inventory
- `tradeHistory` as executed trades that can be mapped back to states for post-trade analysis
- `logs[].sandboxLog` / `lambdaLog` as optional internal diagnostics

### 1.3 Round 2 public price data
The uploaded Round 2 public files are:

- `prices_round_2_day_-1.csv`
- `prices_round_2_day_0.csv`
- `prices_round_2_day_1.csv`
- `trades_round_2_day_-1.csv`
- `trades_round_2_day_0.csv`
- `trades_round_2_day_1.csv`

Observed structure:
- price files: `20000` rows per day, semicolon-separated, two products mixed in one file
- trade files: ~`790-803` trades per day, semicolon-separated

### 1.4 Product behavior in Round 2 public data

#### INTARIAN_PEPPER_ROOT
Pepper still behaves like a deterministic drift/carry product.

Per-day fitted slope in Round 2:
- day `-1`: about `0.001026` price units per timestamp
- day `0`: about `0.000985`
- day `1`: about `0.001025`

Start and end mids:
- day `-1`: `11001.5 -> 11999.5`
- day `0`: `11998.5 -> 13000.0`
- day `1`: `13000.0 -> 13999.5`

Round 2 Pepper summary:
- valid touch coverage: about `92.41%`
- average spread: about `14.12`
- average top-of-book depth: about `23.16`

Conclusion:
- Pepper thesis remains the same: deterministic rising fair, execution/carry product, low marginal upside versus current best Round 1 engine.

#### ASH_COATED_OSMIUM
Osmium still behaves like a local-fair microstructure product around a stable anchor near `10000`.

Round 2 Osmium summary:
- valid touch coverage: about `92.36%`
- average spread: about `16.23`
- average top-of-book depth: about `28.45`
- daily fitted drift is effectively near zero

The hidden local pattern also persists in Round 2:
- when stable-book fair and imbalance agree with `|stable_gap| >= 0.5`, next move sign matches about `86.34%`
- when they agree and `|stable_gap| >= 1.0`, next move sign matches about `87.82%`
- when stable-book and imbalance disagree, imbalance wins about `88.89%` of the time
- in tight-book states (`spread <= 16`) with nonzero microprice gap, next move sign follows microprice about `93.93%`

Conclusion:
- Round 2 does not change what Osmium is.
- It changes the value of extra throughput and quote access on Osmium.

---

## 2. Core Round 2 thesis

Round 2 is **not** primarily a new-signal round.

It is a **throughput-pricing round** on top of already-known product structure.

The correct split is:

- **Pepper:** keep the current carry engine mostly intact.
- **Osmium:** treat extra market access as a way to buy more high-quality fills, more local-fair dislocations, and more inventory recycling opportunities.
- **MAF bid:** compute it from estimated incremental value of access, not from intuition.
- **100k budget:** allocate to the pillar with the highest marginal return on additional throughput / execution quality.

### Practical implication
The most likely path to a large Round 2 gain is:

1. freeze a strong Round 1 baseline
2. build a Round 2 backtester that can estimate `PnL_access - PnL_no_access`
3. improve Osmium execution quality and access monetization
4. only then choose the MAF bid and budget allocation

---

## 3. What to keep from Round 1

### 3.1 Keep Pepper almost unchanged
Keep:
- deterministic drift backbone
- strong early accumulation
- passive buy ladder
- conservative selling
- cheap accumulation logic

Reason:
- current best Pepper contribution is already `7586.0`
- Round 2 public data shows the same deterministic drift identity
- extra flow helps Pepper less than Osmium because Pepper is already closer to the position-cap ceiling

### 3.2 Keep Osmium identity unchanged
Keep:
- slow fair near `10000`
- stable/popular/wall-mid local fair
- microprice + imbalance fast signal
- agreement / magnet logic
- toxicity smoothing
- inventory-aware quoting

Reason:
- Round 2 public data confirms the same local-fair / microstructure identity

---

## 4. What to improve for Round 2

## 4.1 Osmium: add markout-aware net edge
Current Osmium logic already identifies good-looking states.
The next step is to quote off:

```text
net_edge = estimated_edge - expected_markout_cost
```

This matters more in Round 2 because more access means more fills, and more fills only help if their post-fill quality is positive.

Recommended implementation:
- maintain side-specific markout EMA or bucketed markout memory
- start simple:
  - buy_markout by mild/strong toxicity
  - sell_markout by mild/strong toxicity
- quote and take only when net edge stays positive after that penalty

## 4.2 Osmium: make access-mode scalable
Create two execution profiles:

- `no_access` profile = current safe baseline
- `access` profile = same fair model, but:
  - larger front quote size in safe states
  - more permissive join-edge in strong conviction states
  - deeper sweep permission when fair remains positive at level 2/3
  - faster side-specific reentry after fill starvation

The rule is:
- do not invent a new fair for access
- scale the **execution layer**

## 4.3 Osmium: move from global reentry to side-starvation reentry
Track separately:
- bars since buy fill
- bars since sell fill

Then:
- only tighten / repost the side that is starved
- only when that side’s signal and toxicity justify it

This is better than broad “no fills lately” reentry.

## 4.4 Osmium: add multi-level sweep on strongest states
When all of these align:
- stable-mid and imbalance agree
- stable gap is large
- trade confirmation aligns
- toxicity is low
- inventory is not stretched

then:
- take best level
- re-evaluate edge against level 2
- keep sweeping while edge remains positive

This is a high-value Round 2 extension because extra access should increase the number of those deeper profitable opportunities.

## 4.5 Budget allocation should probably favor the Osmium bottleneck
Do not pre-commit to a fixed split until the pillar mechanics are known.
But the prior should be:

- if a pillar increases throughput, fill quality, or local-fair monetization, it is more likely to deserve budget than a pillar that only marginally helps Pepper carry capture

---

## 5. How to choose the Market Access Fee (MAF)

Let:

```text
Δ_access = expected PnL with access - expected PnL without access
```

Then bidding logic should be based on expected value:

```text
EV(bid) = P(access | bid) * (Δ_access - bid)
```

Practical rule:
- estimate `Δ_access` with the backtester
- haircut it for model uncertainty
- bid below a conservative lower bound of value
- do not bid “because access sounds good”

### Useful operational approach
Compute:
- optimistic `Δ_access`
- median `Δ_access`
- conservative `Δ_access` (for example 25th percentile across seeds)

Choose bids only from the conservative region.

---

## 6. How to avoid bad local optima in Round 2

### Rule 1: separate structural edge from access edge
Every experiment should report:
- `PnL_no_access`
- `PnL_access`
- `Δ_access`

Otherwise you will confuse:
- a generally stronger bot
with
- a bot that only looks good because it exploits your access simulation

### Rule 2: change one of these at a time
Only one family per branch:
- fair model
- take logic
- passive quote logic
- markout logic
- reentry logic
- access scaling

### Rule 3: compare per-product, not just total
Always record:
- total PnL
- Pepper PnL
- Osmium PnL
- final positions
- fill counts
- passive vs aggressive contribution
- access delta by product

### Rule 4: if a weird trick helps, isolate it immediately
The “hacky alpha 1 trick” and “magical trick” phenomenon is real in these bots.
Typical hidden causes are:
- one-tick queue-position improvement
- reentry changing actual posted price, not just desired edge
- hysteresis / state persistence
- vacuum or one-sided-book handling
- fill-starvation asymmetry
- markout filters changing when the bot is present at all

If a tweak helps but you do not understand why:
1. run an ablation with that one tweak removed
2. compare only the changed timestamps
3. compare fill count, average fill price, and post-fill markout
4. verify whether the gain survives multiple thinning seeds
5. do **not** optimize around it before understanding it

### Rule 5: restart fast when the family assumption is wrong
If a branch is stuck:
- do not keep tuning constants forever
- reclassify what the branch is trying to do

Examples:
- if extra access gives no benefit, your execution is too passive or your latent access model is wrong
- if access only helps Pepper a little, shift effort back to Osmium
- if markout filtering kills too much throughput, the penalty is over-counted
- if reentry “should” help but does not, it may not be changing actual queue position

---

## 7. Restart protocol when stuck

When a branch stalls, run this checklist:

### A. Is the product classification still right?
- Pepper = drift/carry?
- Osmium = local-fair maker/taker?

If yes, do not reinvent fair.
Fix execution.

### B. Is the branch changing actual posted prices or just theoretical edges?
A lot of “good ideas” fail because they only move internal edge values, while integer rounding and touch constraints leave the actual quotes unchanged.

### C. Is the gain coming from more fills or better fills?
- more fills with worse markout can still lose
- fewer fills with much better markout can win

### D. Is the branch helping `Δ_access` or only baseline?
Round 2 requires separate accounting.

### E. Is the branch robust across thinning seeds?
If no, it is probably a bad optimum.

---

## 8. Recommended immediate experiment queue

### Tier 1
1. `baseline_round2_replay`
2. `osmium_markout_net_edge`
3. `osmium_access_scaling`
4. `osmium_side_starvation_reentry`
5. `osmium_multi_sweep_conviction`

### Tier 2
6. `maf_bid_sweep`
7. `budget_marginal_roi_sweep`

### Tier 3
8. only after the above: narrow parameter tuning

---

## 9. One-line operating principle

**Round 2 should be approached as an Osmium throughput-pricing problem layered on top of an already-solved Pepper carry engine.**
