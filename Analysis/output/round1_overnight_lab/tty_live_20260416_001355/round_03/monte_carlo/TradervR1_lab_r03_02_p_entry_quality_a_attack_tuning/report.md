# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r03_02_p_entry_quality_a_attack_tuning`
- Bots: TradervR1_lab_r03_02_p_entry_quality_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r03_02_p_entry_quality_a_attack_tuning

- Combined total PnL: `290412.5000`
- Day -1: `96394.0000`
- Day -2: `96633.5000`
- Day 0: `97385.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r03_02_p_entry_quality_a_attack_tuning

- Overall samples: `6` | mean `126972.4167` | p10 `-14423.5` | cvar10 `-27077.0` | std `125363.0275`
- Profile `all`: count `6`, mean `126972.4167`, p10 `-14423.5`, cvar10 `-27077.0`
- Profile `plausible`: count `6`, mean `126972.4167`, p10 `-14423.5`, cvar10 `-27077.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51590.75`, p10 `-11343.45`, cvar10 `-27077.0`
- `bootstrap_path`: count `2`, mean `40950.0`, p10 `6774.0`, cvar10 `-1770.0`
- `original_noise`: count `2`, mean `288376.5`, p10 `287798.1`, cvar10 `287653.5`

## Comparison

- Primary: `TradervR1_lab_r03_02_p_entry_quality_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1321.0`
- Median delta: `2917.0`
- P10 delta: `-2172.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-2172.5`, p10 delta `-2449.7`, win rate `0.0`
- `bootstrap_path`: mean delta `3218.5`, p10 delta `3066.1`, win rate `1.0`
- `original_noise`: mean delta `2917.0`, p10 delta `2895.8`, win rate `1.0`

- Profile `all`: mean delta `1321.0`, p10 delta `-2172.5`, win rate `0.6667`
- Profile `plausible`: mean delta `1321.0`, p10 delta `-2172.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

