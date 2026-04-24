# Round 3 Hydrogel Oracle Study

This study compares Hydrogel strategy classes, not bot parameter tweaks.

Classes tested:
- all-day hold
- one-flip trend strategy
- two-flip trend strategy
- anchored mean reverter around `10000`
- local-fair mean reverter around a moving stable fair

## Aggregate Class Totals

- `two_flip`: `167600.00`
- `one_flip`: `107600.00`
- `anchored_mean_reverter`: `71600.00`
- `hold`: `15200.00`
- `local_fair_mm`: `-154640.00`

Interpretation: Hydrogel ceiling looks regime / phase driven.

## Daily Best Results

### Day 0

- `hold`: `{"pattern": "all_day_short", "pnl": 6800.0, "size": 200}`
- `one_flip`: `{"flip_idx": 3770, "flip_timestamp": 377000, "pattern": "long_short", "pnl": 32000.0, "size": 200}`
- `two_flip`: `{"first_flip_idx": 1094, "first_flip_timestamp": 109400, "pattern": "short_long_short", "pnl": 56000.0, "second_flip_idx": 3770, "second_flip_timestamp": 377000, "size": 200}`
- `anchored_mean_reverter`: `{"entry_threshold": 52, "exit_threshold": 26.0, "pattern": "anchored_mean_reverter", "pnl": 26600.0, "size": 200}`
- `local_fair_mm`: `{"entry_threshold": 2.0, "exit_threshold": 1.0, "pattern": "local_fair_mean_reverter", "pnl": -54040.0, "size": 40}`

### Day 1

- `hold`: `{"pattern": "all_day_long", "pnl": 9800.0, "size": 200}`
- `one_flip`: `{"flip_idx": 7224, "flip_timestamp": 722400, "pattern": "long_short", "pnl": 32200.0, "size": 200}`
- `two_flip`: `{"first_flip_idx": 1894, "first_flip_timestamp": 189400, "pattern": "long_short_long", "pnl": 53800.0, "second_flip_idx": 4412, "second_flip_timestamp": 441200, "size": 200}`
- `anchored_mean_reverter`: `{"entry_threshold": 58, "exit_threshold": 29.0, "pattern": "anchored_mean_reverter", "pnl": 25200.0, "size": 200}`
- `local_fair_mm`: `{"entry_threshold": 1.0, "exit_threshold": 0.5, "pattern": "local_fair_mean_reverter", "pnl": -55080.0, "size": 40}`

### Day 2

- `hold`: `{"pattern": "all_day_short", "pnl": -1400.0, "size": 200}`
- `one_flip`: `{"flip_idx": 2800, "flip_timestamp": 280000, "pattern": "short_long", "pnl": 43400.0, "size": 200}`
- `two_flip`: `{"first_flip_idx": 2800, "first_flip_timestamp": 280000, "pattern": "short_long_short", "pnl": 57800.0, "second_flip_idx": 7228, "second_flip_timestamp": 722800, "size": 200}`
- `anchored_mean_reverter`: `{"entry_threshold": 44, "exit_threshold": 22.0, "pattern": "anchored_mean_reverter", "pnl": 19800.0, "size": 200}`
- `local_fair_mm`: `{"entry_threshold": 1.2000000000000002, "exit_threshold": 0.6000000000000001, "pattern": "local_fair_mean_reverter", "pnl": -45520.0, "size": 40}`

## Phase Profile

- bucket `0`: avg return `-0.0328`, positive sign agreement `0.399`, cumulative mean return `-0.0328`
- bucket `1`: avg return `0.0304`, positive sign agreement `0.419`, cumulative mean return `-0.0024`
- bucket `2`: avg return `-0.0290`, positive sign agreement `0.405`, cumulative mean return `-0.0314`
- bucket `3`: avg return `0.0202`, positive sign agreement `0.419`, cumulative mean return `-0.0112`
- bucket `4`: avg return `-0.0148`, positive sign agreement `0.410`, cumulative mean return `-0.0260`
- bucket `5`: avg return `0.0208`, positive sign agreement `0.420`, cumulative mean return `-0.0051`
- bucket `6`: avg return `0.0060`, positive sign agreement `0.420`, cumulative mean return `0.0009`
- bucket `7`: avg return `0.0284`, positive sign agreement `0.413`, cumulative mean return `0.0293`
- bucket `8`: avg return `0.0162`, positive sign agreement `0.402`, cumulative mean return `0.0455`
- bucket `9`: avg return `-0.0236`, positive sign agreement `0.405`, cumulative mean return `0.0218`
- bucket `10`: avg return `-0.0138`, positive sign agreement `0.405`, cumulative mean return `0.0080`
- bucket `11`: avg return `-0.0024`, positive sign agreement `0.402`, cumulative mean return `0.0056`

## Next-Step Read

- If `one_flip` or `two_flip` dominates, Hydrogel should move toward regime / phase detection.
- If `local_fair_mm` dominates, Hydrogel should stay in the moving-fair family and we should retune fair/execution, not build a regime trader.
- If `anchored_mean_reverter` dominates, the current anchor thesis is still competitive and only the execution shape is wrong.
