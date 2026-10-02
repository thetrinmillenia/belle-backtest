# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-01.

## 5 minute signals

Signals: 86 (8.8 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 86 | 3 / 8 / 12 |
| window = W1 | 41 | 3 / 9 / 16 |
| window = W2 | 45 | 2 / 7 / 11 |
| direction = calls | 36 | 2 / 8 / 11 |
| direction = puts | 50 | 4 / 8 / 12 |
| W1 calls | 19 | 7 / 9 / 13 |
| W1 puts | 22 | 3 / 8 / 17 |
| W2 calls | 17 | 0 / 4 / 9 |
| W2 puts | 28 | 5 / 8 / 11 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 27% | 10% | 3% | 3% |
| W1 calls | 32% | 5% | 0% | 0% |
| W1 puts | 36% | 27% | 9% | 9% |
| W2 calls | 18% | 0% | 0% | 0% |
| W2 puts | 21% | 7% | 4% | 4% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 11% |
| pool_swept = 13:30 candle low | 4 | 0% |
| pool_swept = 9:30 open | 2 | 50% |
| pool_swept = bearish FVG CE | 15 | 20% |
| pool_swept = bearish order block opening | 5 | 0% |
| pool_swept = bullish FVG CE | 13 | 0% |
| pool_swept = bullish order block opening | 3 | 0% |
| pool_swept = equal highs | 5 | 60% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 16 | 0% |
| pool_swept = swing high | 5 | 0% |
| pool_swept = swing low | 5 | 20% |
| with_4h_bias = False | 28 | 4% |
| with_4h_bias = True | 58 | 14% |
| confirmed_next_candle = False | 34 | 0% |
| confirmed_next_candle = True | 52 | 17% |
| failed_2 = False | 68 | 13% |
| failed_2 = True | 18 | 0% |
| smt = False | 82 | 10% |
| smt = True | 4 | 25% |
| h1 = green | 44 | 7% |
| h1 = red | 42 | 14% |
| h4 = green | 47 | 6% |
| h4 = red | 39 | 15% |

**Answer key check**

- 2026-09-30 SPX 7670p: W2 entry 15:35 at 9:30 open, moved 37.81 pts | WRONG WAY: calls 14:15
- 2026-10-01 SPX 7675p: W2 entry 15:55 at swing high, moved 10.09 pts | WRONG WAY: calls 14:25
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts | WRONG WAY: puts 15:35

## 15 minute signals

Signals: 49 (6.6 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 49 | 2 / 6 / 14 |
| window = W1 | 31 | 4 / 9 / 14 |
| window = W2 | 18 | 2 / 3 / 7 |
| direction = calls | 21 | 2 / 8 / 13 |
| direction = puts | 28 | 3 / 6 / 14 |
| W1 calls | 13 | 5 / 12 / 14 |
| W1 puts | 18 | 2 / 8 / 18 |
| W2 calls | 8 | 1 / 1 / 6 |
| W2 puts | 10 | 3 / 5 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 31% | 10% | 8% | 8% |
| W1 calls | 38% | 8% | 8% | 8% |
| W1 puts | 33% | 17% | 11% | 11% |
| W2 calls | 25% | 0% | 0% | 0% |
| W2 puts | 20% | 10% | 10% | 10% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 13 | 15% |
| pool_swept = 13:30 candle low | 7 | 0% |
| pool_swept = 9:30 open | 2 | 0% |
| pool_swept = bearish FVG CE | 7 | 0% |
| pool_swept = bearish order block opening | 1 | 0% |
| pool_swept = bullish FVG CE | 4 | 25% |
| pool_swept = bullish order block opening | 2 | 0% |
| pool_swept = midnight open | 3 | 67% |
| pool_swept = rejection block | 6 | 0% |
| pool_swept = swing high | 1 | 0% |
| pool_swept = swing low | 3 | 0% |
| with_4h_bias = False | 19 | 0% |
| with_4h_bias = True | 30 | 17% |
| confirmed_next_candle = False | 19 | 16% |
| confirmed_next_candle = True | 30 | 7% |
| failed_2 = False | 38 | 13% |
| failed_2 = True | 11 | 0% |
| smt = False | 47 | 11% |
| smt = True | 2 | 0% |
| h1 = green | 20 | 10% |
| h1 = red | 29 | 10% |
| h4 = green | 24 | 8% |
| h4 = red | 25 | 12% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED | WRONG WAY: calls 14:45
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:45
