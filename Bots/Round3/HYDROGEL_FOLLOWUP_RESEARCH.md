# Round 3 Hydrogel Follow-Up Research

This note combines:

- the Hydrogel oracle class study
- the official portal log comparison for `R3_27` vs `R3_28`
- the recent split tests of the harder-exit ideas

The goal is to answer:

1. what type of product Hydrogel most likely is
2. why the real `R3_28` improved even though the local backtester hated it
3. what the next Hydrogel research step should actually be

## 1. Product-Class Read

The oracle study still points in the same direction:

- `two_flip`: `167600.0`
- `one_flip`: `107600.0`
- `anchored_mean_reverter`: `71600.0`
- `hold`: `15200.0`
- `local_fair_mm`: `-154640.0`

Interpretation:

- Hydrogel does **not** look like a pure local-fair market-making product.
- Hydrogel does **not** look like a small quote-edge / recycler problem.
- Hydrogel looks much more like a **regime / phase** product.

That means the likely missing edge is:

- better state classification
- earlier regime identification
- better late-state exit or reversal handling

not:

- another round of quote-edge tuning
- more inventory penalties on the same scalar score

## 2. Day-Level Oracle Read

### Day 0

- best one-flip: `long -> short` at `377000`
- best two-flip: `short -> long -> short` at `109400`, then `377000`

### Day 1

- best one-flip: `long -> short` at `722400`
- best two-flip: `long -> short -> long` at `189400`, then `441200`

### Day 2

- best one-flip: `short -> long` at `280000`
- best two-flip: `short -> long -> short` at `280000`, then `722800`

Read:

- there is strong support for a **flip-based** Hydrogel thesis.
- day 2 in particular is the most relevant to the current live log work:
  - short early
  - long mid
  - short again late

That last point matters because the current Hydrogel family still mostly does:

- short early
- long later
- then trim late

It still does **not** really capture the late short leg.

## 3. Real Portal Log: `R3_27` vs `R3_28`

Official totals:

- `R3_27`: `9265.500`
- `R3_28`: `10577.375`

Official Hydrogel PnL:

- `R3_27`: `7855.625`
- `R3_28`: `9167.500`

So the real `R3_28` improvement is real, and it is almost entirely Hydrogel-driven.

### Drawdown comparison

- `R3_27` total peak: `19683.973` at `68900`
- `R3_27` max drawdown: `19580.541` to `93100`
- Hydrogel contribution over that window: `14853.125`

- `R3_28` total peak: `17612.473` at `68900`
- `R3_28` max drawdown: `14360.791` to `93100`
- Hydrogel contribution over that window: `9633.375`

Read:

- `R3_28` gave up some peak, but protected much more of it.
- the improvement came from a real Hydrogel drawdown reduction, not noise elsewhere.

## 4. What `R3_28` Actually Changed In The Real Log

### Early short phase

Very similar to `R3_27`.

### Mid long build

`R3_28` built a little less long than `R3_27`.

Hydrogel position checkpoints:

- `R3_27`
  - `52000`: `+105`
  - `68900`: `+200`
  - `72000`: `+198`
  - `75000`: `+195`
  - `93100`: `+188`
  - `99500`: `+200`

- `R3_28`
  - `52000`: `+100`
  - `68900`: `+148`
  - `72000`: `+122`
  - `75000`: `+63`
  - `93100`: `+141`
  - `99500`: `+141`

### Late phase

This is where the real improvement happened.

`R3_27`:

- stayed close to full long
- trimmed only slightly
- then refilled back toward full size

`R3_28`:

- sold aggressively from `148` down to `48` around `71900-72700`
- only later rebuilt to around `143`

So:

- `R3_28` is not better because it found a better early entry
- `R3_28` is better because it did a **real late long exit**

## 5. Why `R3_28` Still Is Not The Final Answer

Even though the real log improved, `R3_28` is still incomplete.

The oracle for day 2 suggests:

- best path is `short -> long -> short`

But `R3_28` does:

- short -> long -> trim long -> rebuild some long

So `R3_28` improves the second half by exiting part of the long,
but it still does **not** convert that late phase into a real short regime.

That means the next Hydrogel edge is probably not:

- “harder generic exit”

It is more likely:

- “late regime reclassification”
- “flat-to-short late-state transition”

## 6. Why The Local Backtester Misled Us On `R3_28`

The local fast carry replay showed `R3_28` as catastrophic:

- raw local Hydrogel: `-892995.0`

But the real portal log improved by about `+1311.9` total, almost all from Hydrogel.

That tells us:

- the local backtester is still not trustworthy enough for Hydrogel-only exit architecture
- especially when Hydrogel behavior changes execution shape materially

Practical consequence:

- use the official logs as the main judge for Hydrogel exit work
- use local replay only as a rough smoke test

## 7. What We Learned From Splitting `R3_28`

Split tests on top of `R3_27`:

- `R3_29`: extra `hold_cap` tightening only
- `R3_30`: sticky exit ladder only
- `R3_31`: execution hardening only

Results:

- `R3_29`: basically neutral
- `R3_30`: harmful
- `R3_31`: very harmful

So the safe takeaway is:

- broad danger-zone execution hardening is not the main win
- sticky unwind persistence is not the main win
- the real live improvement came from **some kind of earlier late-phase de-risking**, but not from the full `R3_28` stack

## 8. Best Current Hydrogel Hypothesis

Hydrogel is most likely:

- a **phase / regime** product
- with a meaningful late-state transition
- where a large part of the remaining edge is:
  - detect the late fade earlier
  - go flatter sooner
  - possibly turn short when the late phase confirms

That is different from:

- local-fair MM
- anchor-only mean reversion
- or “just hold the big long, but more carefully”

## 9. Recommended Next Hydrogel Research

### First priority

Build a discrete Hydrogel state machine, not a single scalar score.

Candidate states:

- `EARLY_SHORT`
- `BUILD_LONG`
- `HOLD_LONG`
- `LONG_FADE`
- `LATE_SHORT_CANDIDATE`

### Second priority

Add a late-state confirmation model using:

- trend fade from local peak
- return EMA sign
- anchor-gap collapse
- progress / timestamp bucket as a weak prior

### Third priority

Test three late-state actions explicitly:

1. hold long
2. flatten to near zero
3. reverse into small short

The key is to compare those actions directly, not just soften quote sizes.

## 10. Best Immediate Build Direction

The next Hydrogel branch should probably be:

- `R3_27` or `R3_28` log behavior as inspiration
- but implemented as:
  - a **late fade / late short candidate state**
  - not a harder sticky unwind
  - not a stronger danger-clear layer

In short:

**`R3_28` improved because it accidentally moved closer to the right Hydrogel phase behavior, not because the generic harder-exit architecture was correct as a whole.**
