"""SHAY, the shadow (Oct 26 2026). Scores the Belle alerts Penny filtered out. No orders.

record (started by the relay the moment Penny skips an alert):
  saves the SPX and SPY contracts at Belle's strikes and their asks to results/shadow_signals.csv.
eval (runs in Nora's job after the close; EVAL_DATE = YYYY-MM-DD or "all" to rescore every day):
  1. picks the contract Penny would really have bought: Belle's strike, walked out of the money until it fits
     the price caps (SPX $70 to $250, SPY $0.60), the same rule as the relay. A rejected order keeps its own contract.
  2. replays it on 1 minute bars to 15:59 ET with the exit rule of its window:
     morning: 43% stop, breakeven after +60%, trail 30% below the best after +100%, SPY trims 1 at +50% and 1 at +100%
     EOD (15:00 on): 43% stop, breakeven after +60%, trail 20% below the best from +30% and 15% from +100%,
                     SPY trims 1 at +100% and 1 at +200%
  3. writes results/shadow_scores.csv (best price and time, heat before the best, exit, dollars).
  Bad prints (a bar low under half its body, or a high over twice its body) are ignored.
  SHAY_POST=1 also posts the skipped alerts summary to Discord.
"""
import csv
import datetime as dt
import os
import sys
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
DATA = "https://data.alpaca.markets"
H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"].strip(), "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"].strip()}
MODE = os.environ.get("MODE", "record").strip() or "record"
SIG = "results/shadow_signals.csv"
OUT = "results/shadow_trades.csv"
os.makedirs("results", exist_ok=True)


def now():
    return dt.datetime.now(ET)


def append(path, row, header):
    new = not os.path.exists(path)
    with open(path, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(header)
        w.writerow(row)


if MODE == "record":
    # SYM is "CONTRACT|reason;CONTRACT|reason" (one start per alert covers SPX and SPY), or one contract with REASON
    items = []
    for part in os.environ.get("SYM", "").split(";"):
        sym, _, why = part.strip().partition("|")
        if len(sym) >= 16:
            items.append((sym, why or os.environ.get("REASON", "")))
    if not items:
        print("no contract, nothing saved")
        sys.exit(0)
    try:
        sent = dt.datetime.fromtimestamp(float(os.environ.get("SENT", "")), ET)
    except ValueError:
        sent = now()
    q = requests.get(f"{DATA}/v1beta1/options/quotes/latest", headers=H, timeout=15,
                     params={"symbols": ",".join(s for s, _ in items), "feed": "indicative"}).json().get("quotes") or {}
    for sym, why in items:
        ask = (q.get(sym) or {}).get("ap") or ""
        append(SIG, [f"{sent:%Y-%m-%d}", f"{sent:%H:%M}", os.environ.get("SIDE", ""), sym, ask, why],
               ["date", "time_et", "side", "contract", "entry", "reason"])
        print("saved", sym, ask, why)
    sys.exit(0)

# ---------- eval ----------
import re
from collections import OrderedDict

OUTS = "results/shadow_scores.csv"
COLS = ["date", "time_et", "side", "reason", "belle_contract", "contract", "qty", "entry", "best", "best_pct", "best_time_et",
        "low_before_best", "heat_pct", "rule", "exit", "pl", "result"]
want = os.environ.get("EVAL_DATE", "").strip()
if not want and now().hour < 16:
    print("before 16:00 ET, the day is not done yet")
    sys.exit(0)
if not os.path.exists(SIG):
    print("no shadow signals yet")
    sys.exit(0)
with open(SIG) as fh:
    sigs = list(csv.DictReader(fh))
days = sorted({r["date"] for r in sigs}) if want == "all" else [want or f"{now():%Y-%m-%d}"]


def parse(sym):
    m = re.match(r"^(SPXW|SPY)(\d{6})([CP])(\d{8})$", sym)
    return (m.group(1), m.group(2), m.group(3), int(m.group(4)) / 1000) if m else None


def get_bars(syms, t0, t1):
    out, token = {}, None
    while True:
        p = {"symbols": ",".join(syms), "timeframe": "1Min", "start": t0.isoformat(), "end": t1.isoformat(), "limit": 10000}
        if token:
            p["page_token"] = token
        j = requests.get(f"{DATA}/v1beta1/options/bars", headers=H, timeout=30, params=p).json()
        for s, b in (j.get("bars") or {}).items():
            out.setdefault(s, []).extend(b)
        token = j.get("next_page_token")
        if not token:
            return out


def clean(b):
    """ignore bad prints: a low under half the bar body or a high over twice it"""
    lo_b, hi_b = min(b["o"], b["c"]), max(b["o"], b["c"])
    lo = b["l"] if b["l"] >= lo_b * 0.5 else lo_b
    hi = b["h"] if b["h"] <= hi_b * 2 else hi_b
    return lo, hi


def bt(b):
    return dt.datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET)


