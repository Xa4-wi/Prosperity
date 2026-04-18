## `TradervR2_1`

First Round 2 bot built from the Round 2 strategy guide on top of the strongest Round 1 trunk:
- base bot: [TradervR1_121_13.py](/Users/xavierwinkelmann/Prosperity/Bots/Round1/TradervR1_121_13.py)
- new file: [TradervR2_1.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_1.py)

Round 2 design choices:
- keep Pepper as a carry engine, but slow the drift assumptions down to match Round 2 public data
- keep Osmium as a local-fair microstructure product
- add a first access-style Osmium execution layer:
  - slightly more permissive join behavior
  - larger safe-state front quotes
  - multi-level sweeping in strongest aligned states
  - faster side-specific re-entry after fill starvation
- add a first conservative market-access bid through `Trader.bid()`

Current `bid()`:
- `12`

Public Round 2 deterministic replay (`rust` engine):
- day `-1`: total `98'664.0`
  - `ASH_COATED_OSMIUM`: `20'051.0`
  - `INTARIAN_PEPPER_ROOT`: `78'613.0`
- day `0`: total `99'522.0`
  - `ASH_COATED_OSMIUM`: `20'530.0`
  - `INTARIAN_PEPPER_ROOT`: `78'992.0`
- day `1`: total `98'397.0`
  - `ASH_COATED_OSMIUM`: `20'183.0`
  - `INTARIAN_PEPPER_ROOT`: `78'214.0`

Three-day total:
- `296'583.0`

Comparison against the untouched Round 1 trunk on Round 2 public replay:
- [TradervR1_121_13.py](/Users/xavierwinkelmann/Prosperity/Bots/Round1/TradervR1_121_13.py): `298'946.0`
- [TradervR2_1.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_1.py): `296'583.0`
- delta: `-2'363.0`

Read:
- the first Round 2 access-style Osmium layer is directionally reasonable
- but the Pepper drift retune was too weak overall and gave back more than the Ash changes recovered
- so `TradervR2_1` is a valid Round 2 starting branch, but not yet a better public-data replay bot than the untouched `TradervR1_121_13.py`

Artifacts:
- [day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_1_day_-1/metrics.json)
- [day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_1_day_0/metrics.json)
- [day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_1_day_1/metrics.json)

## `TradervR2_2`

Second Round 2 branch built from the same standalone base, but with the Round 2 objective reframed around the cumulative target:
- Pepper goes back to the stronger proven Round 1 carry settings so it remains the base PnL engine
- Osmium keeps the access-oriented execution layer from `R2_1`
- `Trader.bid()` is explicitly set to `25000` for direct Market Access Fee testing

New file:
- [TradervR2_2.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_2.py)

Current `bid()`:
- `25000`

Public Round 2 deterministic replay (`rust` engine):
- day `-1`: total `99'499.0`
  - `ASH_COATED_OSMIUM`: `20'051.0`
  - `INTARIAN_PEPPER_ROOT`: `79'448.0`
- day `0`: total `100'011.0`
  - `ASH_COATED_OSMIUM`: `20'530.0`
  - `INTARIAN_PEPPER_ROOT`: `79'481.0`
- day `1`: total `99'571.0`
  - `ASH_COATED_OSMIUM`: `20'183.0`
  - `INTARIAN_PEPPER_ROOT`: `79'388.0`

Three-day total:
- `299'081.0`

Comparison:
- [TradervR2_1.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_1.py): `296'583.0`
- [TradervR1_121_13.py](/Users/xavierwinkelmann/Prosperity/Bots/Round1/TradervR1_121_13.py): `298'946.0`
- [TradervR2_2.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_2.py): `299'081.0`

Read:
- restoring Pepper as the base engine was the right correction
- the access-style Osmium layer still adds a little on top
- this is the first Round 2 branch here that beats both `R2_1` and the untouched `R1_121_13` public Round 2 replay

Artifacts:
- [day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_2_day_-1/metrics.json)
- [day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_2_day_0/metrics.json)
- [day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_2_day_1/metrics.json)

## `TradervR2_3`

Third Round 2 branch built as an official-path refinement of `R2_2`:
- keep the stronger `R2_2` Pepper base exactly intact
- keep the same explicit `25000` market-access bid
- make the Osmium access layer more selective:
  - smaller access quote-size bonus
  - less take relief
  - shallower sweep depth
  - stronger signal / conviction / magnet requirements

