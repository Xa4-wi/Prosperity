# Round 15 Feedback

## Top Candidates

### TradervR1_lab_r15_08_a_local_fair_blend

- Parent: `TradervR1_47`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `290154.5000`
- Delta vs safe baseline: `2112.0000`
- Delta vs aggressive anchor: `310.0000`
- Composite score: `2882.8438`
- MC plausible mean delta: `1770.5833`
- MC plausible p10 delta: `-957.7500`
- MC win rate: `0.8333`

### TradervR1_lab_r15_02_a_quality_guard_a_local_fair_blend

- Parent: `TradervR1_47`
- Families: `ash_quality_guard, ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `290392.0000`
- Delta vs safe baseline: `2349.5000`
- Delta vs aggressive anchor: `547.5000`
- Composite score: `2229.6988`
- MC plausible mean delta: `273.0833`
- MC plausible p10 delta: `-3506.7500`
- MC win rate: `0.8333`

### TradervR1_lab_r15_04_a_quality_guard_a_local_fair_blend_p_carry_defense

- Parent: `TradervR1_lab_r14_01_a_quality_guard_a_local_fair_blend`
- Families: `ash_quality_guard, ash_local_fair_blend, pepper_carry_defense`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `289003.0000`
- Delta vs safe baseline: `960.5000`
- Delta vs aggressive anchor: `-841.5000`
- Composite score: `2069.7100`
- MC plausible mean delta: `2400.7500`
- MC plausible p10 delta: `1149.7500`
- MC win rate: `1.0000`

### TradervR1_lab_r15_07_a_local_fair_blend_p_entry_quality

- Parent: `TradervR1_39_4`
- Families: `ash_local_fair_blend, pepper_entry_quality`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `288376.0000`
- Delta vs safe baseline: `333.5000`
- Delta vs aggressive anchor: `-1468.5000`
- Composite score: `268.1250`

### TradervR1_lab_r15_05_a_quality_guard_p_carry_defense

- Parent: `TradervR1_34_1`
- Families: `ash_quality_guard, pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `287987.5000`
- Delta vs safe baseline: `-55.0000`
- Delta vs aggressive anchor: `-1857.0000`
- Composite score: `-68.1200`

## Family Weight Update

- ash_attack_tuning: mean_score=-213.3 old=0.203 new=0.2
- ash_quality_guard: mean_score=1410.43 old=0.191 new=0.297
- ash_local_fair_blend: mean_score=1170.55 old=0.191 new=0.293
- pepper_entry_quality: mean_score=268.12 old=0.215 new=0.241
- pepper_carry_defense: mean_score=375.04 old=0.2 new=0.234

