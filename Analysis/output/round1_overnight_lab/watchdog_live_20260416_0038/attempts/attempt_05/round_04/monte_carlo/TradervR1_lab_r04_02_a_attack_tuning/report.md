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

- Combined total PnL: `288805.5000`
- Day -1: `95852.0000`
- Day -2: `95951.5000`
- Day 0: `97002.0000`

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

- Overall samples: `6` | mean `126091.75` | p10 `-15663.0` | cvar10 `-27999.0` | std `125335.3809`
- Profile `all`: count `6`, mean `126091.75`, p10 `-15663.0`, cvar10 `-27999.0`
- Profile `plausible`: count `6`, mean `126091.75`, p10 `-15663.0`, cvar10 `-27999.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52067.75`, p10 `-11985.65`, cvar10 `-27999.0`
- `bootstrap_path`: count `2`, mean `39239.5`, p10 `5186.3`, cvar10 `-3327.0`
- `original_noise`: count `2`, mean `286968.0`, p10 `286569.6`, cvar10 `286470.0`

## Comparison

- Primary: `TradervR1_lab_r04_02_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `440.3333`
- Median delta: `1210.5`
- P10 delta: `-1695.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-1695.5`, p10 delta `-3091.9`, win rate `0.5`
- `bootstrap_path`: mean delta `1508.0`, p10 delta `1232.8`, win rate `1.0`
- `original_noise`: mean delta `1508.5`, p10 delta `1307.3`, win rate `1.0`

- Profile `all`: mean delta `440.3333`, p10 delta `-1695.5`, win rate `0.8333`
- Profile `plausible`: mean delta `440.3333`, p10 delta `-1695.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

