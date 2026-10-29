# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-28.

## 5 minute signals

Signals: 80 (8.5 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 80 | 2 / 7 / 11 |
| window = W1 | 44 | 3 / 8 / 16 |
| window = W2 | 36 | 2 / 6 / 9 |
| direction = calls | 40 | 2 / 7 / 10 |
| direction = puts | 40 | 2 / 6 / 13 |
| W1 calls | 22 | 3 / 8 / 12 |
| W1 puts | 22 | 3 / 8 / 17 |
| W2 calls | 18 | 2 / 5 / 8 |
| W2 puts | 18 | 2 / 6 / 10 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 24% | 15% | 6% | 5% |
| W1 calls | 27% | 14% | 0% | 0% |
| W1 puts | 41% | 32% | 18% | 14% |
| W2 calls | 6% | 0% | 0% | 0% |
| W2 puts | 17% | 11% | 6% | 6% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 2 | 0% |
| pool_swept = 13:30 candle low | 6 | 17% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 13 | 31% |
| pool_swept = bearish order block opening | 8 | 25% |
| pool_swept = bullish FVG CE | 15 | 7% |
| pool_swept = bullish order block opening | 6 | 0% |
| pool_swept = equal highs | 2 | 50% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 17 | 12% |
| pool_swept = swing high | 2 | 0% |
| pool_swept = swing low | 1 | 0% |
| with_4h_bias = False | 31 | 16% |
| with_4h_bias = True | 49 | 14% |
| confirmed_next_candle = False | 33 | 9% |
| confirmed_next_candle = True | 47 | 19% |
| failed_2 = False | 66 | 17% |
| failed_2 = True | 14 | 7% |
| smt = False | 78 | 14% |
| smt = True | 2 | 50% |
| h1 = green | 40 | 8% |
| h1 = red | 40 | 22% |
| h4 = green | 36 | 6% |
| h4 = red | 44 | 23% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 44 (6.1 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 44 | 4 / 8 / 13 |
| window = W1 | 28 | 5 / 9 / 14 |
| window = W2 | 16 | 2 / 7 / 9 |
| direction = calls | 27 | 6 / 8 / 13 |
| direction = puts | 17 | 2 / 5 / 11 |
| W1 calls | 17 | 6 / 8 / 14 |
| W1 puts | 11 | 3 / 9 / 20 |
| W2 calls | 10 | 4 / 8 / 10 |
| W2 puts | 6 | 2 / 3 / 6 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 25% | 7% | 5% | 2% |
| W1 calls | 29% | 0% | 0% | 0% |
| W1 puts | 36% | 27% | 18% | 9% |
| W2 calls | 20% | 0% | 0% | 0% |
| W2 puts | 0% | 0% | 0% | 0% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 8 | 25% |
| pool_swept = 13:30 candle low | 10 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 5 | 20% |
| pool_swept = bearish order block opening | 1 | 0% |
| pool_swept = bullish FVG CE | 5 | 0% |
| pool_swept = bullish order block opening | 2 | 0% |
| pool_swept = midnight open | 1 | 0% |
| pool_swept = rejection block | 6 | 0% |
| pool_swept = swing low | 3 | 0% |
| with_4h_bias = False | 19 | 0% |
| with_4h_bias = True | 25 | 12% |
| confirmed_next_candle = False | 13 | 8% |
| confirmed_next_candle = True | 31 | 6% |
| failed_2 = False | 35 | 9% |
| failed_2 = True | 9 | 0% |
| smt = False | 42 | 7% |
| smt = True | 2 | 0% |
| h1 = green | 25 | 0% |
| h1 = red | 19 | 16% |
| h4 = green | 23 | 0% |
| h4 = red | 21 | 14% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
