# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r18_04_a_local_fair_blend`
- Bots: TradervR1_lab_r18_04_a_local_fair_blend.py, TradervR1_34_1.py

## Families

- `original_noise`: Original historical path with very mild execution-noise perturbations.
- `bootstrap_path`: Block-bootstrap of the historical path with no fill perturbation.
- `bootstrap_balanced`: Block-bootstrap with calibrated mild-to-moderate execution degradation.

## Baseline Replay

### TradervR1_34_1

- Combined total PnL: `287305.5000`
- Day -1: `95486.0000`
- Day -2: `95526.5000`
- Day 0: `96293.0000`

### TradervR1_lab_r18_04_a_local_fair_blend

- Combined total PnL: `289140.5000`
- Day -1: `96004.0000`
- Day -2: `96033.5000`
- Day 0: `97103.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r18_04_a_local_fair_blend

- Overall samples: `6` | mean `126386.5` | p10 `-14066.25` | cvar10 `-24922.0` | std `124583.9502`
- Profile `all`: count `6`, mean `126386.5`, p10 `-14066.25`, cvar10 `-24922.0`
- Profile `plausible`: count `6`, mean `126386.5`, p10 `-14066.25`, cvar10 `-24922.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53081.75`, p10 `-9321.25`, cvar10 `-24922.0`
- `bootstrap_path`: count `2`, mean `39328.25`, p10 `5297.25`, cvar10 `-3210.5`
- `original_noise`: count `2`, mean `286749.5`, p10 `286286.7`, cvar10 `286171.0`

## Comparison

- Primary: `TradervR1_lab_r18_04_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `735.0833`
- Median delta: `1172.0`
- P10 delta: `-681.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-681.5`, p10 delta `-935.5`, win rate `0.0`
- `bootstrap_path`: mean delta `1596.75`, p10 delta `1299.35`, win rate `1.0`
- `original_noise`: mean delta `1290.0`, p10 delta `1153.2`, win rate `1.0`

- Profile `all`: mean delta `735.0833`, p10 delta `-681.5`, win rate `0.6667`
- Profile `plausible`: mean delta `735.0833`, p10 delta `-681.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

