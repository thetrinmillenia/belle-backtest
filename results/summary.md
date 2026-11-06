# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-05.

## 5 minute signals

Signals: 77 (8.2 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 77 | 2 / 7 / 12 |
| window = W1 | 41 | 3 / 8 / 17 |
| window = W2 | 36 | 2 / 6 / 9 |
| direction = calls | 42 | 2 / 6 / 9 |
| direction = puts | 35 | 4 / 9 / 20 |
| W1 calls | 22 | 2 / 8 / 12 |
| W1 puts | 19 | 6 / 12 / 29 |
| W2 calls | 20 | 3 / 5 / 8 |
| W2 puts | 16 | 2 / 6 / 11 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 26% | 18% | 10% | 9% |
| W1 calls | 27% | 14% | 0% | 0% |
| W1 puts | 47% | 42% | 32% | 26% |
| W2 calls | 10% | 0% | 0% | 0% |
| W2 puts | 19% | 19% | 12% | 12% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 1 | 0% |
| pool_swept = 13:30 candle low | 6 | 17% |
| pool_swept = 9:30 open | 3 | 33% |
| pool_swept = bearish FVG CE | 13 | 38% |
| pool_swept = bearish order block opening | 6 | 17% |
| pool_swept = bullish FVG CE | 14 | 7% |
| pool_swept = bullish order block opening | 6 | 0% |
| pool_swept = equal highs | 2 | 50% |
| pool_swept = equal lows | 5 | 0% |
| pool_swept = rejection block | 20 | 20% |
| pool_swept = swing high | 1 | 0% |
| with_4h_bias = False | 30 | 17% |
| with_4h_bias = True | 47 | 19% |
| confirmed_next_candle = False | 29 | 10% |
| confirmed_next_candle = True | 48 | 23% |
| failed_2 = False | 64 | 19% |
| failed_2 = True | 13 | 15% |
| smt = False | 75 | 17% |
| smt = True | 2 | 50% |
| h1 = green | 41 | 10% |
| h1 = red | 36 | 28% |
| h4 = green | 35 | 9% |
| h4 = red | 42 | 26% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 45 (6.1 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 45 | 4 / 8 / 13 |
| window = W1 | 26 | 5 / 9 / 15 |
| window = W2 | 19 | 3 / 7 / 9 |
| direction = calls | 25 | 5 / 8 / 13 |
| direction = puts | 20 | 2 / 6 / 20 |
| W1 calls | 14 | 6 / 8 / 13 |
| W1 puts | 12 | 3 / 10 / 22 |
| W2 calls | 11 | 5 / 8 / 10 |
| W2 puts | 8 | 2 / 5 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 24% | 11% | 9% | 4% |
| W1 calls | 21% | 0% | 0% | 0% |
| W1 puts | 42% | 33% | 25% | 8% |
| W2 calls | 18% | 0% | 0% | 0% |
| W2 puts | 12% | 12% | 12% | 12% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 22% |
| pool_swept = 13:30 candle low | 10 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 6 | 33% |
| pool_swept = bearish order block opening | 3 | 33% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = bullish order block opening | 1 | 0% |
| pool_swept = rejection block | 7 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 19 | 0% |
| with_4h_bias = True | 26 | 19% |
| confirmed_next_candle = False | 14 | 14% |
| confirmed_next_candle = True | 31 | 10% |
| failed_2 = False | 35 | 9% |
| failed_2 = True | 10 | 20% |
| smt = False | 43 | 12% |
| smt = True | 2 | 0% |
| h1 = green | 25 | 0% |
| h1 = red | 20 | 25% |
| h4 = green | 24 | 0% |
| h4 = red | 21 | 24% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
