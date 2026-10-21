"""PENNY trade manager (Alpaca PAPER account only).

Started by the Penny relay after each entry (one run per contract). It waits for the fill, then:
  - step stop (Titi, Oct 20): +20% raises the stop to -20%, +40% moves it to breakeven
  - posts +20%, +50% (take partial), +100% (stop locks +70%, then steps up every +10%), Target 1 hit
  - exits on: Belle's stop (SPY level), a 43% loss of premium (starting stop, Titi Oct 20), the trail, or 15:58 ET (never later, Titi Oct 19)
  - EOD trades (Window 3, label EOD): no 5 minute scalp timer, tight trail (20% below the best from +30%,
    15% from +100%), sell 1 SPY at Target 1, hold the rest to 15:58 for the $100 to $1,000 run
  - unfilled orders: the limit stays working (pullback to the entry price or better, never chase) up to 10 min,
    canceled at once if SPY hits Belle's stop
  - after a breakeven or 43% stop exit: if SPY breaks the move's high/low within 30 min with Belle's stop intact,
    Window 1 re-enters once by itself; every other window posts a REENTER note (Titi, Oct 19)
  - trail after +50%: 30% below the best price, never giving back more than $50
  - after +100%: trail 20% below the best price, never below +50%
  - after +200%: trail 15% below the best price, never below +100%
  - if Belle fires the other side while this is open: stop tightens to 10% under the current price
Every message is short. The trade is saved to results/paper_trades.csv for Nora.
"""
import csv
import math
import os
import sys
import time
import datetime as dt
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
TRADE = "https://paper-api.alpaca.markets"  # PAPER endpoint only
DATA = "https://data.alpaca.markets"
H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"].strip(), "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"].strip()}
HOOK = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
ORDER_ID = os.environ["ORDER_ID"]
SYM = os.environ["SYMBOL"]
LABEL = os.environ.get("LABEL") or SYM
SIDE = os.environ.get("SIDE", "CALLS")
DIR = 1 if SIDE == "CALLS" else -1


def num(name):
    try:
        return float(os.environ.get(name, ""))
    except ValueError:
        return None


SPY_STOP = num("SPY_STOP")
SPY_T1 = num("SPY_T1")


def post(text):
    print(text, flush=True)
    if HOOK:
        try:
            requests.post(HOOK, json={"content": text[:1900]}, timeout=10)
        except Exception:
            pass


DRAFT = os.environ.get("STUDENT_WEBHOOK_URL", "").strip()
DRAFT_ON = False   # Window 1 SPY only, set after the fill
DRAFT_MS = (20, 50, 75, 100, 150, 200, 250, 300, 400, 500, 600, 700, 800, 900, 1000)


def draft(text):
    """BELLE DRAFTS (Titi, Oct 21): Window 1 SPY posts in Titi's voice, to her private #belle-drafts channel.
    She copies them into the community. @everyone is in the text but does not ping in the private channel."""
    if not (DRAFT and DRAFT_ON and LABEL.startswith("SPY")):
        return
    try:
        requests.post(DRAFT, json={"content": text[:1900], "allowed_mentions": {"parse": []}}, timeout=10)
    except Exception:
        pass


def money(p):
    return f"${p:.2f}".replace("$0.", "$.")


def now():
    return dt.datetime.now(ET)


def opposite_alert_since(t0):
    """Belle fired the other side after this entry (relay flip watchlist, or an opposite penny- order)."""
    try:
        r = requests.get(f"{TRADE}/v2/orders", headers=H, timeout=10,
                         params={"status": "all", "after": t0, "limit": 50, "direction": "desc"}).json()
    except Exception:
        return False
    my_cp = SYM[-9]
    # the relay skips the new trade and leaves an empty watchlist named penny-flip-<C|P>-<ms>
    try:
        wl = requests.get(f"{TRADE}/v2/watchlists", headers=H, timeout=10).json()
        for w in wl if isinstance(wl, list) else []:
            nm = w.get("name") or ""
            if nm.startswith("penny-flip-") and len(nm) > 11 and nm[11] != my_cp and (w.get("created_at") or "") > t0:
                return True
    except Exception:
        pass
    for o in r if isinstance(r, list) else []:
        cid = o.get("client_order_id") or ""
        sym = o.get("symbol") or ""
        if cid.startswith("penny-") and len(sym) > 9 and sym[-9] in "CP" and sym[-9] != my_cp:
            return True
    return False


