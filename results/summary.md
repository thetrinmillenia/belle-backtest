# Belle backtest results

Data: Yahoo Finance, last 60d. Strike = 25 SPX points OTM.

## 5 minute signals

| Measure | Value |
| --- | --- |
| Signals | 42 (6.8 per week) |
| Reached ITM by 15:59 | 2% |
| ITM at the close | 2% |
| Average points past strike | -20.6 |
| Underlying stop hit | 60% |

| Split | Signals | Reached ITM |
| --- | --- | --- |
| window = W1 | 28 | 0% |
| window = W2 | 14 | 7% |
| direction = calls | 15 | 0% |
| direction = puts | 27 | 4% |
| failed_2 = False | 33 | 3% |
| failed_2 = True | 9 | 0% |
| smt = False | 40 | 2% |
| smt = True | 2 | 0% |
| h1 = green | 17 | 0% |
| h1 = red | 25 | 4% |
| h4 = green | 17 | 0% |
| h4 = red | 25 | 4% |

**Answer key check**

- 2026-09-30 SPX 7670p: W2 15:35 (9:30 open)
- 2026-10-01 SPX 7675p: not flagged

## 15 minute signals

| Measure | Value |
| --- | --- |
| Signals | 14 (5.8 per week) |
| Reached ITM by 15:59 | 7% |
| ITM at the close | 7% |
| Average points past strike | -13.5 |
| Underlying stop hit | 29% |

| Split | Signals | Reached ITM |
| --- | --- | --- |
| window = W1 | 9 | 11% |
| window = W2 | 5 | 0% |
| direction = calls | 6 | 0% |
| direction = puts | 8 | 12% |
| failed_2 = False | 12 | 8% |
| failed_2 = True | 2 | 0% |
| smt = False | 14 | 7% |
| h1 = green | 6 | 0% |
| h1 = red | 8 | 12% |
| h4 = green | 7 | 0% |
| h4 = red | 7 | 14% |

**Answer key check**

- 2026-09-30 SPX 7670p: not flagged
- 2026-10-01 SPX 7675p: not flagged
