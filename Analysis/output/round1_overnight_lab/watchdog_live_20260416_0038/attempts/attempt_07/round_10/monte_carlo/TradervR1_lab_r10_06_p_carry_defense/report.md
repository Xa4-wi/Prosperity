# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r10_06_p_carry_defense`
- Bots: TradervR1_lab_r10_06_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r10_06_p_carry_defense

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

### TradervR1_lab_r10_06_p_carry_defense

- Overall samples: `6` | mean `125624.9167` | p10 `-16403.25` | cvar10 `-29204.0` | std `125619.0894`
- Profile `all`: count `6`, mean `125624.9167`, p10 `-16403.25`, cvar10 `-29204.0`
- Profile `plausible`: count `6`, mean `125624.9167`, p10 `-16403.25`, cvar10 `-29204.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50844.0`, p10 `-13194.4`, cvar10 `-29204.0`
- `bootstrap_path`: count `2`, mean `39075.75`, p10 `4933.15`, cvar10 `-3602.5`
- `original_noise`: count `2`, mean `286955.0`, p10 `286150.2`, cvar10 `285949.0`

## Comparison

- Primary: `TradervR1_lab_r10_06_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-26.5`
- Median delta: `1175.5`
- P10 delta: `-2919.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-2919.25`, p10 delta `-4300.65`, win rate `0.0`
- `bootstrap_path`: mean delta `1344.25`, p10 delta `1158.45`, win rate `1.0`
- `original_noise`: mean delta `1495.5`, p10 delta `1290.3`, win rate `1.0`

- Profile `all`: mean delta `-26.5`, p10 delta `-2919.25`, win rate `0.6667`
- Profile `plausible`: mean delta `-26.5`, p10 delta `-2919.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

