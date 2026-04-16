# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r14_08_a_attack_tuning_p_carry_defense`
- Bots: TradervR1_lab_r14_08_a_attack_tuning_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r14_08_a_attack_tuning_p_carry_defense

- Combined total PnL: `288491.5000`
- Day -1: `95807.0000`
- Day -2: `95947.5000`
- Day 0: `96737.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r14_08_a_attack_tuning_p_carry_defense

- Overall samples: `6` | mean `123970.0` | p10 `-22039.75` | cvar10 `-39865.0` | std `127854.336`
- Profile `all`: count `6`, mean `123970.0`, p10 `-22039.75`, cvar10 `-39865.0`
- Profile `plausible`: count `6`, mean `123970.0`, p10 `-22039.75`, cvar10 `-39865.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `46869.0`, p10 `-22518.2`, cvar10 `-39865.0`
- `bootstrap_path`: count `2`, mean `38467.75`, p10 `4321.95`, cvar10 `-4214.5`
- `original_noise`: count `2`, mean `286573.25`, p10 `285945.05`, cvar10 `285788.0`

## Comparison

- Primary: `TradervR1_lab_r14_08_a_attack_tuning_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1681.4167`
- Median delta: `1021.25`
- P10 delta: `-7399.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-6894.25`, p10 delta `-13624.45`, win rate `0.5`
- `bootstrap_path`: mean delta `736.25`, p10 delta `553.65`, win rate `1.0`
- `original_noise`: mean delta `1113.75`, p10 delta `1085.15`, win rate `1.0`

- Profile `all`: mean delta `-1681.4167`, p10 delta `-7399.5`, win rate `0.8333`
- Profile `plausible`: mean delta `-1681.4167`, p10 delta `-7399.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

