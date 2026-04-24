# R3_38 Patch Spec — Hydrogel Cooldown / Passive Exit

## Objective

Stabilize `HYDROGEL_PACK` by preventing the churn behavior seen in `R3_37` while preserving the better entry quality from the `R3_28` Hydrogel base.

This patch is **not** a full new Hydrogel model. It is a control-layer patch.

The idea is:
- keep the **R3_28 Hydrogel entry logic**,
- remove the over-reactive emergency unwind behavior from `R3_37`,
- add **cooldown after exit**,
- add **passive-first exits**,
- add a **turnover budget guard**.

---

## Main diagnosis

The failure mode to fix is:

```text
enter -> clear too hard -> refill too soon -> clear too hard again
```

That means Hydrogel is no longer mainly suffering from bad entries. It is suffering from:
- exit churn,
- same-side re-entry too soon after unwind,
- excessive realized turnover,
- inventory control that becomes too aggressive in the wrong way.

So the next patch should optimize for:
- lower Hydrogel turnover,
- better realized buy/sell ordering,
- reduced second-half giveback,
- similar or slightly smaller gross Hydrogel alpha.

---

## Baseline to start from

Use **R3_28 Hydrogel** as the base, not `R3_37` Hydrogel.

Meaning:
- keep the `R3_28` target logic,
- keep `R3_28` flatten-before-flip,
- keep `R3_28` danger logic,
- do **not** carry over the most aggressive emergency-target behavior from `R3_37`.

Voucher / Velvet logic stays unchanged for this patch.

---

## Patch components

# 1. Exit cooldown

### Goal
Prevent immediate same-side re-entry after a Hydrogel unwind has started.

### New Hydrogel memory fields

```python
hydro_state["cooldown_side"]      # -1 for short-side block, +1 for long-side block, 0 for none
hydro_state["cooldown_bars"]      # remaining cooldown bars
hydro_state["cooldown_reason"]    # optional string/debug only
```

### Trigger
When Hydrogel enters a meaningful exit/unwind state and reduces inventory materially, start a cooldown on the side that was just reduced.

### Example trigger condition

```python
if exiting_long and pos_before > 80 and pos_after < pos_before - 20:
    cooldown_side = +1
    cooldown_bars = 6

if exiting_short and pos_before < -80 and pos_after > pos_before + 20:
    cooldown_side = -1
    cooldown_bars = 6
```

### Effect
During cooldown:
- block aggressive taking on the blocked side,
- block or heavily penalize same-side passive quoting,
- still allow opposite-side clearing / flattening,
- allow same-side re-entry only if **very strong reconfirmation** occurs.

### Reconfirmation override

```python
allow_same_side_reentry_during_cooldown only if:
    abs(regime_score) >= 2.4
    and abs(trend_score) >= 1.9
    and book_health is good
```

This should be rare.

---

# 2. Passive-first exit

### Goal
Most exits should reduce inventory with lower churn before the bot uses aggressive clearing.

### New exit states

```python
exit_state = "none" | "soft" | "hard"
```

### Soft exit conditions
Use soft exit when:
- position is moderately stretched, or
- trend/fair has faded, but
- there is not yet absolute danger.

### Soft exit behavior

```python
- shrink hold target
- disable same-side top-ups
- tighten opposite-side passive quote
- reduce same-side quote size by 50% to 80%
- aggressive clear only in small clip sizes
```

### Hard exit conditions
Use hard exit when:
- absolute inventory danger is high,
- trend/fair has materially broken,
- late-session pressure is strong,
- or turnover guard is already warning.

### Hard exit behavior

```python
- strongly shrink target (possibly toward 0)
- disable same-side quoting
- allow larger aggressive clear clips
- allow slightly negative EV clear if inventory is dangerous
```

### Key rule
Do **not** jump directly into hard exit unless the danger is real.

Soft exit should be the default.

---

# 3. Turnover budget guard

### Goal
Stop Hydrogel from becoming a self-harming churn engine.

### New Hydrogel memory fields

```python
hydro_state["recent_turnover"]
hydro_state["recent_signed_volume"]
hydro_state["recent_trade_count"]
```

Track these on a rolling basis over the last 10–20 bars.

### Suggested simplified implementation

```python
recent_turnover = decay * recent_turnover + abs(fill_qty)
recent_trade_count = decay * recent_trade_count + 1
```

with something like:

```python
decay = 0.85 to 0.92 per bar
```

### Turnover warning state

```python
turnover_warning = recent_turnover >= 80
turnover_danger  = recent_turnover >= 120
```

### Effect of turnover warning

When `turnover_warning` is true:
- cut same-side quote size,
- increase take threshold on both sides,
- disable any same-side refill unless strong reconfirmation.

When `turnover_danger` is true:
- force passive-first behavior,
- no same-side taking,
- only opposite-side reduction / maker behavior.

### Important
Turnover guard should be **Hydrogel-only**.

Do not apply it to the whole bot.

---

# 4. Absolute inventory danger override

### Goal
Make Hydrogel danger depend on **absolute exposure**, not only `position - target`.

### New thresholds

Suggested first-pass thresholds:

