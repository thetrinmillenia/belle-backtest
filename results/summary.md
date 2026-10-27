# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-26.

## 5 minute signals

Signals: 81 (8.6 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 81 | 2 / 7 / 11 |
| window = W1 | 44 | 3 / 8 / 13 |
| window = W2 | 37 | 2 / 6 / 9 |
| direction = calls | 39 | 2 / 6 / 9 |
| direction = puts | 42 | 3 / 8 / 12 |
| W1 calls | 20 | 2 / 8 / 11 |
| W1 puts | 24 | 4 / 9 / 16 |
| W2 calls | 19 | 1 / 4 / 8 |
| W2 puts | 18 | 2 / 6 / 10 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 22% | 14% | 6% | 5% |
| W1 calls | 20% | 10% | 0% | 0% |
| W1 puts | 42% | 29% | 17% | 12% |
| W2 calls | 5% | 0% | 0% | 0% |
| W2 puts | 17% | 11% | 6% | 6% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 2 | 0% |
| pool_swept = 13:30 candle low | 6 | 17% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 14 | 29% |
| pool_swept = bearish order block opening | 8 | 25% |
| pool_swept = bullish FVG CE | 15 | 7% |
| pool_swept = bullish order block opening | 6 | 0% |
| pool_swept = equal highs | 2 | 50% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 16 | 6% |
| pool_swept = swing high | 3 | 0% |
| pool_swept = swing low | 1 | 0% |
| with_4h_bias = False | 31 | 13% |
| with_4h_bias = True | 50 | 14% |
| confirmed_next_candle = False | 35 | 9% |
| confirmed_next_candle = True | 46 | 17% |
| failed_2 = False | 67 | 15% |
| failed_2 = True | 14 | 7% |
| smt = False | 79 | 13% |
| smt = True | 2 | 50% |
| h1 = green | 41 | 5% |
| h1 = red | 40 | 22% |
| h4 = green | 37 | 3% |
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
| window = W1 | 28 | 5 / 10 / 14 |
| window = W2 | 16 | 2 / 6 / 8 |
| direction = calls | 25 | 5 / 8 / 13 |
| direction = puts | 19 | 2 / 7 / 12 |
| W1 calls | 16 | 7 / 10 / 14 |
| W1 puts | 12 | 3 / 10 / 20 |
| W2 calls | 9 | 2 / 7 / 8 |
| W2 puts | 7 | 2 / 5 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 25% | 7% | 5% | 2% |
| W1 calls | 31% | 0% | 0% | 0% |
| W1 puts | 33% | 25% | 17% | 8% |
| W2 calls | 22% | 0% | 0% | 0% |
| W2 puts | 0% | 0% | 0% | 0% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 10 | 20% |
| pool_swept = 13:30 candle low | 10 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 5 | 20% |
| pool_swept = bearish order block opening | 1 | 0% |
| pool_swept = bullish FVG CE | 5 | 0% |
| pool_swept = bullish order block opening | 2 | 0% |
| pool_swept = midnight open | 1 | 0% |
| pool_swept = rejection block | 5 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 18 | 0% |
| with_4h_bias = True | 26 | 12% |
| confirmed_next_candle = False | 14 | 7% |
| confirmed_next_candle = True | 30 | 7% |
| failed_2 = False | 35 | 9% |
| failed_2 = True | 9 | 0% |
| smt = False | 42 | 7% |
| smt = True | 2 | 0% |
| h1 = green | 23 | 0% |
| h1 = red | 21 | 14% |
| h4 = green | 21 | 0% |
| h4 = red | 23 | 13% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
