# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r04_02_a_attack_tuning`
- Bots: TradervR1_lab_r04_02_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r04_02_a_attack_tuning

- Combined total PnL: `286134.0000`
- Day -1: `95104.0000`
- Day -2: `95107.0000`
- Day 0: `95923.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r04_02_a_attack_tuning

- Overall samples: `6` | mean `121777.5833` | p10 `-21559.0` | cvar10 `-35837.0` | std `126571.036`
- Profile `all`: count `6`, mean `121777.5833`, p10 `-21559.0`, cvar10 `-35837.0`
- Profile `plausible`: count `6`, mean `121777.5833`, p10 `-21559.0`, cvar10 `-35837.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `44862.5`, p10 `-19697.1`, cvar10 `-35837.0`
- `bootstrap_path`: count `2`, mean `36166.5`, p10 `1408.5`, cvar10 `-7281.0`
- `original_noise`: count `2`, mean `284303.75`, p10 `283661.55`, cvar10 `283501.0`

## Comparison

- Primary: `TradervR1_lab_r04_02_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-3873.8333`
- Median delta: `-1655.5`
- P10 delta: `-8900.75`
- Win rate: `0.0`

- `bootstrap_balanced`: mean delta `-8900.75`, p10 delta `-10803.35`, win rate `0.0`
- `bootstrap_path`: mean delta `-1565.0`, p10 delta `-1994.6`, win rate `0.0`
- `original_noise`: mean delta `-1155.75`, p10 delta `-1198.35`, win rate `0.0`

- Profile `all`: mean delta `-3873.8333`, p10 delta `-8900.75`, win rate `0.0`
- Profile `plausible`: mean delta `-3873.8333`, p10 delta `-8900.75`, win rate `0.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

