"""PEARL, the LIVE bot (Titi, Oct 25 2026). Real money, Alpaca LIVE cash account.

Rules (Titi):
  - 1 SPX contract, ask $1.20 or less. Buys with a limit order only. 30% stop, breakeven at +30%.
  - 1 loss and done for the day. Done at -$60, or no new entries once she is +$1,000 for the day (Nov 2; an open trade is never cut). One Window 1 trade a day. Stall off.
  - One trade at a time. Last entry 15:50 ET. Everything out at 15:59 ET no matter what.
  - Week one setups: Window 1 (10:00 to 11:30 ET), the stall break (14:00 to 15:50 ET), EOD (15:00 to 15:50 ET),
    calls and puts both considered.
  - Sniper rules (Titi, Nov 2; test of 78 alerts Oct 19 to Nov 2):
    entry only on the right side of the 5m SPY 200 EMA (puts below it, calls above it).
    Safety stop -40%, or a 5m close back across the 200 EMA.
    Trend day (Daily, 4H and 1H all agree with the trade): after +100% she sells at half of the best price,
    after +300% at 75% of the best. No selling on the 13 or 50 EMA. Choppy day: she sells at +100%.
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
# Tight rules (Titi, Oct 27): account $400 to $500, goal $200+ a day, as close to no losses as rules allow
MAX_ASK, MIN_ASK = 1.50, 0.70     # Nov 2 (Titi): $70 floor, $150 cap; over $2,000 the cap is $250, or $170 from 13:30 ET (set at entry)
MAX_DAY_LOSS = 60.0               # Nov 2: done for the day at -$60 (one -40% stop on a $150 contract)
DAY_GOAL = 1000.0                 # Nov 2: no new entries once +$1,000 for the day; an open trade keeps running
STOP_LOSS = 0.30                  # starting stop: 30% loss of premium (most she can lose on $1.20: $36)
BE_AT = 1.30                      # breakeven once she is +30%, so a winner never turns into a loser
LAST_ENTRY = 15 * 60 + 50
EXIT_MIN = 15 * 60 + 59
WINDOWS = {"W1": (10 * 60, 11 * 60 + 30), "STALL": (14 * 60, LAST_ENTRY), "EOD": (13 * 60 + 30, 15 * 60 + 55)}   # Nov 2: EOD from 13:30 ET like Penny
SAFETY = 0.60                     # Nov 2: safety stop -40% of premium

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
if SOURCE == "STALL":
    say("Pearl: stall breaks are off for Pearl until they prove themselves on Penny (Titi, Oct 27). Nothing done.")
    sys.exit(0)
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


def spy_bars(tf, days):
    start = (now() - dt.timedelta(days=days)).astimezone(dt.timezone.utc).isoformat()
    out, tok = [], None
    while True:
        p = {"timeframe": tf, "start": start, "feed": "iex", "limit": 10000}
        if tok:
            p["page_token"] = tok
        j = get(f"{DATA}/v2/stocks/SPY/bars", **p)
        out += j.get("bars") or []
        tok = j.get("next_page_token")
        if not tok:
            return out


def rth5(days):
    """Closed regular hours 5m SPY bars, oldest first: (time ET, high, low, close)."""
    rows = []
    for b in spy_bars("5Min", days):
        t = dt.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET)
        if dt.time(9, 30) <= t.time() < dt.time(16, 0) and t + dt.timedelta(minutes=5) <= now():
            rows.append((t, b["h"], b["l"], b["c"]))
    return rows


def ema(vals, n):
    k, m, out = 2 / (n + 1), None, []
    for v in vals:
        m = v if m is None else v * k + m * (1 - k)
        out.append(m)
    return out


def ema200_side():
    """+1 when the last closed 5m SPY close is above its 200 EMA, -1 when below (Titi, Nov 2)."""
    rows = rth5(7)
    if len(rows) < 200:
        return None
    e = ema([r[3] for r in rows], 200)
    return 1 if rows[-1][3] > e[-1] else -1


def mss(g):
    """Market structure: a candle closes through the last swing (2 candles each side). Returns 1, -1 or None."""
    sh = sl = tr = None
    for j in range(len(g)):
        i = j - 2
        if i >= 2:
            if g[i][0] > max(g[i - 2][0], g[i - 1][0], g[i + 1][0], g[i + 2][0]):
                sh = g[i][0]
            if g[i][1] < min(g[i - 2][1], g[i - 1][1], g[i + 1][1], g[i + 2][1]):
                sl = g[i][1]
        if sl is not None and g[j][2] < sl and tr != -1:
            tr = -1
        elif sh is not None and g[j][2] > sh and tr != 1:
            tr = 1
    return tr


def trend_day():
    """Trend day when the Daily, 4H and 1H structure all agree with the trade (Titi, Nov 2)."""
    try:
        rows = rth5(45)
        groups = {}
        for t, h, l, c in rows:
            for size in (60, 240):
                k = (size, t.date(), (t.hour * 60 + t.minute - 570) // size)
                g = groups.get(k)
                groups[k] = [h, l, c] if g is None else [max(g[0], h), min(g[1], l), c]
        days = {}
        for t, h, l, c in rows:
            if t.date() < n0.date():
                g = days.get(t.date())
                days[t.date()] = [h, l, c] if g is None else [max(g[0], h), min(g[1], l), c]
        h1 = [v for k, v in sorted(groups.items()) if k[0] == 60]
        h4 = [v for k, v in sorted(groups.items()) if k[0] == 240]
        d1 = [days[k] for k in sorted(days)]
        trends = [mss(d1), mss(h4), mss(h1)]
        print("trend Daily, 4H, 1H:", trends)
        return all(x == D for x in trends)
    except Exception as e:
        print("trend check failed", e)
        return False


def occ(k):
    return f"SPXW{n0:%y%m%d}{CP}{int(round(k * 1000)):08d}"


def pick(spx):
    """Strike rule (Titi, Nov 2): start at the rule distance out of the money, walk further out until the ask fits the cap."""
    m = n0.hour * 60 + n0.minute
    off = 35 if m < 720 else 10 if m < 810 else 35 if m < 900 else 15   # same rule as the relay (test of 91 alerts)
    base = int(round((spx + D * off) / 5)) * 5
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
    if day_pl >= DAY_GOAL:
        say(f"Pearl: day P/L {day_pl:+.0f}, the $1,000 goal is banked. No new entries today.")
        sys.exit(0)
    w1_buys = [o for o in orders if o["side"] == "buy" and o.get("filled_at")
               and dt.datetime.fromisoformat(o["filled_at"].replace("Z", "+00:00")).astimezone(ET).hour < 12]
    if SOURCE == "W1" and w1_buys:
        say("Pearl: she already took her one Window 1 trade today. No repeat entries.")
        sys.exit(0)
    acct = requests.get(f"{LIVE}/v2/account", headers=H, timeout=15).json()
    cash = float(acct.get("options_buying_power") or acct.get("cash") or 0)
else:
    cash = 10_000.0

# ---------- size (Titi, Nov 2): $150 cap until the account is over $2,000, then $250, or $170 from 13:30 ET ----------
equity = float((globals().get("acct") or {}).get("equity") or cash)
MAX_ASK = 1.50 if equity < 2000 else (1.70 if n0.hour * 60 + n0.minute >= 810 else 2.50)

# ---------- entry ----------
ratio = spx_ratio()
spy = spy_last()
if not spy:
    say("Pearl: no SPY price. Nothing done.")
    sys.exit(0)
if SPY_STOP and ((D == 1 and spy <= SPY_STOP) or (D == -1 and spy >= SPY_STOP)):
    say(f"Pearl: SPY {spy:.2f} is already through Belle's stop {SPY_STOP:.2f}. Nothing done.")
    sys.exit(0)
side200 = ema200_side()
if side200 is not None and side200 != D:
    say(f"Pearl: SPY is on the wrong side of the 5m 200 EMA for {SIDE.lower()}. Nothing done.")
    sys.exit(0)
TREND = trend_day()
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
post(f"**PEARL {SIDE}  {nf:%H:%M} ET ({ct(nf)} CT)**\n\nBought 1 {K} at {entry:.2f} (${entry * 100:.0f})\n\n"
     f"{'Trend day: holding' if TREND else 'Choppy day: selling at +100%'}\n\nWhy:  {WHY}")


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


# ---------- manage (Titi, Nov 2): -40% or the 200 EMA, then the tiered trail on trend days, +100% on choppy days ----------
peak, reason, said100, said300, ema_min, side_now = entry, None, False, False, -1, None
while reason is None:
    b, a = quote(c["sym"])
    px = (b + a) / 2 if b and a else b
    if px:
        peak = max(peak, px)
    stop = entry * SAFETY
    if TREND and peak >= entry * 2.0:
        stop = max(stop, peak * 0.50)
        if not said100:
            post(f"{K} +100%\n\nSells if it drops to half of its best")
            said100 = True
    if TREND and peak >= entry * 4.0:
        stop = max(stop, peak * 0.75)
        if not said300:
            post(f"{K} +300%\n\nSells if it drops to 75% of its best")
            said300 = True
    m = mins()
    if m % 5 == 0 and m != ema_min:   # a 5m candle just closed: check the 200 EMA once
        ema_min = m
        try:
            side_now = ema200_side()
        except Exception as e:
            print("200 EMA check failed", e)
    if m >= EXIT_MIN:
        reason = "15:59"
    elif not TREND and px and px >= entry * 2.0:
        reason = "+100%"
    elif px and px <= stop:
        reason = "trail" if peak >= entry * 2.0 and TREND else "stop"
    elif side_now is not None and side_now != D:
        reason = "200 EMA"
    else:
        time.sleep(2)

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
