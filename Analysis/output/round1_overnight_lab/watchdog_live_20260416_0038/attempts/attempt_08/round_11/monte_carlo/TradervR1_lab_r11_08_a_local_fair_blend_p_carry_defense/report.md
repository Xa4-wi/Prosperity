# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r11_08_a_local_fair_blend_p_carry_defense`
- Bots: TradervR1_lab_r11_08_a_local_fair_blend_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r11_08_a_local_fair_blend_p_carry_defense

- Combined total PnL: `290095.5000`
- Day -1: `96535.0000`
- Day -2: `96237.5000`
- Day 0: `97323.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r11_08_a_local_fair_blend_p_carry_defense

- Overall samples: `6` | mean `126182.5` | p10 `-15017.75` | cvar10 `-26660.0` | std `125184.2978`
- Profile `all`: count `6`, mean `126182.5`, p10 `-15017.75`, cvar10 `-26660.0`
- Profile `plausible`: count `6`, mean `126182.5`, p10 `-15017.75`, cvar10 `-26660.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51306.0`, p10 `-11066.8`, cvar10 `-26660.0`
- `bootstrap_path`: count `2`, mean `39807.25`, p10 `5261.05`, cvar10 `-3375.5`
- `original_noise`: count `2`, mean `287434.25`, p10 `286826.45`, cvar10 `286674.5`

## Comparison

- Primary: `TradervR1_lab_r11_08_a_local_fair_blend_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `531.0833`
- Median delta: `1884.0`
- P10 delta: `-2457.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-2457.25`, p10 delta `-2741.45`, win rate `0.0`
- `bootstrap_path`: mean delta `2075.75`, p10 delta `1857.95`, win rate `1.0`
- `original_noise`: mean delta `1974.75`, p10 delta `1966.55`, win rate `1.0`

- Profile `all`: mean delta `531.0833`, p10 delta `-2457.25`, win rate `0.6667`
- Profile `plausible`: mean delta `531.0833`, p10 delta `-2457.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

