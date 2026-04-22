# Round 2 Risk Management Rebuild

This note turns the recent Round 2 risk discussion into an implementation plan for a cleaner, product-aware risk layer.

## Goal

Risk management should not make the bot passive.

It should:

- trade aggressively only when edge quality is trustworthy
- automatically reduce size when the book, inventory, or recent fill quality becomes fragile
- treat `ASH_COATED_OSMIUM` and `INTARIAN_PEPPER_ROOT` differently
- avoid blunt portfolio-wide throttles that choke the active Osmium engine

## Product Split

### Pepper

Risk style:
- `directional_carry`

Main risks:
- chasing rich positive shocks
- entering too expensively
- drifting too far below the desired long schedule
- accidentally fighting the carry with short inventory

What risk should do:
- improve entry quality
- penalize short inventory strongly
- allow normal long carry unless the state is truly broken

### Osmium

Risk style:
- `market_making_recycler`

Main risks:
- bad passive fills
- trusting a thinned / distorted visible book
- over-trading in one-sided or refill states
- ending with non-carry inventory too late

What risk should do:
- score whether the visible book is trustworthy
- scale size with volatility, disagreement, and inventory pressure
- penalize inventory increases late in the session
- keep passive markout narrow and side-specific

## Step Map

### 1. Book-health score

Keep book health as the first gate for Osmium.

It should drive:
- signal damping
- join suppression
- size reduction
- access aggression gating

### 2. Median-guard fair only when needed

Do not use the guarded fair all the time.

Use it only when:
- book health is weak
- touch looks noisy
- or a recent vacuum makes the touch unreliable

### 3. Volatility and fair-disagreement sizing

Use a short-horizon uncertainty layer from:
- `sigma` / mid-move EWMA
- fair disagreement between anchor, stable mid, last good fair, and chosen fair

This should mainly affect:
- quote size
- access aggression
- attack / press / defend mode

### 4. Terminal Osmium inventory pressure

Late in the session, penalize inventory-increasing Ash quotes and mildly favor recycling quotes.

This should:
- widen inventory-increasing quotes
- tighten inventory-reducing quotes
- reduce size of inventory-increasing passive quotes

### 5. Passive-only markout risk

Keep markout narrow:
- edge penalties on the passive side only
- size penalties on the passive side only

Do not let markout shut down the whole engine at once.

### 6. Osmium-only drawdown throttle

Track Osmium equity and drawdown from:
- own-trade cash
- marked position

Use drawdown only to:
- reduce aggression
- scale down size
- disable deeper / access-style expansion in bad states

Do not use a hard portfolio kill-switch by default.

### 7. Pepper entry-quality risk

Pepper should keep its carry backbone.

Risk should only:
- penalize rich-chase buying
- penalize short inventory harder than long inventory
- lightly reduce aggressive taking when recent Pepper equity is unstable

### 8. Confidence-gated aggression

Build one scalar from:
- book health
- signal conviction / agreement
- low toxicity
- low inventory stress
- low volatility

Then map to:
- `attack`
- `press`
- `balanced`
- `defend`

This should shape execution, not replace the fair model.

## Implementation Principles

- No blunt global order-pruning overlay.
- Keep risk local to the product engine.
- Use the same risk context inside the product before:
  - taking
  - quoting
  - sizing
  - access-style expansion
- Risk should mostly scale behavior, not switch the bot off.

## Success Criteria

The rebuilt risk layer is good if it:

- preserves Pepper carry behavior
- improves or preserves Ash public replay
- reduces Ash overreaction in weak-book states
- does not reintroduce the large PnL collapse seen in the first global risk overlay experiments
