# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r05_07_p_carry_defense_p_entry_quality`
- Bots: TradervR1_lab_r05_07_p_carry_defense_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r05_07_p_carry_defense_p_entry_quality

- Combined total PnL: `289265.0000`
- Day -1: `96012.0000`
- Day -2: `96071.0000`
- Day 0: `97182.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r05_07_p_carry_defense_p_entry_quality

- Overall samples: `6` | mean `126143.6667` | p10 `-16735.75` | cvar10 `-30151.0` | std `125910.2425`
- Profile `all`: count `6`, mean `126143.6667`, p10 `-16735.75`, cvar10 `-30151.0`
- Profile `plausible`: count `6`, mean `126143.6667`, p10 `-16735.75`, cvar10 `-30151.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51367.0`, p10 `-13847.4`, cvar10 `-30151.0`
- `bootstrap_path`: count `2`, mean `39681.75`, p10 `5279.95`, cvar10 `-3320.5`
- `original_noise`: count `2`, mean `287382.25`, p10 `286714.85`, cvar10 `286548.0`

## Comparison

- Primary: `TradervR1_lab_r05_07_p_carry_defense_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `492.25`
- Median delta: `1848.25`
- P10 delta: `-2396.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-2396.25`, p10 delta `-4953.65`, win rate `0.5`
- `bootstrap_path`: mean delta `1950.25`, p10 delta `1876.85`, win rate `1.0`
- `original_noise`: mean delta `1922.75`, p10 delta `1854.95`, win rate `1.0`

- Profile `all`: mean delta `492.25`, p10 delta `-2396.25`, win rate `0.8333`
- Profile `plausible`: mean delta `492.25`, p10 delta `-2396.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

