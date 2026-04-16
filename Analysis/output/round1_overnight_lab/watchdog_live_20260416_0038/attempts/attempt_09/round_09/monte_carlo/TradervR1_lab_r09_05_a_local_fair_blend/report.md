# Monte Carlo Robustness Report

- Output name: `TradervR1_lab_r09_05_a_local_fair_blend`
- Bots: TradervR1_lab_r09_05_a_local_fair_blend.py, TradervR1_34_1.py

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

### TradervR1_lab_r09_05_a_local_fair_blend

- Combined total PnL: `288120.0000`
- Day -1: `95624.0000`
- Day -2: `95713.0000`
- Day 0: `96783.0000`

## Monte Carlo Summary

### TradervR1_34_1

- Overall samples: `6` | mean `125651.4167` | p10 `-14868.5` | cvar10 `-24558.0` | std `124381.8512`
- Profile `all`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `plausible`: count `6`, mean `125651.4167`, p10 `-14868.5`, cvar10 `-24558.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `53763.25`, p10 `-8893.75`, cvar10 `-24558.0`
- `bootstrap_path`: count `2`, mean `37731.5`, p10 `3403.1`, cvar10 `-5179.0`
- `original_noise`: count `2`, mean `285459.5`, p10 `284859.9`, cvar10 `284710.0`

### TradervR1_lab_r09_05_a_local_fair_blend

- Overall samples: `6` | mean `124349.1667` | p10 `-17972.75` | cvar10 `-31370.0` | std `125961.0081`
- Profile `all`: count `6`, mean `124349.1667`, p10 `-17972.75`, cvar10 `-31370.0`
- Profile `plausible`: count `6`, mean `124349.1667`, p10 `-17972.75`, cvar10 `-31370.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `48195.25`, p10 `-15456.95`, cvar10 `-31370.0`
- `bootstrap_path`: count `2`, mean `38506.75`, p10 `4040.95`, cvar10 `-4575.5`
- `original_noise`: count `2`, mean `286345.5`, p10 `285692.7`, cvar10 `285529.5`

## Comparison

- Primary: `TradervR1_lab_r09_05_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-1302.25`
- Median delta: `711.5`
- P10 delta: `-5568.0`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-5568.0`, p10 delta `-6563.2`, win rate `0.0`
- `bootstrap_path`: mean delta `775.25`, p10 delta `637.85`, win rate `1.0`
- `original_noise`: mean delta `886.0`, p10 delta `832.8`, win rate `1.0`

- Profile `all`: mean delta `-1302.25`, p10 delta `-5568.0`, win rate `0.6667`
- Profile `plausible`: mean delta `-1302.25`, p10 delta `-5568.0`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