New file:
- [TradervR2_3.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_3.py)

Current `bid()`:
- `25000`

Public Round 2 deterministic replay (`rust` engine):
- day `-1`: total `99'499.0`
  - `ASH_COATED_OSMIUM`: `20'051.0`
  - `INTARIAN_PEPPER_ROOT`: `79'448.0`
- day `0`: total `100'011.0`
  - `ASH_COATED_OSMIUM`: `20'530.0`
  - `INTARIAN_PEPPER_ROOT`: `79'481.0`
- day `1`: total `99'571.0`
  - `ASH_COATED_OSMIUM`: `20'183.0`
  - `INTARIAN_PEPPER_ROOT`: `79'388.0`

Three-day total:
- `299'081.0`

Comparison:
- [TradervR2_2.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_2.py): `299'081.0`
- [TradervR2_3.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_3.py): `299'081.0`

Read:
- `R2_3` is locally identical to `R2_2`
- that means the more selective access logic does not change the public visible-book replay boundary
- if `R2_3` helps at all, it would most likely be through the official access environment rather than the public deterministic replay

Artifacts:
- [day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_3_day_-1/metrics.json)
- [day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_3_day_0/metrics.json)
- [day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_3_day_1/metrics.json)

## Research Sweep

Research map:
- [BEST_APPROACH.md](/Users/xavierwinkelmann/Prosperity/Bots/Round2/BEST_APPROACH.md)

Branches built from the research themes:
- [TradervR2_4.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_4.py): bucketed markout / passive net-edge quoting
- [TradervR2_5.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_5.py): higher-rank microprice and deep imbalance
- [TradervR2_6.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_6.py): high-conviction throughput expansion
- [TradervR2_7.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_7.py): Pepper schedule / catch-up execution

Public Round 2 deterministic replay totals:
- [TradervR2_2.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_2.py): `299'081.0`
- [TradervR2_4.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_4.py): `293'041.0`
- [TradervR2_5.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_5.py): `299'098.0`
- [TradervR2_6.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_6.py): `299'081.0`
- [TradervR2_7.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_7.py): `299'081.0`

Read:
- `R2_5` is the only branch that improved the public replay, and only slightly: `+17.0` over `R2_2`
- `R2_4` was clearly harmful, entirely through worse Osmium behavior
- `R2_6` and `R2_7` were locally inert on top of `R2_2`

Product split highlights:
- `R2_4` hurt `ASH_COATED_OSMIUM` badly while Pepper stayed unchanged
- `R2_5` improved Osmium slightly while Pepper stayed unchanged
- `R2_6` and `R2_7` preserved both product paths exactly on public replay

Artifacts:
- [R2_4 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_4_day_-1/metrics.json)
- [R2_4 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_4_day_0/metrics.json)
- [R2_4 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_4_day_1/metrics.json)
- [R2_5 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_5_day_-1/metrics.json)
- [R2_5 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_5_day_0/metrics.json)
- [R2_5 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_5_day_1/metrics.json)
- [R2_6 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_6_day_-1/metrics.json)
- [R2_6 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_6_day_0/metrics.json)
- [R2_6 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_6_day_1/metrics.json)
- [R2_7 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_7_day_-1/metrics.json)
- [R2_7 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_7_day_0/metrics.json)
- [R2_7 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_7_day_1/metrics.json)

## `TradervR2_8`

Structural experiment from the critique of the current Pepper target model:
- redesign `INTARIAN_PEPPER_ROOT` target path so it is not effectively max-long from tick 0
- make the Pepper max inventory truly hard
- add explicit mid-round decay, scale-out on strong positive extension, and late neutralization
- add one-sided-book fallback handling to Pepper
- refresh Ash projected inventory again before quote sizing / quote permission checks

New file:
- [TradervR2_8.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_8.py)

Public Round 2 deterministic replay (`rust` engine):
- day `-1`: total `76'493.0`
  - `ASH_COATED_OSMIUM`: `20'041.0`
  - `INTARIAN_PEPPER_ROOT`: `56'452.0`
- day `0`: total `77'041.0`
  - `ASH_COATED_OSMIUM`: `20'511.0`
  - `INTARIAN_PEPPER_ROOT`: `56'530.0`
- day `1`: total `76'694.0`
  - `ASH_COATED_OSMIUM`: `20'229.0`
  - `INTARIAN_PEPPER_ROOT`: `56'465.0`

Three-day total:
- `230'228.0`

