"""BELLE STALL, the EOD stall break watcher (Titi, Oct 21 2026). Started by Vercel in the 13:00 ET hour.

Titi's setup (Oct 21: 7760P $1.10 to $12.10, then 7760C $0.65 to $4.40):
  - STALL: the last 60 minutes stay in a range of 10 SPX points or less, the high (or low) is tapped at least twice
    within 3 points (EQH / EQL) and price sits within 5 points of the day high (or low).
  - BREAK: a 5m close below the stall (puts) or above it (calls), 14:00 to 15:30 ET. Posts STALL BREAK.
  - ENTRY (ICT fib, Oct 25): the pullback into the OTE zone (0.62 to 0.79 of the move) that closes rejected.
    Last entry on the 15:55 ET close. A 5m close back beyond the stall cancels it (log only).
  - TARGETS: -0.27, -0.62, -1 (Symmetrical Price) of the move. Stop beyond the start of the move.
  - Puts are favored EOD (backtest: above PDC at 15:00, down 67% of days).
Posts to Discord: the 15:00 EOD STALL CHECK, the STALL BREAK, the entry, and a REVERSAL WATCH (post only).
On the entry Penny buys 1 SPX + 3 SPY on the Alpaca PAPER account and the Penny manager runs the trade
(label "STALL FIB"), and the setup is handed to Pearl (live, only if PEARL_ON is true).
"""
import sys
import time

from penny_common import (DRY, REPLAY, already_traded, buy, ct, dispatch, hm, holding, market_day, now, pdc_spy,
                          pearl_go, pick, post, spx_ratio, spy_bars, tick)

STALL_RANGE = 15.0   # SPX points over the last 60 minutes (12 x 5m). Oct 29 backtest: 15 pts 5 of 5 (+49.7), 10 pts 2 of 2 (+22.9)
TAP = 3.0            # EQH / EQL tolerance, SPX points
NEAR = 5.0           # stall must sit within 5 points of the day high / low
SPX_MIN, SPX_MAX = 1.50, 2.50   # SPX premium: cheap far out contracts lost 6 of 7 (Oct 16 to 21)
SPY_MAX = 0.60
SPY_QTY = 3

day = market_day(13, "stall")

ratio = spx_ratio(day)
pdc = pdc_spy(day)
print("ratio", round(ratio, 4), "pdc", pdc)
checked = False
fired = None      # (dir, extreme_spy, break_minute)
rev_posted = False
pend = None       # stall break waiting for the OTE pullback (Titi, Oct 25)


def enter(d, start, ext, last, why_base):
    """Penny's entry at the OTE pullback. Fib on the move: 1 = stall extreme (start), 0 = the break's extreme.
    Stop beyond 1. SPY trims at -0.27 and -0.62, everything out at -1. SPX holds (no trims)."""
    if not DRY and already_traded("stall", day):
        print("stall: Penny already took a setup today, this start does nothing (no post, no order)")
        return
    R = abs(start - ext)
    t1, t2, t3 = ext + d * 0.27 * R, ext + d * 0.62 * R, ext + d * 1.0 * R
    side = "PUTS" if d == -1 else "CALLS"
    cp = "P" if d == -1 else "C"
    why = f"{why_base}. OTE entry {last['c']:.1f}"
    if not DRY:
        pearl_go("STALL", side, start / ratio, t3 / ratio, f"Stall break at the {'high' if d == -1 else 'low'}, OTE pullback rejected")
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
            oid = buy("stall", c["sym"], 1, lim, "SPX")
            if oid:
                notes.append(f"bought 1 SPX {c['k']:g}{cp} at {lim:.2f} (${lim * 100:.0f} total)")
                spx_k = int(c["k"])
                dispatch("stall", oid, c["sym"], f"SPX {c['k']:g}{cp} STALL FIB", side, start / ratio, t1 / ratio, why, t2 / ratio, t3 / ratio)
        else:
            notes.append(f"SPX skipped, nothing between ${SPX_MIN:.2f} and ${SPX_MAX:.2f}")
        y = pick(day, "SPY", cp, last["c"] / ratio, 0.05, SPY_MAX, 1)
        if y:
            lim = tick(y["ask"], "SPY")
            oid = buy("stall", y["sym"], SPY_QTY, lim, "SPY")
            if oid:
                notes.append(f"bought {SPY_QTY} SPY {y['k']:g}{cp} at {lim:.2f} (${lim * 100 * SPY_QTY:.0f} total)")
                spy_k = int(y["k"])
                dispatch("stall", oid, y["sym"], f"SPY {y['k']:g}{cp} STALL FIB", side, start / ratio, t1 / ratio, why, t2 / ratio, t3 / ratio)
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
        # spaced out, one fact per line (Oct 29 approved layout, no emojis)
        loc = {"at the HIGH": "Price is at the day HIGH", "at the LOW": "Price is at the day LOW"}.get(where, "Price is mid range")
        lines = ["**STALL CHECK 15:00 ET (14:00 CT)**",
                 ("STALL FORMING" if stall else "No stall") + f"\nLast 60 min range: {hi - lo:.1f} pts" + ("" if stall else ", too wide"),
                 f"{loc}\nHigh tapped {taps_h}x, low tapped {taps_l}x",
                 f"Day high: {hod:.1f}\nDay low: {lod:.1f}\nHalfway: {mid:.1f}",
                 "SPX above PDC: puts favored EOD (down 67% of days)" if above else "SPX below PDC"]
        if fired:
            lines.append(f"STALL BREAK already fired at {hm(fired[2] + 5)} ET ({ct(fired[2] + 5)} CT)\nStop SPX {fired[1]:.1f}\nHold for the target")
        elif stall and where == "at the HIGH":
            lines.append(f"Watch: a 5m close below {lo:.1f} = STALL BREAK puts\nTarget: {mid:.1f}")
        elif stall and where == "at the LOW":
            lines.append(f"Watch: a 5m close above {hi:.1f} = STALL BREAK calls\nTarget: {mid:.1f}")
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
                    stop_spx = hi if d == -1 else lo
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
        if (d == -1 and last["c"] > start) or (d == 1 and last["c"] < start) or last["m"] > 15 * 60 + 50:
            print(f"STALL BREAK {'PUTS' if d == -1 else 'CALLS'}: canceled, {'5m close back above the stall' if last['m'] <= 15 * 60 + 50 else 'no OTE pullback by 15:55 ET'}. No trade.")
            pend = None
        else:
            R = abs(start - pend["ext"])
            z1 = pend["ext"] - d * 0.62 * R   # OTE zone (0.62 to 0.79 of the move) starts here, toward the start
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
    allb = spy_bars(day)
    for n_ in range(14, len(allb) + 1):
        process(allb[:n_])
    print("replay done")
    sys.exit(0)

last_m = -1
while True:
    n = now()
    nm = n.hour * 60 + n.minute
    if nm > 15 * 60 + 57:   # last entry on the 15:55 ET close (Oct 27)
        break
    try:
        B = spy_bars(day)
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