EXIT_MIN = 958   # out at 15:58 ET, never later, regardless of price (Titi, Oct 19)
EOD = "EOD" in LABEL or "SCALP" in LABEL


def opt_ask():
    r = requests.get(f"{DATA}/v1beta1/options/quotes/latest", params={"symbols": SYM, "feed": "indicative"}, headers=H, timeout=10).json()
    return ((r.get("quotes") or {}).get(SYM) or {}).get("ap")


def buy(q, lim):
    o = requests.post(f"{TRADE}/v2/orders", headers=H, timeout=10,
                      json={"symbol": SYM, "qty": str(q), "side": "buy", "type": "limit", "limit_price": f"{lim:.2f}",
                            "time_in_force": "day", "client_order_id": f"penny-re-{int(time.time()*1000)}"}).json()
    return o.get("id")


def get_order(oid):
    return requests.get(f"{TRADE}/v2/orders/{oid}", headers=H, timeout=10).json()


def opt_bid():
    r = requests.get(f"{DATA}/v1beta1/options/quotes/latest", params={"symbols": SYM, "feed": "indicative"}, headers=H, timeout=10).json()
    return ((r.get("quotes") or {}).get(SYM) or {}).get("bp")


def spy_price():
    r = requests.get(f"{DATA}/v2/stocks/SPY/trades/latest", params={"feed": "iex"}, headers=H, timeout=10).json()
    return (r.get("trade") or {}).get("p")


# REAL STOP ORDER at the broker (Titi, Oct 20, before going live). Logged and posted as "EXIT": a stop order sits at Alpaca and triggers the instant
# the contract trades at the floor, instead of Penny noticing it up to 10 seconds later. Penny moves it up as the floor rises.
STOP_ID = None
STOP_PX = None
STOP_FILL = None   # price if the broker stop order filled


def tick_dn(p):
    if SYM.startswith("SPY"):
        return math.floor(p * 100 + 1e-9) / 100
    return math.floor(p * 10 + 1e-9) / 10 if p >= 3 else math.floor(p * 20 + 1e-9) / 20


def place_stop(q, px):
    o = requests.post(f"{TRADE}/v2/orders", headers=H, timeout=10,
                      json={"symbol": SYM, "qty": str(q), "side": "sell", "type": "stop", "stop_price": f"{px:.2f}",
                            "time_in_force": "day", "client_order_id": f"penny-stop-{int(time.time() * 1000)}"}).json()
    if "id" not in o:
        print("stop order rejected", str(o)[:200])
        return None
    return o["id"]


def move_stop(px):
    """Raise the broker stop. Returns False if the old stop already filled."""
    global STOP_ID, STOP_PX
    r = requests.patch(f"{TRADE}/v2/orders/{STOP_ID}", headers=H, timeout=10, json={"stop_price": f"{px:.2f}"}).json()
    if "id" in r:
        STOP_ID, STOP_PX = r["id"], px
        return True
    return not stop_filled()


def stop_filled():
    """True (and STOP_FILL set) if the broker stop order has filled."""
    global STOP_FILL
    if not STOP_ID:
        return False
    x = get_order(STOP_ID)
    if x.get("status") == "filled":
        STOP_FILL = float(x["filled_avg_price"])
        return True
    return False


def cancel_stop():
    """Cancel the broker stop before Penny sells by herself. Returns True if it had already filled."""
    global STOP_ID, STOP_PX
    if not STOP_ID:
        return False
    requests.delete(f"{TRADE}/v2/orders/{STOP_ID}", headers=H, timeout=10)
    for _ in range(10):
        x = get_order(STOP_ID)
        st = x.get("status")
        if st == "filled":
            globals()["STOP_FILL"] = float(x["filled_avg_price"])
            return True
        if st in ("canceled", "expired", "rejected"):
            break
        time.sleep(1)
    STOP_ID, STOP_PX = None, None
    return False


def sell(q=1):
    if cancel_stop():
        return None   # the broker stop already sold everything
    o = requests.post(f"{TRADE}/v2/orders", headers=H, timeout=10,
                      json={"symbol": SYM, "qty": str(q), "side": "sell", "type": "market", "time_in_force": "day"}).json()
    if "id" not in o:
        post(f"PENNY {LABEL}: sell rejected, check Alpaca")
        return None
    for _ in range(30):
        x = get_order(o["id"])
        if x.get("status") == "filled":
            return float(x["filled_avg_price"])
        time.sleep(2)
    return None


