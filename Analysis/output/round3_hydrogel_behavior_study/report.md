# Round 3 Hydrogel Behavior Study

This pass re-checks the raw Hydrogel CSVs to answer a narrower question:
what is the product actually doing, and which signals are useful for the next Hydrogel improvements?

## Oracle Read

- `two_flip`: `167600`
- `one_flip`: `107600`
- `anchored_mean_reverter`: `71600`
- `hold`: `15200`
- `local_fair_mm`: `-154640`

Interpretation: Hydrogel is still much closer to an anchored phase/regime product than to a local-fair MM product.

## Signal Read

Short-horizon local-book predictors work, but they decay fast. Longer-horizon anchor pull is stronger, especially late in the day.

| Horizon | Micro Corr | Imbalance Corr | Anchor Corr |
| --- | ---: | ---: | ---: |
| `1` | `0.297` | `0.299` | `0.034` |
| `5` | `0.137` | `0.139` | `0.067` |
| `20` | `0.068` | `0.069` | `0.130` |
| `50` | `0.040` | `0.041` | `0.202` |

Useful interpretation:
- `1-5` bars: use micro / imbalance for entry timing and re-entry confirmation.
- `20-50` bars: anchor gap matters more than microstructure.
- That means Hydrogel should not use the same signal for entry and hold.

## Phase Windows

The most useful repeated buckets are below.

| Window | Avg Return | Sign Agreement | Day Values |
| --- | ---: | ---: | --- |
| `0-5%` | `-18.3` | `1/3 pos` | `-18.0, 22.0, -59.0` |
| `5-10%` | `-17.8` | `1/3 pos` | `-26.5, -35.0, 8.0` |
| `10-15%` | `33.5` | `3/3 pos` | `24.5, 20.0, 56.0` |
| `20-25%` | `-20.8` | `0/3 pos` | `-20.0, -11.0, -31.5` |
| `45-50%` | `22.0` | `2/3 pos` | `16.0, 59.0, -9.0` |
| `55-60%` | `29.0` | `3/3 pos` | `30.0, 16.0, 41.0` |
| `75-80%` | `-27.0` | `0/3 pos` | `-27.0, -38.0, -16.0` |
| `80-85%` | `12.2` | `3/3 pos` | `5.0, 21.5, 10.0` |
| `95-100%` | `-15.0` | `1/3 pos` | `-50.0, -18.0, 23.0` |

Most actionable phase findings:
- `10-15%` is a consistent rebound window.
- `20-25%` is consistently weak.
- `55-60%` is a consistent positive window.
- `75-80%` is the strongest reliable late fade window across all three days.
- After `80%`, the path splits: fade can continue or rebound, so that window needs confirmation rather than a blind short.

## Late-Window Anchor Edge

Late in the day, being far above or below the anchor has a clear directional meaning.

| Day | 20-bar Fwd if `mid > 10025` | 20-bar Fwd if `mid < 9975` | 50-bar Fwd if `mid > 10025` | 50-bar Fwd if `mid < 9975` |
| --- | ---: | ---: | ---: | ---: |
| `0` | `-3.88` | `4.77` | `-11.60` | `10.63` |
| `1` | `-2.10` | `n/a` | `-6.16` | `n/a` |
| `2` | `-2.12` | `n/a` | `-3.91` | `n/a` |

Interpretation:
- Late Hydrogel above `10025` has negative forward return on every day.
- Late Hydrogel below `9975` has positive forward return whenever that state appears.
- So a late long held far above anchor is dangerous even if the regime score still looks acceptable.

## Liquidity Check

| Phase | Mean Spread | Mean Top Depth | Mean Top-3 Depth |
| --- | ---: | ---: | ---: |
| `early` | `15.70` | `24.85` | `75.24` |
| `mid` | `15.73` | `24.79` | `75.23` |
| `late` | `15.72` | `24.77` | `75.36` |

Interpretation: the late problem is not caused by worse visible liquidity. Spread and depth stay almost unchanged.

## Daily Shape

| Day | Global Min | Global Max | Late High After 60% | Post-75 Move |
| --- | --- | --- | --- | ---: |
| `0` | `9928.0 @ 485300` | `10071.0 @ 377000` | `10055.5 @ 740400` | `-66.0` |
| `1` | `9908.5 @ 441200` | `10079.0 @ 722400` | `10079.0 @ 722400` | `-38.5` |
| `2` | `9891.0 @ 279100` | `10051.0 @ 724000` | `10051.0 @ 724000` | `5.0` |

Interpretation:
- Day `0`: short -> long -> short style.
- Day `1`: long -> short -> long style, but still has an initial `75-80%` fade.
- Day `2`: short -> long -> short style with the second flip around `72%`.

## Best Next Hydrogel Improvements

1. Build a late-phase trigger around `75-80%` day progress. That is the cleanest stable timing signal in the raw data.
2. Use micro / imbalance only for entry and re-entry confirmation. They are strong at `1-5` bars but not a hold signal.
3. Use anchor distance as a stronger hold/exit control. A late long above `10025` is structurally dangerous.
4. Do not blindly short after `80%`. The initial fade is reliable, but post-fade continuation is not stable across all days.
5. A better state machine is likely:
`EARLY_SHOCK -> MID_RECOVERY / BUILD -> LATE_FADE_TRIGGER -> {CLEAR_LONG or SMALL_SHORT if reconfirmed}`

Short version: the next Hydrogel edge is probably not more generic risk control. It is a better late-day state transition that respects both the consistent `75-80%` fade and the fact that the post-fade branch is not always the same.
