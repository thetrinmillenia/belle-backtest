"""PENNY trade manager (Alpaca PAPER account only).

Started by the Penny relay after each entry (one run per contract). It waits for the fill, then:
  - posts +20%, +50% (take partial), +100% (stop to entry), Target 1 hit
  - exits on: Belle's stop (SPY level), a 50% loss of premium, the trail, or 15:59 ET
  - trail after +50%: 30% below the best price, never giving back more than $50
  - after +100%: trail 20% below the best price, never below +50%
  - after +200%: trail 15% below the best price, never below +100%
  - if Belle fires the other side while this is open: stop tightens to 10% under the current price
Every message is short. The trade is saved to results/paper_trades.csv for Nora.
"""
import os
import sys
import time
import datetime as dt
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
TRADE = "https://paper-api.alpaca.markets"  # PAPER endpoint only
DATA = "https://data.alpaca.markets"
H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"].strip(), "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"].strip()}
HOOK = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
ORDER_ID = os.environ["ORDER_ID"]
SYM = os.environ["SYMBOL"]
LABEL = os.environ.get("LABEL") or SYM
SIDE = os.environ.get("SIDE", "CALLS")
DIR = 1 if SIDE == "CALLS" else -1


def num(name):
    try:
        return float(os.environ.get(name, ""))
    except ValueError:
        return None


SPY_STOP = num("SPY_STOP")
SPY_T1 = num("SPY_T1")


def post(text):
    print(text, flush=True)
    if HOOK:
        try:
            requests.post(HOOK, json={"content": text[:1900]}, timeout=10)
        except Exception:
            pass


def now():
    return dt.datetime.now(ET)


def opposite_alert_since(t0):
    """Belle fired the other side after this entry: Penny bought an opposite contract (client id penny-...)."""
    try:
        r = requests.get(f"{TRADE}/v2/orders", headers=H, timeout=10,
                         params={"status": "all", "after": t0, "limit": 50, "direction": "desc"}).json()
    except Exception:
        return False
    my_cp = SYM[-9]
    for o in r if isinstance(r, list) else []:
        cid = o.get("client_order_id") or ""
        sym = o.get("symbol") or ""
        if cid.startswith("penny-") and len(sym) > 9 and sym[-9] in "CP" and sym[-9] != my_cp:
            return True
    return False


def get_order(oid):
    return requests.get(f"{TRADE}/v2/orders/{oid}", headers=H, timeout=10).json()


def opt_bid():
    r = requests.get(f"{DATA}/v1beta1/options/quotes/latest", params={"symbols": SYM, "feed": "indicative"}, headers=H, timeout=10).json()
    return ((r.get("quotes") or {}).get(SYM) or {}).get("bp")


def spy_price():
    r = requests.get(f"{DATA}/v2/stocks/SPY/trades/latest", params={"feed": "iex"}, headers=H, timeout=10).json()
    return (r.get("trade") or {}).get("p")


def sell():
    o = requests.post(f"{TRADE}/v2/orders", headers=H, timeout=10,
                      json={"symbol": SYM, "qty": "1", "side": "sell", "type": "market", "time_in_force": "day"}).json()
    if "id" not in o:
        post(f"PENNY {LABEL}: sell rejected, check Alpaca")
        return None
    for _ in range(30):
        x = get_order(o["id"])
        if x.get("status") == "filled":
            return float(x["filled_avg_price"])
        time.sleep(2)
    return None


def save(entry, exitp, peak, reason):
    os.makedirs("results", exist_ok=True)
    path = "results/paper_trades.csv"
    new = not os.path.exists(path)
    pct = "" if exitp is None else f"{(exitp / entry - 1) * 100:.0f}"
    with open(path, "a") as fh:
        if new:
            fh.write("date,time_in,time_out,contract,side,entry,exit,best,pct,reason\n")
        fh.write(f"{now().date()},{T_IN},{now():%H:%M},{LABEL},{SIDE},{entry:.2f},{'' if exitp is None else f'{exitp:.2f}'},{peak:.2f},{pct},{reason}\n")


# 1) wait up to 3 minutes for the fill
start = time.time()
while True:
    o = get_order(ORDER_ID)
    st = o.get("status")
    if st == "filled":
        entry = float(o["filled_avg_price"])
        break
    if st in ("canceled", "expired", "rejected"):
        post(f"PENNY {LABEL}: not filled ({st})")
        sys.exit(0)
    if time.time() - start > 180:
        requests.delete(f"{TRADE}/v2/orders/{ORDER_ID}", headers=H, timeout=10)
        post(f"PENNY {LABEL}: not filled in 3 min, canceled")
        sys.exit(0)
    time.sleep(5)
T_IN = f"{now():%H:%M}"
FILL_AT = o.get("filled_at") or dt.datetime.now(dt.timezone.utc).isoformat()
warned = False
last_chk = 0.0
warn_stop = 0.0

# 2) manage
peak = entry
said = set()
reason = ""
while True:
    n = now()
    if n.hour * 60 + n.minute >= 959:
        reason = "15:59"
        break
    try:
        bid = opt_bid()
        spy = spy_price()
    except Exception:
        bid, spy = None, None
    if spy and SPY_STOP and (spy - SPY_STOP) * DIR <= 0:
        reason = "stop"
        break
    if spy and SPY_T1 and "t1" not in said and (spy - SPY_T1) * DIR >= 0:
        said.add("t1")
        post(f"{LABEL} Target 1 hit")
    if bid:
        peak = max(peak, bid)
        gain = bid / entry - 1
        for lvl, msg in ((0.20, "+20%"), (0.50, "+50%, take partial"), (1.00, "+100%, trail tightened, at least +50% locked")):
            if gain >= lvl and lvl not in said:
                said.add(lvl)
                post(f"{LABEL} {msg}")
        stop = entry * 0.5
        if peak >= entry * 1.5:
            stop = max(stop, peak - min(peak * 0.30, 0.50))
        # tighter trail once the trade doubles (Titi, Oct 16): keep the winner running toward the target
        if peak >= entry * 2.0:
            stop = max(stop, peak * 0.80, entry * 1.5)   # trail 20% below the best, lock at least +50%
        if peak >= entry * 3.0:
            stop = max(stop, peak * 0.85, entry * 2.0)   # trail 15% below the best, lock at least +100%
        # opposite Belle alert while this trade is open (Titi, Oct 16): keep the new trade, tighten this one
        if not warned and time.time() - last_chk > 30:
            last_chk = time.time()
            if opposite_alert_since(FILL_AT):
                warned = True
                post(f"{LABEL}: Belle flipped sides, stop tightened to 10% under the current price")
        if warned:
            warn_stop = max(warn_stop, bid * 0.90)   # ratchets up only
            stop = max(stop, warn_stop)
        if bid <= stop:
            reason = "flip" if warned and stop == warn_stop else ("trail" if peak >= entry * 1.5 else "50% stop")
            break
    time.sleep(10)

# 3) exit
exitp = sell()
best = (peak / entry - 1) * 100
if exitp is None:
    post(f"PENNY {LABEL}: exit not confirmed, check Alpaca ({reason})")
else:
    pct = (exitp / entry - 1) * 100
    if reason == "15:59":
        post(f"{LABEL} out 15:59, best {best:+.0f}%, closed {pct:+.0f}%")
    elif reason == "stop":
        post(f"{LABEL} stopped out, closed {pct:+.0f}%")
    else:
        post(f"{LABEL} out ({reason}), best {best:+.0f}%, closed {pct:+.0f}%")
save(entry, exitp, peak, reason)
