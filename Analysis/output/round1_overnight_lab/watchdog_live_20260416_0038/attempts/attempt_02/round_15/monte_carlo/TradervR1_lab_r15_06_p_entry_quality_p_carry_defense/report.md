# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r15_06_p_entry_quality_p_carry_defense`
- Bots: TradervR1_lab_r15_06_p_entry_quality_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r15_06_p_entry_quality_p_carry_defense

- Combined total PnL: `287287.5000`
- Day -1: `95488.0000`
- Day -2: `95525.5000`
- Day 0: `96274.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r15_06_p_entry_quality_p_carry_defense

- Overall samples: `6` | mean `125029.1667` | p10 `-14558.0` | cvar10 `-23937.0` | std `124404.2931`
- Profile `all`: count `6`, mean `125029.1667`, p10 `-14558.0`, cvar10 `-23937.0`
- Profile `plausible`: count `6`, mean `125029.1667`, p10 `-14558.0`, cvar10 `-23937.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51518.0`, p10 `-8846.0`, cvar10 `-23937.0`
- `bootstrap_path`: count `2`, mean `37708.0`, p10 `3398.4`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285861.5`, p10 `285233.9`, cvar10 `285077.0`

## Comparison

- Primary: `TradervR1_lab_r15_06_p_entry_quality_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-622.25`
- Median delta: `183.5`
- P10 delta: `-2579.25`
- Win rate: `0.5`

- `bootstrap_balanced`: mean delta `-2245.25`, p10 delta `-4538.25`, win rate `0.5`
- `bootstrap_path`: mean delta `-23.5`, p10 delta `-42.3`, win rate `0.0`
- `original_noise`: mean delta `402.0`, p10 delta `374.0`, win rate `1.0`

- Profile `all`: mean delta `-622.25`, p10 delta `-2579.25`, win rate `0.5`
- Profile `plausible`: mean delta `-622.25`, p10 delta `-2579.25`, win rate `0.5`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

