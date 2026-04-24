# Round 3 Backtest Calibration

Raw local Round 3 replay is currently **not a trustworthy final ranking signal**.

The official logs for [TradervR3_6.log](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_6.log) and [TradervR3_7.log](/Users/xavierwinkelmann/Prosperity/Bots/Round3/TradervR3_7.log) showed a real inversion:

- local public replay preferred `R3_6`
- official submission result preferred `R3_7`

So for Round 3 we now use a two-step workflow:

1. Run the normal local backtest to get a candidate run and `metrics.json`.
2. Score that run with the Round 3 calibration layer built from official logs.

## Current tool

Use:

```bash
python3 Analysis/scripts/round3_backtest_calibration.py \
  --sample R3_6 ProsperityRustBacktester/runs/backtest-1777030405143/metrics.json Bots/Round3/TradervR3_6.log \
  --sample R3_7 ProsperityRustBacktester/runs/backtest-1777030744037/metrics.json Bots/Round3/TradervR3_7.log \
  --sample R3_8 ProsperityRustBacktester/runs/backtest-1777036650303/metrics.json Bots/Round3/TradervR3_8.log \
  --candidate NEW_BOT /path/to/new/metrics.json
```

## One-command workflow

The usable wrapper is:

```bash
python3 Analysis/scripts/run_round3_calibrated_backtest.py Bots/Round3/TradervR3_7.py
```

That command:

1. runs the Rust Round 3 backtester
2. finds the new `metrics.json`
3. applies the calibration samples from [round3_calibration_samples.json](/Users/xavierwinkelmann/Prosperity/Bots/Round3/round3_calibration_samples.json)
4. prints:
   - `raw_local_total`
   - `calibrated_total`
   - top calibrated product contributions
5. writes a saved report bundle under:
   - [round3_calibrated_backtests](/Users/xavierwinkelmann/Prosperity/Analysis/output/round3_calibrated_backtests)

To calibrate an existing run without rerunning the Rust replay:

```bash
python3 Analysis/scripts/run_round3_calibrated_backtest.py \
  Bots/Round3/TradervR3_7.py \
  --skip-backtest \
  --metrics ProsperityRustBacktester/runs/backtest-1777030744037/metrics.json
```

It produces:

- a markdown report
- a JSON summary
- product-level reliability weights
- a `calibrated_total` score for each candidate

## Full Round 3 sweep

To rerun the whole Round 3 bot family with the calibrated selector:

```bash
python3 Analysis/scripts/run_round3_bot_sweep.py
```

That command:

1. discovers `Bots/Round3/TradervR3_*.py`
2. reruns each bot through the Rust backtester
3. scores each run with the calibration samples from [round3_calibration_samples.json](/Users/xavierwinkelmann/Prosperity/Bots/Round3/round3_calibration_samples.json)
4. writes:
   - [summary.json](/Users/xavierwinkelmann/Prosperity/Analysis/output/round3_all_bots_sweep/summary.json)
   - [report.md](/Users/xavierwinkelmann/Prosperity/Analysis/output/round3_all_bots_sweep/report.md)
   - per-bot calibrated bundles under [calibrated_runs](/Users/xavierwinkelmann/Prosperity/Analysis/output/round3_all_bots_sweep/calibrated_runs)

## What the calibration is doing

It is **not** trying to reconstruct the hidden book.

Instead, it asks:

- when local replay says bot B is better than bot A on product `X`,
- did the official portal logs agree?

If yes:
- keep that product as a usable ranking signal

If no:
- downweight that product to zero for now

## Current interpretation from R3_6 vs R3_7

From the current labeled pair:

- usable local ranking signal:
  - `VEV_5000`
  - `VEV_5100`

- misleading local ranking signal:
  - `HYDROGEL_PACK`
  - `VELVETFRUIT_EXTRACT`
  - `VEV_4000`
  - `VEV_4500`
  - `VEV_5200`
  - `VEV_5300`
  - `VEV_5400`
  - `VEV_5500`

That list should be treated as **temporary and data-driven**, not permanent truth.
As more official logs arrive, rerun the calibration and let the weights update.

## Practical rule

For Round 3 bot selection:

- do **not** choose bots from raw local total alone
- first check the calibrated score
- if raw and calibrated disagree, trust the calibrated ranking more
