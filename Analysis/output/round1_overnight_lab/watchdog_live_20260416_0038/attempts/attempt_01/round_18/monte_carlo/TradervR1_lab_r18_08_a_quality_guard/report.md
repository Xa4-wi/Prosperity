# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r18_08_a_quality_guard`
- Bots: TradervR1_lab_r18_08_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r18_08_a_quality_guard

- Combined total PnL: `290141.0000`
- Day -1: `96227.0000`
- Day -2: `96427.0000`
- Day 0: `97487.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r18_08_a_quality_guard

- Overall samples: `6` | mean `126985.1667` | p10 `-17908.25` | cvar10 `-33538.0` | std `126852.627`
- Profile `all`: count `6`, mean `126985.1667`, p10 `-17908.25`, cvar10 `-33538.0`
- Profile `plausible`: count `6`, mean `126985.1667`, p10 `-17908.25`, cvar10 `-33538.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52145.5`, p10 `-16401.3`, cvar10 `-33538.0`
- `bootstrap_path`: count `2`, mean `40509.75`, p10 `6279.15`, cvar10 `-2278.5`
- `original_noise`: count `2`, mean `288300.25`, p10 `287611.65`, cvar10 `287439.5`

## Comparison

- Primary: `TradervR1_lab_r18_08_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1333.75`
- Median delta: `2815.0`
- P10 delta: `-3162.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-1617.75`, p10 delta `-7507.55`, win rate `0.5`
- `bootstrap_path`: mean delta `2778.25`, p10 delta `2680.45`, win rate `1.0`
- `original_noise`: mean delta `2840.75`, p10 delta `2751.75`, win rate `1.0`

- Profile `all`: mean delta `1333.75`, p10 delta `-3162.0`, win rate `0.8333`
- Profile `plausible`: mean delta `1333.75`, p10 delta `-3162.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

