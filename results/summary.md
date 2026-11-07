# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-06.

## 5 minute signals

Signals: 78 (8.3 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 78 | 3 / 7 / 12 |
| window = W1 | 41 | 3 / 8 / 20 |
| window = W2 | 37 | 2 / 6 / 9 |
| direction = calls | 42 | 2 / 6 / 9 |
| direction = puts | 36 | 4 / 8 / 22 |
| W1 calls | 22 | 2 / 8 / 12 |
| W1 puts | 19 | 6 / 12 / 33 |
| W2 calls | 20 | 3 / 5 / 8 |
| W2 puts | 17 | 2 / 6 / 11 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 28% | 21% | 12% | 10% |
| W1 calls | 27% | 14% | 0% | 0% |
| W1 puts | 53% | 47% | 37% | 32% |
| W2 calls | 10% | 0% | 0% | 0% |
| W2 puts | 24% | 24% | 12% | 12% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 1 | 0% |
| pool_swept = 13:30 candle low | 6 | 17% |
| pool_swept = 9:30 open | 3 | 33% |
| pool_swept = bearish FVG CE | 14 | 43% |
| pool_swept = bearish order block opening | 6 | 17% |
| pool_swept = bullish FVG CE | 14 | 7% |
| pool_swept = bullish order block opening | 6 | 0% |
| pool_swept = equal highs | 2 | 50% |
| pool_swept = equal lows | 5 | 0% |
| pool_swept = rejection block | 19 | 21% |
| pool_swept = swing high | 2 | 50% |
| with_4h_bias = False | 30 | 17% |
| with_4h_bias = True | 48 | 23% |
| confirmed_next_candle = False | 30 | 13% |
| confirmed_next_candle = True | 48 | 25% |
| failed_2 = False | 65 | 20% |
| failed_2 = True | 13 | 23% |
| smt = False | 76 | 20% |
| smt = True | 2 | 50% |
| h1 = green | 40 | 10% |
| h1 = red | 38 | 32% |
| h4 = green | 34 | 9% |
| h4 = red | 44 | 30% |

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
| window = W1 | 25 | 5 / 8 / 15 |
| window = W2 | 19 | 3 / 7 / 10 |
| direction = calls | 24 | 6 / 8 / 13 |
| direction = puts | 20 | 2 / 6 / 22 |
| W1 calls | 14 | 6 / 8 / 13 |
| W1 puts | 11 | 3 / 6 / 23 |
| W2 calls | 10 | 7 / 8 / 10 |
| W2 puts | 9 | 2 / 5 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 27% | 14% | 11% | 7% |
| W1 calls | 21% | 0% | 0% | 0% |
| W1 puts | 45% | 36% | 27% | 9% |
| W2 calls | 20% | 0% | 0% | 0% |
| W2 puts | 22% | 22% | 22% | 22% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 33% |
| pool_swept = 13:30 candle low | 9 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 6 | 33% |
| pool_swept = bearish order block opening | 3 | 33% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = bullish order block opening | 1 | 0% |
| pool_swept = rejection block | 7 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 18 | 0% |
| with_4h_bias = True | 26 | 23% |
| confirmed_next_candle = False | 12 | 17% |
| confirmed_next_candle = True | 32 | 12% |
| failed_2 = False | 35 | 11% |
| failed_2 = True | 9 | 22% |
| smt = False | 42 | 14% |
| smt = True | 2 | 0% |
| h1 = green | 23 | 0% |
| h1 = red | 21 | 29% |
| h4 = green | 23 | 0% |
| h4 = red | 21 | 29% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
