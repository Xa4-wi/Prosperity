# TradervR1_12 Round 1 Osmium-Focused CMA-ES CMA-ES Report

- Config: `/Users/xavierwinkelmann/Prosperity/TraderFactory/configs/round1/tradervr1_12_cmaes.json`
- Source bot: `/Users/xavierwinkelmann/Prosperity/Bots/Round1/TradervR1_12.py`
- Best bot: `/Users/xavierwinkelmann/Prosperity/Analysis/output/round1_tradervr1_12_cmaes/bots/TradervR1_12_best.py`
- Total evaluations: `16`

## Baseline Replay

- Day -2: `95731.5000`
- Day -1: `96456.0000`
- Day 0: `95297.0000`

## Best Candidate

- Objective: `95843.3795`
- Average score: `95863.3333`
- Regression penalty: `0.0000`
- Imbalance penalty: `19.2500`
- Drift penalty: `0.7038`

- Day -2: `95776.0000`
- Day -1: `96483.0000`
- Day 0: `95331.0000`

## Parameter Changes

| Parameter | Default | Best | Delta % |
| --- | ---: | ---: | ---: |
| ASH_IMBALANCE_WEIGHT | 1.053020 | 1.033601 | -1.84% |
| ASH_INVENTORY_SKEW | 0.119782 | 0.120423 | +0.53% |
| ASH_BASE_EDGE | 2.000000 | 2.086795 | +4.34% |
| ASH_FRONT_SIZE | 16.000000 | 16.371254 | +2.32% |
| ASH_SOFT_LIMIT | 70.000000 | 70.954897 | +1.36% |
| ASH_ADVERSE_IMBALANCE | 0.200000 | 0.205012 | +2.51% |
| ASH_STRONG_IMBALANCE | 0.160000 | 0.157176 | -1.77% |
| ASH_TOXIC_RETREAT_SIZE | 0.700000 | 0.676248 | -3.39% |
| ASH_TOXIC_RETREAT_EDGE | 0.550000 | 0.518627 | -5.70% |
| ASH_DISLOCATION_EDGE | 6.000000 | 6.239647 | +3.99% |
| ASH_DISLOCATION_BONUS_SIZE | 3.000000 | 2.611964 | -12.93% |
| IPR_BASE_CARRY | 7.704548 | 8.102875 | +5.17% |
| IPR_EARLY_LONG_BIAS | 43.194133 | 42.903319 | -0.67% |
| IPR_PASSIVE_SELL_BUFFER | 8.000000 | 7.937656 | -0.78% |

## Generation History

| Gen | Gen Obj | Gen Avg | Best Obj | Best Avg | Sigma |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 95827.9421 | 95828.1667 | 95828.1667 | 95828.1667 | 0.046504 |
| 2 | 95812.0322 | 95871.3333 | 95828.1667 | 95828.1667 | 0.045630 |
| 3 | 95843.3795 | 95863.3333 | 95843.3795 | 95863.3333 | 0.045895 |
