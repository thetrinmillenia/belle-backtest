"""Belle bots for Titi. One script, four jobs, one Discord channel.

  morning    6:00 AM ET  ES/NQ higher timeframe bias, True DOL, overnight levels, 4H read, news, Belle's read
  release    8:36 AM ET  8:30 news follow up: forecast vs previous (and actual when FRED key is set) + ES/NQ reaction
  afternoon  1:25 PM ET  setup before Window 1: bias, levels, pools, EMAs, news still ahead
  eod        4:05 PM ET  recap: ranges, windows, power hour stats; saves the day's 1m bars to the repo

Secrets (GitHub repo, Settings, Secrets and variables, Actions):
  DISCORD_WEBHOOK_URL  required (your private channel)
  FRED_API_KEY         optional (free at fred.stlouisfed.org) adds the actual number to release posts

Belle style: no contractions, no dashes. Eastern time with Central in parentheses.
Information only, not financial advice.
"""
import io, os, sys, datetime as dt
from zoneinfo import ZoneInfo
import requests
import pandas as pd
import numpy as np

ET, CT = ZoneInfo("America/New_York"), ZoneInfo("America/Chicago")
WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
FRED_KEY = os.environ.get("FRED_API_KEY", "")
CAL_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
SYMS = {"ES": "ES=F", "NQ": "NQ=F"}
ARCHIVE = os.environ.get("ARCHIVE_DIR", "data/archive")
# one year of SPX history (SPY x10), from the Belle backtest: day ATR by weekday
ATR = {0: 78, 1: 76, 2: 75, 3: 85, 4: 84}
WINDOWS = ("Window 1: watch from 1:30 PM ET (12:30 PM CT), entries 1:30 to 2:40 PM ET (12:30 to 1:40 PM CT). "
           "Window 2: 3:30 to 3:55 PM ET (2:30 to 2:55 PM CT). Out by 3:59 PM ET (2:59 PM CT).")
FOOT = "_Information only, not financial advice._"


# ---------------- helpers ----------------
def f12(t):
    return t.strftime("%I:%M %p").lstrip("0")


def both(t):
    return f"{f12(t.astimezone(ET))} ET ({f12(t.astimezone(CT))} CT)"


def bars(sym, interval="5m", period="5d"):
    import yfinance as yf
    df = yf.download(sym, period=period, interval=interval, prepost=True, progress=False, auto_adjust=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)[["open", "high", "low", "close"]].dropna()
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(ET)
    return df


def rth(df, day):
    return df[(df.index.date == day) & (df.index.time >= dt.time(9, 30)) & (df.index.time < dt.time(16, 0))]


def between(df, day, a, b):
    return df[(df.index.date == day) & (df.index.time >= a) & (df.index.time < b)]


def prev_rth(df, day):
    days = sorted({d for d in df.index.date if d < day and len(rth(df, d)) > 0})
    return rth(df, days[-1]) if days else None


def daily(sym, period="6mo"):
    import yfinance as yf
    df = yf.download(sym, period=period, interval="1d", progress=False, auto_adjust=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)[["open", "high", "low", "close"]].dropna()
    df.index = pd.to_datetime(df.index).date
    return df


