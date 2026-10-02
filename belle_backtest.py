"""
Belle backtest: Titi's EOD liquidity sweep method on SPX 0DTE.

What it does, in order, for every day in the data:
 1. Marks ES liquidity pools: PDH, PDL, midnight open, 9:30 open,
    overnight high and low, the 13:30 to 14:00 candle high and low,
    and today's swing highs and lows.
 2. Inside Window 1 (14:00 to 14:50 ET) and Window 2 (closes 15:30 to 15:55 ET)
    it looks for a sweep: a candle trades through a live pool and closes
    back inside it.
 3. BIAS is time frame continuity at the close: 1H and 4H candles both green
    means calls, both red means puts. If they split, Window 1 uses the 15m
    trend and Window 2 uses the 9:30 candle colour.
 4. Trigger, any one alone: a sweep, an equal highs or lows tap, an order
    block opening, a rejection block or an FVG CE. A sweep of a key pool
    (equal highs/lows, PDH/PDL, swing, 13:30 candle) trades the reversal on
    its own; every other trigger must match the bias. The CLOSE confirms (or
    the next candle's close). Max 2 a day, 1 per window.
    In the first hour of a 4H candle the 4H vote is the 4H that just closed.
 5. It measures how far SPX moved in the trade's favour before 15:59, and
    whether strikes 10, 15, 20 and 25 points out of the money went in the money.

Score notes (they never block a trade): CISD within 3 bars, failed 2
(Strat shooter or hammer), ES versus NQ SMT, 1H and 4H candle colour.

Run:  python belle_backtest.py              (downloads free Yahoo data)
      python belle_backtest.py --csv data/   (uses saved CSVs instead)
"""
import argparse
import math
import os
from datetime import time, timedelta

import pandas as pd

import config as C

TZ = "America/New_York"


# ---------------------------------------------------------------- data
def load_yahoo(symbol):
    import yfinance as yf
    df = yf.Ticker(symbol).history(period=C.PERIOD, interval="5m",
                                   prepost=True, auto_adjust=False)
    df = df[["Open", "High", "Low", "Close"]].dropna()
    df.index = df.index.tz_convert(TZ)
    return df


def load_csv(folder, symbol):
    name = symbol.replace("=", "").replace("^", "")
    df = pd.read_csv(os.path.join(folder, f"{name}.csv"), index_col=0)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(TZ)
    return df[["Open", "High", "Low", "Close"]]


def resample(df, minutes):
    if minutes == 5:
        return df
    return (df.resample(f"{minutes}min", label="left", closed="left")
              .agg({"Open": "first", "High": "max", "Low": "min", "Close": "last"})
              .dropna())


# ---------------------------------------------------------------- helpers
def at(ts_date, hh, mm):
    return pd.Timestamp.combine(ts_date, time(hh, mm)).tz_localize(TZ)


def between(df, start, end):
    return df[(df.index >= start) & (df.index < end)]


def swings(day, look):
    """Confirmed swing highs and lows: (confirm_time, level, kind)."""
    out = []
    h, l, idx = day["High"].values, day["Low"].values, day.index
    for i in range(look, len(day) - look):
        win_h = h[i - look:i + look + 1]
        win_l = l[i - look:i + look + 1]
        if h[i] == win_h.max():
            out.append((idx[i + look], h[i], "swing high"))
        if l[i] == win_l.min():
            out.append((idx[i + look], l[i], "swing low"))
    return out


def strike_for(spx_price, direction, dist):
    if direction == "puts":
        return math.floor((spx_price - dist) / C.STRIKE_STEP) * C.STRIKE_STEP
    return math.ceil((spx_price + dist) / C.STRIKE_STEP) * C.STRIKE_STEP


def window_of(t_close):
    for name, ((h1, m1), (h2, m2)) in C.WINDOWS.items():
        if time(h1, m1) < t_close.time() <= time(h2, m2):
            return name
    return None


# ---------------------------------------------------------------- bias, order blocks, rejection blocks
def bias_for(es, d):
    """Direction from the 10:00 4H candle (10:00 to 14:00), judged against the 6:00 candle."""
    c10 = between(es, at(d, 10, 0), at(d, 14, 0))
    c6 = between(es, at(d, 6, 0), at(d, 10, 0))
    if c10.empty or c6.empty:
        return None
    o, h, l, c = c10["Open"].iloc[0], c10["High"].max(), c10["Low"].min(), c10["Close"].iloc[-1]
    took_high = h > c6["High"].max() and c < c6["High"].max()
    took_low = l < c6["Low"].min() and c > c6["Low"].min()
    if took_high and not took_low:
        return "puts"
    if took_low and not took_high:
        return "calls"
    return "puts" if c < o else "calls" if c > o else None


