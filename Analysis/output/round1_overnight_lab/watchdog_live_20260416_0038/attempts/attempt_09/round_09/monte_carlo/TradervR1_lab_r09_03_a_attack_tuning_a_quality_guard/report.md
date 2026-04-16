# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r09_03_a_attack_tuning_a_quality_guard`
- Bots: TradervR1_lab_r09_03_a_attack_tuning_a_quality_guard.py, TradervR1_34_1.py

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

### TradervR1_lab_r09_03_a_attack_tuning_a_quality_guard

- Combined total PnL: `286185.5000`
- Day -1: `95098.0000`
- Day -2: `95172.5000`
- Day 0: `95915.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r09_03_a_attack_tuning_a_quality_guard

- Overall samples: `6` | mean `123578.1667` | p10 `-18936.0` | cvar10 `-31313.0` | std `125630.2859`
- Profile `all`: count `6`, mean `123578.1667`, p10 `-18936.0`, cvar10 `-31313.0`
- Profile `plausible`: count `6`, mean `123578.1667`, p10 `-18936.0`, cvar10 `-31313.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `49766.5`, p10 `-15097.1`, cvar10 `-31313.0`
- `bootstrap_path`: count `2`, mean `36490.5`, p10 `2050.9`, cvar10 `-6559.0`
- `original_noise`: count `2`, mean `284477.5`, p10 `283788.3`, cvar10 `283616.0`

## Comparison

- Primary: `TradervR1_lab_r09_03_a_attack_tuning_a_quality_guard`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-2073.25`
- Median delta: `-1170.25`
- P10 delta: `-4067.5`
- Win rate: `0.0`

- `bootstrap_balanced`: mean delta `-3996.75`, p10 delta `-6203.35`, win rate `0.0`
- `bootstrap_path`: mean delta `-1241.0`, p10 delta `-1352.2`, win rate `0.0`
- `original_noise`: mean delta `-982.0`, p10 delta `-1071.6`, win rate `0.0`

- Profile `all`: mean delta `-2073.25`, p10 delta `-4067.5`, win rate `0.0`
- Profile `plausible`: mean delta `-2073.25`, p10 delta `-4067.5`, win rate `0.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