def expected_move(now):
    """Nov 4 (Titi): the day's priced SPX move from VIX1D (VIX if VIX1D is missing). Information only."""
    spx = daily("^GSPC")
    spx = spx[spx.index < now.date()]
    close = spx.close.iloc[-1]
    vol, name = None, "VIX1D"
    for sym, nm in (("^VIX1D", "VIX1D"), ("^VIX", "VIX")):
        try:
            v = bars(sym, "5m", "1d").close
            vol, name = float(v.iloc[-1]), nm
            break
        except Exception as e:
            print("vol failed", sym, e)
    if not vol:
        return "**EXPECTED MOVE**\n\nVIX not available right now."
    vix = daily("^VIX")
    vix_now = None
    try:
        vix_now = float(bars("^VIX", "5m", "1d").close.iloc[-1])
    except Exception as e:
        print("vix failed", e)
    pct = vol / 15.87
    em = close * pct / 100
    s = ["**EXPECTED MOVE**"]
    s.append(f"{name} {vol:.2f}" + (f"  |  VIX {vix_now:.2f}" if vix_now and name != "VIX" else ""))
    s.append(f"SPX priced move:  {em:,.1f} points  ({pct:.2f}%)")
    s.append(f"Range:  {close - em:,.0f}  to  {close + em:,.0f}")
    s.append(f"Half shelves:  {close - em / 2:,.0f}  and  {close + em / 2:,.0f}")
    if now.time() >= dt.time(9, 35):   # after the open: what SPX has used so far today
        try:
            r = rth(bars("^GSPC", "5m", "1d"), now.date())
            rng = r.high.max() - r.low.min()
            s.append(f"SPX now:  {r.close.iloc[-1]:,.0f}  ({r.close.iloc[-1] - close:+,.1f} points from the close)")
            s.append(f"Range so far:  {rng:,.1f} points  ({rng / em * 100:.0f}% of the move)  |  left:  {max(em - rng, 0):,.1f} points")
        except Exception as e:
            print("used so far failed", e)
    else:
        try:   # overnight ES change since the 16:00 ET close, in points
            es = bars("ES=F", "5m", "5d")
            prior = es[es.index <= dt.datetime.combine(spx.index[-1], dt.time(16, 0), tzinfo=ET)].close.iloc[-1]
            used = es.close.iloc[-1] - prior
            s.append(f"Overnight used:  {used:+,.1f} points  ({abs(used) / em * 100:.0f}% of the move)")
        except Exception as e:
            print("overnight failed", e)
    try:   # last 60 sessions: closes inside the range the VIX priced the day before
        d = pd.concat([spx.close.rename("c"), vix.close.rename("v")], axis=1).dropna()
        d["band"] = d.c.shift(1) * d.v.shift(1) / 15.87 / 100
        d["move"] = (d.c - d.c.shift(1)).abs()
        d = d.dropna().tail(60)
        s.append(f"Last {len(d)} days:  {(d.move <= d.band).mean() * 100:.0f}% closed inside the range")
    except Exception as e:
        print("base rate failed", e)
    if name == "VIX1D" and vol < 14 and now.time() < dt.time(9, 35):   # Nov 6 (Titi): low VIX day flag (Nov 5: VIX1D 12.08, SPX fell 335 pts)
        s += ["**LOW VIX DAY**",
              f"VIX1D {vol:.2f}" + (f"  |  VIX {vix_now:.2f}" if vix_now else ""),
              f"Options are priced for a small move ({em:,.0f} pts). Contracts are cheap.",
              "If the 4H profile confirms a reversal, cheap out of the money contracts can run 1,000%+",
              "Watch the 06:00 and 10:00 ET 4H candles for the sweep and close back"]
    return "\n\n".join(s)


def color(o, c):
    return "green" if c > o else "red"


def candle(x):
    return None if len(x) == 0 else (x.open.iloc[0], x.high.max(), x.low.min(), x.close.iloc[-1])


def four_hour(df):
    """Futures 4H candles anchored to the 6 PM ET open: 6PM, 10PM, 2AM, 6AM, 10AM, 2PM."""
    x = df.copy()
    x["b"] = (x.index - pd.Timedelta(hours=18)).floor("4h") + pd.Timedelta(hours=18)
    return x.groupby("b").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"))


def four_h_read(df, now, n=3):
    g = four_hour(df)
    closed = g[g.index + pd.Timedelta(hours=4) <= now].tail(n + 1)
    out, prev = [], None
    for t, r in closed.iterrows():
        if prev is not None:
            note = ""
            if r.high > prev.high and r.close < prev.high:
                note = ", swept the prior 4H high and closed back under (bearish reversal read)"
            elif r.low < prev.low and r.close > prev.low:
                note = ", swept the prior 4H low and closed back over (bullish reversal read)"
            elif r.close > prev.high:
                note = ", closed above the prior 4H high (bullish continuation)"
            elif r.close < prev.low:
                note = ", closed below the prior 4H low (bearish continuation)"
            out.append(f"{t.strftime('%I %p').lstrip('0')} ET: {color(r.open, r.close)}{note}")
        prev = r
    return " | ".join(out)


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def equal_levels(x, tol=1.0):
    """Equal highs and lows from 5m swing points (2 bars each side)."""
    hs, ls = [], []
    h, l = x.high.values, x.low.values
    for i in range(2, len(x) - 2):
        if h[i] >= max(h[i - 2:i + 3]): hs.append(h[i])
        if l[i] <= min(l[i - 2:i + 3]): ls.append(l[i])
    eqh = [round(max(a, b), 2) for i, a in enumerate(hs) for b in hs[i + 1:] if abs(a - b) <= tol]
    eql = [round(min(a, b), 2) for i, a in enumerate(ls) for b in ls[i + 1:] if abs(a - b) <= tol]
    return sorted(set(eqh))[-2:], sorted(set(eql))[:2]


