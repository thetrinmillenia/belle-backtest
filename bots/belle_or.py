"""BELLE ORB, the 30 minute opening range (ORH / ORL) model on 15m candles (Titi, Oct 25 2026). Runs on GitHub.

Opening range = 9:30 to 10:00 ET high and low. From 10:00 to 12:30 ET, on 15m closes, both directions:
  - Closes through + holds (two 15m closes outside): continuation, trade with the break.
  - Sweeps + closes back inside (a 15m candle pokes out and closes back in): reversal, trade back through the range.
  - Stuck inside: no trade. Patience is a position.
Fib targets on the range: SPY trims at Target 1 and Target 2, all out at Target 3. SPX uses Penny's stop rule E.
Every break is also recorded (5m and 15m candle size, body and volume against the last hour) in results/or_breaks.csv
so Nora can learn whether displacement and volume matter. Backtest Jul to Oct (60 days, 15m): close + hold 14 of 31
hit +10 pts, sweep + back inside 13 of 29. Paper only (Penny). Pearl does not take it until it proves itself.
"""
import csv
import datetime as dt
import os
import sys
import time
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
TRADE = "https://paper-api.alpaca.markets"   # PAPER endpoint only. Never change it.
DATA = "https://data.alpaca.markets"
H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"].strip(), "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"].strip()}
HOOK = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
GH = os.environ.get("GH_TOKEN", "").strip()
REPO = os.environ.get("GITHUB_REPOSITORY", "thetrinmillenia/belle-backtest")
REPLAY = os.environ.get("REPLAY", "").strip()
DRY = os.environ.get("DRY") == "1" or bool(REPLAY)
FORCE = bool(REPLAY)
SPX_MIN, SPX_MAX = 1.50, 2.50
SPY_MAX = 0.60
SPY_QTY = 3


def now():
    return dt.datetime.now(ET)


def post(text):
    print(text)
    if REPLAY:
        return   # test runs print to the GitHub log only, nothing goes to Discord (Titi, Oct 25)
    if HOOK:
        try:
            requests.post(HOOK, json={"content": text[:1900]}, timeout=10)
        except Exception as e:
            print("discord failed", e)


def et(ts):
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(ET)


def ct(m):
    return f"{(m // 60 - 1) % 24:02d}:{m % 60:02d}"


def hm(m):
    return f"{m // 60:02d}:{m % 60:02d}"


n0 = now()
if not FORCE and not (n0.weekday() < 5 and n0.hour == 9):
    print("not the 9 AM ET hour on a weekday, skipping")   # two UTC cron times cover daylight saving
    sys.exit(0)
day = dt.date.fromisoformat(REPLAY) if REPLAY else n0.date()
cal = requests.get(f"{TRADE}/v2/calendar", headers=H, params={"start": str(day), "end": str(day)}, timeout=15).json()
if not cal or cal[0].get("date") != str(day):
    print("market closed today")
    sys.exit(0)


def spy_bars():
    start = dt.datetime.combine(day, dt.time(9, 30), ET)
    end = dt.datetime.combine(day, dt.time(16, 0), ET)
    b = requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, timeout=15,
                     params={"timeframe": "5Min", "start": start.isoformat(), "end": end.isoformat(), "feed": "iex", "limit": 1000}).json().get("bars") or []
    out = []
    for x in b:
        t = et(x["t"])
        out.append({"m": t.hour * 60 + t.minute, "o": x["o"], "h": x["h"], "l": x["l"], "c": x["c"], "v": x.get("v", 0)})
    return out


