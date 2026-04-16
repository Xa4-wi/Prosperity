# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r07_03_p_carry_defense`
- Bots: TradervR1_lab_r07_03_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r07_03_p_carry_defense

- Combined total PnL: `289303.0000`
- Day -1: `96028.0000`
- Day -2: `96096.0000`
- Day 0: `97179.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r07_03_p_carry_defense

- Overall samples: `6` | mean `125889.3333` | p10 `-17425.75` | cvar10 `-31531.0` | std `126215.0304`
- Profile `all`: count `6`, mean `125889.3333`, p10 `-17425.75`, cvar10 `-31531.0`
- Profile `plausible`: count `6`, mean `125889.3333`, p10 `-17425.75`, cvar10 `-31531.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50767.75`, p10 `-15071.25`, cvar10 `-31531.0`
- `bootstrap_path`: count `2`, mean `39521.25`, p10 `5247.85`, cvar10 `-3320.5`
- `original_noise`: count `2`, mean `287379.0`, p10 `286763.8`, cvar10 `286610.0`

## Comparison

- Primary: `TradervR1_lab_r07_03_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `237.9167`
- Median delta: `1789.75`
- P10 delta: `-2995.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-2995.5`, p10 delta `-6177.5`, win rate `0.5`
- `bootstrap_path`: mean delta `1789.75`, p10 delta `1734.75`, win rate `1.0`
- `original_noise`: mean delta `1919.5`, p10 delta `1903.9`, win rate `1.0`

- Profile `all`: mean delta `237.9167`, p10 delta `-2995.5`, win rate `0.8333`
- Profile `plausible`: mean delta `237.9167`, p10 delta `-2995.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

