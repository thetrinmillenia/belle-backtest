"""PEARL, the LIVE bot (Titi, Oct 25 2026). Real money, Alpaca LIVE cash account.

Rules (Titi):
  - 1 SPX contract, ask $1.50 or less ($150 or less per contract). Buys with a limit order only.
  - 1 loss and done for the day. Also done for the day if her day P/L reaches -$150.
  - One trade at a time. Last entry 15:50 ET. Everything out at 15:59 ET no matter what.
  - Week one setups: Window 1 (10:00 to 11:30 ET), the stall break (14:00 to 15:50 ET), EOD (15:00 to 15:50 ET),
    calls and puts both considered.
  - Stops: rule E (43% loss of premium, breakeven after +60%, trail 30% below the best after +100%) plus Belle's
    SPY stop. Exits at Target 3 (fib Symmetrical Price) when the setup gives one, otherwise she rides the trail.
Safety:
  - OFF unless the repo variable PEARL_ON is exactly "true".
  - Live keys come only from PEARL_KEY_ID / PEARL_SECRET_KEY. Penny's paper keys never place an order here.
  - A signal older than 3 minutes is ignored (no stale entries).
  - She only buys options, so the most one trade can lose is what she paid (never more than $150).
  - DRY=1: reads prices and prints what she would do, places no orders (works before the live keys exist).
  - Discord: only the approved messages (entry, +60%, +100%, out, done for the day) go to the Pearl channel
    (secret PEARL_WEBHOOK_URL, Titi adds it herself). Everything else stays in the GitHub log.
"""
import datetime as dt
import os
import sys
import time
from collections import defaultdict
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
LIVE = "https://api.alpaca.markets"        # LIVE trading endpoint. Pearl only.
DATA = "https://data.alpaca.markets"
MAX_ASK, MIN_ASK = 1.50, 0.30
MAX_DAY_LOSS = 150.0
LAST_ENTRY = 15 * 60 + 50
EXIT_MIN = 15 * 60 + 59
WINDOWS = {"W1": (10 * 60, 11 * 60 + 30), "STALL": (14 * 60, LAST_ENTRY), "EOD": (15 * 60, 15 * 60 + 55)}   # EOD to 15:55 like Penny (Oct 27)

DRY = os.environ.get("DRY", "").strip() == "1"
KEY = os.environ.get("PEARL_KEY_ID", "").strip()
SEC = os.environ.get("PEARL_SECRET_KEY", "").strip()
SIDE = os.environ.get("SIDE", "").strip().upper()
SOURCE = os.environ.get("SOURCE", "").strip().upper()
WHY = os.environ.get("WHY", "").strip()
HOOK = os.environ.get("PEARL_WEBHOOK_URL", "").strip()


def num(name):
    try:
        return float(os.environ.get(name, ""))
    except ValueError:
        return None


SPY_STOP, SPY_T3, SENT = num("SPY_STOP"), num("SPY_T3"), num("SENT")


def say(text):
    print(text)   # GitHub log only


def post(text):
    """Approved Pearl messages (Titi, Oct 25) to the Pearl alerts channel. Never on a dry run."""
    print(text)
    if HOOK and not DRY:
        try:
            requests.post(HOOK, json={"content": text[:1900]}, timeout=10)
        except Exception as e:
            print("discord failed", e)


def ct(n):
    return f"{(n.hour - 1) % 24:02d}:{n.minute:02d}"


def now():
    return dt.datetime.now(ET)


def mins():
    n = now()
    return n.hour * 60 + n.minute


# ---------- gates ----------
if os.environ.get("PEARL_ON", "").strip() != "true" and not DRY:
    say("Pearl is OFF (PEARL_ON is not true). Nothing done.")
    sys.exit(0)
