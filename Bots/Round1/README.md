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
