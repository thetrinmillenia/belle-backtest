# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-17.

## 5 minute signals

Signals: 72 (7.8 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 72 | 3 / 7 / 13 |
| window = W1 | 38 | 5 / 8 / 21 |
| window = W2 | 34 | 2 / 6 / 10 |
| direction = calls | 37 | 3 / 6 / 10 |
| direction = puts | 35 | 4 / 7 / 21 |
| W1 calls | 20 | 4 / 8 / 16 |
| W1 puts | 18 | 6 / 9 / 33 |
| W2 calls | 17 | 3 / 4 / 8 |
| W2 puts | 17 | 2 / 6 / 11 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 29% | 21% | 14% | 11% |
| W1 calls | 30% | 20% | 5% | 0% |
| W1 puts | 50% | 44% | 39% | 33% |
| W2 calls | 12% | 0% | 0% | 0% |
| W2 puts | 24% | 18% | 12% | 12% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 1 | 0% |
| pool_swept = 13:30 candle low | 6 | 17% |
| pool_swept = 9:30 open | 3 | 33% |
| pool_swept = bearish FVG CE | 15 | 33% |
| pool_swept = bearish order block opening | 5 | 0% |
| pool_swept = bullish FVG CE | 10 | 20% |
| pool_swept = bullish order block opening | 7 | 0% |
| pool_swept = equal highs | 1 | 100% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 19 | 21% |
| pool_swept = swing high | 1 | 100% |
| with_4h_bias = False | 28 | 14% |
| with_4h_bias = True | 44 | 25% |
| confirmed_next_candle = False | 28 | 14% |
| confirmed_next_candle = True | 44 | 25% |
| failed_2 = False | 59 | 20% |
| failed_2 = True | 13 | 23% |
| smt = False | 70 | 20% |
| smt = True | 2 | 50% |
| h1 = green | 34 | 12% |
| h1 = red | 38 | 29% |
| h4 = green | 30 | 13% |
| h4 = red | 42 | 26% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 44 (5.8 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 44 | 5 / 8 / 14 |
| window = W1 | 27 | 6 / 8 / 15 |
| window = W2 | 17 | 5 / 8 / 11 |
| direction = calls | 24 | 6 / 8 / 12 |
| direction = puts | 20 | 4 / 7 / 25 |
| W1 calls | 15 | 6 / 8 / 13 |
| W1 puts | 12 | 6 / 15 / 25 |
| W2 calls | 9 | 8 / 8 / 11 |
| W2 puts | 8 | 2 / 5 / 12 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 30% | 16% | 14% | 7% |
| W1 calls | 20% | 0% | 0% | 0% |
| W1 puts | 50% | 42% | 33% | 8% |
| W2 calls | 22% | 0% | 0% | 0% |
| W2 puts | 25% | 25% | 25% | 25% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 33% |
| pool_swept = 13:30 candle low | 10 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 5 | 60% |
| pool_swept = bearish order block opening | 3 | 33% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = rejection block | 7 | 0% |
| pool_swept = swing high | 1 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 16 | 0% |
| with_4h_bias = True | 28 | 25% |
| confirmed_next_candle = False | 16 | 19% |
| confirmed_next_candle = True | 28 | 14% |
| failed_2 = False | 33 | 15% |
| failed_2 = True | 11 | 18% |
| smt = False | 41 | 17% |
| smt = True | 3 | 0% |
| h1 = green | 23 | 0% |
| h1 = red | 21 | 33% |
| h4 = green | 23 | 0% |
| h4 = red | 21 | 33% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
