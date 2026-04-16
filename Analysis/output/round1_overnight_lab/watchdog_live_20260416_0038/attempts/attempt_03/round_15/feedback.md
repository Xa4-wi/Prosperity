# Round 15 Feedback

## Top Candidates

### TradervR1_lab_r15_08_a_local_fair_blend

- Parent: `TradervR1_47`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `290154.5000`
- Delta vs safe baseline: `2112.0000`
- Delta vs aggressive anchor: `310.0000`
- Composite score: `2510.0388`
- MC plausible mean delta: `1594.8333`
- MC plausible p10 delta: `-3118.5000`
- MC win rate: `0.8333`

### TradervR1_lab_r15_02_a_quality_guard_a_local_fair_blend

- Parent: `TradervR1_47`
- Families: `ash_quality_guard, ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `290392.0000`
- Delta vs safe baseline: `2349.5000`
- Delta vs aggressive anchor: `547.5000`
- Composite score: `2181.9888`
- MC plausible mean delta: `110.5833`
- MC plausible p10 delta: `-3383.2500`
- MC win rate: `0.8333`

### TradervR1_lab_r15_05_a_quality_guard_p_carry_defense

- Parent: `TradervR1_34_1`
- Families: `ash_quality_guard, pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `287987.5000`
- Delta vs safe baseline: `-55.0000`
- Delta vs aggressive anchor: `-1857.0000`
- Composite score: `-68.1200`

### TradervR1_lab_r15_03_a_attack_tuning_a_local_fair_blend

- Parent: `TradervR1_39_4`
- Families: `ash_attack_tuning, ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `287909.5000`
- Delta vs safe baseline: `-133.0000`
- Delta vs aggressive anchor: `-1935.0000`
- Composite score: `-213.3000`

### TradervR1_lab_r15_06_a_local_fair_blend_p_carry_defense

- Parent: `TradervR1_42_P1_1`
- Families: `ash_local_fair_blend, pepper_carry_defense`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `287916.0000`
- Delta vs safe baseline: `-126.5000`
- Delta vs aggressive anchor: `-1928.5000`
- Composite score: `-213.7750`

## Family Weight Update

- ash_attack_tuning: mean_score=-213.3 old=0.197 new=0.2
- ash_quality_guard: mean_score=551.02 old=0.197 new=0.246
- ash_local_fair_blend: mean_score=570.35 old=0.197 new=0.248
- pepper_entry_quality: mean_score=-382.03 old=0.212 new=0.2
- pepper_carry_defense: mean_score=-257.6 old=0.197 new=0.2

