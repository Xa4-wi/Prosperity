# Product Analysis Tool

This tool profiles Prosperity capsule CSVs and classifies products into strategy archetypes.

It is set up to work directly with this repo:

- data root default: [Data](/Users/xavierwinkelmann/Prosperity/Data)
- competitive intel default: [COMPETITIVE_INTEL.md](/Users/xavierwinkelmann/Prosperity/Bots/Research/COMPETITIVE_INTEL.md)

## Files

- [capsule_product_diagnoser.py](/Users/xavierwinkelmann/Prosperity/Bots/Tools/Product_Analysis/capsule_product_diagnoser.py)
  - core profiler and markdown/JSON report writer
- [build_dashboard.py](/Users/xavierwinkelmann/Prosperity/Bots/Tools/Product_Analysis/build_dashboard.py)
  - builds a standalone HTML dashboard from the JSON summary
- [run_product_diagnosis.py](/Users/xavierwinkelmann/Prosperity/Bots/Tools/Product_Analysis/run_product_diagnosis.py)
  - wrapper that runs the diagnoser and dashboard together

## Output layout

- [output](/Users/xavierwinkelmann/Prosperity/Bots/Tools/Product_Analysis/output)
  - one subdirectory per run
- [logs](/Users/xavierwinkelmann/Prosperity/Bots/Tools/Product_Analysis/logs)
  - one log file per run

## Recommended usage

Run the full tool on a data capsule:

```bash
python3 Bots/Tools/Product_Analysis/run_product_diagnosis.py \
  --root Data/Tutorial \
  --run-name tutorial_capsule
```

Important:

- `--root` scans the directory recursively for all matching `prices_round_*_day_*.csv` and `trades_round_*_day_*.csv` files.
- That means it already merges multiple days into one combined diagnosis run.
- You do not need to run one file at a time if your capsule folder contains several day files.
- The merged result shows up in the report, JSON summary, and dashboard through:
  - file counts
  - `rounds_seen`
  - `days_seen`

That produces:

- `capsule_product_diagnosis_report.md`
- `capsule_product_diagnosis_summary.json`
- `dashboard/index.html`
- a run log in `Bots/Tools/Product_Analysis/logs/`

## Dashboard

After a run, you can serve the generated dashboard:

```bash
python3 -m http.server 8044 --directory Bots/Tools/Product_Analysis/output/tutorial_capsule/dashboard
```

Then open:

- `http://127.0.0.1:8044`

Or open the generated HTML directly from the run folder.
