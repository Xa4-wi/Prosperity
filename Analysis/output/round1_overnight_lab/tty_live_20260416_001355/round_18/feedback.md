# Round 18 Feedback

## Top Candidates

### TradervR1_lab_r18_07_a_local_fair_blend_a_attack_tuning

- Parent: `TradervR1_47`
- Families: `ash_local_fair_blend, ash_attack_tuning`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `290242.5000`
- Delta vs safe baseline: `2200.0000`
- Delta vs aggressive anchor: `398.0000`
- Composite score: `3646.2500`
- MC plausible mean delta: `2479.5000`
- MC plausible p10 delta: `1611.0000`
- MC win rate: `1.0000`

### TradervR1_lab_r18_07_a_local_fair_blend_a_attack_tuning_cmaes_ash_local_fair_blend

- Parent: `TradervR1_lab_r18_07_a_local_fair_blend_a_attack_tuning`
- Families: `ash_local_fair_blend, cmaes_refine`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `290242.5000`
- Delta vs safe baseline: `2200.0000`
- Delta vs aggressive anchor: `398.0000`
- Composite score: `3392.0883`
- MC plausible mean delta: `1985.5833`
- MC plausible p10 delta: `1206.7500`
- MC win rate: `1.0000`

### TradervR1_lab_r18_04_a_local_fair_blend

- Parent: `TradervR1_lab_r17_03_p_entry_quality`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `289674.5000`
- Delta vs safe baseline: `1632.0000`
- Delta vs aggressive anchor: `-170.0000`
- Composite score: `1934.3278`
- MC plausible mean delta: `735.0833`
- MC plausible p10 delta: `-681.5000`
- MC win rate: `0.6667`

### TradervR1_lab_r18_08_p_entry_quality

- Parent: `TradervR1_47_2`
- Families: `pepper_entry_quality`
- Strategy refs: `2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `289363.5000`
- Delta vs safe baseline: `1321.0000`
- Delta vs aggressive anchor: `-481.0000`
- Composite score: `1368.4400`

### TradervR1_lab_r18_02_a_quality_guard_p_carry_defense

- Parent: `TradervR1_lab_r17_01_a_quality_guard`
- Families: `ash_quality_guard, pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `289266.5000`
- Delta vs safe baseline: `1224.0000`
- Delta vs aggressive anchor: `-578.0000`
- Composite score: `1271.6000`

## Family Weight Update

- ash_attack_tuning: mean_score=3646.25 old=0.15 new=0.232
- ash_quality_guard: mean_score=544.74 old=0.224 new=0.279
- ash_local_fair_blend: mean_score=2033.01 old=0.15 new=0.232
- pepper_entry_quality: mean_score=477.34 old=0.169 new=0.205
- pepper_carry_defense: mean_score=1271.6 old=0.308 new=0.477

