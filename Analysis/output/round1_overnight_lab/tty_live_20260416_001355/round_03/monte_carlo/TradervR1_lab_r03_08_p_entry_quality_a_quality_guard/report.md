# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r03_08_p_entry_quality_a_quality_guard`
- Bots: TradervR1_lab_r03_08_p_entry_quality_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r03_08_p_entry_quality_a_quality_guard

- Combined total PnL: `291016.0000`
- Day -1: `96564.0000`
- Day -2: `96761.0000`
- Day 0: `97691.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r03_08_p_entry_quality_a_quality_guard

- Overall samples: `6` | mean `127883.4167` | p10 `-11770.25` | cvar10 `-22529.0` | std `124291.6591`
- Profile `all`: count `6`, mean `127883.4167`, p10 `-11770.25`, cvar10 `-22529.0`
- Profile `plausible`: count `6`, mean `127883.4167`, p10 `-11770.25`, cvar10 `-22529.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53718.25`, p10 `-7279.55`, cvar10 `-22529.0`
- `bootstrap_path`: count `2`, mean `41537.25`, p10 `7498.25`, cvar10 `-1011.5`
- `original_noise`: count `2`, mean `288394.75`, p10 `287522.15`, cvar10 `287304.0`

## Comparison

- Primary: `TradervR1_lab_r03_08_p_entry_quality_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2232.0`
- Median delta: `2935.25`
- P10 delta: `-45.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-45.0`, p10 delta `-1704.2`, win rate `0.5`
- `bootstrap_path`: mean delta `3805.75`, p10 delta `3516.35`, win rate `1.0`
- `original_noise`: mean delta `2935.25`, p10 delta `2662.25`, win rate `1.0`

- Profile `all`: mean delta `2232.0`, p10 delta `-45.0`, win rate `0.8333`
- Profile `plausible`: mean delta `2232.0`, p10 delta `-45.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

