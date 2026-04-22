# Round 1 research note: ASH_COATED_OSMIUM and INTARIAN_PEPPER_ROOT

This note summarizes the observed behavior of the two Round 1 products from the available price and trade files for days `-2`, `-1`, and `0`, and translates those observations into concrete design guidance for the trading engine.

The main conclusion is simple:

- `INTARIAN_PEPPER_ROOT` should be treated as a **drift / carry / execution** product.
- `ASH_COATED_OSMIUM` should be treated as a **local-fair / market-making / microstructure** product.

These two products should **not** share the same fair-value logic.

---

## Data used

This note is based on:
- `prices_round_1_day_-2.csv`
- `prices_round_1_day_-1.csv`
- `prices_round_1_day_0.csv`
- `trades_round_1_day_-2.csv`
- `trades_round_1_day_-1.csv`
- `trades_round_1_day_0.csv`

Important caveat:
some order-book snapshots are incomplete or contain missing quotes. Those rows should be filtered out before fitting any fair-value model.

---

# 1. INTARIAN_PEPPER_ROOT

## 1.1 Observed market behavior

`INTARIAN_PEPPER_ROOT` is the cleaner of the two products.

Across all three days, the price path is extremely close to a deterministic upward drift. A very strong approximation is:

```text
fair_pepper(day, timestamp) ≈ 10000 + 1000 * (day + 2) + timestamp / 1000