def pick(root, ymd, cp, k0, t0, t1):
    """the contract Penny would have bought: walk out of the money until the price fits the caps"""
    step = 1 if root == "SPY" else 5
    d = 1 if cp == "C" else -1
    ks = [k0 + d * i * step for i in range(11)]
    syms = [f"{root}{ymd}{cp}{int(round(k * 1000)):08d}" for k in ks]
    bars = get_bars(syms, t0, t1)
    for s in syms:
        b = [x for x in bars.get(s, []) if bt(x) < t0 + dt.timedelta(minutes=3)]
        if not b:
            continue
        px = b[0]["o"]
        if root == "SPY":
            if px * 100 <= 60:
                return s, bars[s]
        else:
            if px * 100 > 250:
                continue
            return (s, bars[s]) if px * 100 >= 70 else (None, None)
    return None, None


def replay(bars, e, eod, qty):
    """returns exit dollars for qty contracts with trims, the blended exit price, and the best/heat stats"""
    peak, left, cash = e, qty, 0.0
    trims = ((2.0, 3.0) if eod else (1.5, 2.0)) if qty >= 3 else ()
    done = set()
    for b in bars:
        lo, hi = clean(b)
        stop = e * 0.57
        if peak >= e * 1.6:
            stop = max(stop, e)
        if eod:
            if peak >= e * 1.3:
                stop = max(stop, peak * 0.80)
            if peak >= e * 2.0:
                stop = max(stop, peak * 0.85)
        elif peak >= e * 2.0:
            stop = max(stop, peak * 0.70)
        if lo <= stop:
            cash += min(stop, b["o"]) * left
            left = 0
            break
        peak = max(peak, hi)
        for lv in trims:
            if lv not in done and peak >= e * lv and left >= 2:
                done.add(lv)
                cash += e * lv
                left -= 1
    if left:
        cash += bars[-1]["c"] * left
    return cash / qty


rows_out = []
for day in days:
    for r in [x for x in sigs if x["date"] == day]:
        p = parse(r["contract"])
        if not p:
            continue
        root, ymd, cp, k0 = p
        t0 = dt.datetime.fromisoformat(f"{r['date']}T{r['time_et']}").replace(tzinfo=ET)
        t1 = t0.replace(hour=16, minute=0)
        own = re.search(r"\((SPXW?\d{6}[CP]\d{8}|SPY\d{6}[CP]\d{8})\)", r["reason"])
        if own:
            sym = own.group(1)
            bars = get_bars([sym], t0, t1).get(sym)
        else:
            sym, bars = pick(root, ymd, cp, k0, t0, t1)
        if not sym or not bars:
            print(r["time_et"], r["contract"], "no contract Penny could buy, not scored")
            continue
        bars = [b for b in bars if bt(b) >= t0]
        if not bars:
            continue
        qty = 3 if root == "SPY" else 1
        e = bars[0]["o"]
        eod = t0.hour * 60 + t0.minute >= 900
        hs = [clean(b) for b in bars]
        hi_i = max(range(len(bars)), key=lambda i: hs[i][1])
        best = hs[hi_i][1]
        low_before = min(h[0] for h in hs[:hi_i + 1])
        ex = replay(bars, e, eod, qty)
        pl = (ex - e) * 100 * qty
        short = r["reason"].split(" (")[0].split(":")[0].strip()
        rows_out.append({"date": r["date"], "time_et": r["time_et"], "side": r["side"], "reason": short,
                         "belle_contract": r["contract"], "contract": sym, "qty": qty, "entry": f"{e:.2f}",
                         "best": f"{best:.2f}", "best_pct": f"{(best / e - 1) * 100:.0f}", "best_time_et": f"{bt(bars[hi_i]):%H:%M}",
                         "low_before_best": f"{low_before:.2f}", "heat_pct": f"{(low_before / e - 1) * 100:.0f}",
                         "rule": "EOD" if eod else "morning", "exit": f"{ex:.2f}", "pl": f"{pl:.0f}",
                         "result": "win" if pl > 0 else ("flat" if pl == 0 else "loss")})
        print(rows_out[-1])