def events(now, upto=None):
    try:
        ev = requests.get(CAL_URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"}).json()
    except Exception:
        return None
    out = []
    for e in ev:
        if e.get("country") != "USD" or e.get("impact") not in ("High", "Medium"):
            continue
        t = pd.Timestamp(e["date"]).tz_convert(ET)
        e["t"] = t
        out.append(e)
    return out


def ev_line(e):
    s = f"{both(e['t'])} [{'HIGH' if e['impact'] == 'High' else 'med'}] {e['title']}"
    if e.get("forecast") or e.get("previous"):
        s += f" (forecast {e.get('forecast') or 'n/a'}, previous {e.get('previous') or 'n/a'})"
    return s


FRED_MAP = [  # title keyword -> (series, how to show)
    ("Core CPI m/m", "CPILFESL", "pct_mom"), ("CPI m/m", "CPIAUCSL", "pct_mom"),
    ("Core PPI m/m", "PPIFES", "pct_mom"), ("PPI m/m", "PPIFIS", "pct_mom"),
    ("Non-Farm Employment Change", "PAYEMS", "diff_k"), ("Unemployment Rate", "UNRATE", "level"),
    ("Unemployment Claims", "ICSA", "level_k"), ("Core Retail Sales m/m", "RSFSXMV", "pct_mom"),
    ("Retail Sales m/m", "RSAFS", "pct_mom"), ("Core PCE Price Index m/m", "PCEPILFE", "pct_mom"),
]


def fred_actual(title):
    if not FRED_KEY:
        return None
    for key, sid, how in FRED_MAP:
        if key.lower() in title.lower():
            try:
                r = requests.get("https://api.stlouisfed.org/fred/series/observations", timeout=20, params={
                    "series_id": sid, "api_key": FRED_KEY, "file_type": "json", "sort_order": "desc", "limit": 3}).json()
                v = [float(o["value"]) for o in r["observations"] if o["value"] != "."]
                date = r["observations"][0]["date"]
                if how == "pct_mom": return f"{100 * (v[0] / v[1] - 1):.1f}% (FRED, period {date})"
                if how == "diff_k": return f"{v[0] - v[1]:+.0f}K (FRED, period {date})"
                if how == "level_k": return f"{v[0] / 1000:.0f}K (FRED, week of {date})"
                return f"{v[0]} (FRED, period {date})"
            except Exception:
                return None
    return None


def post(text):
    if not WEBHOOK:
        print(text); return
    chunks, cur = [], ""
    for block in text.split("\n\n"):
        if len(cur) + len(block) + 2 > 1900:
            chunks.append(cur); cur = ""
        cur += block + "\n\n"
    chunks.append(cur)
    for c in chunks:
        if c.strip():
            requests.post(WEBHOOK, json={"content": c.strip()}, timeout=20).raise_for_status()


# ---------------- jobs ----------------
def htf_bias(df, now):
    """Bias from the higher timeframes: daily, 4H and 1H (last closed candles). 4H and 1H agree: that side. Split: the daily decides."""
    g = four_hour(df)
    c4 = g[g.index + pd.Timedelta(hours=4) <= now].iloc[-1]
    h1 = df[df.index + pd.Timedelta(hours=1) <= now].iloc[-1]
    p = prev_rth(df, now.date())
    d_col = color(p.open.iloc[0], p.close.iloc[-1])
    col4, col1 = color(c4.open, c4.close), color(h1.open, h1.close)
    if col4 == col1:
        side, why = col4, f"4H and 1H both {col4}, daily {d_col}"
    else:
        side, why = d_col, f"4H {col4} and 1H {col1} split, daily {d_col} decides"
    return ("BULLISH" if side == "green" else "BEARISH"), why

def mss(g):
    """Latest market structure shift (Titi, Oct 30): a candle closes through the last swing (2 candles each side)
    against the trend. Returns (trend, since, flip level) or None. The flip level is the swing that would turn it."""
    hs, ls, cl = g.high.values, g.low.values, g.close.values
    sh = sl = trend = since = None
    for j in range(len(g)):
        i = j - 2
        if i >= 2:
            if hs[i] > max(hs[i - 2], hs[i - 1], hs[i + 1], hs[i + 2]):
                sh = hs[i]
            if ls[i] < min(ls[i - 2], ls[i - 1], ls[i + 1], ls[i + 2]):
                sl = ls[i]
        if sl is not None and cl[j] < sl and trend != "bearish":
            trend, since = "bearish", g.index[j]
        elif sh is not None and cl[j] > sh and trend != "bullish":
            trend, since = "bullish", g.index[j]
    if trend is None:
        return None
    # flip = the swing that would turn it; cont = the swing that, broken, continues the trend (Nov 2)
    return trend, since, (sh if trend == "bearish" else sl), (sl if trend == "bearish" else sh)


def mss_line(tf, m, now, daily=False):
    trend, since, flip, cont = m
    if daily or (now - since).days >= 6:
        when = since.strftime("%b %d")
    else:
        when = f"{since:%a %H:%M} ET ({since.astimezone(CT):%H:%M} CT)"
    out = [f"{tf}: {trend} since {when}"]
    if flip is not None:
        out.append(f"Turns bullish above {flip:,.2f}" if trend == "bearish" else f"Turns bearish below {flip:,.2f}")
    if cont is not None:
        out.append(f"Bearish continues below {cont:,.2f}" if trend == "bearish" else f"Bullish continues above {cont:,.2f}")
    return "\n".join(out)


def mss_note(m4, m1, bias=None):
    """Belle's read: do the 4H and 1H shifts agree? Said only when it matches the candle bias (no mixed message)."""
    if not m4 or not m1:
        return ""
    if m4[0] == m1[0]:
        return f" 4H and 1H agree: {m4[0]}." if not bias or bias.lower() == m4[0] else ""
    lvl = f" Watch {m4[2]:,.2f}." if m4[2] is not None else ""
    return (" 1H bounce inside a bearish 4H." if m4[0] == "bearish" else " 1H pullback inside a bullish 4H.") + lvl


def morning(now):
    parts = [f"**BELLE MORNING READ** {now.strftime('%A %b %d')} | {both(now)}"]
    reads, shifts = {}, {}
    for name, sym in SYMS.items():
        try:
            df = bars(sym, "1h", "7d")
            p = prev_rth(df, now.date())
            start = dt.datetime.combine(now.date() - dt.timedelta(days=1), dt.time(18, 0), tzinfo=ET)
            on = df[(df.index >= start) & (df.index <= now)]
            last = df.close.iloc[-1]
            pdh, pdl = p.high.max(), p.low.min()
            mid = df[(df.index.date == now.date()) & (df.index.time == dt.time(0, 0))]
            bias, why = htf_bias(df, now)
            s = [f"**{name}** {last:,.2f} | Bias: **{bias}** ({why})"]
            dol_side = None
            if len(mid):
                dol = mid.open.iloc[0]
                dol_side = "above" if last > dol else "below"
                s.append(f"True DOL (midnight open) {dol:,.2f}, price is {dol_side} it ({'premium' if dol_side == 'above' else 'discount'})")
            if len(on):
                s.append(f"Overnight high {on.high.max():,.2f} at {both(on.high.idxmax())} | low {on.low.min():,.2f} at {both(on.low.idxmin())} | range {on.high.max() - on.low.min():,.2f} pts")
                took = [w for w, c in (("took the PDH (buy side)", on.high.max() > pdh), ("took the PDL (sell side)", on.low.min() < pdl)) if c]
                s.append("Overnight " + (" and ".join(took) if took else "stayed inside the prior day range"))
            s.append(f"PDH {pdh:,.2f} | PDL {pdl:,.2f} | prior close {p.close.iloc[-1]:,.2f}")
            s.append("4H read: " + four_h_read(df, now))
            try:   # 4H and 1H market structure shift, a month of 1h candles (closed candles only)
                dm = bars(sym, "1h", "1mo")
                g4 = four_hour(dm)
                m4 = mss(g4[g4.index + pd.Timedelta(hours=4) <= now])
                m1 = mss(dm[dm.index + pd.Timedelta(hours=1) <= now])
                s += [mss_line(tf, m, now) for tf, m in (("4H", m4), ("1H", m1)) if m]
                shifts[name] = (m4, m1)
            except Exception as e:
                print("mss failed", name, e)
            reads[name] = (bias, dol_side)
            parts.append("\n".join(s))
        except Exception as e:
            parts.append(f"**{name}**: data not available ({type(e).__name__})")
    ev = events(now)
    high_today = []
    if ev is None:
        parts.append("Economic calendar not available right now.")
    else:
        today = [ev_line(e) for e in ev if e["t"].date() == now.date()]
        high_today = [e for e in ev if e["t"].date() == now.date() and e["impact"] == "High"]
        ahead = [f"{e['t'].strftime('%a')} " + ev_line(e) for e in ev if e["t"].date() > now.date() and e["impact"] == "High"]
        parts.append("**Today (USD news):**\n" + ("\n".join(today) if today else "No medium or high impact USD news today."))
        if ahead:
            parts.append("**Still ahead this week (high impact):**\n" + "\n".join(ahead))
    try:
        parts.append(expected_move(now))
    except Exception as e:
        print("expected move failed", e)
    parts.append(f"**Day ATR for a {now.strftime('%A')}:** about {ATR.get(now.weekday(), 80)} SPX pts (1 year average).")
    parts.append("**Belle's read:** " + belle_summary(reads, high_today) + mss_note(*shifts.get("ES", (None, None)), (reads.get("ES") or (None,))[0]))
    parts.append(earnings_today(now))
    parts.append(FOOT)
    return "\n\n".join(parts)


def index_members():
    """S&P 500 and Nasdaq-100 tickers from Wikipedia (free, no key). Empty set if it cannot be read."""
    out = set()
    for url, col in (("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", "Symbol"),
                     ("https://en.wikipedia.org/wiki/Nasdaq-100", "Ticker")):
        try:
            html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20).text
            for t in pd.read_html(io.StringIO(html)):
                if col in t.columns:
                    out |= {str(x).replace(".", "-").strip().upper() for x in t[col]}
                    break
        except Exception as e:
            print("index list failed", url, e)
    return out


