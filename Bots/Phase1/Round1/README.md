# Round 1 Versions

This folder tracks the dedicated Round 1 bots for:
- `ASH_COATED_OSMIUM`
- `INTARIAN_PEPPER_ROOT`

## Product Read

`ASH_COATED_OSMIUM`
- behaves like a stable anchor product around `10,000`
- wide but fairly regular spread
- best first approach is fixed-fair market making with inventory control

`INTARIAN_PEPPER_ROOT`
- shows a very persistent intraday upward drift of about `+1000` over a full day
- still oscillates around that drift line in a structured way
- best first approach is trend-line fair value plus residual-to-trend execution

## Version Log

### `TradervR1_1.py`

Idea:
- reuse the clean tutorial-bot structure rather than the tangled late-stage hybrids
- trade `ASH_COATED_OSMIUM` as a stable reference-value market maker
- trade `INTARIAN_PEPPER_ROOT` with:
  - a session anchor inferred from the opening level
  - a slow linear drift fair model
  - residual EMA around that drift
  - microprice / imbalance adjustments
  - bullish one-sided quoting when the uptrend is intact

Notes:
- this is intentionally a first clean Round 1 baseline, not a heavily optimized branch yet
- no separate auction-clearing module was added in this first pass because the current dataset and bot interface expose only continuous book snapshots; auction logic can be layered in once we confirm the exact auction API / timing

### `TradervR1_2.py`

Idea:
- keep the exact same clean structure as `TradervR1_1.py`
- promote only the focused TraderFactory CMA-ES calibration changes
- keep the strategy interpretable:
  - slightly faster Pepper Root drift tracking
  - slightly stronger residual adaptation
  - a bit less punitive sell-side trimming in Pepper Root
  - slightly more selective but more trend-aligned quoting and taking
  - slightly softer Osmium inventory skew

Verified local Rust replay:
- day `-2`: `74'472.5`
- day `-1`: `77'509.0`
- day `0`: `75'682.0`

Notes:
- this is the first optimization-driven Round 1 follow-up
- the parameter move is narrow; architecture and memory format are unchanged from `TradervR1_1.py`
- official website log extraction is still pending because the game page is not accessible without your logged-in browser session from this environment

### `TradervR1_3.py`

Idea:
- use the Round 1 market-analysis findings more literally
- `INTARIAN_PEPPER_ROOT`:
  - explicit time-based fair from the opening 1000-level plus `timestamp / 1000`
  - buy below fair, sell above fair
  - keep a mild early long bias, then flatten progressively later in the day
- `ASH_COATED_OSMIUM`:
  - fixed anchor around `10000`
  - add top-of-book imbalance and microprice skew to fair

Important data note:
- rows where both best bid and best ask are missing imply `mid_price = 0.0`
- the bot naturally ignores those snapshots because `Book.valid` is false whenever either side is missing

Verified local Rust replay:
- day `-2`: `26'485.5`
- day `-1`: `28'471.0`
- day `0`: `26'349.0`

Read:
- this version is cleaner and closer to the dataset story
- but it underperformed `TradervR1_2.py`
- the main giveback came from `INTARIAN_PEPPER_ROOT`, where the more literal time-fair/mean-reversion engine captured less than the tuned hybrid

### `TradervR1_8.py`

Idea:
- promote the best focused TraderFactory CMA-ES candidate found from `TradervR1_5.py`
- keep the same architecture and memory schema
- tune only the pricing, carry, overextension, and inventory constants

What moved:
- `ASH_COATED_OSMIUM`
  - slightly tighter base edge
  - slightly stronger imbalance fair skew
  - slightly stronger inventory skew
- `INTARIAN_PEPPER_ROOT`
  - slightly faster trend tracking
  - slightly stronger early long bias
  - slightly stronger sell-side overextension control
  - slightly higher inventory skew
  - slightly more patient overextension threshold
  - slightly lower bullish-imbalance trigger

Verified local Rust replay:
- day `-2`: `89'067.0`
  - `ASH_COATED_OSMIUM`: `9'482.0`
  - `INTARIAN_PEPPER_ROOT`: `79'585.0`
- day `-1`: `90'939.0`
  - `ASH_COATED_OSMIUM`: `11'457.0`
  - `INTARIAN_PEPPER_ROOT`: `79'482.0`
- day `0`: `89'637.0`
  - `ASH_COATED_OSMIUM`: `10'224.0`
  - `INTARIAN_PEPPER_ROOT`: `79'413.0`

Read:
- this is currently the strongest promoted Round 1 local bot in this folder
- the gain came mostly from a more stable and better-monetized `INTARIAN_PEPPER_ROOT` profile, while `ASH_COATED_OSMIUM` also improved modestly

## Comparison Sweep: `v3` to `v6`

Local Rust replay across all Round 1 days:

| Bot | Day -2 | Day -1 | Day 0 | Notes |
| --- | ---: | ---: | ---: | --- |
| `TradervR1_3.py` | `26'485.5` | `28'471.0` | `26'349.0` | clean literal time-fair version, but clearly weaker |
| `TradervR1_4.py` | `81'104.5` | `83'954.0` | `81'912.0` | first strong high-capture branch |
| `TradervR1_5.py` | `81'809.5` | `84'382.0` | `82'635.0` | best among `v3` to `v6` |
| `TradervR1_6.py` | `81'809.5` | `84'382.0` | `82'635.0` | identical to `v5` locally |

Product split:

- `TradervR1_3.py`
  - day `-2`: `ASH_COATED_OSMIUM 8'767.5`, `INTARIAN_PEPPER_ROOT 17'718.0`, trades `981`
  - day `-1`: `ASH_COATED_OSMIUM 10'979.0`, `INTARIAN_PEPPER_ROOT 17'492.0`, trades `1'038`
  - day `0`: `ASH_COATED_OSMIUM 9'450.0`, `INTARIAN_PEPPER_ROOT 16'899.0`, trades `977`
- `TradervR1_4.py`
  - day `-2`: `ASH_COATED_OSMIUM 8'767.5`, `INTARIAN_PEPPER_ROOT 72'337.0`, trades `794`
  - day `-1`: `ASH_COATED_OSMIUM 10'979.0`, `INTARIAN_PEPPER_ROOT 72'975.0`, trades `856`
  - day `0`: `ASH_COATED_OSMIUM 9'450.0`, `INTARIAN_PEPPER_ROOT 72'462.0`, trades `840`
- `TradervR1_5.py`
  - day `-2`: `ASH_COATED_OSMIUM 8'855.0`, `INTARIAN_PEPPER_ROOT 72'954.5`, trades `798`
  - day `-1`: `ASH_COATED_OSMIUM 10'720.0`, `INTARIAN_PEPPER_ROOT 73'662.0`, trades `850`
  - day `0`: `ASH_COATED_OSMIUM 9'358.0`, `INTARIAN_PEPPER_ROOT 73'277.0`, trades `835`
- `TradervR1_6.py`
  - identical to `TradervR1_5.py` on all three local days

Read:
- `v5` is the strongest version in the `v3` to `v6` band
- `v6` does not add a measurable local improvement over `v5`
- the real jump happened between `v3` and `v4`, almost entirely through a much stronger `INTARIAN_PEPPER_ROOT` engine

## Saved Log Analysis

Saved official-style logs found in this folder:
- `TradervR1_5.log`
- `TradervR1_6.log`
- `TradervR1_7.log`
- `TradervR1_8.log`

Final totals from those saved logs:

| Log | Final Total | ASH_COATED_OSMIUM | INTARIAN_PEPPER_ROOT | Max Drawdown |
| --- | ---: | ---: | ---: | ---: |
| `TradervR1_5.log` | `9'185.688` | `1'716.688` | `7'469.000` | `248.527` |
| `TradervR1_6.log` | `8'687.438` | `1'758.812` | `6'928.625` | `182.559` |
| `TradervR1_7.log` | `9'227.812` | `1'758.812` | `7'469.000` | `248.527` |
| `TradervR1_8.log` | `9'314.094` | `1'824.094` | `7'490.000` | `248.527` |

Checkpoint read:
- `v8` leads at every major checkpoint we checked (`10k`, `20k`, `40k`, `60k`, `80k`)
- `v6` is smoother but clearly gives up too much upside
- `v7` already recovered most of the `v6` giveback, but `v8` improved both products again

Takeaway:
- among the saved logs, `TradervR1_8` is the strongest transfer candidate
- the next optimization trunk should therefore be `TradervR1_8.py`, not `v5` or `v6`

### `TradervR1_9.py`

Idea:
- use `TradervR1_8.py` as the trunk
- run one tighter TraderFactory CMA-ES pass around the already-good parameters
- preserve the strong shape from the saved logs rather than opening a wide search again

What changed from `v8`:
- `ASH_COATED_OSMIUM`
  - slightly tighter base edge again
  - slightly lower imbalance-fair weight
  - slightly higher inventory skew
- `INTARIAN_PEPPER_ROOT`
  - marginally softer drift/residual response
  - slightly lower early long bias
  - slightly higher sell-side overextension penalty
  - slightly lower inventory skew
  - slightly wider quote/take edges
  - slightly higher overextension threshold
  - slightly lower bullish trigger

Verified local Rust replay:
- day `-2`: `89'314.0`
- day `-1`: `91'183.0`
- day `0`: `89'899.0`

Read:
- this is a modest but real improvement over `TradervR1_8.py`
- the gain is narrow and believable, which is exactly what we want from a second optimization pass on a strong trunk

### `TradervR1_11.py`

Idea:
- use `TradervR1_9.py` as the base
- keep `INTARIAN_PEPPER_ROOT` unchanged as the stronger carry-and-overlay engine
- rebuild only `ASH_COATED_OSMIUM` into a clearer three-state engine:
  - calm-book passive MM
  - toxic-book one-sided defense
  - dislocation sniper

What changed from `v9`:
- `INTARIAN_PEPPER_ROOT`
  - unchanged
- `ASH_COATED_OSMIUM`
  - lower imbalance fair weight so fair is less jumpy
  - tighter calm-book quoting and larger calm-book size
  - explicit toxic-book defensive mode with one-sided quoting
  - explicit dislocation mode that takes harder, then backs off passive quoting
  - medium-aggression inventory handling between the earlier conservative and aggressive versions

Verified local Rust replay:
- day `-2`: `93'738.0`
  - `ASH_COATED_OSMIUM`: `14'153.0`
  - `INTARIAN_PEPPER_ROOT`: `79'585.0`
  - trades: `645`
- day `-1`: `95'427.0`
  - `ASH_COATED_OSMIUM`: `15'912.0`
  - `INTARIAN_PEPPER_ROOT`: `79'515.0`
  - trades: `666`
- day `0`: `93'546.0`
  - `ASH_COATED_OSMIUM`: `14'129.0`
  - `INTARIAN_PEPPER_ROOT`: `79'417.0`
  - trades: `645`

Read:
- this is a large step up over `TradervR1_9.py`
- the gain came almost entirely from a much stronger `ASH_COATED_OSMIUM` engine
- `INTARIAN_PEPPER_ROOT` stayed very stable, which is exactly the hybrid we wanted

## Official Log Read: `v10` vs `v11`

Saved official-style logs:
- `TradervR1_10.log`: `9'985.28125`
- `TradervR1_11.log`: `9'720.53125`

Breakdown:
- `TradervR1_10.log`
  - `ASH_COATED_OSMIUM`: `2'471.28125`
  - `INTARIAN_PEPPER_ROOT`: `7'514.0`
- `TradervR1_11.log`
  - `ASH_COATED_OSMIUM`: `2'230.53125`
  - `INTARIAN_PEPPER_ROOT`: `7'490.0`

Trade-quality read:
- the loss was almost entirely `ASH_COATED_OSMIUM`
- `v11` traded more, but at worse prices on both sides
- `v10` captured better Osmium spread while keeping Pepper essentially unchanged

Checkpoint read:
- `v10` leads `v11` at every major checkpoint (`10k`, `20k`, `40k`, `60k`, `80k`, finish)
- `v11` is not collapsing; it is simply a bit too intervention-heavy and lower quality

Takeaway:
- `ASH_COATED_OSMIUM` likes the tighter, simpler `v10` spirit better than the fuller `v11` regime engine
- the next improvement path should be small, selective Osmium changes, not another larger rewrite

### `TradervR1_12.py`

Idea:
- use `TradervR1_10.py` as the trunk
- keep the strong simple structure
- add only a narrow Osmium protective overlay:
  - faster retreat in clearly toxic books
  - no back-layer quoting in toxic books
  - slightly larger takes only on obvious dislocations

Verified local Rust replay:
- day `-2`: `95'731.5`
- day `-1`: `96'456.0`
- day `0`: `95'297.0`

Read:
- better than `v11`
- but still slightly worse than `v10` on all three days
- useful conclusion: the right next path is still `v10`, but with even smaller Osmium adjustments than this

### `TradervR1_13.py`

Idea:
- use `TradervR1_10.py` as the trunk
- test a Pepper-only late-day overlay unwind while preserving a hard core long inventory

Verified local Rust replay:
- day `-2`: `95'984.0`
- day `-1`: `96'517.0`
- day `0`: `95'435.0`

Read:
- completely inert relative to `v10`
- useful conclusion: Pepper is not the main missing edge right now
- the next real gains are more likely to come from Osmium execution quality

### `TradervR1_14.py`

Idea:
- use `TradervR1_12.py` as the optimization trunk
- run a narrow TraderFactory CMA-ES pass focused almost entirely on `ASH_COATED_OSMIUM`
- let Pepper stay structurally unchanged

TraderFactory artifacts:
- config: `TraderFactory/configs/round1/tradervr1_12_cmaes_fast.json`
- report: `Analysis/output/round1_tradervr1_12_cmaes_fast/round1_tradervr1_12_cmaes_fast_report.md`
- result json: `Analysis/output/round1_tradervr1_12_cmaes_fast/round1_tradervr1_12_cmaes_fast_best.json`

What moved:
- `ASH_COATED_OSMIUM`
  - slightly lower base edge
  - almost unchanged front size
  - almost unchanged inventory skew
  - slightly less punitive toxic retreat edge
  - slightly higher dislocation threshold
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay from TraderFactory:
- day `-2`: `95'863.5`
- day `-1`: `96'566.0`
- day `0`: `95'383.0`

Smoke check on promoted file:
- `TradervR1_14.py` day `-1`: `96'566.0`

Read:
- this is a small but real improvement over `TradervR1_12.py`
- the gain is narrow and believable
- the optimization result reinforces the same lesson from the logs: Round 1 gains are currently coming from subtle Osmium execution calibration, not Pepper redesign

### `TradervR1_15.py`

Idea:
- use `TradervR1_10.py` as the trunk
- test an explicit Pepper hoarding rule-set:
  - hard minimum core hold of `50`
  - overlay band of `15`
  - no selling before mid-day unless inventory is above `65`
  - bullish sells capped to tiny overlay clips
  - late-day unwind only when residual z-score is clearly rich

Verified local Rust replay:
- day `-2`: `95'984.0`
- day `-1`: `96'517.0`
- day `0`: `95'435.0`

Read:
- completely inert relative to `TradervR1_10.py`
- useful conclusion: `v10` is already effectively behaving like a core-hold Pepper bot
- this strongly suggests the next real improvement path is still Osmium, not more Pepper hoarding logic

### `TradervR1_16.py`

Idea:
- use `TradervR1_10.py` as the trunk
- rebuild only Pepper into three explicit layers:
  - drift estimator
  - target inventory scheduler
  - action-based executor choosing among `aggressive_buy`, `passive_buy`, `hold`, and `overlay_sell`

Verified local Rust replay:
- day `-2`: `94'496.0`
  - `ASH_COATED_OSMIUM`: `16'340.0`
  - `INTARIAN_PEPPER_ROOT`: `78'156.0`
- day `-1`: `94'973.0`
  - `ASH_COATED_OSMIUM`: `17'149.0`
  - `INTARIAN_PEPPER_ROOT`: `77'824.0`
- day `0`: `93'843.0`
  - `ASH_COATED_OSMIUM`: `16'047.0`
  - `INTARIAN_PEPPER_ROOT`: `77'796.0`

Read:
- Osmium stayed identical to `v10`
- all the loss came from Pepper
- the control-style Pepper design was cleaner architecturally, but it gave up too much carry / monetization
- practical takeaway: this explicit action split is interesting research, but not yet better than the simpler Pepper engine in `v10`

### `TradervR1_17.py`

Idea:
- rebuild Pepper around a small hidden-state style filter:
  - `steady_up`
  - `strong_up`
  - `noisy_rich`
- keep Osmium unchanged
- use the filtered state probabilities to drive:
  - target inventory
  - aggressive-buy permission
  - overlay-sell permission
  - quote widths
- keep fair value trend-dominant and use the filter mainly as a smoother execution/target layer

Verified local Rust replay:
- day `-2`: `94'833.0`
  - `ASH_COATED_OSMIUM`: `16'340.0`
  - `INTARIAN_PEPPER_ROOT`: `78'493.0`
- day `-1`: `95'520.0`
  - `ASH_COATED_OSMIUM`: `17'149.0`
  - `INTARIAN_PEPPER_ROOT`: `78'371.0`
- day `0`: `94'199.0`
  - `ASH_COATED_OSMIUM`: `16'047.0`
  - `INTARIAN_PEPPER_ROOT`: `78'152.0`

Read:
- clearly better than the earlier threshold-based `v17`
- still below `TradervR1_10.py`
- all the remaining gap is still Pepper, not Osmium
- useful conclusion: the probability filter is a better direction than hard regime thresholds, but the current implementation still leaves carry on the table versus the simpler production Pepper engine

### `TradervR1_17` TraderFactory Research

Idea:
- use `TradervR1_17.py` as a Pepper-only research trunk
- try two narrow TraderFactory CMA-ES searches before rewriting more code:
  - one on HMM-style state / target / unwind knobs
  - one on Pepper fair / carry-capture / execution knobs

TraderFactory artifacts:
- state-filter config: `TraderFactory/configs/round1/tradervr1_17_cmaes_research.json`
- state-filter report: `Analysis/output/round1_tradervr1_17_cmaes_research/round1_tradervr1_17_cmaes_research_report.md`
- state-filter result json: `Analysis/output/round1_tradervr1_17_cmaes_research/round1_tradervr1_17_cmaes_research_best.json`
- execution config: `TraderFactory/configs/round1/tradervr1_17_cmaes_execution.json`
- execution report: `Analysis/output/round1_tradervr1_17_cmaes_execution/round1_tradervr1_17_cmaes_execution_report.md`
- execution result json: `Analysis/output/round1_tradervr1_17_cmaes_execution/round1_tradervr1_17_cmaes_execution_best.json`

Result:
- both searches returned the current defaults exactly
- baseline and best candidate were identical:
  - day `-2`: `94'833.0`
  - day `-1`: `95'520.0`
  - day `0`: `94'199.0`

Read:
- this is a strong sign that `v17` is not mainly underperforming because of bad parameter calibration
- the remaining gap looks structural, especially in Pepper execution/fair ownership, not just numeric tuning

### `TradervR1_18.py`

Idea:
- take the structural execution concerns seriously and patch Pepper without changing Osmium
- main fixes:
  - unify overlay thresholds between `_execution_mode()` and `build_orders()`
  - wire `PASSIVE_BUY_EDGE` into the real passive-buy quote behavior
  - make the reload cooldown explicit rather than EMA-soft on the first repeat
  - change the hidden-state observation from raw return to drift shock
  - reduce `p_strong` influence on fair so state acts more through target/execution than through fair drift

Verified local Rust replay:
- day `-2`: `94'710.0`
  - `ASH_COATED_OSMIUM`: `16'340.0`
  - `INTARIAN_PEPPER_ROOT`: `78'370.0`
- day `-1`: `95'443.0`
  - `ASH_COATED_OSMIUM`: `17'149.0`
  - `INTARIAN_PEPPER_ROOT`: `78'294.0`
- day `0`: `94'024.0`
  - `ASH_COATED_OSMIUM`: `16'047.0`
  - `INTARIAN_PEPPER_ROOT`: `77'977.0`

Read:
- cleaner structurally, but slightly worse on all three days than `TradervR1_17.py`
- the combined package likely pushed too many changes at once
- most likely the drift-shock observation and fair simplification removed more useful carry capture than the execution cleanup recovered

### `TradervR1_19.py`

Idea:
- isolate the execution-structure fixes from `v18`
- keep the old `v17` state observation and fair logic
- only keep:
  - unified overlay thresholds
  - real `PASSIVE_BUY_EDGE` wiring
  - explicit reload cooldown
  - removal of the dead progress placeholder in `_execution_mode()`

Verified local Rust replay:
- day `-2`: `94'717.0`
- day `-1`: `95'443.0`
- day `0`: `94'024.0`

Read:
- slightly better than `v18` on day `-2`, identical on the other two days
- still below `TradervR1_17.py`
- useful conclusion: the structural fixes are reasonable, but they are not the missing edge by themselves
- the stronger next path is probably not more Pepper control cleanup alone, but either:
  - a better Pepper carry/fair design
  - or going back to the stronger `TradervR1_10.py` / `TradervR1_14.py` trunk for production

### `TradervR1_20.py`

Idea:
- continue from the `v17` Pepper research line, but push directly on carry capture instead of plumbing
- main change:
  - add a more explicit early carry floor
  - keep a higher long target through the day
  - reduce rich-side trimming
  - delay and soften late unwind
  - widen sell suppression in bullish / under-target states

Verified local Rust replay:
- day `-2`: `94'833.0`
  - `ASH_COATED_OSMIUM`: `16'340.0`
  - `INTARIAN_PEPPER_ROOT`: `78'493.0`