def blocks(day, look, t):
    """Live order block openings, rejection blocks and FVG CEs known before time t."""
    before = day[day.index < t]
    out = {"puts": [], "calls": []}
    sw = [s for s in swings(before, look) if s[0] < t]
    o, cl, hi, lo = before["Open"].values, before["Close"].values, before["High"].values, before["Low"].values
    idx = list(before.index)
    for conf_t, lvl, kind in sw:
        i = idx.index(conf_t) - look
        after = before[before.index > conf_t]
        if kind == "swing high":
            body_top = max(o[i], cl[i])
            if after.empty or after["Close"].max() <= lvl:
                out["puts"].append(("rejection block", body_top))
        else:
            body_bot = min(o[i], cl[i])
            if after.empty or after["Close"].min() >= lvl:
                out["calls"].append(("rejection block", body_bot))
    # order blocks: last opposite candle before a close through the latest swing
    last_h = last_l = None
    for j in range(1, len(before)):
        for conf_t, lvl, kind in sw:
            if conf_t <= idx[j]:
                if kind == "swing high":
                    last_h = lvl
                else:
                    last_l = lvl
        if last_l is not None and cl[j] < last_l <= cl[j - 1]:
            for k in range(j - 1, max(j - 11, -1), -1):
                if cl[k] > o[k]:
                    if before["Close"].iloc[j:].max() <= hi[k]:
                        out["puts"].append(("bearish order block opening", o[k]))
                    break
        if last_h is not None and cl[j] > last_h >= cl[j - 1]:
            for k in range(j - 1, max(j - 11, -1), -1):
                if cl[k] < o[k]:
                    if before["Close"].iloc[j:].min() >= lo[k]:
                        out["calls"].append(("bullish order block opening", o[k]))
                    break
    # fair value gaps: entry at the CE (50%) while the gap is still open
    for j in range(2, len(before)):
        if lo[j] > hi[j - 2]:                                   # bullish FVG
            ce = (lo[j] + hi[j - 2]) / 2
            if before["Close"].iloc[j + 1:].min() >= hi[j - 2] if j + 1 < len(before) else True:
                out["calls"].append(("bullish FVG CE", ce))
        if hi[j] < lo[j - 2]:                                   # bearish FVG
            ce = (hi[j] + lo[j - 2]) / 2
            if before["Close"].iloc[j + 1:].max() <= lo[j - 2] if j + 1 < len(before) else True:
                out["puts"].append(("bearish FVG CE", ce))
    return out


