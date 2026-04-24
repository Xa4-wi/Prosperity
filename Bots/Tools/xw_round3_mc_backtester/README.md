# XW Round 3 Monte Carlo Backtester

This tool is a Round 3 focused Python backtester for `HYDROGEL_PACK`, `VELVETFRUIT_EXTRACT`, and the `VEV_*` voucher strip.

It is meant to complement the Rust backtester when we want:

- execution uncertainty instead of one deterministic replay
- fill behavior calibrated from our real official logs
- direct compatibility with the bots in `Bots/Round3`
- quick Monte Carlo distributions instead of one noisy score

## What It Does

The tool:

- loads `prices_round_3_day_*.csv` and `trades_round_3_day_*.csv`
- imports a real bot file from `Bots/Round3/*.py`
- rebuilds `TradingState` objects using `Bots/datamodel.py`
- simulates aggressive fills against the visible book
- simulates passive fills probabilistically
- calibrates passive fill behavior from our official `TradervR3_*.log` files
- runs many Monte Carlo paths and writes a summary bundle

## Current Modeling Assumptions

This is still a research backtester, not a perfect exchange simulator.

The main assumptions are:

- aggressive orders fill against visible best levels immediately
- passive fills depend on:
  - where the quote sits relative to the book
  - inferred contra flow from the tape
  - empirical fillability calibrated from official logs
- final PnL is marked to the latest observed mid

That means it is most useful for:

- ranking branches
- stress testing execution sensitivity
- seeing whether a bot is only good under one very narrow fill path

## Run It

From the repo root:

```bash
python3 Bots/Tools/xw_round3_mc_backtester/run_backtest.py \
  Bots/Round3/TradervR3_45.py \
  --days 0 1 2 \
  --sims 64 \
  --carry-state
```

Compare directly against an official log:

```bash
python3 Bots/Tools/xw_round3_mc_backtester/run_backtest.py \
  Bots/Round3/TradervR3_45.py \
  --days 0 1 2 \
  --sims 64 \
  --carry-state \
  --official-log Bots/Round3/TradervR3_45.log
```

Use a thinner replay for faster iteration:

```bash
python3 Bots/Tools/xw_round3_mc_backtester/run_backtest.py \
  Bots/Round3/TradervR3_45.py \
  --days 0 1 2 \
  --tick-step 5 \
  --sims 32
```

## Outputs

Each run writes:

- `summary.json`
- `report.md`
- `paths.csv`

to a timestamped folder under:

- `Bots/Tools/xw_round3_mc_backtester/output`

## Suggested Workflow

1. Run the branch with `--sims 64` or `--sims 128`.
2. Compare the mean and lower tail, not just the best path.
3. Compare against the matching official log when available.
4. Use the same seed family when comparing two nearby branches.
5. Only then decide whether a branch is actually safer or better.

## Notes

- Official portal logs use about `0..100000` timestamps for one day.
- The historical CSV files are also one day each, but use a larger internal timestamp scale.
- This tool preserves the per-file day structure and can either reset state per day or carry state across days.
