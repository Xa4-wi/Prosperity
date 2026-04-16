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

- Combined total PnL: `290663.5000`
- Day -1: `96374.0000`
- Day -2: `96669.5000`
- Day 0: `97620.0000`

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

- Overall samples: `6` | mean `128482.3333` | p10 `-15890.25` | cvar10 `-30092.0` | std `126113.2038`
- Profile `all`: count `6`, mean `128482.3333`, p10 `-15890.25`, cvar10 `-30092.0`
- Profile `plausible`: count `6`, mean `128482.3333`, p10 `-15890.25`, cvar10 `-30092.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `55894.75`, p10 `-12894.65`, cvar10 `-30092.0`
- `bootstrap_path`: count `2`, mean `41118.25`, p10 `6872.85`, cvar10 `-1688.5`
- `original_noise`: count `2`, mean `288434.0`, p10 `287452.4`, cvar10 `287207.0`

## Comparison

- Primary: `TradervR1_lab_r08_07_p_entry_quality_a_quality_guard_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2830.9167`
- Median delta: `3367.5`
- P10 delta: `-1518.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `2131.5`, p10 delta `-4000.9`, win rate `0.5`
- `bootstrap_path`: mean delta `3386.75`, p10 delta `3303.75`, win rate `1.0`
- `original_noise`: mean delta `2974.5`, p10 delta `2592.5`, win rate `1.0`

- Profile `all`: mean delta `2830.9167`, p10 delta `-1518.5`, win rate `0.8333`
- Profile `plausible`: mean delta `2830.9167`, p10 delta `-1518.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

