"""SAGE, the seller (Titi, Nov 8 2026). Paper account only. No Discord posts (Penny already posts her exits).

The account is small, so every option position gets the same exits, whoever opened it:
  - take profit: sell everything at +100%
  - stop: sell at -50%
  - last ten minutes: from 15:50 ET, a position up 20%+ sells on a 10% pullback from its best
  - out by 15:57 ET, whatever the price
Runs on GitHub's schedule in two parts (09:20 to 12:45 ET and 12:40 to 16:00 ET), checks every 5 seconds.
Holding rules (4H direction, last 1H candle) come later.
"""
import datetime as dt
import os
import sys
import time
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
TRADE = "https://paper-api.alpaca.markets"   # PAPER endpoint only
DATA = "https://data.alpaca.markets"
H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"].strip(), "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"].strip()}
TP, SL = 2.00, 0.50          # +100% and -50% of the entry price
LAST10, OUT = 950, 957       # 15:50 and 15:57 ET


def now():
    return dt.datetime.now(ET)


def mins():
    n = now()
    return n.hour * 60 + n.minute


part = os.environ.get("PART", "")
m0 = mins()
if not part:
    part = "am" if m0 < 760 else "pm"
END = 765 if part == "am" else 960        # am part to 12:45 ET, pm part to 16:00 ET
if now().weekday() > 4 or m0 >= END or m0 < 555:
    print(f"sage {part}: not its time ({now():%a %H:%M} ET)")
    sys.exit(0)
cal = requests.get(f"{TRADE}/v2/calendar", headers=H, params={"start": str(now().date()), "end": str(now().date())}, timeout=15).json()
if not cal or cal[0].get("date") != str(now().date()):
    print("market closed today")
    sys.exit(0)


def positions():
    r = requests.get(f"{TRADE}/v2/positions", headers=H, timeout=10).json()
    return [p for p in (r if isinstance(r, list) else []) if p.get("asset_class") == "us_option" and float(p.get("qty", 0)) > 0]


def bid(sym):
    q = requests.get(f"{DATA}/v1beta1/options/quotes/latest", params={"symbols": sym, "feed": "indicative"}, headers=H, timeout=10).json()
    return ((q.get("quotes") or {}).get(sym) or {}).get("bp") or 0.0


def sell(p, why):
    sym, qty = p["symbol"], int(float(p["qty"]))
    # cancel Penny's open orders on this contract (her stop holds the quantity), then sell at market
    od = requests.get(f"{TRADE}/v2/orders", headers=H, params={"status": "open", "symbols": sym}, timeout=10).json()
    for o in od if isinstance(od, list) else []:
        requests.delete(f"{TRADE}/v2/orders/{o['id']}", headers=H, timeout=10)
    time.sleep(1)
    if not any(x["symbol"] == sym for x in positions()):
        print(f"{sym}: already closed")
        return
    r = requests.post(f"{TRADE}/v2/orders", headers=H, timeout=10, json={
        "symbol": sym, "qty": str(qty), "side": "sell", "type": "market", "time_in_force": "day",
        "client_order_id": f"sage-{why}-{int(time.time() * 1000)}"}).json()
    print(f"{now():%H:%M:%S} sold {qty} {sym} ({why}): {r.get('id') or r}")


peak = {}
print(f"sage {part} running until {END // 60:02d}:{END % 60:02d} ET")
while mins() < END:
    try:
        m = mins()
        for p in positions():
            sym, entry = p["symbol"], float(p["avg_entry_price"])
            b = bid(sym)
            if not b or not entry:
                continue
            peak[sym] = max(peak.get(sym, entry), b)
            if m >= OUT:
                sell(p, "1557")
            elif b >= entry * TP:
                sell(p, "tp100")
            elif b <= entry * SL:
                sell(p, "sl50")
            elif m >= LAST10 and peak[sym] >= entry * 1.2 and b <= peak[sym] * 0.90:
                sell(p, "last10")
    except Exception as e:
        print("sage error", e)
    time.sleep(5)
print("sage done")
