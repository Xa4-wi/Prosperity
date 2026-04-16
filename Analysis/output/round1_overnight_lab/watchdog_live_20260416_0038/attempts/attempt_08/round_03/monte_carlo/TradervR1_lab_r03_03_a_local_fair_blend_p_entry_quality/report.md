# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality`
- Bots: TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality

- Combined total PnL: `286623.0000`
- Day -1: `95316.0000`
- Day -2: `95243.0000`
- Day 0: `96064.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality

- Overall samples: `6` | mean `124514.0833` | p10 `-14957.75` | cvar10 `-23004.0` | std `123977.2486`
- Profile `all`: count `6`, mean `124514.0833`, p10 `-14957.75`, cvar10 `-23004.0`
- Profile `plausible`: count `6`, mean `124514.0833`, p10 `-14957.75`, cvar10 `-23004.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52620.5`, p10 `-7879.1`, cvar10 `-23004.0`
- `bootstrap_path`: count `2`, mean `36449.75`, p10 `1760.75`, cvar10 `-6911.5`
- `original_noise`: count `2`, mean `284472.0`, p10 `283573.2`, cvar10 `283348.5`

## Comparison

- Primary: `TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1137.3333`
- Median delta: `-1096.25`
- P10 delta: `-2786.0`
- Win rate: `0.1667`

- `bootstrap_balanced`: mean delta `-1142.75`, p10 delta `-3300.15`, win rate `0.5`
- `bootstrap_path`: mean delta `-1281.75`, p10 delta `-1642.35`, win rate `0.0`
- `original_noise`: mean delta `-987.5`, p10 delta `-1286.7`, win rate `0.0`

- Profile `all`: mean delta `-1137.3333`, p10 delta `-2786.0`, win rate `0.1667`
- Profile `plausible`: mean delta `-1137.3333`, p10 delta `-2786.0`, win rate `0.1667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

