# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r11_03_a_attack_tuning_p_entry_quality`
- Bots: TradervR1_lab_r11_03_a_attack_tuning_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r11_03_a_attack_tuning_p_entry_quality

- Combined total PnL: `290110.5000`
- Day -1: `96244.0000`
- Day -2: `96424.5000`
- Day 0: `97442.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r11_03_a_attack_tuning_p_entry_quality

- Overall samples: `6` | mean `125972.8333` | p10 `-19034.75` | cvar10 `-35721.0` | std `127293.3465`
- Profile `all`: count `6`, mean `125972.8333`, p10 `-19034.75`, cvar10 `-35721.0`
- Profile `plausible`: count `6`, mean `125972.8333`, p10 `-19034.75`, cvar10 `-35721.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49066.75`, p10 `-18763.45`, cvar10 `-35721.0`
- `bootstrap_path`: count `2`, mean `40504.75`, p10 `6222.15`, cvar10 `-2348.5`
- `original_noise`: count `2`, mean `288347.0`, p10 `287670.2`, cvar10 `287501.0`

## Comparison

- Primary: `TradervR1_lab_r11_03_a_attack_tuning_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `321.4167`
- Median delta: `2753.5`
- P10 delta: `-4696.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-4696.5`, p10 delta `-9869.7`, win rate `0.5`
- `bootstrap_path`: mean delta `2773.25`, p10 delta `2727.45`, win rate `1.0`
- `original_noise`: mean delta `2887.5`, p10 delta `2810.3`, win rate `1.0`

- Profile `all`: mean delta `321.4167`, p10 delta `-4696.5`, win rate `0.8333`
- Profile `plausible`: mean delta `321.4167`, p10 delta `-4696.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

