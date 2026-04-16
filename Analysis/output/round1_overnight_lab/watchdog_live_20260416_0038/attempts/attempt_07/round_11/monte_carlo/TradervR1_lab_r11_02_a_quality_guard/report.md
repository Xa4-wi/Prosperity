# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r11_02_a_quality_guard`
- Bots: TradervR1_lab_r11_02_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r11_02_a_quality_guard

- Combined total PnL: `287999.0000`
- Day -1: `95581.0000`
- Day -2: `95674.0000`
- Day 0: `96744.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r11_02_a_quality_guard

- Overall samples: `6` | mean `127064.5833` | p10 `-13556.5` | cvar10 `-22693.0` | std `124144.1838`
- Profile `all`: count `6`, mean `127064.5833`, p10 `-13556.5`, cvar10 `-22693.0`
- Profile `plausible`: count `6`, mean `127064.5833`, p10 `-13556.5`, cvar10 `-22693.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `56614.0`, p10 `-6831.6`, cvar10 `-22693.0`
- `bootstrap_path`: count `2`, mean `38475.0`, p10 `4159.0`, cvar10 `-4420.0`
- `original_noise`: count `2`, mean `286104.75`, p10 `285495.35`, cvar10 `285343.0`

## Comparison

- Primary: `TradervR1_lab_r11_02_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1413.1667`
- Median delta: `743.5`
- P10 delta: `645.25`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `2850.75`, p10 delta `2062.15`, win rate `1.0`
- `bootstrap_path`: mean delta `743.5`, p10 delta `731.1`, win rate `1.0`
- `original_noise`: mean delta `645.25`, p10 delta `635.45`, win rate `1.0`

- Profile `all`: mean delta `1413.1667`, p10 delta `645.25`, win rate `1.0`
- Profile `plausible`: mean delta `1413.1667`, p10 delta `645.25`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

