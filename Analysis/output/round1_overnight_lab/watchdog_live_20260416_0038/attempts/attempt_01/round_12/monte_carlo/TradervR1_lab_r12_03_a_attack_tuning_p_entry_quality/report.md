# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r12_03_a_attack_tuning_p_entry_quality`
- Bots: TradervR1_lab_r12_03_a_attack_tuning_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r12_03_a_attack_tuning_p_entry_quality

- Combined total PnL: `288736.0000`
- Day -1: `95818.0000`
- Day -2: `95971.0000`
- Day 0: `96947.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r12_03_a_attack_tuning_p_entry_quality

- Overall samples: `6` | mean `124055.8333` | p10 `-21116.75` | cvar10 `-38584.0` | std `127736.7119`
- Profile `all`: count `6`, mean `124055.8333`, p10 `-21116.75`, cvar10 `-38584.0`
- Profile `plausible`: count `6`, mean `124055.8333`, p10 `-21116.75`, cvar10 `-38584.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `45700.5`, p10 `-21727.1`, cvar10 `-38584.0`
- `bootstrap_path`: count `2`, mean `39122.25`, p10 `4904.85`, cvar10 `-3649.5`
- `original_noise`: count `2`, mean `287344.75`, p10 `287023.75`, cvar10 `286943.5`

## Comparison

- Primary: `TradervR1_lab_r12_03_a_attack_tuning_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1595.5833`
- Median delta: `1390.75`
- P10 delta: `-8062.75`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-8062.75`, p10 delta `-12833.35`, win rate `0.0`
- `bootstrap_path`: mean delta `1390.75`, p10 delta `1279.75`, win rate `1.0`
- `original_noise`: mean delta `1885.25`, p10 delta `1606.65`, win rate `1.0`

- Profile `all`: mean delta `-1595.5833`, p10 delta `-8062.75`, win rate `0.6667`
- Profile `plausible`: mean delta `-1595.5833`, p10 delta `-8062.75`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

