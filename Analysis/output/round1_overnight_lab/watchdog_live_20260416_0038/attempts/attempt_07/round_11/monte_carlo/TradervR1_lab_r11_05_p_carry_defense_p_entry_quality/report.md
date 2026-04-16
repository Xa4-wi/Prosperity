# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r11_05_p_carry_defense_p_entry_quality`
- Bots: TradervR1_lab_r11_05_p_carry_defense_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r11_05_p_carry_defense_p_entry_quality

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

### TradervR1_lab_r11_05_p_carry_defense_p_entry_quality

- Overall samples: `6` | mean `125778.6667` | p10 `-15043.25` | cvar10 `-26766.0` | std `125111.0152`
- Profile `all`: count `6`, mean `125778.6667`, p10 `-15043.25`, cvar10 `-26766.0`
- Profile `plausible`: count `6`, mean `125778.6667`, p10 `-15043.25`, cvar10 `-26766.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50525.0`, p10 `-11307.8`, cvar10 `-26766.0`
- `bootstrap_path`: count `2`, mean `39622.25`, p10 `5268.05`, cvar10 `-3320.5`
- `original_noise`: count `2`, mean `287188.75`, p10 `286364.15`, cvar10 `286158.0`

## Comparison

- Primary: `TradervR1_lab_r11_05_p_carry_defense_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `127.25`
- Median delta: `1653.25`
- P10 delta: `-3238.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-3238.25`, p10 delta `-4062.45`, win rate `0.0`
- `bootstrap_path`: mean delta `1890.75`, p10 delta `1864.95`, win rate `1.0`
- `original_noise`: mean delta `1729.25`, p10 delta `1504.25`, win rate `1.0`

- Profile `all`: mean delta `127.25`, p10 delta `-3238.25`, win rate `0.6667`
- Profile `plausible`: mean delta `127.25`, p10 delta `-3238.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

