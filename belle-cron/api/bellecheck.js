// Belle check (Titi, Nov 11): on Nov 9 and Nov 10 Belle's TradingView alert stopped (calculation error) and nothing told us,
// so Penny missed the EOD trades. Belle always sends the EOD READ at 15:00 ET; the relay marks that day with an empty
// Alpaca watchlist belle-seen-YYYY-MM-DD. At 15:05 ET (14:05 CT) this check posts a Discord warning if the mark is missing.
// Vercel calls it on the schedules in vercel.json with Authorization: Bearer CRON_SECRET. PAPER account only.
const TRADE = 'https://paper-api.alpaca.markets';
const TZ = 'America/New_York';
function et(d = new Date()) {
  const f = new Intl.DateTimeFormat('en-US', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false, weekday: 'short' });
  const p = Object.fromEntries(f.formatToParts(d).map(x => [x.type, x.value]));
  return { y: p.year, m: p.month, d: p.day, h: Number(p.hour) % 24, min: Number(p.minute), wd: p.weekday };
}
const H = () => ({ 'APCA-API-KEY-ID': process.env.ALPACA_KEY_ID.trim(), 'APCA-API-SECRET-KEY': process.env.ALPACA_SECRET_KEY.trim(), 'Content-Type': 'application/json' });

export default async function handler(req, res) {
  if (!process.env.CRON_SECRET || req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ ok: false, error: 'not authorized' });
  }
  const t = et();
  const force = req.query.force === '1';
  // two crons (19:05 and 20:05 UTC) cover summer and winter time; only the one landing at 15:xx ET runs
  if (!force && t.h !== 15) return res.status(200).json({ ok: true, skipped: 'not 15:00 ET' });
  const day = `${t.y}-${t.m}-${t.d}`;
  try {
    // market closed or early close (no 16:00 close) -> no EOD READ is expected, stay quiet
    const cal = await (await fetch(`${TRADE}/v2/calendar?start=${day}&end=${day}`, { headers: H() })).json();
    if (!Array.isArray(cal) || !cal.length || cal[0].date !== day || cal[0].close !== '16:00') {
      return res.status(200).json({ ok: true, skipped: 'no full trading day' });
    }
    const wl = await (await fetch(`${TRADE}/v2/watchlists`, { headers: H() })).json();
    const lists = Array.isArray(wl) ? wl : [];
    const seen = lists.some(w => w.name === `belle-seen-${day}`);
    // tidy: remove marks from earlier days
    for (const w of lists) {
      if (/^belle-seen-\d{4}-\d{2}-\d{2}$/.test(w.name) && w.name !== `belle-seen-${day}`) {
        try { await fetch(`${TRADE}/v2/watchlists/${w.id}`, { method: 'DELETE', headers: H() }); } catch (e) { }
      }
    }
    if (seen) return res.status(200).json({ ok: true, belle: 'alive' });
    const text = "**BELLE CHECK 15:05 ET (14:05 CT)**\nNo EOD READ from Belle today. Her TradingView alert may be stopped.\nOpen TradingView, then Alerts, then press Restart on Belle Strike Panel.";
    let posted = 'no DISCORD_WEBHOOK_URL';
    if (process.env.DISCORD_WEBHOOK_URL) {
      const r = await fetch(process.env.DISCORD_WEBHOOK_URL.trim(), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content: text }) });
      posted = r.status;
    }
    return res.status(200).json({ ok: true, belle: 'missing', discord: posted });
  } catch (e) {
    return res.status(500).json({ ok: false, error: String(e).slice(0, 200) });
  }
}
