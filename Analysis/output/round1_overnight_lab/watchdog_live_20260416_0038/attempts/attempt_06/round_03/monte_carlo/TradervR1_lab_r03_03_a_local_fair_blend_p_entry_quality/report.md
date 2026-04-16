# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality`
- Bots: TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality

- Combined total PnL: `289245.5000`
- Day -1: `95997.0000`
- Day -2: `96032.5000`
- Day 0: `97216.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality

- Overall samples: `6` | mean `127510.8333` | p10 `-12786.75` | cvar10 `-22676.0` | std `124142.8454`
- Profile `all`: count `6`, mean `127510.8333`, p10 `-12786.75`, cvar10 `-22676.0`
- Profile `plausible`: count `6`, mean `127510.8333`, p10 `-12786.75`, cvar10 `-22676.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `55564.25`, p10 `-7027.95`, cvar10 `-22676.0`
- `bootstrap_path`: count `2`, mean `39973.75`, p10 `5676.75`, cvar10 `-2897.5`
- `original_noise`: count `2`, mean `286994.5`, p10 `286294.5`, cvar10 `286119.5`

## Comparison

- Primary: `TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1859.4167`
- Median delta: `1801.0`
- P10 delta: `1535.0`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `1801.0`, p10 delta `1736.2`, win rate `1.0`
- `bootstrap_path`: mean delta `2242.25`, p10 delta `2210.85`, win rate `1.0`
- `original_noise`: mean delta `1535.0`, p10 delta `1434.6`, win rate `1.0`

- Profile `all`: mean delta `1859.4167`, p10 delta `1535.0`, win rate `1.0`
- Profile `plausible`: mean delta `1859.4167`, p10 delta `1535.0`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

