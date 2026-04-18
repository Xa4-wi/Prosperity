# Round 2 Backtester

This is a separate Round 2 backtester workspace that still runs bot files directly from `Bots/`.

It is built around the manual in [Bots/Round2/round2_backtester_manual.md](/Users/xavierwinkelmann/Prosperity/Bots/Round2/round2_backtester_manual.md) and supports:

- public Round 2 price and trade CSV replay
- raw run artifact loading with `load_any()`
- run JSON parsing
- raw submission `.log` parsing
- `no_access` replay on the visible public book
- `access` replay with synthetic latent quotes
- `compare` mode to estimate `Δ_access`
- strategy, fill, and plateau diagnostics
- a browser dashboard for saved runs, graphs, and distributions

## Layout

- [run_backtest.py](/Users/xavierwinkelmann/Prosperity/Round2Backtester/run_backtest.py): CLI entry point
- [round2_backtester/loaders.py](/Users/xavierwinkelmann/Prosperity/Round2Backtester/round2_backtester/loaders.py): `load_any()` and schema normalization
- [round2_backtester/replay.py](/Users/xavierwinkelmann/Prosperity/Round2Backtester/round2_backtester/replay.py): replay engine and compare runner
- [round2_backtester/datamodel_bridge.py](/Users/xavierwinkelmann/Prosperity/Round2Backtester/round2_backtester/datamodel_bridge.py): bot import bridge into `Bots/`
- [round2_backtester/dashboard_server.py](/Users/xavierwinkelmann/Prosperity/Round2Backtester/round2_backtester/dashboard_server.py): local dashboard server
- [dashboard/index.html](/Users/xavierwinkelmann/Prosperity/Round2Backtester/dashboard/index.html): dashboard frontend

## Quick start

Run a compare backtest against the default Round 2 dataset:

```bash
python3 Round2Backtester/run_backtest.py backtest Bots/Trader.py
```

Run a single day:

```bash
python3 Round2Backtester/run_backtest.py backtest Bots/Round1/TradervR1_110.py --day -1
```

Switch queue model:

```bash
python3 Round2Backtester/run_backtest.py backtest Bots/Round1/TradervR1_110.py --queue-model touch_join
```

Replay only one mode:

```bash
python3 Round2Backtester/run_backtest.py backtest Bots/Round1/TradervR1_110.py --mode no_access
python3 Round2Backtester/run_backtest.py backtest Bots/Round1/TradervR1_110.py --mode access
```

Launch the dashboard for saved outputs:

```bash
python3 Round2Backtester/run_backtest.py dashboard
```

Or point it at a custom output root:

```bash
python3 Round2Backtester/run_backtest.py dashboard --output-root /tmp/r2bt_compare_smoke --port 8030
```

Inspect a prior artifact:

```bash
python3 Round2Backtester/run_backtest.py inspect Bots/Trader_Round1.log
python3 Round2Backtester/run_backtest.py inspect Bots/Logs/official_runs/imc_prosperity/100232/submission_100232_Traderv39_4.json
```

## Output

Single-mode runs write:

- `summary.json`
- `summary.txt`
- `step_log.csv`
- `product_steps.csv`
- `fills.csv`
- `diagnostics.json`

Compare mode writes:

- `no_access/`
- `access_seed_<seed>/`
- `compare_summary.json`

## Dashboard features

The dashboard is built to browse saved runs directly from the output folder and includes:

- run list with single-run and compare-run summaries
- compare-mode `Δ_access` histograms and per-seed PnL bars
- baseline vs access PnL envelope chart
- total equity and activity charts
- product-level price and fill overlays
- position, signal, spread, and markout distributions
- Osmium bucket diagnostics and plateau windows

## Current modeling assumptions

- Aggressive orders sweep visible levels immediately.
- Passive fills use an explicit queue model.
- `touch_join` is still a local approximation, not an official simulator.
- `access` mode adds synthetic quotes from empirical Round 2 level sizes and offsets.
- Resting orders are refreshed each decision step in the current implementation.

The default data root is:

- [Data/ROUND_2](/Users/xavierwinkelmann/Prosperity/Data/ROUND_2)
