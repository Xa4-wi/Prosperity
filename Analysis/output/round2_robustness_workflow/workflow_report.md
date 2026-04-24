# Round 2 Robustness Workflow

Base research file: [TradervR2_27_researchBase.py](Bots/Round2/TradervR2_27_researchBase.py)
Reference bot: [TradervR2_26.py](Bots/Round2/TradervR2_26.py)

Queue model: `conservative`
Access seeds: `7` to `9`
Robust score: `mean - 0.50 * std`

## Overall Ranking

- `TradervR2_28_fair_medianGuard`: robust `308455.8`, mean `308710.2`, p25 `308276.0`, longest plateau `116`
- `TradervR2_28_bookHealth_mild`: robust `308030.4`, mean `308118.8`, p25 `307886.5`, longest plateau `81`
- `TradervR2_28_starvation_strong`: robust `308023.0`, mean `308091.5`, p25 `307908.5`, longest plateau `81`
- `TradervR2_26`: robust `307998.5`, mean `308071.2`, p25 `307880.5`, longest plateau `37`
- `TradervR2_28_accessGate_highHealth`: robust `307996.2`, mean `308069.8`, p25 `307864.5`, longest plateau `81`
- `TradervR2_28_accessGate_highHealthHighConv`: robust `307996.2`, mean `308069.8`, p25 `307864.5`, longest plateau `81`
- `TradervR2_28_fair_anchorGuard`: robust `307989.5`, mean `308082.5`, p25 `307850.5`, longest plateau `81`
- `TradervR2_28_pepper_cheapEarly`: robust `307987.3`, mean `308055.5`, p25 `307873.5`, longest plateau `81`
- `TradervR2_28_markout_bucketedLight`: robust `307987.1`, mean `308058.2`, p25 `307864.5`, longest plateau `81`
- `TradervR2_27_researchBase`: robust `307982.3`, mean `308052.5`, p25 `307864.5`, longest plateau `81`

## `reference`

### `TradervR2_26`

- baseline no-access: `301262.0`
- access mean/std/p25: `308071.2 / 145.3 / 307880.5`
- access robust score: `307998.5`
- plateau count / longest: `44 / 37`
- plateau classes: `{'signal_neutral': 41, 'inventory_blocked': 3}`
- summary: [TradervR2_26 compare](Analysis/output/round2_robustness_workflow/TradervR2_26/compare_summary.json)

## `research_base`

### `TradervR2_27_researchBase`

- baseline no-access: `301252.0`
- access mean/std/p25: `308052.5 / 140.4 / 307864.5`
- access robust score: `307982.3`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_27_researchBase compare](Analysis/output/round2_robustness_workflow/TradervR2_27_researchBase/compare_summary.json)

## `1_book_health`

### `TradervR2_28_bookHealth_mild`

- baseline no-access: `301303.0`
- access mean/std/p25: `308118.8 / 176.8 / 307886.5`
- access robust score: `308030.4`
- plateau count / longest: `46 / 81`
- plateau classes: `{'signal_neutral': 43, 'inventory_blocked': 3}`
- summary: [TradervR2_28_bookHealth_mild compare](Analysis/output/round2_robustness_workflow/TradervR2_28_bookHealth_mild/compare_summary.json)

### `TradervR2_28_bookHealth_strong`

- baseline no-access: `301252.0`
- access mean/std/p25: `308052.5 / 140.4 / 307864.5`
- access robust score: `307982.3`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_bookHealth_strong compare](Analysis/output/round2_robustness_workflow/TradervR2_28_bookHealth_strong/compare_summary.json)

## `2_fair_robustness`

### `TradervR2_28_fair_medianGuard`

- baseline no-access: `300276.0`
- access mean/std/p25: `308710.2 / 508.7 / 308276.0`
- access robust score: `308455.8`
- plateau count / longest: `42 / 116`
- plateau classes: `{'signal_neutral': 41, 'inventory_blocked': 1}`
- summary: [TradervR2_28_fair_medianGuard compare](Analysis/output/round2_robustness_workflow/TradervR2_28_fair_medianGuard/compare_summary.json)

### `TradervR2_28_fair_anchorGuard`

- baseline no-access: `301242.0`
- access mean/std/p25: `308082.5 / 186.1 / 307850.5`
- access robust score: `307989.5`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_fair_anchorGuard compare](Analysis/output/round2_robustness_workflow/TradervR2_28_fair_anchorGuard/compare_summary.json)

### `TradervR2_28_fair_thinTopIgnore`

- baseline no-access: `301148.0`
- access mean/std/p25: `307909.3 / 162.3 / 307717.0`
- access robust score: `307828.2`
- plateau count / longest: `36 / 44`
- plateau classes: `{'signal_neutral': 35, 'inventory_blocked': 1}`
- summary: [TradervR2_28_fair_thinTopIgnore compare](Analysis/output/round2_robustness_workflow/TradervR2_28_fair_thinTopIgnore/compare_summary.json)

