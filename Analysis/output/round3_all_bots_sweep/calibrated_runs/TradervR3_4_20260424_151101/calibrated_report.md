# Round 3 Backtest Calibration

This report compares local public-data backtests against official submission logs and builds a calibrated selection score.

## Samples

| Label | Local total | Official total |
|---|---:|---:|
| R3_6 | 9514.50 | -17329.61 |
| R3_7 | -59976.00 | -9201.63 |

## Product Reliability

| Product | Class | Weight | Agreement | Notes |
|---|---|---:|---:|---|
| HYDROGEL_PACK | misleading | 0.00 | 0.00 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VELVETFRUIT_EXTRACT | misleading | 0.00 | 0.00 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_4000 | misleading | 0.00 | 0.00 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_4500 | misleading | 0.00 | 0.00 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_5000 | trustworthy | 1.00 | 1.00 | Local sign matched official sign on all informative pairs. |
| VEV_5100 | trustworthy | 1.00 | 1.00 | Local sign matched official sign on all informative pairs. |
| VEV_5200 | misleading | 0.00 | 0.00 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_5300 | misleading | 0.00 | 0.00 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_5400 | misleading | 0.00 | 0.00 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_5500 | misleading | 0.00 | 0.00 | Local deltas pointed the wrong way; ignore in calibrated ranking. |
| VEV_6000 | unproven | 0.00 | 0.00 | Not enough evidence yet. |
| VEV_6500 | unproven | 0.00 | 0.00 | Not enough evidence yet. |

## Candidate Scores

| Label | Raw local total | Calibrated total |
|---|---:|---:|
| TradervR3_4 | -54616.50 | -36884.50 |

## Interpretation

- The calibrated score is a selector, not a hidden-book simulator.
- Products labeled `misleading` are currently downweighted to zero because the local replay ranked them the wrong way versus official logs.
- As more official logs arrive, these weights should be recomputed rather than hardcoded.

