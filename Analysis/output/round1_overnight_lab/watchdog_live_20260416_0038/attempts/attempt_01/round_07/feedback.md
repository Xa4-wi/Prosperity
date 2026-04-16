# Round 7 Feedback

## Top Candidates

### TradervR1_lab_r07_07_a_local_fair_blend

- Parent: `TradervR1_lab_r06_03_a_attack_tuning_best`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `290279.0000`
- Delta vs safe baseline: `2236.5000`
- Delta vs aggressive anchor: `434.5000`
- Composite score: `3236.7305`
- MC plausible mean delta: `1921.5000`
- MC plausible p10 delta: `315.0000`
- MC win rate: `0.8333`

### TradervR1_lab_r07_06_a_attack_tuning_a_local_fair_blend

- Parent: `TradervR1_lab_r06_05_a_quality_guard_a_local_fair_blend`
- Families: `ash_attack_tuning, ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `290137.0000`
- Delta vs safe baseline: `2094.5000`
- Delta vs aggressive anchor: `292.5000`
- Composite score: `2091.6228`
- MC plausible mean delta: `741.8333`
- MC plausible p10 delta: `-3279.5000`
- MC win rate: `0.6667`

### TradervR1_lab_r07_03_p_carry_defense

- Parent: `TradervR1_47`
- Families: `pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum`
- Deterministic total: `289835.5000`
- Delta vs safe baseline: `1793.0000`
- Delta vs aggressive anchor: `-9.0000`
- Composite score: `1425.8345`
- MC plausible mean delta: `-69.7500`
- MC plausible p10 delta: `-3756.5000`
- MC win rate: `0.6667`

### TradervR1_lab_r07_05_a_attack_tuning

- Parent: `TradervR1_lab_r06_04_p_carry_defense_p_entry_quality`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289075.5000`
- Delta vs safe baseline: `1033.0000`
- Delta vs aggressive anchor: `-769.0000`
- Composite score: `1087.9500`

### TradervR1_lab_r07_04_p_entry_quality_a_quality_guard

- Parent: `TradervR1_42_P1_1`
- Families: `pepper_entry_quality, ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `288035.5000`
- Delta vs safe baseline: `-7.0000`
- Delta vs aggressive anchor: `-1809.0000`
- Composite score: `-10.0100`

## Family Weight Update

- ash_attack_tuning: mean_score=472.31 old=0.203 new=0.247
- ash_quality_guard: mean_score=-314.72 old=0.171 new=0.2
- ash_local_fair_blend: mean_score=1405.23 old=0.246 new=0.381
- pepper_entry_quality: mean_score=-10.01 old=0.202 new=0.201
- pepper_carry_defense: mean_score=1425.83 old=0.177 new=0.275