# rewrite the scored days, keep every other day as it is
keep = []
if os.path.exists(OUTS):
    with open(OUTS) as fh:
        keep = [x for x in csv.DictReader(fh) if x["date"] not in days]
with open(OUTS, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader()
    for x in sorted(keep + rows_out, key=lambda x: (x["date"], x["time_et"], x["contract"])):
        w.writerow(x)
print(len(rows_out), "shadow trades scored for", ", ".join(days))


def ct(hm):
    h, m = hm.split(":")
    return f"{int(h) - 1:02d}:{m}"


def summary(day):
    rows = [x for x in rows_out if x["date"] == day]
    if not rows:
        return ""
    alerts = OrderedDict()
    for x in rows:
        alerts.setdefault((x["time_et"], x["side"], x["reason"]), []).append(x)
    groups = []
    for (t, side, why), xs in alerts.items():
        g = groups[-1] if groups else None
        if g and g["side"] == side and g["why"] == why:
            g["times"].append(t)
            g["rows"] += xs
        else:
            groups.append({"side": side, "why": why, "times": [t], "rows": list(xs)})
    L = ["**SKIPPED ALERTS TODAY**", ""]
    saved = cost = 0
    for g in groups:
        a, b = g["times"][0], g["times"][-1]
        n = len(g["times"])
        when = f"{a} ET ({ct(a)} CT)" if a == b else f"{a} to {b} ET ({ct(a)} to {ct(b)} CT)"
        L.append(f"{when} {g['side']}" + (f", {n} alerts" if n > 1 else ""))
        L.append(f"Skipped: {g['why']}")
        for lab, pre in (("SPX", "SPXW"), ("SPY", "SPY")):
            xs = [x for x in g["rows"] if x["contract"].startswith(pre)]
            if not xs:
                continue
            ps = sorted(int(x["best_pct"]) for x in xs)
            top = max(xs, key=lambda x: int(x["best_pct"]))
            rng = f"+{ps[0]}%" if ps[0] == ps[-1] else f"+{ps[0]}% to +{ps[-1]}%"
            L.append(f"{lab} best {rng} at {top['best_time_et']}")
        pl = sum(int(x["pl"]) for x in g["rows"])
        L.append(f"Would have made ${pl:,}" if pl > 0 else (f"Would have lost ${-pl:,}" if pl < 0 else "Would have been flat"))
        L.append("")
        for t in g["times"]:
            s = sum(int(x["pl"]) for x in g["rows"] if x["time_et"] == t)
            saved += s <= 0
            cost += s > 0
    L.append(f"Filters saved {saved}, cost {cost}")
    return "\n".join(L)


for day in days[-1:]:
    text = summary(day)
    print(text)
    hook = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if text and hook and os.environ.get("SHAY_POST") == "1" and want != "all":
        try:
            requests.post(hook, json={"content": text[:1900]}, timeout=10)
        except Exception as ex:
            print("discord failed", ex)
