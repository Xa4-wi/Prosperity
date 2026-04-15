# Monte Carlo Robustness Report

- Output name: `round1_tradervr1_34_1_mc_quick`
- Bots: TradervR1_34_1.py

## Families

- `original_noise`: Original historical path with very mild execution-noise perturbations.
- `bootstrap_path`: Block-bootstrap of the historical path with no fill perturbation.
- `bootstrap_balanced`: Block-bootstrap with calibrated mild-to-moderate execution degradation.

## Baseline Replay

### TradervR1_34_1

- Combined total PnL: `191012.5000`
- Day -1: `95486.0000`
- Day -2: `95526.5000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `76335.4167` | p10 `-2595.75` | cvar10 `-7096.5` | std `84017.0367`
- Profile `all`: count `6`, mean `76335.4167`, p10 `-2595.75`, cvar10 `-7096.5`
- Profile `plausible`: count `6`, mean `76335.4167`, p10 `-2595.75`, cvar10 `-7096.5`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `2969.75`, p10 `-5083.25`, cvar10 `-7096.5`
- `bootstrap_path`: count `2`, mean `36103.5`, p10 `8744.7`, cvar10 `1905.0`
- `original_noise`: count `2`, mean `189933.0`, p10 `189592.2`, cvar10 `189507.0`

