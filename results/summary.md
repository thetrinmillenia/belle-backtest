# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-30.

## 5 minute signals

Signals: 77 (8.2 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 77 | 2 / 6 / 12 |
| window = W1 | 41 | 2 / 8 / 16 |
| window = W2 | 36 | 2 / 5 / 9 |
| direction = calls | 40 | 2 / 6 / 10 |
| direction = puts | 37 | 2 / 6 / 12 |
| W1 calls | 21 | 2 / 8 / 16 |
| W1 puts | 20 | 4 / 8 / 18 |
| W2 calls | 19 | 2 / 5 / 8 |
| W2 puts | 17 | 2 / 6 / 9 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 25% | 16% | 6% | 5% |
| W1 calls | 33% | 14% | 0% | 0% |
| W1 puts | 40% | 35% | 20% | 15% |
| W2 calls | 11% | 0% | 0% | 0% |
| W2 puts | 12% | 12% | 6% | 6% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 2 | 0% |
| pool_swept = 13:30 candle low | 5 | 0% |
| pool_swept = 9:30 open | 5 | 20% |
| pool_swept = bearish FVG CE | 12 | 33% |
| pool_swept = bearish order block opening | 6 | 33% |
| pool_swept = bullish FVG CE | 14 | 7% |
| pool_swept = bullish order block opening | 7 | 0% |
| pool_swept = equal highs | 2 | 50% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 17 | 12% |
| pool_swept = swing high | 2 | 0% |
| pool_swept = swing low | 1 | 100% |
| with_4h_bias = False | 29 | 14% |
| with_4h_bias = True | 48 | 17% |
| confirmed_next_candle = False | 33 | 6% |
| confirmed_next_candle = True | 44 | 23% |
| failed_2 = False | 65 | 18% |
| failed_2 = True | 12 | 0% |
| smt = False | 75 | 15% |
| smt = True | 2 | 50% |
| h1 = green | 40 | 5% |
| h1 = red | 37 | 27% |
| h4 = green | 36 | 3% |
| h4 = red | 41 | 27% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 42 (5.8 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 42 | 4 / 7 / 12 |
| window = W1 | 27 | 5 / 8 / 14 |
| window = W2 | 15 | 2 / 5 / 7 |
| direction = calls | 24 | 5 / 8 / 13 |
| direction = puts | 18 | 2 / 5 / 11 |
| W1 calls | 16 | 6 / 8 / 13 |
| W1 puts | 11 | 3 / 9 / 20 |
| W2 calls | 8 | 3 / 7 / 9 |
| W2 puts | 7 | 2 / 5 / 6 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 21% | 7% | 5% | 2% |
| W1 calls | 25% | 0% | 0% | 0% |
| W1 puts | 36% | 27% | 18% | 9% |
| W2 calls | 12% | 0% | 0% | 0% |
| W2 puts | 0% | 0% | 0% | 0% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 8 | 25% |
| pool_swept = 13:30 candle low | 9 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 5 | 20% |
| pool_swept = bearish order block opening | 2 | 0% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = bullish order block opening | 1 | 0% |
| pool_swept = midnight open | 2 | 0% |
| pool_swept = rejection block | 5 | 0% |
| pool_swept = swing low | 3 | 0% |
| with_4h_bias = False | 17 | 0% |
| with_4h_bias = True | 25 | 12% |
| confirmed_next_candle = False | 13 | 8% |
| confirmed_next_candle = True | 29 | 7% |
| failed_2 = False | 35 | 9% |
| failed_2 = True | 7 | 0% |
| smt = False | 40 | 8% |
| smt = True | 2 | 0% |
| h1 = green | 23 | 0% |
| h1 = red | 19 | 16% |
| h4 = green | 22 | 0% |
| h4 = red | 20 | 15% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
