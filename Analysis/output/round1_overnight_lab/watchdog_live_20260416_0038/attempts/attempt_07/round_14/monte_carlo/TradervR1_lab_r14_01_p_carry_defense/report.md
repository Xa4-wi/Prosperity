# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r14_01_p_carry_defense`
- Bots: TradervR1_lab_r14_01_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r14_01_p_carry_defense

- Combined total PnL: `287283.5000`
- Day -1: `95491.0000`
- Day -2: `95517.5000`
- Day 0: `96275.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r14_01_p_carry_defense

- Overall samples: `6` | mean `124069.8333` | p10 `-19488.5` | cvar10 `-33798.0` | std `126243.8184`
- Profile `all`: count `6`, mean `124069.8333`, p10 `-19488.5`, cvar10 `-33798.0`
- Profile `plausible`: count `6`, mean `124069.8333`, p10 `-19488.5`, cvar10 `-33798.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49093.75`, p10 `-17219.65`, cvar10 `-33798.0`
- `bootstrap_path`: count `2`, mean `37727.5`, p10 `3402.3`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285388.25`, p10 `284850.45`, cvar10 `284716.0`

## Comparison

- Primary: `TradervR1_lab_r14_01_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1581.5833`
- Median delta: `-53.5`
- P10 delta: `-4694.25`
- Win rate: `0.1667`

- `bootstrap_balanced`: mean delta `-4669.5`, p10 delta `-8325.9`, win rate `0.0`
- `bootstrap_path`: mean delta `-4.0`, p10 delta `-7.2`, win rate `0.0`
- `original_noise`: mean delta `-71.25`, p10 delta `-133.05`, win rate `0.5`

- Profile `all`: mean delta `-1581.5833`, p10 delta `-4694.25`, win rate `0.1667`
- Profile `plausible`: mean delta `-1581.5833`, p10 delta `-4694.25`, win rate `0.1667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

