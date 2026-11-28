# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-27.

## 5 minute signals

Signals: 69 (7.7 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 69 | 5 / 9 / 16 |
| window = W1 | 37 | 6 / 10 / 25 |
| window = W2 | 32 | 4 / 7 / 12 |
| direction = calls | 35 | 4 / 7 / 12 |
| direction = puts | 34 | 6 / 11 / 33 |
| W1 calls | 19 | 5 / 10 / 16 |
| W1 puts | 18 | 6 / 23 / 35 |
| W2 calls | 16 | 3 / 5 / 8 |
| W2 puts | 16 | 6 / 10 / 19 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 38% | 25% | 19% | 16% |
| W1 calls | 32% | 11% | 5% | 0% |
| W1 puts | 61% | 56% | 50% | 44% |
| W2 calls | 19% | 0% | 0% | 0% |
| W2 puts | 38% | 31% | 19% | 19% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 1 | 100% |
| pool_swept = 13:30 candle low | 7 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 15 | 40% |
| pool_swept = bearish order block opening | 5 | 20% |
| pool_swept = bullish FVG CE | 11 | 9% |
| pool_swept = bullish order block opening | 6 | 0% |
| pool_swept = equal lows | 3 | 0% |
| pool_swept = rejection block | 15 | 33% |
| pool_swept = swing high | 2 | 100% |
| with_4h_bias = False | 26 | 12% |
| with_4h_bias = True | 43 | 33% |
| confirmed_next_candle = False | 30 | 13% |
| confirmed_next_candle = True | 39 | 33% |
| failed_2 = False | 56 | 25% |
| failed_2 = True | 13 | 23% |
| smt = False | 69 | 25% |
| h1 = green | 37 | 11% |
| h1 = red | 32 | 41% |
| h4 = green | 32 | 12% |
| h4 = red | 37 | 35% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: W2 entry 15:35 at 9:30 open, moved 10.17 pts | WRONG WAY: calls 14:25
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 39 (5.6 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 39 | 5 / 8 / 15 |
| window = W1 | 25 | 5 / 12 / 17 |
| window = W2 | 14 | 5 / 7 / 11 |
| direction = calls | 21 | 6 / 8 / 13 |
| direction = puts | 18 | 5 / 9 / 24 |
| W1 calls | 14 | 6 / 10 / 14 |
| W1 puts | 11 | 6 / 16 / 23 |
| W2 calls | 7 | 7 / 8 / 10 |
| W2 puts | 7 | 4 / 6 / 17 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 36% | 15% | 13% | 5% |
| W1 calls | 29% | 0% | 0% | 0% |
| W1 puts | 55% | 36% | 27% | 0% |
| W2 calls | 29% | 0% | 0% | 0% |
| W2 puts | 29% | 29% | 29% | 29% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 7 | 29% |
| pool_swept = 13:30 candle low | 10 | 0% |
| pool_swept = 9:30 open | 1 | 0% |
| pool_swept = bearish FVG CE | 4 | 75% |
| pool_swept = bearish order block opening | 3 | 33% |
| pool_swept = bullish FVG CE | 5 | 0% |
| pool_swept = rejection block | 6 | 0% |
| pool_swept = swing high | 1 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 12 | 0% |
| with_4h_bias = True | 27 | 22% |
| confirmed_next_candle = False | 15 | 13% |
| confirmed_next_candle = True | 24 | 17% |
| failed_2 = False | 28 | 14% |
| failed_2 = True | 11 | 18% |
| smt = False | 36 | 17% |
| smt = True | 3 | 0% |
| h1 = green | 20 | 0% |
| h1 = red | 19 | 32% |
| h4 = green | 20 | 0% |
| h4 = red | 19 | 32% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED
- 2026-09-29 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:45
