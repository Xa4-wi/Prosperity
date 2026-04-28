# Round 4 Mark Behavior Scan

Data:

- `Data/ROUND_4/trades_round_4_day_1.csv`
- `Data/ROUND_4/trades_round_4_day_2.csv`
- `Data/ROUND_4/trades_round_4_day_3.csv`
- `Data/ROUND_4/prices_round_4_day_*.csv`

Generated files:

- `mark_event_markouts.csv`: one row per mark-side trade event
- `mark_side_summary.csv`: grouped mark/product/side markout summary
- `velvet_mark_side_summary.csv`: VELVET-only grouped summary
- `mark67_velvet_events.csv`: all Mark 67 VELVET events
- `mark67_velvet_counterparties.csv`: Mark 67 VELVET counterparty breakdown

## Main Finding

Mark 67 is a VELVET-only bullish signal in this data. Across all three Round 4 days,
Mark 67 only appears as a buyer in `VELVETFRUIT_EXTRACT`.

Mark 67 VELVET events:

- events: `165`
- quantity: `1510`
- side: `BUY` only
- average 1000-timestamp mid move after event: `+2.242`
- 1000-timestamp hit rate: `75.8%`
- average Mark 67 trade-price markout at 1000 timestamps: `+1.445`

Counterparties:

- `Mark 49`: `89` events, `963` quantity
- `Mark 22`: `75` events, `546` quantity
- `Mark 55`: `1` event, `1` quantity

## Execution Read

The signal is not directly crossable after observation.

If we observe the print and buy the next ask, average PnL to future mid is negative:

- 500 timestamp horizon: `-2.603`
- 1000 timestamp horizon: `-2.306`
- 2000 timestamp horizon: `-2.703`

This means the signal should be used as a fair-value/filter overlay:

- raise VELVET fair modestly after Mark 67 buys
- avoid fresh shorts for a short decay window
- bias passive bids upward
- do not aggressively cross the spread just because Mark 67 bought

## Wider VELVET Mark Read

Useful VELVET signals by 1000-timestamp side mid-change:

- `Mark 67 BUY`: `+2.242`, `75.8%` hit rate
- `Mark 49 SELL`: opposite-side bullish read, because Mark 49 sells are followed by raw VELVET rises
- `Mark 22 SELL`: weaker bullish read

Most other VELVET marks are weaker or mostly execution/spread artifacts.

## Bot Experiment

Created:

- `Bots/Round4/TradervR4_39_mark67_velvet.py`
- `Bots/Round4/TradervR4_43_mark_overlays.py`
- `Bots/Round4/TradervR4_44_velvet_id_fair_only.py`
- `Bots/Round4/TradervR4_45_mark67_mark49_fair.py`

Patch:

- based on `TradervR4_24.py`
- adds Mark 67 VELVET signal into `_velvet_overlay`
- signal decays over time
- signal shifts VELVET fair only; it does not create direct market-taking orders

Backtest comparison:

- `TradervR4_42.py` / no trader-ID base: `+226,279.50`
- `TradervR4_39_mark67_velvet.py`: `+227,975.50`
- `TradervR4_43_mark_overlays.py`: `+224,600.50`
- `TradervR4_44_velvet_id_fair_only.py`: `+227,348.50`
- `TradervR4_45_mark67_mark49_fair.py`: `+227,449.50`

Product impact:

- `VELVETFRUIT_EXTRACT`: `72,625.00 -> 72,102.00`
- `VEV_5100`: `11,621.50 -> 13,466.00`
- total improved mostly through voucher interaction, not direct VELVET PnL.

## Recommendation

The Mark 67 edge is real in the historical trade behavior, but it should stay small.
Use it as a VELVET fair/bias overlay and not as an aggressive alpha engine.

The full target/block/cover implementation underperformed. Adding Mark49/Mark22
to the fair overlay was also weaker than Mark67 alone in the local backtest.
The best tested trader-ID branch remains the small Mark67-only fair overlay.

## Deep-ITM Voucher Follow-Up

Created:

- `Bots/Round4/TradervR4_47_deep_itm_tv.py`

Patch:

- based on `TradervR4_46_moneyness_pair.py`
- routes `VEV_4000` and `VEV_4500` through an intrinsic/time-value residual engine
- uses a decaying time-value EMA instead of IV residual
- adds a small Mark 38 / Mark 14 execution filter only for those deep-ITM vouchers
- leaves `VEV_6000` and `VEV_6500` untouched

Backtest:

- `TradervR4_46_moneyness_pair.py`: `+243,962.50`
- `TradervR4_47_deep_itm_tv.py`: `+245,000.50`
- delta: `+1,038.00`

Product impact:

- `VEV_4000`: `5,239.00 -> 1,505.00`
- `VEV_4500`: `2,377.50 -> 1,426.50`
- `VEV_5000`: `42,231.50 -> 43,110.50`
- `VEV_5100`: `31,464.50 -> 36,404.50`
- `VEV_5200`: `-8,070.00 -> -7,488.00`

The deep-ITM engine improved total PnL, but not because `VEV_4000/4500`
themselves became larger profit centers. It changed the surrounding voucher
strip behavior, especially `VEV_5100`.
