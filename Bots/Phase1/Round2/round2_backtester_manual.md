# Round 2 backtester manual
## Supports public CSVs, run JSON files, and raw submission logs

## 1. Goal

Build a backtester that can do four jobs:

1. replay the public market exactly enough to test baseline strategy changes
2. ingest your own previous runs (`.json` and `.log`) as additional evidence
3. simulate **no-access** versus **access** regimes for Round 2
4. produce diagnostics that explain *why* a branch works or fails

This manual is intentionally structured so an agent can keep feeding in:
- more run JSON files
- more raw logs
- more price/trade CSVs
without changing the architecture.

---

## 2. Supported input schemas

## 2.1 Public price CSV schema

Files:
- `prices_round_1_day_*.csv`
- `prices_round_2_day_*.csv`

Observed format:
- semicolon-separated
- columns:

```text
day
timestamp
product
bid_price_1
bid_volume_1
bid_price_2
bid_volume_2
bid_price_3
bid_volume_3
ask_price_1
ask_volume_1
ask_price_2
ask_volume_2
ask_price_3
ask_volume_3
mid_price
profit_and_loss
```

Notes:
- rows are mixed across products
- missing levels are `NaN`
- in round 2 public files, there are `20000` rows per day

## 2.2 Public trade CSV schema

Files:
- `trades_round_1_day_*.csv`
- `trades_round_2_day_*.csv`

Observed format:
- semicolon-separated
- columns:

```text
timestamp
buyer
seller
symbol
currency
price
quantity
```

Notes:
- buyer and seller can be empty / NaN in public files
- these are market trades, not necessarily your fills

## 2.3 Run JSON schema

Observed fields in uploaded run JSONs:

```text
round: str
status: str
profit: float
activitiesLog: str
graphLog: str
positions: list[dict]
```

Practical parser behavior:
- `activitiesLog` -> parse as semicolon-separated CSV string
- `graphLog` -> parse as semicolon-separated `timestamp,value` curve
- `positions` -> normalize into `dict[symbol] -> quantity`

## 2.4 Raw `.log` schema

Observed fields in uploaded `.log` files:

```text
submissionId: str
activitiesLog: str
logs: list[dict]
tradeHistory: list[dict]
```

With:
```text
logs[i] = {
  "sandboxLog": str,
  "lambdaLog": str,
  "timestamp": int
}
```

and:
```text
tradeHistory[j] = {
  "timestamp": int,
  "buyer": str,
  "seller": str,
  "symbol": str,
  "currency": str,
  "price": float,
  "quantity": int
}
```

Practical parser behavior:
- parse same as JSON for `activitiesLog`
- parse `tradeHistory` into a normalized executions table
- use `logs` as optional diagnostics keyed by timestamp

---

## 3. Normalized internal data model

After ingestion, normalize all sources into these internal tables.

## 3.1 MarketState table
Key:
- `(round, day, timestamp, product)`

Fields:
- top 3 bids and asks
- visible mid
- spread
- visible top depth
- derived microprice
- derived imbalance
- any custom features

## 3.2 MarketTrades table
Key:
- `(round, day, timestamp, symbol, trade_index)`

Fields:
- buyer
- seller
- price
- quantity

## 3.3 RunSummary table
Key:
- `run_id`

Fields:
- source file name
- round
- total profit
- final positions
- graph curve
- notes

## 3.4 RunExecutions table
Key:
- `(run_id, timestamp, trade_index)`

Fields:
- symbol
- side (infer from buyer/seller where possible)
- price
- quantity

## 3.5 RunSnapshots table
Key:
- `(run_id, timestamp, product)`

Fields:
- market snapshot from `activitiesLog`
- per-product PnL at that time
- optional link to internal logs

---

## 4. Loader architecture

Implement one public entry point:

```python
load_any(path) -> ParsedArtifact
```

Behavior:
- if suffix is `.csv`:
  - detect price vs trade schema by column names
- if suffix is `.json`:
  - detect run summary format
