"""FUTURES PAPER (Oct 31 2026): every Belle alert traded as 1 MES on paper, scored after the close. No orders, no Discord.

Why: Alpaca has no futures yet and Tradovate's API needs a funded live account. This shows what Belle's alerts would do
on futures before any real money goes in. Results go to results/futures_paper.csv; Harper reads them.

Alerts = every alert Penny bought (Alpaca buy orders) plus every alert Raven recorded as skipped (results/shadow_trades.csv).
Prices = ES 1 minute bars from Belle's EOD archive (data/archive/ES_<date>_1m.csv). 1 MES = $5 a point.
Rules (v1, to be tuned with Harper):
  entry at the close of the alert's minute, 1 MES, calls = long, puts = short
  stop 20 points, target 40 points (2R), out at 15:55 ET at the latest
  an alert the other way while in a trade = out at that minute (Titi: the opposite alert tells us to get out),
  then the new side is taken; an alert the same way while in a trade is ignored
  costs: about $1.50 a round trip (commission plus exchange fees)
Run: python bots/futures_paper.py                 (today)
     DATES=2026-10-27,2026-10-28 python bots/futures_paper.py   (backfill)
"""
import csv
import datetime as dt
import os
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
TRADE = "https://paper-api.alpaca.markets"   # read only: Penny's PAPER orders, to find the alert times
H = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID", "").strip(), "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET_KEY", "").strip()}
OUT = "results/futures_paper.csv"
STOP, TARGET, LAST_MIN, PT, COST = 20.0, 40.0, 955, 5.0, 1.50   # Oct 27 to 30 test: 20/40 +$78, 15/30 -$237, no target -$262 (13 trades, too few to trust)
COLS = ["date", "time_et", "side", "source", "entry", "exit", "exit_time_et", "reason", "points", "pl", "best_points", "heat_points"]


def alert_list(day):
    out = []
    try:
        od = requests.get(f"{TRADE}/v2/orders", headers=H, timeout=20, params={
            "status": "all", "after": f"{day}T04:00:00Z", "until": f"{day}T21:00:00Z", "direction": "asc", "limit": 500}).json()
        for o in od if isinstance(od, list) else []:
            sym = str(o.get("symbol", ""))
            if o.get("side") != "buy" or len(sym) < 15 or sym[-9] not in "CP":
                continue
            t = dt.datetime.fromisoformat(o["submitted_at"].replace("Z", "+00:00")).astimezone(ET)
            out.append((t.hour * 60 + t.minute, "CALLS" if sym[-9] == "C" else "PUTS", "traded"))
    except Exception as e:
        print("orders not read", e)
    if os.path.exists("results/shadow_trades.csv"):
        with open("results/shadow_trades.csv") as fh:
            for r in csv.DictReader(fh):
                if r["date"] == day and r["side"] in ("CALLS", "PUTS"):
                    h, m = map(int, r["time_et"].split(":"))
                    out.append((h * 60 + m, r["side"], "skipped"))
    out.sort()
    alerts = []
    for m, side, src in out:   # SPX and SPY buys of one alert, and repeats within 2 minutes, are one alert
        if alerts and alerts[-1][1] == side and m - alerts[-1][0] <= 2:
            if src == "traded":
                alerts[-1] = (alerts[-1][0], side, "traded")
            continue
        alerts.append((m, side, src))
    return alerts


def es_bars(day):
    path = f"data/archive/ES_{day}_1m.csv"
    if not os.path.exists(path):
        return []
    bars = []
    with open(path) as fh:
        for r in csv.DictReader(fh):
            t = dt.datetime.fromisoformat(r["Datetime"])
            m = t.hour * 60 + t.minute
            if 570 <= m < 960:
                bars.append((m, float(r["high"]), float(r["low"]), float(r["close"])))
    return bars


def run_day(day):
    bars, alerts = es_bars(day), alert_list(day)
    if not bars or not alerts:
        print(day, "no ES bars" if not bars else "no alerts")
        return []
    rows, pos = [], None   # pos = (alert minute, side, source, entry, best, heat)

    def close(px, m, why):
        a_m, side, src, e, best, heat = pos
        d = 1 if side == "CALLS" else -1
        pts = round((px - e) * d, 2)
        rows.append({"date": day, "time_et": f"{a_m // 60:02d}:{a_m % 60:02d}", "side": side, "source": src, "entry": f"{e:.2f}",
                     "exit": f"{px:.2f}", "exit_time_et": f"{m // 60:02d}:{m % 60:02d}", "reason": why, "points": pts,
                     "pl": round(pts * PT - COST, 2), "best_points": round(best, 2), "heat_points": round(heat, 2)})

    ai = 0
    for m, hi, lo, c in bars:
        if pos:
            a_m, side, src, e, best, heat = pos
            d = 1 if side == "CALLS" else -1
            fav, adv = ((hi - e) if d == 1 else (e - lo)), ((e - lo) if d == 1 else (hi - e))
            if adv >= STOP:   # the stop is checked first inside a minute (the worse case)
                close(e - d * STOP, m, "stop")
                pos = None
            elif fav >= TARGET:
                close(e + d * TARGET, m, "target")
                pos = None
            else:
                pos = (a_m, side, src, e, max(best, fav), max(heat, adv))
            if pos and m >= LAST_MIN:
                close(c, m, "15:55")
                pos = None
        while ai < len(alerts) and alerts[ai][0] <= m:
            a_m, side, src = alerts[ai]
            ai += 1
            if a_m != m or m >= LAST_MIN:
                continue
            if pos and pos[1] != side:
                close(c, m, "opposite alert")
                pos = None
            if not pos:
                pos = (a_m, side, src, c, 0.0, 0.0)
    if pos:
        close(bars[-1][3], bars[-1][0], "close")
    return rows


def main():
    days = [d.strip() for d in os.environ.get("DATES", "").split(",") if d.strip()] or [f"{dt.datetime.now(ET):%Y-%m-%d}"]
    keep = []
    if os.path.exists(OUT):
        with open(OUT) as fh:
            keep = [r for r in csv.DictReader(fh) if r["date"] not in days]
    new = []
    for d in days:
        new += run_day(d)
    rows = sorted(keep + new, key=lambda r: (r["date"], r["time_et"]))
    os.makedirs("results", exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    for r in new:
        print(r["date"], r["time_et"], r["side"], r["source"], r["entry"], "->", r["exit"], r["exit_time_et"], r["reason"], f"{r['points']} pts", f"${r['pl']}")
    if new:
        print("total", f"${sum(float(r['pl']) for r in new):+.2f}", "on", len(new), "trades")


if __name__ == "__main__":
    main()
