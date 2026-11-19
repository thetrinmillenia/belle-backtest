# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-18.

## 5 minute signals

Signals: 71 (7.7 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 71 | 4 / 7 / 14 |
| window = W1 | 38 | 5 / 8 / 17 |
| window = W2 | 33 | 3 / 6 / 10 |
| direction = calls | 36 | 3 / 7 / 10 |
| direction = puts | 35 | 6 / 8 / 21 |
| W1 calls | 20 | 4 / 8 / 16 |
| W1 puts | 18 | 6 / 9 / 33 |
| W2 calls | 16 | 3 / 5 / 8 |
| W2 puts | 17 | 5 / 8 / 11 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 30% | 20% | 14% | 11% |
| W1 calls | 30% | 15% | 5% | 0% |
| W1 puts | 50% | 44% | 39% | 33% |
| W2 calls | 12% | 0% | 0% | 0% |
| W2 puts | 24% | 18% | 12% | 12% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 1 | 0% |
| pool_swept = 13:30 candle low | 5 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 15 | 33% |
| pool_swept = bearish order block opening | 5 | 0% |
| pool_swept = bullish FVG CE | 10 | 20% |
| pool_swept = bullish order block opening | 7 | 0% |
| pool_swept = equal highs | 1 | 100% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 18 | 22% |
| pool_swept = swing high | 1 | 100% |
| with_4h_bias = False | 28 | 11% |
| with_4h_bias = True | 43 | 26% |
| confirmed_next_candle = False | 30 | 10% |
| confirmed_next_candle = True | 41 | 27% |
| failed_2 = False | 57 | 21% |
| failed_2 = True | 14 | 14% |
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

Signals: 41 (5.5 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 41 | 6 / 8 / 15 |
| window = W1 | 27 | 6 / 10 / 16 |
| window = W2 | 14 | 5 / 7 / 11 |
| direction = calls | 22 | 6 / 8 / 13 |
| direction = puts | 19 | 5 / 10 / 25 |
| W1 calls | 15 | 6 / 8 / 13 |
| W1 puts | 12 | 7 / 18 / 25 |
| W2 calls | 7 | 7 / 8 / 10 |
| W2 puts | 7 | 3 / 6 / 17 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 34% | 17% | 15% | 7% |
| W1 calls | 20% | 0% | 0% | 0% |
| W1 puts | 58% | 42% | 33% | 8% |
| W2 calls | 29% | 0% | 0% | 0% |
| W2 puts | 29% | 29% | 29% | 29% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 8 | 38% |
| pool_swept = 13:30 candle low | 9 | 0% |
| pool_swept = 9:30 open | 2 | 0% |
| pool_swept = bearish FVG CE | 5 | 60% |
| pool_swept = bearish order block opening | 3 | 33% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = rejection block | 7 | 0% |
| pool_swept = swing high | 1 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 14 | 0% |
| with_4h_bias = True | 27 | 26% |
| confirmed_next_candle = False | 15 | 20% |
| confirmed_next_candle = True | 26 | 15% |
| failed_2 = False | 31 | 16% |
| failed_2 = True | 10 | 20% |
| smt = False | 38 | 18% |
| smt = True | 3 | 0% |
| h1 = green | 21 | 0% |
| h1 = red | 20 | 35% |
| h4 = green | 21 | 0% |
| h4 = red | 20 | 35% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
