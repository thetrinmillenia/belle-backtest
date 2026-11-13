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
    # Nov 12 (Titi): four windows. W1 10:00-12:30, W2 lunch, W3 13:30-15:00, W4 EOD 15:00-15:55 (ET)
    return "W1" if m <= 750 else ("W2 lunch" if m < 810 else ("W3" if m < 900 else "W4 EOD"))


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
    # Nov 4 (Titi): best price from entry to 15:58 and the first time it reached +100% (the "right" grade)
    tr["best"], tr["t100"] = None, None
    try:
        bb = requests.get(f"{DATA}/v1beta1/options/bars", headers=H, timeout=15,
                          params={"symbols": tr["sym"], "timeframe": "1Min", "start": tr["t_in"].isoformat(),
                                  "end": dt.datetime.combine(day, dt.time(15, 58), ET).isoformat()}).json()
        bl = (bb.get("bars") or {}).get(tr["sym"], [])
        if bl:
            tr["best"] = (max(b["h"] for b in bl) / tr["entry"] - 1) * 100
            hit = [b for b in bl if b["h"] >= tr["entry"] * 2]
            tr["t100"] = et_time(hit[0]["t"]) if hit else None
    except Exception:
        pass
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
# Nov 4 (Titi): an alert is RIGHT only when its contract reached +100% that day
L += ["", "## 2. Belle alerts (right = the contract reached +100%)", "",
      "| Time ET | Side | Window | Grade | Best | Hit +100% at ET | Penny |", "|---|---|---|---|---|---|---|"]
score = {"right": 0, "not right": 0}
for tm, group in sorted(alerts.items()):
    best = max(group, key=lambda t: (t["best"] or -100))
    top = best["best"] if best["best"] is not None else -100
    pct = max((t["pct"] or -100) for t in group)
    verdict = "right" if top >= 100 else "not right"
    score[verdict] += 1
    side = "Calls" if best["sym"][-9] == "C" else "Puts"
    hit = f"{best['t100']:%H:%M}" if best["t100"] else ""
    held = "" if not best["t100"] else (" (out before it)" if best["t_out"] and best["t_out"] < best["t100"] else " (holding)")
    L.append(f"| {tm} | {side} | {window(best['t_in'])} | {verdict.title()} | {top:+.0f}% | {hit}{held} | {pct:+.0f}% |")
L += ["", f"Score: {score['right']} right, {score['not right']} not right.", ""]
# Nov 4 (Titi): VIX check. Priced move from VIX1D at the open vs what SPX actually did
def ychart(sym, interval, rng):
    r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}", params={"interval": interval, "range": rng},
                     headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    return [(dt.datetime.fromtimestamp(t, ET), q["open"][i], q["high"][i], q["low"][i], q["close"][i])
            for i, t in enumerate(r["timestamp"]) if q["close"][i] is not None]