- day `-1`: `95'520.0`
  - `ASH_COATED_OSMIUM`: `17'149.0`
  - `INTARIAN_PEPPER_ROOT`: `78'371.0`
- day `0`: `94'228.0`
  - `ASH_COATED_OSMIUM`: `16'047.0`
  - `INTARIAN_PEPPER_ROOT`: `78'181.0`

Read:
- essentially identical to `TradervR1_17.py` on days `-2` and `-1`
- small Pepper gain on day `0`
- useful conclusion: stronger carry retention is directionally right, but on the `v17` trunk it only helps at the margin

### `TradervR1_21.py`

Idea:
- another carry-capture attempt on the `v17` branch
- keep the carry-floor idea, but also move fair a bit closer to the stronger `v10` trend-dominant blend

Verified local Rust replay:
- day `-2`: `94'826.0`
  - `ASH_COATED_OSMIUM`: `16'340.0`
  - `INTARIAN_PEPPER_ROOT`: `78'486.0`
- day `-1`: `95'520.0`
  - `ASH_COATED_OSMIUM`: `17'149.0`
  - `INTARIAN_PEPPER_ROOT`: `78'371.0`
- day `0`: `94'228.0`
  - `ASH_COATED_OSMIUM`: `16'047.0`
  - `INTARIAN_PEPPER_ROOT`: `78'181.0`

Read:
- almost identical to `TradervR1_20.py`
- tiny giveback on day `-2`, identical on the other two days
- the `v10`-style fair blend alone is not enough to lift the `v17` family materially

Current takeaway:
- the carry-capture direction is correct
- but the stronger production edge still lives in `TradervR1_10.py`
- if we want a real Round 1 gain from here, the next highest-probability move is:
  - keep the `TradervR1_10.py` Pepper engine as the trunk
  - add only a very small state-aware sell veto / late-unwind layer from the research family
  - do not keep iterating on `v17` as the main production path

### `TradervR1_22.py`

Idea:
- build the exact selective hybrid we wanted:
  - keep `TradervR1_10.py` as the production trunk
  - import only a light Pepper state filter from the newer research branch
  - use that filter only for:
    - small target bonus in stronger steady/strong conditions
    - sell veto in good carry states
    - late unwind permission only when the Pepper state looks noisy/rich enough
- keep `ASH_COATED_OSMIUM` unchanged

Verified local Rust replay:
- day `-2`: `95'984.0`
  - `ASH_COATED_OSMIUM`: `16'340.0`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
- day `-1`: `96'517.0`
  - `ASH_COATED_OSMIUM`: `17'149.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
- day `0`: `95'435.0`
  - `ASH_COATED_OSMIUM`: `16'047.0`
  - `INTARIAN_PEPPER_ROOT`: `79'388.0`

Read:
- effectively identical to `TradervR1_10.py`
- this is still useful information:
  - the selective merge is safe
  - but it does not create a new edge by itself
  - so the research-branch state filter is either redundant with `v10` behavior or too weak to alter real execution

Practical takeaway:
- `TradervR1_10.py` remains the stronger trunk
- a simple `v10 + small research veto` merge is not enough to lift Round 1 further

### `TradervR1_23.py`

Idea:
- test whether Pepper simply needs to hold inventory longer on the strong `v10` trunk
- raise sell resistance while under/near target
- delay late trimming and require richer conditions to unwind

Verified local Rust replay:
- day `-2`: `95'984.0`
- day `-1`: `96'517.0`
- day `0`: `95'435.0`

Read:
- completely inert relative to `TradervR1_10.py`
- useful conclusion: `v10` is already holding Pepper about as long as this execution style allows

### `TradervR1_24.py`

Idea:
- extreme hold-long experiment on top of `v10`
- force a minimum Pepper hold until very late in the day
- strongly suppress almost all sells unless the price is very rich

Verified local Rust replay:
- day `-2`: `95'984.0`
- day `-1`: `96'517.0`
- day `0`: `95'435.0`

Read:
- still completely inert
- strong evidence that “hold longer” is already saturated in this branch

### `TradervR1_25.py`

Idea:
- cheaper Pepper accumulation instead of longer holding
- be more selective about aggressive buys early
- push harder for passive bid fills near the front of the book
- use slightly larger passive buy size when below target during the main accumulation phase

Verified local Rust replay:
- day `-2`: `95'942.0`
- day `-1`: `96'474.0`
- day `0`: `95'398.0`

Read:
- this one finally changed the path, but slightly for the worse on all three days
- practical takeaway: Pepper entry quality is a real lever, but this version became too price-sensitive and gave up too much drift participation

### `TradervR1_25_1.py`

Idea:
- soften the cheaper-accumulation experiment from `v25`
- keep the same direction:
  - slightly fewer mediocre aggressive buys
  - slightly better passive buy placement
  - slightly more passive buy size when below target
- but reduce every intervention so Pepper still participates in the drift

Verified local Rust replay:
- day `-2`: `95'968.0`
- day `-1`: `96'517.0`
- day `0`: `95'420.0`

Read:
- this is clearly better than `TradervR1_25.py`
- but it is still not better than `TradervR1_10.py`
- useful conclusion: Pepper accumulation quality is a live lever, but the sweet spot is very narrow

### `TradervR1_25_2.py`

Idea:
- start from `TradervR1_25_1.py`
- keep the softer passive-buy improvement
- remove almost all of the extra aggressive-buy penalty

Verified local Rust replay:
- day `-2`: `95'984.0`
  - `ASH_COATED_OSMIUM`: `16'340.0`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
- day `-1`: `96'517.0`
  - `ASH_COATED_OSMIUM`: `17'149.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
- day `0`: `95'444.0`
  - `ASH_COATED_OSMIUM`: `16'047.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`

Read:
- this gets fully back to the `TradervR1_10.py` line on days `-2` and `-1`
- and is slightly better on day `0`
- practical takeaway: the passive-accumulation improvement is fine, but the aggressive-buy penalty had to be almost fully removed

### `TradervR1_26_*` Osmium Research Branch

Idea:
- start a dedicated Osmium research branch while keeping Pepper fixed on the strong `TradervR1_25_2.py` trunk
- map different academic ideas into separate `ASH_COATED_OSMIUM` engines and compare them cleanly

Baseline for comparison:
- [TradervR1_25_2.py](./TradervR1_25_2.py)
  - day `-2`: `95'984.0`
  - day `-1`: `96'517.0`
  - day `0`: `95'444.0`
  - three-day sum: `287'945.0`

#### `TradervR1_26_as.py`

Paper idea:
- Avellaneda-Stoikov style reservation price and half-spread from risk / fill elasticity proxies

What changed:
- keep fair anchored to `10000`
- compute A-S style reservation from inventory, volatility proxy, and depth-based `k`
- compute passive half-spread from the same reactive terms

Verified local Rust replay:
- day `-2`: `76'541.5`
- day `-1`: `78'770.0`
- day `0`: `75'189.0`
- three-day sum: `230'500.5`

Read:
- clearly broken for this market
- Osmium collapses badly, including negative Osmium PnL on days `-2` and `0`
- practical takeaway: a literal A-S style reactive spread is far too aggressive / unstable here

#### `TradervR1_26_glft.py`

Paper idea:
- Guéant-Lehalle-Fernandez-Tapia style nonlinear inventory pressure

What changed:
- replace linear inventory skew with a nonlinear inventory map
- widen same-side quotes faster as inventory stress rises
- move toward one-sided quoting near the soft limit

Verified local Rust replay:
- day `-2`: `95'832.5`
  - `ASH_COATED_OSMIUM`: `16'188.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
- day `-1`: `96'775.0`
  - `ASH_COATED_OSMIUM`: `17'407.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
- day `0`: `95'014.0`
  - `ASH_COATED_OSMIUM`: `15'617.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
- three-day sum: `287'621.5`

Read:
- this is the most promising paper path
- it improves day `-1` by improving Osmium only
- but it gives back more than that on days `-2` and `0`
- practical takeaway: nonlinear inventory pressure is a real signal, but this first calibration is not yet robust enough to beat the trunk

#### `TradervR1_26_cks.py`

Paper idea:
- Cont-Kukanov-Stoikov depth-aware imbalance fair

What changed:
- replace fixed imbalance skew with depth-scaled imbalance impact
- increase fair movement when top-of-book depth is thinner

Verified local Rust replay:
- day `-2`: `95'764.5`
- day `-1`: `96'387.0`
- day `0`: `95'178.0`
- three-day sum: `287'329.5`

Read:
- safe and reasonably competitive
- but still below the trunk on all-day sum
- practical takeaway: depth-aware fair is directionally sensible, but by itself not enough

#### `TradervR1_26_lm.py`

Paper idea:
- Lehalle-Mounjid style toxicity, cancel, and reinsert logic

What changed:
- retreat faster from toxic queue states
- reinsert farther back on the toxic side
- reduce willingness to sit in clearly adverse passive positions

Verified local Rust replay:
- day `-2`: `95'075.0`
- day `-1`: `95'300.0`
- day `0`: `94'624.0`
- three-day sum: `284'999.0`

Read:
- too defensive
- it cuts Osmium participation and loses real PnL
- practical takeaway: toxicity defense matters, but this layer alone over-retreats

#### `TradervR1_26_delise.py`

Paper idea:
- DeLise-style passive fill penalty / adverse markout gating

What changed:
- add a passive fill penalty proxy based on imbalance, toxicity, and depth
- only allow passive quotes when estimated net edge stays positive after that penalty

Verified local Rust replay:
- day `-2`: `95'984.0`
- day `-1`: `96'517.0`
- day `0`: `95'444.0`
- three-day sum: `287'945.0`

Read:
- completely inert relative to the trunk
- practical takeaway: the current passive fill penalty proxy is either too weak or already implicit in the existing Osmium logic

#### `TradervR1_26_combo.py`

Paper idea:
- combine the main paper ideas in one engine:
  - depth-aware fair
  - nonlinear inventory pressure
  - toxicity retreat
  - passive fill penalty gating

Verified local Rust replay:
- day `-2`: `94'732.0`
- day `-1`: `95'515.0`
- day `0`: `93'832.0`
- three-day sum: `284'079.0`

Read:
- combining everything at once makes the engine too defensive and too noisy
- practical takeaway: the ideas do not compose well naively; they need to be layered much more selectively

#### `TradervR1_26_glft_zones.py`

Idea:
- follow up only on the promising GLFT path
- soften the nonlinear inventory engine into inventory zones so pressure only activates outside a neutral band

Verified local Rust replay:
- day `-2`: `94'095.0`
- day `-1`: `96'020.0`
- day `0`: `92'719.0`

Read:
- worse than the always-on GLFT version
- practical takeaway: the useful edge was the nonlinear inventory shaping itself, not delayed activation

### Osmium Branch Read

What survived the branch best:
- `TradervR1_26_glft.py` is the only paper variant with a real positive local signal
- `TradervR1_26_delise.py` is effectively neutral
- `TradervR1_26_cks.py` is safe but not strong enough
- `TradervR1_26_as.py` is clearly the wrong direction for this simulator

Best current takeaway:
- the strongest next Osmium path is:
  - keep the `TradervR1_25_2.py` / `TradervR1_10.py` trunk
  - borrow only the nonlinear inventory pressure idea from `TradervR1_26_glft.py`
  - tune that very narrowly instead of adding more paper layers all at once

### `TradervR1_27.py`

Idea:
- build the narrow hybrid suggested by the `v26` branch
- keep the full `TradervR1_25_2.py` trunk intact
- keep `INTARIAN_PEPPER_ROOT` exactly unchanged
- import only a mild nonlinear inventory-pressure overlay into `ASH_COATED_OSMIUM`:
  - small cubic inventory pressure added to reservation price
  - light same-side / opposite-side quote asymmetry from inventory ratio
  - no broader GLFT execution rewrite

Verified local Rust replay:
- day `-2`: `95'942.5`
  - `ASH_COATED_OSMIUM`: `16'298.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
- day `-1`: `96'328.0`
  - `ASH_COATED_OSMIUM`: `16'960.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
- day `0`: `95'565.0`
  - `ASH_COATED_OSMIUM`: `16'168.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
- three-day sum: `287'835.5`

Read:
- this hybrid is safe and clearly much better than the full `TradervR1_26_glft.py` rewrite
- it improves `ASH_COATED_OSMIUM` on day `0`
- but it is still slightly below `TradervR1_25_2.py` on the three-day total

Practical takeaway:
- the nonlinear inventory idea does belong in the Osmium trunk
- but only as a very light overlay
- this first blend is close, though not yet a true upgrade

### `TradervR1_27.x` inventory-pressure sweep

Idea:
- narrow local sweep around the two new Osmium-only hybrid knobs in `TradervR1_27.py`
- keep Pepper fixed
- only change:
  - `INV_PRESSURE_A1`
  - `INV_PRESSURE_A3`

Sweep results:
- `TradervR1_27.py`: `95'942.5 / 96'328.0 / 95'565.0`
  - sum: `287'835.5`
- `TradervR1_27_1.py`: `95'951.5 / 96'414.0 / 95'513.0`
  - sum: `287'878.5`
- `TradervR1_27_2.py`: `95'883.0 / 96'342.0 / 95'472.0`
  - sum: `287'697.0`
- `TradervR1_27_3.py`: `95'905.5 / 96'354.0 / 95'601.0`
  - sum: `287'860.5`
- `TradervR1_27_4.py`: `95'914.0 / 96'399.0 / 95'550.0`
  - sum: `287'863.0`

Reference:
- `TradervR1_25_2.py`: `95'984.0 / 96'517.0 / 95'444.0`
  - sum: `287'945.0`

Read:
- none of the sweep variants beat `TradervR1_25_2.py`
- the best overall was `TradervR1_27_1.py`
- `TradervR1_27_4.py` had the strongest day `-1` Osmium result in the sweep, but did not hold that edge across the full three-day view

Practical takeaway:
- the hybrid wants a soft inventory-pressure overlay, not a strong one
- the direction is real, but the gain is too small and too inconsistent so far
- `TradervR1_25_2.py` remains the production trunk for now

### `TradervR1_28.py`

Idea:
- rebuild `ASH_COATED_OSMIUM` into an explicit 4-state anchored execution engine
- keep `INTARIAN_PEPPER_ROOT` unchanged from the strong trunk
- Osmium states:
  - `normal_mm`
  - `stretched_mean_revert`
  - `toxic_defense`
  - `wide_spread_harvest`
- keep fair simple around `10000`
- move adaptation into execution state, quote width, and take behavior

Verified local Rust replay:
- day `-2`: `81'474.0`
  - `ASH_COATED_OSMIUM`: `1'830.0`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `1'468`
- day `-1`: `83'076.0`
  - `ASH_COATED_OSMIUM`: `3'708.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `1'431`
- day `0`: `82'866.0`
  - `ASH_COATED_OSMIUM`: `3'469.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `1'380`

Read:
- the 4-state concept is much too active in this first form
- Pepper stayed intact
- the entire collapse came from Osmium
- trade count exploded while Osmium PnL collapsed, so the engine is switching / harvesting far too often and paying for that churn

Practical takeaway:
- Osmium does not want a broad execution-state rewrite in this form
- the useful lesson is still execution-first, but the adaptation needs to be much lighter and more selective

### `TradervR1_29.py`

Idea:
- try a much simpler mechanism around the failed `TradervR1_28.py` concept
- keep the strong Round 1 trunk intact
- keep `INTARIAN_PEPPER_ROOT` unchanged
- add only two light Osmium overlays:
  - small OU-style stretch lean around the `10000` anchor
  - small toxic retreat on clearly adverse passive states

Verified local Rust replay:
- day `-2`: `79'600.0`
  - `ASH_COATED_OSMIUM`: `-44.0`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `1'665`
- day `-1`: `82'313.0`
  - `ASH_COATED_OSMIUM`: `2'945.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `1'657`
- day `0`: `82'021.0`
  - `ASH_COATED_OSMIUM`: `2'624.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `1'563`

Read:
- this simplified mechanism still breaks Osmium badly
- Pepper remains intact
- the whole loss is again Osmium, with trade count exploding even more than the trunk

Practical takeaway:
- the problem is not only that `TradervR1_28.py` had too many states
- even the lighter stretch-plus-toxic overlay is still pushing Osmium into too much churn
- so the next Osmium path should probably move away from state overlays and focus on narrower execution-quality levers instead

### `TradervR1_30.py`

Idea:
- do the opposite of the active overlay family
- keep the strong Round 1 trunk and Pepper unchanged
- make `ASH_COATED_OSMIUM` more passive-first:
  - less twitchy fair
  - higher take thresholds
  - smaller passive size in narrow or toxic books
  - larger passive size only in wide, safe books
  - stronger retreat from toxic passive states

Verified local Rust replay:
- day `-2`: `94'411.0`
  - `ASH_COATED_OSMIUM`: `14'767.0`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `471`
- day `-1`: `94'802.0`
  - `ASH_COATED_OSMIUM`: `15'434.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `484`
- day `0`: `93'816.0`
  - `ASH_COATED_OSMIUM`: `14'419.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `467`

Read:
- this is still below the trunk, but it is much healthier than `TradervR1_28.py` or `TradervR1_29.py`
- Pepper stayed unchanged
- Osmium trade count dropped sharply and the catastrophic churn disappeared

Practical takeaway:
- the “180 turn” was directionally useful
- Osmium clearly prefers this lower-churn direction over the active state-overlay family
- but the current passive-first calibration is too conservative and gives up too much good Osmium edge

### `TradervR1_31*` middle-ground Osmium refinements

Idea:
- use the information from `TradervR1_30.py`, but move back toward the strong trunk
- keep Pepper unchanged
- test a few middle-ground Osmium variants:
  - less fair twitchiness than the trunk
  - slightly higher take thresholds
  - slightly smaller passive size in narrow / toxic books
  - still keep enough normal spread capture alive

Results:
- `TradervR1_31.py`: `95'385.5 / 95'945.0 / 94'791.0`
  - sum: `286'121.5`
- `TradervR1_31_1.py`: `94'881.0 / 95'247.0 / 94'434.0`
  - sum: `284'562.0`
- `TradervR1_31_2.py`: `95'635.0 / 96'231.0 / 95'106.0`
  - sum: `286'972.0`

Reference:
- `TradervR1_25_2.py`: `95'984.0 / 96'517.0 / 95'444.0`
  - sum: `287'945.0`

Best of the new set:
- `TradervR1_31_2.py`
  - day `-2`: `ASH_COATED_OSMIUM 15'991.0`, `INTARIAN_PEPPER_ROOT 79'644.0`, trades `554`
  - day `-1`: `ASH_COATED_OSMIUM 16'863.0`, `INTARIAN_PEPPER_ROOT 79'368.0`, trades `556`
  - day `0`: `ASH_COATED_OSMIUM 15'709.0`, `INTARIAN_PEPPER_ROOT 79'397.0`, trades `542`

Read:
- the middle-ground direction is much healthier than `TradervR1_30.py`
- `TradervR1_31_2.py` recovers most of the passive-first giveback
- but it still does not beat the main trunk

Practical takeaway:
- the useful signal from `TradervR1_30.py` was real
- Osmium does want some reduction in churn
- but only lightly; once the reduction gets too strong, it gives up too much edge

### `TradervR1_32.py` and `TradervR1_32_1.py`

Idea:
- test the hypothesis that `ASH_COATED_OSMIUM` behaves more like tutorial-round `TOMATOES`
- rebuild Osmium as a small drift-style trader:
  - short / long mid EMAs
  - residual EMA
  - regime-like logic (`trend_up`, `trend_down`, `mean_revert`, `toxic`)
  - target-position style execution instead of a pure anchored market maker
- keep `INTARIAN_PEPPER_ROOT` unchanged

Verified local Rust replay:
- `TradervR1_32.py`
  - day `-2`: `87'111.5`
  - day `-1`: `87'558.0`
  - day `0`: `86'510.0`
- `TradervR1_32_1.py`
  - day `-2`: `87'018.0`
  - day `-1`: `87'644.0`
  - day `0`: `86'462.0`

Read:
- both are far below the trunk
- Pepper stays intact
- the entire loss is Osmium again
- the lighter variant is a touch better, but still nowhere close

Practical takeaway:
- Osmium does not want to be treated as another TOMATOES-style drift asset
- even the lighter adaptation under-monetizes Osmium badly
- this strongly reinforces the anchored-MM view of the product

### `TradervR1_33.py`

Idea:
- keep `INTARIAN_PEPPER_ROOT` unchanged from the strong production trunk
- rebuild `ASH_COATED_OSMIUM` into a cleaner reusable local-fair market-maker base:
  - fair from anchor + stable-book / wall-mid structure + micro + depth-aware imbalance
  - nonlinear reservation / inventory pressure
  - toxicity-aware passive quoting
  - stricter stale-book taking
  - simple fill-quality penalty gating
  - gentle capacity-clearing when inventory is stretched and edge is near flat