if not (KEY and SEC):
    if not DRY:
        say("Pearl has no live keys yet (PEARL_KEY_ID / PEARL_SECRET_KEY). Nothing done.")
        sys.exit(0)
    KEY, SEC = os.environ.get("ALPACA_KEY_ID", "").strip(), os.environ.get("ALPACA_SECRET_KEY", "").strip()
    LIVE = None   # dry run on data only: no account, no orders
H = {"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SEC}
if SIDE not in ("CALLS", "PUTS") or SOURCE not in WINDOWS:
    say(f"Pearl: bad signal (side {SIDE!r}, source {SOURCE!r}). Nothing done.")
    sys.exit(0)
D = 1 if SIDE == "CALLS" else -1
CP = "C" if D == 1 else "P"
n0 = now()
m0 = mins()
lo, hi = WINDOWS[SOURCE]
if not DRY:
    if n0.weekday() >= 5 or not (lo <= m0 <= hi):
        say(f"Pearl: {SOURCE} signal at {n0:%H:%M} ET is outside its window. Nothing done.")
        sys.exit(0)
    if SENT and time.time() - SENT > 180:
        say("Pearl: the signal is older than 3 minutes. Nothing done.")
        sys.exit(0)


def get(url, **params):
    return requests.get(url, headers=H, params=params, timeout=15).json()


def spy_last():
    try:
        return float(get(f"{DATA}/v2/stocks/SPY/trades/latest", feed="iex")["trade"]["p"])
    except Exception:
        return None


def spx_ratio():
    """SPX / SPY ratio from the prior day's closes (Yahoo ^GSPC and Alpaca SPY). Fallback 10.03."""
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC", params={"interval": "1d", "range": "1mo"},
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()["chart"]["result"][0]
        spx = {dt.datetime.fromtimestamp(t, ET).date(): c for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c}
        d = get(f"{DATA}/v2/stocks/SPY/bars", timeframe="1Day", start=str(n0.date() - dt.timedelta(days=10)),
                end=str(n0.date() - dt.timedelta(days=1)), feed="sip").get("bars") or []
        for b in reversed(d):
            k = dt.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET).date()
            if k in spx and 9.5 < spx[k] / b["c"] < 10.5:
                return spx[k] / b["c"]
    except Exception as e:
        print("ratio fallback", e)
    return 10.03


def quote(sym):
    q = (get(f"{DATA}/v1beta1/options/quotes/latest", symbols=sym, feed="indicative").get("quotes") or {}).get(sym) or {}
    return q.get("bp") or 0.0, q.get("ap") or 0.0


def occ(k):
    return f"SPXW{n0:%y%m%d}{CP}{int(round(k * 1000)):08d}"


