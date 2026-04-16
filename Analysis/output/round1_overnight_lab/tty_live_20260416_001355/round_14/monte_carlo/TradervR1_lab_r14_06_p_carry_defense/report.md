# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r14_06_p_carry_defense`
- Bots: TradervR1_lab_r14_06_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r14_06_p_carry_defense

- Combined total PnL: `287984.0000`
- Day -1: `95581.0000`
- Day -2: `95674.0000`
- Day 0: `96729.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r14_06_p_carry_defense

- Overall samples: `6` | mean `125269.75` | p10 `-14703.5` | cvar10 `-25199.0` | std `124544.6531`
- Profile `all`: count `6`, mean `125269.75`, p10 `-14703.5`, cvar10 `-25199.0`
- Profile `plausible`: count `6`, mean `125269.75`, p10 `-14703.5`, cvar10 `-25199.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51133.25`, p10 `-9932.55`, cvar10 `-25199.0`
- `bootstrap_path`: count `2`, mean `38580.0`, p10 `4349.6`, cvar10 `-4208.0`
- `original_noise`: count `2`, mean `286096.0`, p10 `285680.0`, cvar10 `285576.0`

## Comparison

- Primary: `TradervR1_lab_r14_06_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-381.6667`
- Median delta: `566.5`
- P10 delta: `-2630.0`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-2630.0`, p10 delta `-4221.2`, win rate `0.0`
- `bootstrap_path`: mean delta `848.5`, p10 delta `750.5`, win rate `1.0`
- `original_noise`: mean delta `636.5`, p10 delta `452.9`, win rate `1.0`

- Profile `all`: mean delta `-381.6667`, p10 delta `-2630.0`, win rate `0.6667`
- Profile `plausible`: mean delta `-381.6667`, p10 delta `-2630.0`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

