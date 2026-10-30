"""HARPER'S WEEKLY REVIEW (Oct 29 2026). Runs in Nora's job after the close, on Fridays only (FORCE=1 runs it any day).
Read only, PAPER account. No Discord. Writes results/harper/weekly-YYYY-MM-DD.md and results/harper/rule_candidates.csv.

Every Penny trade since the start is tagged with its entry context (window, minute, side, above or below PDC,
inside or outside the 2 PM candle, first trade of the day, after a loss, day tags such as FOMC / earnings / range day).
For each tag: trades, wins, dollars. A tag with 8+ trades whose win rate is 20+ points away from the rest becomes a
rule candidate, replayed on all history ("skip it" = dollars saved or lost, and the winners it would have blocked).
Harper never changes code, orders or alerts. Rules change only with a yes.
"""
import csv
import datetime as dt
import os
import sys
from collections import defaultdict, deque
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
TRADE = "https://paper-api.alpaca.markets"
DATA = "https://data.alpaca.markets"
H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"].strip(), "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"].strip()}
START = "2026-10-14"
now = dt.datetime.now(ET)
if os.environ.get("FORCE") != "1" and (now.weekday() != 4 or now.hour < 16):
    print("Harper weekly: Fridays after 16:00 ET only")
    sys.exit(0)


def et(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(ET)


# 1) Penny's trades: buys of the same side within 5 minutes are one trade (SPX + SPY), P/L matched first in first out
orders, after = [], f"{START}T00:00:00Z"
while True:
    page = requests.get(f"{TRADE}/v2/orders", headers=H, timeout=30,
                        params={"status": "closed", "after": after, "direction": "asc", "limit": 500}).json()
    page = [o for o in page if isinstance(o, dict)]
    orders += page
    if len(page) < 500:
        break
    after = page[-1]["submitted_at"]
fills = sorted([o for o in orders if o.get("filled_at") and len(o.get("symbol", "")) > 15], key=lambda o: o["filled_at"])
lots, trades = defaultdict(deque), []
for o in fills:
    s, q, p, t = o["symbol"], float(o["filled_qty"]), float(o["filled_avg_price"]), et(o["filled_at"])
    if o["side"] == "buy":
        g = next((g for g in reversed(trades) if g["day"] == t.date() and g["cp"] == s[-9] and (t - g["t"]).total_seconds() < 300), None)
        if not g:
            g = {"day": t.date(), "t": t, "cp": s[-9], "pl": 0.0, "cid": o.get("client_order_id", "")}
            trades.append(g)
        lots[s].append([q, p, g])
    else:
        while q > 0 and lots[s]:
            lot = lots[s][0]
            m = min(q, lot[0])
            lot[2]["pl"] += m * (p - lot[1]) * 100
            lot[0] -= m
            q -= m
            if lot[0] <= 0:
                lots[s].popleft()

# 2) context from SPY bars and the day tags
days = sorted({g["day"] for g in trades})
daily = requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, timeout=30,
                     params={"timeframe": "1Day", "start": str(days[0] - dt.timedelta(days=7)), "end": str(days[-1]), "feed": "iex"}).json().get("bars") or []   # iex: sip refuses the latest day on the free plan
closes = {et(b["t"]).date(): b["c"] for b in daily}
intraday = defaultdict(list)
for d in days:
    b = requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, timeout=30,
                     params={"timeframe": "5Min", "start": f"{d}T13:00:00Z", "end": f"{d}T21:00:00Z", "feed": "iex", "limit": 1000}).json().get("bars") or []
    intraday[d] = [(et(x["t"]).hour * 60 + et(x["t"]).minute, x) for x in b]
day_tags = {}
if os.path.exists("data/day_tags.csv"):
    with open("data/day_tags.csv") as fh:
        day_tags = {r["date"]: r["tags"] for r in csv.DictReader(fh)}

by_day = defaultdict(list)
for g in trades:
    by_day[g["day"]].append(g)
for d, gs in by_day.items():
    prev = [k for k in closes if k < d]
    pdc = closes[max(prev)] if prev else None
    bars = intraday.get(d, [])
    two = [x for m, x in bars if 840 <= m < 900]
    h2, l2 = (max(x["h"] for x in two), min(x["l"] for x in two)) if two else (None, None)
    last_pl = None
    for i, g in enumerate(gs):
        m = g["t"].hour * 60 + g["t"].minute
        px = next((x["c"] for mm, x in reversed(bars) if mm + 5 <= m), None)
        win = "W1 morning" if m <= 750 else ("W3 EOD" if m >= 900 else "midday")
        side = "calls" if g["cp"] == "C" else "puts"
        tags = [win, f"{win} {side}", f"{m // 15 * 15 // 60:02d}:{m // 15 * 15 % 60:02d} ET entries"]
        if i == 0:
            tags.append("first trade of the day")
        if last_pl is not None and last_pl < 0:
            tags.append("after a loss")
        if px and pdc:
            tags.append(f"{side} {'above' if px > pdc else 'below'} PDC")
        if px and h2 and m >= 900:
            tags.append(f"W3 {side} " + ("above the 2 PM high" if px > h2 else ("below the 2 PM low" if px < l2 else "inside the 2 PM candle")))
        for tg in (day_tags.get(str(d), "") or "").split(";"):
            if tg.strip():
                tags.append("day: " + tg.strip())
        g["tags"] = tags
        last_pl = g["pl"]