def save(entry, exitp, peak, reason):
    os.makedirs("results", exist_ok=True)
    path = "results/paper_trades.csv"
    new = not os.path.exists(path)
    pct = "" if exitp is None else f"{(exitp / entry - 1) * 100:.0f}"
    with open(path, "a") as fh:
        if new:
            fh.write("date,time_in,time_out,contract,side,entry,exit,best,pct,reason\n")
        fh.write(f"{now().date()},{T_IN},{now():%H:%M},{LABEL},{SIDE},{entry:.2f},{'' if exitp is None else f'{exitp:.2f}'},{peak:.2f},{pct},{reason}\n")
    # full log for Nora's loss library (Titi, Oct 19): adds the contract count and Belle's reason
    os.makedirs("results/penny", exist_ok=True)
    path2 = f"results/penny/{now():%Y-%m-%d}-{ORDER_ID[:8]}.csv"   # one file per trade, no push clashes (Titi, Oct 20)
    new2 = not os.path.exists(path2)
    with open(path2, "a", newline="") as fh:
        w = csv.writer(fh)
        if new2:
            w.writerow(["date", "time_in", "time_out", "contract", "side", "qty", "entry", "exit", "best", "reason", "why"])
        w.writerow([str(now().date()), T_IN, f"{now():%H:%M}", LABEL, SIDE, QTY, f"{entry:.2f}",
                    "" if exitp is None else f"{exitp:.2f}", f"{peak:.2f}", reason, os.environ.get("WHY", "")])


def wait_fill(oid, quiet=False):
    """Strict hold-open rule (Titi, Oct 19): the limit order stays at the entry price (a pullback fills it, never chase).
    Up to 10 minutes, canceled at once if SPY hits Belle's stop or it is 15:53 or later."""
    start = time.time()
    while True:
        o = get_order(oid)
        st = o.get("status")
        if st == "filled":
            return o
        if st in ("canceled", "expired", "rejected"):
            if not quiet:
                post(f"PENNY {LABEL}: not filled ({st})")
            return None
        try:
            spy = spy_price()
        except Exception:
            spy = None
        late = now().hour * 60 + now().minute >= 953
        broke = spy and SPY_STOP and (spy - SPY_STOP) * DIR <= 0
        if time.time() - start > 600 or broke or late:
            requests.delete(f"{TRADE}/v2/orders/{oid}", headers=H, timeout=10)
            why = "Belle's stop hit first" if broke else ("too late in the day" if late else "no pullback to the entry price in 10 min")
            if not quiet:
                post(f"PENNY {LABEL}: not filled, canceled ({why}). Penny does not chase")
            return None
        time.sleep(5)


o = wait_fill(ORDER_ID)
if not o:
    sys.exit(0)
entry = float(o["filled_avg_price"])
T_IN = f"{now():%H:%M}"
WIN1 = now().hour * 60 + now().minute <= 750
DRAFT_ON = WIN1
SIDE_W = "CALLS" if DIR == 1 else "PUTS"
draft(f"JUST FILLED IN @ {money(entry)} avg\n@everyone")
# scale out (Titi, Oct 17): SPY buys 3 contracts. Sell 1 at +50%, 1 at +100%, the last one rides the stop.
QTY = max(1, int(float(o.get("filled_qty") or 1)))
left = QTY
banked = []   # (price, qty) already sold
FILL_AT = o.get("filled_at") or dt.datetime.now(dt.timezone.utc).isoformat()
warned = False
last_chk = 0.0
warn_stop = 0.0

