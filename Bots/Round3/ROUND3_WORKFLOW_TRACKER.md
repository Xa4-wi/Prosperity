# Round 3 Workflow Tracker

Base bot: [TradervR3_7.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_7.py)

## Current Status

- Calibration layer: done
- Exact phased workflow: done
- Phase 1 Hydrogel diagnosis: done
- Phase 1 Velvet diagnosis: done
- Phase 2 strip metrics: done
- Phase 3 fair rebuild: in progress
- Phase 4 strip risk limits: in progress
- Phase 5 overlay A/B validation: pending
- Phase 6 acceptance workflow enforcement: in progress
- Current Phase 1 follow-up bot: [TradervR3_8.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_8.py)
- Current Phase 2 strip-risk bot: [TradervR3_9.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_9.py)
- Current strip-risk winner: [TradervR3_10.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_10.py)
- Current Hydrogel risk-control bot: [TradervR3_15.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_15.py)
- Current BS-first voucher bot: [TradervR3_16.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_16.py)

## Latest Phase Result

- [TradervR3_8.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_8.py)
  - raw local total: `6281.0`
  - calibrated total: `25943.75`
- [TradervR3_9.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_9.py)
  - raw local total: `-54616.5`
  - calibrated total: `23902.9`
- [TradervR3_10.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_10.py)
  - raw local total: `76375.5`
  - calibrated total: `32668.82`
- [TradervR3_13.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_13.py)
  - raw local total: `63290.0`
  - calibrated total: `31964.45`
- [TradervR3_14.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_14.py)
  - raw local total: `51807.0`
  - calibrated total: `30133.6`
- [TradervR3_15.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_15.py)
  - raw local total: `74352.0`
  - calibrated total: `33750.5`
- [TradervR3_16.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_16.py)
  - raw local total: `269531.0`
  - calibrated total: `51278.85`
- [TradervR3_17.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_17.py)
  - raw local total: `297902.0`
  - calibrated total: `50743.0`
- [TradervR3_18.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_18.py)
  - raw local total: `269521.0`
  - calibrated total: `51278.85`
- [TradervR3_19.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_19.py)
  - raw local total: `264696.0`
  - calibrated total: `49586.60`
- [TradervR3_20.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_20.py)
  - raw local total: `266240.0`
  - calibrated total: `50127.00`
- [TradervR3_21.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_21.py)
  - raw local total: `269531.0`
  - calibrated total: `51278.85`
- [TradervR3_22.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_22.py)
  - raw local total: `269533.0`
  - calibrated total: `51278.85`
- [TradervR3_23.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_23.py)
  - raw local total: `269531.0`
  - calibrated total: `51278.85`
- [TradervR3_24.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_24.py)
  - raw local total: `257977.0`
  - calibrated total: `47234.95`

Interpretation:

- `R3_9` successfully adds explicit strip metrics and hard strip caps.
- On the current three-log calibration set, those caps are too blunt and underperform `R3_8`.
- `R3_10` keeps the same strip-monitoring structure but softens the gating enough to improve materially over `R3_8`.
- The next Round 3 change should continue from `R3_10`, not `R3_9`.
- `R3_13` implements the VEV hedge-book + alpha-book split with flatten-before-flip and is directionally reasonable, but still trails `R3_10`.
- `R3_14` isolates the VEV role split without voucher-size changes and is clearly weaker than `R3_10`.
- `R3_15` applies the Hydrogel-only redesign:
  - confidence-scaled target caps
  - flatten-before-flip
  - proactive clearing in stretched inventory
  - same-side blocking beyond the stretch zone
  - late target shrink and inventory aging
- `R3_15` is the first Hydrogel patch that improves the calibrated score over `R3_10` without changing Velvet or voucher logic.
- `R3_16` keeps the `R3_15` Hydrogel engine intact and rewrites the voucher strip into a more explicit Black-Scholes-first flow:
  - guarded voucher prices
  - weighted IV smile fit
  - neighboring-strike sigma sanity
  - explicit IV-residual confirmation before taking/quoting
  - vega-aware voucher sizing
- On the current calibrated selector, `R3_16` is a large improvement over `R3_15`, mainly because it turns the trusted `VEV_5100` bucket from negative to positive while keeping Hydrogel strong.
- `R3_17` is the first controlled low-strike reopening from the `R3_16` trunk:
  - only `VEV_4500` and `VEV_5000` were loosened
  - `5100+` protections stayed intact
- `R3_17` recovered a lot of `VEV_5000` raw local PnL, but it slightly worsened the calibrated score versus `R3_16`.
- So the current mainline conclusion stays: keep `R3_16` as provisional trunk, and treat `R3_17` as evidence that low-strike alpha is real but needs a more selective implementation.
- `R3_18` adds a strip-shock / IV-scalp mode on top of `R3_16`:
  - broad strip dislocation trigger
  - slightly easier voucher taking
  - a modest pair-bias bonus boost
  - a wider VEV hedge band during strip-wide shocks
