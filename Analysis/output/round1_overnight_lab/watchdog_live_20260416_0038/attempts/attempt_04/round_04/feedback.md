# Round 4 Feedback

## Top Candidates

### TradervR1_lab_r04_01_a_local_fair_blend

- Parent: `TradervR1_lab_r03_08_a_attack_tuning_a_quality_guard_p_entry_quality`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `292738.0000`
- Delta vs safe baseline: `4695.5000`
- Delta vs aggressive anchor: `2893.5000`
- Composite score: `6517.0822`
- MC plausible mean delta: `3317.1667`
- MC plausible p10 delta: `241.7500`
- MC win rate: `0.8333`

### TradervR1_lab_r04_01_a_local_fair_blend_cmaes_ash_local_fair_blend

- Parent: `TradervR1_lab_r04_01_a_local_fair_blend`
- Families: `ash_local_fair_blend, cmaes_refine`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `292738.0000`
- Delta vs safe baseline: `4695.5000`
- Delta vs aggressive anchor: `2893.5000`
- Composite score: `6367.9222`
- MC plausible mean delta: `3152.1667`
- MC plausible p10 delta: `-352.2500`
- MC win rate: `0.8333`

### TradervR1_lab_r04_07_a_quality_guard

- Parent: `TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289464.5000`
- Delta vs safe baseline: `1422.0000`
- Delta vs aggressive anchor: `-380.0000`
- Composite score: `1500.5595`
- MC plausible mean delta: `576.2500`
- MC plausible p10 delta: `-1634.2500`
- MC win rate: `0.6667`

### TradervR1_lab_r04_06_a_attack_tuning

- Parent: `TradervR1_lab_r03_04_a_attack_tuning_a_quality_guard_p_entry_quality`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `288731.0000`
- Delta vs safe baseline: `688.5000`
- Delta vs aggressive anchor: `-1113.5000`
- Composite score: `671.5150`

### TradervR1_lab_r04_02_a_attack_tuning

- Parent: `TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289209.0000`
- Delta vs safe baseline: `1166.5000`
- Delta vs aggressive anchor: `-635.5000`
- Composite score: `-30.2205`
- MC plausible mean delta: `-916.2500`
- MC plausible p10 delta: `-5867.5000`
- MC win rate: `0.6667`

## Family Weight Update

- ash_attack_tuning: mean_score=-147.19 old=0.221 new=0.206
- ash_quality_guard: mean_score=319.58 old=0.243 new=0.278
- ash_local_fair_blend: mean_score=3093.76 old=0.175 new=0.271
- pepper_entry_quality: mean_score=-113.63 old=0.177 new=0.2
- pepper_carry_defense: mean_score=-113.63 old=0.185 new=0.2

