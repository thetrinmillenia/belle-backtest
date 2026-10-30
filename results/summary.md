# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-29.

## 5 minute signals

Signals: 79 (8.4 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 79 | 2 / 7 / 11 |
| window = W1 | 43 | 3 / 8 / 16 |
| window = W2 | 36 | 2 / 6 / 9 |
| direction = calls | 41 | 2 / 7 / 10 |
| direction = puts | 38 | 2 / 6 / 12 |
| W1 calls | 22 | 3 / 8 / 12 |
| W1 puts | 21 | 3 / 7 / 17 |
| W2 calls | 19 | 2 / 5 / 8 |
| W2 puts | 17 | 2 / 6 / 9 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 23% | 15% | 6% | 5% |
| W1 calls | 27% | 14% | 0% | 0% |
| W1 puts | 38% | 33% | 19% | 14% |
| W2 calls | 11% | 0% | 0% | 0% |
| W2 puts | 12% | 12% | 6% | 6% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 2 | 0% |
| pool_swept = 13:30 candle low | 6 | 17% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 12 | 33% |
| pool_swept = bearish order block opening | 8 | 25% |
| pool_swept = bullish FVG CE | 15 | 7% |
| pool_swept = bullish order block opening | 7 | 0% |
| pool_swept = equal highs | 2 | 50% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 16 | 12% |
| pool_swept = swing high | 2 | 0% |
| pool_swept = swing low | 1 | 0% |
| with_4h_bias = False | 32 | 16% |
| with_4h_bias = True | 47 | 15% |
| confirmed_next_candle = False | 33 | 9% |
| confirmed_next_candle = True | 46 | 20% |
| failed_2 = False | 66 | 17% |
| failed_2 = True | 13 | 8% |
| smt = False | 77 | 14% |
| smt = True | 2 | 50% |
| h1 = green | 41 | 7% |
| h1 = red | 38 | 24% |
| h4 = green | 37 | 5% |
| h4 = red | 42 | 24% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 46 (6.2 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 46 | 4 / 8 / 13 |
| window = W1 | 29 | 5 / 8 / 14 |
| window = W2 | 17 | 2 / 7 / 9 |
| direction = calls | 28 | 6 / 8 / 13 |
| direction = puts | 18 | 2 / 5 / 11 |
| W1 calls | 17 | 6 / 8 / 14 |
| W1 puts | 12 | 1 / 7 / 20 |
| W2 calls | 11 | 5 / 8 / 12 |
| W2 puts | 6 | 2 / 3 / 6 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 26% | 7% | 4% | 2% |
| W1 calls | 29% | 0% | 0% | 0% |
| W1 puts | 33% | 25% | 17% | 8% |
| W2 calls | 27% | 0% | 0% | 0% |
| W2 puts | 0% | 0% | 0% | 0% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 8 | 25% |
| pool_swept = 13:30 candle low | 10 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 5 | 20% |
| pool_swept = bearish order block opening | 2 | 0% |
| pool_swept = bullish FVG CE | 5 | 0% |
| pool_swept = bullish order block opening | 2 | 0% |
| pool_swept = midnight open | 1 | 0% |
| pool_swept = rejection block | 7 | 0% |
| pool_swept = swing low | 3 | 0% |
| with_4h_bias = False | 20 | 0% |
| with_4h_bias = True | 26 | 12% |
| confirmed_next_candle = False | 14 | 7% |
| confirmed_next_candle = True | 32 | 6% |
| failed_2 = False | 37 | 8% |
| failed_2 = True | 9 | 0% |
| smt = False | 44 | 7% |
| smt = True | 2 | 0% |
| h1 = green | 26 | 0% |
| h1 = red | 20 | 15% |
| h4 = green | 24 | 0% |
| h4 = red | 22 | 14% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