Read:
- Ash stayed broadly fine
- the whole giveback came from Pepper
- so the critique was directionally right, but this first full rewrite over-corrected and gave away too much carry
- the useful lesson is: Pepper does need a better target/exit model, but not one this restrictive on public Round 2 data

Artifacts:
- [R2_8 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_8_day_-1/metrics.json)
- [R2_8 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_8_day_0/metrics.json)
- [R2_8 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_8_day_1/metrics.json)

## `TradervR2_9`

Lighter retry after `R2_8` over-corrected:
- start from the stronger [TradervR2_5.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_5.py) trunk
- keep the stronger top-3 Osmium signal unchanged
- apply only a light Pepper cleanup:
  - make the hard long target internally consistent with intended behavior
  - enforce Pepper buys to stop at the target instead of overshooting it
  - add only mild sell relief on strong positive extension / late round
  - add one-sided-book Pepper fallback handling
- keep the Ash projected-inventory refresh before quote permission / quote sizing

New file:
- [TradervR2_9.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_9.py)

Public Round 2 deterministic replay (`rust` engine):
- day `-1`: total `99'515.0`
  - `ASH_COATED_OSMIUM`: `20'041.0`
  - `INTARIAN_PEPPER_ROOT`: `79'474.0`
- day `0`: total `99'994.0`
  - `ASH_COATED_OSMIUM`: `20'511.0`
  - `INTARIAN_PEPPER_ROOT`: `79'483.0`
- day `1`: total `99'622.0`
  - `ASH_COATED_OSMIUM`: `20'229.0`
  - `INTARIAN_PEPPER_ROOT`: `79'393.0`

Three-day total:
- `299'131.0`

Comparison:
- [TradervR2_5.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_5.py): `299'098.0`
- [TradervR2_9.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_9.py): `299'131.0`

Read:
- this is the first successful retry after the failed heavy Pepper rewrite
- the gain is small but clean: `+33.0`
- all of it comes from Pepper
- Ash stays exactly unchanged on public replay
- so the lighter Pepper cleanup looks like the right direction, while `R2_8` was simply too restrictive

Artifacts:
- [R2_9 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_9_day_-1/metrics.json)
- [R2_9 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_9_day_0/metrics.json)
- [R2_9 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_9_day_1/metrics.json)

## `R2_10` Osmium Structure Sweep

Prompt used for this sweep:
- keep the early Osmium alpha from the stronger branch
- remove the long-run drag
- add explicit short-cover recycling
- separate high-quality alpha detection from baseline market-making activity

Built variants:
- [TradervR2_10_softMarkout.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_softMarkout.py): soften markout penalties so they act more like a warning than a brake
- [TradervR2_10_shortCover.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_shortCover.py): explicit short-cover recycling when no longer strongly bearish
- [TradervR2_10_baselineActive.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_baselineActive.py): keep a baseline maker/recycler alive in normal, low-toxicity states
- [TradervR2_10_combo.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_combo.py): combine all three ideas

Public Round 2 deterministic replay (`rust` engine):
- [TradervR2_9.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_9.py): `99'515.0 / 99'994.0 / 99'622.0` = `299'131.0`
- [TradervR2_10_softMarkout.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_softMarkout.py): `99'705.0 / 99'994.0 / 99'622.0` = `299'321.0`
- [TradervR2_10_shortCover.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_shortCover.py): `99'508.0 / 99'994.0 / 99'576.0` = `299'078.0`
- [TradervR2_10_baselineActive.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_baselineActive.py): `99'611.0 / 99'994.0 / 99'622.0` = `299'227.0`
- [TradervR2_10_combo.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_combo.py): `99'705.0 / 99'994.0 / 99'576.0` = `299'275.0`

Product split over the three public days:
- [TradervR2_9.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_9.py): `ASH_COATED_OSMIUM = 60'781.0`, `INTARIAN_PEPPER_ROOT = 238'350.0`
- [TradervR2_10_softMarkout.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_softMarkout.py): `ASH_COATED_OSMIUM = 60'971.0`, `INTARIAN_PEPPER_ROOT = 238'350.0`
- [TradervR2_10_baselineActive.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_baselineActive.py): `ASH_COATED_OSMIUM = 60'877.0`, `INTARIAN_PEPPER_ROOT = 238'350.0`
- [TradervR2_10_combo.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_combo.py): `ASH_COATED_OSMIUM = 60'925.0`, `INTARIAN_PEPPER_ROOT = 238'350.0`
- [TradervR2_10_shortCover.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_shortCover.py): `ASH_COATED_OSMIUM = 60'728.0`, `INTARIAN_PEPPER_ROOT = 238'350.0`

