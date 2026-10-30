"""RANGE TRACKER (Titi, Oct 30): the ranges SPX stays in every day, so the bots know what consolidation is.

Runs after the close (ranges.yml). No Discord posts. Writes data/day_ranges.csv, one row per day, SPX points
(SPY x 10.03, the same ratio as the relay):
  range, net (close minus open), morning 09:30 to 11:30, lunch 11:30 to 13:45, afternoon 13:45 to 16:00,
  lunch type (inside the morning range, failed sweep of the high or low, broke the high or low),
  box (how many days in a row SPX stayed inside 1.2% of price, about 90 points), day type,
  the latest 1h and 4h market structure shift (MSS: a candle closes through the last swing against the trend).
Backtest notes (Oct 2025 to Oct 2026): a lunch failed sweep reversed in the afternoon 20 of 31 days; a lunch that broke
out and held kept going only 24 of 42. After two tight days a 100 point day came 6% of the time (21% on all days).
"""
import csv
import datetime as dt
import os
from collections import defaultdict
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
DATA = "https://data.alpaca.markets"
H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"].strip(), "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"].strip()}
K = 10.03
OUT = "data/day_ranges.csv"
BOX_PCT = 0.012     # a box is days whose combined high and low stay within 1.2% of price (about 90 SPX points)
TIGHT = 50          # a day under 50 points is a tight day (the median day is about 58)
BIG = 100           # 100 points or more is an expansion day
COLS = ["date", "open", "high", "low", "close", "range", "net", "morning_range", "lunch_range", "afternoon_range",
        "lunch_type", "box_days", "box_low", "box_high", "box_points", "day_type", "mss_1h", "mss_4h"]


def bars(days_back=60):
    start = (dt.datetime.now(ET) - dt.timedelta(days=days_back)).replace(hour=0, minute=0).astimezone(dt.timezone.utc)
    out, token = [], None
    while True:
        p = {"timeframe": "15Min", "start": start.isoformat(), "feed": "iex", "limit": 10000}
        if token:
            p["page_token"] = token
        j = requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, params=p, timeout=20).json()
        out += j.get("bars") or []
        token = j.get("next_page_token")
        if not token:
            return out


def session(v, a, b):
    x = [r for m, r in v if a <= m < b]
    return (max(r["h"] for r in x), min(r["l"] for r in x), x) if x else None


def lunch_type(M, L):
    mh, ml, _ = M
    lh, ll, lx = L
    lc = lx[-1]["c"]
    if lh > mh and ll < ml:
        return "took both sides"
    if lh > mh:
        return "failed sweep of the high" if lc < mh else "broke the high"
    if ll < ml:
        return "failed sweep of the low" if lc > ml else "broke the low"
    return "inside the morning range"


def htf(days, size):
    """Regular hours 1h (size 60) or 4h (size 240) candles built from the 15m bars: 09:30, 10:30 ... and 09:30, 13:30."""
    out = []
    for d in sorted(days):
        b = {}
        for m, r in sorted(days[d], key=lambda x: x[0]):
            k = (m - 570) // size
            if k not in b:
                b[k] = {"day": d, "t": 570 + k * size, "h": r["h"], "l": r["l"], "c": r["c"]}
            else:
                b[k]["h"], b[k]["l"], b[k]["c"] = max(b[k]["h"], r["h"]), min(b[k]["l"], r["l"]), r["c"]
        out += [b[k] for k in sorted(b)]
    return out


