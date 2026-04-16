# TradervR1_56 Robustness Tasks

## Task 1: De-risk Osmium aggression
Status: implemented in `TradervR1_56.py`
- raised `BASE_EDGE` toward zero
- raised `MIN_QUOTE_EDGE`
- reduced `FRONT_SIZE`
- lowered `SOFT_LIMIT`
- made `JOIN_EDGE` less aggressive

## Task 2: Fix the Osmium take ladder
Status: implemented in `TradervR1_56.py`
- rebuilt ladder to monotonic thresholds
- made sizes increase with edge

## Task 3: Turn on robustness architecture
Status: implemented in `TradervR1_56.py`
- enabled `REGIME_STYLE`
- enabled `SIZE_STYLE`
- enabled `SPLIT_FAIR_STYLE`

## Task 4: Separate slow fair and fast signal
Status: implemented in `TradervR1_56.py`
- `slow_fair` now drives reservation / inventory
- `fast_signal` only nudges taking, quoting, and regime routing

## Task 5: Make Osmium quote size state-dependent
Status: implemented in `TradervR1_56.py`
- quote size now reacts to spread, imbalance, toxicity, and inventory stretch
- calm mode gets larger size, bad states get smaller size

## Task 6: Add real Osmium regime routing
Status: implemented in `TradervR1_56.py`
- explicit modes:
  - `calm_mm`
  - `toxic_defense`
  - `dislocation_take`
  - `inventory_clear`
- mode changes both taking and quoting behavior

## Task 7: Coarsen more Osmium parameters
Status: implemented in `TradervR1_56.py`
- rounded / bucketed:
  - `LOCAL_MICRO_WEIGHT`
  - `LOCAL_IMBALANCE_BIAS`
  - `INVENTORY_CURVE`
  - `ADVERSE_IMBALANCE`
  - `STRONG_IMBALANCE`

## Task 8: Keep Pepper mostly unchanged
Status: implemented in `TradervR1_56.py`
- Pepper architecture preserved
- only light parameter cleanup applied

## Task 9: Add ablation hooks before new tuning
Status: prepared in `TradervR1_56.py`
- toggle hooks added for:
  - wall-mid blend
  - depth impact
  - nonlinear inventory
  - join behavior
  - take ladder
- next step is to run one-ablation-per-variant tests

## Task 10: Validate robustness, not only score
Status: current turn validation
- replay `v56` on all Round 1 days
- compare against `v54` / `v55`
- check total PnL, product split, and whether Pepper stays intact