def pick(spx):
    """Closest strike to the money with an ask from $0.30 to $1.50, walking out of the money."""
    base = int(spx // 5) * 5 + (5 if D == 1 else 0)
    ks = [base + D * 5 * i for i in range(30)]
    syms = [occ(k) for k in ks]
    q = get(f"{DATA}/v1beta1/options/quotes/latest", symbols=",".join(syms), feed="indicative").get("quotes") or {}
    for k, s in zip(ks, syms):
        a = (q.get(s) or {}).get("ap")
        if not a or a > MAX_ASK:
            continue
        if a < MIN_ASK:
            return None
        return {"sym": s, "k": k, "ask": a}
    return None


def tick(p):
    return round(-(-p // 0.05) * 0.05, 2) if p < 3 else round(-(-p // 0.10) * 0.10, 2)


# ---------- today's record (1 loss and done, -$150 day limit, one trade at a time) ----------
if LIVE:
    start = dt.datetime.combine(n0.date(), dt.time(0, 0), ET).isoformat()
    orders = requests.get(f"{LIVE}/v2/orders", headers=H, timeout=15,
                          params={"status": "all", "after": start, "direction": "asc", "limit": 500}).json()
    orders = [o for o in orders if isinstance(o, dict) and str(o.get("client_order_id", "")).startswith("pearl-")]
    if any(o["status"] in ("new", "accepted", "partially_filled", "pending_new") for o in orders):
        say("Pearl: an order is still working. Nothing new.")
        sys.exit(0)
    pos = requests.get(f"{LIVE}/v2/positions", headers=H, timeout=15).json()
    if any(len(p.get("symbol", "")) > 15 for p in (pos if isinstance(pos, list) else [])):
        say("Pearl: already holding an option. One trade at a time.")
        sys.exit(0)
    lots, day_pl, losses = defaultdict(list), 0.0, 0
    for o in orders:
        if not o.get("filled_at"):
            continue
        q, p = int(float(o["filled_qty"])), float(o["filled_avg_price"])
        if o["side"] == "buy":
            lots[o["symbol"]] += [p] * q
        else:
            for _ in range(q):
                if lots[o["symbol"]]:
                    pl = (p - lots[o["symbol"]].pop(0)) * 100
                    day_pl += pl
                    losses += pl < 0
    if losses:
        say("Pearl: she already took a loss today. Done for the day.")
        sys.exit(0)
    if day_pl <= -MAX_DAY_LOSS:
        say(f"Pearl: day P/L {day_pl:+.0f}. Done for the day.")
        sys.exit(0)
    acct = requests.get(f"{LIVE}/v2/account", headers=H, timeout=15).json()
    cash = float(acct.get("options_buying_power") or acct.get("cash") or 0)
else:
    cash = 10_000.0

# ---------- entry ----------
ratio = spx_ratio()
spy = spy_last()
if not spy:
    say("Pearl: no SPY price. Nothing done.")
    sys.exit(0)
if SPY_STOP and ((D == 1 and spy <= SPY_STOP) or (D == -1 and spy >= SPY_STOP)):
    say(f"Pearl: SPY {spy:.2f} is already through Belle's stop {SPY_STOP:.2f}. Nothing done.")
    sys.exit(0)
c = pick(spy * ratio)
if not c:
    say(f"Pearl: no SPX {CP} with an ask from ${MIN_ASK:.2f} to ${MAX_ASK:.2f}. Nothing done.")
    sys.exit(0)
lim = min(tick(c["ask"]), MAX_ASK)
if lim * 100 > cash:
    say(f"Pearl: settled cash ${cash:,.0f} is under ${lim * 100:.0f}. Nothing done.")
    sys.exit(0)
plan = (f"Pearl {SOURCE} {SIDE}: 1 SPX {c['k']}{CP} limit {lim:.2f} (${lim * 100:.0f}). SPY {spy:.2f}, ratio {ratio:.4f}. "
        f"Stop SPY {SPY_STOP}. Target 3 SPY {SPY_T3}. Why: {WHY}")
if DRY:
    say("[DRY, no order] " + plan)
    sys.exit(0)
say(plan)
o = requests.post(f"{LIVE}/v2/orders", headers=H, timeout=15,
                  json={"symbol": c["sym"], "qty": "1", "side": "buy", "type": "limit", "limit_price": f"{lim:.2f}",
                        "time_in_force": "day", "client_order_id": f"pearl-{n0:%Y%m%d-%H%M%S}"}).json()
if "id" not in o:
    say(f"Pearl: buy rejected {str(o)[:200]}")
    sys.exit(1)


def order(oid):
    return requests.get(f"{LIVE}/v2/orders/{oid}", headers=H, timeout=15).json()


entry = None
for _ in range(60):   # up to 2 minutes, she does not chase
    x = order(o["id"])
    if x.get("status") == "filled":
        entry = float(x["filled_avg_price"])
        break
    s = spy_last()
    if s and SPY_STOP and ((D == 1 and s <= SPY_STOP) or (D == -1 and s >= SPY_STOP)):
        break
    time.sleep(2)
if entry is None:
    requests.delete(f"{LIVE}/v2/orders/{o['id']}", headers=H, timeout=15)
    time.sleep(2)
    x = order(o["id"])
    if x.get("status") == "filled":
        entry = float(x["filled_avg_price"])
    else:
        say("Pearl: not filled in 2 minutes, canceled. No chase.")
        sys.exit(0)
say(f"Pearl: filled 1 SPX {c['k']}{CP} at {entry:.2f} (${entry * 100:.0f})")
K = f"SPX {c['k']}{CP}"
nf = now()
post(f"**PEARL {SIDE}  {nf:%H:%M} ET ({ct(nf)} CT)**\n\nBought 1 {K} at {entry:.2f} (${entry * 100:.0f})\n\nWhy:  {WHY}")


def sell():
    s = requests.post(f"{LIVE}/v2/orders", headers=H, timeout=15,
                      json={"symbol": c["sym"], "qty": "1", "side": "sell", "type": "market", "time_in_force": "day",
                            "client_order_id": f"pearl-{now():%Y%m%d-%H%M%S}-out"}).json()
    if "id" not in s:
        say(f"Pearl: SELL REJECTED, check Alpaca now. {str(s)[:200]}")
        return None
    for _ in range(30):
        x = order(s["id"])
        if x.get("status") == "filled":
            return float(x["filled_avg_price"])
        time.sleep(2)
    return None


# ---------- manage: rule E, Belle's SPY stop, Target 3, out at 15:59 ET ----------
peak, reason, be_said, trail_said = entry, None, False, False
while reason is None:
    b, a = quote(c["sym"])
    px = (b + a) / 2 if b and a else b
    if px:
        peak = max(peak, px)
    stop = entry * 0.57
    if peak >= entry * 1.60:
        stop = max(stop, entry)
        if not be_said:
            post(f"{K} +60%, stop moved to breakeven")
            be_said = True
    if peak >= entry * 2.0:
        stop = max(stop, peak * (0.85 if SOURCE == "EOD" else 0.70))
        if not trail_said:
            post(f"{K} +100%, trail now {'15' if SOURCE == 'EOD' else '30'}% below the best")
            trail_said = True
    if SOURCE == "EOD" and peak >= entry * 1.30:   # EOD trail (Titi, Oct 27): 20% below the best from +30%
        stop = max(stop, peak * 0.80)
    s = spy_last()
    if mins() >= EXIT_MIN:
        reason = "15:59"
    elif px and px <= stop:
        reason = "stop"
    elif s and SPY_STOP and ((D == 1 and s <= SPY_STOP) or (D == -1 and s >= SPY_STOP)):
        reason = "Belle stop"
    elif s and SPY_T3 and ((D == 1 and s >= SPY_T3) or (D == -1 and s <= SPY_T3)):
        reason = "Target 3"
    else:
        time.sleep(2 if SOURCE == "EOD" else 5)   # EOD checks every 2 seconds (Titi, Oct 27)

out = sell()
if out is None:
    say(f"Pearl: exit ({reason}) NOT confirmed, check Alpaca now")
    post(f"{K} EXIT NOT CONFIRMED, check Alpaca now")
    sys.exit(1)
pl = (out - entry) * 100
post(f"{K} out ({reason}), best {peak / entry * 100 - 100:+.0f}%, closed {'+' if pl >= 0 else '-'}${abs(pl):.0f}")
if pl < 0:
    post("Done for the day (1 loss)")
os.makedirs("results", exist_ok=True)
f = "results/pearl_trades.csv"
new = not os.path.exists(f)
with open(f, "a") as fh:
    if new:
        fh.write("date,time_in,time_out,source,contract,entry,exit,best,pl,reason,why\n")
    fh.write(f"{n0:%Y-%m-%d},{n0:%H:%M},{now():%H:%M},{SOURCE},{c['sym']},{entry:.2f},{out:.2f},{peak:.2f},{pl:.0f},{reason},\"{WHY.replace(chr(34), '')}\"\n")
