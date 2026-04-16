# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r06_08_p_carry_defense_a_quality_guard`
- Bots: TradervR1_lab_r06_08_p_carry_defense_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r06_08_p_carry_defense_a_quality_guard

- Combined total PnL: `287543.0000`
- Day -1: `95520.0000`
- Day -2: `95524.0000`
- Day 0: `96499.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r06_08_p_carry_defense_a_quality_guard

- Overall samples: `6` | mean `124100.8333` | p10 `-18857.25` | cvar10 `-32713.0` | std `126087.2276`
- Profile `all`: count `6`, mean `124100.8333`, p10 `-18857.25`, cvar10 `-32713.0`
- Profile `plausible`: count `6`, mean `124100.8333`, p10 `-18857.25`, cvar10 `-32713.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `48730.0`, p10 `-16424.4`, cvar10 `-32713.0`
- `bootstrap_path`: count `2`, mean `37892.25`, p10 `3577.25`, cvar10 `-5001.5`
- `original_noise`: count `2`, mean `285680.25`, p10 `285092.05`, cvar10 `284945.0`

## Comparison

- Primary: `TradervR1_lab_r06_08_p_carry_defense_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1550.5833`
- Median delta: `160.75`
- P10 delta: `-5033.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-5033.25`, p10 delta `-7530.65`, win rate `0.0`
- `bootstrap_path`: mean delta `160.75`, p10 delta `147.35`, win rate `1.0`
- `original_noise`: mean delta `220.75`, p10 delta `209.35`, win rate `1.0`

- Profile `all`: mean delta `-1550.5833`, p10 delta `-5033.25`, win rate `0.6667`
- Profile `plausible`: mean delta `-1550.5833`, p10 delta `-5033.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

