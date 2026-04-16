# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r13_08_a_local_fair_blend`
- Bots: TradervR1_lab_r13_08_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r13_08_a_local_fair_blend

- Combined total PnL: `288313.5000`
- Day -1: `95832.0000`
- Day -2: `95761.5000`
- Day 0: `96720.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r13_08_a_local_fair_blend

- Overall samples: `6` | mean `126189.0` | p10 `-16121.25` | cvar10 `-28767.0` | std `125255.4639`
- Profile `all`: count `6`, mean `126189.0`, p10 `-16121.25`, cvar10 `-28767.0`
- Profile `plausible`: count `6`, mean `126189.0`, p10 `-16121.25`, cvar10 `-28767.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53302.75`, p10 `-12353.05`, cvar10 `-28767.0`
- `bootstrap_path`: count `2`, mean `39029.25`, p10 `5025.45`, cvar10 `-3475.5`
- `original_noise`: count `2`, mean `286235.0`, p10 `285543.8`, cvar10 `285371.0`

## Comparison

- Primary: `TradervR1_lab_r13_08_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `537.5833`
- Median delta: `891.0`
- P10 delta: `-1774.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-460.5`, p10 delta `-3459.3`, win rate `0.5`
- `bootstrap_path`: mean delta `1297.75`, p10 delta `973.15`, win rate `1.0`
- `original_noise`: mean delta `775.5`, p10 delta `683.9`, win rate `1.0`

- Profile `all`: mean delta `537.5833`, p10 delta `-1774.0`, win rate `0.8333`
- Profile `plausible`: mean delta `537.5833`, p10 delta `-1774.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

