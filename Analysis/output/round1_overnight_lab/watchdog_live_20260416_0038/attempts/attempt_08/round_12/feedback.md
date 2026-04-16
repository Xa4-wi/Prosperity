# Round 12 Feedback

## Top Candidates

### TradervR1_lab_r12_02_p_entry_quality_a_quality_guard

- Parent: `TradervR1_47`
- Families: `pepper_entry_quality, ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `289984.5000`
- Delta vs safe baseline: `1942.0000`
- Delta vs aggressive anchor: `140.0000`
- Composite score: `3029.8705`
- MC plausible mean delta: `2362.0000`
- MC plausible p10 delta: `-107.7500`
- MC win rate: `0.8333`

### TradervR1_lab_r12_02_p_entry_quality_a_quality_guard_cmaes_pepper_entry_quality

- Parent: `TradervR1_lab_r12_02_p_entry_quality_a_quality_guard`
- Families: `pepper_entry_quality, cmaes_refine`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `289984.5000`
- Delta vs safe baseline: `1942.0000`
- Delta vs aggressive anchor: `140.0000`
- Composite score: `2961.5800`
- MC plausible mean delta: `1772.0000`
- MC plausible p10 delta: `1048.5000`
- MC win rate: `1.0000`

### TradervR1_lab_r12_05_a_quality_guard

- Parent: `TradervR1_47_2`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289176.0000`
- Delta vs safe baseline: `1133.5000`
- Delta vs aggressive anchor: `-668.5000`
- Composite score: `2002.4855`
- MC plausible mean delta: `2034.2500`
- MC plausible p10 delta: `438.7500`
- MC win rate: `0.8333`

### TradervR1_lab_r12_03_p_entry_quality_a_attack_tuning

- Parent: `TradervR1_47_2`
- Families: `pepper_entry_quality, ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 2.1 Mean Reversion; 2.2 Trend Following / Momentum; 3.3 Queue-Aware Market Making`
- Deterministic total: `288906.0000`
- Delta vs safe baseline: `863.5000`
- Delta vs aggressive anchor: `-938.5000`
- Composite score: `928.3450`

### TradervR1_lab_r12_06_p_carry_defense_a_local_fair_blend

- Parent: `TradervR1_lab_r11_06_p_carry_defense_p_entry_quality`
- Families: `pepper_carry_defense, ash_local_fair_blend`
- Strategy refs: `1.1 Static Fair-Value Market Making; 1.2 Join / Improve Market Making; 1.3 Inventory-Skewed Market Making; 2.2 Trend Following / Momentum; 3.2 GLFT (Guéant-Lehalle-Fernandez-Tapia)`
- Deterministic total: `288486.0000`
- Delta vs safe baseline: `443.5000`
- Delta vs aggressive anchor: `-1358.5000`
- Composite score: `452.1100`

## Family Weight Update

- ash_attack_tuning: mean_score=155.11 old=0.207 new=0.222
- ash_quality_guard: mean_score=1507.99 old=0.18 new=0.279
- ash_local_fair_blend: mean_score=-147.21 old=0.214 new=0.2
- pepper_entry_quality: mean_score=2306.6 old=0.211 new=0.326
- pepper_carry_defense: mean_score=115.39 old=0.188 new=0.2

