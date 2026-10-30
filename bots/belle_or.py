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
import os
import sys
import time

from penny_common import (DRY, REPLAY, already_traded, buy, ct, dispatch, hm, holding, market_day, now, pdc_spy,
                          pick, post, spx_ratio, spy_bars, tick)

SPX_MIN, SPX_MAX = 1.50, 2.50
SPY_MAX = 0.60
SPY_QTY = 3

day = market_day(9, "orb")

ratio = spx_ratio(day)
pdc = pdc_spy(day)
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
    if not DRY and already_traded("orb", day):
        print("orb: Penny already took a setup today, this start does nothing (no post, no order)")
        return
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
        c = pick(day, "SPXW", cp, last["c"], SPX_MIN, SPX_MAX, 5)
        if c:
            lim = tick(c["ask"], "SPX")
            oid = buy("orb", c["sym"], 1, lim, "SPX")
            if oid:
                notes.append(f"bought 1 SPX {c['k']:g}{cp} at {lim:.2f} (${lim * 100:.0f} total)")
                spx_k = int(c["k"])
                dispatch("orb", oid, c["sym"], f"SPX {c['k']:g}{cp} ORB", side, stop / ratio, t1 / ratio, why, t2 / ratio, t3 / ratio)
        else:
            notes.append(f"SPX skipped, nothing between ${SPX_MIN:.2f} and ${SPX_MAX:.2f}")
        y = pick(day, "SPY", cp, last["c"] / ratio, 0.05, SPY_MAX, 1)
        if y:
            lim = tick(y["ask"], "SPY")
            oid = buy("orb", y["sym"], SPY_QTY, lim, "SPY")
            if oid:
                notes.append(f"bought {SPY_QTY} SPY {y['k']:g}{cp} at {lim:.2f} (${lim * 100 * SPY_QTY:.0f} total)")
                spy_k = int(y["k"])
                dispatch("orb", oid, y["sym"], f"SPY {y['k']:g}{cp} ORB", side, stop / ratio, t1 / ratio, why, t2 / ratio, t3 / ratio)
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
    allb = spy_bars(day)
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
        B = spy_bars(day)
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
