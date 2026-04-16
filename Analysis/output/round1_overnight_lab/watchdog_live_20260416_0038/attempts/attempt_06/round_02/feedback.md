# Round 2 Feedback

## Top Candidates

### TradervR1_lab_r02_03_a_attack_tuning_a_quality_guard

- Parent: `TradervR1_lab_r01_04_p_carry_defense`
- Families: `ash_attack_tuning, ash_quality_guard`
- Strategy refs: `1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `290017.5000`
- Delta vs safe baseline: `1975.0000`
- Delta vs aggressive anchor: `173.0000`
- Composite score: `2457.0822`
- MC plausible mean delta: `1911.1667`
- MC plausible p10 delta: `-3017.5000`
- MC win rate: `0.8333`

### TradervR1_lab_r02_04_a_local_fair_blend

- Parent: `TradervR1_47_2`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `289699.5000`
- Delta vs safe baseline: `1657.0000`
- Delta vs aggressive anchor: `-145.0000`
- Composite score: `1755.6800`

### TradervR1_lab_r02_08_p_carry_defense

- Parent: `TradervR1_47`
- Families: `pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum`
- Deterministic total: `289800.5000`
- Delta vs safe baseline: `1758.0000`
- Delta vs aggressive anchor: `-44.0000`
- Composite score: `1599.8278`
- MC plausible mean delta: `292.5833`
- MC plausible p10 delta: `-3174.5000`
- MC win rate: `0.6667`

### TradervR1_lab_r02_06_p_carry_defense

- Parent: `TradervR1_lab_r01_08_p_carry_defense_a_quality_guard`
- Families: `pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum`
- Deterministic total: `289499.5000`
- Delta vs safe baseline: `1457.0000`
- Delta vs aggressive anchor: `-345.0000`
- Composite score: `1520.2800`

### TradervR1_lab_r02_01_a_attack_tuning_p_carry_defense

- Parent: `TradervR1_47`
- Families: `ash_attack_tuning, pepper_carry_defense`
- Strategy refs: `1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 1.4 Spread-Capture Only MM; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `289323.5000`
- Delta vs safe baseline: `1281.0000`
- Delta vs aggressive anchor: `-521.0000`
- Composite score: `1376.3500`

## Family Weight Update

- ash_attack_tuning: mean_score=1690.7 old=0.165 new=0.256
- ash_quality_guard: mean_score=1605.12 old=0.221 new=0.342
- ash_local_fair_blend: mean_score=632.75 old=0.19 new=0.245
- pepper_entry_quality: mean_score=753.17 old=0.203 new=0.273
- pepper_carry_defense: mean_score=1498.82 old=0.221 new=0.342

