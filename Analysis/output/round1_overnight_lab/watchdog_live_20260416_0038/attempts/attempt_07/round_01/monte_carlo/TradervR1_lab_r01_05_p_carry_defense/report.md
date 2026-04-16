# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r01_05_p_carry_defense`
- Bots: TradervR1_lab_r01_05_p_carry_defense.py, TradervR1_34_1.py

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

### TradervR1_lab_r01_05_p_carry_defense

- Combined total PnL: `289298.0000`
- Day -1: `96012.0000`
- Day -2: `96088.0000`
- Day 0: `97198.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r01_05_p_carry_defense

- Overall samples: `6` | mean `125823.8333` | p10 `-18593.25` | cvar10 `-33866.0` | std `126579.1895`
- Profile `all`: count `6`, mean `125823.8333`, p10 `-18593.25`, cvar10 `-33866.0`
- Profile `plausible`: count `6`, mean `125823.8333`, p10 `-18593.25`, cvar10 `-33866.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `50671.0`, p10 `-16958.6`, cvar10 `-33866.0`
- `bootstrap_path`: count `2`, mean `39715.25`, p10 `5286.65`, cvar10 `-3320.5`
- `original_noise`: count `2`, mean `287085.25`, p10 `286571.45`, cvar10 `286443.0`

## Comparison

- Primary: `TradervR1_lab_r01_05_p_carry_defense`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `172.4167`
- Median delta: `1795.75`
- P10 delta: `-3894.75`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-3092.25`, p10 delta `-8064.85`, win rate `0.5`
- `bootstrap_path`: mean delta `1983.75`, p10 delta `1883.55`, win rate `1.0`
- `original_noise`: mean delta `1625.75`, p10 delta `1539.95`, win rate `1.0`

- Profile `all`: mean delta `172.4167`, p10 delta `-3894.75`, win rate `0.8333`
- Profile `plausible`: mean delta `172.4167`, p10 delta `-3894.75`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

