# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r18_07_p_carry_defense`
- Bots: TradervR1_lab_r18_07_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r18_07_p_carry_defense

- Combined total PnL: `287134.5000`
- Day -1: `95296.0000`
- Day -2: `95531.5000`
- Day 0: `96307.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r18_07_p_carry_defense

- Overall samples: `6` | mean `122919.1667` | p10 `-21087.5` | cvar10 `-36156.0` | std `126887.8156`
- Profile `all`: count `6`, mean `122919.1667`, p10 `-21087.5`, cvar10 `-36156.0`
- Profile `plausible`: count `6`, mean `122919.1667`, p10 `-21087.5`, cvar10 `-36156.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `45958.75`, p10 `-19733.05`, cvar10 `-36156.0`
- `bootstrap_path`: count `2`, mean `37310.0`, p10 `2646.8`, cvar10 `-6019.0`
- `original_noise`: count `2`, mean `285488.75`, p10 `284861.75`, cvar10 `284705.0`

## Comparison

- Primary: `TradervR1_lab_r18_07_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-2732.25`
- Median delta: `-422.5`
- P10 delta: `-7804.5`
- Win rate: `0.1667`

- `bootstrap_balanced`: mean delta `-7804.5`, p10 delta `-10839.3`, win rate `0.0`
- `bootstrap_path`: mean delta `-421.5`, p10 delta `-756.3`, win rate `0.0`
- `original_noise`: mean delta `29.25`, p10 delta `1.85`, win rate `0.5`

- Profile `all`: mean delta `-2732.25`, p10 delta `-7804.5`, win rate `0.1667`
- Profile `plausible`: mean delta `-2732.25`, p10 delta `-7804.5`, win rate `0.1667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

