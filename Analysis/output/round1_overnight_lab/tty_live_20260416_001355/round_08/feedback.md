# Round 8 Feedback

## Top Candidates

### TradervR1_lab_r08_05_a_quality_guard

- Parent: `TradervR1_lab_r07_07_p_carry_defense_a_quality_guard`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289762.5000`
- Delta vs safe baseline: `1720.0000`
- Delta vs aggressive anchor: `-82.0000`
- Composite score: `3151.8672`
- MC plausible mean delta: `3026.1667`
- MC plausible p10 delta: `358.2500`
- MC win rate: `0.8333`

### TradervR1_lab_r08_05_a_quality_guard_cmaes_ash_quality_guard

- Parent: `TradervR1_lab_r08_05_a_quality_guard`
- Families: `ash_quality_guard, cmaes_refine`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289762.5000`
- Delta vs safe baseline: `1720.0000`
- Delta vs aggressive anchor: `-82.0000`
- Composite score: `2585.9678`
- MC plausible mean delta: `1867.5833`
- MC plausible p10 delta: `-332.0000`
- MC win rate: `0.6667`

### TradervR1_lab_r08_03_p_entry_quality_a_local_fair_blend

- Parent: `TradervR1_lab_r07_07_p_carry_defense_a_quality_guard`
- Families: `pepper_entry_quality, ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `289436.0000`
- Delta vs safe baseline: `1393.5000`
- Delta vs aggressive anchor: `-408.5000`
- Composite score: `2424.6500`
- MC plausible mean delta: `2169.5000`
- MC plausible p10 delta: `782.2500`
- MC win rate: `1.0000`

### TradervR1_lab_r08_02_a_attack_tuning

- Parent: `TradervR1_lab_r07_05_p_entry_quality_a_local_fair_blend`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289485.0000`
- Delta vs safe baseline: `1442.5000`
- Delta vs aggressive anchor: `-359.5000`
- Composite score: `1672.4905`
- MC plausible mean delta: `875.7500`
- MC plausible p10 delta: `-1860.0000`
- MC win rate: `0.8333`

### TradervR1_lab_r08_07_a_quality_guard

- Parent: `TradervR1_47_2`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289321.5000`
- Delta vs safe baseline: `1279.0000`
- Delta vs aggressive anchor: `-523.0000`
- Composite score: `1326.4400`

## Family Weight Update

- ash_attack_tuning: mean_score=1672.49 old=0.137 new=0.213
- ash_quality_guard: mean_score=1167.66 old=0.301 new=0.46
- ash_local_fair_blend: mean_score=2424.65 old=0.137 new=0.213
- pepper_entry_quality: mean_score=780.97 old=0.273 new=0.37
- pepper_carry_defense: mean_score=0.0 old=0.152 new=0.2

