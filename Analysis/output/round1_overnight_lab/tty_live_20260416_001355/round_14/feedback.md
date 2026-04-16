# Round 14 Feedback

## Top Candidates

### TradervR1_lab_r14_01_a_attack_tuning_a_quality_guard

- Parent: `TradervR1_47`
- Families: `ash_attack_tuning, ash_quality_guard`
- Strategy refs: `1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289529.0000`
- Delta vs safe baseline: `1486.5000`
- Delta vs aggressive anchor: `-315.5000`
- Composite score: `2870.2867`
- MC plausible mean delta: `2596.1667`
- MC plausible p10 delta: `1605.2500`
- MC win rate: `1.0000`

### TradervR1_lab_r14_01_a_attack_tuning_a_quality_guard_cmaes_ash_attack_tuning

- Parent: `TradervR1_lab_r14_01_a_attack_tuning_a_quality_guard`
- Families: `ash_attack_tuning, cmaes_refine`
- Strategy refs: `1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289529.0000`
- Delta vs safe baseline: `1486.5000`
- Delta vs aggressive anchor: `-315.5000`
- Composite score: `2731.4583`
- MC plausible mean delta: `2373.0833`
- MC plausible p10 delta: `1251.0000`
- MC win rate: `1.0000`

### TradervR1_lab_r14_04_a_local_fair_blend

- Parent: `TradervR1_47_2`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `289460.5000`
- Delta vs safe baseline: `1418.0000`
- Delta vs aggressive anchor: `-384.0000`
- Composite score: `1501.0200`

### TradervR1_lab_r14_06_p_carry_defense

- Parent: `TradervR1_lab_r13_07_p_entry_quality_a_quality_guard`
- Families: `pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum`
- Deterministic total: `289768.5000`
- Delta vs safe baseline: `1726.0000`
- Delta vs aggressive anchor: `-76.0000`
- Composite score: `1379.0278`
- MC plausible mean delta: `-381.6667`
- MC plausible p10 delta: `-2630.0000`
- MC win rate: `0.6667`

### TradervR1_lab_r14_07_a_quality_guard_p_carry_defense

- Parent: `TradervR1_lab_r13_06_a_quality_guard`
- Families: `ash_quality_guard, pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `289836.5000`
- Delta vs safe baseline: `1794.0000`
- Delta vs aggressive anchor: `-8.0000`
- Composite score: `342.8162`
- MC plausible mean delta: `-1368.3333`
- MC plausible p10 delta: `-7795.7500`
- MC win rate: `0.6667`

## Family Weight Update

- ash_attack_tuning: mean_score=1609.86 old=0.138 new=0.213
- ash_quality_guard: mean_score=557.95 old=0.317 new=0.397
- ash_local_fair_blend: mean_score=1501.02 old=0.138 new=0.213
- pepper_entry_quality: mean_score=0.0 old=0.201 new=0.2
- pepper_carry_defense: mean_score=300.34 old=0.207 new=0.235

