# Monte Carlo Robustness Report

- Output name: `round1_tradervr1_34_1_mc_heavy`
- Bots: TradervR1_34_1.py

## Families

- `original_noise`: Original historical path with very mild execution-noise perturbations.
- `bootstrap_path`: Block-bootstrap of the historical path with no fill perturbation.
- `bootstrap_balanced`: Block-bootstrap with calibrated mild-to-moderate execution degradation.
- `bootstrap_stress`: Block-bootstrap with stressed execution assumptions.

## Baseline Replay

### TradervR1_34_1

- Combined total PnL: `191012.5000`
- Day -1: `95486.0000`
- Day -2: `95526.5000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `32` | mean `174166.7812` | p10 `14207.6` | cvar10 `2797.375` | std `130034.086`
- Profile `all`: count `32`, mean `174166.7812`, p10 `14207.6`, cvar10 `2797.375`
- Profile `plausible`: count `24`, mean `132030.7292`, p10 `6252.3`, cvar10 `-615.5`
- Profile `stress`: count `8`, mean `300574.9375`, p10 `131140.5`, cvar10 `128267.0`
- `bootstrap_balanced`: count `8`, mean `107429.3125`, p10 `6996.25`, cvar10 `-7096.5`
- `bootstrap_path`: count `8`, mean `98661.5625`, p10 `2913.0`, cvar10 `1905.0`
- `bootstrap_stress`: count `8`, mean `300574.9375`, p10 `131140.5`, cvar10 `128267.0`
- `original_noise`: count `8`, mean `190001.3125`, p10 `189386.1`, cvar10 `189104.0`

