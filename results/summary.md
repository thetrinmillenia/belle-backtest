# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-11-02.

## 5 minute signals

Signals: 76 (8.1 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 76 | 2 / 7 / 12 |
| window = W1 | 40 | 2 / 8 / 16 |
| window = W2 | 36 | 2 / 6 / 9 |
| direction = calls | 41 | 2 / 5 / 10 |
| direction = puts | 35 | 2 / 7 / 17 |
| W1 calls | 21 | 2 / 8 / 16 |
| W1 puts | 19 | 4 / 10 / 23 |
| W2 calls | 20 | 3 / 5 / 8 |
| W2 puts | 16 | 2 / 6 / 11 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 26% | 17% | 9% | 8% |
| W1 calls | 33% | 14% | 0% | 0% |
| W1 puts | 42% | 37% | 26% | 21% |
| W2 calls | 10% | 0% | 0% | 0% |
| W2 puts | 19% | 19% | 12% | 12% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 2 | 0% |
| pool_swept = 13:30 candle low | 5 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 13 | 38% |
| pool_swept = bearish order block opening | 5 | 20% |
| pool_swept = bullish FVG CE | 14 | 7% |
| pool_swept = bullish order block opening | 7 | 0% |
| pool_swept = equal highs | 2 | 50% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 17 | 18% |
| pool_swept = swing high | 2 | 0% |
| pool_swept = swing low | 1 | 100% |
| with_4h_bias = False | 27 | 15% |
| with_4h_bias = True | 49 | 18% |
| confirmed_next_candle = False | 31 | 6% |
| confirmed_next_candle = True | 45 | 24% |
| failed_2 = False | 63 | 19% |
| failed_2 = True | 13 | 8% |
| smt = False | 74 | 16% |
| smt = True | 2 | 50% |
| h1 = green | 40 | 5% |
| h1 = red | 36 | 31% |
| h4 = green | 35 | 3% |
| h4 = red | 41 | 29% |

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
| All | 42 | 4 / 7 / 13 |
| window = W1 | 26 | 5 / 9 / 15 |
| window = W2 | 16 | 2 / 6 / 8 |
| direction = calls | 23 | 5 / 8 / 13 |
| direction = puts | 19 | 2 / 5 / 15 |
| W1 calls | 15 | 6 / 8 / 14 |
| W1 puts | 11 | 3 / 9 / 20 |
| W2 calls | 8 | 3 / 7 / 9 |
| W2 puts | 8 | 2 / 5 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 24% | 10% | 7% | 5% |
| W1 calls | 27% | 0% | 0% | 0% |
| W1 puts | 36% | 27% | 18% | 9% |
| W2 calls | 12% | 0% | 0% | 0% |
| W2 puts | 12% | 12% | 12% | 12% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 8 | 25% |
| pool_swept = 13:30 candle low | 9 | 0% |
| pool_swept = 9:30 open | 3 | 0% |
| pool_swept = bearish FVG CE | 6 | 33% |
| pool_swept = bearish order block opening | 2 | 0% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = midnight open | 2 | 0% |
| pool_swept = rejection block | 5 | 0% |
| pool_swept = swing low | 3 | 0% |
| with_4h_bias = False | 16 | 0% |
| with_4h_bias = True | 26 | 15% |
| confirmed_next_candle = False | 12 | 8% |
| confirmed_next_candle = True | 30 | 10% |
| failed_2 = False | 34 | 9% |
| failed_2 = True | 8 | 12% |
| smt = False | 40 | 10% |
| smt = True | 2 | 0% |
| h1 = green | 22 | 0% |
| h1 = red | 20 | 20% |
| h4 = green | 21 | 0% |
| h4 = red | 21 | 19% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
