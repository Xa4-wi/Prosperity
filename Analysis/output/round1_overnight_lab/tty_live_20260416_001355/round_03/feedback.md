# Round 3 Feedback

## Top Candidates

### TradervR1_lab_r03_08_p_entry_quality_a_quality_guard

- Parent: `TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard_best`
- Families: `pepper_entry_quality, ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `290011.5000`
- Delta vs safe baseline: `1969.0000`
- Delta vs aggressive anchor: `167.0000`
- Composite score: `3097.2455`
- MC plausible mean delta: `2232.0000`
- MC plausible p10 delta: `-45.0000`
- MC win rate: `0.8333`

### TradervR1_lab_r03_02_p_entry_quality_a_attack_tuning

- Parent: `TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard_best`
- Families: `pepper_entry_quality, ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `289769.5000`
- Delta vs safe baseline: `1727.0000`
- Delta vs aggressive anchor: `-75.0000`
- Composite score: `2078.0645`
- MC plausible mean delta: `1321.0000`
- MC plausible p10 delta: `-2172.5000`
- MC win rate: `0.6667`

### TradervR1_lab_r03_05_p_entry_quality_a_local_fair_blend

- Parent: `TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard`
- Families: `pepper_entry_quality, ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `289212.5000`
- Delta vs safe baseline: `1170.0000`
- Delta vs aggressive anchor: `-632.0000`
- Composite score: `1247.1300`

### TradervR1_lab_r03_07_a_attack_tuning

- Parent: `TradervR1_lab_r02_06_a_local_fair_blend_a_attack_tuning`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289769.0000`
- Delta vs safe baseline: `1726.5000`
- Delta vs aggressive anchor: `-75.5000`
- Composite score: `918.8178`
- MC plausible mean delta: `-289.9167`
- MC plausible p10 delta: `-5737.2500`
- MC win rate: `0.6667`

### TradervR1_lab_r03_06_a_quality_guard

- Parent: `TradervR1_34_1`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `287890.5000`
- Delta vs safe baseline: `-152.0000`
- Delta vs aggressive anchor: `-1954.0000`
- Composite score: `-182.1200`

## Family Weight Update

- ash_attack_tuning: mean_score=1498.44 old=0.196 new=0.303
- ash_quality_guard: mean_score=1457.56 old=0.215 new=0.334
- ash_local_fair_blend: mean_score=-99.25 old=0.202 new=0.2
- pepper_entry_quality: mean_score=1523.2 old=0.224 new=0.347
- pepper_carry_defense: mean_score=-329.64 old=0.163 new=0.2

