# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r10_08_a_quality_guard_p_entry_quality`
- Bots: TradervR1_lab_r10_08_a_quality_guard_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r10_08_a_quality_guard_p_entry_quality

- Combined total PnL: `289524.0000`
- Day -1: `96085.0000`
- Day -2: `96108.0000`
- Day 0: `97331.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r10_08_a_quality_guard_p_entry_quality

- Overall samples: `6` | mean `126721.8333` | p10 `-14896.25` | cvar10 `-26630.0` | std `125183.7047`
- Profile `all`: count `6`, mean `126721.8333`, p10 `-14896.25`, cvar10 `-26630.0`
- Profile `plausible`: count `6`, mean `126721.8333`, p10 `-14896.25`, cvar10 `-26630.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52875.75`, p10 `-10728.85`, cvar10 `-26630.0`
- `bootstrap_path`: count `2`, mean `39823.75`, p10 `5434.75`, cvar10 `-3162.5`
- `original_noise`: count `2`, mean `287466.0`, p10 `286801.6`, cvar10 `286635.5`

## Comparison

- Primary: `TradervR1_lab_r10_08_a_quality_guard_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1070.4167`
- Median delta: `1971.0`
- P10 delta: `-887.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-887.5`, p10 delta `-1835.1`, win rate `0.5`
- `bootstrap_path`: mean delta `2092.25`, p10 delta `2031.65`, win rate `1.0`
- `original_noise`: mean delta `2006.5`, p10 delta `1941.7`, win rate `1.0`

- Profile `all`: mean delta `1070.4167`, p10 delta `-887.5`, win rate `0.8333`
- Profile `plausible`: mean delta `1070.4167`, p10 delta `-887.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