def mss_events(bars):
    """Market structure shift: a candle CLOSES through the last confirmed swing (2 candles each side) against the trend.
    Returns {day: latest shift as of that day's close} as 'bearish 7716 (10-29 09:30)'."""
    sh = sl = None
    trend, last, by_day = None, "", {}
    for j, b in enumerate(bars):
        i = j - 2   # the swing at i is confirmed once candle i+2 has closed
        if i >= 2:
            w = bars[i - 2:i + 3]
            if bars[i]["h"] > max(x["h"] for k, x in enumerate(w) if k != 2):
                sh = bars[i]["h"]
            if bars[i]["l"] < min(x["l"] for k, x in enumerate(w) if k != 2):
                sl = bars[i]["l"]
        when = f"{str(b['day'])[5:]} {b['t'] // 60:02d}:{b['t'] % 60:02d}"
        if sl is not None and b["c"] < sl and trend != "bearish":
            trend, last = "bearish", f"bearish {sl * K:.0f} ({when})"
        elif sh is not None and b["c"] > sh and trend != "bullish":
            trend, last = "bullish", f"bullish {sh * K:.0f} ({when})"
        flip = (f", flips above {sh * K:.0f}" if trend == "bearish" and sh else (f", flips below {sl * K:.0f}" if trend == "bullish" and sl else ""))
        by_day[str(b["day"])] = last + flip
    return by_day


def main():
    days = defaultdict(list)
    for r in bars():
        t = dt.datetime.fromisoformat(r["t"].replace("Z", "+00:00")).astimezone(ET)
        m = t.hour * 60 + t.minute
        if 570 <= m < 960:
            days[t.date()].append((m, r))
    rows = []
    for d in sorted(days):
        v = sorted(days[d], key=lambda x: x[0])
        if len(v) < 20:   # half days and missing data are skipped
            continue
        o, c = v[0][1]["o"], v[-1][1]["c"]
        hi, lo = max(r["h"] for _, r in v), min(r["l"] for _, r in v)
        M, L, A = session(v, 570, 690), session(v, 690, 825), session(v, 825, 960)
        rows.append({"date": str(d), "o": o, "h": hi, "l": lo, "c": c,
                     "m": (M[0] - M[1]) * K if M else "", "lu": (L[0] - L[1]) * K if L else "",
                     "a": (A[0] - A[1]) * K if A else "", "lt": lunch_type(M, L) if M and L else ""})
    m1, m4 = mss_events(htf(days, 60)), mss_events(htf(days, 240))
    out = []
    for i, r in enumerate(rows):
        bh, bl, n = r["h"], r["l"], 1
        for j in range(i - 1, -1, -1):
            h, lo = max(bh, rows[j]["h"]), min(bl, rows[j]["l"])
            if (h - lo) / r["c"] > BOX_PCT:
                break
            bh, bl, n = h, lo, n + 1
        rng = (r["h"] - r["l"]) * K
        kind = "expansion" if rng >= BIG else ("consolidation" if n >= 3 or rng < TIGHT else "normal")
        f = lambda x: f"{x:.0f}" if x != "" else ""
        out.append({"date": r["date"], "open": f(r["o"] * K), "high": f(r["h"] * K), "low": f(r["l"] * K), "close": f(r["c"] * K),
                    "range": f(rng), "net": f((r["c"] - r["o"]) * K), "morning_range": f(r["m"]), "lunch_range": f(r["lu"]),
                    "afternoon_range": f(r["a"]), "lunch_type": r["lt"], "box_days": n, "box_low": f(bl * K),
                    "box_high": f(bh * K), "box_points": f((bh - bl) * K), "day_type": kind,
                    "mss_1h": m1.get(r["date"], ""), "mss_4h": m4.get(r["date"], "")})
    keep = {}
    if os.path.exists(OUT):
        with open(OUT) as fh:
            for r in csv.DictReader(fh):
                keep[r["date"]] = r
    for r in out[1:] if len(out) > 1 else out:   # the first day has no history for its box, the saved row stays
        keep[r["date"]] = r
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for k in sorted(keep):
            w.writerow({c: keep[k].get(c, "") for c in COLS})
    for r in out[-5:]:
        print(r["date"], r["range"], "pts", r["day_type"], "| lunch", r["lunch_range"], r["lunch_type"], "| box", r["box_days"], "days", r["box_points"], "pts", "| 1h", r["mss_1h"], "| 4h", r["mss_4h"])


if __name__ == "__main__":
    main()