- if suffix is `.log`:
  - parse as raw submission output JSON
- return a typed artifact

Recommended modules:
- `io/load_csv.py`
- `io/load_run_json.py`
- `io/load_submission_log.py`
- `io/normalize.py`

---

## 5. Replay engine structure

## 5.1 Event loop
At each timestamp:
1. build `TradingState`
2. load visible order depth for each product
3. attach market trades for that timestamp
4. pass `traderData` memory from previous timestamp
5. call `Trader.run(state)`
6. process aggressive executions
7. process passive quote fills
8. update position, cash, PnL, logs, and `traderData`
9. move to next timestamp

For Round 2:
- `Trader.bid()` should be stored but not injected into dynamics
- bidding should be handled in a separate post-processing layer

## 5.2 Matching engine
Support:
- immediate fills against visible top levels
- partial fills
- multi-level sweeping if the order crosses several visible levels
- persistent passive orders between timestamps unless canceled or replaced

Minimum acceptable approximation:
- aggressive orders consume visible book in price-time order
- passive orders fill when:
  - the market trades through your quote
  - or the visible opposite touch crosses your quote
  - or a queue-proxy model says your resting order got hit

## 5.3 Queue model
Start simple but explicit.

Recommended versions:
- `queue_model = conservative`
  - fill only when market clearly trades through your price
- `queue_model = touch_join`
  - if you join best bid/ask, assign a fill probability based on:
    - side depth
    - trade flow
    - whether your quote improved the touch
- `queue_model = calibrated`
  - fit join fill probability from your historical run logs

Do not hide the queue model inside the engine.
Expose it as a parameterized module.

---

## 6. Round 2 access simulation layer

## 6.1 Concept
Public round 2 data is the **no-access view**.
Access adds approximately **25% more quotes** from the same distribution.

So the backtester must have two book modes:

### `mode = no_access`
Replay only the visible public book.

### `mode = access`
Augment the visible public book with synthetic latent quotes.

## 6.2 Latent quote generator
The generator should sample extra quotes conditional on the visible state.

Recommended conditioning variables:
- product
- spread bucket
- top-of-book depth bucket
- side imbalance bucket
- price distance from slow anchor
- day / time bucket

Recommended outputs:
- whether an extra quote exists
- side
- price level relative to current touch
- size

A good first approximation:
- sample price offsets and sizes from empirical top-level and second-level distributions in the public data
- insert at plausible places consistent with current spread and depth

The goal is not exact hidden-book reconstruction.
The goal is a **stable estimate of access value**.

## 6.3 Access delta
For every strategy variant compute:

```text
PnL_no_access
PnL_access
Δ_access = PnL_access - PnL_no_access
```

This must be a standard output of every backtest.

---

## 7. Round 2 budget layer

Implement the growth pillars as a transformation layer on top of replay.

### Generic interface
```python
apply_pillar_config(state, pillar_config) -> transformed_state
```

Possible transformations:
- volume multiplier
- additional accessible quotes
- quote fill probability modifier
- better latency / faster reposting
- cost reduction
- position or risk scaling

Until the exact pillar mechanics are known, keep the layer generic.
The optimizer should not care what a pillar “means,” only what it changes in the replay.

### Budget search
When pillar mechanics are known:
- evaluate allocations in fixed increments (e.g. 5k or 10k)
- compute final PnL for each allocation
- derive marginal ROI per pillar
- allocate by marginal ROI, not narrative preference

---

## 8. Diagnostics that must exist

A Round 2 backtester without diagnostics is not enough.

### 8.1 Strategy-level outputs
For every run:
- total PnL
- per-product PnL
- final positions
- max drawdown
- total aggressive fills
- total passive fills
- average markout by side
- `Δ_access`

### 8.2 Osmium diagnostics
Bucket every fill by:
- toxicity level
- conviction bucket
- spread bucket
- agreement/magnet state
- side-starvation state
- access vs no-access source
- vacuum / post-vacuum regime

