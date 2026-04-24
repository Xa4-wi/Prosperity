# R3_42 VEV + Voucher Build Plan

This branch keeps the `R3_28` Hydrogel engine unchanged and moves the main research onto the connected `VELVETFRUIT_EXTRACT + voucher strip` system.

## What `R3_42` Implements

1. `VELVETFRUIT_EXTRACT` is split into a hedge book and a small alpha book.
2. The voucher strip is treated as one portfolio instead of 10 disconnected products.
3. Weighted BS / smile fitting from `R3_28` stays as the fair anchor.
4. Voucher trading is pair-first, outright second.
5. A broad strip-dislocation mode lowers entry friction without removing strip limits.
6. The VEV hedge has a deadband and dynamic hedge ratio.
7. Hedge decay is added after residual compression.
8. Voucher exits are driven more by residual normalization and zero-crossing.
9. Strip diagnostics are logged into `traderData`.
10. Hydrogel is intentionally frozen so the new research is attributable.

## Main Structural Changes

### Velvet

- `hedge_target` comes from strip delta.
- `alpha_target` is only allowed when strip delta is modest and the VEV book is healthy.
- `final_target = hedge_target + alpha_target`, hard-clamped inside VEV limits.

### Voucher Strip

- `pair_targets` are built from neighboring IV-residual gaps.
- `neighbor_confirm` tracks whether a strike is supported by nearby distortions.
- outright targets are only allowed for extreme residuals with confirmation.
- middle strikes keep tighter caps than wings.

### Broad Dislocation Mode

Triggers when:

- average absolute residual is large,
- neighboring strikes broadly agree,
- strip delta is still under control,
- middle-strike concentration is not already overloaded.

When active:

- voucher `take_edge` is lowered slightly,
- `take_max` is raised slightly,
- pair-first signals matter more.

## Diagnostics Logged

`strip_monitor` now includes:

- `avg_abs_resid`
- `pair_agreement_count`
- `broad_dislocation`
- `hedge_ratio`
- `target_velvet_hedge_pos`
- `target_velvet_pos`
- `velvet_alpha_target`
- `cheapest_strikes`
- `richest_strikes`
- middle-cluster concentration metrics

`voucher_targets` now includes per strike:

- `pair_target`
- `pair_bias`
- `neighbor_confirm`
- `iv_residual`
- `delta`

## Research Goal

The goal of `R3_42` is not “final best bot”.

The goal is to answer:

- Does hedge-first VEV improve strip stability?
- Are pair-first voucher trades more robust than outright option trades?
- Do broad strip dislocations unlock useful extra alpha without reopening the `5100-5500` blow-up pocket?
