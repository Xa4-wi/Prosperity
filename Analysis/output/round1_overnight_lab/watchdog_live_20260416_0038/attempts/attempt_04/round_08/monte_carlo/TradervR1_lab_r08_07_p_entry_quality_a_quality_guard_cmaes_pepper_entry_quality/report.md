# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r08_07_p_entry_quality_a_quality_guard_cmaes_pepper_entry_quality`
- Bots: TradervR1_lab_r08_07_p_entry_quality_a_quality_guard_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r08_07_p_entry_quality_a_quality_guard_best

- Combined total PnL: `290979.0000`
- Day -1: `96483.0000`
- Day -2: `96715.0000`
- Day 0: `97781.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r08_07_p_entry_quality_a_quality_guard_best

- Overall samples: `6` | mean `127654.25` | p10 `-15499.5` | cvar10 `-29454.0` | std `126102.9615`
- Profile `all`: count `6`, mean `127654.25`, p10 `-15499.5`, cvar10 `-29454.0`
- Profile `plausible`: count `6`, mean `127654.25`, p10 `-15499.5`, cvar10 `-29454.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52605.0`, p10 `-13042.2`, cvar10 `-29454.0`
- `bootstrap_path`: count `2`, mean `41312.0`, p10 `7026.4`, cvar10 `-1545.0`
- `original_noise`: count `2`, mean `289045.75`, p10 `288295.95`, cvar10 `288108.5`

## Comparison

- Primary: `TradervR1_lab_r08_07_p_entry_quality_a_quality_guard_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2002.8333`
- Median delta: `3462.75`
- P10 delta: `-1158.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-1158.25`, p10 delta `-4148.45`, win rate `0.5`
- `bootstrap_path`: mean delta `3580.5`, p10 delta `3537.7`, win rate `1.0`
- `original_noise`: mean delta `3586.25`, p10 delta `3436.05`, win rate `1.0`

- Profile `all`: mean delta `2002.8333`, p10 delta `-1158.25`, win rate `0.8333`
- Profile `plausible`: mean delta `2002.8333`, p10 delta `-1158.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

