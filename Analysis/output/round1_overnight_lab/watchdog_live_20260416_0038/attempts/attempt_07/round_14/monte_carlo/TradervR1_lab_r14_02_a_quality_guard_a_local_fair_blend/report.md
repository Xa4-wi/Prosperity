# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r14_02_a_quality_guard_a_local_fair_blend`
- Bots: TradervR1_lab_r14_02_a_quality_guard_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r14_02_a_quality_guard_a_local_fair_blend

- Combined total PnL: `288703.0000`
- Day -1: `96108.0000`
- Day -2: `95867.0000`
- Day 0: `96728.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r14_02_a_quality_guard_a_local_fair_blend

- Overall samples: `6` | mean `125606.25` | p10 `-16727.75` | cvar10 `-29031.0` | std `125646.9891`
- Profile `all`: count `6`, mean `125606.25`, p10 `-16727.75`, cvar10 `-29031.0`
- Profile `plausible`: count `6`, mean `125606.25`, p10 `-16727.75`, cvar10 `-29031.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51475.5`, p10 `-12929.7`, cvar10 `-29031.0`
- `bootstrap_path`: count `2`, mean `38604.25`, p10 `4181.25`, cvar10 `-4424.5`
- `original_noise`: count `2`, mean `286739.0`, p10 `286340.2`, cvar10 `286240.5`

## Comparison

- Primary: `TradervR1_lab_r14_02_a_quality_guard_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-45.1667`
- Median delta: `872.75`
- P10 delta: `-2287.75`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-2287.75`, p10 delta `-4035.95`, win rate `0.0`
- `bootstrap_path`: mean delta `872.75`, p10 delta `778.15`, win rate `1.0`
- `original_noise`: mean delta `1279.5`, p10 delta `1078.7`, win rate `1.0`

- Profile `all`: mean delta `-45.1667`, p10 delta `-2287.75`, win rate `0.6667`
- Profile `plausible`: mean delta `-45.1667`, p10 delta `-2287.75`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

