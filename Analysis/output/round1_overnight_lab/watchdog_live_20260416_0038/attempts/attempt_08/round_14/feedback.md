# Round 14 Feedback

## Top Candidates

### TradervR1_lab_r14_08_a_attack_tuning_p_carry_defense

- Parent: `TradervR1_47_2`
- Families: `ash_attack_tuning, pepper_carry_defense`
- Strategy refs: `1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 1.4 Spread-Capture Only MM; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `288621.0000`
- Delta vs safe baseline: `578.5000`
- Delta vs aggressive anchor: `-1223.5000`
- Composite score: `105.5628`
- MC plausible mean delta: `-184.9167`
- MC plausible p10 delta: `-2193.0000`
- MC win rate: `0.6667`

### TradervR1_lab_r14_01_a_quality_guard_a_local_fair_blend

- Parent: `TradervR1_34_1`
- Families: `ash_quality_guard, ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `288360.0000`
- Delta vs safe baseline: `317.5000`
- Delta vs aggressive anchor: `-1484.5000`
- Composite score: `96.6528`
- MC plausible mean delta: `226.3333`
- MC plausible p10 delta: `-1410.7500`
- MC win rate: `0.6667`

### TradervR1_lab_r14_06_p_entry_quality

- Parent: `TradervR1_42_O2_1`
- Families: `pepper_entry_quality`
- Strategy refs: `2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `288015.5000`
- Delta vs safe baseline: `-27.0000`
- Delta vs aggressive anchor: `-1829.0000`
- Composite score: `-38.6100`

### TradervR1_lab_r14_03_p_entry_quality_p_carry_defense

- Parent: `TradervR1_42_O2_1`
- Families: `pepper_entry_quality, pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `287952.5000`
- Delta vs safe baseline: `-90.0000`
- Delta vs aggressive anchor: `-1892.0000`
- Composite score: `-116.0700`

### TradervR1_lab_r14_08_a_attack_tuning_p_carry_defense_cmaes_ash_attack_tuning

- Parent: `TradervR1_lab_r14_08_a_attack_tuning_p_carry_defense`
- Families: `ash_attack_tuning, cmaes_refine`
- Strategy refs: `1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 1.4 Spread-Capture Only MM; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `288621.0000`
- Delta vs safe baseline: `578.5000`
- Delta vs aggressive anchor: `-1223.5000`
- Composite score: `-142.0205`
- MC plausible mean delta: `-535.2500`
- MC plausible p10 delta: `-2960.5000`
- MC win rate: `0.6667`

## Family Weight Update

- ash_attack_tuning: mean_score=-18.23 old=0.182 new=0.2
- ash_quality_guard: mean_score=-111.01 old=0.182 new=0.2
- ash_local_fair_blend: mean_score=-352.03 old=0.182 new=0.2
- pepper_entry_quality: mean_score=-125.08 old=0.253 new=0.239
- pepper_carry_defense: mean_score=-5.25 old=0.2 new=0.2

