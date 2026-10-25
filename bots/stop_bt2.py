"""STOP BACKTEST on Penny's real trades (Titi, Oct 25 2026). Read only, PAPER account data.

For every Penny entry since START, it replays the contract's 1 minute bars (trade prices, close to the midpoint)
from the fill to 15:58 ET under several stop rules, one contract each, and compares them with what Penny really got
(her fills used the bid). SPX and SPY are reported apart. Trims are ignored (every rule sells all at once).
"""
import datetime as dt
import os
from collections import defaultdict
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
TRADE = "https://paper-api.alpaca.markets"
DATA = "https://data.alpaca.markets"
H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"].strip(), "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"].strip()}
START = os.environ.get("START", "2026-10-14")


def et(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(ET)


orders, after = [], f"{START}T12:00:00Z"
while True:
    page = requests.get(f"{TRADE}/v2/orders", headers=H, timeout=30,
                        params={"status": "closed", "after": after, "direction": "asc", "limit": 500}).json()
    page = [o for o in page if isinstance(o, dict)]
    orders += page
    if len(page) < 500:
        break
    after = page[-1]["submitted_at"]
fills = [o for o in orders if o.get("filled_at") and len(o.get("symbol", "")) > 15]
fills.sort(key=lambda o: o["filled_at"])

# real results, first in first out per contract
lots, trades = defaultdict(list), []
for o in fills:
    q, p, t = int(float(o["filled_qty"])), float(o["filled_avg_price"]), et(o["filled_at"])
    if o["side"] == "buy":
        tr = {"sym": o["symbol"], "t": t, "qty": q, "e": p, "left": q, "got": 0.0}
        lots[o["symbol"]].append(tr)
        trades.append(tr)
    else:
        while q > 0 and lots[o["symbol"]]:
            tr = lots[o["symbol"]][0]
            n = min(q, tr["left"])
            tr["got"] += (p - tr["e"]) * 100 * n
            tr["left"] -= n
            q -= n
            if tr["left"] == 0:
                lots[o["symbol"]].pop(0)


def rule_current(e, peak, cap=True, lock=True):
    s = e * 0.57
    if peak >= e * 1.2:
        s = max(s, e * 0.80)
    if peak >= e * 1.4:
        s = max(s, e)
    if peak >= e * 1.5:
        s = max(s, peak - (min(peak * 0.30, 0.50) if cap else peak * 0.30))
    if lock and peak >= e * 2.0:
        g = int((peak / e - 1) * 10 + 1e-9) / 10
        s = max(s, e * (1 + g - 0.30))
    return s


RULES = {
    "A now (43%, step, BE, $50 cap, lock)": lambda e, pk: rule_current(e, pk),
    "B no $50 cap": lambda e, pk: rule_current(e, pk, cap=False),
    "C hold (60% floor, trail 40% after +100%)": lambda e, pk: e * 0.40 if pk < e * 2 else max(e * 0.40, pk * 0.60),
    "D 43% start, no step, trail 30% after +100%": lambda e, pk: e * 0.57 if pk < e * 2 else max(e * 0.57, pk * 0.70),
    "E 43% start, breakeven at +60%, trail 30% after +100%": lambda e, pk: e * 0.57 if pk < e * 1.6 else (e if pk < e * 2 else max(e, pk * 0.70)),
    "F 43% start, -20% at +50%, trail 30% after +100%": lambda e, pk: e * 0.57 if pk < e * 1.5 else (e * 0.80 if pk < e * 2 else max(e * 0.80, pk * 0.70)),
    "G 43% start, breakeven at +80%, trail 35% after +100%": lambda e, pk: e * 0.57 if pk < e * 1.8 else (e if pk < e * 2 else max(e, pk * 0.65)),
}

REAL = "REAL"
res = defaultdict(lambda: defaultdict(float))
cnt = defaultdict(int)
rows = []
for tr in trades:
    if tr["left"] > 0:
        continue   # still open or unmatched
    end = tr["t"].replace(hour=15, minute=58, second=0)
    b = requests.get(f"{DATA}/v1beta1/options/bars", headers=H, timeout=30,
                     params={"symbols": tr["sym"], "timeframe": "1Min", "start": tr["t"].isoformat(),
                             "end": end.isoformat(), "limit": 1000}).json()
    bars = (b.get("bars") or {}).get(tr["sym"], [])
    if not bars:
        continue
    kind = "SPX" if tr["sym"].startswith("SPXW") else "SPY"
    e = tr["e"]
    out = {}
    for name, fn in RULES.items():
        peak, ex = e, None
        for x in bars:
            st = fn(e, peak)
            if x["l"] <= st:
                ex = min(st, x["o"])   # gap through the stop fills at the open
                break
            peak = max(peak, x["h"])
        if ex is None:
            ex = bars[-1]["c"]
        pl = (ex - e) * 100 * tr["qty"]
        out[name] = pl
        res[kind][name] += pl
    res[kind][REAL] += tr["got"]
    best = max(x["h"] for x in bars)
    cnt[kind] += 1
    rows.append(f"| {tr['t']:%m-%d %H:%M} | {kind} {tr['sym'][-9]} | {tr['qty']} | {e:.2f} | {best / e * 100 - 100:+.0f}% | {tr['got']:+.0f} | "
                + " | ".join(f"{out[k]:+.0f}" for k in RULES) + " |")

L = [f"# Stop backtest on Penny's real trades ({START} to {dt.date.today()})", "",
     "Bars are 1 minute trade prices (close to the midpoint). REAL = what Penny got on the bid.", ""]
for kind in ("SPX", "SPY"):
    L += [f"## {kind}: {cnt[kind]} trades", "", "| Rule | P/L |", "|---|---|",
          f"| REAL (Penny's fills) | {res[kind][REAL]:+,.0f} |"]
    L += [f"| {k} | {res[kind][k]:+,.0f} |" for k in RULES]
    L.append("")
L += ["## Every trade", "", "| In ET | Contract | Qty | Entry | Best | REAL | " + " | ".join(k.split(" ")[0] for k in RULES) + " |",
      "|---|---|---|---|---|---|" + "---|" * len(RULES)] + rows
md = "\n".join(L) + "\n"
os.makedirs("results", exist_ok=True)
with open("results/stop_bt.md", "w") as fh:
    fh.write(md)
print(md)
