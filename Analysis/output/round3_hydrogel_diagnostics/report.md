# Round 3 Hydrogel Diagnostics

Source log: [TradervR3_16.log](Bots/Round3/TradervR3_16.log)

This report follows the Hydrogel build-order manual:

```text
Measure -> classify -> tune risk shape -> tune execution -> only then redesign fair/model
```

## Headline Read

- Final PnL: `-612.375`
- Min / max PnL: `-9564.25 / 6805.25`
- Final position: `200`
- Max |position|: `200`
- Time with `|pos| >= 150`: `75500`
- Time with `|pos| >= 200`: `69600`

- Classification note: Hydrogel still behaves like an anchored local-fair inventory trader, not a drift product.
- Main risk note: The worst hidden-data behavior is same-side accumulation while already stretched and then carrying near-full inventory too late into the session.
- Execution note: Same-side fills while stretched have strongly negative 20-bar markout, which argues for earlier same-side blocking, harder late-session clearing, and smaller stretched quote size before any fair rewrite.

## Inventory Bucket PnL

- `|pos| < 50`: pnl `-1413.09375`, time `2300.0`
- `50 <= |pos| < 120`: pnl `-1209.78125`, time `20500.0`
- `|pos| >= 120`: pnl `2010.5`, time `77100.0`

## Session Quarter Stats

- `0-25%`: pnl delta `4375.625`, avg |pos| `184.20`, max |pos| `200`, start `0`, end `-180`
- `25-50%`: pnl delta `-6332.875`, avg |pos| `87.27`, max |pos| `200`, start `-180`, end `200`
- `50-75%`: pnl delta `5382.875`, avg |pos| `199.83`, max |pos| `200`, start `200`, end `200`
- `75-100%`: pnl delta `-4173.5`, avg |pos| `199.97`, max |pos| `200`, start `200`, end `200`

## First-Hit Markouts

- `|pos| >= 150`: episodes `2`, long count `1`, short count `1`, long 20-bar markout `-17.0`, short 20-bar markout `0.0`
- `|pos| >= 180`: episodes `2`, long count `1`, short count `1`, long 20-bar markout `-12.0`, short 20-bar markout `0.0`
- `|pos| >= 200`: episodes `11`, long count `9`, short count `2`, long 20-bar markout `-1.3333333333333333`, short 20-bar markout `-12.0`

## Same-Side Fill Quality While Stretched

- threshold `120`: buy fills `13`, buy 20-bar markout `-13.115384615384615`, sell fills `7`, sell 20-bar markout `-5.285714285714286`
- threshold `150`: buy fills `11`, buy 20-bar markout `-10.954545454545455`, sell fills `5`, sell 20-bar markout `-3.0`

## Phase B / C Implications

- Keep the current fair family for now. The measurement still looks like anchored local-fair MM.
- Tighten same-side blocking earlier, because stretched same-side fills are adverse on hidden data.
- Shrink late-session Hydrogel exposure harder. The bot is still carrying near-full inventory too late.
- Make clear behavior more proactive before `|pos|` reaches the worst tail, especially during sign-flip episodes.
