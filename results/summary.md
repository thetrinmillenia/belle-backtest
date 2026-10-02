# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-01.

## 5 minute signals

Signals: 85 (8.9 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 85 | 2 / 7 / 11 |
| window = W1 | 43 | 3 / 9 / 15 |
| window = W2 | 42 | 2 / 6 / 9 |
| direction = calls | 39 | 1 / 5 / 10 |
| direction = puts | 46 | 4 / 7 / 12 |
| W1 calls | 21 | 2 / 9 / 11 |
| W1 puts | 22 | 3 / 9 / 18 |
| W2 calls | 18 | 1 / 3 / 7 |
| W2 puts | 24 | 5 / 7 / 10 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 22% | 9% | 6% | 6% |
| W1 calls | 24% | 5% | 5% | 5% |
| W1 puts | 41% | 27% | 14% | 14% |
| W2 calls | 11% | 0% | 0% | 0% |
| W2 puts | 12% | 4% | 4% | 4% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 5 | 0% |
| pool_swept = 13:30 candle low | 1 | 0% |
| pool_swept = 9:30 open | 3 | 33% |
| pool_swept = bearish FVG CE | 14 | 36% |
| pool_swept = bearish order block opening | 7 | 0% |
| pool_swept = bullish FVG CE | 16 | 0% |
| pool_swept = bullish order block opening | 3 | 0% |
| pool_swept = equal highs | 2 | 50% |
| pool_swept = equal lows | 3 | 0% |
| pool_swept = rejection block | 26 | 4% |
| pool_swept = swing high | 3 | 0% |
| pool_swept = swing low | 2 | 0% |
| with_4h_bias = False | 32 | 9% |
| with_4h_bias = True | 53 | 9% |
| confirmed_next_candle = False | 43 | 0% |
| confirmed_next_candle = True | 42 | 19% |
| failed_2 = False | 65 | 9% |
| failed_2 = True | 20 | 10% |
| smt = False | 84 | 8% |
| smt = True | 1 | 100% |
| h1 = green | 41 | 2% |
| h1 = red | 44 | 16% |
| h4 = green | 43 | 2% |
| h4 = red | 42 | 17% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:00 at bearish FVG CE, moved 53.25 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: W2 entry 15:55 at swing high, moved 10.09 pts | WRONG WAY: calls 14:25
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:00, puts 15:35

## 15 minute signals

Signals: 42 (6.6 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 42 | 4 / 7 / 13 |
| window = W1 | 26 | 5 / 9 / 15 |
| window = W2 | 16 | 2 / 4 / 8 |
| direction = calls | 21 | 5 / 8 / 13 |
| direction = puts | 21 | 4 / 6 / 13 |
| W1 calls | 14 | 6 / 9 / 14 |
| W1 puts | 12 | 4 / 10 / 18 |
| W2 calls | 7 | 1 / 2 / 8 |
| W2 puts | 9 | 3 / 5 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 26% | 12% | 7% | 7% |
| W1 calls | 29% | 7% | 7% | 7% |
| W1 puts | 33% | 25% | 8% | 8% |
| W2 calls | 29% | 0% | 0% | 0% |
| W2 puts | 11% | 11% | 11% | 11% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 22% |
| pool_swept = 13:30 candle low | 6 | 0% |
| pool_swept = 9:30 open | 2 | 0% |
| pool_swept = bearish FVG CE | 5 | 20% |
| pool_swept = bearish order block opening | 1 | 0% |
| pool_swept = bullish FVG CE | 4 | 25% |
| pool_swept = bullish order block opening | 2 | 0% |
| pool_swept = midnight open | 2 | 50% |
| pool_swept = rejection block | 10 | 0% |
| pool_swept = swing high | 1 | 0% |
| with_4h_bias = False | 15 | 0% |
| with_4h_bias = True | 27 | 19% |
| confirmed_next_candle = False | 19 | 21% |
| confirmed_next_candle = True | 23 | 4% |
| failed_2 = False | 32 | 12% |
| failed_2 = True | 10 | 10% |
| smt = False | 42 | 12% |
| h1 = green | 18 | 6% |
| h1 = red | 24 | 17% |
| h4 = green | 21 | 5% |
| h4 = red | 21 | 19% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:15 at rejection block, moved 15.77 pts | WRONG WAY: puts 15:45