Verified local Rust replay:
- day `-2`: `89'818.5`
  - `ASH_COATED_OSMIUM`: `10'174.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `394`
- day `-1`: `90'850.0`
  - `ASH_COATED_OSMIUM`: `11'482.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `421`
- day `0`: `90'353.0`
  - `ASH_COATED_OSMIUM`: `10'956.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `435`

Read:
- the architecture is clean and reusable, and it matches the intended Osmium design much better
- Pepper stayed stable, so the result is a pure Osmium read
- but this base is still materially below the current trunk on all three days
- the new engine is too conservative and gives up too much normal spread capture

Practical takeaway:
- this is a good research base for later Osmium tuning
- but it is not a production upgrade over `TradervR1_25_2.py`
- the main missing piece is not architecture anymore, it is restoring more of the trunk's day-to-day capture without reintroducing bad churn

### `TradervR1_34.py` and `TradervR1_34_1.py`

Idea:
- continue directly from the `TradervR1_33.py` lesson
- test two follow-ups:
  - `TradervR1_34.py`: keep the full local-fair / fill-quality / nonlinear-inventory Osmium structure, but loosen it so it captures more normal spread
  - `TradervR1_34_1.py`: lighter hybrid that keeps the stronger trunk-style Osmium execution and only upgrades the fair / reservation layer with stable-book local fair logic
- keep `INTARIAN_PEPPER_ROOT` unchanged

Verified local Rust replay:
- `TradervR1_34.py`
  - day `-2`: `92'499.0`
    - `ASH_COATED_OSMIUM`: `12'855.0`
    - `INTARIAN_PEPPER_ROOT`: `79'644.0`
    - trades: `562`
  - day `-1`: `93'533.0`
    - `ASH_COATED_OSMIUM`: `14'165.0`
    - `INTARIAN_PEPPER_ROOT`: `79'368.0`
    - trades: `572`
  - day `0`: `93'451.0`
    - `ASH_COATED_OSMIUM`: `14'054.0`
    - `INTARIAN_PEPPER_ROOT`: `79'397.0`
    - trades: `581`
- `TradervR1_34_1.py`
  - day `-2`: `96'129.5`
    - `ASH_COATED_OSMIUM`: `16'485.5`
    - `INTARIAN_PEPPER_ROOT`: `79'644.0`
    - trades: `730`
  - day `-1`: `96'217.0`
    - `ASH_COATED_OSMIUM`: `16'849.0`
    - `INTARIAN_PEPPER_ROOT`: `79'368.0`
    - trades: `708`
  - day `0`: `95'696.0`
    - `ASH_COATED_OSMIUM`: `16'299.0`
    - `INTARIAN_PEPPER_ROOT`: `79'397.0`
    - trades: `690`

Reference:
- `TradervR1_25_2.py`: `95'984.0 / 96'517.0 / 95'444.0`
  - sum: `287'945.0`
- `TradervR1_34_1.py`: `96'129.5 / 96'217.0 / 95'696.0`
  - sum: `288'042.5`

Read:
- `TradervR1_34.py` confirms the main `v33` lesson: the fully structured Osmium base improves over `v33`, but still leaves too much normal capture on the table
- `TradervR1_34_1.py` is the important result:
  - the local-fair upgrade *does* help
  - but it helps most when the trunk-style execution still stays in charge
  - this is the first clean local-fair Osmium follow-up that edges out the current trunk on total three-day sum

Practical takeaway:
- the better path is not “more Osmium architecture”
- it is “strong trunk execution + better local fair + only light nonlinear reservation shaping”
- `TradervR1_34_1.py` becomes the new best candidate from this branch

### `TradervR1_35.py`

Idea:
- continue from `TradervR1_34_1.py`
- keep the strong trunk-style Osmium execution
- do **not** trust the local fair equally in every book state
- blend between:
  - the new stable-book / wall-mid local fair
  - the old trunk fair
- use a simple confidence score based on:
  - top-book depth
  - spread width
  - how far stable-book mid drifts away from the 10000 anchor
- when local structure looks healthy, lean harder on local fair
- when local structure looks noisy, fall back toward the older anchored/trunk fair

Additional research:
- ran a focused TraderFactory search on `TradervR1_34_1.py`
  - config: `TraderFactory/configs/round1/tradervr1_34_1_cmaes.json`
  - result: completely flat; the optimizer returned the default bot unchanged
  - useful conclusion: the old `v34.1` parameters were already locally well-tuned, so the next gain had to come from structure, not another constant sweep

Verified local Rust replay:
- day `-2`: `96'244.5`
  - `ASH_COATED_OSMIUM`: `16'600.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `631`
- day `-1`: `96'584.0`
  - `ASH_COATED_OSMIUM`: `17'216.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `615`
- day `0`: `95'709.0`
  - `ASH_COATED_OSMIUM`: `16'312.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `609`

Reference:
- `TradervR1_34_1.py`: `96'129.5 / 96'217.0 / 95'696.0`
  - sum: `288'042.5`
- `TradervR1_35.py`: `96'244.5 / 96'584.0 / 95'709.0`
  - sum: `288'537.5`

Read:
- this is a clean improvement over `TradervR1_34_1.py`
- the gain is entirely Osmium; Pepper stayed fixed
- day `-1` shows the biggest benefit, but the bot is up on all three days
- trade count came down versus `v34.1`, which is a healthy sign: the improvement did not come from more churn, but from better fair selection

Practical takeaway:
- the local-fair idea is real
- the key is not to use it everywhere, but to trust it selectively
- `TradervR1_35.py` is the new best candidate from this branch

### `TradervR1_36.py`

Idea:
- continue from `TradervR1_35.py`
- add a passive-fill adverse-selection memory layer for `ASH_COATED_OSMIUM`
- track recent side-specific low-quality fills in traderData:
  - buy fills followed by downward markout
  - sell fills followed by upward markout
- use that memory to:
  - widen that side
  - reduce size on that side
  - temporarily suppress that side when recent bad-fill score gets high
- keep `INTARIAN_PEPPER_ROOT` unchanged

Verified local Rust replay:
- day `-2`: `96'244.5`
  - `ASH_COATED_OSMIUM`: `16'600.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `631`
- day `-1`: `96'584.0`
  - `ASH_COATED_OSMIUM`: `17'216.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `615`
- day `0`: `95'709.0`
  - `ASH_COATED_OSMIUM`: `16'312.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `609`

Reference:
- `TradervR1_35.py`: `96'244.5 / 96'584.0 / 95'709.0`
- `TradervR1_36.py`: `96'244.5 / 96'584.0 / 95'709.0`

Read:
- completely inert on local replay
- same product split
- same trade count
- same totals on all three days

Practical takeaway:
- the passive-fill quality idea is structurally reasonable
- but in this first local implementation it did not activate in a way that changed realized behavior
- so the current local bottleneck is probably not simple recent-fill braking on top of `v35`

### `TradervR1_37.py` and `TradervR1_38.py`

Idea:
- push the next structural round directly on the two remaining hypotheses:
  - Pepper should improve mainly through better **entry quality**, not more state complexity
  - Osmium should improve through **markout-aware passive quoting** and **adaptive front size**, not another fair rewrite
- `TradervR1_37.py`
  - keep `TradervR1_35.py` as trunk
  - replace broad cheap-accum activation with a drift-adjusted shock gate
  - add a lighter realized-fill markout memory to Osmium
  - adapt front/back passive size by local-fair confidence, imbalance, toxicity, and inventory stretch
- `TradervR1_38.py`
  - same structure as `v37`
  - but make the shock gate and fill-quality filter materially stronger so the logic actually bites

Verified local Rust replay:
- `TradervR1_37.py`
  - day `-2`: `96'249.5`
    - `ASH_COATED_OSMIUM`: `16'605.5`
    - `INTARIAN_PEPPER_ROOT`: `79'644.0`
    - trades: `631`
  - day `-1`: `96'584.0`
    - `ASH_COATED_OSMIUM`: `17'216.0`
    - `INTARIAN_PEPPER_ROOT`: `79'368.0`
    - trades: `615`
  - day `0`: `95'709.0`
    - `ASH_COATED_OSMIUM`: `16'312.0`
    - `INTARIAN_PEPPER_ROOT`: `79'397.0`
    - trades: `609`
- `TradervR1_38.py`
  - day `-2`: `96'249.5`
    - `ASH_COATED_OSMIUM`: `16'605.5`
    - `INTARIAN_PEPPER_ROOT`: `79'644.0`
    - trades: `631`
  - day `-1`: `96'584.0`
    - `ASH_COATED_OSMIUM`: `17'216.0`
    - `INTARIAN_PEPPER_ROOT`: `79'368.0`
    - trades: `615`
  - day `0`: `95'700.0`
    - `ASH_COATED_OSMIUM`: `16'312.0`
    - `INTARIAN_PEPPER_ROOT`: `79'388.0`
    - trades: `609`

Reference:
- `TradervR1_35.py`: `96'244.5 / 96'584.0 / 95'709.0`
  - sum: `288'537.5`
- `TradervR1_37.py`: `96'249.5 / 96'584.0 / 95'709.0`
  - sum: `288'542.5`
- `TradervR1_38.py`: `96'249.5 / 96'584.0 / 95'700.0`
  - sum: `288'533.5`

Read:
- `v37` moved the bot only marginally
  - small `+5` on day `-2`
  - no change on day `-1`
  - no change on day `0`
- `v38` made the same structure stronger, but that only gave back `-9` on day `0`
- in practice:
  - the new Pepper shock gate barely changes realized behavior on top of this trunk
  - the new Osmium fill-quality / adaptive-size layer is structurally reasonable, but still not a meaningful driver locally

Practical takeaway:
- these improvements are not “wrong,” but on the current `v35` trunk they are mostly inert
- the strongest current bot from this line is still `TradervR1_37.py` by a hair, but the gain is too small to treat as a robust new step
- the real value of this round is the negative information:
  - better Pepper entry timing is not unlocking a big gain here
  - simple realized-fill braking on Osmium is also not the missing edge

## Official Read: `v37`

Saved official-style logs:
- `TradervR1_34_1.log`
- `TradervR1_35.log`
- `TradervR1_37.log`

Official totals:
- `TradervR1_34_1`: `10'086.96875`
  - `ASH_COATED_OSMIUM`: `2'500.96875`
  - `INTARIAN_PEPPER_ROOT`: `7'586.0`
- `TradervR1_35`: `10'049.84375`
  - `ASH_COATED_OSMIUM`: `2'463.84375`
  - `INTARIAN_PEPPER_ROOT`: `7'586.0`
- `TradervR1_37`: `10'011.84375`
  - `ASH_COATED_OSMIUM`: `2'463.84375`
  - `INTARIAN_PEPPER_ROOT`: `7'548.0`

Trade-quality read:
- `TradervR1_35` and `TradervR1_37` had identical `ASH_COATED_OSMIUM` outcomes
- the whole `v37` giveback came from `INTARIAN_PEPPER_ROOT`
- Pepper trade profile:
  - `v35`: buy qty `80`, avg buy `12005.075`
  - `v37`: buy qty `80`, avg buy `12005.55`

Read:
- `v37` did not unlock a new edge
- it effectively kept the `v35` Osmium behavior and only paid a worse average Pepper entry price
- practical conclusion: `v37` should be dropped as a candidate and `v34.1` remains the stronger official-transfer branch

## Broad CMA-ES Sweep Around `TradervR1_34_1`

Goal:
- test whether `TradervR1_34_1.py` is sitting in a real local optimum
- use broader search bands than the earlier focused run
- check both one-product and cross-product escape routes

Searches run:
- `tradervr1_34_1_cmaes_broad_osmium.json`
- `tradervr1_34_1_cmaes_broad_pepper.json`
- `tradervr1_34_1_cmaes_mixed_escape.json`

Configs:
- all used the Round 1 Rust engine on days `-2 / -1 / 0`
- broad single-product bands:
  - `max_iter = 4`
  - `population = 8`
  - `parents = 3`
  - `sigma0 = 0.09`
- mixed escape band:
  - `max_iter = 5`
  - `population = 10`
  - `parents = 4`
  - `sigma0 = 0.10`

Results:
- all three searches returned the exact source bot as the best solution
- best scores in every case stayed:
  - day `-2`: `96'129.5`
  - day `-1`: `96'217.0`
  - day `0`: `95'696.0`
  - average: `96'014.16666666667`

Artifacts:
- `Analysis/output/round1_tradervr1_34_1_cmaes_broad_osmium/`
- `Analysis/output/round1_tradervr1_34_1_cmaes_broad_pepper/`
- `Analysis/output/round1_tradervr1_34_1_cmaes_mixed_escape/`

Read:
- the broad Osmium band did not find a better fair/execution basin
- the broad Pepper band did not find a better carry-entry basin
- even the mixed escape search, which allowed coupled Pepper+Osmium changes, still snapped back to the source defaults

Practical takeaway:
- this is strong evidence that `TradervR1_34_1.py` is sitting in a genuinely robust local optimum under the current architecture
- if we want a real next gain, it likely will not come from broader constant sweeps alone
- the next improvement probably has to be structural, but only if it preserves the turnover/capacity profile that made `v34.1` transfer well

## `TradervR1_39.py` and `TradervR1_39_1.py`

Idea:
- test the “paper-inspired structural change” in the most practical way possible:
  - keep `TradervR1_34_1.py` as the trunk
  - keep `INTARIAN_PEPPER_ROOT` almost unchanged
  - add only a small innovation gate to Pepper aggressive buys
  - add a lightweight calm / normal / toxic state filter to `ASH_COATED_OSMIUM`
  - add side-specific fill-quality memory to Osmium so quoting can react to recent bad fills

`TradervR1_39.py`:
- first full structural version
- Osmium state filter affects:
  - take thresholds
  - quote widths
  - passive-size scaling
  - one-sided shutdown
  - gentle inventory clearing in neutral books

`TradervR1_39_1.py`:
- lighter salvage pass on top of `v39`
- keeps the state filter, but:
  - removes the state-driven edge tightening
  - reduces fill-penalty impact
  - makes size scaling much gentler
  - removes the explicit inventory-clearing add-on

Verified local Rust replay:
- `TradervR1_39.py`
  - day `-2`: `94'857.0`
    - `ASH_COATED_OSMIUM`: `15'213.0`
    - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - day `-1`: `95'562.0`
    - `ASH_COATED_OSMIUM`: `16'199.0`
    - `INTARIAN_PEPPER_ROOT`: `79'363.0`
  - day `0`: `94'896.0`
    - `ASH_COATED_OSMIUM`: `15'499.0`
    - `INTARIAN_PEPPER_ROOT`: `79'397.0`
- `TradervR1_39_1.py`
  - day `-2`: `95'002.0`
    - `ASH_COATED_OSMIUM`: `15'358.0`
    - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - day `-1`: `95'608.0`
    - `ASH_COATED_OSMIUM`: `16'245.0`
    - `INTARIAN_PEPPER_ROOT`: `79'363.0`
  - day `0`: `94'976.0`
    - `ASH_COATED_OSMIUM`: `15'579.0`
    - `INTARIAN_PEPPER_ROOT`: `79'397.0`

Reference:
- `TradervR1_34_1.py`: `96'129.5 / 96'217.0 / 95'696.0`

Read:
- both branches preserve the broad Pepper behavior
- the loss is overwhelmingly Osmium
- `v39.1` is clearly better than `v39`, which means the first version simply over-defended and gave up too much normal spread capture
- but even the lighter stateful branch still stays well below the `v34.1` trunk

Practical takeaway:
- the HMM-style calm / normal / toxic idea is intellectually coherent
- but as a live execution overlay on current Osmium it is still too costly in turnover
- if we revisit this direction, it should be even lighter:
  - state only as a veto / one-sided permission system
  - not as a broad quote-width and capacity controller

## `TradervR1_39_2.py`, `TradervR1_39_3.py`, and `TradervR1_39_4.py`

Idea:
- test truly selective hybrids instead of the heavier `v39` overlay
- all three keep `TradervR1_34_1.py` as the behavioral trunk and only import tiny Osmium-side donor logic

Variants:
- `TradervR1_39_2.py`
  - HMM-style state filter used only as a passive quoting veto / one-sided permission layer
  - side-specific markout veto
  - no state-driven quote-width or size shaping
- `TradervR1_39_3.py`
  - same as `v39.2`
  - plus very mild toxic-state take restraint
- `TradervR1_39_4.py`
  - no HMM state filter at all
  - fill-quality / markout veto only
  - this is the cleanest hybrid donor test

Verified local Rust replay:
- `TradervR1_39_2.py`
  - day `-2`: `95'289.5`
    - `ASH_COATED_OSMIUM`: `15'645.5`
    - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - day `-1`: `95'952.0`
    - `ASH_COATED_OSMIUM`: `16'589.0`
    - `INTARIAN_PEPPER_ROOT`: `79'363.0`
  - day `0`: `95'363.0`
    - `ASH_COATED_OSMIUM`: `15'966.0`
    - `INTARIAN_PEPPER_ROOT`: `79'397.0`
- `TradervR1_39_3.py`
  - identical to `TradervR1_39_2.py` on all three days
- `TradervR1_39_4.py`
  - day `-2`: `95'976.5`
    - `ASH_COATED_OSMIUM`: `16'332.5`
    - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - day `-1`: `96'166.0`
    - `ASH_COATED_OSMIUM`: `16'803.0`
    - `INTARIAN_PEPPER_ROOT`: `79'363.0`
  - day `0`: `95'696.0`
    - `ASH_COATED_OSMIUM`: `16'299.0`
    - `INTARIAN_PEPPER_ROOT`: `79'397.0`

Reference:
- `TradervR1_34_1.py`: `96'129.5 / 96'217.0 / 95'696.0`

Read:
- `v39.2` and `v39.3` still give up too much Osmium edge
- the extra toxic take restraint in `v39.3` is completely inert
- `v39.4` is by far the best hybrid:
  - only `-153.0` on day `-2`
  - only `-51.0` on day `-1`
  - exactly equal on day `0`
- that means the useful donor from the `v39` family is not the state filter
- the only piece that survives is the very light fill-quality / markout veto

Practical takeaway:
- state-based regime filtering still appears too expensive for Osmium
- markout-aware veto is the only hybrid element that comes close to surviving
- if we continue this path, `TradervR1_39_4.py` is the right donor branch, not the HMM-style state versions

## `TradervR1_35_HMMOsmium.py`

Idea:
- keep the stronger `v35`-style local-fair Osmium base
- add a small HMM-style calm / normal / toxic execution filter
- add side-specific markout-aware quote penalties
- keep Pepper mostly unchanged except for a small innovation gate

Status:
- the file runs correctly as-is; no runtime fix was needed

Verified local Rust replay:
- day `-2`: `94'834.5`
  - `ASH_COATED_OSMIUM`: `15'190.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `617`
- day `-1`: `94'878.0`
  - `ASH_COATED_OSMIUM`: `15'510.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `596`
- day `0`: `94'718.0`
  - `ASH_COATED_OSMIUM`: `15'321.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `584`

Reference:
- `TradervR1_34_1.py`: `96'129.5 / 96'217.0 / 95'696.0`

Read:
- this HMM Osmium branch is clearly below the stronger Round 1 trunk
- the loss is again mainly Osmium
- the trade count is notably lower, which is consistent with the state filter over-defending and giving up too much normal spread capture

## Broad CMA-ES On `TradervR1_35_HMMOsmium.py`

Goal:
- see whether this branch is mainly under-tuned or structurally too costly
- search broadly over the HMM-state parameters, Osmium execution parameters, and the small Pepper innovation gate

Config:
- `TraderFactory/configs/round1/tradervr1_35_hmmosmium_cmaes_broad.json`
- search:
  - `max_iter = 5`
  - `population = 10`
  - `parents = 4`
  - `sigma0 = 0.10`

Result:
- the optimizer returned the exact source defaults as best
- best scores stayed:
  - day `-2`: `94'834.5`
  - day `-1`: `94'878.0`
  - day `0`: `94'718.0`

Artifacts:
- `Analysis/output/round1_tradervr1_35_hmmosmium_cmaes_broad/`

Practical takeaway:
- this branch does not appear to hide a better parameter basin
- broad CMA-ES was unable to improve it at all
- the limitation looks architectural, not tuning-related
- if this family is to improve, it likely needs to collapse toward the much lighter `v39.4`-style markout-only donor logic rather than pushing the HMM state filter harder

## `TradervR1_40.py`

Idea:
- keep `TradervR1_34_1.py` as the transfer-friendly trunk
- test the advisor-style “small deliberate volume move” idea in the closest honest form available in the continuous Round 1 interface
- add only two narrow Osmium overlays:
  - a **volume-aware nudge sweep** that removes tiny stale slices of the book only when doing so cheaply reveals a meaningfully better next level
  - a **gentle capacity-recycling cross** when inventory is stretched and local edge is near zero
- keep `INTARIAN_PEPPER_ROOT` unchanged

Important implementation note:
- the Round 1 bot interface exposes only continuous order books and trades, not a separate auction-clearing state
- so this version is a proxy for the auction-volume idea, not a true auction-clearing optimizer

Verified local Rust replay:
- day `-2`: `95'676.5`
  - `ASH_COATED_OSMIUM`: `16'032.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `866`
- day `-1`: `96'094.0`
  - `ASH_COATED_OSMIUM`: `16'726.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `856`
- day `0`: `95'635.0`
  - `ASH_COATED_OSMIUM`: `16'238.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `837`

Reference:
- `TradervR1_34_1.py`: `96'129.5 / 96'217.0 / 95'696.0`
  - trades: `730 / 708 / 690`

Read:
- Pepper stayed perfectly stable, so the whole read is Osmium
- the new layer increased Osmium turnover a lot:
  - `v40`: `866 / 856 / 837` trades
  - `v34.1`: `730 / 708 / 690` trades
- but that extra churn did **not** monetize better:
  - day `-2`: `-453.0`
  - day `-1`: `-123.0`
  - day `0`: `-61.0`
- this suggests the “volume nudge” idea is directionally interesting, but in the continuous-book setting it behaves more like over-aggressive stale-volume harvesting than a true auction edge

Practical takeaway:
- the advisor insight is still useful conceptually
- but without a real auction-clearing interface, this proxy does not transfer well
- for Round 1 continuous trading, small volume nudges added churn faster than they added quality

## `TradervR1_41.py` and `TradervR1_41_1.py`

