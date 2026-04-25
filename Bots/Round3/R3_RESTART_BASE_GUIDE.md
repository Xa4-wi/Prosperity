# Round 3 Restart Base Guide

This is the clean restart scaffold for Round 3 research.

Main file:
- `Bots/Round3/TradervR3_55_structuralBase.py`

Why this exists:
- the old branch family accumulated too many interacting ideas
- Hydrogel, Velvet, and the voucher strip need clearer boundaries
- we want a base where one new competition-intel idea can be tested at a time

What is intentionally simple:
- Hydrogel uses a frozen anchor/stable/micro baseline
- Velvet is hedge-first with a small alpha overlay
- vouchers use a clean side-surface + hybrid-IV + pair-first baseline

What to test from here, one layer at a time:
1. Hydrogel classification change
2. Velvet fair-family change
3. voucher quote cleaning refinement
4. voucher surface model upgrade
5. pair ranking logic
6. shock mode trigger
7. hedge deadband / hedge ratio

Working rule:
- if a new idea changes more than one engine, split it first

Recommended branch flow:
- `structuralBase -> one new idea -> one log -> compare -> keep or revert`

Useful internal diagnostics already exposed:
- Hydrogel fair / signal / target
- Velvet hedge ratio / hedge target / alpha target
- voucher smile stability
- voucher average absolute residual
- voucher pair candidates
- voucher pair targets

This file is not meant to be the strongest live bot immediately.
It is meant to be the cleanest place to restart idea generation.
