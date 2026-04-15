# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r08_02_a_attack_tuning`
- Bots: TradervR1_lab_r08_02_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r08_02_a_attack_tuning

- Combined total PnL: `289188.5000`
- Day -1: `96057.0000`
- Day -2: `96133.5000`
- Day 0: `96998.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r08_02_a_attack_tuning

- Overall samples: `6` | mean `126527.1667` | p10 `-11646.25` | cvar10 `-19289.0` | std `123590.9854`
- Profile `all`: count `6`, mean `126527.1667`, p10 `-11646.25`, cvar10 `-19289.0`
- Profile `plausible`: count `6`, mean `126527.1667`, p10 `-11646.25`, cvar10 `-19289.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `54134.5`, p10 `-4604.3`, cvar10 `-19289.0`
- `bootstrap_path`: count `2`, mean `38740.25`, p10 `4545.25`, cvar10 `-4003.5`
- `original_noise`: count `2`, mean `286706.75`, p10 `285754.55`, cvar10 `285516.5`

## Comparison

- Primary: `TradervR1_lab_r08_02_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `875.75`
- Median delta: `1008.75`
- P10 delta: `-1860.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `371.25`, p10 delta `-3546.95`, win rate `0.5`
- `bootstrap_path`: mean delta `1008.75`, p10 delta `875.35`, win rate `1.0`
- `original_noise`: mean delta `1247.25`, p10 delta `894.65`, win rate `1.0`

- Profile `all`: mean delta `875.75`, p10 delta `-1860.0`, win rate `0.8333`
- Profile `plausible`: mean delta `875.75`, p10 delta `-1860.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