Idea:
- test a completely different Osmium direction:
  - very fast-paced trading
  - do not hold inventory long
  - recycle back toward flat quickly after fills
- keep `INTARIAN_PEPPER_ROOT` unchanged
- use `TradervR1_34_1.py` as the trunk in both cases

What changed:
- `TradervR1_41.py`
  - hard fast-recycle rewrite for Osmium
  - explicit inventory-age memory
  - strong zero-target reservation pull
  - cheaper opposite-side takes
  - reduced same-side quoting once inventory is carried
  - effectively tries to flatten quickly and avoid holding risk
- `TradervR1_41_1.py`
  - much lighter version of the same idea
  - no age-based shutdown
  - mild recycle reservation skew
  - mild opposite-side take bonus
  - slightly smaller same-side passive size
  - tiny stretch-only clearing clip

Verified local Rust replay:
- `TradervR1_41.py`
  - day `-2`: `84'605.0`
    - `ASH_COATED_OSMIUM`: `4'961.0`
    - `INTARIAN_PEPPER_ROOT`: `79'644.0`
    - trades: `808`
  - day `-1`: `85'177.0`
    - `ASH_COATED_OSMIUM`: `5'809.0`
    - `INTARIAN_PEPPER_ROOT`: `79'368.0`
    - trades: `790`
  - day `0`: `83'274.0`
    - `ASH_COATED_OSMIUM`: `3'877.0`
    - `INTARIAN_PEPPER_ROOT`: `79'397.0`
    - trades: `805`
- `TradervR1_41_1.py`
  - day `-2`: `95'621.0`
    - `ASH_COATED_OSMIUM`: `15'977.0`
    - `INTARIAN_PEPPER_ROOT`: `79'644.0`
    - trades: `751`
  - day `-1`: `95'726.0`
    - `ASH_COATED_OSMIUM`: `16'358.0`
    - `INTARIAN_PEPPER_ROOT`: `79'368.0`
    - trades: `739`
  - day `0`: `94'930.0`
    - `ASH_COATED_OSMIUM`: `15'533.0`
    - `INTARIAN_PEPPER_ROOT`: `79'397.0`
    - trades: `702`

Reference:
- `TradervR1_34_1.py`: `96'129.5 / 96'217.0 / 95'696.0`

Read:
- the extreme fast-recycle version in `TradervR1_41.py` is clearly the wrong direction
- the lighter version in `TradervR1_41_1.py` is much healthier, which means the idea itself is not nonsense
- but even the lighter version still loses to the trunk on all three days:
  - day `-2`: `-508.5`
  - day `-1`: `-491.0`
  - day `0`: `-766.0`
- Pepper stayed identical in both cases, so the whole read is Osmium

Practical takeaway:
- Osmium does not seem to want a “flip it back out quickly” identity
- a mild recycle bias is survivable
- but the trunk still monetizes better by letting good passive inventory breathe a bit longer

## Stage 1 Controlled Sweep: `TradervR1_42_*`

Goal:
- run the first isolated sweep from the current best transferable trunk
- change one meaningful mechanism per version so we can see which axis is actually alive

Baseline:
- `TradervR1_42_Base.py`
  - exact snapshot of `TradervR1_34_1.py`

Stage 1 variants:
- `TradervR1_42_P1_1.py`
  - Pepper `ShockGateLight`
  - aggressive buys only get a small innovation / drift-shock gate
- `TradervR1_42_P3_1.py`
  - Pepper `RareOverlaySell`
  - overlay sells only in extreme rich states
- `TradervR1_42_O1_1.py`
  - Osmium `DepthAwareImbalance`
  - fair simplified to anchor + depth-scaled imbalance + microprice
- `TradervR1_42_O2_1.py`
  - Osmium `PassiveFillPenaltyLight`
  - light side-specific markout veto on passive quoting
- `TradervR1_42_O3_2.py`
  - Osmium `ToxicOneSidedMedium`
  - toxic side disabled instead of merely widened
- `TradervR1_42_O4_1.py`
  - Osmium `LinearClearer`
  - explicit near-zero-edge inventory clearing when stretched
- `TradervR1_42_O5_1.py`
  - Osmium `Level1Sniper`
  - best-level-only active taking, no broader aggression

Three-day totals:
- `TradervR1_42_Base.py`: `288'042.5`
- `TradervR1_42_P3_1.py`: `288'042.5`
- `TradervR1_42_O4_1.py`: `288'042.5`
- `TradervR1_42_P1_1.py`: `288'037.5`
- `TradervR1_42_O2_1.py`: `288'015.5`
- `TradervR1_42_O1_1.py`: `286'724.5`
- `TradervR1_42_O5_1.py`: `285'965.0`
- `TradervR1_42_O3_2.py`: `284'205.5`

Read:
- `P3_1` and `O4_1` were completely inert
  - rare Pepper overlay selling did not change realized behavior at all
  - explicit Osmium linear clearing also did not change realized behavior at all
- `P1_1` was almost inert but slightly worse
  - only `-5.0` total over the full three-day sweep
  - this means Pepper shock-gating is still a live research lever, but the light version did not improve the trunk
- `O2_1` was the best surviving Osmium-side change
  - only `-27.0` over the full three-day sweep
  - this is the closest thing to a usable donor from Stage 1
- `O1_1`, `O5_1`, and especially `O3_2` were clearly harmful
  - simplifying Osmium fair to anchor + imbalance + micro lost too much
  - a stricter best-level sniper under-monetized Osmium
  - toxic one-sided shutdown gave up the most normal spread capture

Behavior notes:
- Pepper final position stayed `+80` in every Stage 1 run
- the winners/losers were therefore almost entirely about execution quality, not changing the broad inventory thesis
- Osmium trade count fell meaningfully in the weaker defensive variants, but that lower churn did not translate into better PnL

Artifacts:
- full sweep summary CSV:
  - `Analysis/output/r1_42_stage1/stage1_summary.csv`

Practical takeaway:
- the current trunk really is hard to beat with single isolated changes
- the only Stage 1 ideas that survived contact were:
  - Pepper entry shock gating (`P1_1`)
  - Osmium passive fill-quality veto (`O2_1`)
- if we continue to Stage 2, the highest-value path is:
  - deepen `P1` a bit on Pepper
  - deepen `O2` on Osmium
  - do **not** spend more cycles on `O1`, `O3`, or `O5` in their current form

## `TradervR1_43.py`

Idea:
- build one evidence-based follow-up directly from the base
- keep the exact `TradervR1_34_1.py` structure
- import only the two Stage 1 survivors, but even more softly:
  - Pepper:
    - only suppress clearly positive-shock aggressive buys
    - do not add extra complexity to fair or target logic
  - Osmium:
    - side-specific fill-quality memory
    - soft quote widening / size-down on a side after bad recent passive fills
    - hard veto only in clearly bad markout + adverse-imbalance cases

Verified local Rust replay:
- day `-2`: `96'129.5`
  - `ASH_COATED_OSMIUM`: `16'485.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `730`
- day `-1`: `96'217.0`
  - `ASH_COATED_OSMIUM`: `16'849.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `708`
- day `0`: `95'696.0`
  - `ASH_COATED_OSMIUM`: `16'299.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `690`

Reference:
- `TradervR1_34_1.py`: `96'129.5 / 96'217.0 / 95'696.0`

Read:
- `v43` is completely identical to the base on all three local days
- that means the combined “best surviving donor” branch was still too light to change realized behavior
- this is still useful:
  - it suggests the next improvement is unlikely to come from stacking tiny safe overlays
  - if a better bot exists from here, it probably needs one clearly stronger structural change, not two nearly inert ones

## Round 1 Active Set Cleanup

Top-level Round 1 folder now keeps only the active files that still look useful:
- `TradervR1_34.py`
- `TradervR1_34_1.py`
- `TradervR1_35.py`
- `TradervR1_39_4.py`
- `TradervR1_42_P1_1.py`
- `TradervR1_42_O2_1.py`
- `TradervR1_43.py`

Moved to `Bots/Round1/archive/`:
- all the clearly harmful, inert, superseded, or duplicate top-level research variants from the later Round 1 branch set
- examples include:
  - `TradervR1_27*` to `TradervR1_33*`
  - `TradervR1_35_HMMOsmium.py`
  - `TradervR1_36.py`
  - `TradervR1_37.py`
  - `TradervR1_38.py`
  - `TradervR1_39.py` to `TradervR1_39_3.py`
  - `TradervR1_40.py`
  - `TradervR1_41.py`
  - `TradervR1_41_1.py`
  - `TradervR1_42_Base.py`
  - `TradervR1_42_O1_1.py`
  - `TradervR1_42_O3_2.py`
  - `TradervR1_42_O4_1.py`
  - `TradervR1_42_O5_1.py`
  - `TradervR1_42_P3_1.py`

Practical takeaway:
- the Round 1 working set is now much cleaner
- the visible top-level files are the ones that still carry either:
  - best-performance value
  - or real donor value for the next branch

### `TradervR1_44.py`

Idea:
- keep the `TradervR1_34_1.py` fair-value trunk unchanged for both products
- keep `INTARIAN_PEPPER_ROOT` exactly on the trunk
- change only `ASH_COATED_OSMIUM`
- add an inventory-quality layer that separates Osmium inventory into:
  - fresh inventory worth defending
  - stale inventory worth recycling
- use side-specific entry reference, age, and stale score to:
  - back off new adds when current inventory quality is poor
  - tighten exits on stale inventory
  - allow small recycler behavior before inventory gets extreme

Verified local Rust replay:
- day `-2`: `95'021.5`
  - `ASH_COATED_OSMIUM`: `15'377.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `696`
- day `-1`: `94'749.0`
  - `ASH_COATED_OSMIUM`: `15'381.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `670`
- day `0`: `94'672.0`
  - `ASH_COATED_OSMIUM`: `15'275.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `641`

Comparison vs `TradervR1_34_1.py`:
- day `-2`: `-1'108.0`
- day `-1`: `-1'468.0`
- day `0`: `-1'024.0`

Read:
- Pepper stayed identical on all three days
- the full miss is Osmium
- the structural idea is coherent, but this first recycler implementation is too eager
- it improves inventory hygiene by lowering churn and reducing add-back into weak inventory, but it gives up too much normal spread capture

Takeaway:
- the missing architectural seam is still inventory quality, not fair-value discovery
- but a full “fresh vs stale” recycler should be much lighter
- if we revisit this path, the likely surviving donor is:
  - stale inventory only as a small quote-shaping bias
  - not as a broader recycle controller

### `TradervR1_45.py`

Idea:
- test a blunt but honest execution hypothesis:
  - make the whole bot roughly one tick more aggressive
- keep the same structure as `TradervR1_34_1.py`
- do not change the fair models
- only change execution thresholds:
  - `ASH_COATED_OSMIUM`
    - lower tiered take edges by about one tick
    - lower the passive quote floor by about one tick
  - `INTARIAN_PEPPER_ROOT`
    - lower base take edge by about one tick
    - lower base passive quote edge by about one tick

Verified local Rust replay:
- day `-2`: `96'134.0`
  - `ASH_COATED_OSMIUM`: `16'504.0`
  - `INTARIAN_PEPPER_ROOT`: `79'630.0`
  - trades: `830`
- day `-1`: `96'344.0`
  - `ASH_COATED_OSMIUM`: `17'010.0`
  - `INTARIAN_PEPPER_ROOT`: `79'334.0`
  - trades: `808`
- day `0`: `95'832.0`
  - `ASH_COATED_OSMIUM`: `16'408.0`
  - `INTARIAN_PEPPER_ROOT`: `79'424.0`
  - trades: `797`

Comparison vs `TradervR1_34_1.py`:
- day `-2`: `+4.5`
- day `-1`: `+127.0`
- day `0`: `+136.0`

Read:
- this is one of the first broad execution changes that actually improved the trunk locally
- the gain comes mostly from Osmium monetizing more
- Pepper is mixed:
  - slightly worse on days `-2` and `-1`
  - slightly better on day `0`
- the trade count increased meaningfully, so this version is clearly taking more risk to earn the gain

Takeaway:
- the trunk may have been a little too conservative in execution
- there is real edge in slightly more aggressive participation
- but this should still be treated carefully:
  - local gain is real
  - official transfer is not yet proven

### `TradervR1_46.py`

Idea:
- isolate the `v45` result more cleanly
- keep `INTARIAN_PEPPER_ROOT` exactly on the `TradervR1_34_1.py` trunk
- keep the more aggressive execution only for `ASH_COATED_OSMIUM`
- this tests whether the `v45` gain was really Osmium-led or just a broad risk-on effect

Implementation note:
- this version is a thin local derivative of `TradervR1_34_1.py`
- it is useful for research/backtesting inside this repo
- if promoted, it should be inlined into a standalone single-file trader before official upload

Verified local Rust replay:
- day `-2`: `96'148.0`
  - `ASH_COATED_OSMIUM`: `16'504.0`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `830`
- day `-1`: `96'378.0`
  - `ASH_COATED_OSMIUM`: `17'010.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `808`
- day `0`: `95'805.0`
  - `ASH_COATED_OSMIUM`: `16'408.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `798`

Comparison vs `TradervR1_34_1.py`:
- day `-2`: `+18.5`
- day `-1`: `+161.0`
- day `0`: `+109.0`

Comparison vs `TradervR1_45.py`:
- day `-2`: `+14.0`
- day `-1`: `+34.0`
- day `0`: `-27.0`

Read:
- this is cleaner than `v45`
- the gain really is mostly from more aggressive Osmium execution
- keeping Pepper on the stronger trunk logic improves days `-2` and `-1`
- `v45` is still slightly better on day `0`, but `v46` is the cleaner architecture

Takeaway:
- if we want to keep pushing this direction, Osmium aggression is the right lever
- Pepper did not need the extra aggression

Implementation note:
- `TradervR1_46.py` is now a standalone single-file trader and does not use dynamic loading
- that makes it safe to upload directly

### `TradervR1_47.py`

Idea:
- keep the same clean split as `TradervR1_46.py`
- push only the Osmium aggression much further
- leave Pepper fully unchanged
- this is the strongest standalone Osmium-aggression candidate from the up/down sweep

Verified local Rust replay:
- day `-2`: `96'657.5`
  - `ASH_COATED_OSMIUM`: `17'013.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `830`
- day `-1`: `96'739.0`
  - `ASH_COATED_OSMIUM`: `17'371.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `814`
- day `0`: `96'448.0`
  - `ASH_COATED_OSMIUM`: `17'051.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `789`

Comparison vs `TradervR1_34_1.py`:
- day `-2`: `+528.0`
- day `-1`: `+522.0`
- day `0`: `+752.0`

Three-day total:
- `TradervR1_34_1.py`: `288'042.5`
- `TradervR1_47.py`: `289'844.5`
- delta: `+1'802.0`

Read:
- the Osmium aggression sweep did not top out where we first expected
- stronger Osmium execution kept improving the branch
- the gain is entirely Osmium-led
- Pepper remained unchanged, which is exactly what we wanted from the split architecture

Implementation note:
- `TradervR1_47.py` is also standalone and upload-safe

## Osmium Aggression Flop Sweep

After `TradervR1_47.py` improved strongly, we pushed a standalone Osmium-only aggression ladder further:

| Bot | Day -2 | Day -1 | Day 0 | 3-day Total | Delta vs `TradervR1_34_1.py` |
| --- | ---: | ---: | ---: | ---: | ---: |
| `TradervR1_47.py` | `96'657.5` | `96'739.0` | `96'448.0` | `289'844.5` | `+1'802.0` |
| `TradervR1_48.py` | `96'501.5` | `96'729.0` | `96'455.0` | `289'685.5` | `+1'643.0` |
| `TradervR1_49.py` | `96'501.5` | `96'729.0` | `96'455.0` | `289'685.5` | `+1'643.0` |
| `TradervR1_50.py` | `96'501.5` | `96'729.0` | `96'455.0` | `289'685.5` | `+1'643.0` |
| `TradervR1_51.py` | `96'501.5` | `96'729.0` | `96'455.0` | `289'685.5` | `+1'643.0` |

Read:
- `TradervR1_47.py` is the local peak from this aggression family
- pushing aggression beyond `v47` made the result worse, so that is the first clean local flop point
- stronger variants `v48` to `v51` all collapsed to the same outcome, which suggests the execution logic hit saturation:
  - quote placement is already pinned near `best_ask - 1` / `best_bid + 1`
  - once take thresholds get pushed below the toxicity-driven minimum, further lowering them does not create new good trades

Takeaway:
- the branch was under-aggressive up to `v47`
- the aggression ridge peaks around `v47`
- beyond that, extra aggression is either:
  - ineffective because the logic saturates
  - or slightly harmful because it gives up execution quality without unlocking more capture

### `TradervR1_47_1.py`

Idea:
- keep the exact `TradervR1_47.py` aggression level
- add only a very light Osmium bad-trade brake:
  - side-specific fill-markout EMA
  - small quote-edge penalty after bad fills
  - small size-down in bad states
  - hard veto only when markout is clearly bad and imbalance still points the wrong way

Verified local Rust replay:
- day `-2`: `96'657.5`
  - `ASH_COATED_OSMIUM`: `17'013.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `830`
- day `-1`: `96'739.0`
  - `ASH_COATED_OSMIUM`: `17'371.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `814`
- day `0`: `96'448.0`
  - `ASH_COATED_OSMIUM`: `17'051.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `789`

Read:
- `v47.1` is completely identical to `v47` locally
- that means this first “improve the bad trades” layer is inert on top of the current aggression peak
- the likely reason is that:

### `TradervR1_47_2.py`

Idea:
- keep `TradervR1_47.py` as the attack profile
- add a confidence-gated Osmium mode switch:
  - `attack` when the local book looks calm and trustworthy
  - `normal` when the book is usable but not especially clean
  - `defense` when confidence drops or the book looks noisy / toxic
- leave `INTARIAN_PEPPER_ROOT` completely unchanged

What changed:
- `ASH_COATED_OSMIUM`
  - compute a simple confidence score from:
    - spread width
    - top-of-book depth
    - imbalance magnitude
    - microprice vs mid stability
    - distance from the long-run anchor
    - distance between local fair and raw mid
  - blend take thresholds, quote widths, and passive size between:
    - `v47` attack settings
    - mid-aggression settings near `v46`
    - defensive fallback settings

Verified local Rust replay:
- day `-2`: `96'345.5`
  - `ASH_COATED_OSMIUM`: `16'701.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `821`
- day `-1`: `96'754.0`
  - `ASH_COATED_OSMIUM`: `17'386.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `800`
- day `0`: `96'264.0`
  - `ASH_COATED_OSMIUM`: `16'867.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `786`

Comparison:
- vs `TradervR1_34_1.py`
  - day `-2`: `+216.0`
  - day `-1`: `+537.0`
  - day `0`: `+568.0`
  - three-day delta: `+1'321.0`
- vs `TradervR1_47.py`
  - day `-2`: `-312.0`
  - day `-1`: `+15.0`
  - day `0`: `-184.0`
  - three-day delta: `-481.0`

Read:
- the confidence-gated aggression idea is structurally sane
- it stays comfortably above the old trunk
- but it gives back too much of the `v47` edge
- the fallback logic improves selectivity a bit, but it also trims too many good Osmium opportunities on days `-2` and `0`

Takeaway:
- this is not the new peak
- `TradervR1_47.py` remains the best local aggressive candidate
- the promising part of `v47.2` is the direction:
  - state-selective aggression can work
  - but this first confidence switch is too defensive overall
  - the markout thresholds are too rarely triggered under this branch
  - and/or the current aggressive Osmium logic is already pinned at the effective quote/take boundary

Takeaway:
- the next useful refinement is probably not another very soft brake
- if we keep improving `v47`, it likely needs:
  - a more direct selective rule
  - or a different structural lever than lightweight markout memory

## Robustness Sweep From `v54`

Baseline trunk:
- `TradervR1_54.py`: `292'520.5`
- official-style safe control `TradervR1_52.py`: `290'242.5`

Implemented sweep:
- generated standalone robustness variants under `Bots/Round1/robustness`
- replayed all candidates on Round 1 days `-2 / -1 / 0`
- staged sequence:
  - `R55`: de-risk Osmium aggression
  - `R56`: coarsen Osmium constants
  - `R57`: monotonic take ladders
  - `R58`: slow-fair / fast-signal split
  - `R59`: regime gating
  - `R60`: state-dependent sizing
  - `R61`: light Pepper parameter cleanup
  - ablations + small sensitivity checks

Stage winners:
- Stage A: `TradervR1_R56_OC1_clean.py`
- Stage B: `TradervR1_R58_OF1_blend.py`
- Stage C: `TradervR1_R61_PC1_light.py`

Final promoted candidate:
- `TradervR1_55.py`
- local total: `292'557.5`
- delta vs `TradervR1_54.py`: `+37.0`

Read:
- the only robust improvement that clearly survived was the clean Osmium coarsening pass
- that means slightly rounded Osmium constants were enough to improve the trunk a bit without giving up the edge
- the later structural branches were locally inert on top of that rounded base
- the sensitivity checks also came back flat, which suggests the branch is sitting on a very broad local plateau rather than a knife-edge optimum

What `v55` actually changed:
- kept Pepper behavior effectively unchanged
- kept the same aggressive Osmium shape
- rounded the key Osmium constants into cleaner values:
  - `ANCHOR_WEIGHT 0.5219314046 -> 0.52`
  - `STABLE_MID_WEIGHT 0.4780685954 -> 0.48`
  - `WALL_MID_BLEND 0.2473345402 -> 0.25`
  - `DEPTH_IMPACT_SCALE 33.1754597204 -> 33.18`
  - `INVENTORY_SKEW 0.071843883 -> 0.07`
  - `INVENTORY_CURVE 2.4709663647 -> 2.47`
  - `JOIN_EDGE 1.2583562382 -> 1.26`
  - `SOFT_LIMIT 64.1555274808 -> 64.16`

