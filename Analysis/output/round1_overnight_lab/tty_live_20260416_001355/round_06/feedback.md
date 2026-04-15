# Round 6 Feedback

## Top Candidates

### TradervR1_lab_r06_03_a_quality_guard

- Parent: `TradervR1_lab_r05_04_p_carry_defense_p_entry_quality`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289808.5000`
- Delta vs safe baseline: `1766.0000`
- Delta vs aggressive anchor: `-36.0000`
- Composite score: `3068.4788`
- MC plausible mean delta: `2395.8333`
- MC plausible p10 delta: `1119.0000`
- MC win rate: `0.8333`

### TradervR1_lab_r06_08_a_quality_guard

- Parent: `TradervR1_lab_r05_08_a_quality_guard`
- Families: `ash_quality_guard`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289815.5000`
- Delta vs safe baseline: `1773.0000`
- Delta vs aggressive anchor: `-29.0000`
- Composite score: `2089.5445`
- MC plausible mean delta: `386.5000`
- MC plausible p10 delta: `-183.5000`
- MC win rate: `0.6667`

### TradervR1_lab_r06_05_p_entry_quality

- Parent: `TradervR1_lab_r05_04_p_carry_defense_p_entry_quality`
- Families: `pepper_entry_quality`
- Strategy refs: `2.1 Mean Reversion; 2.2 Trend Following / Momentum`
- Deterministic total: `289805.5000`
- Delta vs safe baseline: `1763.0000`
- Delta vs aggressive anchor: `-39.0000`
- Composite score: `1924.4400`

### TradervR1_lab_r06_03_a_quality_guard_cmaes_ash_quality_guard

- Parent: `TradervR1_lab_r06_03_a_quality_guard`
- Families: `ash_quality_guard, cmaes_refine`
- Strategy refs: `1.3 Inventory-Skewed Market Making; 3.3 Queue-Aware Market Making`
- Deterministic total: `289808.5000`
- Delta vs safe baseline: `1766.0000`
- Delta vs aggressive anchor: `-36.0000`
- Composite score: `1840.8045`
- MC plausible mean delta: `787.2500`
- MC plausible p10 delta: `-3012.5000`
- MC win rate: `0.6667`

### TradervR1_lab_r06_04_a_attack_tuning

- Parent: `TradervR1_47_2`
- Families: `ash_attack_tuning`
- Strategy refs: `1.2 Join / Improve Market Making; 1.4 Spread-Capture Only MM; 3.3 Queue-Aware Market Making`
- Deterministic total: `289354.0000`
- Delta vs safe baseline: `1311.5000`
- Delta vs aggressive anchor: `-490.5000`
- Composite score: `1390.3250`

## Family Weight Update

- ash_attack_tuning: mean_score=1390.33 old=0.144 new=0.224
- ash_quality_guard: mean_score=1697.43 old=0.27 new=0.418
- ash_local_fair_blend: mean_score=1350.24 old=0.144 new=0.224
- pepper_entry_quality: mean_score=962.22 old=0.28 new=0.403
- pepper_carry_defense: mean_score=677.38 old=0.162 new=0.211

