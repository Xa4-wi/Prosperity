# Round 3 Backtest Calibration

This report compares local public-data backtests against official submission logs and builds a calibrated selection score.

## Samples

| Label | Local total | Official total |
|---|---:|---:|
| R3_1 | -49148.00 | -17068.68 |
| R3_10 | 71030.00 | -5094.38 |
| R3_16 | 269531.00 | 797.50 |
| R3_17 | 297902.00 | 1540.63 |
| R3_24 | 257977.00 | 8987.50 |
| R3_26 | 247725.00 | 8952.50 |
| R3_27 | 237157.00 | 9265.50 |
| R3_28 | -755873.00 | 10577.38 |
| R3_29 | 237146.00 | 9265.50 |
| R3_3 | -35436.00 | -19178.07 |
| R3_30 | 214931.00 | 5587.13 |
| R3_31 | 134229.00 | 9255.63 |
| R3_6 | -48170.00 | -17329.61 |
| R3_7 | 83575.00 | -9201.63 |
| R3_8 | 6281.00 | -11894.09 |

## Product Reliability

| Product | Class | Weight | Dir | Agreement | R2 | Notes |
|---|---|---:|---|---:|---:|---|
| HYDROGEL_PACK | inverted | 0.85 | inv | 0.87 | 0.21 | Portal logs indicate the local direction should be flipped. |
| VELVETFRUIT_EXTRACT | mixed | 0.50 | dir | 0.69 | 0.61 | Some direct signal, but not stable enough to trust fully. |
| VEV_4000 | mixed | 0.50 | dir | 0.77 | 0.69 | Some direct signal, but not stable enough to trust fully. |
| VEV_4500 | mixed | 0.50 | dir | 0.66 | 0.60 | Some direct signal, but not stable enough to trust fully. |
| VEV_5000 | mixed_inverted | 0.50 | inv | 0.64 | 0.24 | Some useful signal, but only after flipping local direction. |
| VEV_5100 | mixed | 0.50 | dir | 0.69 | 0.68 | Some direct signal, but not stable enough to trust fully. |
| VEV_5200 | trustworthy | 0.85 | dir | 0.88 | 0.91 | Local direction can be used directly. |
| VEV_5300 | trustworthy | 0.85 | dir | 0.90 | 0.82 | Local direction can be used directly. |
| VEV_5400 | mixed | 0.50 | dir | 0.77 | 0.81 | Some direct signal, but not stable enough to trust fully. |
| VEV_5500 | trustworthy | 0.85 | dir | 0.84 | 0.97 | Local direction can be used directly. |
| VEV_6000 | unproven | 0.00 | dir | 0.00 | 0.00 | Not enough evidence yet. |
| VEV_6500 | unproven | 0.00 | dir | 0.00 | 0.00 | Not enough evidence yet. |

## Candidate Scores

| Label | Raw local total | Calibrated total |
|---|---:|---:|
| TradervR3_32 | 258990.00 | 2930.32 |

## Interpretation

- The calibrated score is still a selector, not a hidden-book simulator.
- It now searches for product-by-product orientation as well as scale, so products can be treated as direct or inverted versus the local replay.
- Products labeled `misleading` are still downweighted to zero because even the best orientation was unstable.
- As more official logs arrive, the affine mappings and weights should be recomputed rather than hardcoded.

