# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-20.

## 5 minute signals

Signals: 73 (7.9 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 73 | 4 / 7 / 16 |
| window = W1 | 39 | 6 / 9 / 24 |
| window = W2 | 34 | 2 / 6 / 10 |
| direction = calls | 34 | 4 / 7 / 10 |
| direction = puts | 39 | 5 / 8 / 29 |
| W1 calls | 18 | 5 / 9 / 16 |
| W1 puts | 21 | 6 / 12 / 36 |
| W2 calls | 16 | 3 / 5 / 8 |
| W2 puts | 18 | 3 / 7 / 14 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 33% | 25% | 18% | 15% |
| W1 calls | 33% | 22% | 6% | 0% |
| W1 puts | 52% | 48% | 43% | 38% |
| W2 calls | 12% | 0% | 0% | 0% |
| W2 puts | 28% | 22% | 17% | 17% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 2 | 50% |
| pool_swept = 13:30 candle low | 6 | 17% |
| pool_swept = 9:30 open | 3 | 33% |
| pool_swept = bearish FVG CE | 18 | 39% |
| pool_swept = bearish order block opening | 5 | 0% |
| pool_swept = bullish FVG CE | 10 | 20% |
| pool_swept = bullish order block opening | 6 | 0% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 17 | 24% |
| pool_swept = swing high | 2 | 100% |
| with_4h_bias = False | 27 | 11% |
| with_4h_bias = True | 46 | 33% |
| confirmed_next_candle = False | 27 | 15% |
| confirmed_next_candle = True | 46 | 30% |
| failed_2 = False | 59 | 24% |
| failed_2 = True | 14 | 29% |
| smt = False | 72 | 25% |
| smt = True | 1 | 0% |
| h1 = green | 32 | 12% |
| h1 = red | 41 | 34% |
| h4 = green | 28 | 14% |
| h4 = red | 45 | 31% |

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
| All | 44 | 6 / 8 / 14 |
| window = W1 | 28 | 6 / 9 / 16 |
| window = W2 | 16 | 5 / 8 / 11 |
| direction = calls | 24 | 6 / 8 / 12 |
| direction = puts | 20 | 5 / 9 / 25 |
| W1 calls | 15 | 6 / 8 / 13 |
| W1 puts | 13 | 6 / 16 / 25 |
| W2 calls | 9 | 8 / 8 / 11 |
| W2 puts | 7 | 3 / 6 / 17 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 32% | 16% | 14% | 7% |
| W1 calls | 20% | 0% | 0% | 0% |
| W1 puts | 54% | 38% | 31% | 8% |
| W2 calls | 22% | 0% | 0% | 0% |
| W2 puts | 29% | 29% | 29% | 29% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 33% |
| pool_swept = 13:30 candle low | 10 | 0% |
| pool_swept = 9:30 open | 2 | 0% |
| pool_swept = bearish FVG CE | 5 | 60% |
| pool_swept = bearish order block opening | 3 | 33% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = rejection block | 8 | 0% |
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
