# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r01_03_p_entry_quality_a_quality_guard`
- Bots: TradervR1_lab_r01_03_p_entry_quality_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r01_03_p_entry_quality_a_quality_guard

- Combined total PnL: `288926.0000`
- Day -1: `95897.0000`
- Day -2: `95972.0000`
- Day 0: `97057.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `3` | mean `85490.6667` | p10 `-20682.2` | cvar10 `-24558.0` | std `142149.624`
- Profile `all`: count `3`, mean `85490.6667`, p10 `-20682.2`, cvar10 `-24558.0`
- Profile `plausible`: count `3`, mean `85490.6667`, p10 `-20682.2`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `1`, mean `-24558.0`, p10 `-24558.0`, cvar10 `-24558.0`
- `bootstrap_path`: count `1`, mean `-5179.0`, p10 `-5179.0`, cvar10 `-5179.0`
- `original_noise`: count `1`, mean `286209.0`, p10 `286209.0`, cvar10 `286209.0`

### TradervR1_lab_r01_03_p_entry_quality_a_quality_guard

- Overall samples: `3` | mean `86162.5` | p10 `-21054.1` | cvar10 `-25372.0` | std `142739.8994`
- Profile `all`: count `3`, mean `86162.5`, p10 `-21054.1`, cvar10 `-25372.0`
- Profile `plausible`: count `3`, mean `86162.5`, p10 `-21054.1`, cvar10 `-25372.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `1`, mean `-25372.0`, p10 `-25372.0`, cvar10 `-25372.0`
- `bootstrap_path`: count `1`, mean `-3782.5`, p10 `-3782.5`, cvar10 `-3782.5`
- `original_noise`: count `1`, mean `287642.0`, p10 `287642.0`, cvar10 `287642.0`

## Comparison

- Primary: `TradervR1_lab_r01_03_p_entry_quality_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `3`
- Mean delta: `671.8333`
- Median delta: `1396.5`
- P10 delta: `-371.9`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-814.0`, p10 delta `-814.0`, win rate `0.0`
- `bootstrap_path`: mean delta `1396.5`, p10 delta `1396.5`, win rate `1.0`
- `original_noise`: mean delta `1433.0`, p10 delta `1433.0`, win rate `1.0`

- Profile `all`: mean delta `671.8333`, p10 delta `-371.9`, win rate `0.6667`
- Profile `plausible`: mean delta `671.8333`, p10 delta `-371.9`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

