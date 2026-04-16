# Round 4 Feedback

## Top Candidates

### TradervR1_lab_r04_01_a_local_fair_blend

- Parent: `TradervR1_lab_r03_08_a_attack_tuning_a_quality_guard_p_entry_quality`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `292738.0000`
- Delta vs safe baseline: `4695.5000`
- Delta vs aggressive anchor: `2893.5000`
- Composite score: `7745.5817`
- MC plausible mean delta: `5220.6667`
- MC plausible p10 delta: `3536.5000`
- MC win rate: `1.0000`

### TradervR1_lab_r04_01_a_local_fair_blend_cmaes_ash_local_fair_blend

- Parent: `TradervR1_lab_r04_01_a_local_fair_blend`
- Families: `ash_local_fair_blend, cmaes_refine`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `292738.0000`
- Delta vs safe baseline: `4695.5000`
- Delta vs aggressive anchor: `2893.5000`
- Composite score: `7230.9655`
- MC plausible mean delta: `4486.7500`
- MC plausible p10 delta: `1999.2500`
- MC win rate: `0.8333`

### TradervR1_lab_r04_06_a_attack_tuning

- Parent: `TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289528.5000`
- Delta vs safe baseline: `1486.0000`
- Delta vs aggressive anchor: `-316.0000`
- Composite score: `1810.0188`
- MC plausible mean delta: `901.8333`
- MC plausible p10 delta: `-874.0000`
- MC win rate: `0.8333`

### TradervR1_lab_r04_02_a_attack_tuning

- Parent: `TradervR1_lab_r03_01_a_local_fair_blend`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `288813.0000`
- Delta vs safe baseline: `770.5000`
- Delta vs aggressive anchor: `-1031.5000`
- Composite score: `805.6150`

### TradervR1_lab_r04_07_a_quality_guard

- Parent: `TradervR1_lab_r03_01_a_local_fair_blend`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289082.0000`
- Delta vs safe baseline: `1039.5000`
- Delta vs aggressive anchor: `-762.5000`
- Composite score: `-47.9645`
- MC plausible mean delta: `-637.5000`
- MC plausible p10 delta: `-5986.7500`
- MC win rate: `0.8333`

## Family Weight Update

- ash_attack_tuning: mean_score=346.4 old=0.233 new=0.269
- ash_quality_guard: mean_score=-196.59 old=0.23 new=0.209
- ash_local_fair_blend: mean_score=3616.64 old=0.175 new=0.272
- pepper_entry_quality: mean_score=-113.63 old=0.175 new=0.2
- pepper_carry_defense: mean_score=-113.63 old=0.187 new=0.2

