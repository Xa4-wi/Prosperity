# Round 8 Feedback

## Top Candidates

### TradervR1_lab_r08_07_a_attack_tuning_a_local_fair_blend

- Parent: `TradervR1_47_2`
- Families: `ash_attack_tuning, ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `289125.5000`
- Delta vs safe baseline: `1083.0000`
- Delta vs aggressive anchor: `-719.0000`
- Composite score: `1636.5672`
- MC plausible mean delta: `1727.4167`
- MC plausible p10 delta: `-966.2500`
- MC win rate: `0.8333`

### TradervR1_lab_r08_08_p_carry_defense_a_quality_guard

- Parent: `TradervR1_lab_r07_05_a_attack_tuning`
- Families: `pepper_carry_defense, ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `289075.5000`
- Delta vs safe baseline: `1033.0000`
- Delta vs aggressive anchor: `-769.0000`
- Composite score: `913.5078`
- MC plausible mean delta: `-99.6667`
- MC plausible p10 delta: `-688.5000`
- MC win rate: `0.6667`

### TradervR1_lab_r08_07_a_attack_tuning_a_local_fair_blend_cmaes_ash_attack_tuning

- Parent: `TradervR1_lab_r08_07_a_attack_tuning_a_local_fair_blend`
- Families: `ash_attack_tuning, cmaes_refine`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `289125.5000`
- Delta vs safe baseline: `1083.0000`
- Delta vs aggressive anchor: `-719.0000`
- Composite score: `366.4638`
- MC plausible mean delta: `-359.1667`
- MC plausible p10 delta: `-4076.7500`
- MC win rate: `0.8333`

### TradervR1_lab_r08_05_p_entry_quality_a_attack_tuning

- Parent: `TradervR1_47`
- Families: `pepper_entry_quality, ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `289354.5000`
- Delta vs safe baseline: `1312.0000`
- Delta vs aggressive anchor: `-490.0000`
- Composite score: `204.0662`
- MC plausible mean delta: `-838.5833`
- MC plausible p10 delta: `-6098.7500`
- MC win rate: `0.6667`

### TradervR1_lab_r08_03_p_carry_defense

- Parent: `TradervR1_34_1`
- Families: `pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum`
- Deterministic total: `288023.5000`
- Delta vs safe baseline: `-19.0000`
- Delta vs aggressive anchor: `-1821.0000`
- Composite score: `-38.6100`

## Family Weight Update

- ash_attack_tuning: mean_score=-268.34 old=0.185 new=0.2
- ash_quality_guard: mean_score=913.51 old=0.177 new=0.25
- ash_local_fair_blend: mean_score=-821.94 old=0.23 new=0.2
- pepper_entry_quality: mean_score=79.15 old=0.18 new=0.2
- pepper_carry_defense: mean_score=135.82 old=0.229 new=0.243

