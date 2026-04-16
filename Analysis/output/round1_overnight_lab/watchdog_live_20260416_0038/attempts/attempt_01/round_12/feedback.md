# Round 12 Feedback

## Top Candidates

### TradervR1_lab_r12_07_a_local_fair_blend_a_attack_tuning

- Parent: `TradervR1_47_2`
- Families: `ash_local_fair_blend, ash_attack_tuning`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `289878.0000`
- Delta vs safe baseline: `1835.5000`
- Delta vs aggressive anchor: `33.5000`
- Composite score: `2512.6555`
- MC plausible mean delta: `1603.2500`
- MC plausible p10 delta: `-800.2500`
- MC win rate: `0.8333`

### TradervR1_lab_r12_07_a_local_fair_blend_a_attack_tuning_cmaes_ash_local_fair_blend

- Parent: `TradervR1_lab_r12_07_a_local_fair_blend_a_attack_tuning`
- Families: `ash_local_fair_blend, cmaes_refine`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `289878.0000`
- Delta vs safe baseline: `1835.5000`
- Delta vs aggressive anchor: `33.5000`
- Composite score: `1303.0928`
- MC plausible mean delta: `-112.9167`
- MC plausible p10 delta: `-4495.0000`
- MC win rate: `0.6667`

### TradervR1_lab_r12_06_a_local_fair_blend_p_entry_quality

- Parent: `TradervR1_47_2`
- Families: `ash_local_fair_blend, pepper_entry_quality`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `289042.5000`
- Delta vs safe baseline: `1000.0000`
- Delta vs aggressive anchor: `-802.0000`
- Composite score: `1099.1900`

### TradervR1_lab_r12_02_a_quality_guard

- Parent: `TradervR1_lab_r11_03_p_entry_quality_p_carry_defense_a_attack_tuning`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `288842.0000`
- Delta vs safe baseline: `799.5000`
- Delta vs aggressive anchor: `-1002.5000`
- Composite score: `829.5150`

### TradervR1_lab_r12_05_p_entry_quality

- Parent: `TradervR1_lab_r11_03_p_entry_quality_p_carry_defense_a_attack_tuning`
- Families: `pepper_entry_quality`
- Strategy refs: `2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `288818.5000`
- Delta vs safe baseline: `776.0000`
- Delta vs aggressive anchor: `-1026.0000`
- Composite score: `828.2300`

## Family Weight Update

- ash_attack_tuning: mean_score=1081.09 old=0.167 new=0.25
- ash_quality_guard: mean_score=-144.47 old=0.242 new=0.226
- ash_local_fair_blend: mean_score=931.2 old=0.166 new=0.236
- pepper_entry_quality: mean_score=432.05 old=0.218 new=0.261
- pepper_carry_defense: mean_score=0.0 old=0.207 new=0.2

