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
