# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r13_02_p_carry_defense`
- Bots: TradervR1_lab_r13_02_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r13_02_p_carry_defense

- Combined total PnL: `289289.0000`
- Day -1: `96012.0000`
- Day -2: `96088.0000`
- Day 0: `97189.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r13_02_p_carry_defense

- Overall samples: `6` | mean `126335.75` | p10 `-16594.25` | cvar10 `-29868.0` | std `125831.1815`
- Profile `all`: count `6`, mean `126335.75`, p10 `-16594.25`, cvar10 `-29868.0`
- Profile `plausible`: count `6`, mean `126335.75`, p10 `-16594.25`, cvar10 `-29868.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51996.5`, p10 `-13495.1`, cvar10 `-29868.0`
- `bootstrap_path`: count `2`, mean `39695.25`, p10 `5282.65`, cvar10 `-3320.5`
- `original_noise`: count `2`, mean `287315.5`, p10 `286545.1`, cvar10 `286352.5`

## Comparison

- Primary: `TradervR1_lab_r13_02_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `684.3333`
- Median delta: `1817.5`
- P10 delta: `-1833.75`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-1766.75`, p10 delta `-4601.35`, win rate `0.5`
- `bootstrap_path`: mean delta `1963.75`, p10 delta `1879.55`, win rate `1.0`
- `original_noise`: mean delta `1856.0`, p10 delta `1685.2`, win rate `1.0`

- Profile `all`: mean delta `684.3333`, p10 delta `-1833.75`, win rate `0.8333`
- Profile `plausible`: mean delta `684.3333`, p10 delta `-1833.75`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

