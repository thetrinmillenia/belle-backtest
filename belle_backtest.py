"""
Belle backtest: Titi's EOD liquidity sweep method on SPX 0DTE.

What it does, in order, for every day in the data:
 1. Marks ES liquidity pools: PDH, PDL, midnight open, 9:30 open,
    overnight high and low, the 13:30 to 14:00 candle high and low,
    and today's swing highs and lows.
 2. Inside Window 1 (14:00 to 14:50 ET) and Window 2 (15:30 to 15:55 ET)
    it looks for a sweep: a candle trades through a live pool and closes
    back inside it.
 3. It then needs a CISD: a body close through the open of the first
    candle in the run that led into the sweep (wicks ignored).
 4. Entry is that CISD candle's close. Stop is the sweep candle's extreme.
 5. Option proxy: a strike OTM_POINTS out of the money (rounded to 5).
    Did SPX go in the money by the close, and how far past the strike?

Score fields (they never block a trade): failed 2 (Strat shooter or hammer),
ES versus NQ SMT, and 1H and 4H candle colour at entry.

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


def strike_for(spx_price, direction):
    if direction == "puts":
        return math.floor((spx_price - C.OTM_POINTS) / C.STRIKE_STEP) * C.STRIKE_STEP
    return math.ceil((spx_price + C.OTM_POINTS) / C.STRIKE_STEP) * C.STRIKE_STEP


def window_of(t_close):
    for name, ((h1, m1), (h2, m2)) in C.WINDOWS.items():
        if time(h1, m1) < t_close.time() <= time(h2, m2):
            return name
    return None


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

    trades, used_windows = [], set()
    bars = list(rth.index)
    for i, t in enumerate(bars):
        if t < at(d, 13, 45) or len(trades) >= C.MAX_TRADES_PER_DAY:
            continue
        bar = rth.loc[t]
        before = rth[rth.index < t]
        if before.empty:
            continue

        for direction in ("puts", "calls"):
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
            if not hit:
                continue
            pool_name, pool_lvl = (max if direction == "puts" else min)(hit, key=lambda x: x[1])

            # CISD level: open of the first candle in the run into the sweep
            k = i if (bar["Close"] > bar["Open"]) == (direction == "puts") else i - 1
            want_up = direction == "puts"
            while k > 0 and (rth.iloc[k]["Close"] > rth.iloc[k]["Open"]) == want_up:
                k -= 1
            cisd_lvl = rth.iloc[min(k + 1, i)]["Open"]

            for j in range(i, min(i + C.CISD_MAX_BARS + 1, len(bars))):
                cb = rth.iloc[j]
                ok = cb["Close"] < cisd_lvl if direction == "puts" else cb["Close"] > cisd_lvl
                if not ok:
                    continue
                entry_t = bars[j] + step
                win = window_of(entry_t)
                if win is None or win in used_windows:
                    break
                trades.append(score_trade(d, direction, win, t, bars[j], entry_t, bar, cb,
                                          pool_name, pool_lvl, cisd_lvl, rth, nq_rth, es, spx_day, step))
                used_windows.add(win)
                break
            if trades and trades[-1]["sweep_time"] == t.strftime("%H:%M"):
                break
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
    strike = strike_for(spx_entry, direction)
    path = spx_day[spx_day.index >= entry_t]
    close = spx_day["Close"].iloc[-1]
    if direction == "puts":
        best = path["Low"].min() if not path.empty else close
        past = strike - best
        itm_close = close < strike
    else:
        best = path["High"].max() if not path.empty else close
        past = best - strike
        itm_close = close > strike
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
        "spx_entry": round(spx_entry, 2), "strike": strike, "spx_close": round(close, 2),
        "points_past_strike": round(past, 2), "reached_itm": bool(past > 0), "itm_at_close": bool(itm_close),
        "stop_hit": stopped, "failed_2": bool(failed2), "smt": smt,
        "h1": colour(h1_open), "h4": colour(h4_open),
    }


# ---------------------------------------------------------------- report
def pct(s):
    return f"{100 * s.mean():.0f}%" if len(s) else "n/a"


def summarize(df, tf, key):
    lines = [f"## {tf} minute signals", ""]
    if df.empty:
        return lines + ["No signals.", ""]
    weeks = max(1, df["date"].nunique() / 5)
    lines += [f"| Measure | Value |", "| --- | --- |",
              f"| Signals | {len(df)} ({len(df) / weeks:.1f} per week) |",
              f"| Reached ITM by 15:59 | {pct(df['reached_itm'])} |",
              f"| ITM at the close | {pct(df['itm_at_close'])} |",
              f"| Average points past strike | {df['points_past_strike'].mean():.1f} |",
              f"| Underlying stop hit | {pct(df['stop_hit'])} |", ""]
    lines += ["| Split | Signals | Reached ITM |", "| --- | --- | --- |"]
    for col in ("window", "direction", "failed_2", "smt", "h1", "h4"):
        for val, g in df.groupby(col, dropna=False):
            lines.append(f"| {col} = {val} | {len(g)} | {pct(g['reached_itm'])} |")
    lines += ["", "**Answer key check**", ""]
    for _, r in key.iterrows():
        m = df[(df["date"] == r["date"]) & (df["direction"] == r["direction"])]
        found = ", ".join(f"{x.window} {x.entry_time} ({x.pool_swept})" for x in m.itertuples()) or "not flagged"
        lines.append(f"- {r['date']} {r['contract']}: {found}")
    return lines + [""]


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
    report = ["# Belle backtest results", "",
              f"Data: Yahoo Finance, last {C.PERIOD}. Strike = {C.OTM_POINTS} SPX points OTM.", ""]
    for tf in C.TIMEFRAMES:
        es, nq, spx = (resample(raw[s], tf) for s in (C.ES, C.NQ, C.SPX))
        days = sorted(set(spx.index.date))
        rows = []
        for prev_d, d in zip(days, days[1:]):
            rows += run_day(d, prev_d, es, nq, spx, tf)
        df = pd.DataFrame(rows)
        df.to_csv(f"results/signals_{tf}m.csv", index=False)
        report += summarize(df, tf, key)
        print(f"{tf}m: {len(df)} signals")
    with open("results/summary.md", "w") as f:
        f.write("\n".join(report))
    print("\n".join(report))


if __name__ == "__main__":
    main()
