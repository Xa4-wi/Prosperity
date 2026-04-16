# TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard short CMA-ES ash_attack_tuning CMA-ES Report

- Config: `/Users/xavierwinkelmann/Prosperity/Analysis/output/round1_overnight_lab/watchdog_live_20260416_0038/attempts/attempt_07/round_02/cmaes/tradervr1_lab_r02_03_a_attack_tuning_a_quality_guard_ash_attack_tuning.json`
- Source bot: `/Users/xavierwinkelmann/Prosperity/Analysis/output/round1_overnight_lab/watchdog_live_20260416_0038/attempts/attempt_07/round_02/candidates/TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard.py`
- Best bot: `/Users/xavierwinkelmann/Prosperity/Analysis/output/round1_overnight_lab/watchdog_live_20260416_0038/attempts/attempt_07/round_02/cmaes/TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard_ash_attack_tuning/bots/TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard_best.py`
- Total evaluations: `9`

## Baseline Replay

- Day -2: `96568.0000`
- Day -1: `96881.0000`
- Day 0: `96496.0000`

## Best Candidate

- Objective: `96650.0101`
- Average score: `96669.8333`
- Regression penalty: `0.0000`
- Imbalance penalty: `19.0000`
- Drift penalty: `0.8232`

- Day -2: `96591.5000`
- Day -1: `96892.0000`
- Day 0: `96526.0000`

## Parameter Changes

| Parameter | Default | Best | Delta % |
| --- | ---: | ---: | ---: |
| DEFAULT_ASH_PARAMS_BASE_EDGE | -0.899817 | -0.657548 | -26.92% |
| DEFAULT_ASH_PARAMS_TAKE_L1_EDGE | 0.950578 | 1.878481 | +97.61% |
| DEFAULT_ASH_PARAMS_TAKE_L2_EDGE | 0.500000 | 0.500000 | +0.00% |
| DEFAULT_ASH_PARAMS_TAKE_L3_EDGE | 4.079596 | 3.120327 | -23.51% |
| DEFAULT_ASH_PARAMS_MIN_QUOTE_EDGE | 1.891189 | 2.147463 | +13.55% |
| DEFAULT_ASH_PARAMS_JOIN_EDGE | 1.258356 | 1.000000 | -20.53% |

## Generation History

| Gen | Gen Obj | Gen Avg | Best Obj | Best Avg | Sigma |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 96648.1810 | 96648.3333 | 96648.3333 | 96648.3333 | 0.076687 |
| 2 | 96650.0101 | 96669.8333 | 96650.0101 | 96669.8333 | 0.080116 |