def earnings_today(now):
    """EARNINGS TODAY (Oct 29): only S&P 500 and Nasdaq-100 companies, biggest first, from Nasdaq's free calendar."""
    head = "**EARNINGS TODAY**"
    try:
        rows = requests.get("https://api.nasdaq.com/api/calendar/earnings", params={"date": now.strftime("%Y-%m-%d")},
                            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}, timeout=20).json()["data"]["rows"] or []
    except Exception as e:
        print("earnings calendar failed", e)
        return head + "\n\nEarnings calendar not available right now."
    members = index_members()

    def cap(r):
        try:
            return float(str(r.get("marketCap", "")).replace("$", "").replace(",", ""))
        except ValueError:
            return 0.0
    rows = [r for r in rows if (r.get("symbol") or "").upper().replace(".", "-") in members] if members else \
        [r for r in rows if cap(r) >= 20e9]   # fallback when the index lists cannot be read: $20B and up
    rows.sort(key=cap, reverse=True)
    pre = [r["symbol"] for r in rows if r.get("time") == "time-pre-market"][:6]
    post_ = [r["symbol"] for r in rows if r.get("time") == "time-after-hours"][:6]
    if not pre and not post_:
        return head + "\n\nNo major S&P 500 or Nasdaq-100 reports"
    lines = [head]
    if pre:
        lines.append("Before the open\n" + ", ".join(pre))
    if post_:
        lines.append("After the close (16:00 ET, 15:00 CT)\n" + ", ".join(post_))
    big = next(r for r in rows if r["symbol"] in pre + post_)
    lines.append(f"Biggest mover risk: {big['symbol']} {'before the open' if big['symbol'] in pre else 'after the close'}")
    return "\n\n".join(lines)

