# Bots Tools

This folder is the toolbox root for standalone research and runtime utilities that sit next to the trading bots.

Each major tool should live in its own subdirectory so we can add more tool families without mixing code, outputs, and docs together.

## Current tools

### Round 3 quick start

Location:
- [ROUND3_RUNBOOK.md](Bots/Tools/ROUND3_RUNBOOK.md)

Use this first when a new round starts. It gives the exact command order for:
- product diagnosis
- Olivia / bot-overlay discovery
- dashboard serving
- first strategy triage

### Product Analysis

Location:
- [Product_Analysis](Bots/Tools/Product_Analysis)

What it contains:
- product archetype diagnosis from capsule CSVs
- markdown and JSON reports
- a standalone HTML dashboard
- per-run output folders and stored logs

Start here:
- [Product_Analysis/README.md](Bots/Tools/Product_Analysis/README.md)

### Olivia detector toolkit

Location:
- [olivia_tool](Bots/Tools/olivia_tool)

What it contains:
- offline discovery and scoring for Olivia-style insider patterns
- a live confidence-based runtime detector
- per-product policy helpers
- a standalone HTML dashboard generator

Start here:
- [olivia_tool/README.md](Bots/Tools/olivia_tool/README.md)

### Imported Prosperity backtester

Location:
- [imc_prosperity_4_backtester](Bots/Tools/imc_prosperity_4_backtester)

What it contains:
- Kevin Fu's Prosperity backtester cloned into our repo
- a repo-local launcher that handles `PYTHONPATH`
- an output folder for saved backtest logs

Start here:
- [imc_prosperity_4_backtester/README.md](Bots/Tools/imc_prosperity_4_backtester/README.md)
- launcher: [run_repo_backtest.py](Bots/Tools/imc_prosperity_4_backtester/run_repo_backtest.py)

### Rust Prosperity backtester

Location:
- [prosperity_rust_backtester](Bots/Tools/prosperity_rust_backtester)

What it contains:
- the Rust Prosperity backtester cloned into this repo
- upstream `Makefile` and CLI
- a repo-local launcher that maps to our `Bots/Round3` traders and `Data/` folders

Start here:
- [prosperity_rust_backtester/README.md](Bots/Tools/prosperity_rust_backtester/README.md)
- local usage guide: [prosperity_rust_backtester/README_PROSPERITY.md](Bots/Tools/prosperity_rust_backtester/README_PROSPERITY.md)
- launcher: [prosperity_rust_backtester/run_repo_backtester.sh](Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh)

## Suggested layout for future tools

```text
Bots/Tools/
  README.md
  olivia_tool/
  some_future_tool/
  another_research_tool/
```

Rule of thumb:
- keep each tool self-contained
- keep each tool’s outputs inside that tool’s own folder when possible
- keep the top-level `Bots/Tools` directory as a clean index, not a dumping ground
