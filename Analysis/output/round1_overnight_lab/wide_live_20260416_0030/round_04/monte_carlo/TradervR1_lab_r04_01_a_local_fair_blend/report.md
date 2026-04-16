# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r04_01_a_local_fair_blend`
- Bots: TradervR1_lab_r04_01_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r04_01_a_local_fair_blend

- Combined total PnL: `292445.5000`
- Day -1: `97159.0000`
- Day -2: `97249.5000`
- Day 0: `98037.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r04_01_a_local_fair_blend

- Overall samples: `6` | mean `131226.8333` | p10 `-8511.75` | cvar10 `-18244.0` | std `123966.2342`
- Profile `all`: count `6`, mean `131226.8333`, p10 `-8511.75`, cvar10 `-18244.0`
- Profile `plausible`: count `6`, mean `131226.8333`, p10 `-8511.75`, cvar10 `-18244.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `59261.25`, p10 `-2742.95`, cvar10 `-18244.0`
- `bootstrap_path`: count `2`, mean `43668.75`, p10 `9710.15`, cvar10 `1220.5`
- `original_noise`: count `2`, mean `290750.5`, p10 `290080.9`, cvar10 `289913.5`

## Comparison

- Primary: `TradervR1_lab_r04_01_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `5575.4167`
- Median delta: `5426.75`
- P10 delta: `4942.75`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `5498.0`, p10 delta `4845.2`, win rate `1.0`
- `bootstrap_path`: mean delta `5937.25`, p10 delta `5567.45`, win rate `1.0`
- `original_noise`: mean delta `5291.0`, p10 delta `5221.0`, win rate `1.0`

- Profile `all`: mean delta `5575.4167`, p10 delta `4942.75`, win rate `1.0`
- Profile `plausible`: mean delta `5575.4167`, p10 delta `4942.75`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

