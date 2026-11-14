# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-13.

## 5 minute signals

Signals: 74 (8.0 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 74 | 3 / 7 / 14 |
| window = W1 | 40 | 4 / 8 / 20 |
| window = W2 | 34 | 2 / 7 / 10 |
| direction = calls | 38 | 3 / 6 / 10 |
| direction = puts | 36 | 4 / 9 / 20 |
| W1 calls | 21 | 2 / 8 / 16 |
| W1 puts | 19 | 6 / 7 / 33 |
| W2 calls | 17 | 3 / 4 / 8 |
| W2 puts | 17 | 2 / 9 / 14 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 30% | 22% | 14% | 11% |
| W1 calls | 29% | 19% | 5% | 0% |
| W1 puts | 47% | 42% | 37% | 32% |
| W2 calls | 12% | 0% | 0% | 0% |
| W2 puts | 29% | 24% | 12% | 12% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 1 | 0% |
| pool_swept = 13:30 candle low | 6 | 17% |
| pool_swept = 9:30 open | 3 | 33% |
| pool_swept = bearish FVG CE | 13 | 38% |
| pool_swept = bearish order block opening | 6 | 17% |
| pool_swept = bullish FVG CE | 10 | 20% |
| pool_swept = bullish order block opening | 7 | 0% |
| pool_swept = equal highs | 1 | 100% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 21 | 19% |
| pool_swept = swing high | 2 | 50% |
| with_4h_bias = False | 31 | 16% |
| with_4h_bias = True | 43 | 26% |
| confirmed_next_candle = False | 28 | 14% |
| confirmed_next_candle = True | 46 | 26% |
| failed_2 = False | 62 | 21% |
| failed_2 = True | 12 | 25% |
| smt = False | 72 | 21% |
| smt = True | 2 | 50% |
| h1 = green | 36 | 14% |
| h1 = red | 38 | 29% |
| h4 = green | 31 | 13% |
| h4 = red | 43 | 28% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 44 (5.9 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 44 | 5 / 8 / 13 |
| window = W1 | 27 | 5 / 8 / 14 |
| window = W2 | 17 | 5 / 7 / 9 |
| direction = calls | 23 | 6 / 8 / 12 |
| direction = puts | 21 | 4 / 7 / 21 |
| W1 calls | 15 | 6 / 8 / 13 |
| W1 puts | 12 | 5 / 9 / 22 |
| W2 calls | 8 | 8 / 8 / 10 |
| W2 puts | 9 | 2 / 6 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 25% | 14% | 11% | 7% |
| W1 calls | 20% | 0% | 0% | 0% |
| W1 puts | 42% | 33% | 25% | 8% |
| W2 calls | 12% | 0% | 0% | 0% |
| W2 puts | 22% | 22% | 22% | 22% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 10 | 30% |
| pool_swept = 13:30 candle low | 10 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 5 | 40% |
| pool_swept = bearish order block opening | 3 | 33% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = rejection block | 6 | 0% |
| pool_swept = swing high | 1 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 17 | 0% |
| with_4h_bias = True | 27 | 22% |
| confirmed_next_candle = False | 15 | 13% |
| confirmed_next_candle = True | 29 | 14% |
| failed_2 = False | 33 | 12% |
| failed_2 = True | 11 | 18% |
| smt = False | 41 | 15% |
| smt = True | 3 | 0% |
| h1 = green | 22 | 0% |
| h1 = red | 22 | 27% |
| h4 = green | 22 | 0% |
| h4 = red | 22 | 27% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
