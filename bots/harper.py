"""HARPER, the manager (Titi, Oct 20 2026). Runs on GitHub every weekday after the close. Read only, PAPER account.

She grades the day and writes one review:
  1. Market context: SPX open, high, low, close and the prior day close (PDC), closed above or below PDC
  2. Belle's alerts (every Penny entry is one Belle alert): right, flat or wrong
  3. Penny's trades from the Alpaca paper fills, and what each contract did AFTER Penny sold it
  4. Titi's trades (data/titi_trades.csv)
  5. Nora's best and costliest setups (results/pattern_stats.csv)
  6. Lessons, and ONE suggested change that needs Titi's yes. Harper never changes code, orders or alerts.
The review is saved to results/harper/YYYY-MM-DD.md. If the GitHub secret NORA_SHEET_URL is set (the journal's
Apps Script web app), the same review is also created as a Google Doc. No Discord posts.
"""
import csv
import datetime as dt
import os
import sys
from collections import defaultdict
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
TRADE = "https://paper-api.alpaca.markets"   # PAPER endpoint only, read only here
DATA = "https://data.alpaca.markets"
H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"].strip(), "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"].strip()}
SHEET = os.environ.get("NORA_SHEET_URL", "").strip()

now = dt.datetime.now(ET)
if os.environ.get("FORCE") != "1" and not (now.hour == 16 and now.weekday() < 5):
    print("not 16:xx ET on a weekday, skipping")   # the workflow runs at two UTC times to cover daylight saving
    sys.exit(0)
day = now.date()
cal = requests.get(f"{TRADE}/v2/calendar", headers=H, params={"start": str(day), "end": str(day)}, timeout=15).json()
if not cal or cal[0].get("date") != str(day):
    print("market closed today, no review")
    sys.exit(0)


def label(sym):
    root, cp, k = sym[:-15], sym[-9], int(sym[-8:]) / 1000
    return f"{'SPX' if root.startswith('SPX') else root} {k:g}{cp}"


def et_time(iso):
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(ET)


def window(t):
    m = t.hour * 60 + t.minute
    return "W1" if m <= 750 else ("W3 EOD" if m >= 900 else "W2")


# 1) market context: Yahoo ^GSPC daily, Alpaca SPY daily as a fallback
ctx = None
try:
    r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC", params={"interval": "1d", "range": "5d"},
                     headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()
    x = r["chart"]["result"][0]
    q = x["indicators"]["quote"][0]
    rows = [(dt.datetime.fromtimestamp(t, ET).date(), q["open"][i], q["high"][i], q["low"][i], q["close"][i])
            for i, t in enumerate(x["timestamp"]) if q["close"][i]]
    today_row = [r_ for r_ in rows if r_[0] == day]
    prev = [r_ for r_ in rows if r_[0] < day]
    if today_row and prev:
        ctx = ("SPX", prev[-1][4], *today_row[0][1:])
except Exception as e:
    print("yahoo failed", e)
if ctx is None:
    try:
        b = requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, timeout=15,
                         params={"timeframe": "1Day", "start": str(day - dt.timedelta(days=7)), "feed": "iex"}).json()["bars"]
        if len(b) >= 2:
            ctx = ("SPY", b[-2]["c"], b[-1]["o"], b[-1]["h"], b[-1]["l"], b[-1]["c"])
    except Exception as e:
        print("spy bars failed", e)

# 2) Penny's trades from today's fills (first in, first out per contract)
orders = requests.get(f"{TRADE}/v2/orders", headers=H, timeout=20,
                      params={"status": "closed", "after": f"{day}T12:00:00Z", "direction": "asc", "limit": 500}).json()
orders = [o for o in orders if isinstance(o, dict) and o.get("filled_at") and len(o.get("symbol", "")) > 15]
orders.sort(key=lambda o: o["filled_at"])
open_lots = defaultdict(list)
trades = []
for o in orders:
    q, p, t = int(float(o["filled_qty"])), float(o["filled_avg_price"]), et_time(o["filled_at"])
    if o["side"] == "buy":
        tr = {"sym": o["symbol"], "contract": label(o["symbol"]), "t_in": t, "qty": q, "entry": p, "sells": [],
              "re": (o.get("client_order_id") or "").startswith("penny-re-"), "left": q}
        open_lots[o["symbol"]].append(tr)
        trades.append(tr)
    else:
        while q > 0 and open_lots[o["symbol"]]:
            tr = open_lots[o["symbol"]][0]
            n = min(q, tr["left"])
            tr["sells"].append((p, n, t))
            tr["left"] -= n
            q -= n
            if tr["left"] == 0:
                open_lots[o["symbol"]].pop(0)
for tr in trades:
    sold = sum(n for _, n, _ in tr["sells"])
    tr["exit"] = sum(p * n for p, n, _ in tr["sells"]) / sold if sold else None
    tr["t_out"] = tr["sells"][-1][2] if tr["sells"] else None
    tr["pl"] = (tr["exit"] - tr["entry"]) * 100 * sold if sold else 0.0
    tr["pct"] = (tr["exit"] / tr["entry"] - 1) * 100 if sold else None
    # what the contract did after Penny sold it (best price until 15:58)
    tr["after"] = None
    if tr["t_out"]:
        try:
            bars = requests.get(f"{DATA}/v1beta1/options/bars", headers=H, timeout=15,
                                params={"symbols": tr["sym"], "timeframe": "1Min", "start": tr["t_out"].isoformat(),
                                        "end": dt.datetime.combine(day, dt.time(15, 58), ET).isoformat()}).json()
            hs = [b["h"] for b in (bars.get("bars") or {}).get(tr["sym"], [])]
            if hs:
                tr["after"] = (max(hs) / tr["entry"] - 1) * 100
        except Exception:
            pass

