# Voucher Phase 2 Plan

Base comparison:

- [TradervR3_7.py](Bots/Round3/TradervR3_7.py)
- [TradervR3_16.py](Bots/Round3/TradervR3_16.py)
- official logs:
  - [TradervR3_7.log](Bots/Round3/TradervR3_7.log)
  - [TradervR3_16.log](Bots/Round3/TradervR3_16.log)

## Main Read

`R3_16` is a much better **risk-controlled voucher bot** than `R3_7`, but it is also too strict.

The right conclusion is not:

`throw away Black-Scholes`

The right conclusion is:

`Black-Scholes should be the risk spine, not the whole alpha brain.`

## What The Charts Say

### 1. Velvet got safer, but too suppressed

The `VELVETFRUIT_EXTRACT` position chart shows:

- `R3_7` swings hard and reaches large positive inventory
- `R3_10` is tighter
- `R3_16` stays heavily short most of the time, with much less active role switching

That matches the portal PnL:

- `R3_7` VEV: `+3450.625`
- `R3_16` VEV: `+1401.625`

So `R3_16` uses Velvet better as a hedge anchor, but it also leaves money on the table.

### 2. The dangerous middle voucher band was the real leak

Portal PnL by product:

- `VEV_5100`: `R3_7 = -1859.27`, `R3_16 = 0.0`
- `VEV_5200`: `R3_7 = -5844.74`, `R3_16 = 0.0`
- `VEV_5300`: `R3_7 = -3721.58`, `R3_16 = 0.0`
- `VEV_5400`: `R3_7 = -487.77`, `R3_16 = 0.0`
- `VEV_5500`: `R3_7 = -155.21`, `R3_16 = 0.0`

The inventory charts confirm this:

- `R3_7` and earlier bots repeatedly maxed the `5100` to `5500` region
- `R3_16` almost completely shuts that region down

This is the strongest success of the BS-first rewrite.

### 3. But `R3_16` also killed the useful low-strike edge

Portal PnL:

- `VEV_4500`: `R3_7 = +347.55`, `R3_16 = +22.60`
- `VEV_5000`: `R3_7 = +467.99`, `R3_16 = -28.80`

The position charts match this:

- `R3_7` carries meaningful low-strike inventory
- `R3_16` is almost flat there too

So `R3_16` did not just remove bad risk.
It also removed part of the profitable part of the strip.

### 4. `R3_7` had real alpha, but bad risk concentration

The total PnL chart shows:

- `R3_7` had by far the biggest upside bursts
- but it could not survive the large middle-strike concentration

So the next development phase should not try to turn `R3_16` into an even stricter no-trade bot.
It should try to recover the **good `R3_7` alpha** in a controlled way.

## Phase 2 Principle

Use a hybrid voucher model:

1. **Black-Scholes / smile fit**
   - for fair construction
   - for residual ranking
   - for delta / vega control
   - for position limits

2. **Non-BS alpha overlays**
   - only where the logs show real edge
   - mainly in the lower strikes
   - never allowed to override strip risk limits

## What To Build Next

### Lane A: Keep BS as the risk framework

This stays:

- guarded underlying fair in `VELVETFRUIT_EXTRACT`
- IV inversion
- weighted smile fit
- neighboring strike sanity
- delta / vega strip monitoring
- hard suppression of the dangerous middle-upper wing when unconfirmed

Do not undo this.

### Lane B: Split the strip into trading zones

Do not treat all strikes the same.

#### Zone 1: Low strikes

Products:

- `VEV_4500`
- `VEV_5000`

Mode:

- allow directional residual trades
- allow modest inventory carry
- looser thresholds than in `R3_16`

Why:

- these strikes made real money in `R3_7`
- they were not the main catastrophic leak

#### Zone 2: Dangerous middle band

Products:

- `VEV_5100`
- `VEV_5200`
- `VEV_5300`

Mode:

- pair-first only
- no large outright inventory
- require stronger residual confirmation
- require hedge capacity

Why:

- this is where `R3_7` and older bots blew up
- `R3_16` correctly identified this as the main risk pocket

#### Zone 3: Upper wing

Products:

- `VEV_5400`
- `VEV_5500`

Mode:

- quote-only or tiny pair support
- no meaningful outright book unless evidence appears

Why:

- earlier bots accumulated large positions here with poor reward
- `R3_16` going flat here is probably correct for now

### Lane C: Add back a controlled “repricing lag” alpha

This is the likely missing piece from `R3_7`.

The next alpha layer should be:

- if `VELVETFRUIT_EXTRACT` moves materially
- and low strikes underreact relative to BS fair / fitted IV response
- then allow temporary directional buying or selling in `4500` and `5000`

This should be:

- spread-adjusted
- capped
- shut off when strip delta is already large

### Lane D: Separate pair alpha from outright alpha

Per strike, compute two things:

- `rv_score`: relative-value score versus neighboring strikes
- `outright_score`: absolute cheap/rich score versus fitted fair

Trading priority:

1. pair / residual normalization
2. only then small outright trades

This is the cleanest way to recover useful alpha without rebuilding the old blowups.

### Lane E: Make Velvet explicitly hedge-first, not alpha-first

Current read:

- `R3_16` is closer to correct than `R3_7`
- but it is too one-sided and passive

Next rule:

- Velvet should first neutralize voucher strip risk
- then use only a small leftover alpha budget
- low-strike voucher alpha may modestly loosen this, but not override it

## Exact Next Build Sequence

### `R3_17`

Goal:

- start from [TradervR3_16.py](Bots/Round3/TradervR3_16.py)
- loosen only the low-strike lane

Changes:

- lower residual threshold for `VEV_4500` and `VEV_5000`
- slightly larger per-strike caps there
- keep `5100+` logic unchanged

Acceptance:

- recover some `4500/5000` PnL
- without reopening `5100/5200/5300`

### `R3_18`

Goal:

- add lagged-repricing overlay for low strikes

Changes:

- detect when low strikes underreact to Velvet move / BS shift
- allow temporary directional trades in `4500/5000`

Acceptance:

- improved low-strike PnL
- no large new Velvet slingshot

### `R3_19`

Goal:

- add explicit pair-first trades inside the middle band

Changes:

- `5100/5200/5300` only trade when residual spread is confirmed across neighbors
- no big outright middle-band inventory

Acceptance:

- middle-band stays stable
- some of the “too flat” opportunity returns

## What Not To Do

- do not remove the BS smile framework
- do not reopen full outright trading in `5100` to `5500`
- do not let Velvet become the main alpha engine again
- do not optimize thresholds globally across all strikes at once

## Short Version

`R3_16` solved the big problem:

- catastrophic middle-band voucher exposure

But it overcorrected:

- it also shut down useful low-strike alpha

So the next phase is:

`keep BS for risk and fair -> reopen only the good alpha pockets -> keep the dangerous band pair-only and capped`
