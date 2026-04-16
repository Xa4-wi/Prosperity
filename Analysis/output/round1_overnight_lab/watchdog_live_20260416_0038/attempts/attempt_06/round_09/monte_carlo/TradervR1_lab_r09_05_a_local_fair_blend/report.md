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

- Combined total PnL: `289162.0000`
- Day -1: `95934.0000`
- Day -2: `96084.0000`
- Day 0: `97144.0000`

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

- Overall samples: `6` | mean `125323.4167` | p10 `-17207.5` | cvar10 `-31770.0` | std `126095.7868`
- Profile `all`: count `6`, mean `125323.4167`, p10 `-17207.5`, cvar10 `-31770.0`
- Profile `plausible`: count `6`, mean `125323.4167`, p10 `-17207.5`, cvar10 `-31770.0`
- Profile `stress`: count `0`, mean `0.0`, p10 `0.0`, cvar10 `0.0`
- `bootstrap_balanced`: count `2`, mean `48502.0`, p10 `-15715.6`, cvar10 `-31770.0`
- `bootstrap_path`: count `2`, mean `40086.0`, p10 `5901.2`, cvar10 `-2645.0`
- `original_noise`: count `2`, mean `287382.25`, p10 `286624.45`, cvar10 `286435.0`

## Comparison

- Primary: `TradervR1_lab_r09_05_a_local_fair_blend`
- Compare: `TradervR1_34_1`
- Shared samples: `6`
- Mean delta: `-328.0`
- Median delta: `1922.75`
- P10 delta: `-5261.25`
- Win rate: `0.6667`

- `bootstrap_balanced`: mean delta `-5261.25`, p10 delta `-6821.85`, win rate `0.0`
- `bootstrap_path`: mean delta `2354.5`, p10 delta `2210.9`, win rate `1.0`
- `original_noise`: mean delta `1922.75`, p10 delta `1764.55`, win rate `1.0`

- Profile `all`: mean delta `-328.0`, p10 delta `-5261.25`, win rate `0.6667`
- Profile `plausible`: mean delta `-328.0`, p10 delta `-5261.25`, win rate `0.6667`
- Profile `stress`: mean delta `0.0`, p10 delta `0.0`, win rate `0.0`

