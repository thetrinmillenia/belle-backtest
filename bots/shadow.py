"""SHADOW (Titi, Oct 26 2026). Scores the Belle alerts Penny filtered out. No orders, no Discord.

record (started by the relay the moment Penny skips an alert):
  saves the SPX contract at Belle's strike and its ask (the entry) to results/shadow_signals.csv.
eval (runs in Nora's job after the close):
  for today's skipped alerts, 1 minute bars from the alert to 15:59 ET give
  the highest price and its time, the lowest price before that high (the heat),
  and what Penny's rule E would have closed at. Writes results/shadow_trades.csv.
"""
import csv
import datetime as dt
import os
import sys
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
DATA = "https://data.alpaca.markets"
H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"].strip(), "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"].strip()}
MODE = os.environ.get("MODE", "record").strip() or "record"
SIG = "results/shadow_signals.csv"
OUT = "results/shadow_trades.csv"
os.makedirs("results", exist_ok=True)


def now():
    return dt.datetime.now(ET)


def append(path, row, header):
    new = not os.path.exists(path)
    with open(path, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(header)
        w.writerow(row)


if MODE == "record":
    sym = os.environ.get("SYM", "").strip()
    if len(sym) < 16:
        print("no contract, nothing saved")
        sys.exit(0)
    try:
        sent = dt.datetime.fromtimestamp(float(os.environ.get("SENT", "")), ET)
    except ValueError:
        sent = now()
    q = (requests.get(f"{DATA}/v1beta1/options/quotes/latest", headers=H, timeout=15,
                      params={"symbols": sym, "feed": "indicative"}).json().get("quotes") or {}).get(sym) or {}
    ask = q.get("ap") or ""
    append(SIG, [f"{sent:%Y-%m-%d}", f"{sent:%H:%M}", os.environ.get("SIDE", ""), sym, ask, os.environ.get("REASON", "")],
           ["date", "time_et", "side", "contract", "entry", "reason"])
    print("saved", sym, ask)
    sys.exit(0)

# ---------- eval ----------
day = os.environ.get("EVAL_DATE", "").strip() or f"{now():%Y-%m-%d}"
if not os.path.exists(SIG):
    print("no shadow signals yet")
    sys.exit(0)
done = set()
if os.path.exists(OUT):
    with open(OUT) as fh:
        done = {(r["date"], r["time_et"], r["contract"]) for r in csv.DictReader(fh)}
with open(SIG) as fh:
    rows = [r for r in csv.DictReader(fh) if r["date"] == day and (r["date"], r["time_et"], r["contract"]) not in done]
for r in rows:
    t0 = dt.datetime.fromisoformat(f"{r['date']}T{r['time_et']}").replace(tzinfo=ET)
    t1 = t0.replace(hour=15, minute=59)
    bars = (requests.get(f"{DATA}/v1beta1/options/bars", headers=H, timeout=30,
                         params={"symbols": r["contract"], "timeframe": "1Min", "start": t0.isoformat(), "end": t1.isoformat(),
                                 "limit": 1000}).json().get("bars") or {}).get(r["contract"], [])
    if not bars:
        print("no bars for", r["contract"])
        continue
    e = float(r["entry"]) if r["entry"] else bars[0]["o"]
    hi_i = max(range(len(bars)), key=lambda i: bars[i]["h"])
    hi = bars[hi_i]["h"]
    hi_t = dt.datetime.fromisoformat(bars[hi_i]["t"].replace("Z", "+00:00")).astimezone(ET)
    low_before = min(b["l"] for b in bars[:hi_i + 1])
    peak, ex = e, None
    for b in bars:   # rule E: 43% stop, breakeven after +60%, trail 30% below the best after +100%
        stop = e * 0.57
        if peak >= e * 1.6:
            stop = max(stop, e)
        if peak >= e * 2.0:
            stop = max(stop, peak * 0.70)
        if b["l"] <= stop:
            ex = min(stop, b["o"])
            break
        peak = max(peak, b["h"])
    if ex is None:
        ex = bars[-1]["c"]
    append(OUT, [r["date"], r["time_et"], r["side"], r["contract"], f"{e:.2f}", f"{hi:.2f}", f"{(hi / e - 1) * 100:.0f}",
                 f"{hi_t:%H:%M}", f"{low_before:.2f}", f"{ex:.2f}", f"{(ex - e) * 100:.0f}", r["reason"]],
           ["date", "time_et", "side", "contract", "entry", "highest", "highest_pct", "highest_time_et", "lowest_before_high",
            "rule_e_exit", "rule_e_pl", "reason"])
    print(r["time_et"], r["contract"], "entry", e, "high", hi, "at", f"{hi_t:%H:%M}", "low before", low_before, "rule E", ex)
print(len(rows), "shadow trades scored for", day)