Read:
- the winning change is the soft markout version
- it improves total public replay by `+190.0` over `R2_9`
- all of the gain is Osmium; Pepper stayed exactly unchanged
- the baseline-activity idea is also live, but weaker than soft markout
- the short-cover-only version is worse than the trunk
- combining all three ideas is better than the trunk, but still worse than just softening markout

Best current public-data branch from this line:
- [TradervR2_10_softMarkout.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_softMarkout.py)

Artifacts:
- [softMarkout day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_10_softMarkout_day_-1/metrics.json)
- [softMarkout day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_10_softMarkout_day_0/metrics.json)
- [softMarkout day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_10_softMarkout_day_1/metrics.json)
- [shortCover day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_10_shortCover_day_-1/metrics.json)
- [shortCover day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_10_shortCover_day_0/metrics.json)
- [shortCover day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_10_shortCover_day_1/metrics.json)
- [baselineActive day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_10_baselineActive_day_-1/metrics.json)
- [baselineActive day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_10_baselineActive_day_0/metrics.json)
- [baselineActive day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_10_baselineActive_day_1/metrics.json)
- [combo day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_10_combo_day_-1/metrics.json)
- [combo day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_10_combo_day_0/metrics.json)
- [combo day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_10_combo_day_1/metrics.json)

## `R2_11` SoftMarkout Follow-Up

Goal:
- continue from [TradervR2_10_softMarkout.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_softMarkout.py)
- test whether smaller refinements around the live markout lever unlock more public-data edge

Branches:
- [TradervR2_11_passiveOnly.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_11_passiveOnly.py): remove markout from take gating, keep it on passive quoting / sizing
- [TradervR2_11_sizeFeather.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_11_sizeFeather.py): soften markout size penalty further
- [TradervR2_11_baselineLite.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_11_baselineLite.py): lighter baseline maker/recycler support
- [TradervR2_11_comboLite.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_11_comboLite.py): passive-only markout plus lighter baseline support

Public Round 2 deterministic replay (`rust` engine):
- [TradervR2_10_softMarkout.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_softMarkout.py): `99'705.0 / 99'994.0 / 99'622.0` = `299'321.0`
- [TradervR2_11_passiveOnly.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_11_passiveOnly.py): `99'705.0 / 99'994.0 / 99'622.0` = `299'321.0`
- [TradervR2_11_sizeFeather.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_11_sizeFeather.py): `99'705.0 / 99'994.0 / 99'622.0` = `299'321.0`
- [TradervR2_11_baselineLite.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_11_baselineLite.py): `99'705.0 / 99'994.0 / 99'622.0` = `299'321.0`
- [TradervR2_11_comboLite.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_11_comboLite.py): `99'705.0 / 99'994.0 / 99'622.0` = `299'321.0`

Read:
- all four `R2_11` variants are completely identical to `R2_10_softMarkout` on public replay
- that means these lighter refinements do not cross a new visible fill boundary
- the current best public-data trunk remains [TradervR2_10_softMarkout.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_10_softMarkout.py)

## `TradervR2_12`

Clean restart baseline:
- goal: stop patching the layered `R2_9`/`R2_10` tree and rebuild from a simpler structure
- restart notes: [RESTART_BASELINE.md](/Users/xavierwinkelmann/Prosperity/Bots/Round2/RESTART_BASELINE.md)

New file:
- [TradervR2_12.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_12.py)

Design:
- Pepper rewritten as a simple drift/carry engine with:
  - day-start anchor
  - linear fair path
  - hard schedule target
  - mild late sell relief
- Osmium rewritten as a simple local-fair maker with:
  - `10000` anchor
  - stable-mid + micro fair
  - separate `take_alpha` and `quote_alpha`
  - simple inventory skew
  - one-sided-book fallback handling

Public Round 2 deterministic replay (`rust` engine):
- day `-1`: total `73'274.0`
  - `ASH_COATED_OSMIUM`: `7'055.0`
  - `INTARIAN_PEPPER_ROOT`: `66'219.0`
- day `0`: total `72'752.0`
  - `ASH_COATED_OSMIUM`: `6'399.0`
  - `INTARIAN_PEPPER_ROOT`: `66'353.0`
