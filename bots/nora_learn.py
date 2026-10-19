"""NORA, the teacher: the loss library (Titi, Oct 19 2026). Runs right after the Nora recap, every weekday.

1) Reads every trade she can find:
   - Titi's Journal tab and Penny's tab in the "ATM Method - Trading Journal" sheet (through the sheet's Nora web app)
   - Penny's own trade log from the manager (results/penny_trades.csv), so nothing depends on manual logging
2) Tags each trade by setup (Strat, sweep, CISD, RB, OB, EOD fade), window, time of day (lunch chop),
   exit (50% stop, breakeven, trail) and "was up 20%+ then lost".
3) Saves results/loss_library.csv (every loss with its tags and lesson) and results/pattern_stats.csv
   (win rate and P/L by tag), sends both back to the sheet ("Loss Library" and "Pattern Stats" tabs),
   adds today's Penny trades to the Penny tab, and posts the top lessons to Discord.
Read only on Alpaca. Paper account only.
"""
import csv
import datetime as dt
import os
import re
from collections import defaultdict
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
HOOK = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
SHEET = os.environ.get("NORA_SHEET_URL", "").strip()   # the sheet's Nora web app (GitHub secret, never in code)
today = dt.datetime.now(ET).date()


def post(text):
    print(text)
    if HOOK:
        try:
            requests.post(HOOK, json={"content": text[:1900]}, timeout=10)
        except Exception:
            pass


def money(x):
    x = str(x or "").replace("$", "").replace(",", "").strip()
    neg = x.startswith("(") and x.endswith(")")
    x = x.strip("()")
    try:
        v = float(x)
    except ValueError:
        return None
    return -v if neg else v


def tod(text):
    m = re.search(r"(\d{1,2}):(\d{2})\s*ET", text or "")
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def tags_for(why, note, minute, reason=""):
    t = f"{why} {note}".lower()
    out = []
    for key, name in (("1-3", "Strat 1-3"), ("3-2-2", "Strat 3-2-2"), ("3-1-2", "Strat 3-1-2"), ("2-1-2", "Strat 2-1-2"),
                      ("2-2", "Strat 2-2"), ("cisd", "CISD"), ("sweep", "Sweep"), ("swept", "Sweep"), ("rejection block", "RB"),
                      (" rb", "RB"), ("order block", "OB"), (" ob", "OB"), ("ote", "OTE"), ("flag", "Flag"),
                      ("orh", "ORH/ORL"), ("orl", "ORH/ORL"), ("pdh", "PDH/PDL"), ("pdl", "PDH/PDL"), ("pdc", "PDC"),
                      ("2 pm", "2 PM candle"), ("14:00", "2 PM candle"), ("late hour", "Late hour high/low"),
                      ("against", "Counter trend"), ("counter", "Counter trend"), ("chas", "Chasing"), ("chop", "Chop")):
        if key in t and name not in out:
            out.append(name)
    if "5m strat" in t:
        out.append("5m Strat")
    if "15m strat" in t:
        out.append("15m Strat")
    if minute is not None:
        out.append("Window 1" if minute < 760 else ("Window 3 EOD" if minute >= 900 else "Window 2"))
        if 690 <= minute < 825:
            out.append("Lunch 11:30 to 13:45")
    r = f"{reason} {note}".lower()
    if "50% stop" in r:
        out.append("Exit: 50% stop")
    elif "breakeven" in r:
        out.append("Exit: breakeven")
    elif "trail" in r:
        out.append("Exit: trail")
    return out


def lesson(tr):
    tg = tr["tags"]
    if tr.get("best") is not None and tr["best"] >= 20 and tr["pl"] < 0:
        return "Was up 20% or more and still lost: take the partial or move the stop sooner."
    if "Lunch 11:30 to 13:45" in tg:
        return "Lunch chop: wait for a range high or low sweep, or skip it."
    if "Counter trend" in tg:
        return "Against the trend: quick in and out only, or wait for the trend side."
    if "Chasing" in tg:
        return "Chased the entry: wait for the pullback to the level."
    if "Exit: 50% stop" in tg:
        return "Full 50% stop: the level did not hold. Wait for the 1m confirmation before entry."
    return "Note what the higher timeframe said before entry."


# 1) collect trades
trades = []
if SHEET:
    try:
        data = requests.get(SHEET, params={"action": "read"}, timeout=60).json()
    except Exception as e:
        data = {}
        print("sheet read failed", e)
    for tab, who in (("journal", "Titi"), ("penny", "Penny")):
        for r in data.get(tab, []):
            d = str(r.get("Date") or "")[:10]
            if not re.match(r"\d{4}-\d{2}-\d{2}", d):
                continue
            pl = money(r.get("P/L"))
            if pl is None:
                continue
            note = str(r.get("Note") or "")
            why = str(r.get("Level Swept") or "")
            m = tod(note)
            trades.append({"who": who, "date": d, "ticker": r.get("Ticker", ""), "bias": r.get("Bias", ""), "why": why,
                           "note": note, "pl": pl, "best": None, "minute": m, "rules": r.get("Followed Rules", ""),
                           "tags": tags_for(why, note, m), "src": "sheet"})

