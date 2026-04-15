# Round 1 Feedback

## Top Candidates

### TradervR1_lab_r01_08_a_local_fair_blend

- Parent: `TradervR1_47`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `290080.0000`
- Delta vs safe baseline: `2037.5000`
- Delta vs aggressive anchor: `235.5000`
- Composite score: `3519.6033`
- MC plausible mean delta: `2462.3333`
- MC plausible p10 delta: `2040.7500`
- MC win rate: `1.0000`

### TradervR1_lab_r01_03_a_local_fair_blend

- Parent: `TradervR1_47`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `289821.0000`
- Delta vs safe baseline: `1778.5000`
- Delta vs aggressive anchor: `-23.5000`
- Composite score: `1658.7205`
- MC plausible mean delta: `462.5000`
- MC plausible p10 delta: `-3064.5000`
- MC win rate: `0.8333`

### TradervR1_lab_r01_01_a_attack_tuning

- Parent: `TradervR1_47_2`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289354.0000`
- Delta vs safe baseline: `1311.5000`
- Delta vs aggressive anchor: `-490.5000`
- Composite score: `1390.3250`

### TradervR1_lab_r01_06_p_entry_quality_p_carry_defense

- Parent: `TradervR1_47_2`
- Families: `pepper_entry_quality, pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `289356.5000`
- Delta vs safe baseline: `1314.0000`
- Delta vs aggressive anchor: `-488.0000`
- Composite score: `1358.4300`

### TradervR1_lab_r01_04_a_quality_guard

- Parent: `TradervR1_47`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289844.5000`
- Delta vs safe baseline: `1802.0000`
- Delta vs aggressive anchor: `0.0000`
- Composite score: `1253.1038`
- MC plausible mean delta: `-662.6667`
- MC plausible p10 delta: `-3409.2500`
- MC win rate: `0.8333`

## Family Weight Update

- ash_attack_tuning: mean_score=296.21 old=0.2 new=0.227
- ash_quality_guard: mean_score=1253.1 old=0.2 new=0.31
- ash_local_fair_blend: mean_score=2589.16 old=0.2 new=0.31
- pepper_entry_quality: mean_score=1358.43 old=0.2 new=0.31
- pepper_carry_defense: mean_score=1358.43 old=0.2 new=0.31

