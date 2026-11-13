"""HARPER'S WEEKLY REVIEW (Oct 29 2026). Runs in Nora's job after the close, on Fridays only (FORCE=1 runs it any day).
Read only, PAPER account. No Discord. Oct 31: day type and lunch type tags (range tracker), 4H MSS tags, walk-forward check. Writes results/harper/weekly-YYYY-MM-DD.md and results/harper/rule_candidates.csv.

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
            g = {"day": t.date(), "t": t, "cp": s[-9], "pl": 0.0, "cid": o.get("client_order_id", ""), "buys": []}
            trades.append(g)
        lots[s].append([q, p, g])
        g["buys"].append((s, q, p))
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
day_hl = {et(b["t"]).date(): (b["h"], b["l"]) for b in daily}
intraday = defaultdict(list)
hist5 = {}   # every regular hours 5m bar fetched for the day (6 days back), for the 1H structure at entry
for d in days:
    b = requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, timeout=30,
                     params={"timeframe": "5Min", "start": f"{d - dt.timedelta(days=6)}T13:00:00Z", "end": f"{d}T21:00:00Z", "feed": "iex",
                             "limit": 5000}).json().get("bars") or []
    b = [x for x in b if 570 <= et(x["t"]).hour * 60 + et(x["t"]).minute < 960]   # regular hours only
    e13 = e50 = e200 = None
    rows = []
    for x in b:   # EMAs 13 / 50 / 200 on 5m closes, carried across days
        c = x["c"]
        e13 = c if e13 is None else e13 + (c - e13) * 2 / 14
        e50 = c if e50 is None else e50 + (c - e50) * 2 / 51
        e200 = c if e200 is None else e200 + (c - e200) * 2 / 201
        x["e"] = (e13, e50, e200)
        if et(x["t"]).date() == d:
            rows.append((et(x["t"]).hour * 60 + et(x["t"]).minute, x))
    intraday[d] = rows
    hist5[d] = [(et(x["t"]), x) for x in b]
K = 10.03   # SPY to SPX points


def h1_structure(d, m):
    """1H trend at the entry (Nov 2): 1H candles from the 5m bars (09:30 based), closed before the entry.
    Returns (trend, flip level, continuation level) in SPY prices, or None."""
    cs = {}
    for t, x in hist5.get(d, []):
        mm = t.hour * 60 + t.minute
        if t.date() == d and mm + 5 > m:
            continue
        k = (t.date(), (mm - 570) // 60)
        if k not in cs:
            cs[k] = [x["h"], x["l"], x["c"], t.date() < d or (mm - 570) // 60 * 60 + 630 <= m]
        else:
            cs[k][0], cs[k][1], cs[k][2] = max(cs[k][0], x["h"]), min(cs[k][1], x["l"]), x["c"]
    g = [v for k, v in sorted(cs.items()) if v[3]]
    sh = sl = trend = None
    for j in range(len(g)):
        i = j - 2
        if i >= 2:
            if g[i][0] > max(g[i - 2][0], g[i - 1][0], g[i + 1][0], g[i + 2][0]):
                sh = g[i][0]
            if g[i][1] < min(g[i - 2][1], g[i - 1][1], g[i + 1][1], g[i + 2][1]):
                sl = g[i][1]
        if sl is not None and g[j][2] < sl and trend != "bearish":
            trend = "bearish"
        elif sh is not None and g[j][2] > sh and trend != "bullish":
            trend = "bullish"
    if trend is None:
        return None
    return trend, (sh if trend == "bearish" else sl), (sl if trend == "bearish" else sh)


def level_tags(d, m, cp):
    """Where the alert fired against the key levels (Titi, Nov 2: the levels are super important)."""
    side = "calls" if cp == "C" else "puts"
    prev = [k for k in day_hl if k < d]
    bars_d = intraday.get(d, [])
    px = next((x["c"] for mm, x in reversed(bars_d) if mm + 5 <= m), None)
    if not prev or px is None:
        return []
    pdh, pdl = day_hl[max(prev)]
    mid = (pdh + pdl) / 2
    tags = [f"level: {side} {'above' if px > mid else 'below'} the prior day 50%"]
    before = [x for mm, x in bars_d if mm + 5 <= m]
    if before and min(x["l"] for x in before) < pdl and px > pdl:
        tags.append(f"level: {side} after a PDL sweep (back above)")
    if before and max(x["h"] for x in before) > pdh and px < pdh:
        tags.append(f"level: {side} after a PDH sweep (back below)")
    if abs(px - pdl) * K <= 5:
        tags.append(f"level: {side} within 5 pts of the PDL")
    if abs(px - pdh) * K <= 5:
        tags.append(f"level: {side} within 5 pts of the PDH")
    st = h1_structure(d, m)
    if st:
        trend, flip, cont = st
        tags.append(f"level: {side} {'with' if (trend == 'bullish') == (cp == 'C') else 'against'} the 1H trend")
        if flip is not None and abs(px - flip) * K <= 5:
            tags.append(f"level: {side} within 5 pts of the 1H flip level")
        if cont is not None and abs(px - cont) * K <= 5:
            tags.append(f"level: {side} within 5 pts of the 1H continuation level")
    return tags


day_tags = {}
if os.path.exists("data/day_tags.csv"):
    with open("data/day_tags.csv") as fh:
        day_tags = {r["date"]: r["tags"] for r in csv.DictReader(fh)}
# daily ranges from the range tracker (Oct 31): day type, lunch type, 1h and 4h MSS
ranges = {}
if os.path.exists("data/day_ranges.csv"):
    with open("data/day_ranges.csv") as fh:
        ranges = {r["date"]: r for r in csv.DictReader(fh)}

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
        win = "W1 morning" if m <= 750 else ("W2 lunch" if m < 810 else ("W3" if m < 900 else "W4 EOD"))   # Nov 12 (Titi): four windows
        side = "calls" if g["cp"] == "C" else "puts"
        tags = [win, f"{win} {side}", f"{m // 15 * 15 // 60:02d}:{m // 15 * 15 % 60:02d} ET entries"]
        if i == 0:
            tags.append("first trade of the day")
        if last_pl is not None and last_pl < 0:
            tags.append("after a loss")
        if px and pdc:
            tags.append(f"{side} {'above' if px > pdc else 'below'} PDC")
        before = [x for mm, x in bars if mm + 5 <= m][-12:]
        if len(before) >= 6:
            crosses = sum(1 for a, b2 in zip(before, before[1:])
                          for k in range(3) if (a["c"] - a["e"][k]) * (b2["c"] - b2["e"][k]) < 0)
            e = before[-1]["e"]
            if crosses >= 3:
                tags.append("EMAs tangled (price crossed the 13/50/200 3+ times in the last hour)")
            elif e[0] > e[1] > e[2] or e[0] < e[1] < e[2]:
                tags.append("EMAs stacked (trend)")
        if px and h2 and m >= 900:
            tags.append(f"W3 {side} " + ("above the 2 PM high" if px > h2 else ("below the 2 PM low" if px < l2 else "inside the 2 PM candle")))
        tags += level_tags(d, m, g["cp"])
        rg = ranges.get(str(d), {})
        if rg.get("day_type"):
            tags.append("day type: " + rg["day_type"])
        if rg.get("lunch_type"):
            tags.append("lunch: " + rg["lunch_type"])
        prev_rg = ranges.get(max([k for k in ranges if k < str(d)], default=""), {})
        m4 = (prev_rg.get("mss_4h") or "").split(" ")[0]   # the 4H MSS known before the open
        if m4 in ("bullish", "bearish"):
            tags.append(f"{side} {'with' if (m4 == 'bullish') == (side == 'calls') else 'against'} the 4H MSS")
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

# 3a) walk-forward (Oct 31, from quants.md): does each candidate hold on data it never saw?
# First half of the trades (in time order) = where the idea was found; second half = the check.
order = sorted(trades, key=lambda g: g["t"])
half = len(order) // 2


def gap_in(gs, tg):
    a = [g for g in gs if tg in g["tags"]]
    b = [g for g in gs if tg not in g["tags"]]
    if len(a) < 4 or len(b) < 4:
        return None
    return sum(g["pl"] > 0 for g in a) / len(a) - sum(g["pl"] > 0 for g in b) / len(b)


for c in cands:
    g1, g2 = gap_in(order[:half], c[0]), gap_in(order[half:], c[0])
    holds = "too few trades" if g1 is None or g2 is None else ("yes" if g1 * g2 > 0 and abs(g2) >= 0.10 else "no")
    c += [f"{g1:+.0%}" if g1 is not None else "-", f"{g2:+.0%}" if g2 is not None else "-", holds]

# 3b) Window 3 exits: what Penny's trail got vs selling at the liquidity target (calls: the highest high since 13:00 ET,
# puts: the lowest low since 13:00 ET, both on SPY 5m before the entry). Same 50% starting stop. SPX contracts only.
w3rows = []
for g in trades:
    m = g["t"].hour * 60 + g["t"].minute
    spx = [b for b in g["buys"] if b[0].startswith("SPXW")]
    if m < 900 or not spx:
        continue
    sym, q, e = spx[0]
    bars = intraday.get(g["day"], [])
    aft = [x for mm, x in bars if 780 <= mm and mm + 5 <= m]
    if not aft:
        continue
    tgt = max(x["h"] for x in aft) if g["cp"] == "C" else min(x["l"] for x in aft)
    hit = next((mm for mm, x in bars if mm >= m and ((g["cp"] == "C" and x["h"] >= tgt) or (g["cp"] == "P" and x["l"] <= tgt))), None)
    ob = requests.get(f"{DATA}/v1beta1/options/bars", headers=H, timeout=30,
                      params={"symbols": sym, "timeframe": "1Min", "start": g["t"].isoformat(),
                              "end": g["t"].replace(hour=15, minute=59).isoformat(), "limit": 1000}).json().get("bars", {}).get(sym, [])
    if not ob:
        continue
    out, peak = None, e
    for x in ob:
        mm = et(x["t"]).hour * 60 + et(x["t"]).minute
        if x["l"] <= e * 0.5 and peak < e * 1.6:
            out = e * 0.5
            break
        peak = max(peak, x["h"])
        if hit is not None and mm >= hit:
            out = x["c"]
            break
    if out is None:
        out = ob[-1]["c"]
    w3rows.append((g["day"], f"{m // 60:02d}:{m % 60:02d}", sym[-9:], e, round(tgt * 10.03, 1), hit, round((out - e) * 100), round(g["pl"])))

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
lv_rows = sorted((tg, v) for tg, v in stat.items() if tg.startswith("level: "))
dt_rows = sorted((tg, v) for tg, v in stat.items() if tg.startswith(("day type: ", "lunch: ")) or "4H MSS" in tg)
if dt_rows:
    L += ["", "## By day type, lunch type and 4H MSS (all trades since the start)", "",
          "| Tag | Trades | Win rate | P/L |", "|---|---|---|---|"]
    L += [f"| {tg} | {n} | {w / n:.0%} | ${pl:+,.0f} |" for tg, (n, w, pl) in dt_rows]
if lv_rows:
    L += ["", "## By level (where Penny's trades fired, all trades since the start)", "",
          "| Level | Trades | Win rate | P/L |", "|---|---|---|---|"]
    L += [f"| {tg[7:]} | {n} | {w / n:.0%} | ${pl:+,.0f} |" for tg, (n, w, pl) in lv_rows]
if os.path.exists("results/shadow_scores.csv"):   # the same level tags for the alerts Raven scored (skipped by Penny)
    with open("results/shadow_scores.csv") as fh:
        sk = list(csv.DictReader(fh))
    lv_sk = defaultdict(lambda: [0, 0])
    for r in sk:
        try:
            d0 = dt.date.fromisoformat(r["date"])
            hh, mi = map(int, r["time_et"].split(":"))
            cp0 = "C" if r["side"] == "CALLS" else "P"
            for tg in level_tags(d0, hh * 60 + mi, cp0):
                lv_sk[tg][0] += 1
                lv_sk[tg][1] += int(float(r["pl"] or 0))
        except Exception:
            continue
    if lv_sk:
        L += ["", "## By level, skipped alerts (Raven)", "", "| Level | Contracts | Would have made |", "|---|---|---|"]
        L += [f"| {tg[7:]} | {v[0]} | ${v[1]:+,} |" for tg, v in sorted(lv_sk.items())]
# SPX hold time (Titi, Nov 3): the new exit from Nov 3 is built to hold for hours; the 1,000% moves took 2 to 4.5 hours
spx_lots, holds = defaultdict(deque), []
for o in fills:
    s_ = o["symbol"]
    if not s_.startswith("SPXW"):
        continue
    q_, p_, t_ = float(o["filled_qty"]), float(o["filled_avg_price"]), et(o["filled_at"])
    if o["side"] == "buy":
        spx_lots[s_].append([q_, p_, t_])
        continue
    while q_ > 0 and spx_lots[s_]:
        lot = spx_lots[s_][0]
        m_ = min(q_, lot[0])
        holds.append(((t_ - lot[2]).total_seconds() / 60, (p_ / lot[1] - 1) * 100, lot[2]))
        lot[0] -= m_
        q_ -= m_
        if lot[0] <= 0:
            spx_lots[s_].popleft()


def hold_row(lab, hs):
    if not hs:
        return f"| {lab} | 0 | | | |"
    ms = sorted(h[0] for h in hs)
    return f"| {lab} | {len(hs)} | {sum(ms) / len(ms):.0f} min | {ms[len(ms) // 2]:.0f} min | {ms[-1]:.0f} min |"


if holds:
    new_exit = dt.date(2026, 11, 3)
    L += ["", "## SPX hold time (Penny's SPX contract)", "", "| Group | Trades | Average | Median | Longest |", "|---|---|---|---|---|",
          hold_row("Before the new exit (to Nov 2)", [h for h in holds if h[2].date() < new_exit]),
          hold_row("New exit (from Nov 3)", [h for h in holds if h[2].date() >= new_exit]),
          hold_row("This week", [h for h in holds if h[2].date() >= wk0]),
          hold_row("This week, winners", [h for h in holds if h[2].date() >= wk0 and h[1] > 0])]
if os.path.exists("results/harper/vix_log.csv"):   # Nov 4 (Titi): VIX week
    with open("results/harper/vix_log.csv") as fh:
        vw = [r for r in csv.DictReader(fh) if r["date"] >= str(wk0)]
    if vw:
        L += ["", "## VIX week", "", "| Day | VIX1D | Priced | Actual | Used | Day type | Right |", "|---|---|---|---|---|---|---|"]
        for r in vw:
            d_ = dt.date.fromisoformat(r["date"])
            L.append(f"| {d_:%a} | {r['vix1d']} | {r['priced_pts']} pts | {r['actual_pts']} pts | {r['used_pct']}% | {r['day_type']} | {r['right']} of {r['alerts']} |")
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
        L += ["", "## Skipped alerts this week (Raven)", "", "| Why skipped | Contracts | Would have made |", "|---|---|---|"]
        L += [f"| {k} | {v[0]} | ${v[1]:+,} |" for k, v in sorted(why.items())]
if w3rows:
    L += ["", "## Window 3: Penny's real result vs selling at the liquidity target (SPX contract)", "",
          "| Day | In ET | Contract | Entry | Target (SPX approx) | Target hit ET | At target | Penny's trade (SPX + SPY) |", "|---|---|---|---|---|---|---|---|"]
    for r in w3rows:
        hit = f"{r[5] // 60:02d}:{r[5] % 60:02d}" if r[5] is not None else "not hit"
        L.append(f"| {r[0]:%m-%d} | {r[1]} | {r[2]} | {r[3]:.2f} | {r[4]} | {hit} | ${r[6]:+,} | ${r[7]:+,} |")
    L.append(f"Total at target: ${sum(r[6] for r in w3rows):+,}")
if os.path.exists("results/futures_paper.csv"):   # Nov 1: every Belle alert as 1 MES on paper (bots/futures_paper.py)
    with open("results/futures_paper.csv") as fh:
        fx = list(csv.DictReader(fh))
    fw = [r for r in fx if r["date"] >= str(wk0)]
    if fx:
        L += ["", "## Futures paper (1 MES per Belle alert)", "", "| Period | Trades | Wins | P/L |", "|---|---|---|---|"]
        for nm, rs in (("This week", fw), ("Since the start", fx)):
            L.append(f"| {nm} | {len(rs)} | {sum(1 for r in rs if float(r['pl']) > 0)} | ${sum(float(r['pl']) for r in rs):+,.0f} |")
        by = defaultdict(lambda: [0, 0.0])
        for r in fx:
            by[r["reason"]][0] += 1
            by[r["reason"]][1] += float(r["pl"])
        L += ["", "| Exit | Trades | P/L |", "|---|---|---|"] + [f"| {k} | {v[0]} | ${v[1]:+,.0f} |" for k, v in sorted(by.items())]
L += ["", "## Rule candidates (8+ trades, win rate 20+ points away from the rest)", "",
      "Walk-forward: the gap in the first half of the trades vs the second half. Holds = same direction and 10+ points in the second half.", ""]
if cands:
    L += ["| Tag | Idea | Trades | Win rate | Rest | Skipping it would change P/L by | Winners it would block | First half | Second half | Holds |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    L += [f"| {c[0]} | {c[1]} | {c[2]} | {c[3]} | {c[4]} | ${c[5]} | {c[6]} | {c[7]} | {c[8]} | {c[9]} |" for c in cands[:10]]
else:
    L.append("None yet. Most tags need more trades.")
L += ["", "Harper never changes code, orders or alerts. A rule changes only with a yes."]
os.makedirs("results/harper", exist_ok=True)
path = f"results/harper/weekly-{now:%Y-%m-%d}.md"
with open(path, "w") as fh:
    fh.write("\n".join(L) + "\n")
with open("results/harper/rule_candidates.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["tag", "idea", "trades", "win_rate", "rest_win_rate", "pl_change_if_skipped", "winners_blocked",
                "first_half_gap", "second_half_gap", "holds", "written"])
    for c in cands:
        w.writerow(c + [f"{now:%Y-%m-%d}"])
print("\n".join(L))
