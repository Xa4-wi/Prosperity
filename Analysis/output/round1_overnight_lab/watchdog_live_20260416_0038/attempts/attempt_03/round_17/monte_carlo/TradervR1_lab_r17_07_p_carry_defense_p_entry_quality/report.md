# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r17_07_p_carry_defense_p_entry_quality`
- Bots: TradervR1_lab_r17_07_p_carry_defense_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r17_07_p_carry_defense_p_entry_quality

- Combined total PnL: `288927.0000`
- Day -1: `95897.0000`
- Day -2: `95973.0000`
- Day 0: `97057.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r17_07_p_carry_defense_p_entry_quality

- Overall samples: `6` | mean `123533.9167` | p10 `-20252.75` | cvar10 `-36903.0` | std `126918.3025`
- Profile `all`: count `6`, mean `123533.9167`, p10 `-20252.75`, cvar10 `-36903.0`
- Profile `plausible`: count `6`, mean `123533.9167`, p10 `-20252.75`, cvar10 `-36903.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `45257.75`, p10 `-20470.85`, cvar10 `-36903.0`
- `bootstrap_path`: count `2`, mean `39053.75`, p10 `4928.75`, cvar10 `-3602.5`
- `original_noise`: count `2`, mean `286290.25`, p10 `285435.65`, cvar10 `285222.0`

## Comparison

- Primary: `TradervR1_lab_r17_07_p_carry_defense_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-2117.5`
- Median delta: `790.0`
- P10 delta: `-8505.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-8505.5`, p10 delta `-11577.1`, win rate `0.0`
- `bootstrap_path`: mean delta `1322.25`, p10 delta `1118.85`, win rate `1.0`
- `original_noise`: mean delta `830.75`, p10 delta `575.75`, win rate `1.0`

- Profile `all`: mean delta `-2117.5`, p10 delta `-8505.5`, win rate `0.6667`
- Profile `plausible`: mean delta `-2117.5`, p10 delta `-8505.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

