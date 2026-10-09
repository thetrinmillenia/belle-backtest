# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-08.

## 5 minute signals

Signals: 81 (8.8 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 81 | 2 / 7 / 11 |
| window = W1 | 42 | 3 / 8 / 15 |
| window = W2 | 39 | 2 / 7 / 9 |
| direction = calls | 39 | 2 / 7 / 10 |
| direction = puts | 42 | 4 / 7 / 15 |
| W1 calls | 21 | 2 / 8 / 11 |
| W1 puts | 21 | 4 / 9 / 17 |
| W2 calls | 18 | 1 / 4 / 8 |
| W2 puts | 21 | 3 / 7 / 10 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 22% | 12% | 4% | 4% |
| W1 calls | 24% | 5% | 0% | 0% |
| W1 puts | 38% | 29% | 10% | 10% |
| W2 calls | 11% | 0% | 0% | 0% |
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
| pool_swept = bullish order block opening | 3 | 0% |
| pool_swept = equal highs | 4 | 75% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 17 | 0% |
| pool_swept = swing high | 3 | 0% |
| pool_swept = swing low | 3 | 0% |
| with_4h_bias = False | 30 | 7% |
| with_4h_bias = True | 51 | 16% |
| confirmed_next_candle = False | 36 | 3% |
| confirmed_next_candle = True | 45 | 20% |
| failed_2 = False | 66 | 15% |
| failed_2 = True | 15 | 0% |
| smt = False | 78 | 12% |
| smt = True | 3 | 33% |
| h1 = green | 41 | 7% |
| h1 = red | 40 | 18% |
| h4 = green | 44 | 5% |
| h4 = red | 37 | 22% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 38 (6.1 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 38 | 4 / 7 / 13 |
| window = W1 | 25 | 5 / 11 / 14 |
| window = W2 | 13 | 2 / 4 / 7 |
| direction = calls | 19 | 5 / 8 / 13 |
| direction = puts | 19 | 3 / 7 / 12 |
| W1 calls | 14 | 6 / 10 / 14 |
| W1 puts | 11 | 4 / 11 / 17 |
| W2 calls | 5 | 0 / 2 / 4 |
| W2 puts | 8 | 2 / 6 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 21% | 8% | 5% | 5% |
| W1 calls | 29% | 7% | 7% | 7% |
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
| pool_swept = bullish FVG CE | 5 | 20% |
| pool_swept = bullish order block opening | 1 | 0% |
| pool_swept = midnight open | 2 | 0% |
| pool_swept = rejection block | 5 | 0% |
| with_4h_bias = False | 14 | 0% |
| with_4h_bias = True | 24 | 12% |
| confirmed_next_candle = False | 16 | 12% |
| confirmed_next_candle = True | 22 | 5% |
| failed_2 = False | 32 | 9% |
| failed_2 = True | 6 | 0% |
| smt = False | 37 | 8% |
| smt = True | 1 | 0% |
| h1 = green | 18 | 6% |
| h1 = red | 20 | 10% |
| h4 = green | 19 | 5% |
| h4 = red | 19 | 11% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