# ---------------------------------------------------------------- one day
def run_day(d, prev_d, es, nq, spx, tf):
    step = timedelta(minutes=tf)
    rth = between(es, at(d, 9, 30), at(d, 16, 0))
    prev_rth = between(es, at(prev_d, 9, 30), at(prev_d, 16, 0))
    if rth.empty or prev_rth.empty:
        return []

    overnight = between(es, at(prev_d, 18, 0), at(d, 9, 30))
    midnight = between(es, at(d, 0, 0), at(d, 0, 0) + step)
    c1330 = between(es, at(d, 13, 30), at(d, 14, 0))

    fixed = [("PDH", prev_rth["High"].max(), "above"),
             ("PDL", prev_rth["Low"].min(), "below"),
             ("9:30 open", rth["Open"].iloc[0], "both")]
    if not midnight.empty:
        fixed.append(("midnight open", midnight["Open"].iloc[0], "both"))
    if not overnight.empty:
        fixed += [("overnight high", overnight["High"].max(), "above"),
                  ("overnight low", overnight["Low"].min(), "below")]
    if not c1330.empty:
        fixed += [("13:30 candle high", c1330["High"].max(), "near_above"),
                  ("13:30 candle low", c1330["Low"].min(), "near_below")]

    sw = swings(rth, C.SWING_LOOKBACK)
    nq_rth = between(nq, at(d, 9, 30), at(d, 16, 0))
    spx_day = between(spx, at(d, 9, 30), at(d, 16, 0))
    if spx_day.empty:
        return []

    bias = bias_for(es, d)          # 10:00 4H read: a note only
    es15 = resample(es, 15)
    o930 = between(es15, at(d, 9, 30), at(d, 9, 45))
    open_colour = None if o930.empty else ("calls" if o930["Close"].iloc[0] > o930["Open"].iloc[0] else "puts")
    trades, used = [], set()
    bars = list(rth.index)
    pending = None                  # a reaction whose candle closed the wrong colour
    for i, t in enumerate(bars):
        if t < at(d, 13, 30) or len(trades) >= C.MAX_PER_DAY:
            continue
        bar = rth.loc[t]
        before = rth[rth.index < t]
        if before.empty:
            continue
        win = window_of(t + step)
        tf_bias, why_bias = window_bias(es, es15, d, t + step, bar["Close"], win, open_colour)

        # 1. a pending reaction confirmed by THIS candle's close
        if pending is not None:
            p, pending = pending, None
            if (win and win not in used and _closes_with(bar, p["direction"])
                    and (p["direction"] == tf_bias or p["pool"] in C.TOP_POOLS)):
                p["bias_why"] = why_bias
                _add(trades, used, p, d, win, t, bar, rth, nq_rth, es, spx_day, step, bias, i, bars)
                continue

        # 2. look for a new reaction on this candle (both sides; bias is checked at entry)
        found = []
        for direction in ("puts", "calls"):
            pools = _pools(direction, fixed, sw, before, t, d, step)
            if direction == "puts":
                hit = [(n, l) for n, l in pools if
                       (bar["High"] > l or (n == "equal highs" and bar["High"] >= l - C.EQ_TOL)) and bar["Close"] < l]
            else:
                hit = [(n, l) for n, l in pools if
                       (bar["Low"] < l or (n == "equal lows" and bar["Low"] <= l + C.EQ_TOL)) and bar["Close"] > l]
            if not hit:
                # PD arrays alone also count: order block opening, rejection block, FVG CE
                hit = [(n, l) for n, l in blocks(rth, C.SWING_LOOKBACK, t)[direction]
                       if ((bar["High"] >= l and bar["Close"] < l) if direction == "puts"
                           else (bar["Low"] <= l and bar["Close"] > l))]
            if hit:
                rank = lambda x: (x[0] in C.TOP_POOLS, x[1] if direction == "puts" else -x[1])
                found.append((direction, max(hit, key=rank)))
        if not found:
            continue
        found.sort(key=lambda f: f[0] != tf_bias)       # prefer the side that matches the bias
        direction, (pool_name, pool_lvl) = found[0]
        p = {"direction": direction, "pool": pool_name, "level": pool_lvl, "t": t, "bar": bar, "bias_why": why_bias}
        if win and win not in used and _closes_with(bar, direction) and (direction == tf_bias or pool_name in C.TOP_POOLS):
            _add(trades, used, p, d, win, t, bar, rth, nq_rth, es, spx_day, step, bias, i, bars)
        else:
            pending = p           # wait one candle: its close must confirm, in the bias direction
    return trades


def _colour(df, start, now, price):
    seg = df[(df.index >= start) & (df.index < now)]
    if seg.empty:
        return None
    o = seg["Open"].iloc[0]
    return "calls" if price > o else "puts" if price < o else None


def trend_15m(es15, now, look=2):
    """15m structure before now: higher highs and higher lows = calls, lower highs and lower lows = puts."""
    seg = es15[(es15.index < now - timedelta(minutes=15)) & (es15.index >= now - timedelta(days=2))]
    sw = swings(seg, look)
    hs = [l for _, l, k in sw if k == "swing high"][-2:]
    ls = [l for _, l, k in sw if k == "swing low"][-2:]
    if len(hs) < 2 or len(ls) < 2:
        return None
    if hs[1] > hs[0] and ls[1] > ls[0]:
        return "calls"
    if hs[1] < hs[0] and ls[1] < ls[0]:
        return "puts"
    return None


