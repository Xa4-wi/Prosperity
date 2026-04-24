# Round 3 Phased Workflow

Base bot: [TradervR3_7.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_7.py)

This workflow is the exact staged process we follow for Round 3 from this point forward. The goal is to keep us out of premature optimization, use the calibrated backtest workflow correctly, and improve the bot one layer at a time.

## Core Rule

Always follow this order:

```text
Profile -> Classify -> Build fair -> Add portfolio risk -> Add alpha -> Validate
```

Do not optimize thresholds before the product and strip structure are classified.

## Round 3 Working Principles

- Use [run_round3_calibrated_backtest.py](/Users/xavierwinkelmann/Prosperity/Analysis/scripts/run_round3_calibrated_backtest.py) for evaluation, not raw local total alone.
- Keep `VELVETFRUIT_EXTRACT` as the default hedge anchor unless diagnostics prove otherwise.
- Treat vouchers as one strip first and 10 products second.
- Prefer relative-value voucher logic before outright directional voucher trading.
- Keep bot-overlay logic small until it survives validation.
- Only change one layer per version.

## Phase 0: Evaluation Baseline

Before any model changes:

1. Run the normal local Round 3 backtest.
2. Run the calibrated wrapper on the same candidate.
3. Save:
   - raw local total
   - calibrated total
   - product-level PnL
   - voucher strip concentration
4. Treat calibration as the ranking signal when raw and calibrated disagree.

Required command:

```bash
python3 Analysis/scripts/run_round3_calibrated_backtest.py Bots/Round3/TradervR3_7.py
```

Done criteria:

- We have both raw and calibrated totals.
- We know whether the candidate improved on `R3_7` by calibrated score.

## Phase 1: Classify the Delta-1 Products Harder

### Phase 1A: HYDROGEL_PACK diagnosis

Measure:

- drift SNR
- mean-reversion half-life
- correlation of next move with micro-gap
- correlation of next move with imbalance
- stability of `stable_mid - raw_mid`
- realized volatility by time bucket
- spread / depth regime stability

Decision goal:

- anchored market maker
- local-fair microstructure
- mean-reverter
- drift/trend
- thin-book / vacuum-sensitive

Implementation output:

- a diagnosis report
- a recommended fair family
- a recommended execution style

### Phase 1B: VELVETFRUIT_EXTRACT diagnosis

Measure the same features, but interpret them with two priorities:

1. direct alpha quality
2. hedge-anchor robustness for vouchers

Decision goal:

- determine whether Velvet should remain the strip hedge anchor
- determine whether its fair should be more anchor-driven or more local-fair-driven

Done criteria:

- Hydrogel and Velvet each have a recommended classification and fair family.
- We have a written note saying what should and should not be changed next.

## Phase 2: Treat Vouchers as a Portfolio

Build strip-level monitoring before adding more alpha.

Track every tick:

- total strip delta
- total strip vega proxy
- middle-strike gross exposure
- same-side adjacent-strike concentration
- wing net exposure
- per-strike residual ranking

Required implementation order:

1. strip metrics only
2. hard strip risk limits
3. 50% hedge baseline
4. only then relative-value trading logic

Done criteria:

- Strip metrics are visible in code and logs.
- We can say how exposed the strip is without reading 10 strikes by hand.

## Phase 3: Improve Fair Construction Before Thresholds

### Underlyings

Fix and validate:

- depth-aware wall mid
- stable mid
- raw-mid vs stable-mid behavior
- guarded fallback when the book is sparse or distorted

### Voucher strip

Protect the smile fit with:

- IV clipping
- liquidity-aware input filtering
- neighboring-strike sanity checks
- no-arbitrage monotonicity checks
- fallback median-vol smile when the fit is sparse

Done criteria:

- Underlying fair inputs are stable and interpretable.
- Smile fit survives sparse / distorted quotes without forcing aggressive trades.

## Phase 4: Risk Management Before Alpha Expansion

Implement in this order:

1. max total strip delta
2. max middle-strike gross exposure
3. max adjacent-strike concentration
4. max outright exposure unless pair confirmation exists
5. 50% Velvet hedge baseline
6. zero-cross exit rule for relative-value positions

Important rule:

Do not use portfolio logic as a big directional target engine until the risk layer is stable.

Done criteria:

- Middle-strike blowups are mechanically capped.
- Hedge ratio is explicit and testable.

## Phase 5: Keep Overlay Alpha Small Until Proven

Current default:

- Velvet overlay remains a small bias only.
- No overlay may override the main position engine.
- No overlay gets a large size multiplier by default.

Validation:

- compare with overlay
- compare without overlay
- compare mean, lower tail, and inventory behavior

Done criteria:

- Overlay survives A/B testing or gets removed.

## Phase 6: Validation Workflow

Every candidate version must follow this acceptance flow:

1. one layer changed only
2. local backtest run
3. calibrated backtest score
4. compare product PnL
5. compare strip concentration
6. reject if improvement only appears in a tiny parameter band

Acceptance criteria:

- improves calibrated total, or
- improves one of:
  - mean PnL
  - 25th percentile PnL
  - worst-run PnL
  - inventory stability
  - strip-risk concentration

Reject if:

- only raw local total improves
- calibrated score worsens
- voucher strip concentration worsens materially
- result depends on a knife-edge threshold

## Exact Implementation Sequence From Here

Starting point: [TradervR3_7.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_7.py)

### Step 1

Run harder Hydrogel and Velvet diagnostics.

Output:

- [round3_phase1_diagnostics.py](/Users/xavierwinkelmann/Prosperity/Analysis/scripts/round3_phase1_diagnostics.py)
- a saved report under [Analysis/output/round3_phase1_diagnostics](/Users/xavierwinkelmann/Prosperity/Analysis/output/round3_phase1_diagnostics)

### Step 2

Use that report to decide:

- Hydrogel fair family
- Velvet fair family
- whether Hydrogel should stay anchored or move toward local-fair / safer mode

### Step 3

Build the next bot from `R3_7` with only:

- fair construction changes that are justified by Phase 1
- no new voucher alpha yet

### Step 4

Add strip-level metrics and hard risk limits before any new voucher alpha logic.

### Step 5

Only after that, add paired residual-value voucher trading.

## Practical Guardrails

- Do not optimize Hydrogel constants before classification is written down.
- Do not add broader voucher alpha until strip risk metrics exist.
- Do not trust raw local total alone.
- Do not accept a candidate because one middle strike happened to print well once.
