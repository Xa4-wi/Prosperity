# Round 16 Feedback

## Top Candidates

### TradervR1_lab_r16_02_a_local_fair_blend

- Parent: `TradervR1_47_2`
- Families: `ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `288974.0000`
- Delta vs safe baseline: `931.5000`
- Delta vs aggressive anchor: `-870.5000`
- Composite score: `450.3962`
- MC plausible mean delta: `-459.3333`
- MC plausible p10 delta: `-2492.2500`
- MC win rate: `0.6667`

### TradervR1_lab_r16_06_p_entry_quality

- Parent: `TradervR1_42_O2_1`
- Families: `pepper_entry_quality`
- Strategy refs: `2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `288002.5000`
- Delta vs safe baseline: `-40.0000`
- Delta vs aggressive anchor: `-1842.0000`
- Composite score: `-54.6200`

### TradervR1_lab_r16_05_p_carry_defense

- Parent: `TradervR1_42_O2_1`
- Families: `pepper_carry_defense`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum`
- Deterministic total: `288004.5000`
- Delta vs safe baseline: `-38.0000`
- Delta vs aggressive anchor: `-1840.0000`
- Composite score: `-56.7300`

### TradervR1_lab_r16_01_p_entry_quality_a_quality_guard

- Parent: `TradervR1_42_P1_1`
- Families: `pepper_entry_quality, ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `287856.5000`
- Delta vs safe baseline: `-186.0000`
- Delta vs aggressive anchor: `-1988.0000`
- Composite score: `-216.9800`

### TradervR1_lab_r16_02_a_local_fair_blend_cmaes_ash_local_fair_blend

- Parent: `TradervR1_lab_r16_02_a_local_fair_blend`
- Families: `ash_local_fair_blend, cmaes_refine`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `288974.0000`
- Delta vs safe baseline: `931.5000`
- Delta vs aggressive anchor: `-870.5000`
- Composite score: `-221.5055`
- MC plausible mean delta: `-1250.0000`
- MC plausible p10 delta: `-5032.5000`
- MC win rate: `0.6667`

## Family Weight Update

- ash_attack_tuning: mean_score=-686.36 old=0.187 new=0.2
- ash_quality_guard: mean_score=-243.39 old=0.19 new=0.2
- ash_local_fair_blend: mean_score=-194.9 old=0.219 new=0.2
- pepper_entry_quality: mean_score=-135.8 old=0.216 new=0.203
- pepper_carry_defense: mean_score=-160.01 old=0.187 new=0.2

