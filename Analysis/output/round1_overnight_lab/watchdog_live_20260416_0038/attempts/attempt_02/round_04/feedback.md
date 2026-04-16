# Round 4 Feedback

## Top Candidates

### TradervR1_lab_r04_01_a_local_fair_blend

- Parent: `TradervR1_lab_r03_08_a_attack_tuning_a_quality_guard_p_entry_quality`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `292738.0000`
- Delta vs safe baseline: `4695.5000`
- Delta vs aggressive anchor: `2893.5000`
- Composite score: `7692.2633`
- MC plausible mean delta: `4773.3333`
- MC plausible p10 delta: `4433.7500`
- MC win rate: `1.0000`

### TradervR1_lab_r04_01_a_local_fair_blend_cmaes_ash_local_fair_blend

- Parent: `TradervR1_lab_r04_01_a_local_fair_blend`
- Families: `ash_local_fair_blend, cmaes_refine`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `292738.0000`
- Delta vs safe baseline: `4695.5000`
- Delta vs aggressive anchor: `2893.5000`
- Composite score: `6231.3122`
- MC plausible mean delta: `2963.4167`
- MC plausible p10 delta: `-788.7500`
- MC win rate: `0.8333`

### TradervR1_lab_r04_07_a_quality_guard

- Parent: `TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289464.5000`
- Delta vs safe baseline: `1422.0000`
- Delta vs aggressive anchor: `-380.0000`
- Composite score: `1388.0805`
- MC plausible mean delta: `470.0000`
- MC plausible p10 delta: `-2175.7500`
- MC win rate: `0.8333`

### TradervR1_lab_r04_06_a_attack_tuning

- Parent: `TradervR1_lab_r03_04_a_attack_tuning_a_quality_guard_p_entry_quality`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `288731.0000`
- Delta vs safe baseline: `688.5000`
- Delta vs aggressive anchor: `-1113.5000`
- Composite score: `671.5150`

### TradervR1_lab_r04_03_p_carry_defense_p_entry_quality_a_local_fair_blend

- Parent: `TradervR1_42_P1_1`
- Families: `pepper_carry_defense, pepper_entry_quality, ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `287975.0000`
- Delta vs safe baseline: `-67.5000`
- Delta vs aggressive anchor: `-1869.5000`
- Composite score: `-113.6300`

## Family Weight Update

- ash_attack_tuning: mean_score=-177.46 old=0.219 new=0.202
- ash_quality_guard: mean_score=282.09 old=0.239 new=0.27
- ash_local_fair_blend: mean_score=3353.4 old=0.175 new=0.271
- pepper_entry_quality: mean_score=-113.63 old=0.19 new=0.2
- pepper_carry_defense: mean_score=-113.63 old=0.176 new=0.2

