# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-12.

## 5 minute signals

Signals: 81 (8.8 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 81 | 2 / 7 / 11 |
| window = W1 | 43 | 3 / 8 / 14 |
| window = W2 | 38 | 2 / 7 / 9 |
| direction = calls | 38 | 2 / 7 / 9 |
| direction = puts | 43 | 4 / 8 / 14 |
| W1 calls | 21 | 2 / 8 / 11 |
| W1 puts | 22 | 4 / 8 / 16 |
| W2 calls | 17 | 0 / 5 / 8 |
| W2 puts | 21 | 6 / 8 / 11 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 22% | 12% | 4% | 4% |
| W1 calls | 24% | 5% | 0% | 0% |
| W1 puts | 36% | 27% | 9% | 9% |
| W2 calls | 6% | 0% | 0% | 0% |
| W2 puts | 19% | 14% | 5% | 5% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 3 | 0% |
| pool_swept = 13:30 candle low | 3 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 16 | 19% |
| pool_swept = bearish order block opening | 7 | 29% |
| pool_swept = bullish FVG CE | 16 | 6% |
| pool_swept = bullish order block opening | 3 | 0% |
| pool_swept = equal highs | 4 | 75% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 17 | 0% |
| pool_swept = swing high | 3 | 0% |
| pool_swept = swing low | 1 | 0% |
| with_4h_bias = False | 30 | 7% |
| with_4h_bias = True | 51 | 16% |
| confirmed_next_candle = False | 34 | 3% |
| confirmed_next_candle = True | 47 | 19% |
| failed_2 = False | 66 | 15% |
| failed_2 = True | 15 | 0% |
| smt = False | 79 | 11% |
| smt = True | 2 | 50% |
| h1 = green | 41 | 7% |
| h1 = red | 40 | 18% |
| h4 = green | 43 | 5% |
| h4 = red | 38 | 21% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 38 (6.3 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 38 | 4 / 7 / 13 |
| window = W1 | 25 | 5 / 9 / 14 |
| window = W2 | 13 | 2 / 4 / 7 |
| direction = calls | 17 | 5 / 8 / 13 |
| direction = puts | 21 | 2 / 6 / 11 |
| W1 calls | 12 | 7 / 10 / 14 |
| W1 puts | 13 | 4 / 9 / 14 |
| W2 calls | 5 | 0 / 2 / 4 |
| W2 puts | 8 | 2 / 6 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 21% | 5% | 3% | 3% |
| W1 calls | 25% | 0% | 0% | 0% |
| W1 puts | 31% | 15% | 8% | 8% |
| W2 calls | 20% | 0% | 0% | 0% |
| W2 puts | 0% | 0% | 0% | 0% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 10 | 20% |
| pool_swept = 13:30 candle low | 7 | 0% |
| pool_swept = 9:30 open | 2 | 0% |
| pool_swept = bearish FVG CE | 7 | 0% |
| pool_swept = bearish order block opening | 1 | 0% |
| pool_swept = bullish FVG CE | 3 | 0% |
| pool_swept = bullish order block opening | 2 | 0% |
| pool_swept = midnight open | 1 | 0% |
| pool_swept = rejection block | 5 | 0% |
| with_4h_bias = False | 15 | 0% |
| with_4h_bias = True | 23 | 9% |
| confirmed_next_candle = False | 15 | 7% |
| confirmed_next_candle = True | 23 | 4% |
| failed_2 = False | 30 | 7% |
| failed_2 = True | 8 | 0% |
| smt = False | 37 | 5% |
| smt = True | 1 | 0% |
| h1 = green | 16 | 0% |
| h1 = red | 22 | 9% |
| h4 = green | 17 | 0% |
| h4 = red | 21 | 10% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
