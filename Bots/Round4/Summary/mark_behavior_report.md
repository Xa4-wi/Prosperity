# Mark behavior analysis

This report summarizes the visible trader IDs (`Mark xx`) across the 3 uploaded Round 4 days.

## Files generated

- `01_total_traded_quantity_by_mark.png`
- `02_alpha_1000_per_unit_by_mark.png`
- `03_immediate_execution_edge_by_mark.png`
- `04_product_mix_by_mark.png`
- `05_velvet_cumulative_signed_qty_all_marks.png`
- `06_velvet_alpha_1000_by_mark.png`
- `07_hydrogel_cumulative_signed_qty_all_marks.png`
- `08_hydrogel_alpha_1000_by_mark.png`
- `09_vouchers_net_quantity_by_strike_and_mark.png`
- `10_vouchers_mark01_vs_mark22.png`
- `Mark_01_cumulative_signed_qty_by_product.png`
- `Mark_14_cumulative_signed_qty_by_product.png`
- `Mark_22_cumulative_signed_qty_by_product.png`
- `Mark_38_cumulative_signed_qty_by_product.png`
- `Mark_49_cumulative_signed_qty_by_product.png`
- `Mark_55_cumulative_signed_qty_by_product.png`
- `Mark_67_cumulative_signed_qty_by_product.png`

## Global summary table

| mark    |   total_qty |   net_qty |   trades |   immediate_edge_per_unit |   alpha_1000_per_unit |   alpha_10000_per_unit |
|:--------|------------:|----------:|---------:|--------------------------:|----------------------:|-----------------------:|
| Mark 14 |        8718 |       302 |     2172 |                     6.541 |                 6.534 |                  6.543 |
| Mark 67 |        1510 |      1510 |      165 |                    -0.797 |                 1.445 |                  0.68  |
| Mark 01 |        7428 |      4678 |     1843 |                     1.136 |                 1.202 |                  1.088 |
| Mark 22 |        5889 |     -5477 |     1584 |                    -0.394 |                -0.514 |                 -0.506 |
| Mark 49 |        1186 |      -956 |      122 |                     0.787 |                -1.332 |                 -1.275 |
| Mark 55 |        6551 |       -43 |     1198 |                    -2.482 |                -2.455 |                 -1.757 |
| Mark 38 |        5000 |       -14 |     1478 |                    -8.572 |                -8.612 |                 -8.969 |

## High-level takeaways

- **Mark 14** looks like the strongest execution-edge trader: very good immediate fills and good forward performance.
- **Mark 67** looks like the cleanest **Velvetfruit directional signal**: mostly buys and tends to be followed by a rebound.
- **Mark 01** looks like a useful voucher/Velvet buyer, especially on higher-strike vouchers.
- **Mark 22** looks like a systematic voucher seller, often the opposite side of Mark 01.
- **Mark 38** is a frequent weak counterparty, especially in Hydrogel / low-strike voucher flow.
- **Mark 49** looks like a weak Velvet seller and can often be used as a contrarian signal.
- **Mark 55** looks more like a noisy/liquidity participant than a clean predictor.

## Per-Mark behavior descriptions

### Mark 14

**Category:** execution-edge winner

**Overall behavior:**
- Total traded quantity: 8718
- Net quantity: 302
- Immediate execution edge per unit: 6.54
- 1000-tick alpha per unit: 6.53
- 10000-tick alpha per unit: 6.54
- Best product by forward alpha: VEV_4000
- Weakest product by forward alpha: VEV_5400

**Top product-level behavior:**
- HYDROGEL_PACK: seller, total_qty=4022, net_qty=-44, alpha_1000/unit=8.13, immediate_edge/unit=7.96
- VELVETFRUIT_EXTRACT: seller, total_qty=3524, net_qty=-2, alpha_1000/unit=2.24, immediate_edge/unit=2.45
- VEV_4000: buyer, total_qty=870, net_qty=46, alpha_1000/unit=10.34, immediate_edge/unit=10.42
- VEV_5200: buyer, total_qty=122, net_qty=122, alpha_1000/unit=0.86, immediate_edge/unit=1.00
- VEV_5300: buyer, total_qty=105, net_qty=105, alpha_1000/unit=0.60, immediate_edge/unit=0.75

**How to use this mark in a bot:**
- Treat as a smart-side execution signal, especially in Hydrogel and some Velvet flow.
- Do not blindly chase; better use as a confirmation/filter.

### Mark 67

**Category:** directionally useful / followable

**Overall behavior:**
- Total traded quantity: 1510
- Net quantity: 1510
- Immediate execution edge per unit: -0.80
- 1000-tick alpha per unit: 1.45
- 10000-tick alpha per unit: 0.68
- Best product by forward alpha: VELVETFRUIT_EXTRACT
- Weakest product by forward alpha: VELVETFRUIT_EXTRACT

**Top product-level behavior:**
- VELVETFRUIT_EXTRACT: buyer, total_qty=1510, net_qty=1510, alpha_1000/unit=1.45, immediate_edge/unit=-0.80

**How to use this mark in a bot:**
- Use as a bullish Velvet overlay.
- If Mark 67 buys during a local Velvet drawdown, raise fair slightly and avoid shorting.

### Mark 01

**Category:** directionally useful / followable

**Overall behavior:**
- Total traded quantity: 7428
- Net quantity: 4678
- Immediate execution edge per unit: 1.14
- 1000-tick alpha per unit: 1.20
- 10000-tick alpha per unit: 1.09
- Best product by forward alpha: VELVETFRUIT_EXTRACT
- Weakest product by forward alpha: VEV_6500

