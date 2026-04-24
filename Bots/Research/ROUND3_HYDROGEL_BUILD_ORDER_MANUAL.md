# Round 3 Hydrogel Build Order Manual

Current working context:

- Round 3 mainline workflow winner: [TradervR3_16.py](Bots/Round3/TradervR3_16.py)
- Hydrogel risk-control foundation: [TradervR3_15.py](Bots/Round3/TradervR3_15.py)

This manual is the concrete build order for the next Hydrogel iteration cycle.

The rule is simple:

```text
Measure first -> shape risk second -> tune execution third -> change fair/model last
```

Do not jump to fair-model redesign before Hydrogel has been measured correctly and the existing inventory / execution controls have been tuned.

## Core Goal

Improve `HYDROGEL_PACK` in a staged way without accidentally mixing together:

- diagnosis problems
- risk-shaping problems
- execution problems
- fair-model problems

Each phase should produce a clear written conclusion before the next phase starts.

## Phase A: Measure

Build the Hydrogel diagnostics notebook first.

Required outputs:

1. inventory-bucket PnL tables
2. inventory-bucket markout tables
3. proper Hydrogel reclassification note

What to measure:

- PnL by inventory bucket
- short-horizon markout by inventory bucket
- adverse selection while long vs while short
- fill quality when already stretched
- same-side accumulation behavior
- inventory aging behavior
- time-of-session behavior

Required interpretation:

- determine whether Hydrogel is mainly failing because of inventory shape, execution timing, or fair estimation
- reclassify Hydrogel based on evidence, not prior assumptions
- write the reclassification explicitly before any fair-model rewrite

Done criteria:

- We can point to the exact inventory zones where Hydrogel makes or loses money.
- We know whether large losses come from getting longer, getting shorter, holding too long, or flipping too late.
- Hydrogel has an explicit updated classification note.

Hard rule:

Do not change the Hydrogel fair model in Phase A.

## Phase B: Risk Shape

Once the measurement pass is complete, tune the current Hydrogel risk shape before touching the fair.

Keep these controls in the design:

- confidence-scaled target caps
- flatten-before-flip

Tune these controls next:

- same-side block thresholds
- inventory aging
- late-session cap shrink

What this phase is trying to answer:

- Are we allowing too much same-direction accumulation before blocking?
- Are we holding stretched inventory too long?
- Are we giving Hydrogel too much inventory budget late in the session?
- Does flatten-before-flip fire early enough to prevent ugly reversals?

Done criteria:

- Inventory tails are mechanically smaller.
- Same-side accumulation is more controlled.
- Late-session Hydrogel exposure is intentionally smaller than mid-session exposure.
- We have a cleaner inventory distribution before any execution retune.

Hard rule:

Do not treat execution issues as fair-model issues yet.

## Phase C: Execution

Only after the risk shape is acceptable should we retune the liquidation and quote behavior.

Tune:

- soft clear thresholds
- hard clear thresholds
- emergency clear size
- quote-size shrink when stretched

Focus:

- clearing earlier when inventory is unhealthy
- clearing harder when Hydrogel is badly stretched
- quoting smaller before the bot reaches the worst inventory states

Questions this phase must answer:

- Is soft clear happening soon enough to reduce inventory drag?
- Is hard clear strong enough when the position is already unhealthy?
- Is emergency clear too weak or too large?
- Should passive quote size shrink earlier as inventory stretches?

Done criteria:

- Hydrogel spends less time trapped in bad inventory states.
- Recovery from stretched inventory is faster and more consistent.
- Quote size adapts before the bot reaches the worst tails.

Hard rule:

If execution tuning fixes the problem, stop here and keep the current fair family.

## Phase D: Fair / Model Changes Only After A-C

Only if Hydrogel still misbehaves after measurement, risk-shape tuning, and execution tuning should the fair model change.

Change order:

1. less anchor
2. more stable / micro
3. maybe full local-fair classification

If the fair still looks wrong after that, test model alternatives such as:

- OU-style mean-reversion variants
- regime-based alternatives

What this phase means in practice:

- first reduce anchor dependence
- then increase the role of stable / microstructure-driven fair inputs
- then, if needed, fully reclassify Hydrogel as a local-fair product
- only after the classification and fair-family changes fail should OU or regime models be tested

Done criteria:

- A fair-model change is justified by surviving evidence from Phases A-C.
- We can explain why the old fair family failed.
- We can explain why the new fair family is more appropriate.

Hard rule:

Do not test OU or regime alternatives as a first response to bad Hydrogel behavior.

## Exact Sequence

Follow this order exactly:

1. Build Hydrogel diagnostics notebook.
2. Produce inventory-bucket PnL and markout tables.
3. Reclassify Hydrogel properly.
4. Keep confidence-scaled target caps.
5. Keep flatten-before-flip.
6. Tune same-side block thresholds.
7. Tune inventory aging.
8. Tune late-session cap shrink.
9. Tune soft clear and hard clear thresholds.
10. Tune emergency clear size.
11. Tune quote-size shrink when stretched.
12. Only then change the fair model if Hydrogel still misbehaves.
13. Start with less anchor.
14. Move to more stable / micro.
15. Maybe promote Hydrogel to full local-fair classification.
16. If fair still looks wrong, test OU / regime alternatives.

## Validation Rule

At every step:

- change one Hydrogel layer at a time
- measure the effect before moving to the next layer
- do not combine risk-shape and fair-model changes in the same version
- prefer the smallest change that fixes the observed failure mode

## One-Line Summary

The Hydrogel workflow is:

```text
Measure -> classify -> tune risk shape -> tune execution -> only then redesign fair/model
```
