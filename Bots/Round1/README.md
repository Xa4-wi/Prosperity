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