- day `1`: total `72'191.0`
  - `ASH_COATED_OSMIUM`: `5'918.0`
  - `INTARIAN_PEPPER_ROOT`: `66'273.0`

Three-day total:
- `218'217.0`

Read:
- this is intentionally a reset baseline, not a contender branch
- Pepper is still doing the majority of the work, which confirms the drift/carry identity
- Osmium is profitable but far less developed than the `R2_10` line
- the main value here is structural clarity: the file is much easier to reason about and extend

Artifacts:
- [R2_12 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_12_day_-1/metrics.json)
- [R2_12 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_12_day_0/metrics.json)
- [R2_12 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_12_day_1/metrics.json)

## `TradervR2_13`

First build-up on top of the clean restart baseline:
- keep [TradervR2_12.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_12.py) structure
- upgrade only Pepper using the stronger Round 2 carry/schedule logic from the older branch
- leave the simple restart Osmium unchanged

New file:
- [TradervR2_13.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_13.py)

Public Round 2 deterministic replay (`rust` engine):
- day `-1`: total `86'529.0`
  - `ASH_COATED_OSMIUM`: `7'055.0`
  - `INTARIAN_PEPPER_ROOT`: `79'474.0`
- day `0`: total `85'882.0`
  - `ASH_COATED_OSMIUM`: `6'399.0`
  - `INTARIAN_PEPPER_ROOT`: `79'483.0`
- day `1`: total `85'311.0`
  - `ASH_COATED_OSMIUM`: `5'918.0`
  - `INTARIAN_PEPPER_ROOT`: `79'393.0`

Three-day total:
- `257'722.0`

Comparison against the bare reset baseline:
- [TradervR2_12.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_12.py): `218'217.0`
- [TradervR2_13.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_13.py): `257'722.0`
- delta: `+39'505.0`

Read:
- this recovered almost all of the strong Pepper performance while keeping the simple restart Ash untouched
- the entire gain is Pepper:
  - `R2_12` Pepper: `198'845.0`
  - `R2_13` Pepper: `238'350.0`
- Osmium is identical to `R2_12`, so the next clean build-up step should now be Ash

Artifacts:
- [R2_13 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_13_day_-1/metrics.json)
- [R2_13 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_13_day_0/metrics.json)
- [R2_13 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_13_day_1/metrics.json)

## `TradervR2_14`

Second build-up on top of the restart line:
- keep [TradervR2_13.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_13.py) Pepper unchanged
- add only the first proven Osmium layer back in:
  - stable-gap / imbalance / micro / trade-confirm conviction
  - conviction only affects:
    - take thresholds
    - quote edge on the signal side
    - `+1` front size in strong states
- no toxicity smoothing
- no reentry
- no markout

New file:
- [TradervR2_14.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_14.py)

Public Round 2 deterministic replay (`rust` engine):
- day `-1`: total `86'160.0`
  - `ASH_COATED_OSMIUM`: `6'686.0`
  - `INTARIAN_PEPPER_ROOT`: `79'474.0`
- day `0`: total `85'474.0`
  - `ASH_COATED_OSMIUM`: `5'991.0`
  - `INTARIAN_PEPPER_ROOT`: `79'483.0`
- day `1`: total `85'006.0`
  - `ASH_COATED_OSMIUM`: `5'613.0`
  - `INTARIAN_PEPPER_ROOT`: `79'393.0`

Three-day total:
- `256'640.0`

Comparison:
- [TradervR2_13.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_13.py): `257'722.0`
- [TradervR2_14.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_14.py): `256'640.0`
- delta: `-1'082.0`

Read:
- this conviction-only port does change behavior
- but it makes the clean Ash branch too selective overall
- Pepper is exactly unchanged; all of the giveback is Osmium
- so the next good step is not “more conviction”
- it is probably the next roadmap item instead: toxicity smoothing or a lighter conviction mapping

Artifacts:
- [R2_14 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_14_day_-1/metrics.json)
- [R2_14 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_14_day_0/metrics.json)
- [R2_14 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_14_day_1/metrics.json)

## `TradervR2_15`

Third build-up on top of the clean restart line:
- keep [TradervR2_13.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_13.py) Pepper unchanged
- keep the simple Ash local-fair stack from `R2_13`
- add only a light side-specific toxicity smoothing layer to Ash:
  - raw bid/ask toxicity from imbalance + micro + spread + exposure
  - sticky bid/ask toxicity scores in memory
  - modest shaping of:
    - take thresholds
    - quote width
    - join aggressiveness
    - front size
    - hard side shutdown only in severe exposed states
