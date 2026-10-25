"""9:30 vs 15:50 candle color test on SPY (Titi, Oct 25 2026). Read only, 2 years of Alpaca SIP 1 minute bars.
Checks: does the first candle of the day close the same color as the 15:50 'algo' candle? Several candle sizes."""
import datetime as dt
import os
from collections import defaultdict
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"].strip(), "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"].strip()}
end = dt.date.today()
start = end - dt.timedelta(days=730)
bars, tok = [], None
while True:
    p = {"timeframe": "1Min", "start": f"{start}T13:00:00Z", "end": f"{end}T00:00:00Z", "feed": "sip", "limit": 10000, "adjustment": "raw"}
    if tok:
        p["page_token"] = tok
    j = requests.get("https://data.alpaca.markets/v2/stocks/SPY/bars", headers=H, params=p, timeout=60).json()
    bars += j.get("bars") or []
    tok = j.get("next_page_token")
    if not tok:
        break
day = defaultdict(dict)
for b in bars:
    t = dt.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET)
    day[t.date()][t.hour * 60 + t.minute] = (b["o"], b["c"])


def candle(d, m0, n):
    xs = [d.get(m) for m in range(m0, m0 + n)]
    if not xs[0] or not xs[-1]:
        return None
    o, c = xs[0][0], xs[-1][1]
    return None if c == o else (c > o)


tests = {"1m 9:30 vs 1m 15:50": (570, 1, 950, 1), "5m 9:30 vs 5m 15:50": (570, 5, 950, 5),
         "15m 9:30 vs 10m 15:50 to 16:00": (570, 15, 950, 10), "1m 9:30 vs 10m 15:50 to 16:00": (570, 1, 950, 10),
         "5m 9:30 vs 10m 15:50 to 16:00": (570, 5, 950, 10), "30m 9:30 vs 10m 15:50 to 16:00": (570, 30, 950, 10)}
print(f"SPY {start} to {end}: {len(day)} days, {len(bars)} bars")
for name, (a, na, b, nb) in tests.items():
    n = m = 0
    for d in day.values():
        x, y = candle(d, a, na), candle(d, b, nb)
        if x is None or y is None:
            continue
        n += 1
        m += x == y
    print(f"{name}: {m}/{n} same color = {m / n * 100:.1f}%")
