# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r16_08_a_quality_guard_cmaes_ash_quality_guard`
- Bots: TradervR1_lab_r16_08_a_quality_guard_best.py, TradervR1_34_1.py

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

### TradervR1_lab_r16_08_a_quality_guard_best

- Combined total PnL: `289550.5000`
- Day -1: `96115.0000`
- Day -2: `96159.5000`
- Day 0: `97276.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r16_08_a_quality_guard_best

- Overall samples: `6` | mean `126240.0833` | p10 `-16842.5` | cvar10 `-31133.0` | std `126076.2458`
- Profile `all`: count `6`, mean `126240.0833`, p10 `-16842.5`, cvar10 `-31133.0`
- Profile `plausible`: count `6`, mean `126240.0833`, p10 `-16842.5`, cvar10 `-31133.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `51155.25`, p10 `-14675.35`, cvar10 `-31133.0`
- `bootstrap_path`: count `2`, mean `39995.0`, p10 `5957.4`, cvar10 `-2552.0`
- `original_noise`: count `2`, mean `287570.0`, p10 `286869.2`, cvar10 `286694.0`

## Comparison

- Primary: `TradervR1_lab_r16_08_a_quality_guard_best`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `588.6667`
- Median delta: `1942.0`
- P10 delta: `-2608.0`
- Win rate: `0.8333`

- `bootstrap_balanced`: mean delta `-2608.0`, p10 delta `-5781.6`, win rate `0.5`
- `bootstrap_path`: mean delta `2263.5`, p10 delta `1972.7`, win rate `1.0`
- `original_noise`: mean delta `2110.5`, p10 delta `2009.3`, win rate `1.0`

- Profile `all`: mean delta `588.6667`, p10 delta `-2608.0`, win rate `0.8333`
- Profile `plausible`: mean delta `588.6667`, p10 delta `-2608.0`, win rate `0.8333`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

