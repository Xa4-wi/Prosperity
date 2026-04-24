# Round 3 Tool Runbook

This is the fast-start guide for using the current tool stack as soon as Round 3 data lands.

The idea is simple:

1. Run `Product_Analysis` first to understand what the products are.
2. Run `olivia_tool` second to check whether a bot-overlay / insider-style pattern exists.
3. Inspect the dashboards and reports.
4. Turn the findings into the first Round 3 bot family instead of guessing from scratch.

## Tool map

### Product Analysis

Location:
- [Product_Analysis](/Users/xavierwinkelmann/Prosperity/Bots/Tools/Product_Analysis)

Best for:
- identifying product archetypes
- finding anchor behavior, drift/carry behavior, mean reversion, basket/option/conversion hints
- getting the first strategy family per product

Main command:

```bash
python3 Bots/Tools/Product_Analysis/run_product_diagnosis.py \
  --root Data/ROUND_3 \
  --run-name round3_capsule_initial
```

Expected outputs:
- markdown report
- JSON summary
- HTML dashboard
- run log

Output location:
- [Product_Analysis/output](/Users/xavierwinkelmann/Prosperity/Bots/Tools/Product_Analysis/output)

### Olivia detector toolkit

Location:
- [olivia_tool](/Users/xavierwinkelmann/Prosperity/Bots/Tools/olivia_tool)

Best for:
- detecting repeated lot-size / daily-extrema behavior
- finding possible Olivia-style or other informed bot overlays
- producing a runtime config for a live detector

Main command:

```bash
python3 Bots/Tools/olivia_tool/run_olivia_pipeline.py \
  --data-root Data \
  --round-dir ROUND_3 \
  --output-dir Bots/Tools/olivia_tool/output/olivia_round3
```

Expected outputs:
- trade feature table
- quantity clusters
- candidate scoring
- validated product summary
- runtime config JSON
- HTML dashboard

Output location:
- [olivia_tool/output](/Users/xavierwinkelmann/Prosperity/Bots/Tools/olivia_tool/output)

## Round 3 startup workflow

### Step 1. Check that the data exists

Usually we want something like:
- `Data/ROUND_3`

Quick check:

```bash
find Data/ROUND_3 -maxdepth 2 -type f | sort
```

If the official folder name differs, swap it into the commands below.

### Step 2. Run Product Analysis first

Use it to answer:
- Is a product anchored?
- Is it local-fair microstructure?
- Is it drift/carry?
- Is it mean reverting?
- Is there an obvious basket / conversion / option family?

Command:

```bash
python3 Bots/Tools/Product_Analysis/run_product_diagnosis.py \
  --root Data/ROUND_3 \
  --run-name round3_capsule_initial
```

Then inspect:
- report:
  [capsule_product_diagnosis_report.md](/Users/xavierwinkelmann/Prosperity/Bots/Tools/Product_Analysis/output/round3_capsule_initial/capsule_product_diagnosis_report.md)
- summary:
  [capsule_product_diagnosis_summary.json](/Users/xavierwinkelmann/Prosperity/Bots/Tools/Product_Analysis/output/round3_capsule_initial/capsule_product_diagnosis_summary.json)
- dashboard:
  [index.html](/Users/xavierwinkelmann/Prosperity/Bots/Tools/Product_Analysis/output/round3_capsule_initial/dashboard/index.html)

Questions to answer immediately:
- Which products are likely maker products?
- Which products are likely carry products?
- Which ones show warnings about bot overlays?
- Which products likely need a linked-product model?

### Step 3. Run the Olivia / bot-overlay pipeline

Use it to answer:
- Is there an informed actor pattern?
- Is there a repeated lot-size cluster?
- Does daily-extrema behavior repeat across products or days?
- Should the product be `FULL_FOLLOW`, `FOLLOW_AFTER_TRIGGER`, `BIAS_ONLY`, or `IGNORE`?

Command:

```bash
python3 Bots/Tools/olivia_tool/run_olivia_pipeline.py \
  --data-root Data \
  --round-dir ROUND_3 \
  --output-dir Bots/Tools/olivia_tool/output/olivia_round3
```

Then inspect:
- validated products:
  [validated_products.json](/Users/xavierwinkelmann/Prosperity/Bots/Tools/olivia_tool/output/olivia_round3/validated_products.json)
- runtime config:
  [runtime_config.json](/Users/xavierwinkelmann/Prosperity/Bots/Tools/olivia_tool/output/olivia_round3/runtime_config.json)
- dashboard:
  [index.html](/Users/xavierwinkelmann/Prosperity/Bots/Tools/olivia_tool/output/olivia_round3/dashboard/index.html)

Questions to answer immediately:
- Is there a strong per-product candidate cluster?
- Is the signal clean enough to trade directly?
- Is it only useful as a bias overlay?
- Is there nothing real and we should ignore it?

### Step 4. Build the first Round 3 strategy tree

Use the two tools together:

- `Product_Analysis` tells us what the product fundamentally is.
- `olivia_tool` tells us whether there is a bot-overlay regime sitting on top of that product.

That gives us a first-pass matrix like:

```text
anchored MM + no overlay         -> local-fair maker / taker
drift carry + no overlay         -> schedule / carry execution
basket / linked family           -> relationship model first
clean overlay + weak baseline    -> follow mode candidate
clean overlay + strong baseline  -> follow-after-trigger or bias-only
```

## Dashboard usage

### Product Analysis dashboard

Serve it locally:

```bash
python3 -m http.server 8044 --directory Bots/Tools/Product_Analysis/output/round3_capsule_initial/dashboard
```

Open:
- `http://127.0.0.1:8044`

### Olivia dashboard

Serve it locally:

```bash
python3 -m http.server 8033 --directory Bots/Tools/olivia_tool/output/olivia_round3/dashboard
```

Open:
- `http://127.0.0.1:8033`

## Server checks and shutdown

If `rg` is installed:

```bash
ps aux | rg 'http.server'
```

If `rg` is not installed:

```bash
ps aux | grep '[h]ttp.server'
```

Check a specific port:

```bash
lsof -nP -iTCP:8044 -sTCP:LISTEN
```

Stop a foreground server:

```bash
Ctrl+C
```

Stop a background server:

```bash
kill <PID>
```

## What to do with the findings

### If Product Analysis says:

- `anchored_market_maker`
  - start with anchor / stable-mid maker-taker logic
- `local_fair_microstructure`
  - prioritize local book state, microprice, imbalance, refill/vacuum handling
- `trending_drift_carry`
  - build a carry target / schedule engine, not a pure market maker
- `mean_reverting_ou`
  - test O-U / band-reversion behavior
- `option_family_black_scholes`
  - build option-family tooling early
- `conversion_candidate`
  - inspect conversion columns immediately
- `basket_etf_candidate`
  - build component fair / residual logic first

### If Olivia says:

- `FULL_FOLLOW`
  - consider a direct follow branch
- `FOLLOW_AFTER_TRIGGER`
  - keep baseline strategy until trigger, then hand over
- `BIAS_ONLY`
  - use as threshold shift / inventory tilt
- `IGNORE`
  - do not force the overlay into the bot

## Round 3 operating rhythm

Best practical sequence:

1. run both tools on the first capsule
2. inspect both dashboards
3. write a one-page product map
4. build the first baseline bot family
5. use later capsules to refine, not to discover from zero

That keeps us from getting dragged into manual spreadsheet archaeology on day one.
