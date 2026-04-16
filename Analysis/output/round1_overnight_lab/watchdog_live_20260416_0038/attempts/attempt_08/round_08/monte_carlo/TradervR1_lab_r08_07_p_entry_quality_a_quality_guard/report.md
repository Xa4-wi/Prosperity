# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r08_07_p_entry_quality_a_quality_guard`
- Bots: TradervR1_lab_r08_07_p_entry_quality_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r08_07_p_entry_quality_a_quality_guard

- Combined total PnL: `291848.0000`
- Day -1: `96904.0000`
- Day -2: `97101.0000`
- Day 0: `97843.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r08_07_p_entry_quality_a_quality_guard

- Overall samples: `6` | mean `127236.75` | p10 `-17109.5` | cvar10 `-34529.0` | std `127189.9482`
- Profile `all`: count `6`, mean `127236.75`, p10 `-17109.5`, cvar10 `-34529.0`
- Profile `plausible`: count `6`, mean `127236.75`, p10 `-17109.5`, cvar10 `-34529.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `48937.75`, p10 `-17835.65`, cvar10 `-34529.0`
- `bootstrap_path`: count `2`, mean `42761.0`, p10 `8800.2`, cvar10 `310.0`
- `original_noise`: count `2`, mean `290011.5`, p10 `289413.9`, cvar10 `289264.5`

## Comparison

- Primary: `TradervR1_lab_r08_07_p_entry_quality_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1585.3333`
- Median delta: `4552.0`
- P10 delta: `-4825.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-4825.5`, p10 delta `-8941.9`, win rate `0.5`
- `bootstrap_path`: mean delta `5029.5`, p10 delta `4661.9`, win rate `1.0`
- `original_noise`: mean delta `4552.0`, p10 delta `4550.0`, win rate `1.0`

- Profile `all`: mean delta `1585.3333`, p10 delta `-4825.5`, win rate `0.8333`
- Profile `plausible`: mean delta `1585.3333`, p10 delta `-4825.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

