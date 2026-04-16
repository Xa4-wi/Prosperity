# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r08_07_a_attack_tuning_a_local_fair_blend`
- Bots: TradervR1_lab_r08_07_a_attack_tuning_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r08_07_a_attack_tuning_a_local_fair_blend

- Combined total PnL: `288695.0000`
- Day -1: `95750.0000`
- Day -2: `95939.0000`
- Day 0: `97006.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r08_07_a_attack_tuning_a_local_fair_blend

- Overall samples: `6` | mean `125243.9167` | p10 `-17560.0` | cvar10 `-32074.0` | std `126034.3724`
- Profile `all`: count `6`, mean `125243.9167`, p10 `-17560.0`, cvar10 `-32074.0`
- Profile `plausible`: count `6`, mean `125243.9167`, p10 `-17560.0`, cvar10 `-32074.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49362.25`, p10 `-15786.75`, cvar10 `-32074.0`
- `bootstrap_path`: count `2`, mean `39552.0`, p10 `5473.6`, cvar10 `-3046.0`
- `original_noise`: count `2`, mean `286817.5`, p10 `286323.1`, cvar10 `286199.5`

## Comparison

- Primary: `TradervR1_lab_r08_07_a_attack_tuning_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-407.5`
- Median delta: `1358.0`
- P10 delta: `-4401.0`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-4401.0`, p10 delta `-6893.0`, win rate `0.0`
- `bootstrap_path`: mean delta `1820.5`, p10 delta `1570.5`, win rate `1.0`
- `original_noise`: mean delta `1358.0`, p10 delta `1252.8`, win rate `1.0`

- Profile `all`: mean delta `-407.5`, p10 delta `-4401.0`, win rate `0.6667`
- Profile `plausible`: mean delta `-407.5`, p10 delta `-4401.0`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