- no conviction
- no reentry
- no markout

New file:
- [TradervR2_15.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_15.py)

Public Round 2 deterministic replay (`rust` engine):
- day `-1`: total `86'641.0`
  - `ASH_COATED_OSMIUM`: `7'167.0`
  - `INTARIAN_PEPPER_ROOT`: `79'474.0`
- day `0`: total `85'888.0`
  - `ASH_COATED_OSMIUM`: `6'405.0`
  - `INTARIAN_PEPPER_ROOT`: `79'483.0`
- day `1`: total `85'441.0`
  - `ASH_COATED_OSMIUM`: `6'048.0`
  - `INTARIAN_PEPPER_ROOT`: `79'393.0`

Three-day total:
- `257'970.0`

Comparison:
- [TradervR2_13.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_13.py): `257'722.0`
- [TradervR2_15.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_15.py): `257'970.0`
- delta: `+248.0`

Read:
- this is the first Ash add-on in the clean rebuild line that clearly helps instead of hurts
- the entire gain is Osmium:
  - `R2_13` Ash: `19'372.0`
  - `R2_15` Ash: `19'620.0`
- Pepper is exactly unchanged at `238'350.0`
- the improvement is broad rather than one lucky day:
  - `+112.0` on day `-1`
  - `+6.0` on day `0`
  - `+130.0` on day `1`

Artifacts:
- [R2_15 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_15_day_-1/metrics.json)
- [R2_15 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_15_day_0/metrics.json)
- [R2_15 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_15_day_1/metrics.json)

## `TradervR2_16`

Fourth build-up on top of the clean restart line:
- keep [TradervR2_15.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_15.py) Pepper and Ash fair model unchanged
- keep the new light Ash toxicity smoothing
- add only a light Ash re-entry / neutral-drip layer:
  - side-specific fill timestamps from `state.own_trades`
  - `bars_since_buy_fill` / `bars_since_sell_fill`
  - stale-side wake-up only when:
    - the favored side has actually gone quiet
    - toxicity is at most mild
    - spread is still tradable
    - inventory is not stretched
  - tiny micro-nibble when the side signal is strong enough
  - small neutral two-sided drip in quiet low-signal states
  - modest quote push toward the book and small front-size bump during reactivation
- no conviction
- no markout

New file:
- [TradervR2_16.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_16.py)

Public Round 2 deterministic replay (`rust` engine):
- day `-1`: total `86'668.0`
  - `ASH_COATED_OSMIUM`: `7'194.0`
  - `INTARIAN_PEPPER_ROOT`: `79'474.0`
- day `0`: total `86'045.0`
  - `ASH_COATED_OSMIUM`: `6'562.0`
  - `INTARIAN_PEPPER_ROOT`: `79'483.0`
- day `1`: total `85'365.0`
  - `ASH_COATED_OSMIUM`: `5'972.0`
  - `INTARIAN_PEPPER_ROOT`: `79'393.0`

Three-day total:
- `258'078.0`

Comparison:
- [TradervR2_15.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_15.py): `257'970.0`
- [TradervR2_16.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_16.py): `258'078.0`
- delta: `+108.0`

Read:
- this layer is live, but it is a smaller add than toxicity smoothing
- the gain is still entirely Osmium:
  - `R2_15` Ash: `19'620.0`
  - `R2_16` Ash: `19'728.0`
- Pepper is again exactly unchanged at `238'350.0`
- the re-entry logic helped most on day `0`, then gave a bit back on day `1`
- so it looks useful, but more fragile than the toxicity layer underneath it

Artifacts:
- [R2_16 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_16_day_-1/metrics.json)
- [R2_16 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_16_day_0/metrics.json)
- [R2_16 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_16_day_1/metrics.json)

## `TradervR2_17`

Fifth build-up on top of the clean restart line:
- keep [TradervR2_16.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_16.py) Pepper, Ash fair model, toxicity smoothing, and re-entry unchanged
- add only a narrow passive-only Ash markout memory:
  - infer post-fill quality from position change and next mid move
  - keep buy/sell markout EMA separately
  - use bad markout only to:
    - widen passive quote width on that side
    - trim passive size on that side
- no markout penalty on taking
- no hard shutdowns from markout

New file:
- [TradervR2_17.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_17.py)

