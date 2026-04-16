# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r09_07_p_carry_defense_a_quality_guard`
- Bots: TradervR1_lab_r09_07_p_carry_defense_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r09_07_p_carry_defense_a_quality_guard

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

### TradervR1_lab_r09_07_p_carry_defense_a_quality_guard

- Overall samples: `6` | mean `125807.25` | p10 `-17628.25` | cvar10 `-32964.0` | std `126559.1445`
- Profile `all`: count `6`, mean `125807.25`, p10 `-17628.25`, cvar10 `-32964.0`
- Profile `plausible`: count `6`, mean `125807.25`, p10 `-17628.25`, cvar10 `-32964.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `48872.25`, p10 `-16596.75`, cvar10 `-32964.0`
- `bootstrap_path`: count `2`, mean `40491.75`, p10 `6264.35`, cvar10 `-2292.5`
- `original_noise`: count `2`, mean `288057.75`, p10 `287244.35`, cvar10 `287041.0`

## Comparison

- Primary: `TradervR1_lab_r09_07_p_carry_defense_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `155.8333`
- Median delta: `2482.5`
- P10 delta: `-4891.0`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-4891.0`, p10 delta `-7703.0`, win rate `0.0`
- `bootstrap_path`: mean delta `2760.25`, p10 delta `2659.25`, win rate `1.0`
- `original_noise`: mean delta `2598.25`, p10 delta `2384.45`, win rate `1.0`

- Profile `all`: mean delta `155.8333`, p10 delta `-4891.0`, win rate `0.6667`
- Profile `plausible`: mean delta `155.8333`, p10 delta `-4891.0`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