def window_bias(es, es15, d, now, price, win, open_colour):
    """Time frame continuity: the 1H and 4H candles in force at the close.
    If they disagree: Window 1 uses the 15m trend, Window 2 uses the 9:30 candle colour."""
    h1_start = now.floor("h") if now.minute else now - timedelta(hours=1)
    h1 = _colour(es, h1_start, now, price)
    start4 = max(h for h in (2, 6, 10, 14) if h < now.hour + (1 if now.minute else 0))
    if h1_start == at(d, start4, 0):
        # first hour of a new 4H candle: the 1H and 4H are the same candle, so use the 4H that just closed
        prev = between(es, at(d, start4 - 4, 0), at(d, start4, 0))
        h4 = None if prev.empty else _colour(prev, prev.index[0], at(d, start4, 0), prev["Close"].iloc[-1])
    else:
        h4 = _colour(es, at(d, start4, 0), now, price)
    if h1 and h1 == h4:
        return h1, f"1H and 4H both {'green' if h1 == 'calls' else 'red'}"
    if win == "W2":
        return open_colour, "1H and 4H split, 9:30 candle " + ("green" if open_colour == "calls" else "red")
    tr = trend_15m(es15, now)
    return tr, "1H and 4H split, 15m trend " + ({"calls": "up", "puts": "down"}.get(tr, "unclear"))


def _closes_with(bar, direction):
    return bar["Close"] < bar["Open"] if direction == "puts" else bar["Close"] > bar["Open"]


def _pools(direction, fixed, sw, before, t, d, step):
    """Live liquidity pools for one direction, known before candle t."""
    pools = []
    prev_close = before["Close"].iloc[-1]
    for name, lvl, side in fixed:
        if name.startswith("13:30") and t < at(d, 14, 0):
            continue
        if side == "near_above":
            if direction == "puts" and prev_close < lvl:
                pools.append((name, lvl))
        elif side == "near_below":
            if direction == "calls" and prev_close > lvl:
                pools.append((name, lvl))
        elif side == "both":
            if direction == "puts" and prev_close < lvl:
                pools.append((name, lvl))
            if direction == "calls" and prev_close > lvl:
                pools.append((name, lvl))
        elif direction == "puts" and side == "above" and lvl > before["High"].max():
            pools.append((name, lvl))
        elif direction == "calls" and side == "below" and lvl < before["Low"].min():
            pools.append((name, lvl))
    live_h, live_l = [], []
    for conf_t, lvl, kind in sw:
        if conf_t > t - step:
            continue
        after = before[before.index > conf_t]
        if kind == "swing high" and (after.empty or after["High"].max() <= lvl):
            live_h.append(lvl)
        if kind == "swing low" and (after.empty or after["Low"].min() >= lvl):
            live_l.append(lvl)
    if direction == "puts":
        pools += [("swing high", l) for l in live_h]
        for a_i, a in enumerate(live_h):        # equal highs: two untaken swing highs within EQ_TOL
            for b in live_h[a_i + 1:]:
                if abs(a - b) <= C.EQ_TOL:
                    pools.append(("equal highs", max(a, b)))
    else:
        pools += [("swing low", l) for l in live_l]
        for a_i, a in enumerate(live_l):
            for b in live_l[a_i + 1:]:
                if abs(a - b) <= C.EQ_TOL:
                    pools.append(("equal lows", min(a, b)))
    return pools


def _add(trades, used, p, d, win, t, bar, rth, nq_rth, es, spx_day, step, bias, i, bars):
    direction = p["direction"]
    entry_t = t + step
    tr = score_trade(d, direction, win, p["t"], t, entry_t, p["bar"], bar,
                     p["pool"], p["level"], bar["Open"], rth, nq_rth, es, spx_day, step)
    tr["bias_4h"] = bias
    tr["bias_why"] = p.get("bias_why")
    tr["prime"] = entry_t.time() >= time(14, 40) and win == "W1"
    tr["with_4h_bias"] = bias == direction
    tr["confirmed_next_candle"] = p["t"] != t
    tr["nth_of_day"] = len(trades) + 1
    tr["cisd_within_bars"] = None
    trades.append(tr)
    used.add(win)


