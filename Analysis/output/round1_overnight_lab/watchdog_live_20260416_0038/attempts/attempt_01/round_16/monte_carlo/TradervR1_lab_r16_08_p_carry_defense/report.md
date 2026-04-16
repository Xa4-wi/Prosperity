# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r16_08_p_carry_defense`
- Bots: TradervR1_lab_r16_08_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r16_08_p_carry_defense

- Combined total PnL: `289276.0000`
- Day -1: `96028.0000`
- Day -2: `96071.0000`
- Day 0: `97177.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r16_08_p_carry_defense

- Overall samples: `6` | mean `126734.6667` | p10 `-14961.25` | cvar10 `-26602.0` | std `125118.2029`
- Profile `all`: count `6`, mean `126734.6667`, p10 `-14961.25`, cvar10 `-26602.0`
- Profile `plausible`: count `6`, mean `126734.6667`, p10 `-14961.25`, cvar10 `-26602.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53328.0`, p10 `-10616.0`, cvar10 `-26602.0`
- `bootstrap_path`: count `2`, mean `39655.25`, p10 `5274.65`, cvar10 `-3320.5`
- `original_noise`: count `2`, mean `287220.75`, p10 `286492.95`, cvar10 `286311.0`

## Comparison

- Primary: `TradervR1_lab_r16_08_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1083.25`
- Median delta: `1729.75`
- P10 delta: `-435.25`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-435.25`, p10 delta `-1722.25`, win rate `0.5`
- `bootstrap_path`: mean delta `1923.75`, p10 delta `1871.55`, win rate `1.0`
- `original_noise`: mean delta `1761.25`, p10 delta `1633.05`, win rate `1.0`

- Profile `all`: mean delta `1083.25`, p10 delta `-435.25`, win rate `0.8333`
- Profile `plausible`: mean delta `1083.25`, p10 delta `-435.25`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

