# Belle system map

SPX 0DTE alerts, paper trading (Penny), live trading (Pearl, off until Titi turns it on) and the daily learning loop.
Times are ET with CT in brackets. Penny is Alpaca PAPER only. Pearl is the only code that can touch the live account.

## Who starts what

| Starter | What it starts |
|---|---|
| TradingView alert to the Vercel relay (`belle-cron/api/alert.js`) | Belle's entry post, Penny's paper buy, Penny manager, Pearl (Window 1 and EOD), Shadow (skipped alerts) |
| Vercel clock (`belle-cron/vercel.json`) | Belle morning 06:00 (05:00), Belle afternoon 13:00 (12:00), ORB in the 09:00 (08:00) hour, Stall in the 13:00 (12:00) hour, Belle EOD, Nora and Harper in the 16:00 (15:00) hour |
| GitHub clock | Backup only. It often starts jobs hours late, and a late start simply exits |
| A push to the repo | Code check (every bot compiles, the relay loads) |

## Bots

| File | Job | Window | Discord |
|---|---|---|---|
| `belle-cron/api/alert.js` | Relay: reads Belle's alert, buys for Penny, starts the manager, Pearl and Shadow | Window 1 10:00 to 12:30 (09:00 to 11:30), EOD 15:00 to 15:53 (14:00 to 14:53). Window 2 off | Belle entry post |
| `bots/belle_manage.py` | Penny manager: rule E stops, fib targets, out at 15:59 (14:59) | per trade | Penny updates |
| `bots/belle_or.py` | ORB: 30 min opening range on 15m, both directions | entries 10:00 to 12:15 (09:00 to 11:15) | entry post |
| `bots/belle_stall.py` | Stall break, OTE entry, EOD stall check, reversal watch | 14:00 to 15:50 (13:00 to 14:50) | stall posts |
| `bots/penny_common.py` | Shared code for ORB and stall (ratio, contract pick, paper orders, manager and Pearl starts) | | |
| `bots/pearl.py` | LIVE bot: 1 SPX contract, ask $1.50 or less, 1 loss and done. OFF unless `PEARL_ON` is `true` | W1, stall, EOD | Pearl channel |
| `bots/shadow.py` | Records every alert Penny skips, scores it after the close (entry, highest, heat, rule E) | | none |
| `bots/nora.py`, `bots/nora_learn.py` | Daily and weekly recap, win and loss library | after the close | recap |
| `bots/harper.py` | Daily review doc | after the close | none |
| `bots/belle.py`, `bots/belle_drafts.py` | Belle reads and the morning drafts | morning, afternoon, EOD | reads |
| `bots/stop_bt2.py`, `bots/color_bt.py` | Read only backtests | on demand | none |

## Results

`results/` holds the trade logs: Penny's paper trades, Nora's libraries, `or_breaks.csv` (ORB break size and volume),
`shadow_signals.csv` and `shadow_trades.csv` (alerts Penny skipped), `pearl_trades.csv` (live). `data/` holds Titi's
own trades and lessons.

## Testing

Every bot that trades has a replay: Run workflow with a past date. Replays print to the GitHub log only:
no orders, no Discord. Pearl has `dry = 1`.

## Secrets (Titi adds these herself, never in code)

Alpaca paper keys, Discord webhooks, `PEARL_KEY_ID`, `PEARL_SECRET_KEY`, `PEARL_WEBHOOK_URL`, and the variable `PEARL_ON`.

## Original EOD sweep backtest (backtest.yml)

Free backtest of the Trin Millenia EOD liquidity sweep method on SPX 0DTE.

## What it tests

1. Marks ES liquidity pools: PDH, PDL, midnight open, 9:30 open, overnight high and low, the 13:30 candle high and low, and today's swing highs and lows.
2. Window 1 (14:00 to 14:50 ET) and Window 2 (15:30 to 15:55 ET) only.
3. The signal is the liquidity sweep: a candle trades through a pool and closes back inside it. Entry at that candle's close, stop at its extreme.
4. A second trade in the same window is allowed if it points the other way.
5. It measures how far SPX moved in the trade's favour before 15:59, and whether strikes 10, 15, 20 and 25 points out of the money went in the money.

Score notes (never block a trade): CISD within 3 bars, failed 2 (Strat shooter or hammer), ES versus NQ SMT, 1H and 4H candle colour.

Tested on the 5 minute and the 15 minute separately. Data: free Yahoo Finance, about the last 60 days.

## How to run it

Actions tab, then **Belle backtest**, then **Run workflow**. It also runs every weekday after the close. Results land in `results/summary.md` and `results/signals_5m.csv` / `results/signals_15m.csv`. `results/history.csv` keeps one row per day forever, so results can be compared over time.

## Change a setting

Edit `config.py` (windows, strike distance, swing size). Add real trades to `answer_key.csv` so the report checks whether the backtest flagged them.

Education only, not financial advice.
