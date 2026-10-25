"""BELLE STALL, the EOD stall break watcher (Titi, Oct 21 2026). Runs on GitHub every weekday afternoon.

Titi's setup (Oct 21: 7760P $1.10 to $12.10, then 7760C $0.65 to $4.40):
  - STALL: the last 60 minutes stay in a range of 10 SPX points or less, the high (or low) is tapped at least twice
    within 3 points (EQH / EQL) and price sits within 5 points of the day high (or low).
  - BREAK: a 5m close below the stall (puts) or above it (calls), 14:00 to 15:30 ET. Allowed against the day's trend.
  - TARGET: 50% of the day's overall swing (day high to day low). Oct 21 retraced exactly that far.
  - Puts are favored EOD (backtest: above PDC at 15:00, down 67% of days).
  - Backtest Jul 29 to Oct 21 (59 days): 8 stall breaks, 7 hit +10 SPX pts, +35 pts; both Oct 21 trades caught.
Posts to Discord (#belle-alerts): the 15:00 EOD STALL CHECK, the STALL BREAK, and a REVERSAL WATCH (post only).
On a STALL BREAK, Penny buys 1 SPX + 3 SPY on the Alpaca PAPER account and the Penny manager runs the trade
(label "STALL": SPX holds, no trims, Belle's stop + 60% floor, out at the target; SPY trims as usual).
"""
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
FORCE = os.environ.get("FORCE") == "1"
REPLAY = os.environ.get("REPLAY", "").strip()   # test: YYYY-MM-DD, replays that day bar by bar, no orders
DRY = os.environ.get("DRY") == "1" or bool(REPLAY)   # test: post with [TEST] and no orders

STALL_RANGE = 10.0   # SPX points over the last 60 minutes (12 x 5m)
TAP = 3.0            # EQH / EQL tolerance, SPX points
NEAR = 5.0           # stall must sit within 5 points of the day high / low
SPX_MIN, SPX_MAX = 1.50, 2.50   # SPX premium: cheap far out contracts lost 6 of 7 (Oct 16 to 21)
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
if REPLAY:
    FORCE = True
if not FORCE and not (n0.weekday() < 5 and n0.hour == 13):
    print("not the 13:00 ET hour on a weekday, skipping")   # two UTC cron times cover daylight saving
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
        out.append({"m": t.hour * 60 + t.minute, "o": x["o"], "h": x["h"], "l": x["l"], "c": x["c"]})
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
                            "time_in_force": "day", "client_order_id": f"penny-stall-{tag}-{int(time.time() * 1000)}"}).json()
    return o.get("id")


def dispatch(order_id, sym, label, side, spy_stop, spy_t1, why, spy_t2=None, spy_t3=None):
    if not GH:
        post("STALL: no GitHub token, the Penny manager was not started. Check the trade in Alpaca.")
        return
    r = requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/belle-manage.yml/dispatches", timeout=15,
                      headers={"Authorization": f"Bearer {GH}", "Accept": "application/vnd.github+json"},
                      json={"ref": "main", "inputs": {"order_id": order_id, "symbol": sym, "label": label, "side": side,
                                                      "spy_stop": f"{spy_stop:.2f}", "spy_t1": f"{spy_t1:.2f}", "why": why[:200],
                                                      **({"spy_t2": f"{spy_t2:.2f}", "spy_t3": f"{spy_t3:.2f}"} if spy_t3 else {})}})
    print("dispatch", r.status_code, r.text[:200])


def pearl_go(side, spy_stop, spy_t3, why):
    """Hand the stall entry to Pearl (LIVE). Pearl checks PEARL_ON and all her own rules."""
    if not GH:
        return
    r = requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/pearl.yml/dispatches", timeout=15,
                      headers={"Authorization": f"Bearer {GH}", "Accept": "application/vnd.github+json"},
                      json={"ref": "main", "inputs": {"side": side, "source": "STALL", "spy_stop": f"{spy_stop:.2f}",
                                                      "spy_t3": f"{spy_t3:.2f}", "why": why[:200], "sent": str(int(time.time()))}})
    print("pearl dispatch", r.status_code)


def holding():
    try:
        pos = requests.get(f"{TRADE}/v2/positions", headers=H, timeout=10).json()
        return [p["symbol"] for p in pos if len(p.get("symbol", "")) > 15]
    except Exception:
        return []


ratio = spx_ratio()
pdc = pdc_spy()
print("ratio", round(ratio, 4), "pdc", pdc)
checked = False
fired = None      # (dir, extreme_spy, break_minute)
rev_posted = False
pend = None       # stall break waiting for the OTE pullback (Titi, Oct 25)


