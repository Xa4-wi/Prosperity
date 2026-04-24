# Round 2 Build-Up Workflow Report

Generated at: `2026-04-17T20:32:39.076468+00:00`

This report tracks the clean Round 2 rebuild path from the staged build-up plan, replays the available bots, and marks missing future steps so the workflow stays easy to supervise.

## Current Best

- Best tested branch: [`R2_17`](Bots/Round2/TradervR2_17.py)
- Three-day total: `258086.0`
- Split: Ash `19736.0`, Pepper `238350.0`

## Stage Board

| Stage             | Bot                         | Status      | Three-day total | Delta vs parent | Ash     | Pepper   | Ash max plateau |
| ----------------- | --------------------------- | ----------- | --------------- | --------------- | ------- | -------- | --------------- |
| R2_12             | TradervR2_12.py             | tested      | 218217.0        | -               | 19372.0 | 198845.0 | 88              |
| R2_13             | TradervR2_13.py             | support     | 257722.0        | +39505.0        | 19372.0 | 238350.0 | 88              |
| R2_14             | TradervR2_14.py             | tested      | 256640.0        | -1082.0         | 18290.0 | 238350.0 | 70              |
| R2_15             | TradervR2_15.py             | tested      | 257970.0        | +248.0          | 19620.0 | 238350.0 | 47              |
| R2_16             | TradervR2_16.py             | tested      | 258078.0        | +108.0          | 19728.0 | 238350.0 | 44              |
| R2_17             | TradervR2_17.py             | tested      | 258086.0        | +8.0            | 19736.0 | 238350.0 | 44              |
| R2_18             | TradervR2_18.py             | exploratory | 256499.0        | -1587.0         | 18149.0 | 238350.0 | 65              |
| R2_19             | TradervR2_19.py             | exploratory | 257329.0        | -757.0          | 18979.0 | 238350.0 | 58              |
| R2_18_recycler    | TradervR2_18_recycler.py    | tested      | 258058.0        | -28.0           | 19708.0 | 238350.0 | 44              |
| R2_19_accessaware | TradervR2_19_accessaware.py | missing     | -               | -               | -       | -        | -               |
| R2_20_multisweep  | TradervR2_20_multisweep.py  | missing     | -               | -               | -       | -        | -               |

## Supported Metrics

The deterministic replay artifacts currently support:
- total PnL
- product PnL split
- total own trade count
- plateau stats inferred from `activitiesLog`

The workflow marks these as unavailable unless future bots emit diagnostics or the replay artifact format changes:
- final positions
- Osmium take/passive fill split
- toxic level flips
- reentry event count
- average passive markout

## Per-Stage Notes

### R2_12 — Structural base rewrite

- File: `Bots/Round2/TradervR2_12.py`
- Notes: Clean restart baseline.
- Three-day total: `218217.0`
- Split: Ash `19372.0`, Pepper `198845.0`
- Max Ash flat plateau: `88` bars (`8800` timestamps)
- Max Pepper flat plateau: `26` bars (`2600` timestamps)
- Day breakdown:
  - day `-1`: total `73274.0`, Ash `7055.0`, Pepper `66219.0`, own trades `897`
  - day `0`: total `72752.0`, Ash `6399.0`, Pepper `66353.0`, own trades `897`
  - day `1`: total `72191.0`, Ash `5918.0`, Pepper `66273.0`, own trades `913`

### R2_13 — Pepper restoration

- File: `Bots/Round2/TradervR2_13.py`
- Notes: Preparatory step outside the formal plan; restores the stronger Pepper engine.
- Three-day total: `257722.0`
- Split: Ash `19372.0`, Pepper `238350.0`
- Delta vs `R2_12`: `+39505.0`
- Max Ash flat plateau: `88` bars (`8800` timestamps)
- Max Pepper flat plateau: `8` bars (`800` timestamps)
- Day breakdown:
  - day `-1`: total `86529.0`, Ash `7055.0`, Pepper `79474.0`, own trades `845`
  - day `0`: total `85882.0`, Ash `6399.0`, Pepper `79483.0`, own trades `845`
  - day `1`: total `85311.0`, Ash `5918.0`, Pepper `79393.0`, own trades `860`

### R2_14 — Step 1 - conviction

- File: `Bots/Round2/TradervR2_14.py`
- Notes: Adds conviction-only Osmium layer.
- Three-day total: `256640.0`
- Split: Ash `18290.0`, Pepper `238350.0`
- Delta vs `R2_13`: `-1082.0`
- Max Ash flat plateau: `70` bars (`7000` timestamps)
- Max Pepper flat plateau: `8` bars (`800` timestamps)
- Day breakdown:
  - day `-1`: total `86160.0`, Ash `6686.0`, Pepper `79474.0`, own trades `883`
  - day `0`: total `85474.0`, Ash `5991.0`, Pepper `79483.0`, own trades `897`
  - day `1`: total `85006.0`, Ash `5613.0`, Pepper `79393.0`, own trades `901`

### R2_15 — Step 2 - toxicity smoothing

