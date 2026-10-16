// PENNY relay: Belle alert (TradingView) -> short Discord call -> 1 SPY + 1 SPXW contract on the Alpaca PAPER account
// -> Penny trade manager on GitHub for the updates and exits.
// TradingView webhook URL: https://<this project>.vercel.app/api/alert?key=RELAY_KEY
// Vercel environment variables: RELAY_KEY, ALPACA_KEY_ID, ALPACA_SECRET_KEY, GITHUB_TOKEN, DISCORD_WEBHOOK_URL
// PAPER ONLY: the trading URL below is the Alpaca paper endpoint. Never change it.
const TRADE = 'https://paper-api.alpaca.markets';
const DATA = 'https://data.alpaca.markets';
const TZ = 'America/New_York';
const REPO = 'thetrinmillenia/belle-backtest';
const MIN_COST = 150; // dollars per contract
const MAX_COST = 300;

function et(d = new Date()) {
  const f = new Intl.DateTimeFormat('en-US', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false, weekday: 'short' });
  const p = Object.fromEntries(f.formatToParts(d).map(x => [x.type, x.value]));
  return { y: p.year, m: p.month, d: p.day, h: Number(p.hour) % 24, min: Number(p.minute), wd: p.weekday };
}
const H = () => ({ 'APCA-API-KEY-ID': process.env.ALPACA_KEY_ID.trim(), 'APCA-API-SECRET-KEY': process.env.ALPACA_SECRET_KEY.trim(), 'Content-Type': 'application/json' });
async function discord(text) {
  if (!process.env.DISCORD_WEBHOOK_URL) return;
  try { await fetch(process.env.DISCORD_WEBHOOK_URL.trim(), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content: text.slice(0, 1900) }) }); } catch (e) { }
}
const n2 = x => (x == null || isNaN(x) ? 'n/a' : Number(x).toFixed(2));
function occ(root, ymd, cp, strike) { return `${root}${ymd}${cp}${String(Math.round(strike * 1000)).padStart(8, '0')}`; }
function tick(p, root) { if (root === 'SPY') return Math.ceil(p * 100 - 1e-9) / 100; return p >= 3 ? Math.ceil(p * 10 - 1e-9) / 10 : Math.ceil(p * 20 - 1e-9) / 20; }

// read the alert: the new Belle alert sends fields; older alerts send one long text line
function readAlert(body) {
  if (body && body.side) return body;
  const t = (body && body.content) || '';
  const m = t.match(/^(CALLS|PUTS)\s+SPXW\s+(\d{4,5})([CP])\s*\|\s*SPY\s+(\d+)/);
  if (!m) return null;
  const num = re => { const x = t.match(re); return x ? Number(x[1]) : null; };
  const spx = num(/SPX ([\d.]+) at/), spxStop = num(/Stop SPX ([\d.]+)/), spxT1 = num(/Target 1: SPX ([\d.]+)/);
  const ratio = spx && Number(m[4]) ? spx / Number(m[4]) : 10.03;
  return { side: m[1], time: (t.match(/at (\d\d:\d\d) ET/) || [])[1], spx, spy: spx ? spx / ratio : null, spxStop, spyStop: spxStop ? spxStop / ratio : null, spxT1, spyT1: spxT1 ? spxT1 / ratio : null, spxStrike: Number(m[2]), spyStrike: Number(m[4]), why: (t.split('|')[4] || '').trim() };
}

