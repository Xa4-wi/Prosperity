# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r06_03_a_attack_tuning`
- Bots: TradervR1_lab_r06_03_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r06_03_a_attack_tuning

- Combined total PnL: `288709.0000`
- Day -1: `95838.0000`
- Day -2: `95918.0000`
- Day 0: `96953.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r06_03_a_attack_tuning

- Overall samples: `6` | mean `125885.8333` | p10 `-16683.75` | cvar10 `-29813.0` | std `125696.0346`
- Profile `all`: count `6`, mean `125885.8333`, p10 `-16683.75`, cvar10 `-29813.0`
- Profile `plausible`: count `6`, mean `125885.8333`, p10 `-16683.75`, cvar10 `-29813.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51736.0`, p10 `-13503.2`, cvar10 `-29813.0`
- `bootstrap_path`: count `2`, mean `39107.25`, p10 `4977.85`, cvar10 `-3554.5`
- `original_noise`: count `2`, mean `286814.25`, p10 `285821.65`, cvar10 `285573.5`

## Comparison

- Primary: `TradervR1_lab_r06_03_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `234.4167`
- Median delta: `1163.75`
- P10 delta: `-2195.75`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-2027.25`, p10 delta `-4609.45`, win rate `0.5`
- `bootstrap_path`: mean delta `1375.75`, p10 delta `1176.75`, win rate `1.0`
- `original_noise`: mean delta `1354.75`, p10 delta `961.75`, win rate `1.0`

- Profile `all`: mean delta `234.4167`, p10 delta `-2195.75`, win rate `0.8333`
- Profile `plausible`: mean delta `234.4167`, p10 delta `-2195.75`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

