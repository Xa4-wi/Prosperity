# Round 3 Workflow Tracker

Base bot: [TradervR3_7.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_7.py)

## Current Status

- Calibration layer: done
- Exact phased workflow: done
- Phase 1 Hydrogel diagnosis: done
- Phase 1 Velvet diagnosis: done
- Phase 2 strip metrics: pending
- Phase 3 fair rebuild: pending
- Phase 4 strip risk limits: pending
- Phase 5 overlay A/B validation: pending
- Phase 6 acceptance workflow enforcement: in progress
- Current Phase 1 follow-up bot: [TradervR3_8.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_8.py)

## Current Evaluation Rule

Use:

- [run_round3_calibrated_backtest.py](/Users/xavierwinkelmann/Prosperity/Analysis/scripts/run_round3_calibrated_backtest.py)

Do not select Round 3 bots from raw local total alone.

## Immediate Next Deliverables

1. Save the Phase 1 Hydrogel and Velvet classification report.
2. Validate [TradervR3_8.py](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_8.py) with the calibrated backtest flow.
3. If `R3_8` is directionally healthy, move to Phase 2 strip metrics before any new voucher alpha changes.
