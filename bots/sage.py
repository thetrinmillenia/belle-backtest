"""SAGE, the seller (Titi, Nov 8 2026). Paper account only. No Discord posts (Penny already posts her exits).

The account is small, so every option position gets the same exits, whoever opened it:
  - take profit: sell everything at +100%
  - stop: sell at -50%
  - last ten minutes: from 15:50 ET, a position up 20%+ sells on a 10% pullback from its best
  - out by 15:57 ET, whatever the price
  - Nov 8 (Titi): at +100%, Sage checks the last closed 1H candle first. If the trend is strong (SPY 1H candle closed
    in the trade's direction with a body of at least half its range), she keeps the contract with a lock at +50% and
    a trail 30% below the best. Each new 1H close is checked again; a candle that is not strong anymore sells.
Runs on GitHub's schedule in two parts (09:20 to 12:45 ET and 12:40 to 16:00 ET), checks every 5 seconds.
Holding rules (4H direction, last 1H candle) come later.
Nov 10 (Titi): positions bought from 15:30 ET on (the 15:30 and 15:50 EOD entries) only get -50% and +500%, and stay to 15:59 ET.
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


peak, held, h1_checked, entered = {}, {}, {}, {}


def entry_min(sym):
    """Minute (ET) of the latest buy fill on this contract today."""
    if sym not in entered:
        od = requests.get(f"{TRADE}/v2/orders", headers=H, timeout=10,
                          params={"status": "closed", "symbols": sym, "after": f"{now().date()}T13:00:00Z", "limit": 50}).json()
        fills = [o["filled_at"] for o in (od if isinstance(od, list) else []) if o.get("side") == "buy" and o.get("filled_at")]
        t = dt.datetime.fromisoformat(max(fills).replace("Z", "+00:00")).astimezone(ET) if fills else None
        entered[sym] = t.hour * 60 + t.minute if t else 0
    return entered[sym]


def h1_strong(cp):
    """Last closed SPY 1H candle closed in the trade's direction with a body of at least half its range."""
    start = (now() - dt.timedelta(hours=6)).astimezone(dt.timezone.utc).isoformat()
    j = requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, timeout=10,
                     params={"timeframe": "1Hour", "start": start, "feed": "iex", "limit": 20}).json()
    bars = [b for b in (j.get("bars") or [])
            if dt.datetime.fromisoformat(b["t"].replace("Z", "+00:00")) + dt.timedelta(hours=1) <= dt.datetime.now(dt.timezone.utc)]
    if not bars:
        return False, "no closed 1H candle"
    b = bars[-1]
    rng, body = b["h"] - b["l"], b["c"] - b["o"]
    up = cp == "C"
    ok = rng > 0 and (body > 0 if up else body < 0) and abs(body) >= 0.5 * rng
    return ok, f"1H {b['t'][11:16]} UTC o {b['o']:.2f} c {b['c']:.2f} body {abs(body) / rng * 100 if rng else 0:.0f}% of range"


print(f"sage {part} running until {END // 60:02d}:{END % 60:02d} ET")
while mins() < END:
    try:
        m = mins()
        for p in positions():
            sym, entry = p["symbol"], float(p["avg_entry_price"])
            b = bid(sym)
            if not b or not entry:
                continue
            if sym.startswith("SPXW") and 0 < entry_min(sym) < 810:
                continue   # Nov 12 (Titi): morning SPX belongs to Penny (no sale at +100%, 30% trail)
            if sym.startswith("SPY") and 0 < entry_min(sym) < 810:
                continue   # Nov 12 (Titi): morning SPY belongs to Penny (her scale out and runner). Sage sold these runners early
            peak[sym] = max(peak.get(sym, entry), b)
            if entry_min(sym) >= 810:   # Nov 12 (Titi): afternoon (13:30 ET on), same exit as Penny. Sage is her backup here
                if m >= 959:
                    sell(p, "1559")
                elif peak[sym] >= entry * 2.0 and b <= peak[sym] * 0.80:
                    sell(p, "trail20")   # past +100%: 20% below the best
                elif b <= entry * SL:
                    sell(p, "sl50")
                continue
            if m >= OUT:
                sell(p, "1557")
            elif sym in held:
                hour = now().hour
                stop = max(entry * 1.5, peak[sym] * 0.70)   # lock +50%, trail 30% below the best
                if b <= stop:
                    sell(p, "trail"); held.pop(sym, None)
                elif h1_checked.get(sym) != hour and now().minute >= 1:   # a new 1H candle closed
                    h1_checked[sym] = hour
                    ok, why = h1_strong(sym[-9])
                    print(f"{now():%H:%M} {sym} 1H check: {'strong, keep' if ok else 'not strong, sell'} ({why})")
                    if not ok:
                        sell(p, "1h"); held.pop(sym, None)
            elif b >= entry * TP:
                ok, why = h1_strong(sym[-9])
                print(f"{now():%H:%M} {sym} +100%, 1H check: {'strong, keep' if ok else 'sell'} ({why})")
                if ok:
                    held[sym] = True; h1_checked[sym] = now().hour
                else:
                    sell(p, "tp100")
            elif b <= entry * SL:
                sell(p, "sl50")
            elif m >= LAST10 and peak[sym] >= entry * 1.2 and b <= peak[sym] * 0.90:
                sell(p, "last10")
    except Exception as e:
        print("sage error", e)
    time.sleep(5)
print("sage done")
