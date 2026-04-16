# Round 5 Feedback

## Top Candidates

### TradervR1_lab_r05_03_a_local_fair_blend

- Parent: `TradervR1_lab_r04_01_a_local_fair_blend`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `292274.5000`
- Delta vs safe baseline: `4232.0000`
- Delta vs aggressive anchor: `2430.0000`
- Composite score: `6048.2588`
- MC plausible mean delta: `3566.0833`
- MC plausible p10 delta: `271.5000`
- MC win rate: `0.8333`

### TradervR1_lab_r05_05_a_attack_tuning

- Parent: `TradervR1_47_2`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289445.0000`
- Delta vs safe baseline: `1402.5000`
- Delta vs aggressive anchor: `-399.5000`
- Composite score: `1477.4850`

### TradervR1_lab_r05_02_p_carry_defense

- Parent: `TradervR1_47_2`
- Families: `pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum`
- Deterministic total: `289293.5000`
- Delta vs safe baseline: `1251.0000`
- Delta vs aggressive anchor: `-551.0000`
- Composite score: `1295.5900`

### TradervR1_lab_r05_06_a_attack_tuning_p_entry_quality_p_carry_defense

- Parent: `TradervR1_47`
- Families: `ash_attack_tuning, pepper_entry_quality, pepper_carry_defense`
- Strategy refs: `1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 1.4 Spread-Capture Only MM; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `289206.5000`
- Delta vs safe baseline: `1164.0000`
- Delta vs aggressive anchor: `-638.0000`
- Composite score: `1286.6800`

### TradervR1_lab_r05_01_p_carry_defense

- Parent: `TradervR1_47`
- Families: `pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum`
- Deterministic total: `289832.5000`
- Delta vs safe baseline: `1790.0000`
- Delta vs aggressive anchor: `-12.0000`
- Composite score: `886.6712`
- MC plausible mean delta: `-742.5833`
- MC plausible p10 delta: `-5524.0000`
- MC win rate: `0.6667`

## Family Weight Update

- ash_attack_tuning: mean_score=1382.08 old=0.199 new=0.309
- ash_quality_guard: mean_score=-225.46 old=0.212 new=0.2
- ash_local_fair_blend: mean_score=6048.26 old=0.231 new=0.358
- pepper_entry_quality: mean_score=898.92 old=0.179 new=0.252
- pepper_carry_defense: mean_score=616.17 old=0.179 new=0.229

