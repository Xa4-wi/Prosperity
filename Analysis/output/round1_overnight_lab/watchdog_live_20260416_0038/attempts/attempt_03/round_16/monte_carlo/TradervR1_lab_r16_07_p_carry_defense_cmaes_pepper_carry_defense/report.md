# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r16_07_p_carry_defense_cmaes_pepper_carry_defense`
- Bots: TradervR1_lab_r16_07_p_carry_defense_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r16_07_p_carry_defense_best

- Combined total PnL: `289276.0000`
- Day -1: `96028.0000`
- Day -2: `96071.0000`
- Day 0: `97177.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r16_07_p_carry_defense_best

- Overall samples: `6` | mean `126770.0` | p10 `-12784.25` | cvar10 `-22248.0` | std `124129.0059`
- Profile `all`: count `6`, mean `126770.0`, p10 `-12784.25`, cvar10 `-22248.0`
- Profile `plausible`: count `6`, mean `126770.0`, p10 `-12784.25`, cvar10 `-22248.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53633.25`, p10 `-7071.75`, cvar10 `-22248.0`
- `bootstrap_path`: count `2`, mean `39655.25`, p10 `5274.65`, cvar10 `-3320.5`
- `original_noise`: count `2`, mean `287021.5`, p10 `286379.5`, cvar10 `286219.0`

## Comparison

- Primary: `TradervR1_lab_r16_07_p_carry_defense_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `1118.5833`
- Median delta: `1736.75`
- P10 delta: `-530.5`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-130.0`, p10 delta `-2082.0`, win rate `0.5`
- `bootstrap_path`: mean delta `1923.75`, p10 delta `1871.55`, win rate `1.0`
- `original_noise`: mean delta `1562.0`, p10 delta `1519.6`, win rate `1.0`

- Profile `all`: mean delta `1118.5833`, p10 delta `-530.5`, win rate `0.8333`
- Profile `plausible`: mean delta `1118.5833`, p10 delta `-530.5`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