def belle_summary(reads, high_today):
    if not reads:
        return "No data this morning, read the chart at the open."
    biases = {b for b, _ in reads.values()}
    if len(biases) > 1:
        s = "ES and NQ disagree on the higher timeframes (SMT). No clean bias yet, let the 9:30 open and the afternoon read decide."
    else:
        b = biases.pop()
        want = "puts" if b == "BEARISH" else "calls"
        good = "above" if b == "BEARISH" else "below"
        sides = {d for _, d in reads.values() if d}
        s = f"ES and NQ both {b.lower()} on the higher timeframes, so look for {want}."
        if sides == {good}:
            s += f" Price is {good} True DOL ({'premium' if good == 'above' else 'discount'}), which lines up with the bias."
        elif sides:
            s += f" Price is {'/'.join(sorted(sides))} True DOL, so wait for price to get {'above' if b == 'BEARISH' else 'below'} it before looking for {want}."
    if high_today:
        s += " High impact news today: " + ", ".join(f"{e['title']} at {both(e['t'])}" for e in high_today) + ". Be careful around that time."
    return s

def release(now):
    ev = events(now) or []
    hit = [e for e in ev if e["t"].date() == now.date() and dt.time(7, 0) <= e["t"].time() <= now.time()]
    if not hit:
        return None  # nothing released this morning, stay quiet
    parts = [f"**BELLE NEWS FOLLOW UP** {now.strftime('%A %b %d')} | {both(now)}"]
    lines = []
    for e in hit:
        a = fred_actual(e["title"])
        lines.append(ev_line(e) + (f"\nActual: {a}" if a else "\nActual: check the release (FRED key not set or not posted yet)"))
    parts.append("\n".join(lines))
    t0 = min(e["t"] for e in hit)
    for name, sym in SYMS.items():
        try:
            df = bars(sym, "1m", "1d")
            pre = df[df.index < t0]
            post_ = df[df.index >= t0]
            if len(pre) and len(post_):
                p0 = pre.close.iloc[-1]
                parts.append(f"**{name} reaction since {both(t0)}:** {post_.close.iloc[-1] - p0:+.2f} pts | "
                             f"high {post_.high.max() - p0:+.2f} | low {post_.low.min() - p0:+.2f}")
        except Exception as e:
            parts.append(f"**{name}**: reaction data not available ({type(e).__name__})")
    parts.append(FOOT)
    return "\n\n".join(parts)


