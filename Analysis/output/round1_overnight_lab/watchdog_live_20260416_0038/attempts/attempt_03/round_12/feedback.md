# Round 12 Feedback

## Top Candidates

### TradervR1_lab_r12_06_a_local_fair_blend_a_attack_tuning_cmaes_ash_local_fair_blend

- Parent: `TradervR1_lab_r12_06_a_local_fair_blend_a_attack_tuning`
- Families: `ash_local_fair_blend, cmaes_refine`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `289878.0000`
- Delta vs safe baseline: `1835.5000`
- Delta vs aggressive anchor: `33.5000`
- Composite score: `2477.0072`
- MC plausible mean delta: `1310.1667`
- MC plausible p10 delta: `-217.5000`
- MC win rate: `0.8333`

### TradervR1_lab_r12_06_a_local_fair_blend_a_attack_tuning

- Parent: `TradervR1_47_2`
- Families: `ash_local_fair_blend, ash_attack_tuning`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `289878.0000`
- Delta vs safe baseline: `1835.5000`
- Delta vs aggressive anchor: `33.5000`
- Composite score: `1965.8045`
- MC plausible mean delta: `771.5000`
- MC plausible p10 delta: `-2288.2500`
- MC win rate: `0.6667`

### TradervR1_lab_r12_04_p_entry_quality

- Parent: `TradervR1_lab_r11_04_p_entry_quality`
- Families: `pepper_entry_quality`
- Strategy refs: `2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `289354.5000`
- Delta vs safe baseline: `1312.0000`
- Delta vs aggressive anchor: `-490.0000`
- Composite score: `1356.5900`

### TradervR1_lab_r12_03_p_entry_quality_a_quality_guard

- Parent: `TradervR1_47_2`
- Families: `pepper_entry_quality, ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `289321.5000`
- Delta vs safe baseline: `1279.0000`
- Delta vs aggressive anchor: `-523.0000`
- Composite score: `1326.4400`

### TradervR1_lab_r12_07_p_entry_quality

- Parent: `TradervR1_lab_r11_02_a_quality_guard`
- Families: `pepper_entry_quality`
- Strategy refs: `2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `289784.5000`
- Delta vs safe baseline: `1742.0000`
- Delta vs aggressive anchor: `-60.0000`
- Composite score: `1230.1128`
- MC plausible mean delta: `-629.4167`
- MC plausible p10 delta: `-3103.7500`
- MC win rate: `0.6667`

## Family Weight Update

- ash_attack_tuning: mean_score=1965.8 old=0.166 new=0.257
- ash_quality_guard: mean_score=217.45 old=0.234 new=0.257
- ash_local_fair_blend: mean_score=1012.18 old=0.161 new=0.235
- pepper_entry_quality: mean_score=878.8 old=0.219 new=0.307
- pepper_carry_defense: mean_score=0.0 old=0.221 new=0.203

