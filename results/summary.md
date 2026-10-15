# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-15.

## 5 minute signals

Signals: 79 (8.6 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 79 | 2 / 7 / 11 |
| window = W1 | 42 | 3 / 8 / 15 |
| window = W2 | 37 | 2 / 6 / 8 |
| direction = calls | 35 | 2 / 7 / 10 |
| direction = puts | 44 | 3 / 7 / 11 |
| W1 calls | 19 | 4 / 8 / 13 |
| W1 puts | 23 | 4 / 7 / 16 |
| W2 calls | 16 | 0 / 5 / 7 |
| W2 puts | 21 | 2 / 7 / 9 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 22% | 11% | 4% | 4% |
| W1 calls | 32% | 11% | 0% | 0% |
| W1 puts | 35% | 22% | 9% | 9% |
| W2 calls | 6% | 0% | 0% | 0% |
| W2 puts | 10% | 10% | 5% | 5% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 3 | 0% |
| pool_swept = 13:30 candle low | 2 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 16 | 19% |
| pool_swept = bearish order block opening | 8 | 25% |
| pool_swept = bullish FVG CE | 14 | 7% |
| pool_swept = bullish order block opening | 4 | 0% |
| pool_swept = equal highs | 2 | 50% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 17 | 6% |
| pool_swept = swing high | 3 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 28 | 11% |
| with_4h_bias = True | 51 | 12% |
| confirmed_next_candle = False | 31 | 3% |
| confirmed_next_candle = True | 48 | 17% |
| failed_2 = False | 66 | 14% |
| failed_2 = True | 13 | 0% |
| smt = False | 76 | 11% |
| smt = True | 3 | 33% |
| h1 = green | 40 | 5% |
| h1 = red | 39 | 18% |
| h4 = green | 41 | 2% |
| h4 = red | 38 | 21% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 40 (6.1 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 40 | 4 / 7 / 13 |
| window = W1 | 26 | 5 / 10 / 14 |
| window = W2 | 14 | 2 / 4 / 7 |
| direction = calls | 19 | 5 / 8 / 13 |
| direction = puts | 21 | 2 / 6 / 11 |
| W1 calls | 13 | 8 / 12 / 14 |
| W1 puts | 13 | 4 / 9 / 14 |
| W2 calls | 6 | 1 / 3 / 6 |
| W2 puts | 8 | 2 / 6 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 20% | 5% | 2% | 2% |
| W1 calls | 31% | 0% | 0% | 0% |
| W1 puts | 31% | 15% | 8% | 8% |
| W2 calls | 0% | 0% | 0% | 0% |
| W2 puts | 0% | 0% | 0% | 0% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 22% |
| pool_swept = 13:30 candle low | 8 | 0% |
| pool_swept = 9:30 open | 2 | 0% |
| pool_swept = bearish FVG CE | 8 | 0% |
| pool_swept = bearish order block opening | 1 | 0% |
| pool_swept = bullish FVG CE | 4 | 0% |
| pool_swept = bullish order block opening | 1 | 0% |
| pool_swept = midnight open | 2 | 0% |
| pool_swept = rejection block | 5 | 0% |
| with_4h_bias = False | 16 | 0% |
| with_4h_bias = True | 24 | 8% |
| confirmed_next_candle = False | 15 | 7% |
| confirmed_next_candle = True | 25 | 4% |
| failed_2 = False | 33 | 6% |
| failed_2 = True | 7 | 0% |
| smt = False | 38 | 5% |
| smt = True | 2 | 0% |
| h1 = green | 19 | 0% |
| h1 = red | 21 | 10% |
| h4 = green | 20 | 0% |
| h4 = red | 20 | 10% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