- On current Round 3 data, that mode is effectively neutral:
  - raw total is only `-10.0` versus `R3_16`
  - calibrated total is identical to `R3_16`
- The useful conclusion is that the mode is not harmful, but it is mostly dormant under the current replay and should not replace `R3_16` as trunk.
- Hydrogel measurement now has an explicit artifact:
  - [round3_hydrogel_diagnostics.py](/Users/xavierwinkelmann/Prosperity/Analysis/scripts/round3_hydrogel_diagnostics.py)
  - [report.md](/Users/xavierwinkelmann/Prosperity/Analysis/output/round3_hydrogel_diagnostics/report.md)
- The Hydrogel diagnostics say:
  - classification still looks anchored local-fair MM
  - stretched same-side fills have negative 20-bar markout
  - the hidden-data problem is over-accumulation while stretched and then carrying near-full inventory too late
- `R3_19` was the first strict Hydrogel Phase B/C retune from `R3_16`:
  - earlier same-side blocks
  - stronger late-session cap shrink
  - harder proactive clear
  - smaller stretched quote size
- `R3_19` was too blunt and gave back too much Hydrogel edge.
- `R3_20` was a lighter Hydrogel-only retune from `R3_16`:
  - narrower late-session shrink
  - milder stretched-inventory controls
  - softer proactive clear changes
- `R3_20` was directionally better than `R3_19`, but still below `R3_16` on the current calibrated selector.
- So the Hydrogel conclusion from this cycle is:
  - the diagnosis is useful
  - but pure risk/execution tightening alone is not yet enough to beat `R3_16`
  - the next Hydrogel step should likely be more selective than broad tail suppression
- Three voucher vanna experiments were tested from the `R3_16` trunk:
  - `R3_21`: Version A, vanna risk overlay
  - `R3_22`: Version B, vanna hedge overlay
  - `R3_23`: Version C, vanna event mode
- Result:
  - `R3_21` was exactly neutral to `R3_16`
  - `R3_22` changed raw local total by only `+2.0`
  - `R3_23` was exactly neutral to `R3_16`
- Practical conclusion:
  - the vanna overlays are safe at small size
  - but on the current `R3_16` trunk they are mostly dormant
  - the likely reason is that `R3_16` already suppresses the near-ATM middle strip hard enough that vanna logic has very little live exposure to shape
  - so vanna is probably a second-order overlay, not the next main driver, unless we first reopen a controlled amount of near-ATM voucher activity
- A Hydrogel oracle class study is now available:
  - [round3_hydrogel_oracle_study.py](/Users/xavierwinkelmann/Prosperity/Analysis/scripts/round3_hydrogel_oracle_study.py)
  - [report.md](/Users/xavierwinkelmann/Prosperity/Analysis/output/round3_hydrogel_oracle_study/report.md)
- The oracle result is very strong:
  - `two_flip`: `167600.0`
  - `one_flip`: `107600.0`
  - `anchored_mean_reverter`: `71600.0`
  - `hold`: `15200.0`
  - `local_fair_mm`: `-154640.0`
- Practical interpretation:
  - Hydrogel ceiling looks regime / phase driven, not local-fair
  - the old Hydrogel family was likely using the wrong product thesis
- `R3_24` was the first regime-style Hydrogel branch from `R3_16`:
  - Hydrogel target ladder from a regime score
  - EMA trend state + anchor gap + flow score
  - Hydrogel fair shifted by regime score
- `R3_24` did not work yet:
  - it gave back Hydrogel too broadly and underperformed `R3_16`
  - so the oracle direction looks right, but the first generic regime detector was too blunt
- The current Hydrogel conclusion is:
  - the next edge probably still comes from a regime / phase thesis
  - but not from a single smooth score over the whole day
  - the next regime branch should be more structured, likely phase-aware or explicit state-machine based

## Current Evaluation Rule

Use:

- [run_round3_calibrated_backtest.py](/Users/xavierwinkelmann/Prosperity/Analysis/scripts/run_round3_calibrated_backtest.py)

Do not select Round 3 bots from raw local total alone.

## Immediate Next Deliverables

1. Keep [TradervR3_16.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_16.py) as the current workflow winner.
2. Keep VEV hedge/alpha separation as a research lane, but do not promote `R3_13` or `R3_14` yet.
3. Build the next voucher branch from `R3_16`, not `R3_17`, and reintroduce low-strike alpha more selectively than the first `R3_17` pass.
4. If we revisit strip-wide shock logic, add explicit diagnostics so we can tell whether the mode is actually triggering often enough to matter.
5. If we revisit Hydrogel next, prefer a narrower branch:
   - keep early-session Hydrogel behavior
   - focus only on late-session carry and sign-flip recovery
   - avoid broad same-side suppression throughout the day
6. If we revisit voucher vanna next, do it only after controlled near-ATM activity is reintroduced; otherwise the overlay stays mostly inactive.
7. If we revisit Hydrogel next, use the oracle study as the design anchor:
   - phase-aware / state-machine Hydrogel
   - not another smooth local-fair or broad risk-throttle variant