# 2) manage
peak = entry
said = set()
reason = ""
spy_best = None   # the move's high (calls) or low (puts) on SPY while in the trade, for the REENTER rule
while True:
    n = now()
    if n.hour * 60 + n.minute >= EXIT_MIN:
        reason = "15:58"
        break
    if stop_filled():
        reason = "EXIT"
        break
    try:
        bid = opt_bid()
        spy = spy_price()
    except Exception:
        bid, spy = None, None
    if spy:
        spy_best = spy if spy_best is None else (max(spy_best, spy) if DIR == 1 else min(spy_best, spy))
    if spy and SPY_STOP and (spy - SPY_STOP) * DIR <= 0:
        reason = "stop"
        break
    if spy and SPY_T1 and "t1" not in said and (spy - SPY_T1) * DIR >= 0:
        said.add("t1")
        msg = f"{LABEL} Target 1 hit"
        if EOD and left >= 2:   # EOD TP1 (Titi, Oct 19): bank 1 at the target, the rest trails
            px = sell(1)
            if px:
                banked.append((px, 1))
                left -= 1
                msg += f", sold 1 of {QTY} at {px:.2f}, {left} left"
        post(msg)
    if bid:
        peak = max(peak, bid)
        gain = bid / entry - 1
        hit = [m for m in DRAFT_MS if gain * 100 >= m and f"d{m}" not in said]
        if hit:
            said.update(f"d{m}" for m in hit)
            draft(f"{money(bid)} HERE ON SPY {SIDE_W}\nUP +{gain * 100:.0f}% {'☢️' if hit[-1] >= 100 else '🔥'}\n@everyone")
        for lvl, msg in ((0.20, "+20%"), (0.50, "+50%, take partial"), (1.00, "+100%, stop locked at +70%. Watch the levels, it can chop at +100% before the next leg")):
            if gain >= lvl and lvl not in said:
                said.add(lvl)
                if lvl in (0.50, 1.00) and left >= 2:
                    px = sell(1)
                    if px:
                        banked.append((px, 1))
                        left -= 1
                        msg += f", sold 1 of {QTY} at {px:.2f}, {left} left"
                        draft(f"TRIMMING 🚨\n{QTY - left}/{QTY} SOLD @ {money(px)}. {left} left, the last one rides.\n@everyone")
                post(f"{LABEL} {msg}")
        stop = entry * 0.57   # starting stop 43% (Titi, Oct 20)
        # step stop (Titi, Oct 20; backtest: best total, same worst loss): +20% raises the stop to -20%, +40% moves it to breakeven
        if peak >= entry * 1.20:
            stop = max(stop, entry * 0.80)
            if "step" not in said:
                said.add("step")
                post(f"{LABEL} +20%, stop raised to -20% ({entry * 0.80:.2f})")
        if peak >= entry * 1.40:
            stop = max(stop, entry)
            if "be" not in said:
                said.add("be")
                post(f"{LABEL} +40%, stop moved to breakeven {entry:.2f}")
                draft(f"Stop moved to breakeven on SPY {SIDE_W} ({money(entry)}). No risk left on this one.\n@everyone")
        if peak >= entry * 1.5:
            stop = max(stop, peak - min(peak * 0.30, 0.50))
        # EOD tight trail (Titi, Oct 19): 20% below the best from +30%, 15% below the best from +100%
        if EOD and peak >= entry * 1.3:
            stop = max(stop, peak * (0.85 if peak >= entry * 2.0 else 0.80), entry * 1.05)
        # tighter trail once the trade doubles (Titi, Oct 16): keep the winner running toward the target
        # never give back a 100% winner (Titi, Oct 17): at +100% lock +70%, then step the lock up every +10%
        # (+120% locks +90%, +150% locks +120%, and so on)
        if peak >= entry * 2.0:
            gain = int((peak / entry - 1) * 10 + 1e-9) / 10
            lock = entry * (1 + gain - 0.30)
            stop = max(stop, lock)
            # Discord only at +120%, +150% and +300% (Titi, Oct 17: no flood of messages)
            for ms in (1.2, 1.5, 3.0):
                if peak >= entry * (1 + ms) and f"ms{ms}" not in said:
                    said.add(f"ms{ms}")
                    post(f"{LABEL} +{ms*100:.0f}%, stop locked at +{(gain-0.30)*100:.0f}% ({lock:.2f})")
        # opposite Belle alert while this trade is open (Titi, Oct 16): no new trade, tighten this one
        if not warned and time.time() - last_chk > 30:
            last_chk = time.time()
            if opposite_alert_since(FILL_AT):
                warned = True
                post(f"{LABEL}: Belle flipped sides, stop tightened to 10% under the current price")
        if warned:
            warn_stop = max(warn_stop, bid * 0.90)   # ratchets up only
            stop = max(stop, warn_stop)
        # keep the broker stop at the floor, only ever moving it up
        sp = tick_dn(stop)
        if STOP_ID is None and left > 0 and sp > 0:
            STOP_ID, STOP_PX = place_stop(left, sp), sp
        elif STOP_ID and sp > STOP_PX + 1e-9:
            if not move_stop(sp):
                reason = "EXIT"
                break
        if bid <= stop:
            reason = "flip" if warned and stop == warn_stop else ("trail" if peak >= entry * 1.3 and stop > entry else ("breakeven" if stop >= entry else ("step stop" if stop >= entry * 0.80 - 1e-9 else "43% stop")))
            break
    time.sleep(10)

