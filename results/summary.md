# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-06.

## 5 minute signals

Signals: 79 (8.6 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 79 | 2 / 7 / 12 |
| window = W1 | 40 | 5 / 9 / 16 |
| window = W2 | 39 | 2 / 6 / 9 |
| direction = calls | 40 | 1 / 6 / 9 |
| direction = puts | 39 | 5 / 9 / 16 |
| W1 calls | 20 | 4 / 9 / 11 |
| W1 puts | 20 | 5 / 11 / 18 |
| W2 calls | 20 | 0 / 3 / 8 |
| W2 puts | 19 | 5 / 7 / 11 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 25% | 13% | 5% | 5% |
| W1 calls | 25% | 5% | 0% | 0% |
| W1 puts | 45% | 35% | 15% | 15% |
| W2 calls | 10% | 0% | 0% | 0% |
| W2 puts | 21% | 11% | 5% | 5% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 2 | 0% |
| pool_swept = 13:30 candle low | 2 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 13 | 31% |
| pool_swept = bearish order block opening | 5 | 20% |
| pool_swept = bullish FVG CE | 17 | 6% |
| pool_swept = bullish order block opening | 2 | 0% |
| pool_swept = equal highs | 4 | 75% |
| pool_swept = equal lows | 5 | 0% |
| pool_swept = rejection block | 20 | 0% |
| pool_swept = swing high | 3 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 28 | 4% |
| with_4h_bias = True | 51 | 18% |
| confirmed_next_candle = False | 33 | 3% |
| confirmed_next_candle = True | 46 | 20% |
| failed_2 = False | 65 | 15% |
| failed_2 = True | 14 | 0% |
| smt = False | 77 | 12% |
| smt = True | 2 | 50% |
| h1 = green | 41 | 7% |
| h1 = red | 38 | 18% |
| h4 = green | 44 | 7% |
| h4 = red | 35 | 20% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 40 (6.2 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 40 | 3 / 8 / 14 |
| window = W1 | 26 | 5 / 12 / 15 |
| window = W2 | 14 | 1 / 3 / 7 |
| direction = calls | 20 | 3 / 8 / 13 |
| direction = puts | 20 | 3 / 8 / 15 |
| W1 calls | 13 | 8 / 12 / 14 |
| W1 puts | 13 | 4 / 11 / 19 |
| W2 calls | 7 | 1 / 1 / 3 |
| W2 puts | 7 | 3 / 7 / 8 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 28% | 12% | 10% | 10% |
| W1 calls | 31% | 8% | 8% | 8% |
| W1 puts | 38% | 23% | 15% | 15% |
| W2 calls | 14% | 0% | 0% | 0% |
| W2 puts | 14% | 14% | 14% | 14% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 22% |
| pool_swept = 13:30 candle low | 6 | 0% |
| pool_swept = 9:30 open | 2 | 0% |
| pool_swept = bearish FVG CE | 5 | 0% |
| pool_swept = bearish order block opening | 1 | 0% |
| pool_swept = bullish FVG CE | 6 | 17% |
| pool_swept = bullish order block opening | 2 | 0% |
| pool_swept = midnight open | 3 | 67% |
| pool_swept = rejection block | 6 | 0% |
| with_4h_bias = False | 16 | 0% |
| with_4h_bias = True | 24 | 21% |
| confirmed_next_candle = False | 16 | 19% |
| confirmed_next_candle = True | 24 | 8% |
| failed_2 = False | 31 | 16% |
| failed_2 = True | 9 | 0% |
| smt = False | 40 | 12% |
| h1 = green | 19 | 11% |
| h1 = red | 21 | 14% |
| h4 = green | 21 | 10% |
| h4 = red | 19 | 16% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
