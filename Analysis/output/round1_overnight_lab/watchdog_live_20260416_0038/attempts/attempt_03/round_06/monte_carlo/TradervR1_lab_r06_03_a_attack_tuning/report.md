# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r06_03_a_attack_tuning`
- Bots: TradervR1_lab_r06_03_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r06_03_a_attack_tuning

- Combined total PnL: `288894.5000`
- Day -1: `95885.0000`
- Day -2: `95917.5000`
- Day 0: `97092.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r06_03_a_attack_tuning

- Overall samples: `6` | mean `125664.4167` | p10 `-17123.0` | cvar10 `-31003.0` | std `125925.7964`
- Profile `all`: count `6`, mean `125664.4167`, p10 `-17123.0`, cvar10 `-31003.0`
- Profile `plausible`: count `6`, mean `125664.4167`, p10 `-17123.0`, cvar10 `-31003.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50744.75`, p10 `-14653.45`, cvar10 `-31003.0`
- `bootstrap_path`: count `2`, mean `39313.5`, p10 `5268.3`, cvar10 `-3243.0`
- `original_noise`: count `2`, mean `286935.0`, p10 `286352.6`, cvar10 `286207.0`

## Comparison

- Primary: `TradervR1_lab_r06_03_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `13.0`
- Median delta: `1341.0`
- P10 delta: `-3018.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-3018.5`, p10 delta `-5759.7`, win rate `0.5`
- `bootstrap_path`: mean delta `1582.0`, p10 delta `1298.8`, win rate `1.0`
- `original_noise`: mean delta `1475.5`, p10 delta `1458.3`, win rate `1.0`

- Profile `all`: mean delta `13.0`, p10 delta `-3018.5`, win rate `0.8333`
- Profile `plausible`: mean delta `13.0`, p10 delta `-3018.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

