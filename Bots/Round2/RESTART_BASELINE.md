# Round 2 Restart Baseline

Baseline file:
- [TradervR2_12.py](/Users/xavierwinkelmann/Prosperity/Bots/Round2/TradervR2_12.py)

Purpose:
- clear out the layered `R2_9`/`R2_10` execution stack
- restart from a much simpler structure that is easy to reason about
- create a clean platform for new ideas instead of patching more edge cases into the old tree

## Market read from the public Round 2 data

### `INTARIAN_PEPPER_ROOT`
- still behaves like a rising deterministic carry product
- all three public days gain roughly `+1000` price units from open to close
- valid touch coverage stays around `92%`
- average spread is roughly `13-15`

So the restart baseline treats Pepper as:
- a schedule-driven long-bias carry engine
- with hard inventory limits
- and only mild sell relief on strong positive extension / very late session

### `ASH_COATED_OSMIUM`
- still behaves like a near-zero-drift local-fair product around `10000`
- valid touch coverage stays around `92%`
- average spread is roughly `16`
- one-sided books happen often enough to matter

So the restart baseline treats Osmium as:
- a simple anchor + stable-mid + micro local-fair maker
- with separate `take_alpha` and `quote_alpha`
- inventory skew
- simple one-sided-book fallback handling

## Structure of `TradervR2_12`

Shared helpers:
- `Book`
- `OrderManager`

Product modules:
- `PepperDriftTrader`
- `AshLocalFairTrader`

Design rules:
- no markout memory
- no access profile
- no layered re-entry stack
- no heavy regime tree
- no hidden donor logic from old variants

## Why this baseline is useful even though it is weaker

It is not meant to beat the current best branch immediately.
It is meant to give us:

1. a clear Pepper block
2. a clear Osmium block
3. a small number of understandable levers
4. a place where new ideas can be added one by one

## Best next build-up directions

The cleanest next ideas on top of this baseline are:
- Osmium markout-aware net edge
- Osmium stronger local fair from top-3 imbalance
- Osmium side-specific re-entry
- Pepper better target schedule
- Pepper cheaper accumulation timing

The key advantage now is that each of those can be tested on a simpler base without fighting old execution overlap.
