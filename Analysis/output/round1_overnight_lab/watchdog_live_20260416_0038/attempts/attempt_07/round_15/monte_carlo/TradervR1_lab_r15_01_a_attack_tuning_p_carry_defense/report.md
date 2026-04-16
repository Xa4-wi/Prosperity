# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r15_01_a_attack_tuning_p_carry_defense`
- Bots: TradervR1_lab_r15_01_a_attack_tuning_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r15_01_a_attack_tuning_p_carry_defense

- Combined total PnL: `288519.5000`
- Day -1: `95807.0000`
- Day -2: `95975.5000`
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

### TradervR1_lab_r15_01_a_attack_tuning_p_carry_defense

- Overall samples: `6` | mean `124856.4167` | p10 `-18705.75` | cvar10 `-33192.0` | std `126317.2945`
- Profile `all`: count `6`, mean `124856.4167`, p10 `-18705.75`, cvar10 `-33192.0`
- Profile `plausible`: count `6`, mean `124856.4167`, p10 `-18705.75`, cvar10 `-33192.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49815.25`, p10 `-16590.55`, cvar10 `-33192.0`
- `bootstrap_path`: count `2`, mean `38465.25`, p10 `4317.45`, cvar10 `-4219.5`
- `original_noise`: count `2`, mean `286288.75`, p10 `285498.15`, cvar10 `285300.5`

## Comparison

- Primary: `TradervR1_lab_r15_01_a_attack_tuning_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-795.0`
- Median delta: `664.25`
- P10 delta: `-4063.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-3948.0`, p10 delta `-7696.8`, win rate `0.5`
- `bootstrap_path`: mean delta `733.75`, p10 delta `553.15`, win rate `1.0`
- `original_noise`: mean delta `829.25`, p10 delta `638.25`, win rate `1.0`

- Profile `all`: mean delta `-795.0`, p10 delta `-4063.0`, win rate `0.8333`
- Profile `plausible`: mean delta `-795.0`, p10 delta `-4063.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