def afternoon(now):
    parts = [f"**BELLE AFTERNOON SETUP** {now.strftime('%A %b %d')} | {both(now)}"]
    for name, sym in SYMS.items():
        try:
            df = bars(sym, "5m", "5d")
            d = now.date()
            r = rth(df, d); r = r[r.index <= now]
            p = prev_rth(df, d)
            last = df.close.iloc[-1]
            h1 = between(df, d, (now - dt.timedelta(hours=1)).replace(minute=0).time(), now.replace(minute=0).time())
            g = four_hour(df)
            cur4 = g[g.index <= now].iloc[-1]
            c1 = color(h1.open.iloc[0], h1.close.iloc[-1]) if len(h1) else "n/a"
            c4 = color(cur4.open, last)
            e13, e50, e200 = ema(df.close, 13).iloc[-1], ema(df.close, 50).iloc[-1], ema(df.close, 200).iloc[-1]
            if c1 == c4:
                bias = "BULLISH" if c1 == "green" else "BEARISH"; why = f"1H and 4H both {c1}"
            else:
                bias = "BULLISH" if e13 > e50 else "BEARISH"; why = f"1H {c1} and 4H {c4} split, 13 EMA {'over' if e13 > e50 else 'under'} 50 EMA decides"
            mid = df[(df.index.date == d) & (df.index.time == dt.time(0, 0))]
            eqh, eql = equal_levels(r)
            s = [f"**{name}** {last:,.2f} | Bias: **{bias}** ({why})",
                 f"Day high {r.high.max():,.2f} | day low {r.low.min():,.2f} | range so far {r.high.max() - r.low.min():,.2f} pts",
                 f"9:30 open {r.open.iloc[0]:,.2f} | midnight open {mid.open.iloc[0]:,.2f}" if len(mid) else f"9:30 open {r.open.iloc[0]:,.2f}",
                 f"PDH {p.high.max():,.2f} | PDL {p.low.min():,.2f}",
                 f"EMAs (5m): 13 {e13:,.2f} | 50 {e50:,.2f} | 200 {e200:,.2f}"]
            if eqh: s.append("Equal highs: " + ", ".join(f"{v:,.2f}" for v in eqh))
            if eql: s.append("Equal lows: " + ", ".join(f"{v:,.2f}" for v in eql))
            parts.append("\n".join(s))
        except Exception as e:
            parts.append(f"**{name}**: data not available ({type(e).__name__})")
    ev = events(now) or []
    later = [ev_line(e) for e in ev if e["t"].date() == now.date() and e["t"].time() > now.time()]
    if later:
        parts.append("**News still ahead today:**\n" + "\n".join(later))
    try:   # Nov 4 (Titi): live VIX1D expected move after the open
        parts.append(expected_move(now))
    except Exception as e:
        print("expected move failed", e)
    parts.append(f"**Range left today:** a {now.strftime('%A')} averages about {ATR.get(now.weekday(), 80)} SPX pts. "
                 "Mark the 2 PM to 3 PM range at 3 PM: power hour breaks it 88% of days.")
    parts.append("**Targets:** W1 about 12 pts doubles a 10 to 40 OTM contract (typically 25 to 30 min). "
                 "W2 about 8 pts doubles a 10 to 30 OTM contract (about 5 min).")
    parts.append(FOOT)
    return "\n\n".join(parts)


def eod(now):
    parts = [f"**BELLE END OF DAY RECAP** {now.strftime('%A %b %d')}"]
    d = now.date()
    for name, sym in SYMS.items():
        try:
            df = bars(sym, "1m", "1d")
            r = rth(df, d)
            if len(r) == 0:
                parts.append(f"**{name}**: no session today"); continue
            os.makedirs(ARCHIVE, exist_ok=True)
            df[df.index.date == d].to_csv(f"{ARCHIVE}/{name}_{d}_1m.csv")
            o, h, l, c = candle(r)
            w1, w2 = between(df, d, dt.time(13, 30), dt.time(14, 40)), between(df, d, dt.time(15, 30), dt.time(15, 56))
            r23, ph, pre = between(df, d, dt.time(14, 0), dt.time(15, 0)), between(df, d, dt.time(15, 0), dt.time(16, 0)), between(df, d, dt.time(9, 30), dt.time(15, 0))
            brk = [s for s, cnd in (("high", ph.high.max() > r23.high.max()), ("low", ph.low.min() < r23.low.min())) if cnd]
            def win(x, lab):
                if len(x) == 0: return f"{lab}: no data"
                return f"{lab}: {color(x.open.iloc[0], x.close.iloc[-1])}, up {x.high.max() - x.open.iloc[0]:.1f} pts | down {x.open.iloc[0] - x.low.min():.1f} pts"
            s = [f"**{name}** {color(o, c)} day | open {o:,.2f} | close {c:,.2f} | range {h - l:.1f} pts (a {now.strftime('%A')} averages about {ATR.get(now.weekday(), 80)} SPX pts)",
                 win(w1, "Window 1 (1:30 to 2:40 PM ET)"), win(w2, "Window 2 (3:30 to 3:55 PM ET)"),
                 f"Power hour broke the 2 to 3 PM range: {' and '.join(brk) if brk else 'no'}"
                 + (" | new day high in power hour" if ph.high.max() > pre.high.max() else "")
                 + (" | new day low in power hour" if ph.low.min() < pre.low.min() else "")]
            parts.append("\n".join(s))
            row = pd.DataFrame([dict(date=d, sym=name, open=o, high=h, low=l, close=c,
                                     w1_up=w1.high.max() - w1.open.iloc[0] if len(w1) else np.nan,
                                     w1_down=w1.open.iloc[0] - w1.low.min() if len(w1) else np.nan,
                                     w2_up=w2.high.max() - w2.open.iloc[0] if len(w2) else np.nan,
                                     w2_down=w2.open.iloc[0] - w2.low.min() if len(w2) else np.nan,
                                     ph_break=",".join(brk))])
            log = f"{ARCHIVE}/../daily_log.csv"
            row.to_csv(log, mode="a", header=not os.path.exists(log), index=False)
        except Exception as e:
            parts.append(f"**{name}**: data not available ({type(e).__name__})")
    # free SPX 1m archive from Yahoo (^GSPC), next to the ES and NQ files (Titi, Oct 14)
    try:
        g = bars("^GSPC", "1m", "1d")
        g = g[g.index.date == d]
        if len(g):
            os.makedirs(ARCHIVE, exist_ok=True)
            g.to_csv(f"{ARCHIVE}/SPX_{d}_1m.csv")
    except Exception as e:
        parts.append(f"SPX archive not saved ({type(e).__name__})")
    parts.append(FOOT)
    return "\n\n".join(parts)


