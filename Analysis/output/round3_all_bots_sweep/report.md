# Round 3 Bot Sweep

This report reruns the Round 3 bots through the Rust backtester and ranks them with the official-log calibration layer.

## Calibration Samples

| Label | Local total | Official total |
|---|---:|---:|
| R3_6 | 9514.50 | -17329.61 |
| R3_7 | -59976.00 | -9201.63 |
| R3_8 | 6281.00 | -11894.09 |

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

## Bot Ranking

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

## Notes

- The calibrated total is a selector, not a hidden-book reconstruction.
- If raw and calibrated rankings disagree, prefer the calibrated ordering until more official logs arrive.