Artifacts:
- sweep summary: `Analysis/output/round1_robustness_sweep_20260416_105344/summary.md`
- sweep leaderboard: `Analysis/output/round1_robustness_sweep_20260416_105344/leaderboard.csv`

Takeaway:
- this robustness pass did not uncover a new major structural gain
- but it did show that the current edge survives cleaner Osmium constants
- `TradervR1_55.py` is therefore the cleaner and slightly better local continuation of the `v54` branch

## `TradervR1_56.py`

Idea:
- implement the robustness checklist directly as one standalone bot
- keep `INTARIAN_PEPPER_ROOT` almost unchanged
- make `ASH_COATED_OSMIUM` meaningfully less brittle by:
  - de-risking aggression
  - forcing a monotonic take ladder
  - turning on regime routing, size adaptation, and slow-fair / fast-signal separation
  - coarsening more Osmium constants

Task tracker:
- see `TradervR1_56_TASKS.md`

What changed:
- `ASH_COATED_OSMIUM`
  - `BASE_EDGE` moved toward zero
  - `MIN_QUOTE_EDGE` increased
  - `FRONT_SIZE` reduced
  - `SOFT_LIMIT` lowered
  - `JOIN_EDGE` made less aggressive
  - monotonic `TAKE_L1/L2/L3` ladder
  - `REGIME_STYLE`, `SIZE_STYLE`, and `SPLIT_FAIR_STYLE` turned on
  - slow fair now drives reservation and inventory
  - fast signal only nudges taking, quoting, and routing
  - added ablation-friendly toggles for wall-mid, depth impact, nonlinear inventory, join behavior, and take ladder
- `INTARIAN_PEPPER_ROOT`
  - architecture unchanged
  - only light parameter cleanup

Verified local Rust replay:
- day `-2`: `83'674.5`
  - `ASH_COATED_OSMIUM`: `4'030.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `251`
- day `-1`: `83'506.0`
  - `ASH_COATED_OSMIUM`: `4'138.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `256`
- day `0`: `83'835.0`
  - `ASH_COATED_OSMIUM`: `4'438.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `288`

Comparison vs `TradervR1_54.py`:
- day `-2`: `-13'594.0`
- day `-1`: `-14'444.0`
- day `0`: `-13'467.0`
- three-day delta: `-41'505.0`

Read:
- Pepper stayed completely intact
- the entire giveback is Osmium
- the robustness architecture itself is now real and active
- but this first full robustness turn is too conservative and gives away too much normal Osmium spread capture

Takeaway:
- `TradervR1_56.py` is a good research base for robust Osmium behavior
- it is not a promotion candidate over `v54` / `v55`
- the next useful move is probably to re-open some Osmium aggression selectively inside calm / dislocation modes rather than rolling back to the old always-aggressive profile

## `TradervR1_57.py`

Idea:
- take the robust `v56` branch and simplify Osmium down to just 3 modes:
  - `calm_mm`
  - `normal`
  - `toxic_clear`
- hardcode the behavior change inside the mode logic instead of adding more parameters:
  - calm: tighter quotes, slightly larger front size, easier `L1/L2` takes
  - normal: unchanged `v56`-style behavior
  - toxic / inventory clear: wider or one-sided, smaller size, stricter takes

What changed:
- removed the separate `dislocation_take` and `inventory_clear` style branching
- merged bad states into one `toxic_clear` mode
- calm mode now gets:
  - `buy_qe -= 0.35`
  - `sell_qe -= 0.35`
  - `front_size *= 1.20`
  - lower `L1/L2` thresholds
- toxic_clear now:
  - widens the dangerous side
  - cuts size
  - disables one side when imbalance is strongly adverse
- Pepper unchanged from `v56`

Verified local Rust replay:
- day `-2`: `82'432.0`
  - `ASH_COATED_OSMIUM`: `2'788.0`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `155`
- day `-1`: `81'940.0`
  - `ASH_COATED_OSMIUM`: `2'572.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `153`
- day `0`: `82'086.0`
  - `ASH_COATED_OSMIUM`: `2'689.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `173`

Comparison:
- vs `TradervR1_56.py`
  - day `-2`: `-1'242.5`
  - day `-1`: `-1'566.0`
  - day `0`: `-1'749.0`
  - three-day delta: `-4'557.5`
- vs `TradervR1_54.py`
  - three-day delta: `-46'062.5`

Read:
- Pepper stayed fully intact again
- the whole miss is still Osmium
- the 3-mode simplification made the branch even more defensive than `v56`
- that means the missing edge is not just “simplify the mode logic”
- the robust branch still needs some selective re-acceleration in good Osmium states, not another blanket simplification

Takeaway:
- `v57` is cleaner conceptually than `v56`
- but it is worse economically
- the useful lesson is that the robust recovery path needs:
  - stronger calm-mode aggression
  - or a separate positive dislocation/attack permission
  - not only a calm/normal/toxic compression

### `TradervR1_58.py`

Idea:
- keep the robust `v56` architecture
- reopen Osmium aggression only in cleaner states instead of restoring the old global aggressive profile
- use clean rounded changes rather than optimizer-style decimals

What changed:
- `ASH_COATED_OSMIUM`
  - lower global quote edges again, but still much cleaner than `v54`
  - slightly larger front size and slightly higher soft limit
  - lower monotonic take thresholds
  - stronger calm-mode attack:
    - tighter quotes
    - larger front size
    - easier `L1/L2` take permission
    - more willing joining
  - lighter dislocation take gating
- `INTARIAN_PEPPER_ROOT`
  - unchanged from `v56`

Verified local Rust replay:
- day `-2`: `83'807.5`
  - `ASH_COATED_OSMIUM`: `4'163.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `272`
- day `-1`: `83'603.0`
  - `ASH_COATED_OSMIUM`: `4'235.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `273`
- day `0`: `83'812.0`
  - `ASH_COATED_OSMIUM`: `4'415.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `301`

Comparison:
- vs `TradervR1_56.py`
  - day `-2`: `+133.0`
  - day `-1`: `+97.0`
  - day `0`: `-23.0`
  - three-day delta: `+207.0`
- vs `TradervR1_54.py`
  - three-day delta: `-41'298.0`

Read:
- Pepper stayed fully intact again
- the whole change is Osmium
- this is the first robust-architecture follow-up that actually recovers some Osmium edge versus `v56`
- but the recovery is still tiny compared with how much `v56` gave up versus `v54`

Takeaway:
- selective re-acceleration helps
- but the robust branch is still far too defensive overall
- the next useful step, if we continue on this line, is not more Pepper work
- it is to re-open substantially more Osmium aggression inside calm and dislocation states while keeping toxic / inventory-clear behavior intact

### `TradervR1_59.py`

Idea:
- build a real hybrid between the robust `v56` architecture and the more aggressive `v54` Osmium behavior
- keep the robust slow-fair / fast-signal / regime / size structure
- but restore much more aggression in normal, calm, and dislocation states

What changed:
- `ASH_COATED_OSMIUM`
  - more aggressive rounded base parameters:
    - lower `BASE_EDGE`
    - lower `MIN_QUOTE_EDGE`
    - lower monotonic take thresholds
    - larger `FRONT_SIZE`
    - slightly higher `SOFT_LIMIT`
  - calmer states attack much harder:
    - tighter quotes
    - larger front size
    - easier take permission
    - more willing join
  - normal mode no longer adds extra caution
  - toxic mode still keeps the structural brakes instead of reverting fully to `v54`
- `INTARIAN_PEPPER_ROOT`
  - unchanged from `v56`

Verified local Rust replay:
- day `-2`: `91'582.5`
  - `ASH_COATED_OSMIUM`: `11'938.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `565`
- day `-1`: `92'882.0`
  - `ASH_COATED_OSMIUM`: `13'514.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `576`
- day `0`: `91'351.0`
  - `ASH_COATED_OSMIUM`: `11'954.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `563`

Comparison:
- vs `TradervR1_58.py`
  - day `-2`: `+7'775.0`
  - day `-1`: `+9'279.0`
  - day `0`: `+7'539.0`
  - three-day delta: `+24'593.0`
- vs `TradervR1_56.py`
  - three-day delta: `+24'800.0`
- vs `TradervR1_54.py`
  - three-day delta: `-16'705.0`

Read:
- Pepper stayed completely stable again
- the whole gain is recovered Osmium edge
- this is the first branch in the robust family that gets a meaningful amount of aggression back
- but it still remains clearly below the full aggressive trunk

Takeaway:
- the hybrid direction is right
- the useful seam is:
  - robust architecture from `v56`
  - much stronger aggression in normal/calm/dislocation states
  - toxic and inventory-clear protection kept intact
- the remaining gap is that the robust branch still backs off too much relative to `v54`

### `TradervR1_60.py`

Idea:
- continue from `v59`
- relax normal-mode caution further
- make dislocation routing easier
- increase front-size boosts in normal/calm states

What changed:
- `ASH_COATED_OSMIUM`
  - lower dislocation trigger
  - weaker extra signal requirement for dislocation mode
  - lower normal-mode quote edges and take needs
  - stronger normal/calm/dislocation size boosts
  - slightly more willing join in normal mode
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `91'582.5`
  - `ASH_COATED_OSMIUM`: `11'938.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `565`
- day `-1`: `92'882.0`
  - `ASH_COATED_OSMIUM`: `13'514.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `576`
- day `0`: `91'351.0`
  - `ASH_COATED_OSMIUM`: `11'954.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `563`

Comparison:
- vs `TradervR1_59.py`
  - identical on all three days
- vs `TradervR1_54.py`
  - three-day delta: `-16'705.0`

Read:
- this change set was completely inert on top of `v59`
- so the current bottleneck is not small additional loosening of normal/dislocation conditions
- the branch is likely already pinned at the same realized quote/take boundary in the local replay

Takeaway:
- `v60` confirms the direction from `v59`
- but these specific extra relaxations do not move realized behavior
- the next real improvement likely needs either:
  - stronger base aggression again
  - or a different structural lever than more small mode loosening

### `TradervR1_61.py`

Idea:
- keep the robust `v59` hybrid
- add a selective aggression bridge that only activates in high-quality states
- move quote, take, join, and size together instead of nudging a single rule at a time

What changed:
- `ASH_COATED_OSMIUM`
  - added an `attack_factor` from:
    - spread
    - depth
    - imbalance
    - toxicity
    - inventory stretch
    - regime
  - in stronger states, the bot now:
    - lowers quote edges
    - lowers take needs
    - raises join tolerance
    - scales size up slightly
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `91'582.5`
  - `ASH_COATED_OSMIUM`: `11'938.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `565`
- day `-1`: `92'882.0`
  - `ASH_COATED_OSMIUM`: `13'514.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `576`
- day `0`: `91'371.0`
  - `ASH_COATED_OSMIUM`: `11'974.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `564`

Comparison:
- vs `TradervR1_59.py`
  - day `-2`: `0.0`
  - day `-1`: `0.0`
  - day `0`: `+20.0`
  - three-day delta: `+20.0`
- vs `TradervR1_54.py`
  - three-day delta: `-16'685.0`

Read:
- Pepper stayed perfectly stable again
- the change is entirely Osmium
- this is the first non-inert improvement after `v59`, but it is very small

Takeaway:
- the attack-bridge idea is directionally valid
- but the current rounded implementation still only opens a tiny amount of extra Osmium edge
- the next gain probably needs either:
  - a stronger attack bridge
  - or a different structural lever than quote/take shaping alone

### `TradervR1_62.py`

Idea:
- push the structure, not the decimals
- replace some of the attack-layer parameterization with hardcoded execution profiles
- let Osmium trade more by changing placement and sizing style, not by relying on more fine-tuned thresholds

What changed:
- `ASH_COATED_OSMIUM`
  - removed the extra `ATTACK_*` parameter dependence from execution logic
  - added structural execution profiles:
    - `attack`
    - `press`
    - `balanced`
    - `defend`
  - profiles now jointly control:
    - take relief
    - quote-edge relief
    - size multiplier
    - join / inside-improve behavior
  - attack / press profiles can now improve queue position more directly instead of only shaving thresholds
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `91'582.5`
  - `ASH_COATED_OSMIUM`: `11'938.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `565`
- day `-1`: `92'892.0`
  - `ASH_COATED_OSMIUM`: `13'524.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `578`
- day `0`: `91'371.0`
  - `ASH_COATED_OSMIUM`: `11'974.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `564`

Comparison:
- vs `TradervR1_61.py`
  - day `-2`: `0.0`
  - day `-1`: `+10.0`
  - day `0`: `0.0`
  - three-day delta: `+10.0`
- vs `TradervR1_59.py`
  - three-day delta: `+30.0`

Read:
- Pepper stayed perfectly stable again
- the gain is still entirely Osmium
- this is a small result, but it is the cleanest structural improvement in the robust family so far
- importantly, it came from execution-profile structure rather than more numeric fine-tuning

Takeaway:
- “better trades and a higher amount” does seem to respond to profile-based execution
- the effect is still modest, but the direction is credible
- this branch is a better foundation for further structural work than another round of tiny threshold nudges

### `TradervR1_63.py`

Idea:
- test whether the extra multi-state regime routing itself was the restraint
- collapse Osmium into just 2 states:
  - `normal`
  - `toxic_defense`
- let execution profiles carry the rest of the behavior instead of a larger mode tree

What changed:
- `ASH_COATED_OSMIUM`
  - removed the live `calm_mm / dislocation_take / inventory_clear` execution branches
  - folded stretched weak-edge inventory behavior into `toxic_defense`
  - normal mode now owns all non-toxic trading
  - execution profiles still decide whether the bot behaves as:
    - `attack`
    - `press`
    - `balanced`
    - `defend`
  - normal mode is less restrained:
    - easier take permission
    - tighter quotes
    - more willing joining
    - larger front sizes through the profile layer
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `94'072.0`
  - `ASH_COATED_OSMIUM`: `14'428.0`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `625`
- day `-1`: `94'921.0`
  - `ASH_COATED_OSMIUM`: `15'553.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `632`
- day `0`: `93'987.0`
  - `ASH_COATED_OSMIUM`: `14'590.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `622`

Comparison:
- vs `TradervR1_62.py`
  - day `-2`: `+2'489.5`
  - day `-1`: `+2'029.0`
  - day `0`: `+2'616.0`
  - three-day delta: `+7'134.5`
- vs `TradervR1_59.py`
  - three-day delta: `+7'164.5`
- vs `TradervR1_54.py`
  - three-day delta: `-9'540.5`

Read:
- Pepper stayed perfectly stable again
- the whole gain is Osmium
- this is the first major structural jump in the robust family
- the simpler 2-state controller appears to remove a real restraint from the branch

Takeaway:
- the extra regime complexity was likely holding the robust branch back
- a simpler `normal / toxic` controller works better with the execution-profile architecture
- `v63` is still below the full aggressive trunk, but it closes a large part of the gap without falling back into the old fully aggressive design

### `TradervR1_65.py`

Idea:
- test whether the next gain simply comes from a stronger base aggression step again
- keep the `v63` two-state structure, but move the base Osmium parameters closer to the older aggressive trunk

What changed:
- `ASH_COATED_OSMIUM`
  - lower `BASE_EDGE`
  - lower `MIN_QUOTE_EDGE`
  - lower take thresholds
  - larger `FRONT_SIZE`
  - slightly higher `SOFT_LIMIT`
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `94'060.5`
- day `-1`: `94'841.0`
- day `0`: `94'003.0`

Comparison:
- vs `TradervR1_63.py`
  - day `-2`: `-11.5`
  - day `-1`: `-80.0`
  - day `0`: `+16.0`
  - three-day delta: `-75.5`

Read:
- stronger blanket aggression did not help
- it traded more, but with worse net quality
- so the next gain is probably not “just make the whole bot more aggressive again”

### `TradervR1_66.py`

Idea:
- test a different structural lever than quote/take/join tuning
- keep `v63` parameters, but concentrate more size at the front in good states instead of splitting across the ladder

What changed:
- `ASH_COATED_OSMIUM`
  - added front-size concentration in non-toxic normal / attack / press states
  - shifted back size into the front quote in those states
  - reduced ladder fragmentation without broad parameter changes
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `94'072.0`
- day `-1`: `94'921.0`
- day `0`: `93'987.0`

Comparison:
- identical to `TradervR1_63.py` on all three days

Read:
- the front-concentration structural lever was completely inert in local replay
- that means the live execution boundary did not move from this change alone

Takeaway:
- `v65` says stronger base aggression again is not the next answer
- `v66` says this particular alternative structural lever is inert
- so `v63` remains the best branch from this round of tests

### `TradervR1_67.py`

Idea:
- test whether the bottleneck is weaker early/mid Oscmium monetization on the exit side
- in normal non-toxic states, prioritize the inventory-reducing side a bit more

What changed:
- `ASH_COATED_OSMIUM`
  - added a normal-mode exit-priority bias
  - when long, sells get:
    - slightly tighter quote edge
    - slightly larger front size
    - slightly more inside improvement
  - symmetric behavior on the buy side when short
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `94'099.0`
- day `-1`: `94'921.0`
- day `0`: `93'959.0`

Comparison:
- vs `TradervR1_63.py`
  - day `-2`: `+27.0`
  - day `-1`: `0.0`
  - day `0`: `-28.0`
  - three-day delta: `-1.0`

Read:
- the idea is directionally plausible
- but in local replay it is effectively neutral

### `TradervR1_68.py`

Idea:
- test whether the remaining restraint is entering `toxic_defense` too early
- only go defensive when toxicity actually threatens current inventory, or when the market is both wide and toxic

What changed:
- `ASH_COATED_OSMIUM`
  - toxicity routing became inventory-aware:
    - `bid_toxic` only forces defense when we are meaningfully long
    - `ask_toxic` only forces defense when we are meaningfully short
    - or when spread is wide and the book is toxic
  - otherwise the bot stays in `normal` and keeps monetizing
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `94'383.5`
  - `ASH_COATED_OSMIUM`: `14'739.5`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `647`
- day `-1`: `94'960.0`
  - `ASH_COATED_OSMIUM`: `15'592.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `653`
- day `0`: `94'181.0`
  - `ASH_COATED_OSMIUM`: `14'784.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `634`

Comparison:
- vs `TradervR1_63.py`
  - day `-2`: `+311.5`
  - day `-1`: `+39.0`
  - day `0`: `+194.0`
  - three-day delta: `+544.5`
- vs `TradervR1_54.py`
  - three-day delta: `-8'996.0`

### `TradervR1_69.py`

Idea:
- replace the broad toxic-mode switch with side-specific toxic levels
- treat bid-side and ask-side toxicity separately, with mild and severe severity instead of one global defense state

What changed:
- `ASH_COATED_OSMIUM`
  - toxicity is now per side:
    - `bid_toxic_level in {0, 1, 2}`
    - `ask_toxic_level in {0, 1, 2}`
  - mild toxicity:
    - widens that side a bit
    - trims same-side add/take permission slightly
    - keeps the other side monetizing
  - severe toxicity:
    - widens that side more
    - can shut down only that side when inventory is exposed
  - toxic pressure now helps the exit side:
    - if we are long and bids are toxic, asks get a small extra push
    - if we are short and asks are toxic, bids get a small extra push
  - global `toxic_defense` was removed from the live routing
    - only `inventory_clear` remains as a true defensive mode
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `96'507.0`
  - `ASH_COATED_OSMIUM`: `16'863.0`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `656`
- day `-1`: `97'390.0`
  - `ASH_COATED_OSMIUM`: `18'022.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `672`
- day `0`: `96'482.0`
  - `ASH_COATED_OSMIUM`: `17'085.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `655`

Comparison:
- vs `TradervR1_68.py`
  - day `-2`: `+2'123.5`
  - day `-1`: `+2'430.0`
  - day `0`: `+2'301.0`
  - three-day delta: `+6'854.5`
- vs `TradervR1_63.py`
  - three-day delta: `+7'399.0`
- vs `TradervR1_54.py`
  - day `-2`: `-761.5`
  - day `-1`: `-560.0`
  - day `0`: `-820.0`
  - three-day delta: `-2'141.5`

Read:
- this is a real bottleneck release
- the problem was not “too little global defense” or “too little aggression everywhere”
- the problem was that whole-engine toxic switching was still too broad
- once toxicity became side-specific and severity-based, Osmium could keep trading the safe side while backing off only where needed

### `TradervR1_70.py`

Idea:
- keep the side-specific toxic levels from `v69`
- add light toxic memory so severe toxicity usually needs persistence or real inventory exposure, instead of triggering off one noisy snapshot

What changed:
- `ASH_COATED_OSMIUM`
  - side-specific toxic levels now flow through a small persistent score in `traderData`
  - mild toxicity can still appear immediately
  - severe toxicity now usually requires:
    - repeated same-side toxic pressure, or
    - clearly exposed inventory on that side
  - toxic scores decay when the book calms down, so the engine can re-arm naturally
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `97'553.0`
  - `ASH_COATED_OSMIUM`: `17'909.0`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `681`
- day `-1`: `98'521.0`
  - `ASH_COATED_OSMIUM`: `19'153.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `685`
- day `0`: `97'509.0`
  - `ASH_COATED_OSMIUM`: `18'112.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `667`

Comparison:
- vs `TradervR1_69.py`
  - day `-2`: `+1'046.0`
  - day `-1`: `+1'131.0`
  - day `0`: `+1'027.0`
  - three-day delta: `+3'204.0`
