# Round 3 Backtest Calibration

This report compares local public-data backtests against official submission logs and builds a calibrated selection score.

## Samples

| Label | Local total | Official total |
|---|---:|---:|
| R3_1 | -49148.00 | -17068.68 |
| R3_3 | -35436.00 | -19178.07 |
| R3_6 | -48170.00 | -17329.61 |
| R3_7 | 83575.00 | -9201.63 |
| R3_8 | 6281.00 | -11894.09 |
| R3_10 | 71030.00 | -5094.38 |
| R3_16 | 269531.00 | 797.50 |
| R3_17 | 297902.00 | 1540.63 |
| R3_24 | 257977.00 | 8987.50 |
| R3_26 | 247725.00 | 8952.50 |
| R3_27 | 237157.00 | 9265.50 |
| R3_28 | -755873.00 | 10577.38 |
| R3_29 | 237146.00 | 9265.50 |

## Product Reliability

| Product | Class | Weight | Dir | Agreement | R2 | Notes |
|---|---|---:|---|---:|---:|---|
| HYDROGEL_PACK | inverted | 0.85 | inv | 0.91 | 0.22 | Portal logs indicate the local direction should be flipped. |
| VELVETFRUIT_EXTRACT | mixed | 0.50 | dir | 0.68 | 0.60 | Some direct signal, but not stable enough to trust fully. |
| VEV_4000 | mixed | 0.50 | dir | 0.75 | 0.67 | Some direct signal, but not stable enough to trust fully. |
| VEV_4500 | mixed | 0.50 | dir | 0.65 | 0.58 | Some direct signal, but not stable enough to trust fully. |
| VEV_5000 | misleading | 0.00 | inv | 0.62 | 0.23 | Too unstable even after orientation search; ignore in calibrated ranking. |
| VEV_5100 | mixed | 0.50 | dir | 0.68 | 0.66 | Some direct signal, but not stable enough to trust fully. |
| VEV_5200 | trustworthy | 0.85 | dir | 0.86 | 0.90 | Local direction can be used directly. |
| VEV_5300 | trustworthy | 0.85 | dir | 0.88 | 0.80 | Local direction can be used directly. |
| VEV_5400 | mixed | 0.50 | dir | 0.75 | 0.79 | Some direct signal, but not stable enough to trust fully. |
| VEV_5500 | trustworthy | 0.85 | dir | 0.81 | 0.96 | Local direction can be used directly. |
| VEV_6000 | unproven | 0.00 | dir | 0.00 | 0.00 | Not enough evidence yet. |
| VEV_6500 | unproven | 0.00 | dir | 0.00 | 0.00 | Not enough evidence yet. |

## Candidate Scores

| Label | Raw local total | Calibrated total |
|---|---:|---:|
| TradervR3_28 | -755873.00 | 9163.50 |

## Interpretation

- The calibrated score is still a selector, not a hidden-book simulator.
- It now searches for product-by-product orientation as well as scale, so products can be treated as direct or inverted versus the local replay.
- Products labeled `misleading` are still downweighted to zero because even the best orientation was unstable.
- As more official logs arrive, the affine mappings and weights should be recomputed rather than hardcoded.

