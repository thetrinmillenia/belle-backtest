# Belle Backtest

Free backtest of the Trin Millenia EOD liquidity sweep method on SPX 0DTE.

## What it tests

1. Marks ES liquidity pools: PDH, PDL, midnight open, 9:30 open, overnight high and low, the 13:30 candle high and low, and today's swing highs and lows.
2. Window 1 (14:00 to 14:50 ET) and Window 2 (15:30 to 15:55 ET) only. At most 2 trades a day, 1 per window.
3. Needs a sweep: a candle trades through a pool and closes back inside it.
4. Needs a CISD: a body close through the open of the first candle in the run into the sweep.
5. Entry at the CISD close. Stop at the sweep candle's extreme.
6. Option proxy: a strike 25 SPX points OTM. Did SPX reach the money by the close, and how far past the strike?

Score fields (never block a trade): failed 2 (Strat shooter or hammer), ES versus NQ SMT, 1H and 4H candle colour.

Tested on the 5 minute and the 15 minute separately. Data: free Yahoo Finance, about the last 60 days.

## How to run it

Actions tab, then **Belle backtest**, then **Run workflow**. It also runs every weekday after the close. Results land in `results/summary.md` and `results/signals_5m.csv` / `results/signals_15m.csv`.

## Change a setting

Edit `config.py` (windows, strike distance, swing size). Add real trades to `answer_key.csv` so the report checks whether the backtest flagged them.

Education only, not financial advice.