- vs `TradervR1_54.py`
  - day `-2`: `+284.5`
  - day `-1`: `+571.0`
  - day `0`: `+207.0`
  - three-day delta: `+1'062.5`

Read:
- this keeps the `v69` idea, but removes some of the snap-to-defense behavior
- the toxic layer is now less jumpy and more side-aware over time
- the gain is entirely Osmium again; Pepper remains identical

### `TradervR1_71.py`

Idea:
- keep the side-specific toxic memory from `v70`
- make the toxic score actively accelerate exits when inventory is exposed

What changed:
- `ASH_COATED_OSMIUM`
  - if long and bid-side toxic pressure is elevated:
    - new buys are restrained more
    - asks get more aggressive
    - ask front size increases
    - exit-side joining becomes easier
  - mirror logic for short inventory under ask-side toxic pressure
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `97'540.0`
  - `ASH_COATED_OSMIUM`: `17'896.0`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `682`
- day `-1`: `98'513.0`
  - `ASH_COATED_OSMIUM`: `19'145.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `686`
- day `0`: `97'509.0`
  - `ASH_COATED_OSMIUM`: `18'112.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `667`

Comparison:
- vs `TradervR1_70.py`
  - day `-2`: `-13.0`
  - day `-1`: `-8.0`
  - day `0`: `0.0`
  - three-day delta: `-21.0`

Read:
- the idea is directionally reasonable
- but this version exits a little too eagerly
- Pepper stayed identical, and the small giveback is entirely Osmium

### `TradervR1_72.py`

Idea:
- keep the side-specific toxic memory from `v70`
- add real hysteresis to toxic severity:
  - mild toxicity can appear immediately
  - severe toxicity should usually require persistence or real inventory exposure
  - once severe toxicity is active, it decays more slowly instead of snapping off

What changed:
- `ASH_COATED_OSMIUM`
  - side-specific toxic scores now use asymmetric enter/exit behavior
  - severe toxic levels are harder to trigger from one noisy snapshot
  - severe levels also unwind more gradually, reducing flip-flop behavior
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `97'717.0`
  - `ASH_COATED_OSMIUM`: `18'073.0`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `668`
- day `-1`: `98'509.0`
  - `ASH_COATED_OSMIUM`: `19'141.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `681`
- day `0`: `97'529.0`
  - `ASH_COATED_OSMIUM`: `18'132.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `658`

Comparison:
- vs `TradervR1_70.py`
  - day `-2`: `+164.0`
  - day `-1`: `-12.0`
  - day `0`: `+20.0`
  - three-day delta: `+172.0`

Read:
- this is a small but clean improvement
- it comes entirely from Osmium
- the gain comes with fewer trades, which is a good sign that the toxic layer is behaving more selectively rather than just becoming more active

### `TradervR1_72` toxicity sweep

Goal:
- test *directional* changes to the `v72` toxic-memory idea instead of doing tiny local nudges

Variants:
- `TradervR1_72_s1.py`
  - harder defense
  - faster toxic build
  - slower decay
  - lower severe thresholds
- `TradervR1_72_s2.py`
  - softer defense
  - slower severe entry
  - faster decay
  - higher severe thresholds
- `TradervR1_72_s3.py`
  - inventory-biased severity
  - easier severe entry only when exposure is already meaningful
  - harder severe entry otherwise
- `TradervR1_72_s4.py`
  - sticky severe
  - slower severe decay after activation
- `TradervR1_72_s5.py`
  - remove mild persistence
  - only let raw toxic reads or severe persistence keep the state alive

Results:
- `TradervR1_72.py`: `293'755.0`
- `TradervR1_72_s1.py`: `291'237.5`
- `TradervR1_72_s2.py`: `294'139.0`
- `TradervR1_72_s3.py`: `293'846.0`
- `TradervR1_72_s4.py`: `293'564.0`
- `TradervR1_72_s5.py`: `293'892.0`

Read:
- the worst direction was `s1`
  - making toxicity harsher and stickier too early clearly hurt
- the best direction was `s2`
  - softer severe entry
  - faster decay
  - higher severe thresholds
- `s3` and `s5` were both mildly positive
  - inventory-biased severity helped a bit
  - removing mild persistence also helped a bit
- `s4` showed that “stickier severe” is not the answer by itself

Conclusion:
- the branch still wants toxicity to be selective
- the next gains come from avoiding overclassification into severe toxic states, not from pushing defense harder

### `TradervR1_73.py`

Idea:
- promote the best sweep direction from `TradervR1_72_s2.py` into a clean candidate

What changed vs `TradervR1_72.py`:
- severe toxicity enters more slowly
- severe toxicity decays faster
- severe thresholds are higher
- mild toxic behavior remains intact

Verified local Rust replay:
- day `-2`: `97'798.0`
  - `ASH_COATED_OSMIUM`: `18'154.0`
  - `INTARIAN_PEPPER_ROOT`: `79'644.0`
  - trades: `669`
- day `-1`: `98'735.0`
  - `ASH_COATED_OSMIUM`: `19'367.0`
  - `INTARIAN_PEPPER_ROOT`: `79'368.0`
  - trades: `686`
- day `0`: `97'606.0`
  - `ASH_COATED_OSMIUM`: `18'209.0`
  - `INTARIAN_PEPPER_ROOT`: `79'397.0`
  - trades: `661`

Comparison:
- vs `TradervR1_72.py`
  - day `-2`: `+81.0`
  - day `-1`: `+226.0`
  - day `0`: `+77.0`
  - three-day delta: `+384.0`

Read:
- this is the best local candidate from the toxicity sweep
- the gain is entirely Osmium
- the best direction was not “more defense,” but more selective severe defense

### `TradervR1_74.py`

Idea:
- use the full fill graph to test a `wide_safe_harvest` overlay
- in wide, clean states:
  - improve the front quote more aggressively
  - keep a tiny third wing quote to catch outer-edge fills

What changed:
- `ASH_COATED_OSMIUM`
  - added a wide-spread, low-toxicity harvest branch
  - front quote became more competitive in those states
  - added a tiny wing quote beyond the back quote
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `97'553.0`
- day `-1`: `98'521.0`
- day `0`: `97'509.0`

Comparison:
- exactly identical to `TradervR1_70.py`

Read:
- the graph-based idea was directionally plausible
- but this implementation was completely inert
- that means the missing edge is probably not “quote an extra outer wing” by itself

### `TradervR1_75.py`

Idea:
- use `state.own_trades` directly to react to same-side passive fills
- after a safe buy fill, keep bids slightly more aggressive for a short window
- after a safe sell fill, do the same on asks

What changed:
- `ASH_COATED_OSMIUM`
  - added per-side decaying reload scores from `own_trades`
  - reload only activates in benign states:
    - normal mode
    - low toxicity
    - moderate imbalance
  - same-side take need, quote edge, join tolerance, and front size get a small temporary boost
- `INTARIAN_PEPPER_ROOT`
  - unchanged

Verified local Rust replay:
- day `-2`: `97'553.0`
- day `-1`: `98'521.0`
- day `0`: `97'509.0`

Comparison:
- exactly identical to `TradervR1_70.py`

Read:
- the fill-reactive continuation idea is structurally reasonable
- but this first implementation was too soft to change realized behavior
- so the branch is still sitting on the same effective execution boundary as `v70`

### `TradervR1_80` to `TradervR1_83` behavior-jump sweep

Goal:
- try genuinely different execution behaviors on top of `TradervR1_70.py`, not more smooth threshold tuning

Variants:
- `TradervR1_80.py`
  - discrete safe-state quote placement
  - explicit touch vs one-tick-inside behavior in benign states
- `TradervR1_81.py`
  - safe-state take jump
  - easier `L1` taking only in clean states
- `TradervR1_82.py`
  - front-size concentration
  - push more size to the front and less to the back in benign states
- `TradervR1_83.py`
  - inventory-aware safe-state exit bias
  - stronger quote/join preference on the exit side when carrying inventory

Results:
- `TradervR1_70.py`: `293'583.0`
- `TradervR1_80.py`: `293'583.0`
- `TradervR1_81.py`: `293'619.5`
- `TradervR1_82.py`: `284'281.5`
- `TradervR1_83.py`: `292'536.5`

Read:
- `TradervR1_81.py` is the only behavior jump that helped
  - three-day delta vs `TradervR1_70.py`: `+36.5`
  - the gain is entirely Osmium
  - trades also increased: `2058` vs `2033`
- `TradervR1_80.py` was completely inert
- `TradervR1_82.py` was clearly harmful
  - front concentration damaged Osmium heavily
- `TradervR1_83.py` was directionally plausible but still worse than the trunk

Conclusion:
- the only live family from this sweep is **safe-state make/take hybridization**
- the branch still does not want:
  - more front concentration
  - or stronger exit bias by itself
- if we continue from here, `TradervR1_81.py` is the right donor branch

### `TradervR1_70` lever sweep

Goal:
- test several different execution levers on top of `TradervR1_70.py`
- find out whether the next edge is in quote placement, taking, front-size concentration, or inventory-aware exit bias

Variants:
- `TradervR1_76.py`
  - discrete safe-state quote placement
  - more inside/improve behavior in benign normal states
- `TradervR1_77.py`
  - safe-state `L1` take relief
  - easier small takes when the book is clean
- `TradervR1_78.py`
  - front-size concentration
  - bigger front, smaller back in safe states
- `TradervR1_79.py`
  - inventory-aware safe-state exit bias
  - stronger exit-side quote / join / size preference

Results:
- `TradervR1_70.py`: `293'583.0`
- `TradervR1_76.py`: `293'583.0`
- `TradervR1_77.py`: `293'583.0`
- `TradervR1_78.py`: `293'583.0`
- `TradervR1_79.py`: `293'583.0`

Read:
- all four lever families were completely inert in local replay
- this strongly suggests the current branch is pinned at one effective execution boundary
- small quote/take/size/join adjustments are no longer crossing real fill boundaries

Conclusion:
- the next gain probably does not come from another soft modifier
- it likely needs a more discrete behavior jump, for example:
  - explicit touch-vs-inside quoting
  - explicit side shutdown / side permission
  - or a different inventory/state transition rule

Read:
- Pepper stayed perfectly stable again
- the gain is entirely Osmium
- this is the strongest new bottleneck release after `v63`

Takeaway:
- the robust branch was still going defensive too broadly
- making toxicity inventory-aware lets the bot keep monetizing normal states longer
- this looks like a stronger next trunk than `v63`

### `TradervR1_81` family follow-up

Goal:
- keep pushing the only live family from the recent execution sweep
- test whether the edge comes from:
  - a narrower but stronger benign-state taker
  - inventory-aware asymmetric safe-state taking
  - or coupling the safe state to front-quote placement

Variants:
- `TradervR1_84.py`
  - narrower / cleaner safe-state filter
  - stronger mini-takes and slightly stronger benign exit recycle
- `TradervR1_85.py`
  - inventory-aware asymmetric safe-state make/take hybrid
  - gives more relief to the exit side when already carrying inventory
- `TradervR1_86.py`
  - quote-coupled safe-state hybrid
  - keeps the `v81` extra takes but also makes front quotes more competitive in the same state

Results:
- `TradervR1_70.py`: `293'583.0`
- `TradervR1_81.py`: `293'619.5`
- `TradervR1_84.py`: `293'583.0`
- `TradervR1_85.py`: `293'656.5`
- `TradervR1_86.py`: `293'619.5`

Read:
- `TradervR1_85.py` is the best continuation of this family
  - delta vs `TradervR1_70.py`: `+73.5`
  - delta vs `TradervR1_81.py`: `+37.0`
  - the gain is entirely Osmium
  - Pepper stayed fixed at `238'409.0`
  - trades rose to `2060` vs `2058` in `v81`
- `TradervR1_84.py` fell back to the exact `v70` boundary
  - the narrower / stronger benign filter was too restrictive overall
- `TradervR1_86.py` was exactly identical to `v81`
  - coupling the same safe state to quote placement did not change realized fills

Conclusion:
- this family still has some life
- the useful direction is not “cleaner but narrower”
- it is **inventory-aware asymmetric safe-state taking**
- if we keep going from this branch, `TradervR1_85.py` is the right donor

### `TradervR1_87.x` basic Osmium strategy matrix

Goal:
- test the basic market-making families directly on `ASH_COATED_OSMIUM`
- keep Pepper fixed
- find out where the product becomes "real" and where the logic is still too naive

Variants:
- `TradervR1_87_1.py`
  - Version A
  - pure anchor maker
  - fair = `10000`, fixed symmetric spread
- `TradervR1_87_2.py`
  - Version B
  - anchor + inventory skew maker
  - fair = `10000`, reservation shifted by inventory
- `TradervR1_87_3.py`
  - Version C
  - local-fair symmetric maker
  - fair = anchor + stable mid + wall-mid + micro/imbalance adjustment
- `TradervR1_87_4.py`
  - Version D
  - local-fair + inventory skew maker
- `TradervR1_87_5.py`
  - Version E
  - local-fair + skew + toxicity gate
- `TradervR1_87_6.py`
  - Version F
  - local-fair + skew + hybrid stale-quote taking

Results:
- `TradervR1_87_1.py`: `257'486.0`
- `TradervR1_87_2.py`: `259'732.5`
- `TradervR1_87_3.py`: `263'593.0`
- `TradervR1_87_4.py`: `261'862.5`
- `TradervR1_87_5.py`: `261'049.5`
- `TradervR1_87_6.py`: `270'535.0`

Reference:
- `TradervR1_70.py`: `293'583.0`
- `TradervR1_85.py`: `293'656.5`

Read:
- the family ranking is very clean:
  - best basic version: `TradervR1_87_6.py`
  - next best: `TradervR1_87_3.py`
  - worst: `TradervR1_87_1.py`
- every single variant kept Pepper fixed at `238'409.0`
- so the whole test is a pure Osmium read
- the product clearly wants more than a dumb anchored maker
- local fair helps materially:
  - `v87_3` beat `v87_1` by `+6'107.0`
- hybrid taking helps materially:
  - `v87_6` beat `v87_4` by `+8'672.5`
- simple toxicity gating on top of the basic engine did not help here:
  - `v87_5` was worse than `v87_4`
- surprisingly, the simple linear inventory skew versions were not better than the equivalent no-skew version in this stripped-down family

Conclusion:
- the matrix confirms the product identity pretty strongly:
  - **local fair matters**
  - **selective hybrid taking matters**
  - **a basic anchor maker is far too weak**
- but it also confirms that the current edge in the live branch is not coming from the basic family alone
- the gap from `v87_6` to `TradervR1_70.py` is still huge, so the real value is in:
  - smarter execution
  - richer toxicity handling
  - and the more evolved Osmium control logic we built later

### `TradervR1_88.py`

Goal:
- test the hypothesis that Osmium has a real microstructure pattern in one-sided / half-empty books
- instead of ignoring those states, treat them as temporary vacuum states and handle the refill explicitly

What changed:
- based on the `TradervR1_73` / `TradervR1_70` family
- `ASH_COATED_OSMIUM` now:
  - detects one-sided books (`bid_only` / `ask_only`)
  - stores the last good two-sided fair in memory
  - uses a frozen fair blend during vacuum states
  - only quotes the missing side lightly, and only when it helps flatten inventory
  - dampens fair / signal usage on the first normal book after a vacuum refill
- `INTARIAN_PEPPER_ROOT` unchanged

Results:
- `TradervR1_70.py`: `293'583.0`
- `TradervR1_88.py`: `294'073.0`

By day:
- `TradervR1_88.py`: `97'738.0 / 98'730.0 / 97'605.0`
- delta vs `TradervR1_70.py`: `+185.0 / +209.0 / +96.0`

Read:
- this is a real local improvement
- the gain is entirely Osmium:
  - `TradervR1_70.py` Ash: `55'174.0`
  - `TradervR1_88.py` Ash: `55'664.0`
- Pepper stayed fixed at `238'409.0`
- trades actually fell a bit:
  - `TradervR1_70.py`: `2033`
  - `TradervR1_88.py`: `2007`

Conclusion:
- the one-sided book / refill pattern looks actionable, not just descriptive
- Osmium seems to benefit from:
  - not trusting vacuum states as true fair value
  - and not dropping those states entirely either
- `TradervR1_88.py` is the new best local branch from this line of research

### `TradervR1_89.py`

Goal:
- improve the vacuum-state branch by calculating a more explicit side-specific fair in one-sided books
- test whether the bot can safely participate on the visible side as well, instead of using vacuum states only defensively

What changed:
- built on `TradervR1_88.py`
- added a side-specific synthetic vacuum fair:
  - `bid_only`: visible bid + recent half-spread estimate
  - `ask_only`: visible ask - recent half-spread estimate
- blended that synthetic fair with the frozen last-good fair
- used the synthetic vacuum fair to:
  - stabilize the first refill tick more directly
  - allow tiny visible-side participation in vacuum states when the refill edge is large enough
- kept the missing-side flattening logic from `v88`

Results:
- `TradervR1_88.py`: `294'073.0`
- `TradervR1_89.py`: `294'346.0`

By day:
- `TradervR1_89.py`: `97'891.0 / 98'781.0 / 97'674.0`
- delta vs `TradervR1_88.py`: `+153.0 / +51.0 / +69.0`

Read:
- this is another real local improvement
- all of the gain is Osmium:
  - `TradervR1_88.py` Ash: `55'664.0`
  - `TradervR1_89.py` Ash: `55'937.0`
- Pepper stayed fixed at `238'409.0`
- trades rose slightly:
  - `TradervR1_88.py`: `2007`
  - `TradervR1_89.py`: `2047`

Conclusion:
- the vacuum branch improves further when the bot calculates a side-specific refill fair instead of only freezing the last healthy fair
- light visible-side participation in vacuum states appears to be helping rather than hurting
- `TradervR1_89.py` is the new best local version from the vacuum / refill branch

### `TradervR1_89` official read and `v90` follow-up

Official `TradervR1_89.log` vs `TradervR1_70.log`:
- `TradervR1_70.log`: `10'383.59375`
- `TradervR1_89.log`: `10'403.15625`
- delta: `+19.5625`

Read from the official log:
- the gain is entirely Osmium
  - `v70` Ash: `2'797.59375`
  - `v89` Ash: `2'817.15625`
- Pepper is identical at `7'586.0`
- drawdown is identical at `173.0`
- `v89` buys Osmium slightly cheaper, but sells only slightly worse
- this suggested the vacuum edge was real, but maybe stronger on the `bid_only` side than on the `ask_only` side

Follow-up variants:
- `TradervR1_90.py`
  - asymmetric vacuum thresholds / blends
  - stronger `bid_only` participation, stricter `ask_only`
- `TradervR1_90_1.py`
  - `bid_only` visible participation only
  - `ask_only` visible-side participation disabled
- `TradervR1_90_2.py`
  - inventory-aligned `ask_only` visible participation
  - only sell the visible ask when already long

Local replay:
- `TradervR1_89.py`: `294'346.0`
- `TradervR1_90.py`: `294'362.0`
- `TradervR1_90_1.py`: `294'062.5`
- `TradervR1_90_2.py`: `294'323.0`

Read:
- `TradervR1_90.py` is only `+16.0` over `v89` locally
- `TradervR1_90_1.py` is clearly worse
- `TradervR1_90_2.py` is slightly worse
- the stricter / more one-sided interpretations of the vacuum edge do not look stronger than `v89`

Conclusion:
- the official `v89` gain looks real
- but the edge does not seem to want a much harsher asymmetric rewrite
- `TradervR1_89.py` remains the best branch to upload from this family unless a future official test shows `v90` transfers the tiny local gain

### `TradervR1_92.py`

Pattern-driven Osmium rewrite from the new book-structure research:
- reduced anchor reliance in the slow fair
- promoted the top-3 stable book into the main local-fair center
- in tight books, let microprice and imbalance dominate the fast signal
- if stable-book fair and imbalance agree, increase conviction
- if they disagree, trust imbalance / microprice over stable-book pull
- use public trades only as a confirmation layer when they align with imbalance
- kept the `v89` vacuum handling and Pepper unchanged

Local replay:
- `TradervR1_89.py`: `294'346.0`
- `TradervR1_92.py`: `294'366.0`

By day:
- `TradervR1_92.py`: `97'774.0 / 98'763.0 / 97'829.0`
- delta vs `v89`: `-117.0 / -18.0 / +155.0`

Read:
- this is a real full-stack Osmium signal rewrite, not another threshold tweak
- total gain is small but positive: `+20.0`
- Pepper stayed identical
- the new hierarchy seems most helpful on day `0`, while days `-2` and `-1` gave back a little

Conclusion:
- the local-fair / imbalance hierarchy looks directionally right
- but the added conviction machinery is still only a modest improvement over `v89`
- `TradervR1_92.py` is a valid research continuation, but not yet a clear new champion

### `TradervR1_92` research branch

I opened a proper research branch off `v92` to isolate which part of the rewrite was actually helping:

- `TradervR1_93.py`
  - kept the new hierarchy
  - removed the extra conviction spillover into attack, quote relief, take relief, and size
- `TradervR1_94.py`
  - kept `v92`
  - removed trade-print confirmation entirely
- `TradervR1_95.py`
  - softer full hierarchy
  - more anchor in the slow fair
  - lighter agreement / magnet bonuses
  - no stable-book pull at all in disagreement states
  - lighter conviction spillover
- `TradervR1_96.py`
  - mid-ground hierarchy
  - slightly more anchor
  - no trade confirmation
  - no stable-book pull in disagreement states

