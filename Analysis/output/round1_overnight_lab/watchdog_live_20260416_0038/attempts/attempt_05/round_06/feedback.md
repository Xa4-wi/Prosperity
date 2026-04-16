# Round 6 Feedback

## Top Candidates

### TradervR1_lab_r06_04_p_carry_defense_p_entry_quality

- Parent: `TradervR1_47_2`
- Families: `pepper_carry_defense, pepper_entry_quality`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `289311.5000`
- Delta vs safe baseline: `1269.0000`
- Delta vs aggressive anchor: `-533.0000`
- Composite score: `1316.4400`

### TradervR1_lab_r06_05_a_quality_guard_a_local_fair_blend

- Parent: `TradervR1_47`
- Families: `ash_quality_guard, ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `289258.5000`
- Delta vs safe baseline: `1216.0000`
- Delta vs aggressive anchor: `-586.0000`
- Composite score: `1284.9000`

### TradervR1_lab_r06_03_a_attack_tuning

- Parent: `TradervR1_lab_r05_02_p_carry_defense`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289312.0000`
- Delta vs safe baseline: `1269.5000`
- Delta vs aggressive anchor: `-532.5000`
- Composite score: `1125.6022`
- MC plausible mean delta: `234.4167`
- MC plausible p10 delta: `-2195.7500`
- MC win rate: `0.8333`

### TradervR1_lab_r06_03_a_attack_tuning_cmaes_ash_attack_tuning

- Parent: `TradervR1_lab_r06_03_a_attack_tuning`
- Families: `ash_attack_tuning, cmaes_refine`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289409.0000`
- Delta vs safe baseline: `1366.5000`
- Delta vs aggressive anchor: `-435.5000`
- Composite score: `412.2478`
- MC plausible mean delta: `-810.9167`
- MC plausible p10 delta: `-5097.2500`
- MC win rate: `0.6667`

### TradervR1_lab_r06_02_a_quality_guard_a_local_fair_blend_p_carry_defense

- Parent: `TradervR1_47_2`
- Families: `ash_quality_guard, ash_local_fair_blend, pepper_carry_defense`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `289546.0000`
- Delta vs safe baseline: `1503.5000`
- Delta vs aggressive anchor: `-298.5000`
- Composite score: `82.7712`
- MC plausible mean delta: `-1690.5833`
- MC plausible p10 delta: `-6112.7500`
- MC win rate: `0.6667`

## Family Weight Update

- ash_attack_tuning: mean_score=174.72 old=0.22 new=0.237
- ash_quality_guard: mean_score=-17.99 old=0.165 new=0.2
- ash_local_fair_blend: mean_score=683.84 old=0.245 new=0.321
- pepper_entry_quality: mean_score=644.71 old=0.191 new=0.247
- pepper_carry_defense: mean_score=152.48 old=0.179 new=0.2

