# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r01_01_a_local_fair_blend`
- Bots: TradervR1_lab_r01_01_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r01_01_a_local_fair_blend

- Combined total PnL: `287969.5000`
- Day -1: `95732.0000`
- Day -2: `95711.5000`
- Day 0: `96526.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `3` | mean `85490.6667` | p10 `-20682.2` | cvar10 `-24558.0` | std `142149.624`
- Profile `all`: count `3`, mean `85490.6667`, p10 `-20682.2`, cvar10 `-24558.0`
- Profile `plausible`: count `3`, mean `85490.6667`, p10 `-20682.2`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `1`, mean `-24558.0`, p10 `-24558.0`, cvar10 `-24558.0`
- `bootstrap_path`: count `1`, mean `-5179.0`, p10 `-5179.0`, cvar10 `-5179.0`
- `original_noise`: count `1`, mean `286209.0`, p10 `286209.0`, cvar10 `286209.0`

### TradervR1_lab_r01_01_a_local_fair_blend

- Overall samples: `3` | mean `83174.6667` | p10 `-27487.3` | cvar10 `-33157.0` | std `144935.2101`
- Profile `all`: count `3`, mean `83174.6667`, p10 `-27487.3`, cvar10 `-33157.0`
- Profile `plausible`: count `3`, mean `83174.6667`, p10 `-27487.3`, cvar10 `-33157.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `1`, mean `-33157.0`, p10 `-33157.0`, cvar10 `-33157.0`
- `bootstrap_path`: count `1`, mean `-4808.5`, p10 `-4808.5`, cvar10 `-4808.5`
- `original_noise`: count `1`, mean `287489.5`, p10 `287489.5`, cvar10 `287489.5`

## Comparison

- Primary: `TradervR1_lab_r01_01_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `3`
- Mean delta: `-2316.0`
- Median delta: `370.5`
- P10 delta: `-6805.1`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-8599.0`, p10 delta `-8599.0`, win rate `0.0`
- `bootstrap_path`: mean delta `370.5`, p10 delta `370.5`, win rate `1.0`
- `original_noise`: mean delta `1280.5`, p10 delta `1280.5`, win rate `1.0`

- Profile `all`: mean delta `-2316.0`, p10 delta `-6805.1`, win rate `0.6667`
- Profile `plausible`: mean delta `-2316.0`, p10 delta `-6805.1`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