# ---------------- open read (Titi, Nov 2): 09:30 ET (08:30 CT), cash indices and ETFs, Daily and 1H ----------------
OPEN_SYMS = (("SPX", "^GSPC"), ("NDX", "^NDX"), ("SPY", "SPY"), ("QQQ", "QQQ"))


def rth_only(df):
    t = df.index.time
    return df[(t >= dt.time(9, 30)) & (t < dt.time(16, 0))]


def daily_read(d):
    """The prior daily candle against the day before it."""
    p, q = d.iloc[-1], d.iloc[-2]
    col = color(p.open, p.close)
    if p.high > q.high and p.low < q.low:
        how = "outside day, took both the PDH and the PDL"
    elif p.low < q.low:
        how = "took the PDL and closed back inside" if p.close > q.low else "closed below the PDL"
    elif p.high > q.high:
        how = "took the PDH and closed back inside" if p.close < q.high else "closed above the PDH"
    else:
        how = "inside day"
    return f"Daily: {col} candle, {how}"


def open_data(sym, now):
    d = bars(sym, "1d", "6mo")
    d = d[d.index.date < now.date()]
    h1 = rth_only(bars(sym, "1h", "1mo"))
    h1 = h1[h1.index + pd.Timedelta(hours=1) <= now]
    m1 = bars(sym, "1m", "1d")
    m1 = m1[(m1.index.date == now.date()) & (m1.index.time >= dt.time(9, 30))]
    if not len(m1) or len(d) < 3:
        return None
    p = d.iloc[-1]
    return {"open": float(m1.open.iloc[0]), "pdh": float(p.high), "pdl": float(p.low), "pdc": float(p.close),
            "mid": (float(p.high) + float(p.low)) / 2, "dread": daily_read(d), "md": mss(d), "m1": mss(h1)}


def gap_line(x, pts="pts"):
    g = x["open"] - x["pdc"]
    return f"Gap: {'up' if g >= 0 else 'down'} {abs(g):,.2f} {pts} from the prior close {x['pdc']:,.2f}"


def likely(x):
    """WHAT IS LIKELY: bias from the Daily and 1H MSS, pivot = prior day 50%, targets = nearest levels, invalidation."""
    d, h = (x["md"] or (None,))[0], (x["m1"] or (None,))[0]
    P = x["mid"]
    lv = [x["pdh"], x["pdl"]] + [v for m in (x["md"], x["m1"]) if m for v in (m[2], m[3]) if v is not None]
    below = sorted([v for v in lv if v < min(P, x["open"]) - 0.5], reverse=True)
    above = sorted([v for v in lv if v > max(P, x["open"]) + 0.5])
    out = []
    if d and d == h:
        out.append(f"Bias: {d} (daily and 1H agree)")
    else:
        out.append(f"Bias: split (daily {d or 'none'}, 1H {h or 'none'}). Wait for the 5m")
    bear = (d == h == "bearish")
    if below:
        out.append(f"Below {P:,.2f}: sell side target {below[0]:,.2f}" + (" (PDL)" if abs(below[0] - x["pdl"]) < 0.01 else ""))
    if above:
        out.append(f"Back above {P:,.2f}: first stop {above[0]:,.2f}" + (" (PDH)" if abs(above[0] - x["pdh"]) < 0.01 else ""))
    if d and d == h:
        if bear and above:
            out.append(f"Above {above[0]:,.2f}: the bearish read is wrong")
        elif not bear and below:
            out.append(f"Below {below[0]:,.2f}: the bullish read is wrong")
    return out


