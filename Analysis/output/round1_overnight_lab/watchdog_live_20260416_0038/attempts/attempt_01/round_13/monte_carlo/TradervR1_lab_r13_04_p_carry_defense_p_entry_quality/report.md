# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r13_04_p_carry_defense_p_entry_quality`
- Bots: TradervR1_lab_r13_04_p_carry_defense_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r13_04_p_carry_defense_p_entry_quality

- Combined total PnL: `288905.0000`
- Day -1: `95867.0000`
- Day -2: `95973.0000`
- Day 0: `97065.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r13_04_p_carry_defense_p_entry_quality

- Overall samples: `6` | mean `125116.3333` | p10 `-18759.25` | cvar10 `-33916.0` | std `126513.6355`
- Profile `all`: count `6`, mean `125116.3333`, p10 `-18759.25`, cvar10 `-33916.0`
- Profile `plausible`: count `6`, mean `125116.3333`, p10 `-18759.25`, cvar10 `-33916.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49559.75`, p10 `-17220.85`, cvar10 `-33916.0`
- `bootstrap_path`: count `2`, mean `39072.75`, p10 `4932.55`, cvar10 `-3602.5`
- `original_noise`: count `2`, mean `286716.5`, p10 `285995.3`, cvar10 `285815.0`

## Comparison

- Primary: `TradervR1_lab_r13_04_p_carry_defense_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-535.0833`
- Median delta: `1105.5`
- P10 delta: `-4203.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-4203.5`, p10 delta `-8327.1`, win rate `0.5`
- `bootstrap_path`: mean delta `1341.25`, p10 delta `1153.05`, win rate `1.0`
- `original_noise`: mean delta `1257.0`, p10 delta `1135.4`, win rate `1.0`

- Profile `all`: mean delta `-535.0833`, p10 delta `-4203.5`, win rate `0.8333`
- Profile `plausible`: mean delta `-535.0833`, p10 delta `-4203.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

