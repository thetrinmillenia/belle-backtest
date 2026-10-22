# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-21.

## 5 minute signals

Signals: 78 (8.5 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 78 | 2 / 7 / 11 |
| window = W1 | 43 | 3 / 9 / 16 |
| window = W2 | 35 | 2 / 5 / 8 |
| direction = calls | 35 | 1 / 5 / 10 |
| direction = puts | 43 | 3 / 7 / 12 |
| W1 calls | 19 | 2 / 8 / 13 |
| W1 puts | 24 | 4 / 9 / 16 |
| W2 calls | 16 | 0 / 4 / 7 |
| W2 puts | 19 | 2 / 6 / 10 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 24% | 14% | 6% | 5% |
| W1 calls | 32% | 11% | 0% | 0% |
| W1 puts | 42% | 29% | 17% | 12% |
| W2 calls | 6% | 0% | 0% | 0% |
| W2 puts | 11% | 11% | 5% | 5% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 2 | 0% |
| pool_swept = 13:30 candle low | 3 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 14 | 29% |
| pool_swept = bearish order block opening | 8 | 25% |
| pool_swept = bullish FVG CE | 13 | 8% |
| pool_swept = bullish order block opening | 5 | 0% |
| pool_swept = equal highs | 2 | 50% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 18 | 11% |
| pool_swept = swing high | 3 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 29 | 14% |
| with_4h_bias = True | 49 | 14% |
| confirmed_next_candle = False | 32 | 6% |
| confirmed_next_candle = True | 46 | 20% |
| failed_2 = False | 65 | 17% |
| failed_2 = True | 13 | 0% |
| smt = False | 75 | 13% |
| smt = True | 3 | 33% |
| h1 = green | 40 | 5% |
| h1 = red | 38 | 24% |
| h4 = green | 39 | 3% |
| h4 = red | 39 | 26% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 40 (5.9 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 40 | 3 / 7 / 13 |
| window = W1 | 27 | 5 / 9 / 14 |
| window = W2 | 13 | 2 / 4 / 7 |
| direction = calls | 21 | 4 / 8 / 13 |
| direction = puts | 19 | 2 / 7 / 12 |
| W1 calls | 15 | 7 / 8 / 14 |
| W1 puts | 12 | 3 / 10 / 20 |
| W2 calls | 6 | 1 / 3 / 6 |
| W2 puts | 7 | 2 / 5 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 20% | 8% | 5% | 2% |
| W1 calls | 27% | 0% | 0% | 0% |
| W1 puts | 33% | 25% | 17% | 8% |
| W2 calls | 0% | 0% | 0% | 0% |
| W2 puts | 0% | 0% | 0% | 0% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 22% |
| pool_swept = 13:30 candle low | 9 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 6 | 17% |
| pool_swept = bearish order block opening | 1 | 0% |
| pool_swept = bullish FVG CE | 5 | 0% |
| pool_swept = bullish order block opening | 1 | 0% |
| pool_swept = midnight open | 2 | 0% |
| pool_swept = rejection block | 4 | 0% |
| with_4h_bias = False | 16 | 0% |
| with_4h_bias = True | 24 | 12% |
| confirmed_next_candle = False | 14 | 7% |
| confirmed_next_candle = True | 26 | 8% |
| failed_2 = False | 33 | 9% |
| failed_2 = True | 7 | 0% |
| smt = False | 38 | 8% |
| smt = True | 2 | 0% |
| h1 = green | 21 | 0% |
| h1 = red | 19 | 16% |
| h4 = green | 21 | 0% |
| h4 = red | 19 | 16% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
