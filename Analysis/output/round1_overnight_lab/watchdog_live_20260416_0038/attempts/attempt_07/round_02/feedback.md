# Round 2 Feedback

## Top Candidates

### TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard

- Parent: `TradervR1_lab_r01_08_p_carry_defense_a_quality_guard`
- Families: `ash_attack_tuning, ash_quality_guard`
- Strategy refs: `1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289945.0000`
- Delta vs safe baseline: `1902.5000`
- Delta vs aggressive anchor: `100.5000`
- Composite score: `2790.8338`
- MC plausible mean delta: `1989.8333`
- MC plausible p10 delta: `-438.0000`
- MC win rate: `0.8333`

### TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard_cmaes_ash_attack_tuning

- Parent: `TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard`
- Families: `ash_attack_tuning, cmaes_refine`
- Strategy refs: `1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `290009.5000`
- Delta vs safe baseline: `1967.0000`
- Delta vs aggressive anchor: `165.0000`
- Composite score: `2272.9255`
- MC plausible mean delta: `1127.7500`
- MC plausible p10 delta: `-2190.0000`
- MC win rate: `0.8333`

### TradervR1_lab_r02_04_a_local_fair_blend

- Parent: `TradervR1_47_2`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `289699.5000`
- Delta vs safe baseline: `1657.0000`
- Delta vs aggressive anchor: `-145.0000`
- Composite score: `1755.6800`

### TradervR1_lab_r02_06_p_carry_defense

- Parent: `TradervR1_lab_r01_03_p_entry_quality_a_quality_guard`
- Families: `pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum`
- Deterministic total: `289483.5000`
- Delta vs safe baseline: `1441.0000`
- Delta vs aggressive anchor: `-361.0000`
- Composite score: `1506.8600`

### TradervR1_lab_r02_07_a_local_fair_blend_p_entry_quality_a_quality_guard

- Parent: `TradervR1_47_2`
- Families: `ash_local_fair_blend, pepper_entry_quality, ash_quality_guard`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `290129.0000`
- Delta vs safe baseline: `2086.5000`
- Delta vs aggressive anchor: `284.5000`
- Composite score: `1402.2333`
- MC plausible mean delta: `-1191.4167`
- MC plausible p10 delta: `-2757.7500`
- MC win rate: `0.0000`

## Family Weight Update

- ash_attack_tuning: mean_score=2146.7 old=0.165 new=0.255
- ash_quality_guard: mean_score=2096.53 old=0.22 new=0.341
- ash_local_fair_blend: mean_score=932.3 old=0.19 new=0.27
- pepper_entry_quality: mean_score=1402.23 old=0.205 new=0.318
- pepper_carry_defense: mean_score=1419.74 old=0.22 new=0.341

