# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-10.

## 5 minute signals

Signals: 75 (8.0 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 75 | 3 / 7 / 14 |
| window = W1 | 40 | 3 / 8 / 17 |
| window = W2 | 35 | 3 / 6 / 10 |
| direction = calls | 42 | 2 / 5 / 9 |
| direction = puts | 33 | 6 / 9 / 25 |
| W1 calls | 22 | 2 / 8 / 14 |
| W1 puts | 18 | 6 / 9 / 33 |
| W2 calls | 20 | 3 / 5 / 7 |
| W2 puts | 15 | 5 / 9 / 16 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 29% | 20% | 13% | 11% |
| W1 calls | 27% | 14% | 5% | 0% |
| W1 puts | 50% | 44% | 39% | 33% |
| W2 calls | 10% | 0% | 0% | 0% |
| W2 puts | 33% | 27% | 13% | 13% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 1 | 0% |
| pool_swept = 13:30 candle low | 5 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 12 | 42% |
| pool_swept = bearish order block opening | 5 | 20% |
| pool_swept = bullish FVG CE | 14 | 14% |
| pool_swept = bullish order block opening | 6 | 0% |
| pool_swept = equal highs | 1 | 100% |
| pool_swept = equal lows | 5 | 0% |
| pool_swept = rejection block | 20 | 20% |
| pool_swept = swing high | 2 | 50% |
| with_4h_bias = False | 29 | 14% |
| with_4h_bias = True | 46 | 24% |
| confirmed_next_candle = False | 31 | 10% |
| confirmed_next_candle = True | 44 | 27% |
| failed_2 = False | 62 | 21% |
| failed_2 = True | 13 | 15% |
| smt = False | 73 | 19% |
| smt = True | 2 | 50% |
| h1 = green | 40 | 10% |
| h1 = red | 35 | 31% |
| h4 = green | 36 | 8% |
| h4 = red | 39 | 31% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 41 (5.7 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 41 | 5 / 8 / 14 |
| window = W1 | 25 | 5 / 8 / 15 |
| window = W2 | 16 | 2 / 7 / 8 |
| direction = calls | 21 | 5 / 8 / 13 |
| direction = puts | 20 | 3 / 7 / 22 |
| W1 calls | 14 | 6 / 8 / 13 |
| W1 puts | 11 | 5 / 10 / 23 |
| W2 calls | 7 | 4 / 8 / 8 |
| W2 puts | 9 | 2 / 5 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 27% | 15% | 12% | 7% |
| W1 calls | 21% | 0% | 0% | 0% |
| W1 puts | 45% | 36% | 27% | 9% |
| W2 calls | 14% | 0% | 0% | 0% |
| W2 puts | 22% | 22% | 22% | 22% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 8 | 38% |
| pool_swept = 13:30 candle low | 8 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 6 | 33% |
| pool_swept = bearish order block opening | 3 | 33% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = rejection block | 6 | 0% |
| pool_swept = swing high | 1 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 17 | 0% |
| with_4h_bias = True | 24 | 25% |
| confirmed_next_candle = False | 11 | 18% |
| confirmed_next_candle = True | 30 | 13% |
| failed_2 = False | 33 | 12% |
| failed_2 = True | 8 | 25% |
| smt = False | 38 | 16% |
| smt = True | 3 | 0% |
| h1 = green | 20 | 0% |
| h1 = red | 21 | 29% |
| h4 = green | 20 | 0% |
| h4 = red | 21 | 29% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