def score_trade(d, direction, win, sweep_t, cisd_t, entry_t, sbar, cbar,
                pool_name, pool_lvl, cisd_lvl, rth, nq_rth, es, spx_day, step):
    prior = rth[rth.index < sweep_t]
    prev = prior.iloc[-1]
    if direction == "puts":
        failed2 = sbar["High"] > prev["High"] and sbar["Low"] >= prev["Low"] and sbar["Close"] < prev["High"] and sbar["Close"] < sbar["Open"]
        es_new = sbar["High"] > prior["High"].max()
    else:
        failed2 = sbar["Low"] < prev["Low"] and sbar["High"] <= prev["High"] and sbar["Close"] > prev["Low"] and sbar["Close"] > sbar["Open"]
        es_new = sbar["Low"] < prior["Low"].min()
    smt = None
    if sweep_t in nq_rth.index:
        nq_prior = nq_rth[nq_rth.index < sweep_t]
        nb = nq_rth.loc[sweep_t]
        if not nq_prior.empty:
            nq_new = nb["High"] > nq_prior["High"].max() if direction == "puts" else nb["Low"] < nq_prior["Low"].min()
            smt = bool(es_new != nq_new)

    entry_es = cbar["Close"]
    # SPX at entry: same-time bar, else ES minus the latest basis
    spx_at = spx_day[spx_day.index <= cisd_t]
    if cisd_t in spx_day.index:
        spx_entry = spx_day.loc[cisd_t, "Close"]
    else:
        last = spx_at.index[-1]
        spx_entry = entry_es - (es.loc[last, "Close"] - spx_day.loc[last, "Close"]) if last in es.index else spx_at["Close"].iloc[-1]
    path = spx_day[spx_day.index >= entry_t]
    close = spx_day["Close"].iloc[-1]
    if direction == "puts":
        best = path["Low"].min() if not path.empty else close
        max_move = spx_entry - best
        close_move = spx_entry - close
    else:
        best = path["High"].max() if not path.empty else close
        max_move = best - spx_entry
        close_move = close - spx_entry
    by_dist = {}
    for dist in C.OTM_LIST:
        strike = strike_for(spx_entry, direction, dist)
        gap = abs(strike - spx_entry)
        by_dist[f"strike_{dist}"] = strike
        by_dist[f"itm_{dist}"] = bool(max_move > gap)
        by_dist[f"itm_close_{dist}"] = bool(close_move > gap)
    stop = max(sbar["High"], cbar["High"]) if direction == "puts" else min(sbar["Low"], cbar["Low"])
    es_after = rth[rth.index >= entry_t]
    stopped = bool((es_after["High"] > stop).any() if direction == "puts" else (es_after["Low"] < stop).any())

    # context: 1H and 4H candle colour at entry (ES 4H opens at 18,22,2,6,10,14 ET)
    h1_open = es[es.index >= entry_t.floor("h")]["Open"].iloc[0]
    four = max(h for h in (2, 6, 10, 14) if h <= entry_t.hour)
    h4_open = es[es.index >= at(d, four, 0)]["Open"].iloc[0]
    colour = lambda o: "green" if entry_es > o else "red"

    return {
        "date": str(d), "window": win, "direction": direction,
        "sweep_time": sweep_t.strftime("%H:%M"), "entry_time": entry_t.strftime("%H:%M"),
        "pool_swept": pool_name, "pool_level": round(pool_lvl, 2),
        "cisd_level": round(cisd_lvl, 2), "entry_es": round(entry_es, 2), "stop_es": round(stop, 2),
        "spx_entry": round(spx_entry, 2), "spx_close": round(close, 2),
        "max_move_pts": round(max_move, 2), "close_move_pts": round(close_move, 2),
        **by_dist,
        "stop_hit": stopped, "failed_2": bool(failed2), "smt": smt,
        "h1": colour(h1_open), "h4": colour(h4_open),
    }


# ---------------------------------------------------------------- report
def pct(s):
    return f"{100 * s.mean():.0f}%" if len(s) else "n/a"


def move_stats(g):
    q = g["max_move_pts"].quantile([0.25, 0.5, 0.75])
    return f"{q[0.25]:.0f} / {q[0.5]:.0f} / {q[0.75]:.0f}"


