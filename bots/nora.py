"""NORA, the record keeper (Alpaca PAPER account, read only).

Runs after the close. Pulls today's fills from the paper account, pairs each buy with its sell,
saves them to results/nora_trades.csv and posts a short recap to Discord.
On Fridays it adds a weekly recap from the saved file.
"""
import csv
import os
import sys
import datetime as dt
from collections import defaultdict
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
TRADE = "https://paper-api.alpaca.markets"  # PAPER endpoint, read only here
H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"].strip(), "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"].strip()}
HOOK = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
PATH = "results/nora_trades.csv"

now = dt.datetime.now(ET)
if os.environ.get("FORCE") != "1" and not (now.hour == 16 and now.weekday() < 5):
    print("not 16:xx ET on a weekday, skipping")  # the workflow runs at two UTC times to cover daylight saving
    sys.exit(0)
today = now.date()


def post(text):
    print(text)
    if HOOK:
        requests.post(HOOK, json={"content": text[:1900]}, timeout=10)


def label(sym):
    # SPY261016C00772000 -> SPY 772C ; SPXW261016P07745000 -> SPX 7745P
    root = sym[:-15]
    cp = sym[-9]
    strike = int(sym[-8:]) / 1000
    return f"{'SPX' if root.startswith('SPX') else root} {strike:g}{cp}"


acts = requests.get(f"{TRADE}/v2/account/activities/FILL", headers=H, params={"date": str(today), "direction": "asc", "page_size": 100}, timeout=15).json()
if not isinstance(acts, list):
    acts = []

book = defaultdict(lambda: {"buy": [], "sell": []})
for a in acts:
    book[a["symbol"]][a["side"]].append((float(a["price"]), int(float(a["qty"])), a["transaction_time"]))

rows = []
for sym, b in book.items():
    if not b["buy"]:
        continue
    q_in = sum(q for _, q, _ in b["buy"])
    p_in = sum(p * q for p, q, _ in b["buy"]) / q_in
    q_out = sum(q for _, q, _ in b["sell"])
    p_out = sum(p * q for p, q, _ in b["sell"]) / q_out if q_out else None
    t_in = dt.datetime.fromisoformat(b["buy"][0][2].replace("Z", "+00:00")).astimezone(ET)
    pl = (p_out - p_in) * 100 * q_out if p_out is not None else None
    pct = (p_out / p_in - 1) * 100 if p_out is not None else None
    win = "W1" if t_in.hour * 60 + t_in.minute < 760 else ("W3" if t_in.hour >= 15 else "W2")
    rows.append({"date": str(today), "time": f"{t_in:%H:%M}", "window": win, "contract": label(sym), "qty": q_in,
                 "entry": f"{p_in:.2f}", "exit": "" if p_out is None else f"{p_out:.2f}",
                 "pct": "" if pct is None else f"{pct:.0f}", "pl": "" if pl is None else f"{pl:.0f}"})

os.makedirs("results", exist_ok=True)
new = not os.path.exists(PATH)
with open(PATH, "a", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["date", "time", "window", "contract", "qty", "entry", "exit", "pct", "pl"])
    if new:
        w.writeheader()
    w.writerows(rows)

acct = requests.get(f"{TRADE}/v2/account", headers=H, timeout=10).json()
eq = float(acct.get("equity", 0))
last = float(acct.get("last_equity", eq) or eq)

if not rows:
    post(f"NORA recap {today:%b %d}\nNo trades today | account ${eq:,.2f}")
else:
    closed = [r for r in rows if r["pct"] != ""]
    wins = sum(1 for r in closed if float(r["pct"]) > 0)
    parts = " | ".join(f"{r['contract']} {int(r['pct']):+d}%" if r["pct"] != "" else f"{r['contract']} open" for r in rows)
    by_win = defaultdict(float)
    for r in closed:
        by_win[r["window"]] += float(r["pl"])
    best_w = max(by_win, key=by_win.get) if by_win else "n/a"
    post(f"NORA recap {today:%b %d}\n{len(rows)} trades | {wins} wins | {len(closed) - wins} losses\n{parts}\n"
         f"Best window: {best_w} | Day P/L {eq - last:+,.0f} | account ${eq:,.2f}")

# weekly recap on Fridays
if today.weekday() == 4 and os.path.exists(PATH):
    start = today - dt.timedelta(days=4)
    with open(PATH) as fh:
        wk = [r for r in csv.DictReader(fh) if r["pct"] and start <= dt.date.fromisoformat(r["date"]) <= today]
    if wk:
        wins = sum(1 for r in wk if float(r["pct"]) > 0)
        pl = sum(float(r["pl"]) for r in wk)
        lines = []
        for win in ("W1", "W2", "W3"):
            x = [r for r in wk if r["window"] == win]
            if x:
                lines.append(f"{win}: {len(x)} trades, {sum(1 for r in x if float(r['pct']) > 0)} wins, {sum(float(r['pl']) for r in x):+,.0f}")
        for und in ("SPY", "SPX"):
            x = [r for r in wk if r["contract"].startswith(und)]
            if x:
                lines.append(f"{und}: {len(x)} trades, {sum(1 for r in x if float(r['pct']) > 0)} wins, {sum(float(r['pl']) for r in x):+,.0f}")
        post(f"NORA week of {start:%b %d}\n{len(wk)} trades | {wins} wins | P/L {pl:+,.0f}\n" + "\n".join(lines))
