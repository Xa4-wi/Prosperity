# Round 17 Feedback

## Top Candidates

### TradervR1_lab_r17_05_a_local_fair_blend

- Parent: `TradervR1_lab_r16_04_a_local_fair_blend`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `288857.5000`
- Delta vs safe baseline: `815.0000`
- Delta vs aggressive anchor: `-987.0000`
- Composite score: `844.4900`

### TradervR1_lab_r17_02_a_local_fair_blend_a_quality_guard

- Parent: `TradervR1_42_P1_1`
- Families: `ash_local_fair_blend, ash_quality_guard`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia); 3.3 Queue-Aware Market Making`
- Deterministic total: `288105.0000`
- Delta vs safe baseline: `62.5000`
- Delta vs aggressive anchor: `-1739.5000`
- Composite score: `2.4950`

### TradervR1_lab_r17_01_a_attack_tuning

- Parent: `TradervR1_39_4`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `287771.5000`
- Delta vs safe baseline: `-271.0000`
- Delta vs aggressive anchor: `-2073.0000`
- Composite score: `-342.2900`

### TradervR1_lab_r17_08_a_attack_tuning_p_entry_quality_p_carry_defense

- Parent: `TradervR1_34_1`
- Families: `ash_attack_tuning, pepper_entry_quality, pepper_carry_defense`
- Strategy refs: `1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 1.4 Spread-Capture Only MM; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `287631.0000`
- Delta vs safe baseline: `-411.5000`
- Delta vs aggressive anchor: `-2213.5000`
- Composite score: `-473.7550`

### TradervR1_lab_r17_06_a_quality_guard

- Parent: `TradervR1_lab_r16_07_p_carry_defense`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289836.5000`
- Delta vs safe baseline: `1794.0000`
- Delta vs aggressive anchor: `-8.0000`
- Composite score: `-657.0583`
- MC plausible mean delta: `-3487.3333`
- MC plausible p10 delta: `-8716.7500`
- MC win rate: `0.0000`

## Family Weight Update

- ash_attack_tuning: mean_score=-574.91 old=0.185 new=0.2
- ash_quality_guard: mean_score=-327.28 old=0.203 new=0.2
- ash_local_fair_blend: mean_score=423.49 old=0.185 new=0.221
- pepper_entry_quality: mean_score=-741.55 old=0.185 new=0.2
- pepper_carry_defense: mean_score=-587.37 old=0.241 new=0.2

