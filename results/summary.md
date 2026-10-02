# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-01.

## 5 minute signals

Signals: 92 (10.2 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 92 | 2 / 5 / 10 |
| window = W1 | 54 | 3 / 8 / 13 |
| window = W2 | 38 | 1 / 3 / 5 |
| direction = calls | 49 | 1 / 4 / 9 |
| direction = puts | 43 | 3 / 6 / 11 |
| W1 calls | 27 | 4 / 8 / 12 |
| W1 puts | 27 | 3 / 9 / 15 |
| W2 calls | 22 | 1 / 2 / 3 |
| W2 puts | 16 | 4 / 6 / 8 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 18% | 9% | 4% | 2% |
| W1 calls | 26% | 7% | 0% | 0% |
| W1 puts | 30% | 22% | 15% | 7% |
| W2 calls | 0% | 0% | 0% | 0% |
| W2 puts | 12% | 0% | 0% | 0% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| cisd_followed = False | 55 | 11% |
| cisd_followed = True | 37 | 5% |
| failed_2 = False | 74 | 8% |
| failed_2 = True | 18 | 11% |
| smt = False | 83 | 10% |
| smt = True | 9 | 0% |
| h1 = green | 36 | 14% |
| h1 = red | 56 | 5% |
| h4 = green | 43 | 12% |
| h4 = red | 49 | 6% |

**Answer key check**

- 2026-09-30 SPX 7670p: not flagged
- 2026-10-01 SPX 7675p: W1 entry 14:45 after sweeping 9:30 open, moved 9.06 pts, W2 entry 15:45 after sweeping swing high, moved 11.93 pts

## 15 minute signals

Signals: 45 (6.8 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 45 | 5 / 8 / 13 |
| window = W1 | 36 | 5 / 9 / 14 |
| window = W2 | 9 | 6 / 7 / 8 |
| direction = calls | 20 | 3 / 8 / 13 |
| direction = puts | 25 | 6 / 8 / 13 |
| W1 calls | 17 | 3 / 8 / 13 |
| W1 puts | 19 | 6 / 9 / 15 |
| W2 calls | 3 | 5 / 7 / 8 |
| W2 puts | 6 | 6 / 7 / 8 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 27% | 16% | 9% | 4% |
| W1 calls | 35% | 18% | 6% | 0% |
| W1 puts | 32% | 21% | 16% | 11% |
| W2 calls | 0% | 0% | 0% | 0% |
| W2 puts | 0% | 0% | 0% | 0% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| cisd_followed = False | 27 | 15% |
| cisd_followed = True | 18 | 17% |
| failed_2 = False | 38 | 18% |
| failed_2 = True | 7 | 0% |
| smt = False | 41 | 17% |
| smt = True | 4 | 0% |
| h1 = green | 19 | 16% |
| h1 = red | 26 | 15% |
| h4 = green | 22 | 14% |
| h4 = red | 23 | 17% |

**Answer key check**

- 2026-09-30 SPX 7670p: not flagged
- 2026-10-01 SPX 7675p: W1 entry 14:45 after sweeping 9:30 open, moved 9.06 pts
