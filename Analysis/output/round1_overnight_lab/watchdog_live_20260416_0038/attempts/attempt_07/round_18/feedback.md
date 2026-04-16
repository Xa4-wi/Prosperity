# Round 18 Feedback

## Top Candidates

### TradervR1_lab_r18_06_a_attack_tuning

- Parent: `TradervR1_lab_r17_01_a_local_fair_blend_a_quality_guard`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289573.0000`
- Delta vs safe baseline: `1530.5000`
- Delta vs aggressive anchor: `-271.5000`
- Composite score: `2300.6455`
- MC plausible mean delta: `1739.2500`
- MC plausible p10 delta: `194.2500`
- MC win rate: `0.8333`

### TradervR1_lab_r18_06_a_attack_tuning_cmaes_ash_attack_tuning

- Parent: `TradervR1_lab_r18_06_a_attack_tuning`
- Families: `ash_attack_tuning, cmaes_refine`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289573.0000`
- Delta vs safe baseline: `1530.5000`
- Delta vs aggressive anchor: `-271.5000`
- Composite score: `1663.0462`
- MC plausible mean delta: `954.4167`
- MC plausible p10 delta: `-2076.0000`
- MC win rate: `0.6667`

### TradervR1_lab_r18_02_a_quality_guard

- Parent: `TradervR1_lab_r17_08_p_carry_defense_p_entry_quality`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289500.5000`
- Delta vs safe baseline: `1458.0000`
- Delta vs aggressive anchor: `-344.0000`
- Composite score: `1526.8700`

### TradervR1_lab_r18_04_a_attack_tuning_a_quality_guard

- Parent: `TradervR1_lab_r17_01_a_local_fair_blend_a_quality_guard`
- Families: `ash_attack_tuning, ash_quality_guard`
- Strategy refs: `1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289334.0000`
- Delta vs safe baseline: `1291.5000`
- Delta vs aggressive anchor: `-510.5000`
- Composite score: `1351.3050`

### TradervR1_lab_r18_08_a_quality_guard

- Parent: `TradervR1_47`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `290021.5000`
- Delta vs safe baseline: `1979.0000`
- Delta vs aggressive anchor: `177.0000`
- Composite score: `1007.0612`
- MC plausible mean delta: `-363.0833`
- MC plausible p10 delta: `-6980.5000`
- MC win rate: `0.6667`

## Family Weight Update

- ash_attack_tuning: mean_score=1106.81 old=0.169 new=0.254
- ash_quality_guard: mean_score=1295.08 old=0.189 new=0.292
- ash_local_fair_blend: mean_score=629.38 old=0.24 new=0.309
- pepper_entry_quality: mean_score=-410.31 old=0.169 new=0.2
- pepper_carry_defense: mean_score=175.36 old=0.233 new=0.252