- File: `Bots/Round2/TradervR2_15.py`
- Notes: Light side-specific toxicity smoothing.
- Three-day total: `257970.0`
- Split: Ash `19620.0`, Pepper `238350.0`
- Delta vs `R2_13`: `+248.0`
- Max Ash flat plateau: `47` bars (`4700` timestamps)
- Max Pepper flat plateau: `8` bars (`800` timestamps)
- Day breakdown:
  - day `-1`: total `86641.0`, Ash `7167.0`, Pepper `79474.0`, own trades `842`
  - day `0`: total `85888.0`, Ash `6405.0`, Pepper `79483.0`, own trades `853`
  - day `1`: total `85441.0`, Ash `6048.0`, Pepper `79393.0`, own trades `854`

### R2_16 — Step 3 - reentry / neutral drip

- File: `Bots/Round2/TradervR2_16.py`
- Notes: Side-specific re-entry and neutral drip on top of toxicity.
- Three-day total: `258078.0`
- Split: Ash `19728.0`, Pepper `238350.0`
- Delta vs `R2_15`: `+108.0`
- Max Ash flat plateau: `44` bars (`4400` timestamps)
- Max Pepper flat plateau: `8` bars (`800` timestamps)
- Day breakdown:
  - day `-1`: total `86668.0`, Ash `7194.0`, Pepper `79474.0`, own trades `1130`
  - day `0`: total `86045.0`, Ash `6562.0`, Pepper `79483.0`, own trades `1140`
  - day `1`: total `85365.0`, Ash `5972.0`, Pepper `79393.0`, own trades `1161`

### R2_17 — Step 4 - passive-only markout

- File: `Bots/Round2/TradervR2_17.py`
- Notes: Passive-only markout memory on top of re-entry.
- Three-day total: `258086.0`
- Split: Ash `19736.0`, Pepper `238350.0`
- Delta vs `R2_16`: `+8.0`
- Max Ash flat plateau: `44` bars (`4400` timestamps)
- Max Pepper flat plateau: `8` bars (`800` timestamps)
- Day breakdown:
  - day `-1`: total `86676.0`, Ash `7202.0`, Pepper `79474.0`, own trades `1130`
  - day `0`: total `86045.0`, Ash `6562.0`, Pepper `79483.0`, own trades `1140`
  - day `1`: total `85365.0`, Ash `5972.0`, Pepper `79393.0`, own trades `1161`

### R2_18 — Exploratory - alpha split heavy

- File: `Bots/Round2/TradervR2_18.py`
- Notes: Aggressive take/quote alpha split experiment; not part of the main plan.
- Three-day total: `256499.0`
- Split: Ash `18149.0`, Pepper `238350.0`
- Delta vs `R2_17`: `-1587.0`
- Max Ash flat plateau: `65` bars (`6500` timestamps)
- Max Pepper flat plateau: `8` bars (`800` timestamps)
- Day breakdown:
  - day `-1`: total `86066.0`, Ash `6592.0`, Pepper `79474.0`, own trades `1244`
  - day `0`: total `85452.0`, Ash `5969.0`, Pepper `79483.0`, own trades `1270`
  - day `1`: total `84981.0`, Ash `5588.0`, Pepper `79393.0`, own trades `1278`

### R2_19 — Exploratory - alpha split light

- File: `Bots/Round2/TradervR2_19.py`
- Notes: Lighter take/quote alpha split experiment; not part of the main plan.
- Three-day total: `257329.0`
- Split: Ash `18979.0`, Pepper `238350.0`
- Delta vs `R2_17`: `-757.0`
- Max Ash flat plateau: `58` bars (`5800` timestamps)
- Max Pepper flat plateau: `8` bars (`800` timestamps)
- Day breakdown:
  - day `-1`: total `86344.0`, Ash `6870.0`, Pepper `79474.0`, own trades `1154`
  - day `0`: total `85859.0`, Ash `6376.0`, Pepper `79483.0`, own trades `1176`
  - day `1`: total `85126.0`, Ash `5733.0`, Pepper `79393.0`, own trades `1197`

### R2_18_recycler — Step 5 - recycler

- File: `Bots/Round2/TradervR2_18_recycler.py`
- Notes: Planned but not implemented yet.
- Three-day total: `258058.0`
- Split: Ash `19708.0`, Pepper `238350.0`
- Delta vs `R2_17`: `-28.0`
- Max Ash flat plateau: `44` bars (`4400` timestamps)
- Max Pepper flat plateau: `8` bars (`800` timestamps)
- Day breakdown:
  - day `-1`: total `86649.0`, Ash `7175.0`, Pepper `79474.0`, own trades `1132`
  - day `0`: total `86044.0`, Ash `6561.0`, Pepper `79483.0`, own trades `1140`
  - day `1`: total `85365.0`, Ash `5972.0`, Pepper `79393.0`, own trades `1161`

### R2_19_accessaware — Step 6 - access-aware extension

- File: `Bots/Round2/TradervR2_19_accessaware.py`
- Notes: Planned but not implemented yet.
- Status: missing

### R2_20_multisweep — Step 7 - multi-level sweep

- File: `Bots/Round2/TradervR2_20_multisweep.py`
- Notes: Optional later stage; not implemented yet.
- Status: missing

## Next Gaps

- `R2_19_accessaware` is still missing: Step 6 - access-aware extension
- `R2_20_multisweep` is still missing: Step 7 - multi-level sweep
