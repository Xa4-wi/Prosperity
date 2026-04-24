# Round 3 Backtest Calibration

Raw local Round 3 replay is currently **not a trustworthy final ranking signal**.

The official logs for [TradervR3_6.log](Bots/Round3/TradervR3_6.log) and [TradervR3_7.log](Bots/Round3/TradervR3_7.log) showed a real inversion:

- local public replay preferred `R3_6`
- official submission result preferred `R3_7`

So for Round 3 we now use a two-step workflow:

1. Run the normal local backtest to get a candidate run and `metrics.json`.
2. Score that run with the Round 3 calibration layer built from official logs.

## Current improvement

The calibration is now **orientation-aware**.

That means:

- if a product is locally trustworthy in the same direction as official logs, keep it as-is
- if a product is locally informative but consistently inverted, flip its contribution instead of treating it as useless
- if a product is still inconsistent, downweight it hard or ignore it

This matters especially for `HYDROGEL_PACK`, where the uploaded official logs now show the local replay often has the **wrong sign**, not just the wrong magnitude.

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

1. runs the Rust Round 3 backtester in the faster `--carry --artifact-mode none` mode
2. finds the new `metrics.json`
3. applies the calibration samples from [round3_calibration_samples.json](Bots/Round3/round3_calibration_samples.json)
4. prints:
   - `raw_local_total`
   - `calibrated_total`
   - top calibrated product contributions
5. writes a saved report bundle under:
   - [round3_calibrated_backtests](Analysis/output/round3_calibrated_backtests)

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

## Refreshing the sample set

When new official `.log` files arrive, refresh the calibration sample list first:

```bash
python3 Analysis/scripts/refresh_round3_calibration_samples.py
```

That script scans:

- [Bots/Round3](Bots/Round3) for uploaded official logs
- [ProsperityRustBacktester/runs](ProsperityRustBacktester/runs) for the latest matching `metrics.json`

and rewrites:

- [round3_calibration_samples.json](Bots/Round3/round3_calibration_samples.json)

## Full Round 3 sweep

To rerun the whole Round 3 bot family with the calibrated selector:

```bash
python3 Analysis/scripts/run_round3_bot_sweep.py
```

That command:

1. discovers `Bots/Round3/TradervR3_*.py`
2. reruns each bot through the Rust backtester
3. scores each run with the calibration samples from [round3_calibration_samples.json](Bots/Round3/round3_calibration_samples.json)
4. writes:
   - [summary.json](Analysis/output/round3_all_bots_sweep/summary.json)
   - [report.md](Analysis/output/round3_all_bots_sweep/report.md)
   - per-bot calibrated bundles under [calibrated_runs](Analysis/output/round3_all_bots_sweep/calibrated_runs)

## What the calibration is doing

It is **not** trying to reconstruct the hidden book.

Instead, it asks:

- when local replay says bot B is better than bot A on product `X`,
- did the official portal logs agree?

If yes:
- keep that product as a usable ranking signal

If it is consistently reversed:
- flip the local contribution and fit it to the official log direction

If no:
- downweight that product to zero for now

## Current interpretation from R3_6 vs R3_7

From the refreshed sample set, the important practical read is:

- `HYDROGEL_PACK` currently behaves more like an **inverted signal** than a dead one
- `VELVETFRUIT_EXTRACT` is still only partially trustworthy
- the lower / middle voucher buckets remain the most usable anchors for local ranking

That interpretation is still **temporary and data-driven**, not permanent truth.
As more official logs arrive, rerun the calibration and let the weights update.

## Practical rule

For Round 3 bot selection:

- do **not** choose bots from raw local total alone
- first check the calibrated score
- if raw and calibrated disagree, trust the calibrated ranking more