**Top product-level behavior:**
- VELVETFRUIT_EXTRACT: buyer, total_qty=2792, net_qty=42, alpha_1000/unit=2.92, immediate_edge/unit=2.64
- VEV_6000: buyer, total_qty=1105, net_qty=1105, alpha_1000/unit=0.50, immediate_edge/unit=0.50
- VEV_6500: buyer, total_qty=1105, net_qty=1105, alpha_1000/unit=0.50, immediate_edge/unit=0.50
- VEV_5500: buyer, total_qty=1042, net_qty=1042, alpha_1000/unit=0.51, immediate_edge/unit=0.53
- VEV_5400: buyer, total_qty=911, net_qty=911, alpha_1000/unit=0.59, immediate_edge/unit=0.60

**How to use this mark in a bot:**
- Use as a soft bullish confirmation on Velvet and higher-strike voucher bids.
- Combine with Black-Scholes residual checks before following voucher flow.

### Mark 22

**Category:** mixed or noisy

**Overall behavior:**
- Total traded quantity: 5889
- Net quantity: -5477
- Immediate execution edge per unit: -0.39
- 1000-tick alpha per unit: -0.51
- 10000-tick alpha per unit: -0.51
- Best product by forward alpha: VEV_5000
- Weakest product by forward alpha: VEV_5200

**Top product-level behavior:**
- VEV_6500: seller, total_qty=1105, net_qty=-1105, alpha_1000/unit=-0.50, immediate_edge/unit=-0.50
- VEV_6000: seller, total_qty=1105, net_qty=-1105, alpha_1000/unit=-0.50, immediate_edge/unit=-0.50
- VEV_5500: seller, total_qty=1069, net_qty=-1069, alpha_1000/unit=-0.51, immediate_edge/unit=-0.53
- VEV_5400: seller, total_qty=959, net_qty=-959, alpha_1000/unit=-0.56, immediate_edge/unit=-0.59
- VELVETFRUIT_EXTRACT: seller, total_qty=843, net_qty=-551, alpha_1000/unit=-0.41, immediate_edge/unit=0.74

**How to use this mark in a bot:**
- Usually better as a trader to fade rather than follow.
- If Mark 22 is selling higher-strike vouchers and your fair says cheap, passive bids may be attractive.

### Mark 49

**Category:** mixed or noisy

**Overall behavior:**
- Total traded quantity: 1186
- Net quantity: -956
- Immediate execution edge per unit: 0.79
- 1000-tick alpha per unit: -1.33
- 10000-tick alpha per unit: -1.27
- Best product by forward alpha: VELVETFRUIT_EXTRACT
- Weakest product by forward alpha: VELVETFRUIT_EXTRACT

**Top product-level behavior:**
- VELVETFRUIT_EXTRACT: seller, total_qty=1186, net_qty=-956, alpha_1000/unit=-1.33, immediate_edge/unit=0.79

**How to use this mark in a bot:**
- Use as a contrarian Velvet signal.
- If Mark 49 sells and Velvet is already locally stretched down, that supports a long bias.

### Mark 55

**Category:** consistently exploitable / trade against

**Overall behavior:**
- Total traded quantity: 6551
- Net quantity: -43
- Immediate execution edge per unit: -2.48
- 1000-tick alpha per unit: -2.45
- 10000-tick alpha per unit: -1.76
- Best product by forward alpha: VELVETFRUIT_EXTRACT
- Weakest product by forward alpha: VELVETFRUIT_EXTRACT

**Top product-level behavior:**
- VELVETFRUIT_EXTRACT: seller, total_qty=6551, net_qty=-43, alpha_1000/unit=-2.45, immediate_edge/unit=-2.48

**How to use this mark in a bot:**
- Mostly treat as liquidity/noise.
- Useful for market activity context, but not a strong stand-alone predictor.

### Mark 38

**Category:** consistently exploitable / trade against

**Overall behavior:**
- Total traded quantity: 5000
- Net quantity: -14
- Immediate execution edge per unit: -8.57
- 1000-tick alpha per unit: -8.61
- 10000-tick alpha per unit: -8.97
- Best product by forward alpha: VEV_5300
- Weakest product by forward alpha: VEV_4000

**Top product-level behavior:**
- HYDROGEL_PACK: buyer, total_qty=4096, net_qty=34, alpha_1000/unit=-7.97, immediate_edge/unit=-7.88
- VEV_4000: seller, total_qty=876, net_qty=-46, alpha_1000/unit=-10.29, immediate_edge/unit=-10.39
- VEV_4500: balanced, total_qty=6, net_qty=0, alpha_1000/unit=-2.83, immediate_edge/unit=-3.67
- VEV_5000: balanced, total_qty=6, net_qty=0, alpha_1000/unit=-3.00, immediate_edge/unit=-1.17
- VEV_5100: balanced, total_qty=6, net_qty=0, alpha_1000/unit=-2.50, immediate_edge/unit=-1.00

**How to use this mark in a bot:**
- Strong candidate to trade against, especially in Hydrogel.
- Keep as a weak-counterparty / contrarian input, not a primary alpha source.

## Suggested next implementation ideas

1. **Velvet overlay:** add a decaying trader-ID signal with strongest positive weights on Mark 67 buys and Mark 49 sells.
2. **Voucher overlay:** add a small passive-bid bias when Mark 22 is selling higher-strike vouchers and BS residual says cheap.
3. **Hydrogel:** keep any trader-ID use very small or disabled until the main Hydrogel strategy is stable.
