# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-23.

## 5 minute signals

Signals: 80 (8.5 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 80 | 2 / 7 / 11 |
| window = W1 | 43 | 3 / 9 / 16 |
| window = W2 | 37 | 2 / 6 / 8 |
| direction = calls | 39 | 1 / 5 / 10 |
| direction = puts | 41 | 3 / 7 / 12 |
| W1 calls | 20 | 2 / 8 / 13 |
| W1 puts | 23 | 5 / 10 / 16 |
| W2 calls | 19 | 1 / 4 / 7 |
| W2 puts | 18 | 3 / 6 / 10 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 24% | 15% | 6% | 5% |
| W1 calls | 30% | 15% | 0% | 0% |
| W1 puts | 43% | 30% | 17% | 13% |
| W2 calls | 5% | 0% | 0% | 0% |
| W2 puts | 11% | 11% | 6% | 6% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 2 | 0% |
| pool_swept = 13:30 candle low | 5 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 14 | 29% |
| pool_swept = bearish order block opening | 6 | 33% |
| pool_swept = bullish FVG CE | 13 | 8% |
| pool_swept = bullish order block opening | 6 | 0% |
| pool_swept = equal highs | 2 | 50% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 18 | 11% |
| pool_swept = swing high | 3 | 0% |
| pool_swept = swing low | 3 | 33% |
| with_4h_bias = False | 30 | 13% |
| with_4h_bias = True | 50 | 16% |
| confirmed_next_candle = False | 34 | 6% |
| confirmed_next_candle = True | 46 | 22% |
| failed_2 = False | 67 | 18% |
| failed_2 = True | 13 | 0% |
| smt = False | 77 | 14% |
| smt = True | 3 | 33% |
| h1 = green | 41 | 5% |
| h1 = red | 39 | 26% |
| h4 = green | 38 | 3% |
| h4 = red | 42 | 26% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 41 (5.9 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 41 | 4 / 8 / 13 |
| window = W1 | 27 | 6 / 11 / 14 |
| window = W2 | 14 | 2 / 4 / 7 |
| direction = calls | 23 | 5 / 8 / 13 |
| direction = puts | 18 | 2 / 7 / 12 |
| W1 calls | 16 | 7 / 10 / 14 |
| W1 puts | 11 | 5 / 11 / 20 |
| W2 calls | 7 | 1 / 4 / 8 |
| W2 puts | 7 | 2 / 5 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 22% | 7% | 5% | 2% |
| W1 calls | 31% | 0% | 0% | 0% |
| W1 puts | 36% | 27% | 18% | 9% |
| W2 calls | 0% | 0% | 0% | 0% |
| W2 puts | 0% | 0% | 0% | 0% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 22% |
| pool_swept = 13:30 candle low | 9 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 5 | 20% |
| pool_swept = bearish order block opening | 1 | 0% |
| pool_swept = bullish FVG CE | 5 | 0% |
| pool_swept = bullish order block opening | 1 | 0% |
| pool_swept = midnight open | 2 | 0% |
| pool_swept = rejection block | 4 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 17 | 0% |
| with_4h_bias = True | 24 | 12% |
| confirmed_next_candle = False | 14 | 7% |
| confirmed_next_candle = True | 27 | 7% |
| failed_2 = False | 34 | 9% |
| failed_2 = True | 7 | 0% |
| smt = False | 39 | 8% |
| smt = True | 2 | 0% |
| h1 = green | 21 | 0% |
| h1 = red | 20 | 15% |
| h4 = green | 21 | 0% |
| h4 = red | 20 | 15% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
