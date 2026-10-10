# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-09.

## 5 minute signals

Signals: 82 (8.9 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 82 | 2 / 7 / 10 |
| window = W1 | 43 | 3 / 8 / 14 |
| window = W2 | 39 | 2 / 6 / 9 |
| direction = calls | 40 | 1 / 7 / 9 |
| direction = puts | 42 | 4 / 7 / 15 |
| W1 calls | 22 | 3 / 8 / 11 |
| W1 puts | 21 | 4 / 9 / 17 |
| W2 calls | 18 | 0 / 3 / 7 |
| W2 puts | 21 | 3 / 7 / 10 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 21% | 12% | 4% | 4% |
| W1 calls | 23% | 5% | 0% | 0% |
| W1 puts | 38% | 29% | 10% | 10% |
| W2 calls | 6% | 0% | 0% | 0% |
| W2 puts | 14% | 14% | 5% | 5% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 3 | 0% |
| pool_swept = 13:30 candle low | 3 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 15 | 20% |
| pool_swept = bearish order block opening | 6 | 33% |
| pool_swept = bullish FVG CE | 16 | 6% |
| pool_swept = bullish order block opening | 4 | 0% |
| pool_swept = equal highs | 4 | 75% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 17 | 0% |
| pool_swept = swing high | 3 | 0% |
| pool_swept = swing low | 3 | 0% |
| with_4h_bias = False | 30 | 7% |
| with_4h_bias = True | 52 | 15% |
| confirmed_next_candle = False | 38 | 3% |
| confirmed_next_candle = True | 44 | 20% |
| failed_2 = False | 65 | 15% |
| failed_2 = True | 17 | 0% |
| smt = False | 79 | 11% |
| smt = True | 3 | 33% |
| h1 = green | 42 | 7% |
| h1 = red | 40 | 18% |
| h4 = green | 45 | 4% |
| h4 = red | 37 | 22% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 37 (6.2 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 37 | 4 / 7 / 13 |
| window = W1 | 24 | 5 / 10 / 14 |
| window = W2 | 13 | 2 / 4 / 7 |
| direction = calls | 18 | 5 / 8 / 12 |
| direction = puts | 19 | 3 / 7 / 12 |
| W1 calls | 13 | 5 / 8 / 14 |
| W1 puts | 11 | 4 / 11 / 17 |
| W2 calls | 5 | 0 / 2 / 4 |
| W2 puts | 8 | 2 / 6 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 19% | 5% | 3% | 3% |
| W1 calls | 23% | 0% | 0% | 0% |
| W1 puts | 36% | 18% | 9% | 9% |
| W2 calls | 0% | 0% | 0% | 0% |
| W2 puts | 0% | 0% | 0% | 0% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 22% |
| pool_swept = 13:30 candle low | 7 | 0% |
| pool_swept = 9:30 open | 2 | 0% |
| pool_swept = bearish FVG CE | 6 | 0% |
| pool_swept = bearish order block opening | 1 | 0% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = bullish order block opening | 1 | 0% |
| pool_swept = midnight open | 2 | 0% |
| pool_swept = rejection block | 5 | 0% |
| with_4h_bias = False | 14 | 0% |
| with_4h_bias = True | 23 | 9% |
| confirmed_next_candle = False | 15 | 7% |
| confirmed_next_candle = True | 22 | 5% |
| failed_2 = False | 31 | 6% |
| failed_2 = True | 6 | 0% |
| smt = False | 36 | 6% |
| smt = True | 1 | 0% |
| h1 = green | 17 | 0% |
| h1 = red | 20 | 10% |
| h4 = green | 18 | 0% |
| h4 = red | 19 | 11% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
