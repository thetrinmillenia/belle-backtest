# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-04.

## 5 minute signals

Signals: 76 (8.1 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 76 | 3 / 7 / 12 |
| window = W1 | 40 | 4 / 9 / 16 |
| window = W2 | 36 | 3 / 6 / 9 |
| direction = calls | 44 | 2 / 6 / 10 |
| direction = puts | 32 | 5 / 9 / 19 |
| W1 calls | 23 | 2 / 8 / 14 |
| W1 puts | 17 | 6 / 12 / 25 |
| W2 calls | 21 | 3 / 5 / 8 |
| W2 puts | 15 | 3 / 6 / 11 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 26% | 17% | 9% | 8% |
| W1 calls | 30% | 13% | 0% | 0% |
| W1 puts | 47% | 41% | 29% | 24% |
| W2 calls | 10% | 0% | 0% | 0% |
| W2 puts | 20% | 20% | 13% | 13% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 1 | 0% |
| pool_swept = 13:30 candle low | 5 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 12 | 42% |
| pool_swept = bearish order block opening | 5 | 20% |
| pool_swept = bullish FVG CE | 14 | 7% |
| pool_swept = bullish order block opening | 7 | 0% |
| pool_swept = equal highs | 2 | 50% |
| pool_swept = equal lows | 5 | 0% |
| pool_swept = rejection block | 19 | 16% |
| pool_swept = swing high | 1 | 0% |
| pool_swept = swing low | 1 | 100% |
| with_4h_bias = False | 28 | 14% |
| with_4h_bias = True | 48 | 19% |
| confirmed_next_candle = False | 31 | 6% |
| confirmed_next_candle = True | 45 | 24% |
| failed_2 = False | 63 | 19% |
| failed_2 = True | 13 | 8% |
| smt = False | 74 | 16% |
| smt = True | 2 | 50% |
| h1 = green | 42 | 5% |
| h1 = red | 34 | 32% |
| h4 = green | 34 | 3% |
| h4 = red | 42 | 29% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 42 (5.8 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 42 | 4 / 8 / 13 |
| window = W1 | 25 | 5 / 9 / 15 |
| window = W2 | 17 | 2 / 7 / 8 |
| direction = calls | 24 | 5 / 8 / 13 |
| direction = puts | 18 | 2 / 6 / 17 |
| W1 calls | 15 | 6 / 8 / 14 |
| W1 puts | 10 | 4 / 10 / 20 |
| W2 calls | 9 | 4 / 8 / 8 |
| W2 puts | 8 | 2 / 5 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 24% | 10% | 7% | 5% |
| W1 calls | 27% | 0% | 0% | 0% |
| W1 puts | 40% | 30% | 20% | 10% |
| W2 calls | 11% | 0% | 0% | 0% |
| W2 puts | 12% | 12% | 12% | 12% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 8 | 25% |
| pool_swept = 13:30 candle low | 9 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 6 | 33% |
| pool_swept = bearish order block opening | 2 | 0% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = midnight open | 1 | 0% |
| pool_swept = rejection block | 6 | 0% |
| pool_swept = swing low | 3 | 0% |
| with_4h_bias = False | 17 | 0% |
| with_4h_bias = True | 25 | 16% |
| confirmed_next_candle = False | 13 | 8% |
| confirmed_next_candle = True | 29 | 10% |
| failed_2 = False | 34 | 9% |
| failed_2 = True | 8 | 12% |
| smt = False | 40 | 10% |
| smt = True | 2 | 0% |
| h1 = green | 23 | 0% |
| h1 = red | 19 | 21% |
| h4 = green | 22 | 0% |
| h4 = red | 20 | 20% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
