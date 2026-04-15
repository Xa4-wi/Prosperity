# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard`
- Bots: TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard

- Combined total PnL: `290399.5000`
- Day -1: `96607.0000`
- Day -2: `96418.5000`
- Day 0: `97374.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard

- Overall samples: `6` | mean `127374.3333` | p10 `-18077.75` | cvar10 `-33994.0` | std `126936.7627`
- Profile `all`: count `6`, mean `127374.3333`, p10 `-18077.75`, cvar10 `-33994.0`
- Profile `plausible`: count `6`, mean `127374.3333`, p10 `-18077.75`, cvar10 `-33994.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53169.75`, p10 `-16561.25`, cvar10 `-33994.0`
- `bootstrap_path`: count `2`, mean `40693.75`, p10 `6409.55`, cvar10 `-2161.5`
- `original_noise`: count `2`, mean `288259.5`, p10 `287520.7`, cvar10 `287336.0`

## Comparison

- Primary: `TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1722.9167`
- Median delta: `2940.5`
- P10 delta: `-3405.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-593.5`, p10 delta `-7667.5`, win rate `0.5`
- `bootstrap_path`: mean delta `2962.25`, p10 delta `2918.05`, win rate `1.0`
- `original_noise`: mean delta `2800.0`, p10 delta `2660.8`, win rate `1.0`

- Profile `all`: mean delta `1722.9167`, p10 delta `-3405.0`, win rate `0.8333`
- Profile `plausible`: mean delta `1722.9167`, p10 delta `-3405.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

