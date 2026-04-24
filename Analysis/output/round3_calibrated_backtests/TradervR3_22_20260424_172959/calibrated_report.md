# Round 3 Backtest Calibration

This report compares local public-data backtests against official submission logs and builds a calibrated selection score.

## Samples

| Label | Local total | Official total |
|---|---:|---:|
| R3_6 | 9514.50 | -17329.61 |
| R3_7 | -59976.00 | -9201.63 |
| R3_8 | 6281.00 | -11894.09 |

## Product Reliability

| Product | Class | Weight | Agreement | Notes |
|---|---|---:|---:|---|
| HYDROGEL_PACK | mixed | 0.35 | 0.67 | Some signal, but not stable enough to trust fully. |
| VELVETFRUIT_EXTRACT | misleading | 0.00 | 0.00 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_4000 | misleading | 0.00 | 0.33 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_4500 | misleading | 0.00 | 0.00 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_5000 | misleading | 0.00 | 0.33 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_5100 | mixed | 0.35 | 0.67 | Some signal, but not stable enough to trust fully. |
| VEV_5200 | misleading | 0.00 | 0.33 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_5300 | misleading | 0.00 | 0.33 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_5400 | misleading | 0.00 | 0.00 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_5500 | misleading | 0.00 | 0.00 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_6000 | unproven | 0.00 | 0.00 | Not enough evidence yet. |
| VEV_6500 | unproven | 0.00 | 0.00 | Not enough evidence yet. |

## Candidate Scores

| Label | Raw local total | Calibrated total |
|---|---:|---:|
| TradervR3_22 | 269533.00 | 51278.85 |

## Interpretation

- The calibrated score is a selector, not a hidden-book simulator.
- Products labeled `misleading` are currently downweighted to zero because the local replay ranked them the wrong way versus official logs.
- As more official logs arrive, these weights should be recomputed rather than hardcoded.

