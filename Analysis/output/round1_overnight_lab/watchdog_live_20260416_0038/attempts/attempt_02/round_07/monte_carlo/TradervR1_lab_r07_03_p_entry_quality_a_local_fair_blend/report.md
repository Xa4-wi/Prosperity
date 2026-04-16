# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r07_03_p_entry_quality_a_local_fair_blend`
- Bots: TradervR1_lab_r07_03_p_entry_quality_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r07_03_p_entry_quality_a_local_fair_blend

- Combined total PnL: `290540.5000`
- Day -1: `96548.0000`
- Day -2: `96672.5000`
- Day 0: `97320.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r07_03_p_entry_quality_a_local_fair_blend

- Overall samples: `6` | mean `127169.6667` | p10 `-14837.25` | cvar10 `-28455.0` | std `125667.4233`
- Profile `all`: count `6`, mean `127169.6667`, p10 `-14837.25`, cvar10 `-28455.0`
- Profile `plausible`: count `6`, mean `127169.6667`, p10 `-14837.25`, cvar10 `-28455.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51403.0`, p10 `-12483.4`, cvar10 `-28455.0`
- `bootstrap_path`: count `2`, mean `41420.75`, p10 `7308.55`, cvar10 `-1219.5`
- `original_noise`: count `2`, mean `288685.25`, p10 `288033.05`, cvar10 `287870.0`

## Comparison

- Primary: `TradervR1_lab_r07_03_p_entry_quality_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1518.25`
- Median delta: `3225.75`
- P10 delta: `-2360.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-2360.25`, p10 delta `-3589.65`, win rate `0.0`
- `bootstrap_path`: mean delta `3689.25`, p10 delta `3473.05`, win rate `1.0`
- `original_noise`: mean delta `3225.75`, p10 delta `3173.15`, win rate `1.0`

- Profile `all`: mean delta `1518.25`, p10 delta `-2360.25`, win rate `0.6667`
- Profile `plausible`: mean delta `1518.25`, p10 delta `-2360.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

