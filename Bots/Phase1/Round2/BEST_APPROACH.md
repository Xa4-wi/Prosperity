# Round 2 Best Approach Map

## Goal

Use Round 2 as a thresholded optimization problem:
- keep `INTARIAN_PEPPER_ROOT` as the base PnL engine
- use `ASH_COATED_OSMIUM` as the marginal access monetizer
- test research-backed execution upgrades as isolated branches instead of mixing everything at once

## Research Themes

### 1. Net-edge market making
Idea:
- passive fills are not free
- a quote should be judged on raw edge minus expected post-fill drift

Best fit:
- DeLise, *The Negative Drift of a Limit Order Fill*
- Avellaneda–Stoikov reservation-price logic

What to test:
- side-specific expected markout
- regime-conditioned markout buckets
- quote/size penalties driven by expected markout, not only by raw toxicity

Bot:
- [TradervR2_4.py](Bots/Round2/TradervR2_4.py)

### 2. Higher-rank microprice / OFI local fair
Idea:
- short-horizon price movement is better explained by order flow imbalance and microprice than by anchor-only fair
- top-2/top-3 depth should matter, not just level-1

Best fit:
- Cont–Kukanov–Stoikov, *The Price Impact of Order Book Events*
- Stoikov, *The Micro-Price: A High Frequency Estimator of Future Prices*

What to test:
- deeper microprice using top-3 levels
- higher-rank imbalance added to fast signal
- stronger tight-book local-fair estimator

Bot:
- [TradervR2_5.py](Bots/Round2/TradervR2_5.py)

### 3. Conditional throughput expansion
Idea:
- do not turn aggression up globally
- when stable-gap, imbalance, and trade confirmation all agree, allow more throughput

Best fit:
- Cartea–Wang style alpha-conditioned market making
- Pulido–Rosenbaum–Sfendourakis style asymmetric quoting under imbalance

What to test:
- stronger join behavior only in strongest aligned states
- larger front size only in strongest aligned states
- extra sweep depth only in strongest aligned states

Bot:
- [TradervR2_6.py](Bots/Round2/TradervR2_6.py)

### 4. Drift execution / catch-up schedule
Idea:
- Pepper is not a second market maker
- it is a carry engine that should buy faster when behind schedule and prices are favorable, but avoid chasing when shock is adverse

Best fit:
- Lorenz–Schied drift-sensitive execution
- Lehalle–Neuman signal-conditioned execution

What to test:
- schedule target versus current Pepper inventory
- buy catch-up when behind and shock is favorable
- softer/earlier late-session trimming when ahead and overextended

Bot:
- [TradervR2_7.py](Bots/Round2/TradervR2_7.py)

## Baseline

Current public-data Round 2 baseline:
- [TradervR2_2.py](Bots/Round2/TradervR2_2.py)

Why it stays the baseline:
- strongest Pepper backbone so far
- access-style Osmium layer is alive without obviously damaging public replay
- explicit `25000` access bid for direct auction testing

## Evaluation Plan

For each branch:
- compare total PnL
- compare Pepper and Osmium split
- note whether public replay changes at all
- keep an eye on whether the branch is:
  - public-data live
  - official-path only
  - or clearly harmful

## Sources

- Avellaneda–Stoikov, *High-frequency trading in a limit order book*:
  https://people.orie.cornell.edu/sfs33/LimitOrderBook.pdf
- Cont–Kukanov–Stoikov, *The Price Impact of Order Book Events*:
  https://arxiv.org/abs/1011.6402
- Stoikov, *The Micro-Price*:
  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2970694
- DeLise, *The Negative Drift of a Limit Order Fill*:
  https://arxiv.org/abs/2407.16527
