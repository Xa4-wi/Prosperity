# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r15_07_a_local_fair_blend_p_entry_quality`
- Bots: TradervR1_lab_r15_07_a_local_fair_blend_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r15_07_a_local_fair_blend_p_entry_quality

- Combined total PnL: `288179.5000`
- Day -1: `95884.0000`
- Day -2: `95843.5000`
- Day 0: `96452.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r15_07_a_local_fair_blend_p_entry_quality

- Overall samples: `6` | mean `125374.0833` | p10 `-18089.25` | cvar10 `-31738.0` | std `126102.9319`
- Profile `all`: count `6`, mean `125374.0833`, p10 `-18089.25`, cvar10 `-31738.0`
- Profile `plausible`: count `6`, mean `125374.0833`, p10 `-18089.25`, cvar10 `-31738.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50812.75`, p10 `-15227.85`, cvar10 `-31738.0`
- `bootstrap_path`: count `2`, mean `38796.25`, p10 `4206.85`, cvar10 `-4440.5`
- `original_noise`: count `2`, mean `286513.25`, p10 `285771.05`, cvar10 `285585.5`

## Comparison

- Primary: `TradervR1_lab_r15_07_a_local_fair_blend_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-277.3333`
- Median delta: `1053.75`
- P10 delta: `-3220.75`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-2950.5`, p10 delta `-6334.1`, win rate `0.5`
- `bootstrap_path`: mean delta `1064.75`, p10 delta `803.75`, win rate `1.0`
- `original_noise`: mean delta `1053.75`, p10 delta `911.15`, win rate `1.0`

- Profile `all`: mean delta `-277.3333`, p10 delta `-3220.75`, win rate `0.8333`
- Profile `plausible`: mean delta `-277.3333`, p10 delta `-3220.75`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

