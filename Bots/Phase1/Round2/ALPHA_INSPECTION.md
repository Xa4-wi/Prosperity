# Round 2 Alpha Inspection

## Scope

This note inspects the alpha path in:
- current visible Round 2 branch: [TradervR2_3.py](Bots/Round2/TradervR2_3.py)
- stronger later branch kept in archive: [TradervR2_9.py](Bots/Round2/archive/TradervR2_9.py)

The goal is to understand:
- where alpha is created
- where it gets clipped or damped
- where execution actually turns that alpha into PnL

## `ASH_COATED_OSMIUM` Alpha Path

### In `R2_3`

Signal construction lives in:
- [_stable_mid](Bots/Round2/TradervR2_3.py#L233)
- [_slow_fair](Bots/Round2/TradervR2_3.py#L254)
- [_trade_confirmation](Bots/Round2/TradervR2_3.py#L261)
- [_signal_components](Bots/Round2/TradervR2_3.py#L297)

What it does:
- `slow_fair` is anchored:
  - `0.45 * 10000`
  - `0.55 * stable_mid`
- `stable_mid` is a top-3 popular-price mid with wall-mid blending
- fast signal is built from:
  - L1 microprice gap
  - imbalance gap
  - depth-adjusted imbalance
  - stable-gap agreement/disagreement bonuses
  - trade confirmation bonus when it aligns with imbalance

Then it gets compressed into:
- `take_signal`
- `quote_signal`
- `signal_conviction`

### In `R2_9`

The stronger Osmium branch adds:
- [_deep_micro_signal](Bots/Round2/archive/TradervR2_9.py#L269)
- higher-rank depth imbalance inside [_signal_components](Bots/Round2/archive/TradervR2_9.py#L321)

This is the key improvement:
- `R2_3` mostly uses level-1 micro/imbalance
- `R2_9` adds top-3 depth structure directly into the fast signal

That matches the research direction well and is likely why the public replay improved slightly in the `R2_5/R2_9` family.

## Where Osmium Alpha Gets Weaker

### 1. One signal drives both taking and quoting

In both branches:
- the same clipped fast signal becomes both `take_signal` and `quote_signal`
- only the weights differ

That means:
- if a feature is good for deciding direction but bad for deciding passive quote placement,
  the bot still uses it for both

This is probably the biggest current alpha bottleneck.

Better structure:
- `take_alpha`
- `quote_alpha`
- `conviction`

separately.

### 2. Conviction is mostly a nudge, not a regime

`signal_conviction` affects:
- take thresholds a bit
- quote edges a bit
- front size a bit
- access / re-entry activation gates

But most of the time it does not create a real execution-state jump.

So the current architecture does:
- detect good states
- but often only responds mildly

That is why the throughput-expansion branch was directionally good but mostly inert in public replay.

### 3. Markout is execution-side only

Markout enters later:
- after fills
- as quote/take penalties

It does **not** currently reshape the signal itself.

So right now the Osmium logic says:
- “this state points up”
- then later “but fills here have been bad”

instead of:
- “the net alpha for this state is weaker because expected fill quality is poor”

That is a cleaner next research route than adding more fair-value constants.

## `INTARIAN_PEPPER_ROOT` Alpha Path

Pepper alpha lives in:
- [build_orders](Bots/Round2/archive/TradervR2_9.py#L1180)

Core pieces:
- `trend_line = anchor + drift * timestamp`
- `fair` blends:
  - trend line
  - raw mid
  - micro
  - imbalance flow fair
  - residual correction
  - positive lookahead bonus
- `edge = fair - mid`
- `target` starts from carry, then gets:
  - early long bias
  - edge target scale
  - z-score buy bonus / sell penalty
  - bullish imbalance bonus

So Pepper alpha is not really “predict price” in a rich way.
It is:
- deterministic carry
- plus timing nudges around residual and microstructure

That still fits the product well.

## Where Pepper Alpha Gets Weaker

### 1. Fair and target are tightly coupled

Pepper uses one fair path to do all of:
- decide direction
- decide target inventory
- drive take edges
- drive quote placement

That makes the engine simple, but it also means:
- if the fair is a bit too high,
  everything becomes too accumulation-friendly at once

The lighter `R2_9` fix helped by:
- enforcing the buy cap more honestly
- adding mild exit relief

But the alpha source itself is still basically one coupled fair/target model.

### 2. Alpha is mostly “long carry until proven otherwise”

This is not necessarily wrong.
But it means the main live question is:
- when should Pepper *not* add
- when should it scale out earlier

That is an execution-schedule problem more than a fair-model problem.

## What Looks Most Promising

### Osmium

Best next alpha-inspection directions:

1. Split alpha into:
- `take_alpha`
- `quote_alpha`
- `conviction`

2. Add net-alpha diagnostics:
- raw fast signal
- expected markout
- net signal after markout adjustment

3. Inspect disagreement states explicitly:
- stable-gap vs imbalance
- deep micro vs level-1 micro
- quote alpha sign vs take alpha sign

4. Promote only the best states into true execution regimes:
- not bigger global aggression
- but real one-state jumps when alignment is strongest

### Pepper

Best next alpha-inspection directions:

1. Separate:
- target alpha
- execution alpha

2. Log how often the target is effectively saturated

3. Inspect where:
- `edge > 0`
- but buy cap / target cap blocks more accumulation

4. Inspect where:
- positive z-score extension happens
- but the bot still does not scale out enough

## My Read

The biggest current opportunity is still on the Osmium side.

Not because the fair is totally wrong.
But because:
- the bot now has a decent signal stack
- and the next gain is likely in how that alpha is separated and routed into execution

The shortest summary is:

**right now the bot is better at building a single combined signal than it is at deciding how different signals should be used.**

That is the strongest reason to inspect the alpha route next.
