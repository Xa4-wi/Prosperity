# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r10_05_p_carry_defense`
- Bots: TradervR1_lab_r10_05_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r10_05_p_carry_defense

- Combined total PnL: `288932.0000`
- Day -1: `95897.0000`
- Day -2: `95963.0000`
- Day 0: `97072.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r10_05_p_carry_defense

- Overall samples: `6` | mean `125358.0` | p10 `-18489.75` | cvar10 `-33377.0` | std `126364.9044`
- Profile `all`: count `6`, mean `125358.0`, p10 `-18489.75`, cvar10 `-33377.0`
- Profile `plausible`: count `6`, mean `125358.0`, p10 `-18489.75`, cvar10 `-33377.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50395.25`, p10 `-16622.55`, cvar10 `-33377.0`
- `bootstrap_path`: count `2`, mean `39075.75`, p10 `4933.15`, cvar10 `-3602.5`
- `original_noise`: count `2`, mean `286603.0`, p10 `285781.8`, cvar10 `285576.5`

## Comparison

- Primary: `TradervR1_lab_r10_05_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-293.4167`
- Median delta: `1266.25`
- P10 delta: `-3976.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-3368.0`, p10 delta `-7728.8`, win rate `0.5`
- `bootstrap_path`: mean delta `1344.25`, p10 delta `1158.45`, win rate `1.0`
- `original_noise`: mean delta `1143.5`, p10 delta `921.9`, win rate `1.0`

- Profile `all`: mean delta `-293.4167`, p10 delta `-3976.25`, win rate `0.8333`
- Profile `plausible`: mean delta `-293.4167`, p10 delta `-3976.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