# 3) stats per tag and rule candidates
stat = defaultdict(lambda: [0, 0, 0.0])
for g in trades:
    for tg in g["tags"]:
        s = stat[tg]
        s[0] += 1
        s[1] += g["pl"] > 0
        s[2] += g["pl"]
n_all = len(trades)
w_all = sum(1 for g in trades if g["pl"] > 0)
cands = []
for tg, (n, w, pl) in stat.items():
    rest_n, rest_w = n_all - n, w_all - w
    if n < 8 or rest_n < 8:
        continue
    gap = w / n - rest_w / rest_n
    if abs(gap) >= 0.20:
        blocked = sum(1 for g in trades if tg in g["tags"] and g["pl"] > 0)
        idea = f"skip {tg}" if gap < 0 else f"favor {tg}"
        cands.append([tg, idea, n, f"{w / n:.0%}", f"{rest_w / rest_n:.0%}", f"{-pl:+.0f}", blocked])
cands.sort(key=lambda c: -abs(float(c[5])))

# 4) write the weekly review
wk0 = (now - dt.timedelta(days=now.weekday())).date()
week = [g for g in trades if g["day"] >= wk0]
L = [f"# Harper's weekly review, week of {wk0:%b %d} (written {now:%a %b %d %H:%M} ET)", ""]
L += [f"Penny this week: {len(week)} trades, {sum(1 for g in week if g['pl'] > 0)} wins, ${sum(g['pl'] for g in week):+,.0f}",
      f"Since {START}: {n_all} trades, {w_all} wins, ${sum(g['pl'] for g in trades):+,.0f}", ""]
L += ["## By day", "", "| Day | Trades | Wins | P/L | Day tags |", "|---|---|---|---|---|"]
for d in sorted({g["day"] for g in week}):
    gs = by_day[d]
    L.append(f"| {d:%a %m-%d} | {len(gs)} | {sum(1 for g in gs if g['pl'] > 0)} | ${sum(g['pl'] for g in gs):+,.0f} | {day_tags.get(str(d), '')} |")
L += ["", "## Entry timing, all trades since the start", "", "| Tag | Trades | Win rate | P/L |", "|---|---|---|---|"]
for tg, (n, w, pl) in sorted(stat.items(), key=lambda x: (-x[1][0], x[0])):
    if n >= 3:
        L.append(f"| {tg} | {n} | {w / n:.0%} | ${pl:+,.0f} |")
if os.path.exists("results/shadow_scores.csv"):
    with open("results/shadow_scores.csv") as fh:
        sh = [r for r in csv.DictReader(fh) if r["date"] >= str(wk0)]
    if sh:
        why = defaultdict(lambda: [0, 0])
        for r in sh:
            why[r["reason"]][0] += 1
            why[r["reason"]][1] += int(r["pl"])
        L += ["", "## Skipped alerts this week (Shay)", "", "| Why skipped | Contracts | Would have made |", "|---|---|---|"]
        L += [f"| {k} | {v[0]} | ${v[1]:+,} |" for k, v in sorted(why.items())]
L += ["", "## Rule candidates (8+ trades, win rate 20+ points away from the rest)", ""]
if cands:
    L += ["| Tag | Idea | Trades | Win rate | Rest | Skipping it would change P/L by | Winners it would block |", "|---|---|---|---|---|---|---|"]
    L += [f"| {c[0]} | {c[1]} | {c[2]} | {c[3]} | {c[4]} | ${c[5]} | {c[6]} |" for c in cands[:10]]
else:
    L.append("None yet. Most tags need more trades.")
L += ["", "Harper never changes code, orders or alerts. A rule changes only with a yes."]
os.makedirs("results/harper", exist_ok=True)
path = f"results/harper/weekly-{now:%Y-%m-%d}.md"
with open(path, "w") as fh:
    fh.write("\n".join(L) + "\n")
with open("results/harper/rule_candidates.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["tag", "idea", "trades", "win_rate", "rest_win_rate", "pl_change_if_skipped", "winners_blocked", "written"])
    for c in cands:
        w.writerow(c + [f"{now:%Y-%m-%d}"])
print("\n".join(L))
