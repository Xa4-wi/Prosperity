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

- Overall samples: `6` | mean `129203.5` | p10 `-15090.25` | cvar10 `-28961.0` | std `126035.7385`
- Profile `all`: count `6`, mean `129203.5`, p10 `-15090.25`, cvar10 `-28961.0`
- Profile `plausible`: count `6`, mean `129203.5`, p10 `-15090.25`, cvar10 `-28961.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `57231.5`, p10 `-11722.5`, cvar10 `-28961.0`
- `bootstrap_path`: count `2`, mean `41420.75`, p10 `7308.55`, cvar10 `-1219.5`
- `original_noise`: count `2`, mean `288958.25`, p10 `288502.85`, cvar10 `288389.0`

## Comparison

- Primary: `TradervR1_lab_r07_03_p_entry_quality_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `3552.0833`
- Median delta: `3549.0`
- P10 delta: `-542.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `3468.25`, p10 delta `-2828.75`, win rate `0.5`
- `bootstrap_path`: mean delta `3689.25`, p10 delta `3473.05`, win rate `1.0`
- `original_noise`: mean delta `3498.75`, p10 delta `3354.55`, win rate `1.0`

- Profile `all`: mean delta `3552.0833`, p10 delta `-542.25`, win rate `0.8333`
- Profile `plausible`: mean delta `3552.0833`, p10 delta `-542.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

