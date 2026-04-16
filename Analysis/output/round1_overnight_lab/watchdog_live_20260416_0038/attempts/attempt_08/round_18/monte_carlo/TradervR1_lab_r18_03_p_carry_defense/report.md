# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r18_03_p_carry_defense`
- Bots: TradervR1_lab_r18_03_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r18_03_p_carry_defense

- Combined total PnL: `287311.5000`
- Day -1: `95491.0000`
- Day -2: `95547.5000`
- Day 0: `96273.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r18_03_p_carry_defense

- Overall samples: `6` | mean `125562.6667` | p10 `-16959.5` | cvar10 `-28740.0` | std `125300.7277`
- Profile `all`: count `6`, mean `125562.6667`, p10 `-16959.5`, cvar10 `-28740.0`
- Profile `plausible`: count `6`, mean `125562.6667`, p10 `-16959.5`, cvar10 `-28740.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53589.75`, p10 `-12274.05`, cvar10 `-28740.0`
- `bootstrap_path`: count `2`, mean `37611.5`, p10 `3379.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285486.75`, p10 `284992.55`, cvar10 `284869.0`

## Comparison

- Primary: `TradervR1_lab_r18_03_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-88.75`
- Median delta: `-52.25`
- P10 delta: `-2211.0`
- Win rate: `0.3333`

- `bootstrap_balanced`: mean delta `-173.5`, p10 delta `-3380.3`, win rate `0.5`
- `bootstrap_path`: mean delta `-120.0`, p10 delta `-216.0`, win rate `0.0`
- `original_noise`: mean delta `27.25`, p10 delta `-78.15`, win rate `0.5`

- Profile `all`: mean delta `-88.75`, p10 delta `-2211.0`, win rate `0.3333`
- Profile `plausible`: mean delta `-88.75`, p10 delta `-2211.0`, win rate `0.3333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

