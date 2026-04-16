# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r16_02_p_entry_quality`
- Bots: TradervR1_lab_r16_02_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r16_02_p_entry_quality

- Combined total PnL: `289313.0000`
- Day -1: `96028.0000`
- Day -2: `96110.0000`
- Day 0: `97175.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r16_02_p_entry_quality

- Overall samples: `6` | mean `125960.4167` | p10 `-18090.75` | cvar10 `-32861.0` | std `126343.1577`
- Profile `all`: count `6`, mean `125960.4167`, p10 `-18090.75`, cvar10 `-32861.0`
- Profile `plausible`: count `6`, mean `125960.4167`, p10 `-18090.75`, cvar10 `-32861.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51255.25`, p10 `-16037.75`, cvar10 `-32861.0`
- `bootstrap_path`: count `2`, mean `39629.25`, p10 `5269.45`, cvar10 `-3320.5`
- `original_noise`: count `2`, mean `286996.75`, p10 `286228.15`, cvar10 `286036.0`

## Comparison

- Primary: `TradervR1_lab_r16_02_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `309.0`
- Median delta: `1803.5`
- P10 delta: `-3488.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-2508.0`, p10 delta `-7144.0`, win rate `0.5`
- `bootstrap_path`: mean delta `1897.75`, p10 delta `1866.35`, win rate `1.0`
- `original_noise`: mean delta `1537.25`, p10 delta `1368.25`, win rate `1.0`

- Profile `all`: mean delta `309.0`, p10 delta `-3488.5`, win rate `0.8333`
- Profile `plausible`: mean delta `309.0`, p10 delta `-3488.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

