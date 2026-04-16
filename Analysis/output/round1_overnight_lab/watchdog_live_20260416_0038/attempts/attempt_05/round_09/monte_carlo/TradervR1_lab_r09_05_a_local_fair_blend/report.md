# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r09_05_a_local_fair_blend`
- Bots: TradervR1_lab_r09_05_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r09_05_a_local_fair_blend

- Combined total PnL: `288749.5000`
- Day -1: `95905.0000`
- Day -2: `95981.5000`
- Day 0: `96863.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r09_05_a_local_fair_blend

- Overall samples: `6` | mean `126298.5` | p10 `-14333.0` | cvar10 `-24613.0` | std `124616.2882`
- Profile `all`: count `6`, mean `126298.5`, p10 `-14333.0`, cvar10 `-24613.0`
- Profile `plausible`: count `6`, mean `126298.5`, p10 `-14333.0`, cvar10 `-24613.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53346.5`, p10 `-9021.1`, cvar10 `-24613.0`
- `bootstrap_path`: count `2`, mean `38920.5`, p10 `4541.7`, cvar10 `-4053.0`
- `original_noise`: count `2`, mean `286628.5`, p10 `285991.3`, cvar10 `285832.0`

## Comparison

- Primary: `TradervR1_lab_r09_05_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `647.0833`
- Median delta: `1124.0`
- P10 delta: `-416.75`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-416.75`, p10 delta `-706.15`, win rate `0.0`
- `bootstrap_path`: mean delta `1189.0`, p10 delta `1138.6`, win rate `1.0`
- `original_noise`: mean delta `1169.0`, p10 delta `1131.4`, win rate `1.0`

- Profile `all`: mean delta `647.0833`, p10 delta `-416.75`, win rate `0.6667`
- Profile `plausible`: mean delta `647.0833`, p10 delta `-416.75`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