## `3_vacuum_recovery`

### `TradervR2_28_vacuumRecovery_cooldown`

- baseline no-access: `301252.0`
- access mean/std/p25: `308052.5 / 140.4 / 307864.5`
- access robust score: `307982.3`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_vacuumRecovery_cooldown compare](Analysis/output/round2_robustness_workflow/TradervR2_28_vacuumRecovery_cooldown/compare_summary.json)

### `TradervR2_28_vacuumRecovery_stableBars`

- baseline no-access: `301252.0`
- access mean/std/p25: `308052.5 / 140.4 / 307864.5`
- access robust score: `307982.3`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_vacuumRecovery_stableBars compare](Analysis/output/round2_robustness_workflow/TradervR2_28_vacuumRecovery_stableBars/compare_summary.json)

## `4_side_starvation`

### `TradervR2_28_starvation_strong`

- baseline no-access: `301256.0`
- access mean/std/p25: `308091.5 / 137.0 / 307908.5`
- access robust score: `308023.0`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_starvation_strong compare](Analysis/output/round2_robustness_workflow/TradervR2_28_starvation_strong/compare_summary.json)

### `TradervR2_28_starvation_priority`

- baseline no-access: `301252.0`
- access mean/std/p25: `308057.5 / 168.6 / 307829.5`
- access robust score: `307973.2`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_starvation_priority compare](Analysis/output/round2_robustness_workflow/TradervR2_28_starvation_priority/compare_summary.json)

## `5_markout_passive`

### `TradervR2_28_markout_bucketedLight`

- baseline no-access: `301252.0`
- access mean/std/p25: `308058.2 / 142.2 / 307864.5`
- access robust score: `307987.1`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_markout_bucketedLight compare](Analysis/output/round2_robustness_workflow/TradervR2_28_markout_bucketedLight/compare_summary.json)

### `TradervR2_28_markout_bucketedStrong`

- baseline no-access: `301231.0`
- access mean/std/p25: `308002.2 / 138.6 / 307806.5`
- access robust score: `307932.9`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_markout_bucketedStrong compare](Analysis/output/round2_robustness_workflow/TradervR2_28_markout_bucketedStrong/compare_summary.json)

## `6_terminal_risk`

### `TradervR2_28_terminalRisk_soft`

- baseline no-access: `301252.0`
- access mean/std/p25: `308052.5 / 140.4 / 307864.5`
- access robust score: `307982.3`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_terminalRisk_soft compare](Analysis/output/round2_robustness_workflow/TradervR2_28_terminalRisk_soft/compare_summary.json)

### `TradervR2_28_terminalRisk_asymmetric`

- baseline no-access: `301261.0`
- access mean/std/p25: `308052.5 / 140.4 / 307864.5`
- access robust score: `307982.3`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_terminalRisk_asymmetric compare](Analysis/output/round2_robustness_workflow/TradervR2_28_terminalRisk_asymmetric/compare_summary.json)

## `7_access_safe`

### `TradervR2_28_accessGate_highHealth`

- baseline no-access: `301252.0`
- access mean/std/p25: `308069.8 / 147.2 / 307864.5`
- access robust score: `307996.2`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_accessGate_highHealth compare](Analysis/output/round2_robustness_workflow/TradervR2_28_accessGate_highHealth/compare_summary.json)

### `TradervR2_28_accessGate_highHealthHighConv`

- baseline no-access: `301252.0`
- access mean/std/p25: `308069.8 / 147.2 / 307864.5`
- access robust score: `307996.2`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_accessGate_highHealthHighConv compare](Analysis/output/round2_robustness_workflow/TradervR2_28_accessGate_highHealthHighConv/compare_summary.json)

## `10_pepper_robustness`

### `TradervR2_28_pepper_cheapEarly`

- baseline no-access: `301252.0`
- access mean/std/p25: `308055.5 / 136.4 / 307873.5`
- access robust score: `307987.3`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_pepper_cheapEarly compare](Analysis/output/round2_robustness_workflow/TradervR2_28_pepper_cheapEarly/compare_summary.json)

### `TradervR2_28_pepper_lateTrim`

- baseline no-access: `301252.0`
- access mean/std/p25: `308052.5 / 140.4 / 307864.5`
- access robust score: `307982.3`
- plateau count / longest: `47 / 81`
- plateau classes: `{'signal_neutral': 44, 'inventory_blocked': 3}`
- summary: [TradervR2_28_pepper_lateTrim compare](Analysis/output/round2_robustness_workflow/TradervR2_28_pepper_lateTrim/compare_summary.json)

## Plateau Classification Heuristic

The plateau labels are heuristic and come from `no_access/product_steps.csv` on Ash:
- `market_dry`: wide-ish, toxic, low-opportunity windows
- `self_throttled`: book looked tradable but the bot stayed too quiet
- `inventory_blocked`: position was already stretched
- `signal_neutral`: no strong directional edge
- `stale_toxicity`: toxic memory likely outlived the raw state

