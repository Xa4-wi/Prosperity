# Round 11 Feedback

## Top Candidates

### TradervR1_lab_r11_02_a_quality_guard

- Parent: `TradervR1_47`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289784.5000`
- Delta vs safe baseline: `1742.0000`
- Delta vs aggressive anchor: `-60.0000`
- Composite score: `2583.6717`
- MC plausible mean delta: `1413.1667`
- MC plausible p10 delta: `645.2500`
- MC win rate: `1.0000`

### TradervR1_lab_r11_01_a_quality_guard_p_entry_quality

- Parent: `TradervR1_47`
- Families: `ash_quality_guard, pepper_entry_quality`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `290302.0000`
- Delta vs safe baseline: `2259.5000`
- Delta vs aggressive anchor: `457.5000`
- Composite score: `2558.9962`
- MC plausible mean delta: `905.4167`
- MC plausible p10 delta: `-1617.5000`
- MC win rate: `0.6667`

### TradervR1_lab_r11_03_p_entry_quality_p_carry_defense_a_attack_tuning

- Parent: `TradervR1_lab_r10_04_a_attack_tuning`
- Families: `pepper_entry_quality, pepper_carry_defense, ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 1.4 Spread-Capture Only MM; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `289504.0000`
- Delta vs safe baseline: `1461.5000`
- Delta vs aggressive anchor: `-340.5000`
- Composite score: `1610.1350`

### TradervR1_lab_r11_05_p_carry_defense_p_entry_quality

- Parent: `TradervR1_47`
- Families: `pepper_carry_defense, pepper_entry_quality`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `289836.5000`
- Delta vs safe baseline: `1794.0000`
- Delta vs aggressive anchor: `-8.0000`
- Composite score: `1579.0995`
- MC plausible mean delta: `127.2500`
- MC plausible p10 delta: `-3238.2500`
- MC win rate: `0.6667`

### TradervR1_lab_r11_04_p_entry_quality

- Parent: `TradervR1_47_2`
- Families: `pepper_entry_quality`
- Strategy refs: `2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `289363.5000`
- Delta vs safe baseline: `1321.0000`
- Delta vs aggressive anchor: `-481.0000`
- Composite score: `1368.4400`

## Family Weight Update

- ash_attack_tuning: mean_score=282.63 old=0.216 new=0.244
- ash_quality_guard: mean_score=2571.33 old=0.235 new=0.365
- ash_local_fair_blend: mean_score=-293.23 old=0.158 new=0.2
- pepper_entry_quality: mean_score=1287.14 old=0.175 new=0.271
- pepper_carry_defense: mean_score=1594.62 old=0.216 new=0.334