# Belle alerts = Penny entry times (re-entries excluded)
alerts = defaultdict(list)
for tr in trades:
    if not tr["re"]:
        alerts[tr["t_in"].strftime("%H:%M")].append(tr)

# 3) Titi's trades and Nora's setups
titi = []
if os.path.exists("data/titi_trades.csv"):
    with open("data/titi_trades.csv") as fh:
        titi = [r for r in csv.DictReader(fh) if r["date"] == str(day)]
stats = []
if os.path.exists("results/pattern_stats.csv"):
    with open("results/pattern_stats.csv") as fh:
        stats = list(csv.DictReader(fh))

# 4) the review
f2 = lambda v: f"{v:,.2f}"
L = [f"# Harper Daily Review: {day:%A, %B %d, %Y}", ""]
L += ["## 1. Market context", ""]
if ctx:
    name, pdc, o_, h_, l_, c_ = ctx
    side = "ABOVE" if c_ >= pdc else "BELOW"
    L += ["| Item | Value |", "|---|---|", f"| Prior day close (PDC) | {f2(pdc)} |",
          f"| Open | {f2(o_)} ({o_ - pdc:+.1f} pts vs PDC) |", f"| High | {f2(h_)} |", f"| Low | {f2(l_)} |",
          f"| Close | {f2(c_)} |", f"| Close vs PDC | **Closed {side} PDC by {abs(c_ - pdc):.1f} pts** |",
          f"| Day range | {h_ - l_:.1f} pts |", ""]
    if (o_ - pdc) * (c_ - pdc) < 0:
        L.append(f"Opened on one side of PDC and closed on the other ({'below to above' if c_ >= pdc else 'above to below'}).")
    L.append(f"Source: {name} daily data. Tomorrow's PDC: {f2(c_)}.")
else:
    L.append("Market data not available today.")
L += ["", "## 2. Belle alerts", "", "| Time ET | Side | Window | Result |", "|---|---|---|---|"]
score = {"right": 0, "flat": 0, "wrong": 0}
for tm, group in sorted(alerts.items()):
    best = max(group, key=lambda t: (t["after"] or -100, t["pct"] or -100))
    pct = max((t["pct"] or -100) for t in group)
    ran = max((t["after"] or -100) for t in group)
    verdict = "right" if pct >= 20 or ran >= 50 else ("wrong" if pct <= -20 and ran < 20 else "flat")
    score[verdict] += 1
    side = "Calls" if best["sym"][-9] == "C" else "Puts"
    L.append(f"| {tm} | {side} | {window(best['t_in'])} | {verdict.title()}: Penny {pct:+.0f}%, best after her exit {ran:+.0f}% |")
L += ["", f"Score: {score['right']} right, {score['flat']} flat, {score['wrong']} wrong.", ""]
total = sum(t["pl"] for t in trades)
L += ["## 3. Penny (paper)", "", f"{len(trades)} trades, **{total:+,.0f} dollars**.", "",
      "| In | Contract | Qty | Entry | Exit | P/L | After she sold |", "|---|---|---|---|---|---|---|"]
for t in trades:
    ex = "" if t["exit"] is None else f"{t['exit']:.2f}"
    af = "" if t["after"] is None else f"{t['after']:+.0f}%"
    re_ = " RE" if t["re"] else ""
    L.append(f"| {t['t_in']:%H:%M}{re_} | {t['contract']} | {t['qty']} | {t['entry']:.2f} | {ex} | {t['pl']:+,.0f} | {af} |")
missed = [t for t in trades if t["pct"] is not None and t["pct"] < 40 and (t["after"] or 0) >= 100]
L.append("")
for t in missed:
    L.append(f"- Missed runner: {t['contract']} sold at {t['pct']:+.0f}%, it went to {t['after']:+.0f}% after.")
L += ["", "## 4. Titi", ""]
if titi:
    for r in titi:
        L.append(f"- {r['setup']}: {r.get('note', '')} P/L {r.get('pl') or (r.get('pct', '') + '%')}")
else:
    L.append("Titi's trades not logged yet.")
L += ["", "## 5. Nora setups", ""]
if stats:
    s2 = sorted(stats, key=lambda s: float(s["P/L"]))
    L.append("Best: " + " | ".join(f"{s['Pattern']} {s['Win %']}% wins {float(s['P/L']):+,.0f}" for s in s2[::-1][:3]))
    L.append("Costliest: " + " | ".join(f"{s['Pattern']} {s['Win %']}% wins {float(s['P/L']):+,.0f}" for s in s2[:3]))
L += ["", "## 6. One suggestion (needs Titi's yes, Harper changes nothing)", ""]
w3 = [t for t in trades if window(t["t_in"]) == "W3 EOD"]
if missed:
    L.append("Runners were sold early. Review the step stop and breakeven timing on these trades before changing anything.")
elif total < 0 and w3 and sum(t["pl"] for t in w3) < 0:
    L.append("Window 3 lost today. Check whether the entries had 1m, 5m and 15m agreement.")
elif score["wrong"] > score["right"]:
    L.append("More wrong alerts than right. Check the bias filter on today's losing windows.")
else:
    L.append("No change needed. Keep the rules as they are.")
md = "\n".join(L) + "\n"

os.makedirs("results/harper", exist_ok=True)
with open(f"results/harper/{day}.md", "w") as fh:
    fh.write(md)
print(md)
if SHEET:
    try:
        r = requests.post(SHEET, json={"action": "harperDoc", "title": f"Harper Daily Review - {day}", "markdown": md}, timeout=60)
        print("google doc", r.status_code, r.text[:200])
    except Exception as e:
        print("google doc failed", e)