def enter(d, start, ext, last, why_base):
    """Penny's entry at the OTE pullback. Fib on the move: 1 = stall extreme (start), 0 = the break's extreme.
    Stop beyond 1. SPY trims at -0.27 and -0.62, everything out at -1. SPX holds (no trims)."""
    R = abs(start - ext)
    t1, t2, t3 = ext + d * 0.27 * R, ext + d * 0.62 * R, ext + d * 1.0 * R
    side = "PUTS" if d == -1 else "CALLS"
    cp = "P" if d == -1 else "C"
    why = f"{why_base}. OTE entry {last['c']:.1f}"
    if not DRY:
        pearl_go(side, start / ratio, t3 / ratio, f"Stall break at the {'high' if d == -1 else 'low'}, OTE pullback rejected")
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
                dispatch(oid, c["sym"], f"SPX {c['k']:g}{cp} STALL FIB", side, start / ratio, t1 / ratio, why, t2 / ratio, t3 / ratio)
        else:
            notes.append(f"SPX skipped, nothing between ${SPX_MIN:.2f} and ${SPX_MAX:.2f}")
        y = pick("SPY", cp, last["c"] / ratio, 0.05, SPY_MAX, 1)
        if y:
            lim = tick(y["ask"], "SPY")
            oid = buy(y["sym"], SPY_QTY, lim, "SPY")
            if oid:
                notes.append(f"bought {SPY_QTY} SPY {y['k']:g}{cp} at {lim:.2f} (${lim * 100 * SPY_QTY:.0f} total)")
                spy_k = int(y["k"])
                dispatch(oid, y["sym"], f"SPY {y['k']:g}{cp} STALL FIB", side, start / ratio, t1 / ratio, why, t2 / ratio, t3 / ratio)
        else:
            notes.append("SPY skipped, nothing at $0.60 or less")
    msg = [f"**{side}  {hm(last['m'] + 5)} ET ({ct(last['m'] + 5)} CT)**",
           f"Belle's strike:  SPX {spx_k}{cp}  |  SPY {spy_k}{cp}",
           f"Stop:  SPX {start:.1f}  |  SPY {start / ratio:.2f}",
           f"Target 1:  {t1:.1f}  |  Target 2:  {t2:.1f}  |  Target 3:  {t3:.1f}",
           f"Why:  Stall break at the {'high' if d == -1 else 'low'}, OTE pullback rejected",
           "PENNY:  " + ("\n".join(notes) or "no trade")]
    post("\n\n".join(msg))


