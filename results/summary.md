# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-11.

## 5 minute signals

Signals: 73 (7.9 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 73 | 3 / 7 / 14 |
| window = W1 | 39 | 3 / 8 / 17 |
| window = W2 | 34 | 3 / 6 / 10 |
| direction = calls | 40 | 2 / 5 / 10 |
| direction = puts | 33 | 6 / 9 / 25 |
| W1 calls | 21 | 2 / 8 / 16 |
| W1 puts | 18 | 6 / 9 / 33 |
| W2 calls | 19 | 3 / 5 / 8 |
| W2 puts | 15 | 5 / 9 / 16 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 30% | 21% | 14% | 11% |
| W1 calls | 29% | 14% | 5% | 0% |
| W1 puts | 50% | 44% | 39% | 33% |
| W2 calls | 11% | 0% | 0% | 0% |
| W2 puts | 33% | 27% | 13% | 13% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 1 | 0% |
| pool_swept = 13:30 candle low | 5 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 12 | 42% |
| pool_swept = bearish order block opening | 5 | 20% |
| pool_swept = bullish FVG CE | 12 | 17% |
| pool_swept = bullish order block opening | 6 | 0% |
| pool_swept = equal highs | 1 | 100% |
| pool_swept = equal lows | 5 | 0% |
| pool_swept = rejection block | 20 | 20% |
| pool_swept = swing high | 2 | 50% |
| with_4h_bias = False | 29 | 14% |
| with_4h_bias = True | 44 | 25% |
| confirmed_next_candle = False | 31 | 10% |
| confirmed_next_candle = True | 42 | 29% |
| failed_2 = False | 60 | 22% |
| failed_2 = True | 13 | 15% |
| smt = False | 71 | 20% |
| smt = True | 2 | 50% |
| h1 = green | 38 | 11% |
| h1 = red | 35 | 31% |
| h4 = green | 34 | 9% |
| h4 = red | 39 | 31% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 39 (5.6 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 39 | 5 / 8 / 14 |
| window = W1 | 24 | 5 / 9 / 15 |
| window = W2 | 15 | 3 / 7 / 8 |
| direction = calls | 20 | 6 / 8 / 13 |
| direction = puts | 19 | 4 / 7 / 23 |
| W1 calls | 14 | 6 / 8 / 13 |
| W1 puts | 10 | 6 / 15 / 24 |
| W2 calls | 6 | 7 / 8 / 8 |
| W2 puts | 9 | 2 / 5 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 28% | 15% | 13% | 8% |
| W1 calls | 21% | 0% | 0% | 0% |
| W1 puts | 50% | 40% | 30% | 10% |
| W2 calls | 17% | 0% | 0% | 0% |
| W2 puts | 22% | 22% | 22% | 22% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 8 | 38% |
| pool_swept = 13:30 candle low | 8 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 5 | 40% |
| pool_swept = bearish order block opening | 3 | 33% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = rejection block | 5 | 0% |
| pool_swept = swing high | 1 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 16 | 0% |
| with_4h_bias = True | 23 | 26% |
| confirmed_next_candle = False | 11 | 18% |
| confirmed_next_candle = True | 28 | 14% |
| failed_2 = False | 31 | 13% |
| failed_2 = True | 8 | 25% |
| smt = False | 36 | 17% |
| smt = True | 3 | 0% |
| h1 = green | 19 | 0% |
| h1 = red | 20 | 30% |
| h4 = green | 19 | 0% |
| h4 = red | 20 | 30% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
