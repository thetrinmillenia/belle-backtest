# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-16.

## 5 minute signals

Signals: 71 (7.7 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 71 | 4 / 7 / 14 |
| window = W1 | 38 | 5 / 8 / 17 |
| window = W2 | 33 | 3 / 6 / 10 |
| direction = calls | 37 | 3 / 6 / 10 |
| direction = puts | 34 | 5 / 9 / 23 |
| W1 calls | 20 | 4 / 8 / 16 |
| W1 puts | 18 | 6 / 9 / 33 |
| W2 calls | 17 | 3 / 4 / 8 |
| W2 puts | 16 | 4 / 9 / 12 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 30% | 20% | 14% | 11% |
| W1 calls | 30% | 15% | 5% | 0% |
| W1 puts | 50% | 44% | 39% | 33% |
| W2 calls | 12% | 0% | 0% | 0% |
| W2 puts | 25% | 19% | 12% | 12% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 1 | 0% |
| pool_swept = 13:30 candle low | 5 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 13 | 38% |
| pool_swept = bearish order block opening | 4 | 0% |
| pool_swept = bullish FVG CE | 10 | 20% |
| pool_swept = bullish order block opening | 7 | 0% |
| pool_swept = equal highs | 1 | 100% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 20 | 20% |
| pool_swept = swing high | 2 | 50% |
| with_4h_bias = False | 28 | 11% |
| with_4h_bias = True | 43 | 26% |
| confirmed_next_candle = False | 28 | 11% |
| confirmed_next_candle = True | 43 | 26% |
| failed_2 = False | 59 | 20% |
| failed_2 = True | 12 | 17% |
| smt = False | 69 | 19% |
| smt = True | 2 | 50% |
| h1 = green | 35 | 9% |
| h1 = red | 36 | 31% |
| h4 = green | 30 | 10% |
| h4 = red | 41 | 27% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 42 (5.7 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 42 | 5 / 8 / 14 |
| window = W1 | 27 | 6 / 8 / 15 |
| window = W2 | 15 | 3 / 7 / 8 |
| direction = calls | 21 | 6 / 8 / 13 |
| direction = puts | 21 | 5 / 7 / 25 |
| W1 calls | 15 | 6 / 8 / 13 |
| W1 puts | 12 | 6 / 15 / 25 |
| W2 calls | 6 | 7 / 8 / 8 |
| W2 puts | 9 | 2 / 6 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 29% | 17% | 14% | 7% |
| W1 calls | 20% | 0% | 0% | 0% |
| W1 puts | 50% | 42% | 33% | 8% |
| W2 calls | 17% | 0% | 0% | 0% |
| W2 puts | 22% | 22% | 22% | 22% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 33% |
| pool_swept = 13:30 candle low | 9 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 6 | 50% |
| pool_swept = bearish order block opening | 3 | 33% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = rejection block | 5 | 0% |
| pool_swept = swing high | 1 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 15 | 0% |
| with_4h_bias = True | 27 | 26% |
| confirmed_next_candle = False | 15 | 20% |
| confirmed_next_candle = True | 27 | 15% |
| failed_2 = False | 32 | 16% |
| failed_2 = True | 10 | 20% |
| smt = False | 39 | 18% |
| smt = True | 3 | 0% |
| h1 = green | 20 | 0% |
| h1 = red | 22 | 32% |
| h4 = green | 20 | 0% |
| h4 = red | 22 | 32% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
