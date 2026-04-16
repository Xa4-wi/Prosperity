# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r08_05_p_entry_quality_a_attack_tuning`
- Bots: TradervR1_lab_r08_05_p_entry_quality_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r08_05_p_entry_quality_a_attack_tuning

- Combined total PnL: `289137.5000`
- Day -1: `95969.0000`
- Day -2: `96116.5000`
- Day 0: `97052.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r08_05_p_entry_quality_a_attack_tuning

- Overall samples: `6` | mean `125540.5` | p10 `-17133.0` | cvar10 `-31120.0` | std `125959.7438`
- Profile `all`: count `6`, mean `125540.5`, p10 `-17133.0`, cvar10 `-31120.0`
- Profile `plausible`: count `6`, mean `125540.5`, p10 `-17133.0`, cvar10 `-31120.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49910.0`, p10 `-14914.0`, cvar10 `-31120.0`
- `bootstrap_path`: count `2`, mean `39618.0`, p10 `5406.8`, cvar10 `-3146.0`
- `original_noise`: count `2`, mean `287093.5`, p10 `286321.9`, cvar10 `286129.0`

## Comparison

- Primary: `TradervR1_lab_r08_05_p_entry_quality_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-110.9167`
- Median delta: `1579.5`
- P10 delta: `-3853.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-3853.25`, p10 delta `-6020.25`, win rate `0.0`
- `bootstrap_path`: mean delta `1886.5`, p10 delta `1769.3`, win rate `1.0`
- `original_noise`: mean delta `1634.0`, p10 delta `1462.0`, win rate `1.0`

- Profile `all`: mean delta `-110.9167`, p10 delta `-3853.25`, win rate `0.6667`
- Profile `plausible`: mean delta `-110.9167`, p10 delta `-3853.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

