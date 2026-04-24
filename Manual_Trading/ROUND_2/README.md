# Invest & Expand Optimizer

This folder contains a standalone optimizer for the Prosperity manual trading "Invest & Expand" challenge:

- paste in observed opponent `Speed` bids
- compute the exact best response
- test a weighted set of possible opponent setups
- inspect the best `Research / Scale / Speed` target before entering values in the challenge UI

The script in this repo is:

- [invest_expand_optimizer.py](Manual_Trading/ROUND_2/invest_expand_optimizer.py)

## What the script solves

For a fixed `Speed = v`, the script assumes the remaining budget is:

`B = 100 - v`

It then solves the best exact split between `Research` and `Scale` for that remaining budget.

Because `Speed` only matters through your rank, the only `Speed` values worth checking are:

- `0`
- each unique opponent `Speed` bid

So this is not a heuristic search. It checks every relevant speed threshold and solves the optimal `Research / Scale` split for each one.

## Quick start

From the repository root:

```bash
cd Manual_Trading/ROUND_2
python3 invest_expand_optimizer.py --speeds "70,70,70,50,40,40,30"
```

You can also run it without arguments and paste speeds when prompted:

```bash
cd Manual_Trading/ROUND_2
python3 invest_expand_optimizer.py
```

## Mode 1: Exact best response

Use `--speeds` when you know the other players' `Speed` bids.

Example:

```bash
python3 invest_expand_optimizer.py --speeds "70,70,70,50,40,40,30"
```

Output for that field:

```text
Best exact response:
Speed=40.00% | Research=15.1337% | Scale=44.8663% | Multiplier=0.442857 | Rank=#5 | Gross=167,616.15 | Net=117,616.15
```

So the best response is approximately:

- `Speed = 40.00%`
- `Research = 15.13%`
- `Scale = 44.87%`
- `Net PnL = 117,616`

## Mode 2: Weighted scenarios

Use `--scenarios` when you do not know the exact field, but have a small set of plausible opponent setups.

Format:

- separate scenarios with `;`
- prefix each scenario with `weight|`
- then list the opponent speeds for that scenario

Example:

```bash
python3 invest_expand_optimizer.py --scenarios "0.5|70,70,70,50,40,40,30;0.3|95,20,10;0.2|60,60,60,60"
```

The script normalizes weights automatically, computes the expected multiplier for each relevant speed threshold, and returns the best fixed strategy across those scenarios.

## Input rules

For `--speeds`:

- use percentages between `0` and `100`
- commas are the clearest separator
- spaces and semicolons are also accepted by the parser

Examples:

```bash
python3 invest_expand_optimizer.py --speeds "70,70,70,50,40,40,30"
python3 invest_expand_optimizer.py --speeds "70 70 70 50 40 40 30"
```

For `--scenarios`:

- each scenario must have a positive weight
- weights do not need to sum to `1.0`
- the script rescales them internally

## Reading the output

Each candidate row shows:

- `Speed %`: the speed threshold being tested
- `Research %`: optimal research spend for that speed
- `Scale %`: optimal scale spend for that speed
- `Mult`: the rank multiplier implied by that speed
- `Rank`: your rank when exact opponent speeds are known
- `Gross`: gross challenge payout before budget cost
- `Net`: gross payout minus budget cost

The top line is the best strategy under the chosen mode.

## Practical takeaway

If you spend `0` on `Speed`, the best pure `Research / Scale` split is about:

- `Research = 23.14%`
- `Scale = 76.86%`

In the current script, that still gives positive net PnL even at the worst speed multiplier:

- `Gross ≈ 74,233.63`
- `Net ≈ 24,233.63`

## Challenge UI note

If the UI only accepts whole percentages, use the optimizer output as the target and test nearby rounded values manually.

For the example field above, sensible integer checks would be values near:

- `Speed = 40`
- `Research = 15`
- `Scale = 45`

## Current assumptions

The checked-in script currently assumes:

- full budget is used, so `Research + Scale + Speed = 100`
- budget cost is treated as a fixed `50,000` because the optimizer always spends the full `100%`
- exact optimization is over relevant speed thresholds only, which is valid because rank only changes when crossing opponent speed levels

If you later extend the tool to manually score partial-budget mixes, update the cost term to use the prorated rule:

`50_000 * used_percent / 100`
