# Monte Carlo Viewer

This viewer lets you browse the saved Monte Carlo dashboard JSON files in `MonteCarloBacktester/backtests/` and compare multiple test runs side by side.

## What It Does

- lists all dashboard JSON files in the backtests directory
- shows summary stats for a selected run
- shows percentile bands and top/bottom sessions
- includes a comparison module for multiple saved tests

## Run It

From the repo root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 MonteCarloBacktester/monte_carlo_viewer/server.py --port 8012
```

Then open:

```text
http://127.0.0.1:8012
```

## Stop It

If the server is running in the terminal, stop it with:

```bash
Ctrl+C
```

If you started it in the background and want to stop the process manually, find it and kill it:

```bash
ps aux | grep "monte_carlo_viewer/server.py"
kill <PID>
```

## Notes

- `PYTHONDONTWRITEBYTECODE=1` avoids Python cache writes, which helps in restricted environments.
- By default, the viewer reads all `*.json` dashboard files from:

```text
MonteCarloBacktester/backtests
```

## Optional Arguments

You can point it at a different dashboard directory or use another port:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 MonteCarloBacktester/monte_carlo_viewer/server.py \
  --backtests-dir MonteCarloBacktester/backtests \
  --host 127.0.0.1 \
  --port 8012
```

## Example Workflow

1. Run a few Monte Carlo backtests so dashboard JSON files exist in `MonteCarloBacktester/backtests/`.
2. Start the viewer.
3. Select a test from the sidebar.
4. Tick multiple tests with the compare checkbox to inspect them side by side.

## Files

- server: [server.py](MonteCarloBacktester/monte_carlo_viewer/server.py)
- frontend: [index.html](MonteCarloBacktester/monte_carlo_viewer/index.html)
