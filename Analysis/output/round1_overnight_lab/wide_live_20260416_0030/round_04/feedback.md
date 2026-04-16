# Round 4 Feedback

## Top Candidates

### TradervR1_lab_r04_01_a_local_fair_blend

- Parent: `TradervR1_lab_r03_03_a_local_fair_blend_p_entry_quality`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `292504.5000`
- Delta vs safe baseline: `4462.0000`
- Delta vs aggressive anchor: `2660.0000`
- Composite score: `7767.2717`
- MC plausible mean delta: `5575.4167`
- MC plausible p10 delta: `4942.7500`
- MC win rate: `1.0000`

### TradervR1_lab_r04_01_a_local_fair_blend_cmaes_ash_local_fair_blend

- Parent: `TradervR1_lab_r04_01_a_local_fair_blend`
- Families: `ash_local_fair_blend, cmaes_refine`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `292504.5000`
- Delta vs safe baseline: `4462.0000`
- Delta vs aggressive anchor: `2660.0000`
- Composite score: `6738.0888`
- MC plausible mean delta: `4223.5833`
- MC plausible p10 delta: `1495.5000`
- MC win rate: `0.8333`

### TradervR1_lab_r04_07_a_quality_guard

- Parent: `TradervR1_lab_r03_08_a_attack_tuning_a_quality_guard_p_entry_quality`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `290253.0000`
- Delta vs safe baseline: `2210.5000`
- Delta vs aggressive anchor: `408.5000`
- Composite score: `2716.0838`
- MC plausible mean delta: `1140.3333`
- MC plausible p10 delta: `-954.0000`
- MC win rate: `0.8333`

### TradervR1_lab_r04_02_a_attack_tuning

- Parent: `TradervR1_lab_r03_08_a_attack_tuning_a_quality_guard_p_entry_quality`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289989.5000`
- Delta vs safe baseline: `1947.0000`
- Delta vs aggressive anchor: `145.0000`
- Composite score: `1958.1912`
- MC plausible mean delta: `484.6667`
- MC plausible p10 delta: `-2356.5000`
- MC win rate: `0.6667`

### TradervR1_lab_r04_06_a_attack_tuning

- Parent: `TradervR1_lab_r03_01_a_local_fair_blend`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289145.5000`
- Delta vs safe baseline: `1103.0000`
- Delta vs aggressive anchor: `-699.0000`
- Composite score: `1143.2800`

## Family Weight Update

- ash_attack_tuning: mean_score=467.86 old=0.222 new=0.269
- ash_quality_guard: mean_score=724.76 old=0.233 new=0.31
- ash_local_fair_blend: mean_score=3498.85 old=0.184 new=0.285
- pepper_entry_quality: mean_score=-113.63 old=0.183 new=0.2
- pepper_carry_defense: mean_score=-113.63 old=0.178 new=0.2

