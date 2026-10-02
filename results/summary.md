# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-02.

## 5 minute signals

Signals: 81 (8.8 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 81 | 2 / 7 / 12 |
| window = W1 | 40 | 5 / 9 / 16 |
| window = W2 | 41 | 2 / 6 / 9 |
| direction = calls | 40 | 1 / 7 / 9 |
| direction = puts | 41 | 5 / 9 / 16 |
| W1 calls | 20 | 5 / 9 / 11 |
| W1 puts | 20 | 5 / 11 / 18 |
| W2 calls | 20 | 0 / 3 / 8 |
| W2 puts | 21 | 5 / 7 / 11 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 26% | 12% | 5% | 5% |
| W1 calls | 25% | 5% | 0% | 0% |
| W1 puts | 45% | 35% | 15% | 15% |
| W2 calls | 10% | 0% | 0% | 0% |
| W2 puts | 24% | 10% | 5% | 5% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 3 | 0% |
| pool_swept = 13:30 candle low | 2 | 0% |
| pool_swept = 9:30 open | 4 | 25% |
| pool_swept = bearish FVG CE | 13 | 31% |
| pool_swept = bearish order block opening | 4 | 25% |
| pool_swept = bullish FVG CE | 17 | 6% |
| pool_swept = bullish order block opening | 2 | 0% |
| pool_swept = equal highs | 5 | 60% |
| pool_swept = equal lows | 5 | 0% |
| pool_swept = rejection block | 21 | 0% |
| pool_swept = swing high | 3 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 28 | 4% |
| with_4h_bias = True | 53 | 17% |
| confirmed_next_candle = False | 35 | 3% |
| confirmed_next_candle = True | 46 | 20% |
| failed_2 = False | 64 | 16% |
| failed_2 = True | 17 | 0% |
| smt = False | 79 | 11% |
| smt = True | 2 | 50% |
| h1 = green | 42 | 7% |
| h1 = red | 39 | 18% |
| h4 = green | 46 | 7% |
| h4 = red | 35 | 20% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:15, calls 15:50
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 39 (6.5 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 39 | 3 / 8 / 13 |
| window = W1 | 25 | 5 / 11 / 15 |
| window = W2 | 14 | 1 / 3 / 7 |
| direction = calls | 18 | 2 / 7 / 13 |
| direction = puts | 21 | 4 / 8 / 14 |
| W1 calls | 11 | 7 / 12 / 14 |
| W1 puts | 14 | 4 / 11 / 18 |
| W2 calls | 7 | 1 / 1 / 3 |
| W2 puts | 7 | 3 / 5 / 8 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 28% | 13% | 10% | 10% |
| W1 calls | 36% | 9% | 9% | 9% |
| W1 puts | 36% | 21% | 14% | 14% |
| W2 calls | 14% | 0% | 0% | 0% |
| W2 puts | 14% | 14% | 14% | 14% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 22% |
| pool_swept = 13:30 candle low | 6 | 0% |
| pool_swept = 9:30 open | 2 | 0% |
| pool_swept = bearish FVG CE | 5 | 0% |
| pool_swept = bearish order block opening | 1 | 0% |
| pool_swept = bullish FVG CE | 5 | 20% |
| pool_swept = bullish order block opening | 2 | 0% |
| pool_swept = midnight open | 3 | 67% |
| pool_swept = rejection block | 5 | 0% |
| pool_swept = swing high | 1 | 0% |
| with_4h_bias = False | 15 | 0% |
| with_4h_bias = True | 24 | 21% |
| confirmed_next_candle = False | 17 | 18% |
| confirmed_next_candle = True | 22 | 9% |
| failed_2 = False | 29 | 17% |
| failed_2 = True | 10 | 0% |
| smt = False | 39 | 13% |
| h1 = green | 17 | 12% |
| h1 = red | 22 | 14% |
| h4 = green | 20 | 10% |
| h4 = red | 19 | 16% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts
