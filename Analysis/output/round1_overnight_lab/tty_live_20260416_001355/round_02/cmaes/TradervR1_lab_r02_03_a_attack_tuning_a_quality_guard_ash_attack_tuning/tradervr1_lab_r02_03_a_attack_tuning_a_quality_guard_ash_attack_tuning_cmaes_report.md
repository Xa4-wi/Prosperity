# TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard short CMA-ES ash_attack_tuning CMA-ES Report

- Config: `/Users/xavierwinkelmann/Prosperity/Analysis/output/round1_overnight_lab/tty_live_20260416_001355/round_02/cmaes/tradervr1_lab_r02_03_a_attack_tuning_a_quality_guard_ash_attack_tuning.json`
- Source bot: `/Users/xavierwinkelmann/Prosperity/Analysis/output/round1_overnight_lab/tty_live_20260416_001355/round_02/candidates/TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard.py`
- Best bot: `/Users/xavierwinkelmann/Prosperity/Analysis/output/round1_overnight_lab/tty_live_20260416_001355/round_02/cmaes/TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard_ash_attack_tuning/bots/TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard_best.py`
- Total evaluations: `9`

## Baseline Replay

- Day -2: `96635.5000`
- Day -1: `96811.0000`
- Day 0: `96328.0000`

## Best Candidate

- Objective: `96617.5648`
- Average score: `96672.8333`
- Regression penalty: `0.0000`
- Imbalance penalty: `55.0000`
- Drift penalty: `0.2685`

- Day -2: `96751.5000`
- Day -1: `96878.0000`
- Day 0: `96389.0000`

## Parameter Changes

| Parameter | Default | Best | Delta % |
| --- | ---: | ---: | ---: |
| DEFAULT_ASH_PARAMS_BASE_EDGE | -0.762871 | -0.679065 | -10.99% |
| DEFAULT_ASH_PARAMS_TAKE_L1_EDGE | -0.683906 | -0.617041 | -9.78% |
| DEFAULT_ASH_PARAMS_TAKE_L2_EDGE | 2.356074 | 1.538694 | -34.69% |
| DEFAULT_ASH_PARAMS_TAKE_L3_EDGE | 2.667250 | 2.483099 | -6.90% |
| DEFAULT_ASH_PARAMS_MIN_QUOTE_EDGE | 1.857169 | 2.149221 | +15.73% |
| DEFAULT_ASH_PARAMS_JOIN_EDGE | 2.170278 | 2.124519 | -2.11% |

## Generation History

| Gen | Gen Obj | Gen Avg | Best Obj | Best Avg | Sigma |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 96580.7211 | 96660.1667 | 96591.5000 | 96591.5000 | 0.075614 |
| 2 | 96617.5648 | 96672.8333 | 96617.5648 | 96672.8333 | 0.067863 |
