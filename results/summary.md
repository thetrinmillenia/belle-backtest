# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-24.

## 5 minute signals

Signals: 69 (7.7 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 69 | 4 / 8 / 16 |
| window = W1 | 37 | 6 / 10 / 22 |
| window = W2 | 32 | 3 / 6 / 11 |
| direction = calls | 34 | 4 / 7 / 11 |
| direction = puts | 35 | 6 / 10 / 29 |
| W1 calls | 19 | 5 / 9 / 16 |
| W1 puts | 18 | 6 / 17 / 35 |
| W2 calls | 15 | 2 / 4 / 7 |
| W2 puts | 17 | 5 / 10 / 14 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 33% | 22% | 17% | 14% |
| W1 calls | 32% | 11% | 5% | 0% |
| W1 puts | 56% | 50% | 44% | 39% |
| W2 calls | 13% | 0% | 0% | 0% |
| W2 puts | 29% | 24% | 18% | 18% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 1 | 100% |
| pool_swept = 13:30 candle low | 7 | 0% |
| pool_swept = 9:30 open | 5 | 20% |
| pool_swept = bearish FVG CE | 15 | 40% |
| pool_swept = bearish order block opening | 4 | 0% |
| pool_swept = bullish FVG CE | 9 | 11% |
| pool_swept = bullish order block opening | 6 | 0% |
| pool_swept = equal lows | 3 | 0% |
| pool_swept = rejection block | 17 | 24% |
| pool_swept = swing high | 2 | 100% |
| with_4h_bias = False | 27 | 7% |
| with_4h_bias = True | 42 | 31% |
| confirmed_next_candle = False | 28 | 11% |
| confirmed_next_candle = True | 41 | 29% |
| failed_2 = False | 56 | 21% |
| failed_2 = True | 13 | 23% |
| smt = False | 69 | 22% |
| h1 = green | 36 | 8% |
| h1 = red | 33 | 36% |
| h4 = green | 31 | 10% |
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