# Penny's own log, for days not in the sheet yet (and to send to the Penny tab)
penny_new = []
seen = {(t["date"], t["ticker"], t["note"][:60]) for t in trades}
sheet_days = {t["date"] for t in trades if t["who"] == "Penny"}
if os.path.exists("results/penny_trades.csv"):
    with open("results/penny_trades.csv") as fh:
        for r in csv.DictReader(fh):
            try:
                entry, exitp, qty = float(r["entry"]), float(r["exit"] or 0), int(float(r.get("qty") or 1))
            except ValueError:
                continue
            pl = round((exitp - entry) * 100 * qty, 2)
            hh, mm = (r["time_in"] or "0:0").split(":")
            m = int(hh) * 60 + int(mm)
            tk = "SPY" if r["contract"].startswith("SPY") else "SPX"
            note = (f"Penny auto log. {r['contract']}, entry {r['time_in']} ET, out {r['time_out']} ET ({r['reason']}), "
                    f"best {float(r['best']) / entry * 100 - 100:+.0f}%.")
            tr = {"who": "Penny", "date": r["date"], "ticker": tk, "bias": "Bullish" if r["side"] == "CALLS" else "Bearish",
                  "why": r.get("why", ""), "note": note, "pl": pl, "best": float(r["best"]) / entry * 100 - 100,
                  "minute": m, "rules": "Y", "tags": tags_for(r.get("why", ""), note, m, r["reason"]), "src": "penny"}
            if r["date"] not in sheet_days:
                trades.append(tr)
            if r["date"] == str(today):
                penny_new.append({"Date": r["date"], "Ticker": tk, "Bias": tr["bias"], "Level Swept": tr["why"][:120],
                                  "Sweep/Break": "Sweep" if "swe" in tr["why"].lower() else "Break",
                                  "Entry": entry, "Exit": exitp, "Contracts": qty, "P/L": pl, "Followed Rules": "Y",
                                  "Note": note})

# 2) the library
losses = [t for t in trades if t["pl"] < 0]
for t in losses:
    t["lesson"] = lesson(t)
stats = defaultdict(lambda: {"n": 0, "w": 0, "pl": 0.0})
for t in trades:
    for g in t["tags"] + [f"{t['who']} {t['ticker']}"]:
        s = stats[g]
        s["n"] += 1
        s["w"] += t["pl"] > 0
        s["pl"] += t["pl"]

os.makedirs("results", exist_ok=True)
lib_rows = [{"Date": t["date"], "Who": t["who"], "Ticker": t["ticker"], "Bias": t["bias"], "Setup": t["why"][:120],
             "Tags": ", ".join(t["tags"]), "P/L": round(t["pl"], 2), "Lesson": t["lesson"], "Note": t["note"][:300]}
            for t in sorted(losses, key=lambda x: x["date"], reverse=True)]
stat_rows = [{"Pattern": g, "Trades": s["n"], "Wins": s["w"], "Win %": round(s["w"] / s["n"] * 100), "P/L": round(s["pl"], 2)}
             for g, s in sorted(stats.items(), key=lambda kv: kv[1]["pl"]) if s["n"] >= 2]
for path, rows in (("results/loss_library.csv", lib_rows), ("results/pattern_stats.csv", stat_rows)):
    with open(path, "w", newline="") as fh:
        if rows:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

# 3) back to the sheet
if SHEET:
    try:
        r = requests.post(SHEET, json={"action": "write", "lossLibrary": lib_rows, "patternStats": stat_rows, "penny": penny_new},
                          timeout=60)
        print("sheet write", r.status_code, r.text[:200])
    except Exception as e:
        print("sheet write failed", e)

# 4) Discord: the three costliest patterns and today's losses
worst = [s for s in stat_rows if s["P/L"] < 0][:3]
best = sorted(stat_rows, key=lambda s: s["P/L"], reverse=True)[:2]
lines = [f"NORA lessons {today:%b %d} | {len(trades)} trades studied, {len(losses)} losses in the library"]
if worst:
    lines.append("Costliest setups: " + " | ".join(f"{s['Pattern']} {s['Win %']}% wins, {s['P/L']:+,.0f}" for s in worst))
if best:
    lines.append("Best setups: " + " | ".join(f"{s['Pattern']} {s['Win %']}% wins, {s['P/L']:+,.0f}" for s in best))
for t in [t for t in losses if t["date"] == str(today)][:4]:
    lines.append(f"Today {t['who']} {t['ticker']} {t['pl']:+,.0f}: {t['lesson']}")
post("\n".join(lines))
