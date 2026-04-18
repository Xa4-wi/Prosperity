# Round 2 build-up plan from the clean rewrite

## Goal
Build up from the clean rewrite (`TradervR2_12.py`) in a controlled order so we keep the code understandable while adding back only the layers that have the highest probability of improving Round 2 PnL.

This plan is deliberately staged. Each stage should be tested on its own before the next one is added.

---

## Which base to use
Use `TradervR2_12.py` as the **structural base**.

Reason:
- clean `Book`
- clean `OrderManager`
- Pepper and Osmium split is readable
- memory handling is simple
- `bid()` is isolated
- much easier to debug than the later “everything at once” branches

Do **not** use the weaker experimental round-2 branches as the main base.
Use them only as feature donors.

---

## What to preserve from the base

### Pepper
Keep Pepper close to the clean rewrite for now.
It should remain:
- drift/carry driven
- schedule based
- long-biased early
- conservative on selling

Do not spend major effort on Pepper until Osmium is stronger.
Pepper can still be refined later, but it is not the main marginal edge.

### Osmium
Keep these rewrite ideas as the permanent skeleton:
- stable anchor around 10000
- local-fair concept
- separation of fair / take / quote logic
- vacuum handling path
- inventory-aware reservation price

---

## Before adding alpha: cleanup step

### Step 0 — clean the base
Create `R2_13_baseclean`.

Do:
- remove or comment out dead parameters that no longer drive logic
- keep parameter names only for active behavior
- add lightweight diagnostics counters in memory

Add diagnostics for Osmium:
- take fills count
- passive fills count (if available from your replay)
- bars since buy fill
- bars since sell fill
- toxic level flips
- time spent in inventory-clear state

Success criterion:
- same or almost same PnL as base
- no behavioral change intended
- easier to interpret logs

If this step changes score materially, debug first before continuing.

---

## Main build order

### Step 1 — add Osmium conviction layer
Create `R2_14_conviction`.

Port back only the strongest proven Osmium alpha:
- stable-mid vs mid gap
- imbalance agreement
- magnet threshold
- trade-confirm bonus

Use conviction only to:
- relax `buy_need` / `sell_need` slightly
- tighten `buy_qe` / `sell_qe` slightly in the signal direction
- add `+1` front size only in very strong states

Do **not** yet add:
- toxicity smoothing
- markout memory
- side starvation logic

Why first:
- this improves **what** the bot trades
- it is the most product-specific proven alpha layer
- it is less likely to create hidden behavioral side effects than execution-control layers

Success criterion:
- Osmium PnL improves or at least the bot gets earlier quality gains
- no large increase in bad end-of-day inventory

If it fails:
- reduce trade-confirm bonus first
- then reduce magnet bonus
- keep agreement logic unless clearly harmful

---

### Step 2 — add toxicity smoothing / hysteresis
Create `R2_15_toxicity`.

Port in:
- raw toxicity -> toxic score -> toxic level 0/1/2
- separate bid/ask side smoothing
- decay with memory so one noisy snapshot does not flip the bot immediately

Use toxic levels only for:
- raising take thresholds on the bad side
- widening quote edge on the bad side
- reducing size on the bad side
- disabling that side only in the strongest toxic state

Do **not** yet add markout-based suppression.

Why second:
- improves execution quality without changing fair estimation
- should reduce being picked off in bad states
- is modular and interpretable

Success criterion:
- fewer ugly Osmium drawdowns
- similar or better total Osmium PnL
- no long dead plateaus caused by excessive stickiness

If it fails:
- toxicity is probably too sticky
- reduce score persistence before removing the layer entirely

---

### Step 3 — add corrected reentry / neutral drip
Create `R2_16_reentry`.

Port only the corrected version, not the early broken one.

Required behavior:
- use **bar count**, not raw timestamp gap
- track `bars_since_buy_fill`
- track `bars_since_sell_fill`
- track global quiet state if useful, but side-specific timers should matter more

Add:
- side-specific reentry
- neutral drip mode for low-signal, non-toxic plateau states
- reentry that actually changes the **posted price level**, not just theoretical edge
- slight `join_edge` boost during reentry

Important rules:
- if reentry triggers, force one-tick closer quoting on the reactivated side where safe
- neutral drip should be two-sided and tiny
- avoid reentry immediately after dangerous vacuum states unless the book has clearly normalized

Why third:
- this directly targets Osmium plateaus
- it is useful only once conviction and toxicity logic already exist

