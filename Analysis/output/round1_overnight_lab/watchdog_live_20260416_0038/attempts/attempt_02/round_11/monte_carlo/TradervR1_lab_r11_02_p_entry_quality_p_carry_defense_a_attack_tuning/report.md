# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r11_02_p_entry_quality_p_carry_defense_a_attack_tuning`
- Bots: TradervR1_lab_r11_02_p_entry_quality_p_carry_defense_a_attack_tuning.py, TradervR1_34_1.py

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

### TradervR1_lab_r11_02_p_entry_quality_p_carry_defense_a_attack_tuning

- Combined total PnL: `290213.5000`
- Day -1: `96317.0000`
- Day -2: `96488.5000`
- Day 0: `97408.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r11_02_p_entry_quality_p_carry_defense_a_attack_tuning

- Overall samples: `6` | mean `128095.8333` | p10 `-11697.75` | cvar10 `-21119.0` | std `124137.295`
- Profile `all`: count `6`, mean `128095.8333`, p10 `-11697.75`, cvar10 `-21119.0`
- Profile `plausible`: count `6`, mean `128095.8333`, p10 `-11697.75`, cvar10 `-21119.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `55622.75`, p10 `-5770.65`, cvar10 `-21119.0`
- `bootstrap_path`: count `2`, mean `40590.75`, p10 `6296.95`, cvar10 `-2276.5`
- `original_noise`: count `2`, mean `288074.0`, p10 `287356.0`, cvar10 `287176.5`

## Comparison

- Primary: `TradervR1_lab_r11_02_p_entry_quality_p_carry_defense_a_attack_tuning`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2444.4167`
- Median delta: `2789.25`
- P10 delta: `1373.25`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `1859.5`, p10 delta `595.9`, win rate `1.0`
- `bootstrap_path`: mean delta `2859.25`, p10 delta `2824.65`, win rate `1.0`
- `original_noise`: mean delta `2614.5`, p10 delta `2496.1`, win rate `1.0`

- Profile `all`: mean delta `2444.4167`, p10 delta `1373.25`, win rate `1.0`
- Profile `plausible`: mean delta `2444.4167`, p10 delta `1373.25`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

