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

- Combined total PnL: `289493.5000`
- Day -1: `95998.0000`
- Day -2: `96288.5000`
- Day 0: `97207.0000`

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

- Overall samples: `6` | mean `126136.0833` | p10 `-15200.5` | cvar10 `-27339.0` | std `125227.1208`
- Profile `all`: count `6`, mean `126136.0833`, p10 `-15200.5`, cvar10 `-27339.0`
- Profile `plausible`: count `6`, mean `126136.0833`, p10 `-15200.5`, cvar10 `-27339.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51406.75`, p10 `-11589.85`, cvar10 `-27339.0`
- `bootstrap_path`: count `2`, mean `39735.5`, p10 `5497.5`, cvar10 `-3062.0`
- `original_noise`: count `2`, mean `287266.0`, p10 `286650.4`, cvar10 `286496.5`

## Comparison

- Primary: `TradervR1_lab_r04_02_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `484.6667`
- Median delta: `1806.5`
- P10 delta: `-2356.5`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-2356.5`, p10 delta `-2696.1`, win rate `0.0`
- `bootstrap_path`: mean delta `2004.0`, p10 delta `1913.6`, win rate `1.0`
- `original_noise`: mean delta `1806.5`, p10 delta `1790.5`, win rate `1.0`

- Profile `all`: mean delta `484.6667`, p10 delta `-2356.5`, win rate `0.6667`
- Profile `plausible`: mean delta `484.6667`, p10 delta `-2356.5`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

