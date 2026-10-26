"""Shared pieces for Penny's watcher bots (ORB and stall). Alpaca PAPER only.

One copy of: time helpers, Discord posting, the SPX/SPY ratio, contract picking, paper orders,
starting Penny's manager and handing a setup to Pearl. Pearl (live) keeps her own code on purpose.
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
REPLAY = os.environ.get("REPLAY", "").strip()   # test: YYYY-MM-DD, replays that day bar by bar, no orders
DRY = os.environ.get("DRY") == "1" or bool(REPLAY)
FORCE = os.environ.get("FORCE") == "1" or bool(REPLAY)


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


def market_day(start_hour, name):
    """The trading day to work on. Live runs only start in their ET hour on a weekday (two UTC start times
    cover daylight saving, the extra one exits here). Exits when the market is closed."""
    n0 = now()
    if not FORCE and not (n0.weekday() < 5 and n0.hour == start_hour):
        print(f"{name}: not the {start_hour:02d}:00 ET hour on a weekday, skipping")
        sys.exit(0)
    day = dt.date.fromisoformat(REPLAY) if REPLAY else n0.date()
    cal = requests.get(f"{TRADE}/v2/calendar", headers=H, params={"start": str(day), "end": str(day)}, timeout=15).json()
    if not cal or cal[0].get("date") != str(day):
        print("market closed today")
        sys.exit(0)
    return day


def spy_bars(day):
    start = dt.datetime.combine(day, dt.time(9, 30), ET)
    end = dt.datetime.combine(day, dt.time(16, 0), ET)
    b = requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, timeout=15,
                     params={"timeframe": "5Min", "start": start.isoformat(), "end": end.isoformat(), "feed": "iex",
                             "limit": 1000}).json().get("bars") or []
    out = []
    for x in b:
        t = et(x["t"])
        out.append({"m": t.hour * 60 + t.minute, "o": x["o"], "h": x["h"], "l": x["l"], "c": x["c"], "v": x.get("v", 0)})
    return out


def _daily_spy(day):
    return requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, timeout=15,
                        params={"timeframe": "1Day", "start": str(day - dt.timedelta(days=10)), "end": str(day - dt.timedelta(days=1)),
                                "feed": "sip"}).json().get("bars") or []


def spx_ratio(day):
    """SPX / SPY ratio from the prior day's closes (Yahoo ^GSPC and Alpaca SPY), so it is right before the open
    and in replays. Fallback 10.03."""
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC", params={"interval": "1d", "range": "3mo"},
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()["chart"]["result"][0]
        spx = {dt.datetime.fromtimestamp(t, ET).date(): c for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c}
        for b in reversed(_daily_spy(day)):
            k = et(b["t"]).date()
            if k in spx and 9.5 < spx[k] / b["c"] < 10.5:
                return spx[k] / b["c"]
    except Exception as e:
        print("ratio fallback", e)
    return 10.03


def pdc_spy(day):
    try:
        d = _daily_spy(day)
        return d[-1]["c"] if d else None
    except Exception:
        return None


def occ(day, root, cp, k):
    return f"{root}{day:%y%m%d}{cp}{int(round(k * 1000)):08d}"


def quotes(syms):
    return requests.get(f"{DATA}/v1beta1/options/quotes/latest", headers=H, timeout=15,
                        params={"symbols": ",".join(syms), "feed": "indicative"}).json().get("quotes") or {}


def pick(day, root, cp, px, lo, hi, step):
    """Closest strike to the money whose ask is inside [lo, hi], walking out of the money."""
    base = (int(px // step) * step) if cp == "P" else (int(px // step) * step + step)
    ks = [base - i * step if cp == "P" else base + i * step for i in range(12)]
    syms = [occ(day, root, cp, k) for k in ks]
    q = quotes(syms)
    for k, s in zip(ks, syms):
        a = (q.get(s) or {}).get("ap")
        if not a or a > hi:
            continue
        if a < lo:
            return None   # further out is only cheaper
        return {"sym": s, "k": k, "ask": a}
    return None


def tick(p, root):
    if root == "SPY":
        return round(p + 0.004, 2)
    return round(-(-p // 0.05) * 0.05, 2) if p < 3 else round(-(-p // 0.10) * 0.10, 2)


def buy(bot, sym, qty, lim, tag):
    o = requests.post(f"{TRADE}/v2/orders", headers=H, timeout=10,
                      json={"symbol": sym, "qty": str(qty), "side": "buy", "type": "limit", "limit_price": f"{lim:.2f}",
                            "time_in_force": "day", "client_order_id": f"penny-{bot}-{tag}-{int(time.time() * 1000)}"}).json()
    return o.get("id")


def _start(workflow, inputs):
    return requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/{workflow}/dispatches", timeout=15,
                         headers={"Authorization": f"Bearer {GH}", "Accept": "application/vnd.github+json"},
                         json={"ref": "main", "inputs": inputs})


def dispatch(bot, order_id, sym, label, side, spy_stop, spy_t1, why, spy_t2=None, spy_t3=None):
    """Start Penny's manager for a filled paper order."""
    if not GH:
        post(f"{bot.upper()}: no GitHub token, the Penny manager was not started. Check the trade in Alpaca.")
        return
    inputs = {"order_id": order_id, "symbol": sym, "label": label, "side": side,
              "spy_stop": f"{spy_stop:.2f}", "spy_t1": f"{spy_t1:.2f}", "why": why[:200]}
    if spy_t3:
        inputs.update({"spy_t2": f"{spy_t2:.2f}", "spy_t3": f"{spy_t3:.2f}"})
    r = _start("belle-manage.yml", inputs)
    print("dispatch", r.status_code, r.text[:200])


def pearl_go(source, side, spy_stop, spy_t3, why):
    """Hand a setup to Pearl (LIVE). Pearl checks PEARL_ON and all her own rules."""
    if not GH:
        return
    r = _start("pearl.yml", {"side": side, "source": source, "spy_stop": f"{spy_stop:.2f}", "spy_t3": f"{spy_t3:.2f}",
                             "why": why[:200], "sent": str(int(time.time()))})
    print("pearl dispatch", r.status_code)


def holding():
    try:
        pos = requests.get(f"{TRADE}/v2/positions", headers=H, timeout=10).json()
        return [p["symbol"] for p in pos if len(p.get("symbol", "")) > 15]
    except Exception:
        return []
