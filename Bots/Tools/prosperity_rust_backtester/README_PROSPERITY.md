# Prosperity Repo Usage

This copy of `prosperity_rust_backtester` is installed inside this repo at:

- [Bots/Tools/prosperity_rust_backtester](/Users/xavierwinkelmann/Prosperity/Bots/Tools/prosperity_rust_backtester)

The upstream README assumes a standalone checkout with its own `datasets/` and `traders/` workflow.

In this repo, the important local paths are:

- traders: [Bots/Round3](/Users/xavierwinkelmann/Prosperity/Bots/Round3)
- datasets:
  - [Data/Tutorial](/Users/xavierwinkelmann/Prosperity/Data/Tutorial)
  - [Data/ROUND_1](/Users/xavierwinkelmann/Prosperity/Data/ROUND_1)
  - [Data/ROUND_2](/Users/xavierwinkelmann/Prosperity/Data/ROUND_2)
  - [Data/ROUND_3](/Users/xavierwinkelmann/Prosperity/Data/ROUND_3)
  - [Data/ROUND_4](/Users/xavierwinkelmann/Prosperity/Data/ROUND_4)

## One-time setup

On macOS:

```bash
xcode-select --install
curl https://sh.rustup.rs -sSf | sh
source "$HOME/.cargo/env"
cargo --version
python3 --version
```

If you already have `cargo`, you are ready.

## Fastest way to use it in this repo

Use the local wrapper:

```bash
Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh
```

Defaults:

- trader: newest `Bots/Round3/*.py`
- dataset: `Data/ROUND_3`

## Common commands

Run the newest Round 3 trader on all Round 3 days:

```bash
Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh
```

Run a specific trader on all Round 3 days:

```bash
Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh Bots/Round3/TradervR3_87.py
```

Run only Round 3 day 2:

```bash
Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh Bots/Round3/TradervR3_87.py round3 --day 2
```

Run Round 2:

```bash
Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh Bots/Round3/TradervR3_87.py round2
```

Run Round 4:

```bash
Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh Bots/Round4/TradervR4_1.py round4
```

Run the tutorial data:

```bash
Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh Bots/Round3/TradervR3_87.py tutorial
```

Run with full product output and persisted artifacts:

```bash
Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh \
  Bots/Round3/TradervR3_87.py \
  round3 \
  --products full \
  --persist
```

Run a portal submission log directly:

```bash
Bots/Tools/prosperity_rust_backtester/run_repo_backtester.sh \
  Bots/Round3/TradervR3_87.py \
  Bots/Round3/TradervR3_87.log
```

## Where output goes

The backtester writes runs under:

- [Bots/Tools/prosperity_rust_backtester/runs](/Users/xavierwinkelmann/Prosperity/Bots/Tools/prosperity_rust_backtester/runs)

By default, fast runs still write:

- `metrics.json`
- `submission.log`

With `--persist`, it can also write larger diagnostic artifacts.

## Direct upstream commands

If you want to use the upstream commands directly from inside the tool directory:

```bash
cd Bots/Tools/prosperity_rust_backtester
make help
make doctor
```

For repo-local backtests, the wrapper is better because it points at this repo's real trader and data paths.