def day_type():
    """Trend day when the Daily, 4H and 1H structure all agree (same check as Penny and Pearl), else choppy."""
    start = (now - dt.timedelta(days=45)).astimezone(dt.timezone.utc).isoformat()
    rows, tok = [], None
    while True:
        p = {"timeframe": "5Min", "feed": "iex", "start": start, "limit": 10000}
        if tok:
            p["page_token"] = tok
        j = requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, timeout=15, params=p).json()
        for x in j.get("bars") or []:
            t = et_time(x["t"])
            if dt.time(9, 30) <= t.time() < dt.time(16, 0):
                rows.append((t, x["h"], x["l"], x["c"]))
        tok = j.get("next_page_token")
        if not tok:
            break

    def mss(g):
        sh = sl = tr_ = None
        for j_ in range(len(g)):
            i = j_ - 2
            if i >= 2:
                if g[i][0] > max(g[i - 2][0], g[i - 1][0], g[i + 1][0], g[i + 2][0]):
                    sh = g[i][0]
                if g[i][1] < min(g[i - 2][1], g[i - 1][1], g[i + 1][1], g[i + 2][1]):
                    sl = g[i][1]
            if sl is not None and g[j_][2] < sl and tr_ != -1:
                tr_ = -1
            elif sh is not None and g[j_][2] > sh and tr_ != 1:
                tr_ = 1
        return tr_
    groups, days = {}, {}
    for t, h, l, c in rows:
        for size in (60, 240):
            k = (size, t.date(), (t.hour * 60 + t.minute - 570) // size)
            g = groups.get(k)
            groups[k] = [h, l, c] if g is None else [max(g[0], h), min(g[1], l), c]
        g = days.get(t.date())
        days[t.date()] = [h, l, c] if g is None else [max(g[0], h), min(g[1], l), c]
    tr3 = [mss([days[k] for k in sorted(days)]), mss([v for k, v in sorted(groups.items()) if k[0] == 240]),
           mss([v for k, v in sorted(groups.items()) if k[0] == 60])]
    return ("trend" if tr3[0] is not None and tr3.count(tr3[0]) == 3 else "choppy"), tr3


L += ["## VIX check", ""]
vix_row = None
try:
    vol, vname = None, "VIX1D"
    for sym, nm in (("%5EVIX1D", "VIX1D"), ("%5EVIX", "VIX")):
        try:
            b_ = [r_ for r_ in ychart(sym, "5m", "1d") if r_[0].date() == day and r_[0].time() >= dt.time(9, 30)]
            if b_:
                vol, vname = b_[0][1], nm
                break
        except Exception as e:
            print("vol failed", sym, e)
    vx = [r_ for r_ in ychart("%5EVIX", "5m", "1d") if r_[0].date() == day and r_[0].time() >= dt.time(9, 30)]
    vix_open = vx[0][1] if vx else None
    if vol and ctx:
        name, pdc, o_, h_, l_, c_ = ctx
        em = pdc * vol / 15.87 / 100
        rng = h_ - l_
        inside = abs(c_ - pdc) <= em
        g5 = [r_ for r_ in ychart("%5EGSPC", "5m", "1d") if r_[0].date() == day and dt.time(9, 30) <= r_[0].time() < dt.time(11, 30)]
        am = (max(r_[2] for r_ in g5) - min(r_[3] for r_ in g5)) if g5 else None
        try:
            dtype, tr3 = day_type()
        except Exception as e:
            print("day type failed", e)
            dtype, tr3 = "unknown", []
        n_alerts = score["right"] + score["not right"]
        L += [f"{vname} {vol:.2f}" + (f"  |  VIX {vix_open:.2f}" if vix_open and vname != "VIX" else "") + "  (at 09:30 ET, 08:30 CT)", "",
              f"Priced move:  {em:,.1f} points  ({vol / 15.87:.2f}%)", "",
              f"Actual range:  {rng:,.1f} points  ({rng / em * 100:.0f}% of the priced move)", "",
              f"Close inside the priced range:  {'yes' if inside else 'no'}", ""]
        if am is not None:
            L += [f"Used before 11:30 ET (10:30 CT):  {am:,.1f} points  ({am / em * 100:.0f}%)", ""]
        L += [f"Day type:  {dtype}" + (f"  (Daily, 4H, 1H: {tr3})" if tr3 else ""), "",
              f"Right alerts (hit +100%):  {score['right']} of {n_alerts}", ""]
        vix_row = [str(day), f"{vol:.2f}", f"{vix_open:.2f}" if vix_open else "", f"{em:.1f}", f"{rng:.1f}",
                   f"{rng / em * 100:.0f}", "yes" if inside else "no", f"{am:.1f}" if am is not None else "", dtype,
                   score["right"], n_alerts]
    else:
        L += ["VIX data not available today.", ""]
except Exception as e:
    print("vix check failed", e)
    L += ["VIX data not available today.", ""]
if vix_row:   # one row per day for the weekly review and the final review
    path_v = "results/harper/vix_log.csv"
    os.makedirs("results/harper", exist_ok=True)
    old = []
    if os.path.exists(path_v):
        with open(path_v) as fh:
            old = [r_ for r_ in csv.reader(fh)][1:]
    old = [r_ for r_ in old if r_ and r_[0] != str(day)] + [vix_row]
    with open(path_v, "w", newline="") as fh:
        w_ = csv.writer(fh)
        w_.writerow(["date", "vix1d", "vix", "priced_pts", "actual_pts", "used_pct", "close_inside", "am_pts", "day_type",
                     "right", "alerts"])
        w_.writerows(sorted(old))

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
spx_h = [t for t in trades if t["sym"].startswith("SPXW") and t["t_out"]]   # Titi, Nov 3: track how long SPX is held
if spx_h:
    hm = [(t["t_out"] - t["t_in"]).total_seconds() / 60 for t in spx_h]
    L.append(f"- SPX hold time today: {len(spx_h)} trade{'s' if len(spx_h) > 1 else ''}, average {sum(hm) / len(hm):.0f} min, longest {max(hm):.0f} min "
             f"(before the new exit on Nov 3: median 8 min; the 1,000% moves needed 2 to 4.5 hours).")
# Nov 12 (Titi): afternoon exit check. Rule: -50% until +100%, then sell on a 20% drop from the best, out 15:59
aft = [t for t in trades if window(t["t_in"]) in ("W3", "W4 EOD") and t.get("best") is not None and t["best"] >= 100]
for t in aft:
    L.append(f"- Afternoon runner {t['contract']}: best {t['best']:+.0f}%, kept {(t['pct'] if t['pct'] is not None else 0):+.0f}% (20% trail after +100%).")
L += ["", "## 4. Titi", ""]
if titi:
    for r in titi:
        L.append(f"- {r['setup']}: {r.get('note', '')} P/L {r.get('pl') or (r.get('pct', '') + '%')}")
else:
    L.append("Titi's trades not logged yet.")
# Titi's study notes for the day (data/titi_lessons.csv, Oct 22)
notes = []
if os.path.exists("data/titi_lessons.csv"):
    with open("data/titi_lessons.csv") as fh:
        notes = [r for r in csv.DictReader(fh) if r["date"] == str(day)]
for r in notes:
    L.append(f"- Study note ({r['source']}, {r['setup']}): {r['lesson']} Rule: {r['rule']}")
L += ["", "## 5. Nora setups", ""]
if stats:
    s2 = sorted(stats, key=lambda s: float(s["P/L"]))
    L.append("Best: " + " | ".join(f"{s['Pattern']} {s['Win %']}% wins {float(s['P/L']):+,.0f}" for s in s2[::-1][:3]))
    L.append("Costliest: " + " | ".join(f"{s['Pattern']} {s['Win %']}% wins {float(s['P/L']):+,.0f}" for s in s2[:3]))
L += ["", "## 6. One suggestion (needs Titi's yes, Harper changes nothing)", ""]
w3 = [t for t in trades if window(t["t_in"]) in ("W3", "W4 EOD")]   # the afternoon (13:30 ET on)
if missed:
    L.append("Runners were sold early. Review the step stop and breakeven timing on these trades before changing anything.")
elif total < 0 and w3 and sum(t["pl"] for t in w3) < 0:
    L.append("The afternoon (Windows 3 and 4) lost today. Check whether the entries had the 15m flip (15m candle turned to the trade's side) and 1H/4H bias.")
elif score["not right"] > score["right"]:
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