Local replay:
- `TradervR1_89.py`: `294'346.0`
- `TradervR1_92.py`: `294'366.0`
- `TradervR1_93.py`: `294'458.0`
- `TradervR1_94.py`: `294'366.0`
- `TradervR1_95.py`: `294'773.0`
- `TradervR1_96.py`: `294'482.0`

Read:
- the rewrite absolutely still has life
- removing trade confirmation did nothing:
  - `TradervR1_94.py` was exactly the same as `v92`
- pure hierarchy without conviction spillover helped:
  - `TradervR1_93.py` beat `v92` by `+92.0`
- the best version was the softer hierarchy:
  - `TradervR1_95.py` beat `v92` by `+407.0`
  - `TradervR1_95.py` beat `v89` by `+427.0`
- `TradervR1_96.py` also improved, but less than `v95`

Best interpretation:
- the stable-book / imbalance rewrite is good
- the part that was too blunt in `v92` was the heavy conviction machinery
- trade prints were not contributing meaningful edge here
- disagreement states should trust imbalance cleanly, without keeping a residual stable-book pull
- the rewrite works better when it stays more anchored and more selective

Conclusion:
- `TradervR1_95.py` is the new best research continuation from this branch
- the surviving idea is:
  - slow fair = anchor + stable-book
  - fast signal = micro / imbalance
  - agreement boosts conviction
  - disagreement follows imbalance
  - keep the extra conviction effects light

### `TradervR1_97.py`

Promoted the winning `v95` research shape into a clean next mainline version:
- same surviving hierarchy as `TradervR1_95.py`
- no trade-print confirmation
- more anchor in the slow fair
- lighter agreement / magnet bonuses
- no residual stable-book pull in disagreement states
- lighter conviction spillover into execution

Local replay:
- `TradervR1_97.py`: `97'914.0 / 98'906.0 / 97'953.0`
- three-day total: `294'773.0`

Reference:
- `TradervR1_89.py`: `294'346.0`
- `TradervR1_92.py`: `294'366.0`
- `TradervR1_95.py`: `294'773.0`

Read:
- `TradervR1_97.py` is exactly the promoted production version of the best research candidate
- delta vs `TradervR1_89.py`: `+427.0`
- delta vs `TradervR1_92.py`: `+407.0`
- the improvement is entirely Osmium; Pepper stays unchanged

Conclusion:
- `TradervR1_97.py` is the right trunk to test next from the stable-book / imbalance rewrite branch

### `TradervR1_98.py`

Next continuation off `TradervR1_97.py`:
- removed the remaining trade-print confirmation dependency entirely
- made stable-book agreement explicitly thresholded
- made disagreement states lean harder into imbalance / micro instead of any residual stable-book pull

Local replay:
- `TradervR1_97.py`: `97'914.0 / 98'906.0 / 97'953.0`
- `TradervR1_98.py`: `97'914.0 / 98'906.0 / 97'941.0`

Three-day total:
- `TradervR1_97.py`: `294'773.0`
- `TradervR1_98.py`: `294'761.0`

Read:
- `v98` is effectively the same bot on days `-2` and `-1`
- it gave back `12.0` on day `0`
- so the explicit thresholding / harder disagreement override did not improve on the softer `v97` balance

Conclusion:
- `TradervR1_97.py` remains the better mainline version
- the rewrite still seems to want a softer treatment than a more discrete threshold controller

### `TradervR1_99.py`

Tried the refill-state decision layer on top of `TradervR1_97.py`:
- classify the first valid post-vacuum book as:
  - `strong`
  - `weak`
  - `unstable`
- `strong`: re-arm normal behavior quickly
- `weak`: bias toward the exit side
- `unstable`: suppress taking for one tick and shrink size slightly

Local replay:
- `TradervR1_97.py`: `97'914.0 / 98'906.0 / 97'953.0`
- `TradervR1_99.py`: `97'607.5 / 98'730.0 / 97'579.0`

Three-day total:
- `TradervR1_97.py`: `294'773.0`
- `TradervR1_99.py`: `293'916.5`

Read:
- `v99` is clearly worse than `v97`
- the refill-state controller made the bot too cautious
- the whole giveback is Osmium; Pepper stayed unchanged

Conclusion:
- the refill transition is important conceptually
- but this first strong/weak/unstable controller over-damped good post-vacuum trading
- `TradervR1_97.py` remains the better trunk

### `TradervR1_100.py`

Plateau / fill-drought experiment on top of `TradervR1_97.py`:
- detect long no-fill stretches while:
  - inventory is near flat
  - the book is still normal / benign
  - no vacuum is active
  - toxicity is low
- in those stretches:
  - ease quote edges slightly
  - join a bit more aggressively
  - lift front size by a tiny amount
  - relax take needs slightly

Local replay:
- `TradervR1_97.py`: `97'914.0 / 98'906.0 / 97'953.0`
- `TradervR1_100.py`: `97'914.0 / 98'904.0 / 97'953.0`

Three-day total:
- `TradervR1_97.py`: `294'773.0`
- `TradervR1_100.py`: `294'771.0`

Read:
- essentially inert
- no meaningful gain on the plateau idea in this first form
- only `-2.0` on day `-1`
- so a soft anti-plateau mode does not seem to cross a new fill boundary yet

Conclusion:
- the plateau diagnosis was reasonable
- but the first no-fill harvester was too mild to unlock extra PnL
- `TradervR1_97.py` remains the stronger trunk

### Plateau Sweep from `TradervR1_97.py`

I explored the flat sections more directly and tried three discrete anti-plateau variants:

- `TradervR1_101.py`
  - plateau touch-maker
  - after a benign no-fill drought, collapse to single-front touch-style quoting
- `TradervR1_102.py`
  - plateau taker pulse
  - after a benign no-fill drought, relax take needs more aggressively
- `TradervR1_103.py`
  - combination of touch-maker and taker-pulse

Plateau read from official logs:
- the biggest late flat section in `TradervR1_95.log` around `62.7k–65.7k` happened in a still-normal book
- inventory was near flat
- almost no trades occurred
- so the plateau looked like a benign no-fill drought, not a clearly dead or toxic market

Local replay:
- `TradervR1_97.py`: `97'914.0 / 98'906.0 / 97'953.0`
- `TradervR1_101.py`: `97'914.0 / 98'906.0 / 97'953.0`
- `TradervR1_102.py`: `97'914.0 / 98'906.0 / 97'953.0`
- `TradervR1_103.py`: `97'914.0 / 98'906.0 / 97'953.0`

Read:
- all three plateau variants were completely inert
- neither touch-style passive harvesting nor a small taker pulse changed realized fills
- this strongly suggests the branch is pinned at the same effective execution boundary in those plateau states

Conclusion:
- the plateau phenomenon is real
- but these first discrete anti-plateau actions do not unlock it
- the next plateau idea would need a deeper execution jump than these mild drought handlers

### Stronger Plateau Sweep from `TradervR1_97.py`

I pushed the plateau idea harder with three more discrete variants:

- `TradervR1_104.py`
  - queue-priority plateau maker
  - after a benign no-fill drought, force one-tick-inside quotes and drop the back layer
- `TradervR1_105.py`
  - plateau taker pulse
  - after a benign no-fill drought, cross small size on the signal side
- `TradervR1_106.py`
  - combined plateau maker + taker pulse

Local replay:
- `TradervR1_97.py`: `97'914.0 / 98'906.0 / 97'953.0`
- `TradervR1_104.py`: `97'914.0 / 98'906.0 / 97'953.0`
- `TradervR1_105.py`: `97'575.0 / 98'475.0 / 97'592.0`
- `TradervR1_106.py`: `97'688.0 / 98'649.0 / 97'782.0`

Three-day totals:
- `TradervR1_97.py`: `294'773.0`
- `TradervR1_104.py`: `294'773.0`
- `TradervR1_105.py`: `293'642.0`
- `TradervR1_106.py`: `294'119.0`

Read:
- forcing one-tick-inside plateau quotes was completely inert
- the only thing that really changed behavior was small taker aggression
- and that was clearly harmful
- so the plateau is not solved by “trade a bit harder” or “cross a bit when bored”

Conclusion:
- the branch already seems to be near its passive fill frontier
- when we try to break the plateau by taking, PnL gets worse
- if there is still a plateau edge, it likely requires a better queue-position / catalyst model, not simple extra aggression

### Queue-Position / Catalyst Sweep from `TradervR1_97.py`

I tested the two deeper levers suggested by the plateau work:

- `TradervR1_107.py`
  - queue-priority maker
  - choose between stepping back, joining touch, and improving one tick inside based on visible queue crowding and signal quality
- `TradervR1_108.py`
  - catalyst detector
  - only wake up when tight-book microprice, imbalance, and stable-book structure line up as a real short-horizon event
- `TradervR1_109.py`
  - combined queue-priority + catalyst branch

Local replay:
- `TradervR1_97.py`: `97'914.0 / 98'906.0 / 97'953.0`
- `TradervR1_107.py`: `95'432.0 / 96'353.0 / 95'298.0`
- `TradervR1_108.py`: `97'914.0 / 98'906.0 / 97'953.0`
- `TradervR1_109.py`: `95'432.0 / 96'353.0 / 95'298.0`

Three-day totals:
- `TradervR1_97.py`: `294'773.0`
- `TradervR1_107.py`: `287'083.0`
- `TradervR1_108.py`: `294'773.0`
- `TradervR1_109.py`: `287'083.0`

Product split:
- `TradervR1_97.py`
  - `ASH_COATED_OSMIUM`: `56'364.0`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_107.py`
  - `ASH_COATED_OSMIUM`: `48'674.0`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_108.py`
  - `ASH_COATED_OSMIUM`: `56'364.0`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_109.py`
  - `ASH_COATED_OSMIUM`: `48'674.0`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`

Read:
- the queue-priority model did change realized behavior, but clearly for the worse
- it reduced Osmium trades and gave up spread capture on all three days
- the catalyst detector, as implemented here, was completely inert
- the combined branch collapsed exactly to the queue-priority result, which means the catalyst layer did not add any extra fill boundary on top

Conclusion:
- a naive visible-queue heuristic is too blunt for this product
- a “genuine catalyst” layer is still plausible, but the first version here was not strong or discrete enough to matter
- the best current trunk remains `TradervR1_97.py`

### `TradervR1_110.py`

No-fill reactivation branch on top of `TradervR1_97.py`:
- track `ash_no_fill_ticks` from `state.own_trades`
- after `8+` quiet ticks in normal, non-stretched, non-vacuum states with toxicity at most level `1`:
  - tighten the signal-side quote edge by `0.15 + extra`
  - slightly lift signal-side front size
- also decay smoothed toxicity faster after quiet non-toxic stretches

Local replay:
- `TradervR1_97.py`: `97'914.0 / 98'906.0 / 97'953.0`
- `TradervR1_110.py`: `97'957.0 / 98'906.0 / 97'953.0`

Three-day totals:
- `TradervR1_97.py`: `294'773.0`
- `TradervR1_110.py`: `294'816.0`

Product split:
- `TradervR1_97.py`
  - `ASH_COATED_OSMIUM`: `56'364.0`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_110.py`
  - `ASH_COATED_OSMIUM`: `56'407.0`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`

Read:
- small but real improvement: `+43.0`
- entirely Osmium-led
- Pepper stayed unchanged
- only day `-2` moved, but it did so with slightly more Ash trades rather than a broad aggression jump

Conclusion:
- low-risk re-entry after quiet periods looks more promising than plateau taker pulses
- this is still a small local edge, not a breakthrough
- but it is the first plateau-style refinement in this area that actually improved the trunk

### `TradervR1_111.py`

Smarter silent-period re-entry on top of `TradervR1_110.py`:
- keep `ash_no_fill_ticks`
- add signal persistence tracking:
  - signal-side direction
  - short EMA of quote signal
  - consecutive same-direction ticks
- only reactivate when the same favored side has persisted for several ticks
- then let that side join a little closer and scale front size by persistence strength

Local replay:
- `TradervR1_110.py`: `97'957.0 / 98'906.0 / 97'953.0`
- `TradervR1_111.py`: `97'957.0 / 98'906.0 / 97'953.0`

Three-day totals:
- `TradervR1_110.py`: `294'816.0`
- `TradervR1_111.py`: `294'816.0`

Read:
- completely identical to `v110`
- same Osmium PnL
- same Pepper PnL
- same trade count

Conclusion:
- adding persistence-based re-entry logic did not cross a new fill boundary on top of `v110`
- the simpler no-fill reactivation branch remains just as good

### Plateau Influence Sweep from `TradervR1_110.py`

I tested three more discrete ways to try to break the silent Ash plateaus:

- `TradervR1_112.py`
  - concentrated single-front presence
  - during silent reactivation, drop the same-side back quote and concentrate more size at the front
- `TradervR1_113.py`
  - asymmetric silent leaning
  - during silent reactivation, tighten the favored side and widen the opposite side a bit more explicitly
- `TradervR1_114.py`
  - micro-catalyst nibble
  - after a longer quiet period, if the signal is strong, toxicity is zero, spread is tight, and inventory is flat-ish, cross tiny size (`2`) on the favored side before resuming passive quoting

Local replay:
- `TradervR1_110.py`: `97'957.0 / 98'906.0 / 97'953.0`
- `TradervR1_112.py`: `97'957.0 / 98'906.0 / 97'953.0`
- `TradervR1_113.py`: `97'957.0 / 98'906.0 / 97'953.0`
- `TradervR1_114.py`: `97'999.5 / 98'939.0 / 97'937.0`

Three-day totals:
- `TradervR1_110.py`: `294'816.0`
- `TradervR1_112.py`: `294'816.0`
- `TradervR1_113.py`: `294'816.0`
- `TradervR1_114.py`: `294'875.5`

Product split:
- `TradervR1_110.py`
  - `ASH_COATED_OSMIUM`: `56'407.0`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_114.py`
  - `ASH_COATED_OSMIUM`: `56'466.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`

Read:
- the passive “shape the book” plateau ideas were completely inert
- a tiny, highly selective catalyst nibble was the only thing that actually moved the boundary
- the gain is small but real: `+59.5` vs `v110`
- all of it is Osmium
- trade count rose from `2209` to `2368`, so the bot is doing more work, but in a much narrower and more controlled way than the earlier bad taker pulses

Conclusion:
- the promising plateau strategy is not broader passive presence
- it is a very selective make/take hybrid only after quiet periods, in tight non-toxic books, with strong same-side signal
- `TradervR1_114.py` is the new best branch from this plateau-influence family

### `TradervR1_115.py`

Inventory-layer / reserve-age / plateau-harvest experiment on top of `TradervR1_114.py`:
- split Ash inventory into:
  - neutral
  - working
  - reserve
  - danger
- only keep building reserve inventory when the side still looks feasible relative to local fair
- track reserve age
- switch quiet working/reserve inventory into a passive harvest mode during plateaus

Local replay:
- `TradervR1_114.py`: `97'999.5 / 98'939.0 / 97'937.0`
- `TradervR1_115.py`: `95'974.5 / 96'516.0 / 95'244.0`

Three-day totals:
- `TradervR1_114.py`: `294'875.5`
- `TradervR1_115.py`: `287'734.5`

Product split:
- `TradervR1_114.py`
  - `ASH_COATED_OSMIUM`: `56'466.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_115.py`
  - `ASH_COATED_OSMIUM`: `49'325.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`

Read:
- the whole giveback is Osmium
- trade count fell from `2368` to `2118`
- the layered inventory controller became too restrictive and shut down too much normal Ash monetization

Conclusion:
- the idea is directionally interesting
- but in this first full form it is too heavy for the current branch
- the better live edge is still the lighter `TradervR1_114.py` approach:
  a narrow catalyst nibble after silence, not a broad inventory-management overlay

### `TradervR1_116.py`

Bar-corrected plateau re-entry rewrite on top of `TradervR1_114.py`:
- convert silent re-entry timing from raw timestamp delta into actual bar count
- make re-entry move the real front quote, not just the theoretical edge
- add a neutral two-sided drip-maker when the book is tradable but `quote_signal` is near zero
- relax join behavior slightly during quiet reactivation
- allow a small re-entry boost shortly after vacuum recovery instead of blocking it entirely

Local replay:
- `TradervR1_114.py`: `97'999.5 / 98'939.0 / 97'937.0`
- `TradervR1_116.py`: `98'009.5 / 98'903.0 / 97'877.0`

Three-day totals:
- `TradervR1_114.py`: `294'875.5`
- `TradervR1_110.py`: `294'816.0`
- `TradervR1_116.py`: `294'789.5`

Product split:
- `TradervR1_116.py`
  - `ASH_COATED_OSMIUM`: `56'380.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`

Read:
- the fixes were real and did change behavior
- day `-2` improved slightly, but day `0` gave back more than that gain
- all movement was in Osmium; Pepper stayed unchanged
- versus the current plateau trunk, this is:
  - `-86.0` vs `TradervR1_114.py`
  - `-26.5` vs `TradervR1_110.py`

Conclusion:
- the diagnosis was directionally right:
  - raw timestamps were the wrong unit
  - the old re-entry often changed intent more than posted price
- but the stronger bar-corrected re-entry still did not beat the simpler catalyst-nibble branch
- `TradervR1_114.py` remains the better plateau-focused trunk for now

### Split Re-entry Sweep from `TradervR1_114.py`

I split the stronger re-entry idea into isolated branches so the silence handling would not interfere across unrelated quiet regimes:

- `TradervR1_117_1.py`
  - timer / bar-count fix only
  - keep the `v114` logic shape, but convert the re-entry and toxicity-release timing into actual bars
- `TradervR1_117_2.py`
  - side-specific stale-side re-entry
  - track buy-side and sell-side silence separately
  - only reactivate the side that has actually gone stale
- `TradervR1_117_3.py`
  - quiet-book toxicity release only
  - separate quiet non-toxic decay from fill silence without changing the re-entry logic

Local replay:
- `TradervR1_114.py`: `97'999.5 / 98'939.0 / 97'937.0`
- `TradervR1_117_1.py`: `98'009.5 / 98'899.0 / 97'885.0`
- `TradervR1_117_2.py`: `98'009.5 / 98'908.0 / 97'941.0`
- `TradervR1_117_3.py`: `97'975.0 / 98'930.0 / 97'949.0`

Three-day totals:
- `TradervR1_114.py`: `294'875.5`
- `TradervR1_117_1.py`: `294'793.5`
- `TradervR1_117_2.py`: `294'858.5`
- `TradervR1_117_3.py`: `294'854.0`

Product split:
- `TradervR1_117_1.py`
  - `ASH_COATED_OSMIUM`: `56'384.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_117_2.py`
  - `ASH_COATED_OSMIUM`: `56'449.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_117_3.py`
  - `ASH_COATED_OSMIUM`: `56'445.0`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`

Read:
- splitting the idea helped compared with the heavier `TradervR1_116.py` rewrite
- the best slice is `TradervR1_117_2.py`, the side-specific stale-side re-entry branch
- that means the promising part of the re-entry idea is:
  - wake up only the side that actually went stale
  - do not let generic silence handling spill into all quiet states
- the timer fix alone was not enough
- the separate quiet-book toxicity release also helped, but slightly less than side-specific stale-side handling

Conclusion:
- the good direction is narrower, side-specific silence handling
- the re-entry idea becomes stronger when it stops treating all quiet periods as the same
- `TradervR1_114.py` is still the best overall plateau trunk right now, but `TradervR1_117_2.py` is the best donor branch from this split experiment

### `TradervR1_118.py`

Surgical hybrid:
- keep `TradervR1_114.py` as the plateau trunk
- keep the `v114` micro-catalyst nibble exactly as-is
- import only the side-specific stale-side wake-up from `TradervR1_117_2.py`

Local replay:
- `TradervR1_114.py`: `97'999.5 / 98'939.0 / 97'937.0`
- `TradervR1_118.py`: `97'999.5 / 98'939.0 / 97'937.0`

Three-day totals:
- `TradervR1_114.py`: `294'875.5`
- `TradervR1_118.py`: `294'875.5`

Product split:
- `TradervR1_118.py`
  - `ASH_COATED_OSMIUM`: `56'466.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`

Read:
- the hybrid is completely identical to `v114` in local replay
- same total PnL
- same Ash PnL
- same Pepper PnL
- same trade count

Conclusion:
- the side-specific stale-side wake-up is directionally compatible with the `v114` trunk
- but in this exact merged form it does not cross a new fill boundary
- `TradervR1_114.py` remains the active plateau trunk

### Pepper Push Sweep from `TradervR1_118.py`

I tried three small Pepper-only variants to see whether we could push the current `INTARIAN_PEPPER_ROOT` split higher without disturbing the Osmium trunk:

- `TradervR1_119_1.py`
  - more patient Pepper taking
  - slightly lower lookahead
  - stronger cheap-accum take penalty
  - slightly stronger cheap-accum quote bonus
- `TradervR1_119_2.py`
  - passive-first early accumulation
  - early Pepper buys stay passive unless the book looks clearly cheap
- `TradervR1_119_3.py`
  - lighter chase / entry-quality version
  - slightly lower lookahead, lower early-long bias, lower edge-target scale
  - modestly more patient cheap accumulation

Local replay:
- `TradervR1_118.py`: `97'999.5 / 98'939.0 / 97'937.0`
- `TradervR1_119_1.py`: `97'982.5 / 98'935.0 / 97'932.0`
- `TradervR1_119_2.py`: `97'957.5 / 98'905.0 / 97'881.0`
- `TradervR1_119_3.py`: `97'984.5 / 98'942.0 / 97'934.0`

Three-day totals:
- `TradervR1_118.py`: `294'875.5`
- `TradervR1_119_1.py`: `294'849.5`
- `TradervR1_119_2.py`: `294'743.5`
- `TradervR1_119_3.py`: `294'860.5`

