# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r09_06_p_carry_defense_a_quality_guard`
- Bots: TradervR1_lab_r09_06_p_carry_defense_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r09_06_p_carry_defense_a_quality_guard

- Combined total PnL: `289998.5000`
- Day -1: `96228.0000`
- Day -2: `96462.5000`
- Day 0: `97308.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r09_06_p_carry_defense_a_quality_guard

- Overall samples: `6` | mean `126836.4167` | p10 `-16844.75` | cvar10 `-31397.0` | std `126128.2375`
- Profile `all`: count `6`, mean `126836.4167`, p10 `-16844.75`, cvar10 `-31397.0`
- Profile `plausible`: count `6`, mean `126836.4167`, p10 `-16844.75`, cvar10 `-31397.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `52317.25`, p10 `-14654.15`, cvar10 `-31397.0`
- `bootstrap_path`: count `2`, mean `40491.75`, p10 `6264.35`, cvar10 `-2292.5`
- `original_noise`: count `2`, mean `287700.25`, p10 `287008.05`, cvar10 `286835.0`

## Comparison

- Primary: `TradervR1_lab_r09_06_p_carry_defense_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1185.0`
- Median delta: `2495.25`
- P10 delta: `-2357.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-1446.0`, p10 delta `-5760.4`, win rate `0.5`
- `bootstrap_path`: mean delta `2760.25`, p10 delta `2659.25`, win rate `1.0`
- `original_noise`: mean delta `2240.75`, p10 delta `2148.15`, win rate `1.0`

- Profile `all`: mean delta `1185.0`, p10 delta `-2357.0`, win rate `0.8333`
- Profile `plausible`: mean delta `1185.0`, p10 delta `-2357.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