def summarize(df, tf, key):
    lines = [f"## {tf} minute signals", ""]
    if df.empty:
        return lines + ["No signals.", ""]
    weeks = max(1, df["date"].nunique() / 5)
    lines += [f"Signals: {len(df)} ({len(df) / weeks:.1f} per week). Entry = the sweep candle's close.", "",
              "**How far SPX moved after the signal (best point before 15:59), in SPX points: 25th / median / 75th percentile**", "",
              "| Group | Signals | Move |", "| --- | --- | --- |",
              f"| All | {len(df)} | {move_stats(df)} |"]
    for col in ("window", "direction"):
        for val, g in df.groupby(col):
            lines.append(f"| {col} = {val} | {len(g)} | {move_stats(g)} |")
    for val, g in df.groupby(["window", "direction"]):
        lines.append(f"| {val[0]} {val[1]} | {len(g)} | {move_stats(g)} |")
    lines += ["", "**Strike went in the money by 15:59, by distance out of the money**", "",
              "| Group | " + " | ".join(f"{d} pts" for d in C.OTM_LIST) + " |",
              "| --- |" + " --- |" * len(C.OTM_LIST)]
    groups = [("All", df)] + [(f"{w} {dr}", g) for (w, dr), g in df.groupby(["window", "direction"])]
    for name, g in groups:
        lines.append(f"| {name} | " + " | ".join(pct(g[f"itm_{d}"]) for d in C.OTM_LIST) + " |")
    lines += ["", "**Score notes (never block a trade): share reaching ITM at 15 pts**", "",
              "| Note | Signals | ITM at 15 pts |", "| --- | --- | --- |"]
    for col in ("pool_swept", "with_4h_bias", "confirmed_next_candle", "failed_2", "smt", "h1", "h4"):
        for val, g in df.groupby(col, dropna=False):
            lines.append(f"| {col} = {val} | {len(g)} | {pct(g['itm_15'])} |")
    lines += ["", "**Answer key check**", ""]
    for _, r in key.iterrows():
        m = df[(df["date"] == r["date"]) & (df["direction"] == r["direction"])]
        found = ", ".join(f"{x.window} entry {x.entry_time} at {x.pool_swept}, moved {x.max_move_pts} pts" for x in m.itertuples()) or "NOT FLAGGED"
        other = df[(df["date"] == r["date"]) & (df["direction"] != r["direction"])]
        if len(other):
            found += " | WRONG WAY: " + ", ".join(f"{x.direction} {x.entry_time}" for x in other.itertuples())
        lines.append(f"- {r['date']} {r['contract']}: {found}")
    return lines + [""]


def log_history(df, tf, run_date):
    """One row per run day and timeframe, kept forever in results/history.csv."""
    path = "results/history.csv"
    row = {"run_date": run_date, "timeframe": f"{tf}m", "signals": len(df)}
    if not df.empty:
        row["median_move_pts"] = round(df["max_move_pts"].median(), 1)
        for w in C.WINDOWS:
            g = df[df["window"] == w]
            row[f"{w}_median_move_pts"] = round(g["max_move_pts"].median(), 1) if len(g) else None
        for d in C.OTM_LIST:
            row[f"itm_{d}_pct"] = round(100 * df[f"itm_{d}"].mean())
    hist = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()
    if not hist.empty:
        hist = hist[~((hist["run_date"] == run_date) & (hist["timeframe"] == f"{tf}m"))]
    pd.concat([hist, pd.DataFrame([row])], ignore_index=True).to_csv(path, index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="folder of saved CSVs instead of downloading")
    ap.add_argument("--save", help="folder to save downloaded CSVs")
    a = ap.parse_args()

    raw = {}
    for s in (C.ES, C.NQ, C.SPX):
        raw[s] = load_csv(a.csv, s) if a.csv else load_yahoo(s)
        if a.save:
            os.makedirs(a.save, exist_ok=True)
            raw[s].to_csv(os.path.join(a.save, s.replace("=", "").replace("^", "") + ".csv"))

    key = pd.read_csv("answer_key.csv", dtype=str)
    os.makedirs("results", exist_ok=True)
    run_date = pd.Timestamp.now(tz=TZ).strftime("%Y-%m-%d")
    report = ["# Belle backtest results", "",
              f"Data: Yahoo Finance, last {C.PERIOD}. Run {run_date}.", ""]
    for tf in C.TIMEFRAMES:
        es, nq, spx = (resample(raw[s], tf) for s in (C.ES, C.NQ, C.SPX))
        days = sorted(set(spx.index.date))
        rows = []
        for prev_d, d in zip(days, days[1:]):
            rows += run_day(d, prev_d, es, nq, spx, tf)
        df = pd.DataFrame(rows)
        df.to_csv(f"results/signals_{tf}m.csv", index=False)
        report += summarize(df, tf, key)
        log_history(df, tf, run_date)
        print(f"{tf}m: {len(df)} signals")
    with open("results/summary.md", "w") as f:
        f.write("\n".join(report))
    print("\n".join(report))


if __name__ == "__main__":
    main()
