# Round 4 Feedback

## Top Candidates

### TradervR1_lab_r04_01_a_local_fair_blend

- Parent: `TradervR1_lab_r03_08_a_attack_tuning_a_quality_guard_p_entry_quality`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `292738.0000`
- Delta vs safe baseline: `4695.5000`
- Delta vs aggressive anchor: `2893.5000`
- Composite score: `7789.1167`
- MC plausible mean delta: `5063.4167`
- MC plausible p10 delta: `4296.7500`
- MC win rate: `1.0000`

### TradervR1_lab_r04_01_a_local_fair_blend_cmaes_ash_local_fair_blend

- Parent: `TradervR1_lab_r04_01_a_local_fair_blend`
- Families: `ash_local_fair_blend, cmaes_refine`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `292738.0000`
- Delta vs safe baseline: `4695.5000`
- Delta vs aggressive anchor: `2893.5000`
- Composite score: `6376.2955`
- MC plausible mean delta: `3130.7500`
- MC plausible p10 delta: `-231.2500`
- MC win rate: `0.8333`

### TradervR1_lab_r04_06_a_attack_tuning

- Parent: `TradervR1_lab_r03_04_a_attack_tuning_a_quality_guard_p_entry_quality`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `288842.0000`
- Delta vs safe baseline: `799.5000`
- Delta vs aggressive anchor: `-1002.5000`
- Composite score: `819.0050`

### TradervR1_lab_r04_03_p_carry_defense_p_entry_quality_a_local_fair_blend

- Parent: `TradervR1_42_P1_1`
- Families: `pepper_carry_defense, pepper_entry_quality, ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `287975.0000`
- Delta vs safe baseline: `-67.5000`
- Delta vs aggressive anchor: `-1869.5000`
- Composite score: `-113.6300`

### TradervR1_lab_r04_04_a_quality_guard_a_attack_tuning

- Parent: `TradervR1_42_O2_1`
- Families: `ash_quality_guard, ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `287975.5000`
- Delta vs safe baseline: `-67.0000`
- Delta vs aggressive anchor: `-1869.0000`
- Composite score: `-145.4700`

## Family Weight Update

- ash_attack_tuning: mean_score=-467.23 old=0.215 new=0.2
- ash_quality_guard: mean_score=-311.57 old=0.242 new=0.207
- ash_local_fair_blend: mean_score=3413.86 old=0.174 new=0.27
- pepper_entry_quality: mean_score=-113.63 old=0.195 new=0.2
- pepper_carry_defense: mean_score=-113.63 old=0.174 new=0.2

