# Round 2 Parameter Categories

This note matches the grouped parameter blocks in
[TradervR2_33_2.py](Bots/Round2/TradervR2_33_2.py).

## Tier legend

- `core live`: should stay in the main trading surface
- `robustness live`: active protection / stability logic that is still part of the live bot
- `selective live`: useful, but only matters in specific strong states
- `mixed`: contains both live and research-facing toggles
- `legacy / research-only`: candidates for later pruning or moving into a research base

## `DEFAULT_ASH_PARAMS`

### Feature toggles
Tier: `mixed`
Turns whole subsystems on or off.

Examples:
- `FAIR_STYLE`
- `BOOK_HEALTH_ENABLE`
- `ENABLE_TAKE_LADDER`
- `TERMINAL_RISK_ENABLE`

### Fair model and anchor shaping
Tier: `core live`
Defines how Osmium constructs its fair and how much it trusts anchor, stable mid, wall mid, and deeper book structure.

Examples:
- `ANCHOR_WEIGHT`
- `STABLE_MID_WEIGHT`
- `LOCAL_MICRO_WEIGHT`
- `DEEP_IMBALANCE_WEIGHT`

### Inventory and regime control
Tier: `core live`
Controls when the bot should keep market making normally versus shifting into recycle behavior.

Examples:
- `SOFT_LIMIT`
- `INVENTORY_SKEW`
- `CLEAR_EDGE_LIMIT`

### Core quoting and taking
Tier: `core live`
The main execution geometry.

Examples:
- `BASE_EDGE`
- `JOIN_EDGE`
- `TAKE_L1_EDGE`
- `FRONT_SIZE`

### Signal thresholds and conviction shaping
Tier: `core live`
Controls how much strong local agreement changes behavior.

Examples:
- `FAST_TAKE_WEIGHT`
- `STABLE_MAGNET_EDGE`
- `AGREE_SIGNAL_BONUS`

### Passive fill quality
Tier: `robustness live`
Side-specific penalties for bad maker fills.

Examples:
- `MARKOUT_ALPHA`
- `SOFT_BAD_MARKOUT`
- `MARKOUT_EDGE_PENALTY`

### Access / strong-state expansion
Tier: `selective live`
Only matters in the best Ash states and should not be treated as always-on aggression.

Examples:
- `ACCESS_BOOK_HEALTH_MIN`
- `ACCESS_JOIN_EDGE_BONUS`
- `AGREE_UNLOCK_TAKE_RELIEF`

### Vacuum and refill handling
Tier: `core live`
Used when the book becomes one-sided or is just recovering.

Examples:
- `VACUUM_GAP`
- `VACUUM_FAIR_BLEND`
- `REFILL_STICKY_TICKS`

### Noisy-book and robustness overlays
Tier: `robustness live`
Protects the bot from trusting a thinned or distorted visible book too much.

Examples:
- `NOISY_TOUCH_GAP`
- `ALTMM_GEOMETRY_BLEND`

### Book-health controller
Tier: `robustness live`
The main Round 2 robustness layer.

Examples:
- `BOOK_HEALTH_LOW`
- `BOOK_HEALTH_EDGE_PENALTY_LOW`
- `BOOK_HEALTH_SIZE_MULT_MED`

### Side-specific reentry
Tier: `robustness live`
Wakes up only the stale side instead of turning the whole bot aggressive.

Examples:
- `STARVATION_BARS`
- `STARVATION_JOIN_BONUS`

### Legacy terminal recycler path
Tier: `legacy / research-only`
Older recycler knobs kept for optional testing.

### Rebuilt Ash risk context
Tier: `robustness live`
The top-level Ash risk inputs from the newer rebuild.

Examples:
- `RISK_VOL_NORMAL`
- `RISK_DRAWDOWN_SOFT`
- `RISK_TERMINAL_STEP2`
- `RISK_CONF_PRESS`

## `DEFAULT_IPR_PARAMS`

### Core carry model
Tier: `core live`
Defines the Pepper long-drift backbone and target path.

### Residual and spread memory
Tier: `core live`
Controls how Pepper reacts to rich/cheap deviations around drift.

### Inventory and reservation
Tier: `core live`
Shapes Pepper’s tolerance around the long schedule.

### Core execution
Tier: `core live`
Main take and quote edges plus passive sizes.

### Cheap accumulation and early schedule
Tier: `core live`
Helps Pepper get long earlier when still cheap.

### Rich / cheap residual response
Tier: `core live`
Extra handling for very good or very bad entry windows.

### Exit and late-session trimming
Tier: `core live`
Controls how much Pepper monetizes rich states later in the session.

### One-sided-book handling
Tier: `robustness live`
Fallback logic for sparse or degraded Pepper books.

### Rebuilt Pepper risk context
Tier: `robustness live`
Light entry-quality and catastrophic-drawdown risk.

Main point:
- Pepper risk should improve entry quality without flattening the carry engine.
- Ash risk should decide when local-fair edge is trustworthy enough to expand.

## First pruning candidates

If we do a future cleanup pass, the safest first candidates are:

- Ash `legacy / research-only` terminal recycler block
- mixed feature toggles that only support disabled paths
- duplicated Ash execution tuning that is already dominated by book-health / risk-context logic

The sections least worth pruning early are:

- Ash fair model and anchor shaping
- Ash book-health controller
- Ash core quoting and taking
- Pepper core carry model
- Pepper cheap accumulation and early schedule
