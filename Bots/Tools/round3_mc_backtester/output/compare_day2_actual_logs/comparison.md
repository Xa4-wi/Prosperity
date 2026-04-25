# Day 2 Monte Carlo vs Official Logs

This compares the custom Round 3 Monte Carlo backtester against uploaded official day-2 logs.

| Bot | Config | MC Mean | MC Median | MC P05 | MC P95 | Official | Official - MC Mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TradervR3_28 | 6 sims, tick_step 10 | -3821.58 | 5864.00 | -25422.50 | 6132.00 | 10577.38 | 14398.96 |
| TradervR3_37 | 6 sims, tick_step 10 | -20545.50 | -21643.75 | -25598.50 | -16980.00 | -27804.62 | -7259.12 |
| TradervR3_40 | 6 sims, tick_step 10 | -19509.42 | -18431.75 | -23787.00 | -17473.50 | -54943.25 | -35433.83 |
| TradervR3_42 | 4 sims, tick_step 20 | 5320.25 | 5434.00 | -179.00 | 6017.00 | 9167.50 | 3847.25 |
| TradervR3_43 | 4 sims, tick_step 20 | 13721.50 | 14127.00 | 1559.00 | 17261.00 | 11949.48 | -1772.02 |
| TradervR3_44 | 4 sims, tick_step 20 | 14525.25 | 14606.00 | 10824.50 | 15298.50 | 11653.68 | -2871.57 |
| TradervR3_45 | 2 sims, tick_step 40 | 36775.25 | 36775.25 | 34086.50 | 34086.50 | 12019.68 | -24755.57 |
