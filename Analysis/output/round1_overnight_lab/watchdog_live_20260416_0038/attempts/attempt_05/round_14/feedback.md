# Round 14 Feedback

## Top Candidates

### TradervR1_lab_r14_05_a_local_fair_blend

- Parent: `TradervR1_42_P1_1`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `288252.0000`
- Delta vs safe baseline: `209.5000`
- Delta vs aggressive anchor: `-1592.5000`
- Composite score: `417.8772`
- MC plausible mean delta: `910.4167`
- MC plausible p10 delta: `-255.0000`
- MC win rate: `0.8333`

### TradervR1_lab_r14_07_p_entry_quality

- Parent: `TradervR1_42_O2_1`
- Families: `pepper_entry_quality`
- Strategy refs: `2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `288015.5000`
- Delta vs safe baseline: `-27.0000`
- Delta vs aggressive anchor: `-1829.0000`
- Composite score: `-38.6100`

### TradervR1_lab_r14_04_p_entry_quality_p_carry_defense

- Parent: `TradervR1_42_O2_1`
- Families: `pepper_entry_quality, pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `287952.5000`
- Delta vs safe baseline: `-90.0000`
- Delta vs aggressive anchor: `-1892.0000`
- Composite score: `-116.0700`

### TradervR1_lab_r14_06_p_entry_quality_a_quality_guard

- Parent: `TradervR1_lab_r13_06_a_quality_guard`
- Families: `pepper_entry_quality, ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `287881.5000`
- Delta vs safe baseline: `-161.0000`
- Delta vs aggressive anchor: `-1963.0000`
- Composite score: `-194.9900`

### TradervR1_lab_r14_03_a_quality_guard

- Parent: `TradervR1_34_1`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `287863.5000`
- Delta vs safe baseline: `-179.0000`
- Delta vs aggressive anchor: `-1981.0000`
- Composite score: `-209.1200`

## Family Weight Update

- ash_attack_tuning: mean_score=0.0 old=0.196 new=0.2
- ash_quality_guard: mean_score=-468.99 old=0.196 new=0.2
- ash_local_fair_blend: mean_score=-379.42 old=0.196 new=0.2
- pepper_entry_quality: mean_score=-116.56 old=0.205 new=0.2
- pepper_carry_defense: mean_score=-708.11 old=0.207 new=0.2