Public Round 2 deterministic replay (`rust` engine):
- day `-1`: total `86'676.0`
  - `ASH_COATED_OSMIUM`: `7'202.0`
  - `INTARIAN_PEPPER_ROOT`: `79'474.0`
- day `0`: total `86'045.0`
  - `ASH_COATED_OSMIUM`: `6'562.0`
  - `INTARIAN_PEPPER_ROOT`: `79'483.0`
- day `1`: total `85'365.0`
  - `ASH_COATED_OSMIUM`: `5'972.0`
  - `INTARIAN_PEPPER_ROOT`: `79'393.0`

Three-day total:
- `258'086.0`

Comparison:
- [TradervR2_16.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_16.py): `258'078.0`
- [TradervR2_17.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_17.py): `258'086.0`
- delta: `+8.0`

Read:
- this confirms that passive-only markout is directionally compatible with the clean rebuild
- but it is a very small lever on public data so far
- the gain is again entirely Osmium:
  - `R2_16` Ash: `19'728.0`
  - `R2_17` Ash: `19'736.0`
- Pepper stays exactly unchanged at `238'350.0`
- so the bigger wins in the rebuild path are still:
  - Pepper restoration in `R2_13`
  - toxicity smoothing in `R2_15`
  - then re-entry in `R2_16`

Artifacts:
- [R2_17 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_17_day_-1/metrics.json)
- [R2_17 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_17_day_0/metrics.json)
- [R2_17 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_17_day_1/metrics.json)

## `TradervR2_18` and `TradervR2_19`

Alpha-route split experiments on top of [TradervR2_17.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_17.py):

- [TradervR2_18.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_18.py)
  - stronger alpha split
  - `take_alpha` leans much more on micro / imbalance / deeper book flow
  - `quote_alpha` leans more on stable-book center with disagreement damping
- [TradervR2_19.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_19.py)
  - lighter version of the same idea
  - quote path kept closer to the `R2_17` winner
  - take path only modestly shifted toward directional flow

Public Round 2 deterministic replay (`rust` engine):

- `R2_18`
  - day `-1`: total `86'066.0`
    - `ASH_COATED_OSMIUM`: `6'592.0`
    - `INTARIAN_PEPPER_ROOT`: `79'474.0`
  - day `0`: total `85'452.0`
    - `ASH_COATED_OSMIUM`: `5'969.0`
    - `INTARIAN_PEPPER_ROOT`: `79'483.0`
  - day `1`: total `84'981.0`
    - `ASH_COATED_OSMIUM`: `5'588.0`
    - `INTARIAN_PEPPER_ROOT`: `79'393.0`
  - three-day total: `256'499.0`

- `R2_19`
  - day `-1`: total `86'344.0`
    - `ASH_COATED_OSMIUM`: `6'870.0`
    - `INTARIAN_PEPPER_ROOT`: `79'474.0`
  - day `0`: total `85'859.0`
    - `ASH_COATED_OSMIUM`: `6'376.0`
    - `INTARIAN_PEPPER_ROOT`: `79'483.0`
  - day `1`: total `85'126.0`
    - `ASH_COATED_OSMIUM`: `5'733.0`
    - `INTARIAN_PEPPER_ROOT`: `79'393.0`
  - three-day total: `257'329.0`

Comparison:
- [TradervR2_17.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_17.py): `258'086.0`
- [TradervR2_18.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_18.py): `256'499.0`
- [TradervR2_19.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_19.py): `257'329.0`

Read:
- separating Ash alpha paths did change behavior
- but both tested versions underperformed the `R2_17` trunk
- the heavier split in `R2_18` clearly over-rotated the engine away from the current winner
- the lighter split in `R2_19` was less bad, but still gave back meaningful Ash PnL
- Pepper stayed exactly unchanged in both, so the entire miss is Osmium
- current conclusion: the clean rebuild benefits more from execution-quality layers than from splitting Ash alpha more aggressively

Artifacts:
- [R2_18 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_18_day_-1/metrics.json)
- [R2_18 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_18_day_0/metrics.json)
- [R2_18 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_18_day_1/metrics.json)
- [R2_19 day -1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_19_day_-1/metrics.json)
- [R2_19 day 0 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_19_day_0/metrics.json)
- [R2_19 day 1 metrics](/Users/xavierwinkelmann/Prosperity/TraderFactory/generated/runs/deterministic/rust/TradervR2_19_day_1/metrics.json)
