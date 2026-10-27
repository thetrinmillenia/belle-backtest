"""EOD STOP TEST on Penny's real EOD trades (Titi, Oct 27 2026). Read only, PAPER account data.

Every Penny entry filled 15:00 to 15:55 ET since START is replayed on 1 minute bars to 15:59 ET under several
starting stops, all with the EOD trail (20% below the best from +30%, 15% from +100%). One contract each.
Also shows the heat: how far each trade dropped before its best price. SPX and SPY are reported apart.
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
START = os.environ.get("START", "").strip() or "2026-10-14"


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
buys = [o for o in orders if o.get("filled_at") and o["side"] == "buy" and len(o.get("symbol", "")) > 15]
buys = [o for o in buys if 900 <= et(o["filled_at"]).hour * 60 + et(o["filled_at"]).minute <= 955]


def run(bars, e, start_loss, be_at):
    """Exit price under: starting stop, breakeven at be_at, EOD trail. Out at the last bar (15:59)."""
    peak = e
    for b in bars:
        stop = e * (1 - start_loss)
        if peak >= e * be_at:
            stop = max(stop, e)
        if peak >= e * 1.30:
            stop = max(stop, peak * 0.80)
        if peak >= e * 2.0:
            stop = max(stop, peak * 0.85)
        if b["l"] <= stop:
            return min(stop, b["o"])
        peak = max(peak, b["h"])
    return bars[-1]["c"]


RULES = {"30% stop, BE +30%": (0.30, 1.30), "43% stop, BE +60%": (0.43, 1.60), "50% stop, BE +60%": (0.50, 1.60),
         "50% stop, BE +30%": (0.50, 1.30)}
res = defaultdict(lambda: defaultdict(float))
wins = defaultdict(lambda: defaultdict(int))
cnt = defaultdict(int)
heat = defaultdict(list)
rows = []
for o in buys:
    t = et(o["filled_at"])
    e = float(o["filled_avg_price"])
    end = t.replace(hour=15, minute=59, second=0)
    bars = ((requests.get(f"{DATA}/v1beta1/options/bars", headers=H, timeout=30,
                          params={"symbols": o["symbol"], "timeframe": "1Min", "start": t.isoformat(), "end": end.isoformat(),
                                  "limit": 1000}).json().get("bars") or {}).get(o["symbol"]) or [])
    if not bars:
        continue
    kind = "SPX" if o["symbol"].startswith("SPXW") else "SPY"
    hi_i = max(range(len(bars)), key=lambda i: bars[i]["h"])
    low_before = min(b["l"] for b in bars[:hi_i + 1])
    h = (low_before / e - 1) * 100
    heat[kind].append(h)
    cnt[kind] += 1
    outs = []
    for name, (sl, be) in RULES.items():
        x = run(bars, e, sl, be)
        pl = (x - e) * 100
        res[kind][name] += pl
        wins[kind][name] += pl > 0
        outs.append(f"{pl:+.0f}")
    rows.append(f"| {t:%m-%d %H:%M} | {kind} {o['symbol'][-9]} | {e:.2f} | {bars[hi_i]['h'] / e * 100 - 100:+.0f}% | {h:+.0f}% | "
                + " | ".join(outs) + " |")

L = [f"# EOD stop test, Penny's EOD entries 15:00 to 15:55 ET ({START} to {dt.date.today()}), 1 contract each", ""]
for kind in ("SPX", "SPY"):
    hs = sorted(heat[kind])
    L += [f"## {kind}: {cnt[kind]} trades", ""]
    if hs:
        L.append("Heat before the best price: " + ", ".join(f"{x:+.0f}%" for x in hs))
        for lim in (30, 43, 50):
            L.append(f"- dropped more than {lim}% before the best: {sum(1 for x in hs if x < -lim)} of {len(hs)}")
        L.append("")
    L += ["| Rule | P/L | Wins |", "|---|---|---|"] + [f"| {k} | {res[kind][k]:+,.0f} | {wins[kind][k]} of {cnt[kind]} |" for k in RULES]
    L.append("")
L += ["## Every trade", "", "| In ET | Contract | Entry | Best | Heat | " + " | ".join(RULES) + " |",
      "|---|---|---|---|---|" + "---|" * len(RULES)] + rows
md = "\n".join(L) + "\n"
os.makedirs("results", exist_ok=True)
with open("results/eod_bt.md", "w") as fh:
    fh.write(md)
print(md)
