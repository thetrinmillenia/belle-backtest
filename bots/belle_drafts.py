"""BELLE DRAFTS, the morning posts (Titi, Oct 21 2026). Runs on GitHub every weekday morning.

8:20 AM ET (7:20 AM CT): message 1, the same opener every day, then message 2, the game plan.
Both go to Titi's private #belle-drafts channel (webhook "Trin Millenia (WILL NOT DM FIRST)").
She copies them into the community. @everyone is in the text but does not ping in the private channel.
Read only. SPY data from Alpaca. Webhook link lives only in the GitHub secret STUDENT_WEBHOOK_URL.
"""
import datetime as dt
import os
import sys
import time
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
TRADE = "https://paper-api.alpaca.markets"   # read only here (market calendar)
DATA = "https://data.alpaca.markets"
H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"].strip(), "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"].strip()}
HOOK = os.environ.get("STUDENT_WEBHOOK_URL", "").strip()
FORCE = os.environ.get("FORCE") == "1"

if not HOOK:
    print("STUDENT_WEBHOOK_URL not set, nothing to do")
    sys.exit(0)
now = dt.datetime.now(ET)
if not FORCE and not (now.weekday() < 5 and now.hour == 8):
    print("not the 8 AM ET hour on a weekday, skipping")   # two UTC cron times cover daylight saving
    sys.exit(0)
day = now.date()
cal = requests.get(f"{TRADE}/v2/calendar", headers=H, params={"start": str(day), "end": str(day)}, timeout=15).json()
if not cal or cal[0].get("date") != str(day):
    print("market closed today")
    sys.exit(0)
# wait for 8:20 AM ET (GitHub starts scheduled jobs a few minutes late, so the job is scheduled early)
if not FORCE:
    go = now.replace(hour=8, minute=20, second=0, microsecond=0)
    if now < go:
        time.sleep((go - now).total_seconds())


def send(text):
    r = requests.post(HOOK, json={"content": text[:1900], "allowed_mentions": {"parse": []}}, timeout=15)
    print("posted", r.status_code)
    time.sleep(2)


# Message 1: the same line every day (Titi, Oct 21)
send("LET'S GET THIS 🧀!\n\nLooking for 100% setups for yall!\n@everyone")

# Message 2: the game plan
lv = {}
spy = None
try:
    d = requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, timeout=15,
                     params={"timeframe": "1Day", "start": str(day - dt.timedelta(days=10)), "end": str(day - dt.timedelta(days=1)),
                             "feed": "sip", "adjustment": "raw"}).json().get("bars") or []
    if d:
        lv["PDH (prior day high)"] = d[-1]["h"]
        lv["PDC (prior day close)"] = d[-1]["c"]
        lv["PDL (prior day low)"] = d[-1]["l"]
except Exception as e:
    print("daily bars failed", e)
try:
    start = dt.datetime.combine(day, dt.time(4, 0), ET)
    end = dt.datetime.now(ET) - dt.timedelta(minutes=16)   # free data: SIP bars must be 15 minutes old
    b = requests.get(f"{DATA}/v2/stocks/SPY/bars", headers=H, timeout=15,
                     params={"timeframe": "1Min", "start": start.isoformat(), "end": end.isoformat(), "feed": "sip", "limit": 1000}).json().get("bars") or []
    if b:
        lv["Premarket high"] = max(x["h"] for x in b)
        lv["Premarket low"] = min(x["l"] for x in b)
except Exception as e:
    print("premarket bars failed", e)
try:
    spy = requests.get(f"{DATA}/v2/stocks/SPY/trades/latest", headers=H, params={"feed": "iex"}, timeout=15).json()["trade"]["p"]
except Exception as e:
    print("latest trade failed", e)

pdc = lv.get("PDC (prior day close)")
L = ["**Game plan for today**", ""]
if spy and pdc:
    up = spy >= pdc
    L += [f"Bias: {'Bullish lean 📈' if up else 'Bearish lean 📉'}",
          f"• SPY is at {spy:.2f}, {'above' if up else 'below'} PDC by {abs(spy - pdc):.2f}", ""]
if lv:
    L.append("Key levels (SPY), high to low:")
    rows = sorted(lv.items(), key=lambda kv: -kv[1])
    placed = spy is None
    for name, px in rows:
        if not placed and spy >= px:
            L.append(f"• ▶ SPY now: {spy:.2f}")
            placed = True
        L.append(f"• {name}: {px:.2f}")
    if not placed:
        L.append(f"• ▶ SPY now: {spy:.2f}")
    L.append("")
L += ["What I want to see:",
      "• The opening range (ORH and ORL) set by 9:45 AM ET (8:45 AM CT)",
      "• A sweep of a key level and a reclaim before any entry",
      "• Window 1 entries from 10:00 AM ET (9:00 AM CT)",
      "", "@everyone"]
send("\n".join(L))
