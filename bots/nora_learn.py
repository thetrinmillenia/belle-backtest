"""NORA, the teacher: the loss library (Titi, Oct 19 2026). Runs right after the Nora recap, every weekday.

1) Reads every trade she can find:
   - Titi's Journal tab and Penny's tab in the "ATM Method - Trading Journal" sheet (through the sheet's Nora web app)
   - Penny's own trade log from the manager (results/penny_trades.csv), so nothing depends on manual logging
2) Tags each trade by setup (Strat, sweep, CISD, RB, OB, EOD fade), window, time of day (lunch chop),
   exit (50% stop, breakeven, trail) and "was up 20%+ then lost".
3) Saves results/loss_library.csv (every loss with its tags and lesson) and results/pattern_stats.csv
   (win rate and P/L by tag), plus results/win_library.csv (every win and what worked). With the sheet link set,
   sends them to the "Loss Library", "Win Library" and "Pattern Stats" tabs and adds today's Penny trades.
   No Discord posts (Titi, Oct 19).
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
SHEET = os.environ.get("NORA_SHEET_URL", "").strip()   # the sheet's Nora web app (GitHub secret, never in code)
today = dt.datetime.now(ET).date()


def post(text):
    print(text)   # Titi, Oct 19: Nora does not post to Discord. The summary stays in the GitHub run log only.


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
                      ("stall", "Stall break"), ("flush", "Flush"), ("eqh", "EQH/EQL"), ("eql", "EQH/EQL"), ("reversal", "Reversal"),
                      ("against", "Counter trend"), ("counter", "Counter trend"), ("chas", "Chasing"), ("chop", "Chop")):
        if key in t and name not in out:
            out.append(name)
    if re.search(r"(?<!1)5m strat", t):
        out.append("5m Strat")
    if "15m strat" in t:
        out.append("15m Strat")
    if minute is not None:
        out.append("Window 1" if minute < 760 else ("Window 3 EOD" if minute >= 900 else "Window 2"))
        if 690 <= minute < 825:
            out.append("Lunch 11:30 to 13:45")
    r = f"{reason} {note}".lower()
    if "target" in r:
        out.append("Exit: target")
    elif "43% stop" in r:
        out.append("Exit: 43% stop")
    elif "step stop" in r:
        out.append("Exit: step stop")
    elif re.search(r"\bexit\b", r):
        out.append("Exit: broker stop")
    elif "50% stop" in r:
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
    if "Window 3 EOD" in tg and "Stall break" not in tg:
        return "EOD loss: puts are favored EOD. Check the EOD STALL CHECK and the PDC side before calls."
    if "Lunch 11:30 to 13:45" in tg:
        return "Lunch chop: wait for a range high or low sweep, or skip it."
    if "Counter trend" in tg:
        return "Against the trend: quick in and out only, or wait for the trend side."
    if "Chasing" in tg:
        return "Chased the entry: wait for the pullback to the level."
    if "Exit: 50% stop" in tg:
        return "Full 50% stop: the level did not hold. Wait for the 1m confirmation before entry."
    return "Note what the higher timeframe said before entry."


def win_lesson(tr):
    tg = tr["tags"]
    if "Stall break" in tg:
        return "Stall break paid: tiny candles at the high, then a fast break. Hold SPX, target 50% of the day's swing."
    if tr["pl"] >= 300:
        return "Big runner: same setup, same patience. Let the trail work."
    if "Window 3 EOD" in tg:
        return "EOD worked: key level failed, trail tight, out by 15:58."
    if any(g.startswith("Strat") or g.endswith("Strat") for g in tg):
        return "Strat entry on the close of the 2 worked: wait for the bar to close."
    if "Sweep" in tg:
        return "Sweep then reclaim worked: liquidity first, then entry."
    if "Exit: breakeven" in tg:
        return "Flat to small win at breakeven: the idea may have been right, watch for the REENTER."
    return "Repeat it: same window, same setup."


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

# Titi's own trades (data/titi_trades.csv, Titi Oct 20): Nora learns from them even without the sheet link.
# P/L is in dollars; when only a percent is known it counts as dollars on a $100 contract.
if not any(t["who"] == "Titi" for t in trades) and os.path.exists("data/titi_trades.csv"):
    with open("data/titi_trades.csv") as fh:
        for r in csv.DictReader(fh):
            pl = money(r.get("pl"))
            if pl is None and r.get("pct"):
                pl = float(r["pct"])
            if pl is None:
                continue
            note = r.get("note", "")
            m = tod(note)
            trades.append({"who": "Titi", "date": r["date"], "ticker": r["ticker"], "bias": r["bias"], "why": r["setup"],
                           "note": note, "pl": pl, "best": None, "minute": m, "rules": "Y",
                           "tags": tags_for(r["setup"], note, m), "src": "titi"})

# Penny's own log, for days not in the sheet yet (and to send to the Penny tab).
# Each manager run writes its own file in results/penny/ (Titi, Oct 20: one shared file lost trades when runs pushed at once).
import glob
penny_new = []
sheet_days = {t["date"] for t in trades if t["who"] == "Penny"}
penny_pl = {}   # (date, contract) -> P/L already counted from Penny's log
rows = []
for path in ["results/penny_trades.csv"] + sorted(glob.glob("results/penny/*.csv")):
    if os.path.exists(path):
        with open(path) as fh:
            rows += list(csv.DictReader(fh))
seen_rows = set()
for r in rows:
    key = (r.get("date"), r.get("time_in"), r.get("contract"))
    if key in seen_rows:
        continue
    seen_rows.add(key)
    try:
        entry, exitp, qty = float(r["entry"]), float(r["exit"] or 0), int(float(r.get("qty") or 1))
    except (ValueError, KeyError, TypeError):
        continue
    pl = round((exitp - entry) * 100 * qty, 2)
    hh, mm = (r["time_in"] or "0:0").split(":")
    m = int(hh) * 60 + int(mm)
    tk = "SPY" if r["contract"].startswith("SPY") else "SPX"
    base = " ".join(r["contract"].split()[:2])   # "SPX 7740C" without EOD / RE
    penny_pl[(r["date"], base)] = penny_pl.get((r["date"], base), 0) + pl
    note = (f"Penny auto log. {r['contract']}, entry {r['time_in']} ET, out {r['time_out']} ET ({r['reason']}), "
            f"best {float(r['best']) / entry * 100 - 100:+.0f}%.")
    tr = {"who": "Penny", "date": r["date"], "ticker": tk, "bias": "Bullish" if r["side"] == "CALLS" else "Bearish",
          "why": r.get("why", "") or "", "note": note, "pl": pl, "best": float(r["best"]) / entry * 100 - 100,
          "minute": m, "rules": "Y", "tags": tags_for(r.get("why", "") or "", note, m, r["reason"]), "src": "penny"}
    if r["date"] not in sheet_days:
        trades.append(tr)
    if r["date"] == str(today):
        penny_new.append({"Date": r["date"], "Ticker": tk, "Bias": tr["bias"], "Level Swept": tr["why"][:120],
                          "Sweep/Break": "Sweep" if "swe" in tr["why"].lower() else "Break",
                          "Entry": entry, "Exit": exitp, "Contracts": qty, "P/L": pl, "Followed Rules": "Y",
                          "Note": note})

# Alpaca fills (the truth for P/L): anything the Penny log missed is added from the paper account fills
if os.path.exists("results/nora_trades.csv"):
    with open("results/nora_trades.csv") as fh:
        for r in csv.DictReader(fh):
            if r["date"] in sheet_days or not r.get("pl"):
                continue
            try:
                pl = float(r["pl"]) - penny_pl.get((r["date"], r["contract"]), 0)
            except ValueError:
                continue
            if abs(pl) < 1 and (r["date"], r["contract"]) in penny_pl:
                continue
            hh, mm = (r["time"] or "0:0").split(":")
            m = int(hh) * 60 + int(mm)
            tk = "SPY" if r["contract"].startswith("SPY") else "SPX"
            note = f"Alpaca fill. {r['contract']} x{r['qty']}, first entry {r['time']} ET, {r['entry']} to {r['exit']} ({r['pct']}%)."
            trades.append({"who": "Penny", "date": r["date"], "ticker": tk,
                           "bias": "Bullish" if r["contract"].endswith("C") else "Bearish", "why": "", "note": note,
                           "pl": round(pl, 2), "best": None, "minute": m, "rules": "", "tags": tags_for("", note, m), "src": "alpaca"})

# 2) the library
losses = [t for t in trades if t["pl"] < 0]
for t in losses:
    t["lesson"] = lesson(t)
# win library (Titi, Oct 19): learn from the wins too
wins = [t for t in trades if t["pl"] > 0]
for t in wins:
    t["lesson"] = win_lesson(t)
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
win_rows = [{"Date": t["date"], "Who": t["who"], "Ticker": t["ticker"], "Bias": t["bias"], "Setup": t["why"][:120],
             "Tags": ", ".join(t["tags"]), "P/L": round(t["pl"], 2), "Lesson": t["lesson"], "Note": t["note"][:300]}
            for t in sorted(wins, key=lambda x: (x["date"], x["pl"]), reverse=True)]
for path, rows in (("results/loss_library.csv", lib_rows), ("results/win_library.csv", win_rows),
                   ("results/pattern_stats.csv", stat_rows)):
    with open(path, "w", newline="") as fh:
        if rows:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

# 3) back to the sheet
if SHEET:
    try:
        r = requests.post(SHEET, json={"action": "write", "lossLibrary": lib_rows, "winLibrary": win_rows, "patternStats": stat_rows, "penny": penny_new},
                          timeout=60)
        print("sheet write", r.status_code, r.text[:200])
    except Exception as e:
        print("sheet write failed", e)

# 4) summary in the run log only (no Discord)
worst = [s for s in stat_rows if s["P/L"] < 0][:3]
best = sorted(stat_rows, key=lambda s: s["P/L"], reverse=True)[:2]
lines = [f"NORA lessons {today:%b %d} | {len(trades)} trades studied, {len(losses)} losses and {len(wins)} wins in the libraries"]
if worst:
    lines.append("Costliest setups: " + " | ".join(f"{s['Pattern']} {s['Win %']}% wins, {s['P/L']:+,.0f}" for s in worst))
if best:
    lines.append("Best setups: " + " | ".join(f"{s['Pattern']} {s['Win %']}% wins, {s['P/L']:+,.0f}" for s in best))
for t in [t for t in losses if t["date"] == str(today)][:4]:
    lines.append(f"Today {t['who']} {t['ticker']} {t['pl']:+,.0f}: {t['lesson']}")
post("\n".join(lines))
