# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-22.

## 5 minute signals

Signals: 82 (8.7 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 82 | 2 / 7 / 11 |
| window = W1 | 45 | 3 / 8 / 13 |
| window = W2 | 37 | 2 / 6 / 9 |
| direction = calls | 37 | 2 / 7 / 9 |
| direction = puts | 45 | 2 / 7 / 12 |
| W1 calls | 20 | 2 / 8 / 11 |
| W1 puts | 25 | 3 / 9 / 16 |
| W2 calls | 17 | 2 / 5 / 8 |
| W2 puts | 20 | 2 / 6 / 10 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 22% | 13% | 6% | 5% |
| W1 calls | 20% | 10% | 0% | 0% |
| W1 puts | 40% | 28% | 16% | 12% |
| W2 calls | 6% | 0% | 0% | 0% |
| W2 puts | 15% | 10% | 5% | 5% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 2 | 0% |
| pool_swept = 13:30 candle low | 6 | 17% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 15 | 27% |
| pool_swept = bearish order block opening | 10 | 20% |
| pool_swept = bullish FVG CE | 14 | 7% |
| pool_swept = bullish order block opening | 6 | 0% |
| pool_swept = equal highs | 2 | 50% |
| pool_swept = equal lows | 3 | 0% |
| pool_swept = rejection block | 16 | 6% |
| pool_swept = swing high | 3 | 0% |
| pool_swept = swing low | 1 | 0% |
| with_4h_bias = False | 31 | 13% |
| with_4h_bias = True | 51 | 14% |
| confirmed_next_candle = False | 34 | 9% |
| confirmed_next_candle = True | 48 | 17% |
| failed_2 = False | 68 | 15% |
| failed_2 = True | 14 | 7% |
| smt = False | 80 | 12% |
| smt = True | 2 | 50% |
| h1 = green | 41 | 5% |
| h1 = red | 41 | 22% |
| h4 = green | 39 | 3% |
| h4 = red | 43 | 23% |

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
| All | 44 | 3 / 8 / 13 |
| window = W1 | 29 | 5 / 9 / 14 |
| window = W2 | 15 | 2 / 5 / 8 |
| direction = calls | 24 | 5 / 8 / 13 |
| direction = puts | 20 | 2 / 6 / 12 |
| W1 calls | 16 | 7 / 10 / 14 |
| W1 puts | 13 | 1 / 9 / 19 |
| W2 calls | 8 | 1 / 5 / 9 |
| W2 puts | 7 | 2 / 5 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 25% | 7% | 5% | 2% |
| W1 calls | 31% | 0% | 0% | 0% |
| W1 puts | 31% | 23% | 15% | 8% |
| W2 calls | 25% | 0% | 0% | 0% |
| W2 puts | 0% | 0% | 0% | 0% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 10 | 20% |
| pool_swept = 13:30 candle low | 9 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 6 | 17% |
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
| failed_2 = False | 36 | 8% |
| failed_2 = True | 8 | 0% |
| smt = False | 42 | 7% |
| smt = True | 2 | 0% |
| h1 = green | 23 | 0% |
| h1 = red | 21 | 14% |
| h4 = green | 22 | 0% |
| h4 = red | 22 | 14% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
