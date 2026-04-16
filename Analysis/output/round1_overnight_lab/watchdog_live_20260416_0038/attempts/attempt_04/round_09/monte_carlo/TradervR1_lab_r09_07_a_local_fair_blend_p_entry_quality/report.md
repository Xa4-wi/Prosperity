# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r09_07_a_local_fair_blend_p_entry_quality`
- Bots: TradervR1_lab_r09_07_a_local_fair_blend_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r09_07_a_local_fair_blend_p_entry_quality

- Combined total PnL: `288398.5000`
- Day -1: `95715.0000`
- Day -2: `95807.5000`
- Day 0: `96876.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r09_07_a_local_fair_blend_p_entry_quality

- Overall samples: `6` | mean `125372.5` | p10 `-17803.75` | cvar10 `-32559.0` | std `126013.0751`
- Profile `all`: count `6`, mean `125372.5`, p10 `-17803.75`, cvar10 `-32559.0`
- Profile `plausible`: count `6`, mean `125372.5`, p10 `-17803.75`, cvar10 `-32559.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50111.25`, p10 `-16024.95`, cvar10 `-32559.0`
- `bootstrap_path`: count `2`, mean `39526.25`, p10 `5466.45`, cvar10 `-3048.5`
- `original_noise`: count `2`, mean `286480.0`, p10 `285518.4`, cvar10 `285278.0`

## Comparison

- Primary: `TradervR1_lab_r09_07_a_local_fair_blend_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-278.9167`
- Median delta: `1078.0`
- P10 delta: `-3716.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-3652.0`, p10 delta `-7131.2`, win rate `0.5`
- `bootstrap_path`: mean delta `1794.75`, p10 delta `1526.15`, win rate `1.0`
- `original_noise`: mean delta `1020.5`, p10 delta `658.5`, win rate `1.0`

- Profile `all`: mean delta `-278.9167`, p10 delta `-3716.5`, win rate `0.8333`
- Profile `plausible`: mean delta `-278.9167`, p10 delta `-3716.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

