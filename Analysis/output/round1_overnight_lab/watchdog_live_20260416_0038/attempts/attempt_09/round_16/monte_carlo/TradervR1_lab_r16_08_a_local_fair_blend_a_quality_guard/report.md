# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r16_08_a_local_fair_blend_a_quality_guard`
- Bots: TradervR1_lab_r16_08_a_local_fair_blend_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r16_08_a_local_fair_blend_a_quality_guard

- Combined total PnL: `289797.0000`
- Day -1: `96108.0000`
- Day -2: `96120.0000`
- Day 0: `97569.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r16_08_a_local_fair_blend_a_quality_guard

- Overall samples: `6` | mean `126382.5` | p10 `-16225.5` | cvar10 `-30481.0` | std `125863.2379`
- Profile `all`: count `6`, mean `126382.5`, p10 `-16225.5`, cvar10 `-30481.0`
- Profile `plausible`: count `6`, mean `126382.5`, p10 `-16225.5`, cvar10 `-30481.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51007.75`, p10 `-14183.25`, cvar10 `-30481.0`
- `bootstrap_path`: count `2`, mean `40454.0`, p10 `6514.8`, cvar10 `-1970.0`
- `original_noise`: count `2`, mean `287685.75`, p10 `287039.15`, cvar10 `286877.5`

## Comparison

- Primary: `TradervR1_lab_r16_08_a_local_fair_blend_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `731.0833`
- Median delta: `2201.75`
- P10 delta: `-2755.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-2755.5`, p10 delta `-5289.5`, win rate `0.5`
- `bootstrap_path`: mean delta `2722.5`, p10 delta `2333.3`, win rate `1.0`
- `original_noise`: mean delta `2226.25`, p10 delta `2179.25`, win rate `1.0`

- Profile `all`: mean delta `731.0833`, p10 delta `-2755.5`, win rate `0.8333`
- Profile `plausible`: mean delta `731.0833`, p10 delta `-2755.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

