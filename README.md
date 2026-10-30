# 🔔 Belle Bots

A small team of trading bots for **SPX and SPY 0DTE options**. One bot reads the chart and calls the trade, one paper trades it, one manages every open trade, one trades live with tight rules, and a few more keep the records so the team learns every day.

> Educational project. Not financial advice. Options can lose 100% of what you pay. Paper results are not live results.

---

## 👯 Meet the team

| | Bot | What she does | When (ET) |
|---|---|---|---|
| 🔔 | **Belle** | Reads the chart and sends the alerts: the morning read, the afternoon read and every entry | all day |
| 🪙 | **Penny** | Paper trader. Buys the alert on a practice account | on each alert |
| ⭐ | **Stella** | Penny's manager. Babysits every open trade: the stop, the trims, the trail and the exit | until 15:59 |
| 🫒 | **Olive** | Watches the 30 minute opening range (ORH and ORL) on 15 minute candles | 10:00 to 12:15 |
| 🌿 | **Willow** | Watches for the afternoon stall break and its pullback entry | 14:00 to 15:55 |
| 🦪 | **Pearl** | Live trader. Same playbook as Penny with tighter rules. Off until switched on | W1 and EOD |
| 🐦‍⬛ | **Raven** | Shadow. Scores every alert Penny skipped, so we know which filters help | after the close |
| 📒 | **Nora** | Record keeper: daily recap, win and loss library, bot attendance | 16:00 |
| 📝 | **Harper** | Writes the daily review | 16:30 |

---

## 🗺️ How it fits together

```mermaid
flowchart LR
    TV["📈 TradingView<br/>Belle's chart alerts"] --> R["⚡ Relay<br/>(Vercel)"]
    VC["⏰ Vercel clock"] --> R
    R --> D["💬 Discord<br/>alerts and reads"]
    R --> P["🪙 Penny<br/>paper buy"]
    R --> PL["🦪 Pearl<br/>live buy (when on)"]
    R --> SH["🐦‍⬛ Raven<br/>skipped alerts"]
    VC --> O["🫒 Olive<br/>morning"]
    VC --> S["🌿 Willow<br/>afternoon"]
    O --> P
    S --> P
    P --> ST["⭐ Stella<br/>manages the trade"]
    PL --> ST
    ST --> D
    ST --> A["🏦 Alpaca<br/>orders"]
    A --> N["📒 Nora + 📝 Harper<br/>after the close"]
```

---

## 📐 The rules in one place

| Rule | Penny (paper) | Pearl (live) |
|---|---|---|
| Contract | 1 SPX + 3 SPY | 1 SPX, ask $1.20 or less |
| Starting stop | 43% of the premium | 30% of the premium |
| Breakeven | at +60% | at +30% |
| Morning trail | 30% below the best price after +100% | same |
| EOD trail | 20% below the best from +30%, 15% from +100%, checked every 2 seconds | same |
| EOD trims (SPY) | 1 at +100%, 1 at +200%, the last one rides | (1 contract, rides the trail) |
| Day limits | none | 1 loss and done, done at -$40 or at +$200 |
| Last entry | 15:55 | 15:55 (EOD) |
| Everything out | 15:59 | 15:59 |

---

## 📊 Results

Every bot writes plain CSV files you can open in any spreadsheet:

| File | What is in it |
|---|---|
| `results/paper_trades.csv` | every Penny trade: entry, exit, best price, why |
| `results/or_breaks.csv` | Olive: size and volume of every opening range break |
| `results/shadow_scores.csv` | Raven: what the skipped alerts would have done |
| `results/pearl_trades.csv` | Pearl's live trades |
| `results/bot_health.csv` | Nora's check that every bot started on time |
| `results/*_library.csv` | the win and loss libraries the team learns from |

---

## ▶️ How to run it

1. **Copy the repo** and connect the `belle-cron` folder to a free Vercel project.
2. **Add your own keys as secrets.** Keys never go in the code:
   - GitHub, under Settings, then Secrets and variables, then Actions: `ALPACA_KEY_ID`, `ALPACA_SECRET_KEY`, `DISCORD_WEBHOOK_URL`
   - Vercel: the same Alpaca keys and webhook, plus `GITHUB_TOKEN`, `RELAY_KEY` and `CRON_SECRET`
   - Pearl only: `PEARL_KEY_ID`, `PEARL_SECRET_KEY`, `PEARL_WEBHOOK_URL`, and the variable `PEARL_ON` set to `true` when you are ready
3. **Point your TradingView alerts** at the relay link.
4. **Test first.** Every trading bot has a replay: open the Actions tab, pick the bot, press **Run workflow** and type a past date. Replays print to the log only: no orders, no Discord.

A code check runs on every change, so a broken file shows a red X before the market ever sees it.

---

<sub>Made with care for SPX 0DTE traders. Built on Alpaca, TradingView, Vercel, GitHub Actions and Discord.</sub>
