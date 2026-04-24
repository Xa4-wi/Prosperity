# Round 3 Phase 1 Diagnostics

Base bot under review: [TradervR3_7.py](Bots/Round3/TradervR3_7.py)

This report is the Phase 1 hard-classification pass for the two delta-1 products.

## HYDROGEL_PACK

- Primary classification: **anchored_local_fair_mm**
- Anchor reference: `10000.0`
- Anchor strength: **strong**
- Recommended execution style: Take -> Clear -> Make around a robust stable/wall fair
- Interpretation: drift signal is weak; mean-reversion is not strong enough to be the base model; short-horizon local book state contains predictive information; the product stays near a strong anchor

### Core metrics

- Mean mid: `9990.807`
- Mean spread: `15.721`
- Mean top depth: `24.799`
- Mean top-3 depth: `75.264`
- Drift SNR: `0.027`
- Mean-reversion half-life: `300.5` bars
- Corr(next move, micro gap): `0.297`
- Corr(next move, imbalance): `0.299`
- Corr(next move, stable gap): `0.327`
- Std(stable mid - raw mid): `0.3731`
- Mean |stable mid - raw mid|: `0.4584`

### Realized volatility by time bucket

- Bucket `0`: `0.015692`
- Bucket `1`: `0.015276`
- Bucket `2`: `0.015238`
- Bucket `3`: `0.015281`
- Bucket `4`: `0.014962`
- Bucket `5`: `0.015681`

### Daily metrics

- day `0`, drift `-0.192`, half-life `188.8`, micro corr `0.298`, imb corr `0.300`, vol `0.021931`
- day `1`, drift `0.265`, half-life `418.9`, micro corr `0.295`, imb corr `0.297`, vol `0.021500`
- day `2`, drift `-0.005`, half-life `293.8`, micro corr `0.298`, imb corr `0.300`, vol `0.021721`

## VELVETFRUIT_EXTRACT

- Primary classification: **anchored_local_fair_mm**
- Anchor reference: `5250.0`
- Anchor strength: **strong**
- Recommended execution style: Take -> Clear -> Make around a robust stable/wall fair
- Interpretation: drift signal is weak; mean-reversion is not strong enough to be the base model; short-horizon local book state contains predictive information; the product stays near a strong anchor

### Core metrics

- Mean mid: `5250.098`
- Mean spread: `4.988`
- Mean top depth: `75.626`
- Mean top-3 depth: `120.732`
- Drift SNR: `0.232`
- Mean-reversion half-life: `279.3` bars
- Corr(next move, micro gap): `0.227`
- Corr(next move, imbalance): `0.281`
- Corr(next move, stable gap): `0.345`
- Std(stable mid - raw mid): `0.2251`
- Mean |stable mid - raw mid|: `0.1814`

### Realized volatility by time bucket

- Bucket `0`: `0.015320`
- Bucket `1`: `0.015497`
- Bucket `2`: `0.014939`
- Bucket `3`: `0.015097`
- Bucket `4`: `0.015290`
- Bucket `5`: `0.015256`

### Daily metrics

- day `0`, drift `-0.054`, half-life `206.1`, micro corr `0.226`, imb corr `0.278`, vol `0.021356`
- day `1`, drift `0.181`, half-life `234.7`, micro corr `0.229`, imb corr `0.284`, vol `0.021621`
- day `2`, drift `0.246`, half-life `347.6`, micro corr `0.226`, imb corr `0.280`, vol `0.021656`

## Phase 1 Takeaways

- `HYDROGEL_PACK` should only remain strongly anchor-driven if the classification stays anchored after this harder pass.
- `VELVETFRUIT_EXTRACT` must be judged not just on direct alpha, but on how reliable it is as the voucher hedge anchor.
- The next implementation change should be fair-family adjustments only, not new voucher alpha.