// pick the contract that costs closest to $150, never under $150 or over $300
async function pick(root, cp, price, ymd) {
  const step = root === 'SPY' ? 1 : 5;
  const atm = Math.round(price / step) * step;
  const dir = cp === 'C' ? 1 : -1; // moving OTM
  const strikes = []; for (let i = -2; i <= 14; i++) strikes.push(atm + dir * i * step);
  const syms = strikes.map(s => occ(root, ymd, cp, s));
  const r = await fetch(`${DATA}/v1beta1/options/quotes/latest?symbols=${syms.join(',')}&feed=indicative`, { headers: H() });
  const q = await r.json();
  let best = null;
  syms.forEach((s, i) => {
    const x = q.quotes && q.quotes[s];
    if (!x || !x.ap) return;
    const cost = x.ap * 100;
    if (cost < MIN_COST || cost > MAX_COST) return;
    const score = cost - MIN_COST;
    if (!best || score < best.score) best = { sym: s, strike: strikes[i], ask: x.ap, cost, score };
  });
  return best;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'POST only' });
  if (!process.env.RELAY_KEY || req.query.key !== process.env.RELAY_KEY) return res.status(401).json({ ok: false, error: 'not authorized' });
  try {
    let body = req.body;
    if (typeof body === 'string') { try { body = JSON.parse(body); } catch { body = { content: body }; } }
    const a = readAlert(body);
    if (!a) { if (body && body.content) await discord(body.content); return res.status(200).json({ ok: true, traded: false, why: 'not an entry alert' }); }

    const cp = a.side === 'CALLS' ? 'C' : 'P';
    const t = et();
    const mins = t.h * 60 + t.min;
    const ymd = `${t.y.slice(2)}${t.m}${t.d}`;
    // same windows as Belle v42 (by candle close): W1 10:00 to 12:30, W2 13:45 to 15:00, W3 15:00 to 15:50 ET
    const inWin = t.wd !== 'Sat' && t.wd !== 'Sun' && ((mins >= 600 && mins <= 750) || (mins >= 825 && mins <= 950));

    // morning: SPY first; afternoon: SPX first. Penny buys both when the cash allows.
    const order = mins < 760 ? ['SPY', 'SPXW'] : ['SPXW', 'SPY'];
    const picked = {}, notes = [];
    if (inWin) {
      const acct = await (await fetch(`${TRADE}/v2/account`, { headers: H() })).json();
      let bp = Number(acct.options_buying_power || acct.buying_power || 0);
      for (const root of order) {
        const price = root === 'SPY' ? a.spy : a.spx;
        const label = root === 'SPY' ? 'SPY' : 'SPX';
        if (!price) { notes.push(`${label} skipped, no price`); continue; }
        const c = await pick(root, cp, price, ymd);
        if (!c) { notes.push(`${label} skipped, no contract between $150 and $300`); continue; }
        const lim = tick(c.ask, root);
        if (lim * 100 > bp) { notes.push(`${label} skipped, not enough buying power`); continue; }
        const o = await (await fetch(`${TRADE}/v2/orders`, { method: 'POST', headers: H(), body: JSON.stringify({ symbol: c.sym, qty: '1', side: 'buy', type: 'limit', limit_price: lim.toFixed(2), time_in_force: 'day', client_order_id: `penny-${t.y}-${t.m}-${t.d}-${label}-${Date.now()}` }) })).json();
        if (!o.id) { notes.push(`${label} order rejected`); continue; }
        bp -= lim * 100;
        picked[label] = { ...c, lim, id: o.id };
        if (process.env.GITHUB_TOKEN) {
          await fetch(`https://api.github.com/repos/${REPO}/actions/workflows/belle-manage.yml/dispatches`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${process.env.GITHUB_TOKEN.trim()}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'penny' },
            body: JSON.stringify({ ref: 'main', inputs: { order_id: o.id, symbol: c.sym, label: `${label} ${c.strike}${cp}`, side: a.side, spy_stop: n2(a.spyStop), spy_t1: n2(a.spyT1) } })
          });
        }
      }
    } else notes.push('no trade, outside the windows');

    const spyK = picked.SPY ? picked.SPY.strike : a.spyStrike;
    const spxK = picked.SPX ? picked.SPX.strike : a.spxStrike;
    const bought = Object.entries(picked).map(([k, v]) => `${k} ${v.strike}${cp} at ${v.lim.toFixed(2)}`).join(' | ');
    const lines = [
      `${a.side} ${a.time || `${String(t.h).padStart(2, '0')}:${String(t.min).padStart(2, '0')}`} ET`,
      `SPY ${spyK ?? 'n/a'}${cp} | stop SPY ${n2(a.spyStop)}`,
      `SPX ${spxK ?? 'n/a'}${cp} | stop SPX ${n2(a.spxStop)}`,
      `Target 1: SPX ${n2(a.spxT1)} | SPY ${n2(a.spyT1)}`,
      a.why ? `Why: ${a.why}` : null,
      `PENNY: ${[bought, ...notes].filter(Boolean).join(' | ') || 'no trade'}`
    ].filter(Boolean);
    await discord(lines.join('\n'));
    return res.status(200).json({ ok: true, picked, notes });
  } catch (e) {
    await discord('PENNY error: ' + String(e).slice(0, 300));
    return res.status(500).json({ ok: false, error: String(e) });
  }
}
