# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r17_04_p_entry_quality`
- Bots: TradervR1_lab_r17_04_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r17_04_p_entry_quality

- Combined total PnL: `288935.0000`
- Day -1: `95897.0000`
- Day -2: `95973.0000`
- Day 0: `97065.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r17_04_p_entry_quality

- Overall samples: `6` | mean `123428.1667` | p10 `-21830.75` | cvar10 `-40059.0` | std `127894.375`
- Profile `all`: count `6`, mean `123428.1667`, p10 `-21830.75`, cvar10 `-40059.0`
- Profile `plausible`: count `6`, mean `123428.1667`, p10 `-21830.75`, cvar10 `-40059.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `44193.5`, p10 `-23208.5`, cvar10 `-40059.0`
- `bootstrap_path`: count `2`, mean `39086.25`, p10 `4935.25`, cvar10 `-3602.5`
- `original_noise`: count `2`, mean `287004.75`, p10 `286161.75`, cvar10 `285951.0`

## Comparison

- Primary: `TradervR1_lab_r17_04_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-2223.25`
- Median delta: `1187.0`
- P10 delta: `-9569.75`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-9569.75`, p10 delta `-14314.75`, win rate `0.0`
- `bootstrap_path`: mean delta `1354.75`, p10 delta `1177.35`, win rate `1.0`
- `original_noise`: mean delta `1545.25`, p10 delta `1301.85`, win rate `1.0`

- Profile `all`: mean delta `-2223.25`, p10 delta `-9569.75`, win rate `0.6667`
- Profile `plausible`: mean delta `-2223.25`, p10 delta `-9569.75`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

