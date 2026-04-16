# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r09_06_p_carry_defense_a_quality_guard`
- Bots: TradervR1_lab_r09_06_p_carry_defense_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r09_06_p_carry_defense_a_quality_guard

- Combined total PnL: `289378.5000`
- Day -1: `96030.0000`
- Day -2: `96154.5000`
- Day 0: `97194.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r09_06_p_carry_defense_a_quality_guard

- Overall samples: `6` | mean `126717.75` | p10 `-14619.0` | cvar10 `-26832.0` | std `124976.1115`
- Profile `all`: count `6`, mean `126717.75`, p10 `-14619.0`, cvar10 `-26832.0`
- Profile `plausible`: count `6`, mean `126717.75`, p10 `-14619.0`, cvar10 `-26832.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52834.0`, p10 `-10898.8`, cvar10 `-26832.0`
- `bootstrap_path`: count `2`, mean `40147.5`, p10 `6104.7`, cvar10 `-2406.0`
- `original_noise`: count `2`, mean `287171.75`, p10 `286408.35`, cvar10 `286217.5`

## Comparison

- Primary: `TradervR1_lab_r09_06_p_carry_defense_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1066.3333`
- Median delta: `1712.25`
- P10 delta: `-929.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-929.25`, p10 delta `-2005.05`, win rate `0.5`
- `bootstrap_path`: mean delta `2416.0`, p10 delta `2130.4`, win rate `1.0`
- `original_noise`: mean delta `1712.25`, p10 delta `1548.45`, win rate `1.0`

- Profile `all`: mean delta `1066.3333`, p10 delta `-929.25`, win rate `0.8333`
- Profile `plausible`: mean delta `1066.3333`, p10 delta `-929.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