# 3) exit
if reason == "EXIT" or STOP_FILL is not None:
    exitp = STOP_FILL
    if reason != "EXIT":
        reason = "EXIT"
else:
    exitp = sell(left)
    if exitp is None and STOP_FILL is not None:   # the stop filled while Penny was cancelling it
        exitp, reason = STOP_FILL, "EXIT"
if exitp is not None and banked:
    exitp = (sum(p * q for p, q in banked) + exitp * left) / QTY   # average exit over all contracts
best = (peak / entry - 1) * 100
if exitp is None:
    post(f"PENNY {LABEL}: exit not confirmed, check Alpaca ({reason})")
else:
    pct = (exitp / entry - 1) * 100
    if reason == "15:58":
        post(f"{LABEL} out 15:58, best {best:+.0f}%, closed {pct:+.0f}%")
    elif reason == "stop":
        post(f"{LABEL} stopped out, closed {pct:+.0f}%")
    else:
        post(f"{LABEL} out ({reason}), best {best:+.0f}%, closed {pct:+.0f}%")
save(entry, exitp, peak, reason)
if exitp is not None:
    pct = (exitp / entry - 1) * 100
    if pct < 0 and best < 20:
        draft(f"STOPPED OUT on SPY {SIDE_W} @ {money(exitp)} avg, {pct:+.0f}%.\nThat is why we size small.\n@everyone")
        tail = f"Setup failed, stopped at {pct:+.0f}%. Risk was managed."
    else:
        sc = ", ".join(money(p) for p, q in banked)
        draft(f"ALL OUT on SPY {SIDE_W} @ {money(exitp)} avg, {pct:+.0f}%." + (f"\nScaled out at {sc}, then the runner." if banked else "") + "\n@everyone")
        tail = (f"Setup delivered, max profits were {best:.0f}%. 🧀" if best > 100 else
                f"Solid setup, max profits were {best:.0f}%." if best >= 50 else
                f"Not satisfied with setup as max profits were {best:.0f}% only.")
    draft(f"Just a note. I am fully hands off here. No active position remaining in SPY.\n\nI will let markets settle before alerting the next setup.\n\n{tail}\n@everyone")

# 4) re-entry after a breakeven or 43% stop exit (Titi, Oct 19). Example: Oct 19 12:25 puts, out at breakeven,
# then SPY broke the low of the move and kept going. Window 1: Penny re-enters once by herself. Other windows: REENTER note.
if (reason in ("breakeven", "step stop", "43% stop") or (reason == "EXIT" and exitp is not None and exitp <= entry * 1.02)) and spy_best is not None and not os.environ.get("REENTERED"):
    t_end = time.time() + 1800
    while time.time() < t_end and now().hour * 60 + now().minute < 950:
        try:
            spy = spy_price()
        except Exception:
            spy = None
        if spy and SPY_STOP and (spy - SPY_STOP) * DIR <= 0:
            break   # Belle's stop broke, the idea is dead
        if spy and (spy - spy_best) * DIR > 0.02:
            side_w = "calls" if DIR == 1 else "puts"
            if WIN1:
                ask = opt_ask()
                if ask and ask * 100 * QTY <= 250:
                    oid = buy(QTY, round(ask, 2))
                    if oid:
                        post(f"PENNY {LABEL}: re-entering {QTY} at {ask:.2f}, SPY broke the move's {'high' if DIR == 1 else 'low'} {spy_best:.2f}. Same stop as Belle (SPY {SPY_STOP})")
                        # hand the new order to a fresh run of this manager (same job), one re-entry only
                        os.environ.update({"ORDER_ID": oid, "LABEL": LABEL + " RE", "REENTERED": "1"})
                        os.execv(sys.executable, [sys.executable] + sys.argv)
                post(f"REENTER {LABEL} {side_w}: SPY broke the move's {'high' if DIR == 1 else 'low'} {spy_best:.2f}, Belle's stop SPY {SPY_STOP} intact. Penny could not fill, your call")
            else:
                post(f"REENTER {LABEL} {side_w}: SPY broke the move's {'high' if DIR == 1 else 'low'} {spy_best:.2f}, Belle's stop SPY {SPY_STOP} intact. Your call, Penny does not re-enter outside Window 1")
            break
        time.sleep(15)
