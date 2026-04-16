# Round 12 Feedback

## Top Candidates

### TradervR1_lab_r12_06_a_local_fair_blend_a_attack_tuning

- Parent: `TradervR1_47_2`
- Families: `ash_local_fair_blend, ash_attack_tuning`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `289878.0000`
- Delta vs safe baseline: `1835.5000`
- Delta vs aggressive anchor: `33.5000`
- Composite score: `2247.6712`
- MC plausible mean delta: `1087.6667`
- MC plausible p10 delta: `-1178.2500`
- MC win rate: `0.6667`

### TradervR1_lab_r12_04_p_entry_quality

- Parent: `TradervR1_lab_r11_01_a_quality_guard`
- Families: `pepper_entry_quality`
- Strategy refs: `2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `289777.5000`
- Delta vs safe baseline: `1735.0000`
- Delta vs aggressive anchor: `-67.0000`
- Composite score: `1887.8600`

### TradervR1_lab_r12_06_a_local_fair_blend_a_attack_tuning_cmaes_ash_local_fair_blend

- Parent: `TradervR1_lab_r12_06_a_local_fair_blend_a_attack_tuning`
- Families: `ash_local_fair_blend, cmaes_refine`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `289878.0000`
- Delta vs safe baseline: `1835.5000`
- Delta vs aggressive anchor: `33.5000`
- Composite score: `1861.8805`
- MC plausible mean delta: `577.0000`
- MC plausible p10 delta: `-2516.5000`
- MC win rate: `0.8333`

### TradervR1_lab_r12_01_a_quality_guard

- Parent: `TradervR1_lab_r11_01_a_quality_guard`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289784.5000`
- Delta vs safe baseline: `1742.0000`
- Delta vs aggressive anchor: `-60.0000`
- Composite score: `1638.0072`
- MC plausible mean delta: `591.1667`
- MC plausible p10 delta: `-3719.2500`
- MC win rate: `0.8333`

### TradervR1_lab_r12_07_p_entry_quality

- Parent: `TradervR1_lab_r11_04_p_carry_defense_p_entry_quality`
- Families: `pepper_entry_quality`
- Strategy refs: `2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `289837.5000`
- Delta vs safe baseline: `1795.0000`
- Delta vs aggressive anchor: `-7.0000`
- Composite score: `1455.3112`
- MC plausible mean delta: `24.6667`
- MC plausible p10 delta: `-3836.5000`
- MC win rate: `0.6667`

## Family Weight Update

- ash_attack_tuning: mean_score=1176.86 old=0.192 new=0.295
- ash_quality_guard: mean_score=460.46 old=0.176 new=0.213
- ash_local_fair_blend: mean_score=1122.91 old=0.168 new=0.253
- pepper_entry_quality: mean_score=1145.06 old=0.242 new=0.369
- pepper_carry_defense: mean_score=0.0 old=0.222 new=0.204

