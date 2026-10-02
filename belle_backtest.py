"""
Belle backtest: Titi's EOD liquidity sweep method on SPX 0DTE.

What it does, in order, for every day in the data:
 1. Marks ES liquidity pools: PDH, PDL, midnight open, 9:30 open,
    overnight high and low, the 13:30 to 14:00 candle high and low,
    and today's swing highs and lows.
 2. Inside Window 1 (14:00 to 14:50 ET) and Window 2 (closes 15:30 to 15:55 ET)
    it looks for a sweep: a candle trades through a live pool and closes
    back inside it.
 3. Bias from the 10:00 4H candle: took the 6:00 high and closed back below,
    or closed red, means puts only. The mirror means calls only.
 4. No pool swept? A rejection of an order block opening or a rejection block
    (the swing candle wick) also counts. The trigger candle must close in the
    trade direction. Entry is its close, stop is its extreme.
    Max 2 trades a day, 1 per window.
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
    """Live order block openings and rejection blocks known before time t."""
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

    bias = bias_for(es, d)
    if bias is None:
        return []
    trades, used = [], set()
    bars = list(rth.index)
    for i, t in enumerate(bars):
        if t < at(d, 13, 45):
            continue
        bar = rth.loc[t]
        before = rth[rth.index < t]
        if before.empty:
            continue

        if len(trades) >= C.MAX_PER_DAY:
            break
        win = window_of(t + step)
        if win is None or win in used:
            continue
        for direction in (bias,):
            # live pools: not yet traded through since 9:30, known before t
            pools = []
            for name, lvl, side in fixed:
                if name.startswith("13:30") and t < at(d, 14, 0):
                    continue
                prev_close = before["Close"].iloc[-1]
                if side == "near_above":
                    if direction == "puts" and prev_close < lvl:
                        pools.append((name, lvl))
                    continue
                if side == "near_below":
                    if direction == "calls" and prev_close > lvl:
                        pools.append((name, lvl))
                    continue
                if side == "both":
                    # opens act as pools from whichever side price sits on
                    if direction == "puts" and prev_close < lvl:
                        pools.append((name, lvl))
                    if direction == "calls" and prev_close > lvl:
                        pools.append((name, lvl))
                    continue
                if direction == "puts" and side == "above" and lvl > before["High"].max():
                    pools.append((name, lvl))
                if direction == "calls" and side == "below" and lvl < before["Low"].min():
                    pools.append((name, lvl))
            for conf_t, lvl, kind in sw:
                if conf_t > t - step:
                    continue
                after = before[before.index > conf_t]
                if direction == "puts" and kind == "swing high" and (after.empty or after["High"].max() <= lvl):
                    pools.append((kind, lvl))
                if direction == "calls" and kind == "swing low" and (after.empty or after["Low"].min() >= lvl):
                    pools.append((kind, lvl))

            # sweep: trade through, close back inside
            if direction == "puts":
                hit = [(n, l) for n, l in pools if bar["High"] > l and bar["Close"] < l]
            else:
                hit = [(n, l) for n, l in pools if bar["Low"] < l and bar["Close"] > l]
            if hit:
                pool_name, pool_lvl = (max if direction == "puts" else min)(hit, key=lambda x: x[1])
            else:
                hit = [(n, l) for n, l in blocks(rth, C.SWING_LOOKBACK, t)[direction]
                       if ((bar["High"] >= l and bar["Close"] < l) if direction == "puts"
                           else (bar["Low"] <= l and bar["Close"] > l))]
                if not hit:
                    continue
                pool_name, pool_lvl = hit[-1]
            # the trigger candle must close in the trade direction
            if (bar["Close"] < bar["Open"]) != (direction == "puts"):
                continue

            # CISD level: open of the first candle in the run into the sweep
            k = i if (bar["Close"] > bar["Open"]) == (direction == "puts") else i - 1
            want_up = direction == "puts"
            while k > 0 and (rth.iloc[k]["Close"] > rth.iloc[k]["Open"]) == want_up:
                k -= 1
            cisd_lvl = rth.iloc[min(k + 1, i)]["Open"]
            cisd_bar = None
            for j in range(i, min(i + C.CISD_MAX_BARS + 1, len(bars))):
                cb = rth.iloc[j]
                if (cb["Close"] < cisd_lvl) if direction == "puts" else (cb["Close"] > cisd_lvl):
                    cisd_bar = j - i
                    break

            # entry: the sweep candle's close (the sweep is the signal)
            entry_t = t + step
            trades.append(score_trade(d, direction, win, t, t, entry_t, bar, bar,
                                      pool_name, pool_lvl, cisd_lvl, rth, nq_rth, es, spx_day, step))
            trades[-1]["cisd_within_bars"] = cisd_bar
            trades[-1]["nth_of_day"] = len(trades)
            trades[-1]["bias"] = bias
            used.add(win)
    return trades


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
    stop = sbar["High"] if direction == "puts" else sbar["Low"]
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
    df = df.assign(cisd_followed=df["cisd_within_bars"].notna())
    for col in ("cisd_followed", "failed_2", "smt", "h1", "h4"):
        for val, g in df.groupby(col, dropna=False):
            lines.append(f"| {col} = {val} | {len(g)} | {pct(g['itm_15'])} |")
    lines += ["", "**Answer key check**", ""]
    for _, r in key.iterrows():
        m = df[(df["date"] == r["date"]) & (df["direction"] == r["direction"])]
        found = ", ".join(f"{x.window} entry {x.entry_time} after sweeping {x.pool_swept}, moved {x.max_move_pts} pts" for x in m.itertuples()) or "not flagged"
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