def open_read(now):
    import time as _t
    start = now.replace(hour=9, minute=30, second=30, microsecond=0)
    while dt.datetime.now(ET) < start:   # the run starts early (GitHub can be late), then waits for the first candle
        _t.sleep(5)
    data = {}
    for _ in range(40):   # up to about 10 minutes for the 09:30 candle to show up
        now = dt.datetime.now(ET)
        for name, sym in OPEN_SYMS:
            if name not in data:
                try:
                    x = open_data(sym, now)
                    if x:
                        data[name] = x
                except Exception as e:
                    print("open data", name, type(e).__name__, e)
        if "SPX" in data:
            break
        _t.sleep(15)
    if "SPX" not in data:
        return None
    now = dt.datetime.now(ET)
    parts = ["**BELLE OPEN READ**  09:30 ET (08:30 CT)"]
    x = data["SPX"]
    where = ("Opened above the PDH" if x["open"] > x["pdh"] else ("Opened below the PDL" if x["open"] < x["pdl"] else "Opened inside the prior day range"))
    s = [f"SPX opened {x['open']:,.2f}", gap_line(x), f"{where} ({x['pdl']:,.2f} to {x['pdh']:,.2f})",
         f"{'Above' if x['open'] > x['mid'] else 'Below'} the prior day 50% {x['mid']:,.2f} ({'premium' if x['open'] > x['mid'] else 'discount'})"]
    parts.append("\n".join(s))
    s = [x["dread"]]
    if x["md"]:
        s.append(mss_line("Daily", x["md"], now, daily=True))
    parts.append("\n".join(s))
    if x["m1"]:
        parts.append(mss_line("1H", x["m1"], now))
    if "NDX" in data:
        n = data["NDX"]
        nd, nh = (n["md"] or ("none",))[0], (n["m1"] or ("none",))[0]
        sd, sh_ = (x["md"] or ("none",))[0], (x["m1"] or ("none",))[0]
        agree = "agrees with SPX" if (nd, nh) == (sd, sh_) else "does not agree with SPX, SMT"
        g = n["open"] - n["pdc"]
        parts.append(f"NDX opened {n['open']:,.2f} | gap {'up' if g >= 0 else 'down'} {abs(g):,.2f} pts\nDaily {nd} | 1H {nh} ({agree})")
    if "SPY" in data:
        y = data["SPY"]
        s = [f"SPY opened {y['open']:,.2f} | gap {'up' if y['open'] >= y['pdc'] else 'down'} {abs(y['open'] - y['pdc']):,.2f}",
             f"PDH {y['pdh']:,.2f} | PDL {y['pdl']:,.2f} | 50% {y['mid']:,.2f}"]
        if y["m1"]:
            tr, _, fl, co = y["m1"]
            if fl is not None:
                s.append(f"1H turns {'bullish above' if tr == 'bearish' else 'bearish below'} {fl:,.2f}")
            if co is not None:
                s.append(f"1H {tr} continues {'below' if tr == 'bearish' else 'above'} {co:,.2f}")
        parts.append("\n".join(s))
    if "QQQ" in data:
        q = data["QQQ"]
        qd = "up" if q["open"] >= q["pdc"] else "down"
        if "SPY" in data:
            yd = "up" if data["SPY"]["open"] >= data["SPY"]["pdc"] else "down"
            rel = f"with SPY: both opened {qd}" if qd == yd else f"against SPY: QQQ {qd}, SPY {yd}"
            parts.append(f"QQQ {q['open']:,.2f} ({rel})")
        else:
            parts.append(f"QQQ {q['open']:,.2f} (opened {qd})")
    parts.append("**WHAT IS LIKELY**\n" + "\n".join(likely(x)))
    ev = events(now)
    if ev:
        nxt = [e for e in ev if e["t"].date() == now.date() and e["t"] > now]
        if nxt:
            parts.append("Next news: " + ev_line(nxt[0]))
    parts.append(FOOT)
    return "\n\n".join(parts)


JOBS = {"morning": morning, "release": release, "afternoon": afternoon, "eod": eod, "open": open_read}
# allowed ET minutes after midnight for each job. Cron fires twice (summer and winter time);
# only the run inside its window posts, so there are never duplicates.
ALLOWED = {"morning": (300, 565), "release": (510, 560), "afternoon": (800, 860), "eod": (960, 1015), "open": (545, 575)}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in JOBS:
        sys.exit(f"Unknown mode {mode}")
    now = dt.datetime.now(ET)
    test = os.environ.get("FORCE_POST", "") == "test"   # test run: print to the GitHub log only, nothing to Discord
    force = os.environ.get("FORCE_POST", "") == "1" or test
    m = now.hour * 60 + now.minute
    a, b = ALLOWED[mode]
    if not force and (now.weekday() > 4 or not a <= m < b):
        print(f"{mode}: not its time ({now:%a %H:%M} ET); skipping."); sys.exit(0)
    text = JOBS[mode](now)
    if text and test:
        print(text)
    elif text:
        post(text)
    else:
        print("Nothing to post.")
