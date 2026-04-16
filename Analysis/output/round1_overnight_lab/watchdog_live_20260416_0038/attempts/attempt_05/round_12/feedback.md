# Round 12 Feedback

## Top Candidates

### TradervR1_lab_r12_07_a_local_fair_blend_a_attack_tuning

- Parent: `TradervR1_47_2`
- Families: `ash_local_fair_blend, ash_attack_tuning`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `289878.0000`
- Delta vs safe baseline: `1835.5000`
- Delta vs aggressive anchor: `33.5000`
- Composite score: `1891.6105`
- MC plausible mean delta: `611.2500`
- MC plausible p10 delta: `-2402.0000`
- MC win rate: `0.8333`

### TradervR1_lab_r12_08_p_entry_quality

- Parent: `TradervR1_lab_r11_05_p_carry_defense_p_entry_quality`
- Families: `pepper_entry_quality`
- Strategy refs: `2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `289837.5000`
- Delta vs safe baseline: `1795.0000`
- Delta vs aggressive anchor: `-7.0000`
- Composite score: `1614.8495`
- MC plausible mean delta: `155.5000`
- MC plausible p10 delta: `-3070.7500`
- MC win rate: `0.6667`

### TradervR1_lab_r12_07_a_local_fair_blend_a_attack_tuning_cmaes_ash_local_fair_blend

- Parent: `TradervR1_lab_r12_07_a_local_fair_blend_a_attack_tuning`
- Families: `ash_local_fair_blend, cmaes_refine`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `289878.0000`
- Delta vs safe baseline: `1835.5000`
- Delta vs aggressive anchor: `33.5000`
- Composite score: `1489.0855`
- MC plausible mean delta: `106.7500`
- MC plausible p10 delta: `-3835.7500`
- MC win rate: `0.8333`

### TradervR1_lab_r12_05_p_entry_quality

- Parent: `TradervR1_lab_r11_04_p_entry_quality`
- Families: `pepper_entry_quality`
- Strategy refs: `2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `289354.5000`
- Delta vs safe baseline: `1312.0000`
- Delta vs aggressive anchor: `-490.0000`
- Composite score: `1356.5900`

### TradervR1_lab_r12_02_a_quality_guard

- Parent: `TradervR1_lab_r11_04_p_entry_quality`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289178.0000`
- Delta vs safe baseline: `1135.5000`
- Delta vs aggressive anchor: `-666.5000`
- Composite score: `1153.5150`

## Family Weight Update

- ash_attack_tuning: mean_score=953.44 old=0.172 new=0.247
- ash_quality_guard: mean_score=-36.47 old=0.252 new=0.248
- ash_local_fair_blend: mean_score=822.43 old=0.16 new=0.22
- pepper_entry_quality: mean_score=802.63 old=0.194 new=0.265
- pepper_carry_defense: mean_score=0.0 old=0.221 new=0.203