def process(B):
    global checked, fired, rev_posted, pend
    S = [dict(b, o=b["o"] * ratio, h=b["h"] * ratio, l=b["l"] * ratio, c=b["c"] * ratio) for b in B]
    hod = max(b["h"] for b in S)
    lod = min(b["l"] for b in S)
    mid = (hod + lod) / 2
    last = S[-1]
    above = pdc and last["c"] / ratio >= pdc

    # 15:00 ET: the EOD STALL CHECK (part of the EOD read)
    if not checked and last["m"] >= 14 * 60 + 55:
        checked = True
        W = S[-13:-1] if len(S) > 13 else S[:-1]
        hi, lo = max(b["h"] for b in W), min(b["l"] for b in W)
        taps_h = sum(1 for b in W if b["h"] >= hi - TAP)
        taps_l = sum(1 for b in W if b["l"] <= lo + TAP)
        stall = hi - lo <= STALL_RANGE
        where = ("at the HIGH" if hod - hi <= NEAR else ("at the LOW" if lo - lod <= NEAR else "mid range"))
        lines = [f"**EOD STALL CHECK  15:00 ET (14:00 CT)**",
                 f"Last 60 min range: {hi - lo:.1f} pts ({'STALL' if stall else 'no stall'}), {where}. "
                 f"High taps {taps_h}, low taps {taps_l}.",
                 f"Day high {hod:.1f} | day low {lod:.1f} | 50% of the day's swing {mid:.1f}",
                 f"SPX {'ABOVE' if above else 'BELOW'} PDC: puts are favored EOD{' (above PDC: down 67% of days)' if above else ''}.",
                 (f"Watch: a 5m close below {lo:.1f} = STALL BREAK puts, target {mid:.1f}." if stall and where == "at the HIGH" else
                  f"Watch: a 5m close above {hi:.1f} = STALL BREAK calls, target {mid:.1f}." if stall and where == "at the LOW" else
                  "No stall at the extreme yet. No EOD stall trade unless one forms by 15:30 ET.")]
        if fired:
            lines[-1] = f"STALL BREAK already fired at {hm(fired[2] + 5)} ET ({ct(fired[2] + 5)} CT). Stop SPX {fired[1]:.1f}. Hold for the target."
        post("\n\n".join(lines))

    # STALL BREAK, 14:00 to 15:30 ET, once a day
    if fired is None and 14 * 60 <= last["m"] <= 15 * 60 + 30 and len(S) >= 14:
        W = S[-13:-1]
        hi, lo = max(b["h"] for b in W), min(b["l"] for b in W)
        pre_hod = max(b["h"] for b in S[:-1])
        pre_lod = min(b["l"] for b in S[:-1])
        if hi - lo <= STALL_RANGE:
            for d in (-1, 1):
                taps = sum(1 for b in W if (b["h"] >= hi - TAP if d == -1 else b["l"] <= lo + TAP))
                near = (pre_hod - hi <= NEAR) if d == -1 else (lo - pre_lod <= NEAR)
                brk = last["c"] < lo if d == -1 else last["c"] > hi
                if taps >= 2 and near and brk:
                    side = "PUTS" if d == -1 else "CALLS"
                    cp = "P" if d == -1 else "C"
                    stop_spx = hi if d == -1 else lo
                    tgt = mid if (mid - last["c"]) * d >= 5 else last["c"] + d * 20
                    fired = (d, stop_spx, last["m"])
                    why = (f"STALL BREAK {side}: 60 min range {hi - lo:.1f} pts at the day {'high' if d == -1 else 'low'}, "
                           f"{taps} taps, 5m close {last['c']:.1f} through {lo if d == -1 else hi:.1f}. Target 50% of the day's swing")
                    msg = [f"**STALL BREAK {side}  {hm(last['m'] + 5)} ET ({ct(last['m'] + 5)} CT)**",
                           f"Stall {lo:.1f} to {hi:.1f} broke {'lower' if d == -1 else 'higher'}",
                           f"Why:  60 min stall at the {'high' if d == -1 else 'low'} of day, 5m close {'below' if d == -1 else 'above'} the stall"]
                    pend = {"d": d, "start": stop_spx, "ext": last["l"] if d == -1 else last["h"], "why": why}
                    post("\n\n".join(msg))
                    break

    # OTE ENTRY after a stall break (Titi, Oct 25: ICT fib, enter on the 0.62 to 0.79 pullback)
    if pend and last["m"] > fired[2]:
        d, start = pend["d"], pend["start"]
        if (d == -1 and last["c"] > start) or (d == 1 and last["c"] < start) or last["m"] > 15 * 60 + 45:
            print(f"STALL BREAK {'PUTS' if d == -1 else 'CALLS'}: canceled, {'5m close back above the stall' if last['m'] <= 15 * 60 + 45 else 'no OTE pullback by 15:50 ET'}. No trade.")
            pend = None
        else:
            R = abs(start - pend["ext"])
            z1, z2 = pend["ext"] - d * 0.62 * R, pend["ext"] - d * 0.79 * R   # zone toward the start
            touched = (last["h"] >= z1) if d == -1 else (last["l"] <= z1)
            rejected = (last["c"] < last["o"]) if d == -1 else (last["c"] > last["o"])
            if touched and rejected and R >= 5:
                enter(d, start, pend["ext"], last, pend["why"])
                pend = None
            else:
                pend["ext"] = min(pend["ext"], last["l"]) if d == -1 else max(pend["ext"], last["h"])

    # REVERSAL WATCH after the break: a sweep of a key level then a 5m close back across it (post only)
    if fired and not rev_posted and last["m"] <= 15 * 60 + 45 and last["m"] > fired[2]:
        d = fired[0]
        after = [b for b in S if b["m"] > fired[2]]
        ext = min(b["l"] for b in after) if d == -1 else max(b["h"] for b in after)
        lv = {"50% of the day's swing": mid}
        if pdc:
            lv["PDC"] = pdc * ratio
        swept = [(k, v) for k, v in lv.items() if (ext <= v + 1.5 if d == -1 else ext >= v - 1.5)]
        if swept and (last["c"] > swept[0][1] and last["c"] > last["o"] if d == -1 else last["c"] < swept[0][1] and last["c"] < last["o"]):
            rev_posted = True
            post(f"**REVERSAL WATCH {'CALLS' if d == -1 else 'PUTS'}  {hm(last['m'] + 5)} ET ({ct(last['m'] + 5)} CT)**\n\n"
                 f"Swept {swept[0][0]} {swept[0][1]:.1f} (extreme {ext:.1f}) and closed back {'above' if d == -1 else 'below'} at "
                 f"{last['c']:.1f}. Stop: {ext:.1f}. Post only, Penny does not trade it yet.")


if REPLAY:
    allb = spy_bars()
    for n_ in range(14, len(allb) + 1):
        process(allb[:n_])
    print("replay done")
    sys.exit(0)

last_m = -1
while True:
    n = now()
    nm = n.hour * 60 + n.minute
    if nm > 15 * 60 + 52:   # last entry on the 15:50 ET close (Titi, Oct 25)
        break
    try:
        B = spy_bars()
    except Exception as e:
        print("bars failed", e)
        time.sleep(30)
        continue
    B = [b for b in B if b["m"] + 5 <= nm]   # closed 5m bars only
    if B and B[-1]["m"] != last_m:
        last_m = B[-1]["m"]
        process(B)
    time.sleep(20)
print("done")
