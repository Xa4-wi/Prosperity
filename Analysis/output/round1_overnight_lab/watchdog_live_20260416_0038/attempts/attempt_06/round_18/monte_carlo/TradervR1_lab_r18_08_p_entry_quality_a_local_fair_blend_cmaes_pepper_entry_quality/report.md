# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r18_08_p_entry_quality_a_local_fair_blend_cmaes_pepper_entry_quality`
- Bots: TradervR1_lab_r18_08_p_entry_quality_a_local_fair_blend_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r18_08_p_entry_quality_a_local_fair_blend_best

- Combined total PnL: `290460.0000`
- Day -1: `96403.0000`
- Day -2: `96683.0000`
- Day 0: `97374.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r18_08_p_entry_quality_a_local_fair_blend_best

- Overall samples: `6` | mean `128260.5833` | p10 `-13886.75` | cvar10 `-26920.0` | std `125378.0765`
- Profile `all`: count `6`, mean `128260.5833`, p10 `-13886.75`, cvar10 `-26920.0`
- Profile `plausible`: count `6`, mean `128260.5833`, p10 `-13886.75`, cvar10 `-26920.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `54417.75`, p10 `-10652.45`, cvar10 `-26920.0`
- `bootstrap_path`: count `2`, mean `41560.75`, p10 `7629.35`, cvar10 `-853.5`
- `original_noise`: count `2`, mean `288803.25`, p10 `288175.85`, cvar10 `288019.0`

## Comparison

- Primary: `TradervR1_lab_r18_08_p_entry_quality_a_local_fair_blend_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2609.1667`
- Median delta: `3355.75`
- P10 delta: `473.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `654.5`, p10 delta `-1758.7`, win rate `0.5`
- `bootstrap_path`: mean delta `3829.25`, p10 delta `3432.25`, win rate `1.0`
- `original_noise`: mean delta `3343.75`, p10 delta `3315.95`, win rate `1.0`

- Profile `all`: mean delta `2609.1667`, p10 delta `473.5`, win rate `0.8333`
- Profile `plausible`: mean delta `2609.1667`, p10 delta `473.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

