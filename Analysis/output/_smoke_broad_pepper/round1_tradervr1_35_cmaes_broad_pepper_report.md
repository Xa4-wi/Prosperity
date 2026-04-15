# TradervR1_35 Round 1 Broad Pepper Basin CMA-ES CMA-ES Report

- Config: `/Users/xavierwinkelmann/Prosperity/TraderFactory/configs/round1/tradervr1_35_cmaes_broad_pepper.json`
- Source bot: `/Users/xavierwinkelmann/Prosperity/Bots/Round1/TradervR1_35.py`
- Best bot: `/Users/xavierwinkelmann/Prosperity/Analysis/output/_smoke_broad_pepper/bots/TradervR1_35_best.py`
- Total evaluations: `3`

## Baseline Replay

- Day -2: `95977.5000`
- Day -1: `95887.0000`
- Day 0: `96602.0000`

## Best Candidate

- Objective: `88788.5765`
- Average score: `96151.8333`
- Regression penalty: `5784.0000`
- Imbalance penalty: `1579.0000`
- Drift penalty: `0.2568`

- Day -2: `95977.5000`
- Day -1: `95887.0000`
- Day 0: `96591.0000`

## Parameter Changes

| Parameter | Default | Best | Delta % |
| --- | ---: | ---: | ---: |
| IPR_RESIDUAL_ALPHA | 0.100000 | 0.107602 | +7.60% |
| IPR_LOOKAHEAD_BONUS | 4.884903 | 5.037814 | +3.13% |
| IPR_BASE_CARRY | 7.704548 | 6.835534 | -11.28% |
| IPR_EARLY_LONG_BIAS | 43.194133 | 42.228044 | -2.24% |
| IPR_EDGE_TARGET_SCALE | 12.000000 | 12.474155 | +3.95% |
| IPR_BASE_TAKE_EDGE | 2.767838 | 2.799105 | +1.13% |
| IPR_BASE_QUOTE_EDGE | 5.351603 | 5.338882 | -0.24% |
| IPR_EARLY_ACCUM_END | 0.420000 | 0.445678 | +6.11% |
| IPR_CHEAP_ACCUM_END | 0.560000 | 0.565878 | +1.05% |
| IPR_CHEAP_ACCUM_TAKE_PENALTY | 0.080000 | 0.109331 | +36.66% |
| IPR_CHEAP_ACCUM_QUOTE_EDGE_BONUS | 0.450000 | 0.489835 | +8.85% |
| IPR_CHEAP_ACCUM_Z_RELAX | -0.550000 | -0.558754 | +1.59% |
| IPR_CHEAP_ACCUM_TARGET_BUFFER | 20.000000 | 19.338023 | -3.31% |

## Generation History

| Gen | Gen Obj | Gen Avg | Best Obj | Best Avg | Sigma |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 88788.5765 | 96151.8333 | 88788.5765 | 96151.8333 | 0.047070 |
