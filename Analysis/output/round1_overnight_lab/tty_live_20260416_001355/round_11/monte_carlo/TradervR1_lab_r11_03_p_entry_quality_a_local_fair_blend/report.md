# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r11_03_p_entry_quality_a_local_fair_blend`
- Bots: TradervR1_lab_r11_03_p_entry_quality_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r11_03_p_entry_quality_a_local_fair_blend

- Combined total PnL: `289405.5000`
- Day -1: `96045.0000`
- Day -2: `96143.5000`
- Day 0: `97217.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r11_03_p_entry_quality_a_local_fair_blend

- Overall samples: `6` | mean `125481.3333` | p10 `-16661.25` | cvar10 `-29835.0` | std `125919.3489`
- Profile `all`: count `6`, mean `125481.3333`, p10 `-16661.25`, cvar10 `-29835.0`
- Profile `plausible`: count `6`, mean `125481.3333`, p10 `-16661.25`, cvar10 `-29835.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49542.5`, p10 `-13959.5`, cvar10 `-29835.0`
- `bootstrap_path`: count `2`, mean `39402.25`, p10 `5090.45`, cvar10 `-3487.5`
- `original_noise`: count `2`, mean `287499.25`, p10 `286875.05`, cvar10 `286719.0`

## Comparison

- Primary: `TradervR1_lab_r11_03_p_entry_quality_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-170.0833`
- Median delta: `1670.75`
- P10 delta: `-4220.75`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-4220.75`, p10 delta `-5065.75`, win rate `0.0`
- `bootstrap_path`: mean delta `1670.75`, p10 delta `1654.15`, win rate `1.0`
- `original_noise`: mean delta `2039.75`, p10 delta `2015.15`, win rate `1.0`

- Profile `all`: mean delta `-170.0833`, p10 delta `-4220.75`, win rate `0.6667`
- Profile `plausible`: mean delta `-170.0833`, p10 delta `-4220.75`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

