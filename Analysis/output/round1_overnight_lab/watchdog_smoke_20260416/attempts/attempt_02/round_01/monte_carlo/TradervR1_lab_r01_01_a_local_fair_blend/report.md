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

- Overall samples: `3` | mean `84455.1667` | p10 `-23844.9` | cvar10 `-28604.0` | std `143393.2893`
- Profile `all`: count `3`, mean `84455.1667`, p10 `-23844.9`, cvar10 `-28604.0`
- Profile `plausible`: count `3`, mean `84455.1667`, p10 `-23844.9`, cvar10 `-28604.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `1`, mean `-28604.0`, p10 `-28604.0`, cvar10 `-28604.0`
- `bootstrap_path`: count `1`, mean `-4808.5`, p10 `-4808.5`, cvar10 `-4808.5`
- `original_noise`: count `1`, mean `286778.0`, p10 `286778.0`, cvar10 `286778.0`

## Comparison

- Primary: `TradervR1_lab_r01_01_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `3`
- Mean delta: `-1035.5`
- Median delta: `370.5`
- P10 delta: `-3162.7`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-4046.0`, p10 delta `-4046.0`, win rate `0.0`
- `bootstrap_path`: mean delta `370.5`, p10 delta `370.5`, win rate `1.0`
- `original_noise`: mean delta `569.0`, p10 delta `569.0`, win rate `1.0`

- Profile `all`: mean delta `-1035.5`, p10 delta `-3162.7`, win rate `0.6667`
- Profile `plausible`: mean delta `-1035.5`, p10 delta `-3162.7`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

