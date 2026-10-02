# Belle backtest results

Data: Yahoo Finance, last 60d. Run 2026-10-01.

## 5 minute signals

Signals: 81 (8.4 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 81 | 3 / 8 / 13 |
| window = W1 | 39 | 6 / 10 / 16 |
| window = W2 | 42 | 2 / 6 / 10 |
| direction = calls | 34 | 2 / 7 / 11 |
| direction = puts | 47 | 5 / 9 / 14 |
| W1 calls | 17 | 7 / 10 / 13 |
| W1 puts | 22 | 5 / 11 / 21 |
| W2 calls | 17 | 2 / 4 / 8 |
| W2 puts | 25 | 5 / 8 / 11 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 28% | 12% | 5% | 5% |
| W1 calls | 35% | 6% | 0% | 0% |
| W1 puts | 45% | 32% | 14% | 14% |
| W2 calls | 12% | 0% | 0% | 0% |
| W2 puts | 20% | 8% | 4% | 4% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 6 | 17% |
| pool_swept = 13:30 candle low | 2 | 0% |
| pool_swept = 9:30 open | 2 | 50% |
| pool_swept = bearish FVG CE | 15 | 27% |
| pool_swept = bearish order block opening | 6 | 0% |
| pool_swept = bullish FVG CE | 14 | 0% |
| pool_swept = bullish order block opening | 3 | 0% |
| pool_swept = equal highs | 5 | 60% |
| pool_swept = equal lows | 4 | 0% |
| pool_swept = rejection block | 17 | 0% |
| pool_swept = swing high | 4 | 0% |
| pool_swept = swing low | 3 | 33% |
| with_4h_bias = False | 22 | 5% |
| with_4h_bias = True | 59 | 15% |
| confirmed_next_candle = False | 33 | 0% |
| confirmed_next_candle = True | 48 | 21% |
| failed_2 = False | 66 | 15% |
| failed_2 = True | 15 | 0% |
| smt = False | 79 | 11% |
| smt = True | 2 | 50% |
| h1 = green | 41 | 7% |
| h1 = red | 40 | 18% |
| h4 = green | 43 | 7% |
| h4 = red | 38 | 18% |

**Answer key check**

- 2026-09-30 SPX 7670p: W1 entry 14:20 at bearish FVG CE, moved 46.35 pts, W2 entry 15:35 at 9:30 open, moved 37.81 pts
- 2026-10-01 SPX 7675p: W2 entry 15:55 at swing high, moved 10.09 pts | WRONG WAY: calls 14:25
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:10, puts 15:30
- 2026-09-29 SPX calls: W1 entry 14:05 at equal lows, moved 16.18 pts

## 15 minute signals

Signals: 41 (6.4 per week). Entry = the sweep candle's close.

**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**

| Group | Signals | Move |
| --- | --- | --- |
| All | 41 | 3 / 7 / 14 |
| window = W1 | 25 | 5 / 11 / 15 |
| window = W2 | 16 | 2 / 4 / 8 |
| direction = calls | 17 | 4 / 8 / 14 |
| direction = puts | 24 | 3 / 6 / 13 |
| W1 calls | 10 | 8 / 12 / 15 |
| W1 puts | 15 | 3 / 9 / 17 |
| W2 calls | 7 | 1 / 2 / 8 |
| W2 puts | 9 | 3 / 5 / 7 |

**Strike went in the money by 15:59, by distance out of the money**

| Group | 10 pts | 15 pts | 20 pts | 25 pts |
| --- | --- | --- | --- | --- |
| All | 29% | 12% | 10% | 10% |
| W1 calls | 40% | 10% | 10% | 10% |
| W1 puts | 33% | 20% | 13% | 13% |
| W2 calls | 29% | 0% | 0% | 0% |
| W2 puts | 11% | 11% | 11% | 11% |

**Score notes (never block a trade): share reaching ITM at 15 pts**

| Note | Signals | ITM at 15 pts |
| --- | --- | --- |
| pool_swept = 13:30 candle high | 9 | 22% |
| pool_swept = 13:30 candle low | 5 | 0% |
| pool_swept = 9:30 open | 2 | 0% |
| pool_swept = bearish FVG CE | 7 | 0% |
| pool_swept = bearish order block opening | 1 | 0% |
| pool_swept = bullish FVG CE | 4 | 25% |
| pool_swept = bullish order block opening | 2 | 0% |
| pool_swept = midnight open | 3 | 67% |
| pool_swept = rejection block | 6 | 0% |
| pool_swept = swing high | 1 | 0% |
| pool_swept = swing low | 1 | 0% |
| with_4h_bias = False | 12 | 0% |
| with_4h_bias = True | 29 | 17% |
| confirmed_next_candle = False | 15 | 20% |
| confirmed_next_candle = True | 26 | 8% |
| failed_2 = False | 33 | 15% |
| failed_2 = True | 8 | 0% |
| smt = False | 41 | 12% |
| h1 = green | 16 | 12% |
| h1 = red | 25 | 12% |
| h4 = green | 19 | 11% |
| h4 = red | 22 | 14% |

**Answer key check**

- 2026-09-30 SPX 7670p: NOT FLAGGED
- 2026-10-01 SPX 7675p: NOT FLAGGED | WRONG WAY: calls 14:30
- 2026-09-26 SPX puts: NOT FLAGGED
- 2026-09-18 SPX calls: NOT FLAGGED | WRONG WAY: puts 14:15, puts 15:30
- 2026-09-29 SPX calls: NOT FLAGGED | WRONG WAY: puts 15:45
