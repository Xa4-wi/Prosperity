# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r10_06_p_carry_defense_cmaes_pepper_carry_defense`
- Bots: TradervR1_lab_r10_06_p_carry_defense_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r10_06_p_carry_defense_best

- Combined total PnL: `288932.0000`
- Day -1: `95897.0000`
- Day -2: `95963.0000`
- Day 0: `97072.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r10_06_p_carry_defense_best

- Overall samples: `6` | mean `126295.5833` | p10 `-13995.75` | cvar10 `-24389.0` | std `124435.1093`
- Profile `all`: count `6`, mean `126295.5833`, p10 `-13995.75`, cvar10 `-24389.0`
- Profile `plausible`: count `6`, mean `126295.5833`, p10 `-13995.75`, cvar10 `-24389.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53331.25`, p10 `-8844.95`, cvar10 `-24389.0`
- `bootstrap_path`: count `2`, mean `39075.75`, p10 `4933.15`, cvar10 `-3602.5`
- `original_noise`: count `2`, mean `286479.75`, p10 `286000.75`, cvar10 `285881.0`

## Comparison

- Primary: `TradervR1_lab_r10_06_p_carry_defense_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `644.1667`
- Median delta: `990.75`
- P10 delta: `-432.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-432.0`, p10 delta `-912.8`, win rate `0.5`
- `bootstrap_path`: mean delta `1344.25`, p10 delta `1158.45`, win rate `1.0`
- `original_noise`: mean delta `1020.25`, p10 delta `899.65`, win rate `1.0`

- Profile `all`: mean delta `644.1667`, p10 delta `-432.0`, win rate `0.8333`
- Profile `plausible`: mean delta `644.1667`, p10 delta `-432.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

