# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r04_07_a_quality_guard`
- Bots: TradervR1_lab_r04_07_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r04_07_a_quality_guard

- Combined total PnL: `289499.0000`
- Day -1: `96115.0000`
- Day -2: `96096.0000`
- Day 0: `97288.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r04_07_a_quality_guard

- Overall samples: `6` | mean `126791.75` | p10 `-15712.5` | cvar10 `-28328.0` | std `125702.6959`
- Profile `all`: count `6`, mean `126791.75`, p10 `-15712.5`, cvar10 `-28328.0`
- Profile `plausible`: count `6`, mean `126791.75`, p10 `-15712.5`, cvar10 `-28328.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52855.0`, p10 `-12091.4`, cvar10 `-28328.0`
- `bootstrap_path`: count `2`, mean `39703.5`, p10 `5463.1`, cvar10 `-3097.0`
- `original_noise`: count `2`, mean `287816.75`, p10 `287064.55`, cvar10 `286876.5`

## Comparison

- Primary: `TradervR1_lab_r04_07_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1140.3333`
- Median delta: `2017.75`
- P10 delta: `-954.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-908.25`, p10 delta `-3197.65`, win rate `0.5`
- `bootstrap_path`: mean delta `1972.0`, p10 delta `1884.0`, win rate `1.0`
- `original_noise`: mean delta `2357.25`, p10 delta `2204.65`, win rate `1.0`

- Profile `all`: mean delta `1140.3333`, p10 delta `-954.0`, win rate `0.8333`
- Profile `plausible`: mean delta `1140.3333`, p10 delta `-954.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

