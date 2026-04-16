# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r18_04_p_carry_defense_p_entry_quality`
- Bots: TradervR1_lab_r18_04_p_carry_defense_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r18_04_p_carry_defense_p_entry_quality

- Combined total PnL: `288725.0000`
- Day -1: `95863.0000`
- Day -2: `96043.0000`
- Day 0: `96819.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r18_04_p_carry_defense_p_entry_quality

- Overall samples: `6` | mean `124375.25` | p10 `-19826.25` | cvar10 `-34260.0` | std `126897.9461`
- Profile `all`: count `6`, mean `124375.25`, p10 `-19826.25`, cvar10 `-34260.0`
- Profile `plausible`: count `6`, mean `124375.25`, p10 `-19826.25`, cvar10 `-34260.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `48820.5`, p10 `-17643.9`, cvar10 `-34260.0`
- `bootstrap_path`: count `2`, mean `37676.75`, p10 `3221.35`, cvar10 `-5392.5`
- `original_noise`: count `2`, mean `286628.5`, p10 `285974.1`, cvar10 `285810.5`

## Comparison

- Primary: `TradervR1_lab_r18_04_p_carry_defense_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1276.1667`
- Median delta: `-39.75`
- P10 delta: `-4957.75`
- Win rate: `0.5`

- `bootstrap_balanced`: mean delta `-4942.75`, p10 delta `-8750.15`, win rate `0.0`
- `bootstrap_path`: mean delta `-54.75`, p10 delta `-181.75`, win rate `0.5`
- `original_noise`: mean delta `1169.0`, p10 delta `1114.2`, win rate `1.0`

- Profile `all`: mean delta `-1276.1667`, p10 delta `-4957.75`, win rate `0.5`
- Profile `plausible`: mean delta `-1276.1667`, p10 delta `-4957.75`, win rate `0.5`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

