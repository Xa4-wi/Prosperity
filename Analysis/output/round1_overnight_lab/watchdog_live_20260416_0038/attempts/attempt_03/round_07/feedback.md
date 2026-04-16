# Round 7 Feedback

## Top Candidates

### TradervR1_lab_r07_07_a_local_fair_blend

- Parent: `TradervR1_lab_r06_03_a_attack_tuning_best`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `290181.0000`
- Delta vs safe baseline: `2138.5000`
- Delta vs aggressive anchor: `336.5000`
- Composite score: `1948.6788`
- MC plausible mean delta: `380.3333`
- MC plausible p10 delta: `-3823.7500`
- MC win rate: `0.8333`

### TradervR1_lab_r07_06_a_attack_tuning_a_local_fair_blend

- Parent: `TradervR1_lab_r06_05_a_quality_guard_a_local_fair_blend`
- Families: `ash_attack_tuning, ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `290137.0000`
- Delta vs safe baseline: `2094.5000`
- Delta vs aggressive anchor: `292.5000`
- Composite score: `1899.2588`
- MC plausible mean delta: `540.0833`
- MC plausible p10 delta: `-4118.7500`
- MC win rate: `0.8333`

### TradervR1_lab_r07_03_p_carry_defense

- Parent: `TradervR1_47`
- Families: `pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum`
- Deterministic total: `289835.5000`
- Delta vs safe baseline: `1793.0000`
- Delta vs aggressive anchor: `-9.0000`
- Composite score: `1661.2722`
- MC plausible mean delta: `237.9167`
- MC plausible p10 delta: `-2995.5000`
- MC win rate: `0.8333`

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

- ash_attack_tuning: mean_score=424.22 old=0.21 new=0.25
- ash_quality_guard: mean_score=-314.72 old=0.177 new=0.2
- ash_local_fair_blend: mean_score=911.76 old=0.23 new=0.325
- pepper_entry_quality: mean_score=-10.01 old=0.205 new=0.204
- pepper_carry_defense: mean_score=1661.27 old=0.179 new=0.277

