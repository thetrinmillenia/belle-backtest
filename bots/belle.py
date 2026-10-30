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
    return trend, since, (sh if trend == "bearish" else sl)


def mss_line(tf, m, now):
    trend, since, flip = m
    when = f"{since:%a %H:%M} ET ({since.astimezone(CT):%H:%M} CT)" if (now - since).days < 6 else since.strftime("%b %d")
    turn = f"Turns bullish above {flip:,.2f}" if trend == "bearish" else f"Turns bearish below {flip:,.2f}"
    return f"{tf}: {trend} since {when}. {turn}" if flip is not None else f"{tf}: {trend} since {when}"


def mss_note(m4, m1):
    """Belle's read: do the 4H and 1H shifts agree?"""
    if not m4 or not m1:
        return ""
    if m4[0] == m1[0]:
        return f" 4H and 1H agree: {m4[0]}."
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
    parts.append(f"**Day ATR for a {now.strftime('%A')}:** about {ATR.get(now.weekday(), 80)} SPX pts (1 year average).")
    parts.append("**Belle's read:** " + belle_summary(reads, high_today) + mss_note(*shifts.get("ES", (None, None))))
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


JOBS = {"morning": morning, "release": release, "afternoon": afternoon, "eod": eod}
# allowed ET minutes after midnight for each job. Cron fires twice (summer and winter time);
# only the run inside its window posts, so there are never duplicates.
ALLOWED = {"morning": (300, 565), "release": (510, 560), "afternoon": (800, 860), "eod": (960, 1015)}

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