def spx_ratio():
    """SPX / SPY ratio from the prior day's closes (Yahoo ^GSPC and Alpaca SPY), so it is right before the open
    and in replays. Fallback 10.03."""
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC", params={"interval": "1d", "range": "3mo"},
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()["chart"]["result"][0]
        spx = {dt.datetime.fromtimestamp(t, ET).date(): c for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c}
        d = requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, timeout=15,
                         params={"timeframe": "1Day", "start": str(day - dt.timedelta(days=10)), "end": str(day - dt.timedelta(days=1)),
                                 "feed": "sip"}).json().get("bars") or []
        for b in reversed(d):
            k = et(b["t"]).date()
            if k in spx and 9.5 < spx[k] / b["c"] < 10.5:
                return spx[k] / b["c"]
    except Exception as e:
        print("ratio fallback", e)
    return 10.03


def pdc_spy():
    try:
        d = requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, timeout=15,
                         params={"timeframe": "1Day", "start": str(day - dt.timedelta(days=10)), "end": str(day - dt.timedelta(days=1)),
                                 "feed": "sip"}).json().get("bars") or []
        return d[-1]["c"] if d else None
    except Exception:
        return None


def occ(root, cp, k):
    return f"{root}{day:%y%m%d}{cp}{int(round(k * 1000)):08d}"


def quotes(syms):
    q = requests.get(f"{DATA}/v1beta1/options/quotes/latest", headers=H, timeout=15,
                     params={"symbols": ",".join(syms), "feed": "indicative"}).json().get("quotes") or {}
    return q