Product split:
- `TradervR1_118.py`
  - `ASH_COATED_OSMIUM`: `56'466.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_119_1.py`
  - `ASH_COATED_OSMIUM`: `56'466.5`
  - `INTARIAN_PEPPER_ROOT`: `238'383.0`
- `TradervR1_119_2.py`
  - `ASH_COATED_OSMIUM`: `56'466.5`
  - `INTARIAN_PEPPER_ROOT`: `238'277.0`
- `TradervR1_119_3.py`
  - `ASH_COATED_OSMIUM`: `56'466.5`
  - `INTARIAN_PEPPER_ROOT`: `238'394.0`

Read:
- all of the movement was in Pepper; Osmium stayed exactly unchanged
- none of the tested Pepper nudges improved the trunk
- the least-bad version was `TradervR1_119_3.py`, but it still gave back `-15.0`
- the current Pepper engine still sits at the same local `238'409.0` line

Conclusion:
- this particular “be a bit more patient on Pepper entry” family does not unlock a better split
- if there is still extra Pepper edge left, it is probably not in broad parameter nudges around cheap accumulation
- `TradervR1_118.py` / `TradervR1_114.py` remain the better trunks

### Pepper Entry-Structure Sweep from `TradervR1_118.py`

I tried three more genuinely different Pepper entry structures while keeping Osmium untouched:

- `TradervR1_119_1.py`
  - patient-taker Pepper
  - smaller lookahead, stricter early taking, slightly stronger passive cheap accumulation
- `TradervR1_119_2.py`
  - passive-first early accumulation
  - in the early session, Pepper only crosses when the book looks clearly cheap; otherwise it waits to accumulate passively
- `TradervR1_119_3.py`
  - lighter-chase entry-quality Pepper
  - lower lookahead, lower early-long bias, lower edge-target scale, and slightly more patient cheap accumulation

Local replay:
- `TradervR1_118.py`: `97'999.5 / 98'939.0 / 97'937.0`
- `TradervR1_119_1.py`: `97'982.5 / 98'935.0 / 97'932.0`
- `TradervR1_119_2.py`: `97'957.5 / 98'905.0 / 97'881.0`
- `TradervR1_119_3.py`: `97'984.5 / 98'942.0 / 97'934.0`

Three-day totals:
- `TradervR1_118.py`: `294'875.5`
- `TradervR1_119_1.py`: `294'849.5`
- `TradervR1_119_2.py`: `294'743.5`
- `TradervR1_119_3.py`: `294'860.5`

Product split:
- `TradervR1_118.py`
  - `ASH_COATED_OSMIUM`: `56'466.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_119_1.py`
  - `ASH_COATED_OSMIUM`: `56'466.5`
  - `INTARIAN_PEPPER_ROOT`: `238'383.0`
- `TradervR1_119_2.py`
  - `ASH_COATED_OSMIUM`: `56'466.5`
  - `INTARIAN_PEPPER_ROOT`: `238'277.0`
- `TradervR1_119_3.py`
  - `ASH_COATED_OSMIUM`: `56'466.5`
  - `INTARIAN_PEPPER_ROOT`: `238'394.0`

Read:
- all three variants changed only Pepper
- Osmium stayed exactly unchanged in every case
- none of the entry-structure variants improved the current Pepper line
- the least-bad version was `TradervR1_119_3.py`, but it still gave back `-15.0`

Conclusion:
- Pepper is still very saturated on this structure
- there does not appear to be an easy gain left from small early-entry reshaping around the current engine
- if we revisit Pepper, it likely needs a meaningfully different structural entry family, not another local modification of cheap accumulation

### Osmium Lever Sweep from `TradervR1_118.py`

I cleaned the active `TradervR1_118.py` trunk by removing stale Osmium parameters from the old calm/dislocation regime work:

- removed unused `CALM_DEPTH_MIN`
- removed unused `CALM_SPREAD_MAX`
- removed unused `CALM_IMBALANCE_MAX`
- removed unused `DISLOCATION_EDGE`

That cleanup was clarity-only. Then I tested the five candidate Ash levers separately:

- `TradervR1_120_1.py`
  - markout-aware net edge
  - adds side-specific markout memory and uses effective edge after expected markout
- `TradervR1_120_2.py`
  - true multi-level sweep
  - in high-conviction states, take through levels 1-3 while edge stays positive after inventory re-evaluation
- `TradervR1_120_3.py`
  - side-specific re-entry only
  - removes the broad global no-fill gate and reactivates only the starved side when its signal is favorable
- `TradervR1_120_4.py`
  - stronger conviction regime
  - when all signals line up, conviction becomes a real throughput regime with tighter favored-side quoting, more join, and larger front size
- `TradervR1_120_5.py`
  - low-conviction inventory recycler
  - starts flattening moderately stretched inventory earlier when conviction is weak

Local replay:
- `TradervR1_118.py`: `97'999.5 / 98'939.0 / 97'937.0`
- `TradervR1_120_1.py`: `97'987.5 / 98'947.0 / 97'911.0`
- `TradervR1_120_2.py`: `97'998.5 / 98'939.0 / 97'937.0`
- `TradervR1_120_3.py`: `97'968.5 / 98'934.0 / 98'008.0`
- `TradervR1_120_4.py`: `97'988.5 / 98'931.0 / 97'923.0`
- `TradervR1_120_5.py`: `97'992.5 / 98'886.0 / 97'930.0`

Three-day totals:
- `TradervR1_118.py`: `294'875.5`
- `TradervR1_120_1.py`: `294'845.5`
- `TradervR1_120_2.py`: `294'874.5`
- `TradervR1_120_3.py`: `294'910.5`
- `TradervR1_120_4.py`: `294'842.5`
- `TradervR1_120_5.py`: `294'808.5`

Product split:
- `TradervR1_118.py`
  - `ASH_COATED_OSMIUM`: `56'466.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_120_1.py`
  - `ASH_COATED_OSMIUM`: `56'436.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_120_2.py`
  - `ASH_COATED_OSMIUM`: `56'465.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_120_3.py`
  - `ASH_COATED_OSMIUM`: `56'501.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_120_4.py`
  - `ASH_COATED_OSMIUM`: `56'433.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_120_5.py`
  - `ASH_COATED_OSMIUM`: `56'399.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`

Trade counts:
- `TradervR1_118.py`: `2368`
- `TradervR1_120_1.py`: `2365`
- `TradervR1_120_2.py`: `2368`
- `TradervR1_120_3.py`: `2850`
- `TradervR1_120_4.py`: `2374`
- `TradervR1_120_5.py`: `2378`

Read:
- the only clear new live lever here is `TradervR1_120_3.py`
- pure side-specific re-entry improved Ash by `+35.0` total without touching Pepper
- multi-level sweep was effectively inert in this first form
- markout-aware net edge, stronger conviction regime, and the early recycler all made the trunk worse

Conclusion:
- the best next lever from this sweep is not broader aggression; it is cleaner side-specific re-entry
- the current best test from this family is `TradervR1_120_3.py`
- if we keep pushing, `TradervR1_120_3.py` is the right donor branch for a promoted next version

### Combination Sweep of The Five Osmium Levers

I generated and tested every combination of the five isolated Ash levers from the `TradervR1_120_*` family:

- `1`: markout-aware net edge
- `2`: multi-level high-conviction sweep
- `3`: side-specific re-entry
- `4`: stronger conviction regime
- `5`: low-conviction inventory recycler

References:
- `TradervR1_118.py`: `294'875.5`
- `TradervR1_120_3.py`: `294'910.5`

Important constant:
- every combination left Pepper unchanged at `238'409.0`
- all movement in this sweep was purely `ASH_COATED_OSMIUM`

Two-way combinations:
- `TradervR1_121_13.py`: `294'913.5`
- `TradervR1_121_23.py`: `294'890.5`
- `TradervR1_121_34.py`: `294'878.0`
- `TradervR1_121_24.py`: `294'864.5`
- `TradervR1_121_12.py`: `294'844.5`
- `TradervR1_121_14.py`: `294'818.5`
- `TradervR1_121_25.py`: `294'808.5`
- `TradervR1_121_45.py`: `294'771.5`
- `TradervR1_121_15.py`: `294'762.5`
- `TradervR1_121_35.py`: `294'743.5`

Three-way combinations:
- `TradervR1_121_134.py`: `294'909.5`
- `TradervR1_121_123.py`: `294'905.5`
- `TradervR1_121_234.py`: `294'842.0`
- `TradervR1_121_124.py`: `294'840.5`
- `TradervR1_121_245.py`: `294'793.5`
- `TradervR1_121_135.py`: `294'771.5`
- `TradervR1_121_1235.py`: `294'763.5`
- `TradervR1_121_125.py`: `294'762.5`
- `TradervR1_121_345.py`: `294'738.5`
- `TradervR1_121_235.py`: `294'723.5`

Four-way combinations:
- `TradervR1_121_1234.py`: `294'861.5`
- `TradervR1_121_1235.py`: `294'763.5`
- `TradervR1_121_1345.py`: `294'790.5`
- `TradervR1_121_1245.py`: `294'753.5`
- `TradervR1_121_2345.py`: `294'690.5`

Five-way combination:
- `TradervR1_121_12345.py`: `294'742.5`

Best performers:
- `TradervR1_121_13.py`: `294'913.5`
- `TradervR1_120_3.py`: `294'910.5`
- `TradervR1_121_134.py`: `294'909.5`
- `TradervR1_121_123.py`: `294'905.5`

Read:
- the clean winner is `TradervR1_121_13.py`, which combines:
  - markout-aware net edge
  - side-specific re-entry
- that beat `TradervR1_120_3.py` by `+3.0`
- and beat the `TradervR1_118.py` trunk by `+38.0`
- the side-specific re-entry lever is still the main driver
- markout becomes slightly useful only when paired with that re-entry lever
- the stronger conviction regime can help a little when stacked on top of `1+3`, but not enough to beat `1+3`
- the multi-level sweep remains mostly inert
- the low-conviction recycler is the most consistently harmful lever in combined form

Trade count pattern:
- `TradervR1_118.py`: `2368`
- `TradervR1_120_3.py`: `2850`
- `TradervR1_121_13.py`: `2848`
- `TradervR1_121_134.py`: `2862`

Conclusion:
- the best merge from the full subset sweep is `TradervR1_121_13.py`
- the current live donor stack is:
  - side-specific re-entry
  - plus a light markout-aware net-edge memory
- if we promote one next mainline from this matrix, `TradervR1_121_13.py` is the right candidate

### Focused Optimization Sweep from `TradervR1_121_13.py`

I ran a tight local optimization pass around the only two live levers in `TradervR1_121_13.py`:

- side-specific re-entry
- markout-aware net edge

Tested variants:
- `TradervR1_122_1.py`
  - softer markout memory plus slightly stronger re-entry
- `TradervR1_122_2.py`
  - firmer / harsher markout protection
- `TradervR1_122_3.py`
  - stronger re-entry only
- `TradervR1_122_4.py`
  - later / cleaner re-entry only
- `TradervR1_122_5.py`
  - softer markout only
- `TradervR1_122_6.py`
  - middle-ground blended markout + re-entry

Local replay:
- `TradervR1_121_13.py`: `97'973.5 / 98'932.0 / 98'008.0`
- `TradervR1_122_1.py`: `97'968.5 / 98'934.0 / 98'008.0`
- `TradervR1_122_2.py`: `97'973.5 / 98'890.0 / 97'958.0`
- `TradervR1_122_3.py`: `97'973.5 / 98'932.0 / 98'008.0`
- `TradervR1_122_4.py`: `97'961.5 / 98'901.0 / 97'976.0`
- `TradervR1_122_5.py`: `97'968.5 / 98'934.0 / 98'008.0`
- `TradervR1_122_6.py`: `97'973.5 / 98'932.0 / 98'008.0`

Three-day totals:
- `TradervR1_121_13.py`: `294'913.5`
- `TradervR1_122_1.py`: `294'910.5`
- `TradervR1_122_2.py`: `294'821.5`
- `TradervR1_122_3.py`: `294'913.5`
- `TradervR1_122_4.py`: `294'838.5`
- `TradervR1_122_5.py`: `294'910.5`
- `TradervR1_122_6.py`: `294'913.5`

Product split:
- `TradervR1_121_13.py`
  - `ASH_COATED_OSMIUM`: `56'504.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_122_1.py`
  - `ASH_COATED_OSMIUM`: `56'501.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_122_2.py`
  - `ASH_COATED_OSMIUM`: `56'412.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_122_3.py`
  - `ASH_COATED_OSMIUM`: `56'504.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_122_4.py`
  - `ASH_COATED_OSMIUM`: `56'429.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_122_5.py`
  - `ASH_COATED_OSMIUM`: `56'501.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_122_6.py`
  - `ASH_COATED_OSMIUM`: `56'504.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`

Read:
- no focused local variant beat `TradervR1_121_13.py`
- `TradervR1_122_3.py` and `TradervR1_122_6.py` were completely identical to the trunk
- softer markout variants (`122_1`, `122_5`) were very slightly worse
- harsher markout (`122_2`) clearly hurt
- later / cleaner re-entry (`122_4`) also hurt

Conclusion:
- the current `TradervR1_121_13.py` branch is locally saturated under small parameter nudges
- the next gain probably will not come from another tiny markout/re-entry retune
- if we keep pushing, we likely need a new structural Osmium lever rather than a local optimization of this pair

### Larger-Fill Sweep from `TradervR1_121_13.py`

I tested whether simply making Ash fill more size would improve the current best branch:

- `TradervR1_123_1.py`
  - larger passive sizes only
  - `FRONT_SIZE 16 -> 18`
  - `BACK_SIZE 5 -> 6`
- `TradervR1_123_2.py`
  - larger take clips only
  - `TAKE_L1_SIZE 4 -> 5`
  - `TAKE_L2_SIZE 8 -> 10`
  - `TAKE_L3_SIZE 14 -> 18`
- `TradervR1_123_3.py`
  - larger size only in high-conviction states
  - adds front/back size only on the favored side when conviction is high and toxicity is low
- `TradervR1_123_4.py`
  - larger size only during side-specific re-entry
  - micro-nibbles and reactivation front size were both increased

Local replay:
- `TradervR1_121_13.py`: `97'973.5 / 98'932.0 / 98'008.0`
- `TradervR1_123_1.py`: `97'973.5 / 98'932.0 / 98'008.0`
- `TradervR1_123_2.py`: `97'978.0 / 98'939.0 / 97'926.0`
- `TradervR1_123_3.py`: `97'973.5 / 98'932.0 / 98'008.0`
- `TradervR1_123_4.py`: `97'882.0 / 98'901.0 / 97'945.0`

Three-day totals:
- `TradervR1_121_13.py`: `294'913.5`
- `TradervR1_123_1.py`: `294'913.5`
- `TradervR1_123_2.py`: `294'843.0`
- `TradervR1_123_3.py`: `294'913.5`
- `TradervR1_123_4.py`: `294'728.0`

Product split:
- `TradervR1_121_13.py`
  - `ASH_COATED_OSMIUM`: `56'504.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_123_1.py`
  - `ASH_COATED_OSMIUM`: `56'504.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_123_2.py`
  - `ASH_COATED_OSMIUM`: `56'434.0`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_123_3.py`
  - `ASH_COATED_OSMIUM`: `56'504.5`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`
- `TradervR1_123_4.py`
  - `ASH_COATED_OSMIUM`: `56'319.0`
  - `INTARIAN_PEPPER_ROOT`: `238'409.0`

Read:
- larger passive sizes were completely inert
- larger high-conviction passive sizes were also completely inert
- larger take clips made the bot worse
- larger re-entry / micro-nibble size was clearly worse

Conclusion:
- simply asking Ash to trade more size is not enough
- the current best branch appears pinned at the same execution boundary for passive size
- when size changes do matter, they currently hurt rather than help
- the next gain is more likely to come from a different execution decision, not a larger order size by itself

### CMA-ES on `TradervR1_121_13.py`

I ran a focused CMA-ES pass on the current best bot using:
- [tradervr1_121_13_cmaes.json](TraderFactory/configs/round1/tradervr1_121_13_cmaes.json)
- search space:
  - `BASE_EDGE`
  - `JOIN_EDGE`
  - `MIN_QUOTE_EDGE`
  - `TAKE_L1_EDGE`
  - `TAKE_L2_EDGE`
  - `MARKOUT_ALPHA`
  - `SOFT_BAD_MARKOUT`
  - `HARD_BAD_MARKOUT`
  - `MARKOUT_EDGE_PENALTY`
  - `MARKOUT_SIZE_PENALTY`

Artifacts:
- best bot: [TradervR1_121_13_best.py](Analysis/output/round1_tradervr1_121_13_cmaes/bots/TradervR1_121_13_best.py)
- report: [round1_tradervr1_121_13_cmaes_report.md](Analysis/output/round1_tradervr1_121_13_cmaes/round1_tradervr1_121_13_cmaes_report.md)

Result:
- baseline replay: `97'973.5 / 98'932.0 / 98'008.0`
- best candidate replay: `97'973.5 / 98'932.0 / 98'008.0`
- best objective: `98'304.5`
- total evaluations: `19`

Read:
- CMA-ES did not find a robust improvement over `TradervR1_121_13.py`
- the winning artifact is effectively the same bot; the only textual diff is float formatting (`-0.90 -> -0.9`)
- generation history showed tiny raw-average bumps inside the search, but they were not good enough under the regularized objective

Conclusion:
- the exposed `121_13` parameter surface looks locally saturated for this objective
- if we want CMA-ES to matter on this branch, we probably need to expose the side-specific re-entry constants rather than only the existing dict parameters

### CMA-ES on `TradervR1_110.py`

I also ran a broader CMA-ES pass on the older `TradervR1_110.py` branch using:
- [tradervr1_110_cmaes.json](TraderFactory/configs/round1/tradervr1_110_cmaes.json)
- search space:
  - `ANCHOR_WEIGHT`
  - `STABLE_MID_WEIGHT`
  - `WALL_MID_BLEND`
  - `LOCAL_MICRO_WEIGHT`
  - `DEPTH_IMPACT_SCALE`
  - `BASE_EDGE`
  - `JOIN_EDGE`
  - `MIN_QUOTE_EDGE`
  - `TAKE_L1_EDGE`
  - `TAKE_L2_EDGE`
  - `FAST_TAKE_WEIGHT`
  - `FAST_QUOTE_WEIGHT`

Artifacts:
- best bot: [TradervR1_110_best.py](Analysis/output/round1_tradervr1_110_cmaes/bots/TradervR1_110_best.py)
- report: [round1_tradervr1_110_cmaes_report.md](Analysis/output/round1_tradervr1_110_cmaes/round1_tradervr1_110_cmaes_report.md)

Result:
- baseline replay: `97'957.0 / 98'906.0 / 97'953.0`
- best candidate replay: `97'957.0 / 98'906.0 / 97'953.0`
- best objective: `98'272.0`
- total evaluations: `19`

Read:
- CMA-ES also failed to improve `TradervR1_110.py`
- unlike `121_13`, the broader `110` search mostly wandered into bad regions; generation-best candidates had much worse averages and were heavily penalized
- the winning artifact again collapsed back to the source defaults, with only cosmetic float-format diffs

Conclusion:
- `TradervR1_110.py` has a broader but much less stable parameter surface
- CMA-ES on the old exposed knobs is not a shortcut to catching up with the newer branch

### `TradervR1_121_*` Targeted Fix Branches

I tested three clean corrective branches off `TradervR1_121_13.py`:

- [TradervR1_121_fixDecay.py](Bots/Round1/TradervR1_121_fixDecay.py)
  - changes `quiet_non_toxic_ticks` to use a bar-based measure (`no_fill_ticks // 100`) instead of raw timestamp distance
  - same intent as the old `bars_since_fill` correction, but isolated to toxicity decay only
- [TradervR1_121_fixReentryExecution.py](Bots/Round1/TradervR1_121_fixReentryExecution.py)
  - keeps side-specific `bars_since_buy_fill` / `bars_since_sell_fill`
  - restores the `v116`-style execution fix:
    - wider `join_edge` during reactivation
    - front quote pushed toward the book on the reactivating side
- [TradervR1_121_markoutPassiveOnly.py](Bots/Round1/TradervR1_121_markoutPassiveOnly.py)
  - removes markout from aggressive take gating
  - keeps markout only in passive quote edge and passive quote size penalties

Local replay:
- `TradervR1_121_13.py`: `97'973.5 / 98'932.0 / 98'008.0`
- `TradervR1_121_fixDecay.py`: `97'973.5 / 98'932.0 / 98'008.0`
- `TradervR1_121_fixReentryExecution.py`: `97'973.5 / 98'932.0 / 98'008.0`
- `TradervR1_121_markoutPassiveOnly.py`: `97'968.5 / 98'934.0 / 98'008.0`

Three-day totals:
- `TradervR1_121_13.py`: `294'913.5`
- `TradervR1_121_fixDecay.py`: `294'913.5`
- `TradervR1_121_fixReentryExecution.py`: `294'913.5`
- `TradervR1_121_markoutPassiveOnly.py`: `294'910.5`

Read:
- the decay correction is clean but locally inert
- the re-entry execution correction is also clean but locally inert
- de-overlapping markout changed behavior, but only slightly and in the wrong direction overall (`-3.0`)

Conclusion:
- these three branches improve code clarity and isolate real levers, which is useful
- but none of them opens a new local edge over `TradervR1_121_13.py`
- the most interesting one structurally is still `TradervR1_121_markoutPassiveOnly.py`, because it is the only branch that changed realized behavior at all
