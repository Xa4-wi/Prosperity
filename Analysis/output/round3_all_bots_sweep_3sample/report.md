# Round 3 Backtester Status

This report re-scores the existing Round 3 runs using the current three-log calibration set (`R3_6`, `R3_7`, `R3_8`).

## Product Reliability

| Product | Class | Weight | Agreement |
|---|---|---:|---:|
| HYDROGEL_PACK | mixed | 0.35 | 0.67 |
| VELVETFRUIT_EXTRACT | misleading | 0.00 | 0.00 |
| VEV_4000 | misleading | 0.00 | 0.33 |
| VEV_4500 | misleading | 0.00 | 0.00 |
| VEV_5000 | misleading | 0.00 | 0.33 |
| VEV_5100 | mixed | 0.35 | 0.67 |
| VEV_5200 | misleading | 0.00 | 0.33 |
| VEV_5300 | misleading | 0.00 | 0.33 |
| VEV_5400 | misleading | 0.00 | 0.00 |
| VEV_5500 | misleading | 0.00 | 0.00 |
| VEV_6000 | unproven | 0.00 | 0.00 |
| VEV_6500 | unproven | 0.00 | 0.00 |

## Current Ranking

| Rank | Bot | Raw local total | Calibrated total |
|---:|---|---:|---:|
| 1 | TradervR3_2.py | -44685.50 | 29001.00 |
| 2 | TradervR3_3.py | -35436.00 | 28556.50 |
| 3 | TradervR3_1.py | -49148.00 | 27565.65 |
| 4 | TradervR3_7.py | 83575.00 | 26329.10 |
| 5 | TradervR3_8.py | 6281.00 | 25943.75 |
| 6 | TradervR3_5.py | -52049.00 | 25295.20 |
| 7 | TradervR3_6.py | -48170.00 | 24368.75 |
| 8 | TradervR3_4.py | -54616.50 | 23902.90 |
| 9 | TradervR3_4_1.py | -54507.50 | 23902.90 |
| 10 | TradervR3_4_2.py | -55025.50 | 22726.20 |

## Interpretation

- The backtester workflow is now usable, but the calibration is still sample-sensitive.
- After adding `R3_8`, `VEV_5000` dropped out as a fully trustworthy selector and `HYDROGEL_PACK` moved into the mixed bucket.
- This means we should trust the calibrated process more than raw local PnL, but not over-trust exact rankings until we have more official logs.
