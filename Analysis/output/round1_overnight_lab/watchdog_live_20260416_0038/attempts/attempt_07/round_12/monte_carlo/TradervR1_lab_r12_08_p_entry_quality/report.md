# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r12_08_p_entry_quality`
- Bots: TradervR1_lab_r12_08_p_entry_quality.py, TradervR1_34_1.py

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

### TradervR1_lab_r12_08_p_entry_quality

- Combined total PnL: `289524.0000`
- Day -1: `96085.0000`
- Day -2: `96108.0000`
- Day 0: `97331.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r12_08_p_entry_quality

- Overall samples: `6` | mean `127798.25` | p10 `-12321.75` | cvar10 `-21481.0` | std `124107.9825`
- Profile `all`: count `6`, mean `127798.25`, p10 `-12321.75`, cvar10 `-21481.0`
- Profile `plausible`: count `6`, mean `127798.25`, p10 `-12321.75`, cvar10 `-21481.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `56211.5`, p10 `-5942.5`, cvar10 `-21481.0`
- `bootstrap_path`: count `2`, mean `39823.75`, p10 `5434.75`, cvar10 `-3162.5`
- `original_noise`: count `2`, mean `287359.5`, p10 `286814.7`, cvar10 `286678.5`

## Comparison

- Primary: `TradervR1_lab_r12_08_p_entry_quality`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `2146.8333`
- Median delta: `1992.5`
- P10 delta: `1825.5`
- Win rate: `1.0`

- `bootstrap_balanced`: mean delta `2448.25`, p10 delta `1945.25`, win rate `1.0`
- `bootstrap_path`: mean delta `2092.25`, p10 delta `2031.65`, win rate `1.0`
- `original_noise`: mean delta `1900.0`, p10 delta `1845.2`, win rate `1.0`

- Profile `all`: mean delta `2146.8333`, p10 delta `1825.5`, win rate `1.0`
- Profile `plausible`: mean delta `2146.8333`, p10 delta `1825.5`, win rate `1.0`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