def pick(root, cp, px, lo, hi, step):
    """Closest strike to the money whose ask is inside [lo, hi], walking out of the money."""
    base = (int(px // step) * step) if cp == "P" else (int(px // step) * step + step)
    ks = [base - i * step if cp == "P" else base + i * step for i in range(12)]
    syms = [occ(root, cp, k) for k in ks]
    q = quotes(syms)
    for k, s in zip(ks, syms):
        a = (q.get(s) or {}).get("ap")
        if not a:
            continue
        if a > hi:
            continue
        if a < lo:
            return None   # further out is only cheaper
        return {"sym": s, "k": k, "ask": a}
    return None


def tick(p, root):
    if root == "SPY":
        return round(p + 0.004, 2)
    return round(-(-p // 0.05) * 0.05, 2) if p < 3 else round(-(-p // 0.10) * 0.10, 2)


def buy(sym, qty, lim, tag):
    o = requests.post(f"{TRADE}/v2/orders", headers=H, timeout=10,
                      json={"symbol": sym, "qty": str(qty), "side": "buy", "type": "limit", "limit_price": f"{lim:.2f}",
                            "time_in_force": "day", "client_order_id": f"penny-orb-{tag}-{int(time.time() * 1000)}"}).json()
    return o.get("id")


def dispatch(order_id, sym, label, side, spy_stop, spy_t1, why, spy_t2=None, spy_t3=None):
    if not GH:
        post("ORB: no GitHub token, the Penny manager was not started. Check the trade in Alpaca.")
        return
    r = requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/belle-manage.yml/dispatches", timeout=15,
                      headers={"Authorization": f"Bearer {GH}", "Accept": "application/vnd.github+json"},
                      json={"ref": "main", "inputs": {"order_id": order_id, "symbol": sym, "label": label, "side": side,
                                                      "spy_stop": f"{spy_stop:.2f}", "spy_t1": f"{spy_t1:.2f}", "why": why[:200],
                                                      **({"spy_t2": f"{spy_t2:.2f}", "spy_t3": f"{spy_t3:.2f}"} if spy_t3 else {})}})
    print("dispatch", r.status_code, r.text[:200])


def holding():
    try:
        pos = requests.get(f"{TRADE}/v2/positions", headers=H, timeout=10).json()
        return [p["symbol"] for p in pos if len(p.get("symbol", "")) > 15]
    except Exception:
        return []


ratio = spx_ratio()
pdc = pdc_spy()
print("ratio", round(ratio, 4))
state = {"done": False, "inside_posted": False, "rec": set()}
rows = []


def agg15(S):
    out = []
    for m0 in range(570, 960, 15):
        g = [b for b in S if m0 <= b["m"] < m0 + 15]
        if len(g) == 3:
            out.append({"m": m0, "o": g[0]["o"], "h": max(x["h"] for x in g), "l": min(x["l"] for x in g), "c": g[-1]["c"],
                        "v": sum(x.get("v", 0) for x in g)})
    return out


def record(tf, kind, d, bar, ref):
    """Displacement and volume of a break candle against the candles before it (Titi: record, do not filter yet)."""
    key = (tf, kind, d)
    if key in state["rec"] or not ref:
        return
    state["rec"].add(key)
    ar = sum(x["h"] - x["l"] for x in ref) / len(ref)
    av = sum(x.get("v", 0) for x in ref) / len(ref) or 1
    rng = bar["h"] - bar["l"] or 0.01
    rows.append({"date": str(day), "time_et": hm(bar["m"]), "tf": tf, "type": kind, "dir": "up" if d == 1 else "down",
                 "range_x_avg": round(rng / ar, 2) if ar else "", "body_pct": round(abs(bar["c"] - bar["o"]) / rng * 100),
                 "vol_x_avg": round(bar.get("v", 0) / av, 2), "close": round(bar["c"], 2)})


def trade(d, kind, last, orh, orl, stop):
    R = orh - orl
    if kind == "CONTINUATION":
        base = orh if d == 1 else orl
        t1, t2, t3 = base + d * 0.27 * R, base + d * 0.62 * R, base + d * 1.0 * R
    else:   # reversal back through the range
        t1, t2, t3 = (orh + orl) / 2, (orl if d == -1 else orh), (orl - 0.27 * R if d == -1 else orh + 0.27 * R)
    side, cp = ("CALLS", "C") if d == 1 else ("PUTS", "P")
    why = f"ORB {kind} {side}: 30 min range {orl:.1f} to {orh:.1f}, 15m close {last['c']:.1f}"
    spx_k = int(round(last["c"] / 5) * 5)
    spy_k = int(round(last["c"] / ratio))
    notes = []
    if DRY:
        notes.append("test run, no orders")
    elif holding():
        notes.append("Penny already holds an option, no new trade")
    else:
        c = pick("SPXW", cp, last["c"], SPX_MIN, SPX_MAX, 5)
        if c:
            lim = tick(c["ask"], "SPX")
            oid = buy(c["sym"], 1, lim, "SPX")
            if oid:
                notes.append(f"bought 1 SPX {c['k']:g}{cp} at {lim:.2f} (${lim * 100:.0f} total)")
                spx_k = int(c["k"])
                dispatch(oid, c["sym"], f"SPX {c['k']:g}{cp} ORB", side, stop / ratio, t1 / ratio, why, t2 / ratio, t3 / ratio)
        else:
            notes.append(f"SPX skipped, nothing between ${SPX_MIN:.2f} and ${SPX_MAX:.2f}")
        y = pick("SPY", cp, last["c"] / ratio, 0.05, SPY_MAX, 1)
        if y:
            lim = tick(y["ask"], "SPY")
            oid = buy(y["sym"], SPY_QTY, lim, "SPY")
            if oid:
                notes.append(f"bought {SPY_QTY} SPY {y['k']:g}{cp} at {lim:.2f} (${lim * 100 * SPY_QTY:.0f} total)")
                spy_k = int(y["k"])
                dispatch(oid, y["sym"], f"SPY {y['k']:g}{cp} ORB", side, stop / ratio, t1 / ratio, why, t2 / ratio, t3 / ratio)
        else:
            notes.append("SPY skipped, nothing at $0.60 or less")
    if kind == "SWEEP":
        reason = f"Swept the {'ORH' if d == -1 else 'ORL'} {orh if d == -1 else orl:.1f} and closed back inside on the 15m"
    else:
        reason = f"Two 15m closes {'above the ORH' if d == 1 else 'below the ORL'} {orh if d == 1 else orl:.1f}"
    msg = [f"**{side}  {hm(last['m'] + 15)} ET ({ct(last['m'] + 15)} CT)**",
           f"Belle's strike:  SPX {spx_k}{cp}  |  SPY {spy_k}{cp}",
           f"Stop:  SPX {stop:.1f}  |  SPY {stop / ratio:.2f}",
           f"Target 1:  {t1:.1f}  |  Target 2:  {t2:.1f}  |  Target 3:  {t3:.1f}",
           f"Why:  {reason}",
           "PENNY:  " + ("\n".join(notes) or "no trade")]
    post("\n\n".join(msg))


def process(B):
    S = [dict(b, o=b["o"] * ratio, h=b["h"] * ratio, l=b["l"] * ratio, c=b["c"] * ratio) for b in B]
    first = [b for b in S if b["m"] < 600]
    if len(first) < 6:
        return
    orh, orl = max(b["h"] for b in first), min(b["l"] for b in first)
    # record every first 5m break of each side (data only)
    for b in S:
        if b["m"] >= 600:
            ref = [x for x in S if b["m"] - 60 <= x["m"] < b["m"]]
            if b["c"] > orh:
                record("5m", "close outside", 1, b, ref)
            if b["c"] < orl:
                record("5m", "close outside", -1, b, ref)
    F = agg15(S)
    F = [f for f in F if f["m"] >= 600]
    if not F:
        return
    last = F[-1]
    prev = F[-2] if len(F) >= 2 else None
    ref15 = [x for x in agg15(S) if x["m"] < last["m"]][-4:]
    for d in (1, -1):
        edge = orh if d == 1 else orl
        if (last["c"] - edge) * d > 0:
            record("15m", "close outside", d, last, ref15)
        if (last["h"] > orh and last["c"] < orh and d == -1) or (last["l"] < orl and last["c"] > orl and d == 1):
            record("15m", "sweep back inside", d, last, ref15)
    if state["done"] or last["m"] > 12 * 60 + 15:
        return
    if last["h"] > orh and last["c"] < orh:
        state["done"] = True
        trade(-1, "SWEEP", last, orh, orl, last["h"] + 1)
    elif last["l"] < orl and last["c"] > orl:
        state["done"] = True
        trade(1, "SWEEP", last, orh, orl, last["l"] - 1)
    elif prev and prev["c"] > orh and last["c"] > orh:
        state["done"] = True
        trade(1, "CONTINUATION", last, orh, orl, orh - 3)
    elif prev and prev["c"] < orl and last["c"] < orl:
        state["done"] = True
        trade(-1, "CONTINUATION", last, orh, orl, orl + 3)
    elif not state["inside_posted"] and last["m"] >= 10 * 60 + 45 and orl <= last["c"] <= orh:
        state["inside_posted"] = True
        print(f"ORB  11:00 ET (10:00 CT): stuck inside the 30 min range ({orl:.1f} to {orh:.1f}). No trade. Patience is a position.")


def save_rows():
    if not rows:
        return
    os.makedirs("results", exist_ok=True)
    f = "results/or_breaks.csv"
    new = not os.path.exists(f)
    with open(f, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        if new:
            w.writeheader()
        w.writerows(rows)
    print(len(rows), "breaks recorded")


if REPLAY:
    allb = spy_bars()
    for n_ in range(7, len(allb) + 1):
        process(allb[:n_])
    print(rows)
    print("replay done")
    sys.exit(0)

last_m = -1
while True:
    nm = now().hour * 60 + now().minute
    if nm > 12 * 60 + 35:
        break
    try:
        B = spy_bars()
    except Exception as e:
        print("bars failed", e)
        time.sleep(30)
        continue
    B = [b for b in B if b["m"] + 5 <= nm]
    if B and B[-1]["m"] != last_m:
        last_m = B[-1]["m"]
        process(B)
    time.sleep(20)
save_rows()
print("done")
