# Round 2 Robustness Research Plan

## Goal
Find Round 2 improvements that survive randomized quote visibility.

The target is not:
- highest single upload
- prettiest single seed
- strongest visible-book aggression

The target is:
- higher mean
- better lower tail
- lower terminal-inventory risk
- less dependence on raw touch noise

Current strong reference:
- [TradervR2_26.py](Bots/Round2/TradervR2_26.py)

Primary score style:
- repeated-run distribution
- `mean`
- `std`
- `p25`
- `p10`
- robust score: `mean - 0.5 * std`

---

## Idea Map

### 1. Book-health score for Osmium
Hypothesis:
- the bot should trade differently when the visible book is sparse, one-sided, or unstable

Testable knobs:
- top-level depth thresholds
- recent one-sided memory
- stable-mid vs raw-touch divergence
- mid jump from last good mid

Variants:
- `bookHealth_mild`
- `bookHealth_strong`

Success:
- better lower tail without killing mean

### 2. Quote-thinning-resistant fair value
Hypothesis:
- fair should lean less on raw touch when the book is degraded

Fair candidates:
- anchor-heavier when book health is low
- median of anchor / stable / last good fair
- ignore suspiciously thin top level

Variants:
- `fair_anchorGuard`
- `fair_medianGuard`
- `fair_thinTopIgnore`

Success:
- lower terminal Ash variance
- better access/no-access consistency

### 3. Stateful vacuum recovery
Hypothesis:
- the dangerous part is often right after vacuum ends, not only during vacuum

Variants:
- `vacuumRecovery_cooldown`
- `vacuumRecovery_stableBars`

Success:
- fewer bad post-vacuum fills
- similar throughput

### 4. Side-specific starvation / reentry
Hypothesis:
- side-starved execution is a better trigger than global silence

Variants:
- `starvation_buySellPriority`
- `starvation_inventoryRepair`

Success:
- shorter avoidable plateaus
- no broad aggression leak

### 5. Passive-only markout buckets
Hypothesis:
- markout helps when it only shapes passive quoting, not everything

Variants:
- `markout_bucketedLight`
- `markout_bucketedStrong`

Success:
- better lower-tail maker quality
- no throughput collapse

### 6. Terminal Osmium inventory control
Hypothesis:
- lower-tail results suffer when leftover Ash inventory is marked badly

Variants:
- `terminalRisk_soft`
- `terminalRisk_asymmetric`

Success:
- lower terminal position variance
- better p10/p25

### 7. Access-safe aggression gating
Hypothesis:
- access-style behavior is only good when book health and conviction are both high

Variants:
- `accessGate_highHealth`
- `accessGate_highHealthHighConviction`

Success:
- preserve no-access robustness while keeping access upside

### 8. Plateau classification
Hypothesis:
- not every plateau is the same problem

Output:
- diagnostic report, not just bot variants

Classes:
- market dry
- self-throttled
- inventory blocked
- signal neutral
- stale toxicity

Success:
- actionable counts by class

### 9. Seed-stable alpha features
Hypothesis:
- some features improve only best-case seeds, others improve mean and lower tail

Output:
- distribution-ranked feature table

Success:
- keep only features that help mean + lower tail

### 10. Pepper robustness lightly
Hypothesis:
- Pepper should only get small execution refinements, not a rebuild

Variants:
- `pepper_cheapEarly`
- `pepper_lateTrim`

Success:
- tiny uplift or no harm

---

## Workflow

1. Use [TradervR2_26.py](Bots/Round2/TradervR2_26.py) as the research base.
2. Generate per-idea mild/strong variants from a single research-capable base.
3. Run repeated-run distribution scoring on each variant.
4. Keep only ideas that move:
   - mean by a useful amount
   - or p25/p10 by a useful amount
5. Promote only the ideas that clear the noise floor.

Noise-floor guidance:
- do not trust tiny single-seed wins
- prefer ideas that improve:
  - robust score
  - p25
  - p10

---

## Current expectation

Highest-probability research directions:
1. book health
2. fair robustness
3. vacuum recovery
4. side-specific starvation

Most likely diagnostic-only directions:
1. plateau classification
2. seed-stable feature ranking

Lower-priority live bot work:
1. Pepper micro tweaks

