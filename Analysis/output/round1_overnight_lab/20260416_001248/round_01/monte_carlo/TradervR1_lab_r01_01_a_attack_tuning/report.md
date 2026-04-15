# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r01_01_a_attack_tuning`
- Bots: TradervR1_lab_r01_01_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r01_01_a_attack_tuning

- Combined total PnL: `288820.0000`
- Day -1: `95873.0000`
- Day -2: `95910.0000`
- Day 0: `97037.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `3` | mean `85490.6667` | p10 `-20682.2` | cvar10 `-24558.0` | std `142149.624`
- Profile `all`: count `3`, mean `85490.6667`, p10 `-20682.2`, cvar10 `-24558.0`
- Profile `plausible`: count `3`, mean `85490.6667`, p10 `-20682.2`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `1`, mean `-24558.0`, p10 `-24558.0`, cvar10 `-24558.0`
- `bootstrap_path`: count `1`, mean `-5179.0`, p10 `-5179.0`, cvar10 `-5179.0`
- `original_noise`: count `1`, mean `286209.0`, p10 `286209.0`, cvar10 `286209.0`

### TradervR1_lab_r01_01_a_attack_tuning

- Overall samples: `3` | mean `84396.1667` | p10 `-25343.1` | cvar10 `-30797.0` | std `144056.1057`
- Profile `all`: count `3`, mean `84396.1667`, p10 `-25343.1`, cvar10 `-30797.0`
- Profile `plausible`: count `3`, mean `84396.1667`, p10 `-25343.1`, cvar10 `-30797.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `1`, mean `-30797.0`, p10 `-30797.0`, cvar10 `-30797.0`
- `bootstrap_path`: count `1`, mean `-3527.5`, p10 `-3527.5`, cvar10 `-3527.5`
- `original_noise`: count `1`, mean `287513.0`, p10 `287513.0`, cvar10 `287513.0`

## Comparison

- Primary: `TradervR1_lab_r01_01_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `3`
- Mean delta: `-1094.5`
- Median delta: `1304.0`
- P10 delta: `-4730.4`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-6239.0`, p10 delta `-6239.0`, win rate `0.0`
- `bootstrap_path`: mean delta `1651.5`, p10 delta `1651.5`, win rate `1.0`
- `original_noise`: mean delta `1304.0`, p10 delta `1304.0`, win rate `1.0`

- Profile `all`: mean delta `-1094.5`, p10 delta `-4730.4`, win rate `0.6667`
- Profile `plausible`: mean delta `-1094.5`, p10 delta `-4730.4`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

