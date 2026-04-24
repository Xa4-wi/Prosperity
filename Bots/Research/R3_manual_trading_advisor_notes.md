# Round 3 Advisor Notes — Manual Trading / Practical Decision Notes

## Important limitation

The advisor text you provided is overwhelmingly about the **voucher/options side**.
It does **not** contain direct new information about the manual `Ornamental Bio-Pod` offers.

So this file separates two things:

1. what the advisor text implies for any manual decision-making
2. what is **not** actually supported by the text and still needs market-specific evidence

---

## What the advisor does tell us that matters manually

Even though the text is about options, the advisor is really teaching four general decision rules.

## Rule 1 — Price from structure, not from headline numbers
Do not look only at a price and ask “is this high or low?”
Instead ask:
- what underlying value supports it?
- what cross-product structure surrounds it?
- what does the market seem to be implying?

Manual trading translation:
- for any manual offer, first estimate the **embedded value**
- then compare that with the quoted/opportunity price

## Rule 2 — Misalignment is not automatically opportunity
The advisor explicitly says that a deviation is not enough.
Something can look off and still not be worth trading.

Manual translation:
Only act when you can answer all three:
- what is misaligned?
- why is it misaligned?
- why should it converge before it hurts you?

## Rule 3 — Size should reflect conviction
The advisor is very strong on this point.
Bigger apparent edge does not mean infinite size.

Manual translation:
- stronger edge -> larger size
- weaker edge -> smaller size
- uncertain edge -> maybe no trade

## Rule 4 — Conviction is not certainty
The market can stay misaligned longer than expected.

Manual translation:
- use staggered offers
- avoid putting the whole manual edge into one price level
- preserve downside if your read is wrong

---

## How to use this for Bio-Pods manual offers

Again: the advisor text does NOT give Bio-Pod-specific valuation.
But it does tell you how to think.

### Manual offer framework
For each possible Bio-Pod offer, estimate:

```text
expected resale / conversion value
- purchase cost
= expected gross edge
```

Then apply confidence and execution uncertainty:

```text
conviction-adjusted edge = expected gross edge * confidence
```

Then choose two offers:

### Offer A — Value-maximizing bid
This is your best estimate of the highest price that still leaves enough edge.

### Offer B — Coverage / discovery bid
This is a second offer that either:
- catches slightly worse but still acceptable value,
- or learns where acceptance may be if quantities are uncertain.

### General principle
Do not use two offers that are nearly identical.
One should be your “main” value bid, the other should change your coverage.

---

## Possible two-offer styles

### Style 1 — Tight value ladder
Use when you are confident in fair value.

```text
Offer A: near your best estimate of fair minus target margin
Offer B: slightly lower, for extra edge if available
```

### Style 2 — Split confidence ladder
Use when fair value is uncertain.

```text
Offer A: conservative / safer
Offer B: more aggressive / higher fill chance
```

### Style 3 — Quantity diversification
Use when you are unsure how many counterparties may hit your price.

```text
Offer A: better price, lower size target mentally
Offer B: slightly worse price, backup fill path
```

---

## What the advisor text does NOT give us

The advisor notes do NOT tell us:
- how many Gardeners there are
- whether their behavior is strategic or passive
- whether Bio-Pod value is fixed or variable
- how your two offers are matched
- what exact acceptance logic they use

So for the manual side, this text is mostly a **decision discipline guide**, not a direct alpha source.

---

## Practical manual checklist

Before choosing your two manual offers:

```text
1. estimate value per Bio-Pod after conversion
2. define minimum acceptable profit margin
3. define a confidence score in that value estimate
4. choose one main bid and one backup / coverage bid
5. ensure the worse-priced bid still has positive conviction-adjusted edge
6. avoid overcommitting both offers to the same assumption
```

---

## If more advisor info appears later

Manual-side information would become much more useful if future advisor notes mention:
- Gardener behavior
- acceptance mechanics
- resale/conversion pricing of Bio-Pods
- timing / quantity asymmetry
- hidden thresholds

If you get that kind of text later, it should be added here, not mixed with the voucher algo notes.

---

## Final takeaway

From the current advisor text, the manual-side lesson is:

**Do not place manual offers just because something looks attractive. Place them only when the estimated embedded value, confidence, and downside all justify the size and price.**

The options text mostly strengthens your discipline for manual decisions, but it does not yet give a Bio-Pod-specific edge.
