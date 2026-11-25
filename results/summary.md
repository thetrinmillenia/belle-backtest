# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-24.

## 5 minute signals

Signals: 71 (7.7 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 71 | 4 / 8 / 16 |
| window = W1 | 38 | 6 / 10 / 24 |
| window = W2 | 33 | 3 / 6 / 11 |
| direction = calls | 35 | 4 / 7 / 12 |
| direction = puts | 36 | 6 / 10 / 33 |
| W1 calls | 19 | 5 / 9 / 16 |
| W1 puts | 19 | 6 / 22 / 35 |
| W2 calls | 16 | 3 / 5 / 8 |
| W2 puts | 17 | 5 / 10 / 14 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 35% | 23% | 18% | 15% |
| W1 calls | 32% | 11% | 5% | 0% |
| W1 puts | 58% | 53% | 47% | 42% |
| W2 calls | 19% | 0% | 0% | 0% |
| W2 puts | 29% | 24% | 18% | 18% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 1 | 100% |
| pool_swept = 13:30 candle low | 7 | 0% |
| pool_swept = 9:30 open | 5 | 20% |
| pool_swept = bearish FVG CE | 15 | 40% |
| pool_swept = bearish order block opening | 4 | 0% |
| pool_swept = bullish FVG CE | 10 | 10% |
| pool_swept = bullish order block opening | 6 | 0% |
| pool_swept = equal lows | 3 | 0% |
| pool_swept = rejection block | 18 | 28% |
| pool_swept = swing high | 2 | 100% |
| with_4h_bias = False | 28 | 7% |
| with_4h_bias = True | 43 | 33% |
| confirmed_next_candle = False | 29 | 10% |
| confirmed_next_candle = True | 42 | 31% |
| failed_2 = False | 58 | 22% |
| failed_2 = True | 13 | 23% |
| smt = False | 71 | 23% |
| h1 = green | 38 | 11% |
| h1 = red | 33 | 36% |
| h4 = green | 33 | 12% |
| h4 = red | 38 | 32% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: W2 entry 15:35 at 9:30 open, moved 10.17 pts | WRONG WAY: calls 14:25
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 40 (5.6 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 40 | 5 / 8 / 14 |
| window = W1 | 25 | 5 / 10 / 16 |
| window = W2 | 15 | 4 / 7 / 10 |
| direction = calls | 21 | 6 / 8 / 13 |
| direction = puts | 19 | 4 / 7 / 23 |
| W1 calls | 14 | 6 / 8 / 13 |
| W1 puts | 11 | 6 / 16 / 23 |
| W2 calls | 7 | 7 / 8 / 10 |
| W2 puts | 8 | 3 / 5 / 12 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 32% | 15% | 12% | 5% |
| W1 calls | 21% | 0% | 0% | 0% |
| W1 puts | 55% | 36% | 27% | 0% |
| W2 calls | 29% | 0% | 0% | 0% |
| W2 puts | 25% | 25% | 25% | 25% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 7 | 29% |
| pool_swept = 13:30 candle low | 10 | 0% |
| pool_swept = 9:30 open | 2 | 0% |
| pool_swept = bearish FVG CE | 4 | 75% |
| pool_swept = bearish order block opening | 3 | 33% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = rejection block | 7 | 0% |
| pool_swept = swing high | 1 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 13 | 0% |
| with_4h_bias = True | 27 | 22% |
| confirmed_next_candle = False | 15 | 13% |
| confirmed_next_candle = True | 25 | 16% |
| failed_2 = False | 30 | 13% |
| failed_2 = True | 10 | 20% |
| smt = False | 37 | 16% |
| smt = True | 3 | 0% |
| h1 = green | 20 | 0% |
| h1 = red | 20 | 30% |
| h4 = green | 21 | 0% |
| h4 = red | 19 | 32% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:30
- 2026-09-29 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:45