```python
ABS_DANGER_SOFT = 130
ABS_DANGER_HARD = 150
ABS_DANGER_MAX  = 180
```

### Behavior

If `abs(pos) >= ABS_DANGER_SOFT`:
- start soft exit bias,
- cut same-side size,
- increase urgency to flatten.

If `abs(pos) >= ABS_DANGER_HARD`:
- hard exit enabled,
- no same-side taking,
- more aggressive opposite-side clear.

If `abs(pos) >= ABS_DANGER_MAX`:
- target collapses toward 0 or a very small hold target,
- only clear / hedge actions remain.

### Why this is necessary
The current issue is that Hydrogel can still look “okay relative to target” while being objectively too large.

---

# 5. Keep flatten-before-flip

Do not remove this.

Retain the current rule shape:

```python
if pos * target < 0 and abs(pos) > 60:
    target = 0
```

This is still correct and should remain part of the base.

You may consider making it slightly stricter if churn remains high:

```python
if pos * target < 0 and abs(pos) > 40:
    target = 0
```

But do not change this in the first patch unless needed.

---

# 6. Do not change the Hydrogel fair model in this patch

This patch is **not** for:
- changing the anchor weight,
- changing stable/micro weights,
- changing the regime-score formula,
- changing Hydrogel classification.

Why:
- we want to isolate hold/exit control,
- not blur the results with a new fair model.

Hydrogel classification should be a separate workstream after this churn patch.

---

## Pseudocode outline

```python
# after computing target / caps / danger flags

cooldown_side = hydro_state.get("cooldown_side", 0)
cooldown_bars = hydro_state.get("cooldown_bars", 0)
recent_turnover = hydro_state.get("recent_turnover", 0.0)

turnover_warning = recent_turnover >= 80
turnover_danger = recent_turnover >= 120

abs_soft = abs(pos) >= 130
abs_hard = abs(pos) >= 150
abs_max = abs(pos) >= 180

# exit state selection
if abs_max or turnover_danger:
    exit_state = "hard"
elif abs_hard or fade_score > FADE_HARD:
    exit_state = "hard"
elif abs_soft or fade_score > FADE_SOFT:
    exit_state = "soft"
else:
    exit_state = "none"

# target override
if exit_state == "soft":
    target = hold_target_shrunk
elif exit_state == "hard":
    target = emergency_target

# cooldown block
same_side_block = False
if cooldown_bars > 0 and position_side_matches(cooldown_side, desired_trade_side):
    same_side_block = True

if same_side_block and not very_strong_reconfirmation:
    disable_same_side_take = True
    same_side_quote_size *= 0.2
    same_side_quote_edge += 2.0

# turnover guard
if turnover_warning:
    same_side_quote_size *= 0.5
    take_edge += 0.8

if turnover_danger:
    disable_same_side_take = True
    favor_opposite_side_clear = True

# after a real unwind fill
if unwind_fill_happened:
    cooldown_side = exited_side
    cooldown_bars = 6
```

---

## Validation plan

Run this patch only against `R3_28`.

### Metrics to compare

For Hydrogel specifically:
- total Hydrogel PnL
- realized Hydrogel average buy price
- realized Hydrogel average sell price
- Hydrogel trade count
- Hydrogel turnover
- time spent at `|pos| >= 150`
- time spent at `|pos| == 200`
- Hydrogel markout after first reaching `+150`
- Hydrogel markout after first reaching `-150`

For whole-bot stability:
- total final PnL
- max drawdown
- PnL at peak vs close
- close-to-peak giveback

### Success conditions

This patch is a success if it achieves at least **three** of the following:

1. lower Hydrogel turnover
2. fewer Hydrogel trades
3. better Hydrogel realized buy/sell ordering
4. less peak-to-close giveback
5. lower time at `|pos| >= 150`
6. equal or better total PnL

### Failure condition

If Hydrogel trade count falls but Hydrogel alpha disappears entirely, the patch is too conservative.

---

## Suggested parameter ranges

Start here:

```python
COOLDOWN_BARS = 6
TURNOVER_WARNING = 80
TURNOVER_DANGER = 120
FADE_SOFT = 0.9
FADE_HARD = 1.4
ABS_DANGER_SOFT = 130
ABS_DANGER_HARD = 150
ABS_DANGER_MAX = 180
SOFT_EXIT_SHRINK = 0.7
HARD_EXIT_SHRINK = 0.35
```

If churn still persists:
- increase `COOLDOWN_BARS` to `8`
- lower `TURNOVER_WARNING` to `70`
- make same-side re-entry override stricter

If Hydrogel becomes too passive:
- reduce `COOLDOWN_BARS` to `4`
- raise turnover thresholds
- allow smaller same-side passive quotes during soft exit

---

## What not to do in this patch

Do **not**:
- change voucher smile logic
- change `target_velvet_pos`
- loosen voucher thresholds globally
- rework Hydrogel classification
- add more predictive Hydrogel alpha terms

This patch should stay clean and focused.

---

## Recommended branch name

```text
TradervR3_38_hydroCooldownPassiveExit.py
```

---

## One-line summary

**Keep the `R3_28` Hydrogel entry logic, but make exits slower, safer, and harder to reverse immediately.**