Success criterion:
- fewer flat Osmium PnL plateaus
- more small wins in quiet regions
- no major increase in adverse fills

If it fails:
- check timer units first
- then check whether price level actually changed or only edge variables changed

---

### Step 4 — add passive-only markout memory
Create `R2_17_markout_passive`.

This is where to use ideas from the `121_13` branch, but narrowly.

Add:
- buy-side passive markout EMA or bucketed estimate
- sell-side passive markout EMA or bucketed estimate

Use markout only for:
- passive quote width on that side
- passive front/back size on that side

Do **not** use markout yet for:
- aggressive taking
- full bot shutdown
- all thresholds at once

Reason:
- the earlier markout branch likely over-penalized too many actions at the same time
- passive quoting is where markout is most natural and most useful

Better version if possible:
Use buckets instead of one EMA:
- side
- spread regime
- toxic level
- maybe agreement state

Success criterion:
- similar or better fill count quality
- better Osmium markout after passive fills
- no collapse in long-session throughput

If it fails:
- reduce edge penalty first
- then reduce size penalty
- do not remove the whole feature before testing weaker intensity

---

### Step 5 — add inventory recycler / short-cover logic
Create `R2_18_recycler`.

Add a soft recycling regime for Osmium:
- when conviction is weak
- inventory is stretched
- toxicity is not extreme
- allow low-edge flattening earlier than full inventory-clear mode

Especially important:
- if ending too short, prioritize short-cover when bearish conviction fades
- if ending too long, prioritize light sell recycling when bullish conviction fades

Why:
- Osmium often makes money by freeing capacity for the next good trade
- some weaker branches stayed too short or too long too long

Success criterion:
- end-of-day Osmium inventory closer to neutral unless a strong signal justifies holding
- no loss of strong-trend capture in valid conviction states

---

### Step 6 — add access-aware Round 2 extension
Create `R2_19_accessaware`.

Only do this after the no-access version is already strong.

Access-aware changes should be **conditional**, not global:
- slightly larger front size in safe high-conviction states
- deeper sweep only when conviction is very strong and toxicity is low
- faster re-posting on the starved side
- maybe wider participation in level-2 / level-3 stale-book takes

Do not make access mode simply “more aggressive everywhere”.

Success criterion:
- estimated access delta is positive and robust in backtests
- no-access version remains strong

---

## Optional later step

### Step 7 — multi-level sweep in only the best Osmium states
Create `R2_20_multisweep`.

Only add once the rest is stable.

Condition for multi-sweep should require:
- strong conviction
- low toxicity
- positive net edge after each consumed level
- inventory not stretched too far already

Why later:
- easiest feature to destabilize
- best added only after fill-quality controls already exist

---

## What not to do too early

Do **not**:
- run CMA-ES / broad optimization before Step 4 is stable
- re-add every old mode from older bots
- optimize Pepper heavily before Osmium is stronger
- use markout penalties in every place at once
- use raw timestamps instead of bar counts for any silence logic

---

## Testing protocol after every step

For each new version record:
- total PnL
- Pepper PnL
- Osmium PnL
- final Pepper position
- final Osmium position
- number of Osmium take fills
- number of Osmium passive fills
- number of toxic flips
- number of reentry events
- average passive markout if available
- size of flat plateaus in Osmium PnL

Interpretation rules:
- if total PnL is flat but Osmium plateau shrinks, the step may still be useful
- if early Osmium improves but late Osmium worsens badly, the feature needs a recycler or weaker penalties
- if Pepper changes materially during an Osmium step, something leaked across products

---

## Donor map: where each feature comes from

- clean structure base: `TradervR2_12.py`
- conviction / local-fair richer Osmium family: current best and related best-family bots
- corrected reentry / neutral drip: the corrected `R1_116` style direction
- passive markout concept: `121_13` style branch, but narrowed
- threshold reminder from hidden round logs: long-session results where Pepper remains the base engine and Osmium remains the marginal edge engine

---

## Suggested naming sequence

- `R2_13_baseclean`
- `R2_14_conviction`
- `R2_15_toxicity`
- `R2_16_reentry`
- `R2_17_markout_passive`
- `R2_18_recycler`
- `R2_19_accessaware`
- `R2_20_multisweep`

---

## Best short version

If only one path is followed, do this order exactly:

1. clean base
2. Osmium conviction
3. toxicity smoothing
4. corrected reentry
5. passive-only markout
6. recycler
7. access-aware extension

That is the safest path to add back real Osmium alpha without turning the bot back into a parameter jungle.