Track:
- fill count
- mean edge at fill
- mean post-fill markout
- realized PnL contribution

### 8.3 Pepper diagnostics
Track:
- average entry price
- carry accumulation schedule
- buy vs sell counts
- residual z-score at fill
- deviation from deterministic trend
- late-day trimming contribution

### 8.4 Plateau diagnostics
Track timestamps or windows where:
- Osmium has no fill for `N` bars
- quotes are present but not filling
- toxicity is low but throughput is zero
- signal is nonzero but queue position never improves

This is crucial for debugging “plateau” branches.

---

## 9. Parser and replay examples

## 9.1 Parse `activitiesLog`
```python
import io
import pandas as pd

def parse_activities_log(text: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(text), sep=';')
```

## 9.2 Parse `graphLog`
```python
def parse_graph_log(text: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(text), sep=';')
```

## 9.3 Parse run JSON
```python
def parse_run_json(path):
    raw = json.load(open(path))
    return {
        "round": raw["round"],
        "profit": raw["profit"],
        "activities": parse_activities_log(raw["activitiesLog"]),
        "graph": parse_graph_log(raw["graphLog"]),
        "positions": {x["symbol"]: x["quantity"] for x in raw["positions"]},
    }
```

## 9.4 Parse raw `.log`
```python
def parse_run_log(path):
    raw = json.load(open(path))
    activities = parse_activities_log(raw["activitiesLog"])
    trade_history = pd.DataFrame(raw["tradeHistory"])
    logs = pd.DataFrame(raw["logs"])
    return {
        "submission_id": raw["submissionId"],
        "activities": activities,
        "trade_history": trade_history,
        "internal_logs": logs,
    }
```

---

## 10. Validation plan

## 10.1 Schema validation
For every new file:
- validate required columns / keys
- validate types
- validate timestamp monotonicity within day/product

## 10.2 Replay validation
For known historical runs:
- run the same bot on the same public data
- compare:
  - fill count
  - end positions
  - PnL curve shape
  - final PnL

You do not need perfect equality at first.
You do need the right directional sensitivities.

## 10.3 Access simulation validation
For each strategy:
- run many seeds for latent quote generation
- report mean, median, p25, p10 of `Δ_access`

Never trust a single access seed.

## 10.4 Optimization validation
Only optimize after:
- replay is stable
- access delta is reasonably stable
- diagnostics explain why the baseline behaves the way it does

---

## 11. How to investigate “hacky” or mysterious alpha

When a tweak improves the bot but you cannot explain why, use this procedure:

### Step 1: isolate the exact timestamps where the new run differs
Use:
- per-timestamp PnL difference
- per-timestamp fill difference
- per-timestamp quote difference

### Step 2: classify the difference
Common hidden causes:
- one-tick queue-position change
- side-specific fill starvation resolved
- toxicity released earlier or later
- post-vacuum behavior changed
- integer rounding changed the actual quote level
- access-layer latent quotes got hit by a different fill profile

### Step 3: run targeted ablations
Turn off only:
- markout penalty
- reentry
- join-edge boost
- multi-level sweep
- vacuum rescue
- conviction scaling

### Step 4: test across seeds
If the improvement disappears across seed changes, it is not robust alpha yet.

---

## 12. Recommended build order

### Phase 1: ingestion
- parse price/trade CSVs
- parse run JSONs
- parse raw logs

### Phase 2: baseline replay
- visible-book replay
- deterministic run support
- per-product PnL
- order persistence

### Phase 3: diagnostics
- fill attribution
- markout attribution
- plateau diagnostics

### Phase 4: access simulation
- latent quote generator
- no-access vs access mode
- `Δ_access`

### Phase 5: budget layer
- generic pillar transform
- allocation sweep

### Phase 6: optimization
- only after all above are validated

---

## 13. One-line design principle

**The Round 2 backtester should be built as a replay-and-diagnostics system first, and only second as an optimizer.**
