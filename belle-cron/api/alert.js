// PENNY relay: Belle alert (TradingView) -> short Discord call -> 1 SPY + 1 SPXW contract on the Alpaca PAPER account
// -> Penny trade manager on GitHub for the updates and exits.
// TradingView webhook URL: https://<this project>.vercel.app/api/alert?key=RELAY_KEY
// Vercel environment variables: RELAY_KEY, ALPACA_KEY_ID, ALPACA_SECRET_KEY, GITHUB_TOKEN, DISCORD_WEBHOOK_URL
// PAPER ONLY: the trading URL below is the Alpaca paper endpoint. Never change it.
const TRADE = 'https://paper-api.alpaca.markets';
const DATA = 'https://data.alpaca.markets';
const TZ = 'America/New_York';
const REPO = 'thetrinmillenia/belle-backtest';
const MIN_COST = 70; // Titi, Oct 19: lowest SPX contract is $70
const SPY_MAX = 60; // Titi, Oct 19: SPY not much higher than $0.60 per contract
const TARGET_COST = 100; // Titi, Oct 16: loves premiums around $100
const MAX_COST = 250; // Titi, Oct 17: anything over $250 is too much
const SPY_QTY = 3;   // SPY: 3 contracts so Penny can scale out, all 3 together within the same $ limit

function et(d = new Date()) {
  const f = new Intl.DateTimeFormat('en-US', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false, weekday: 'short' });
  const p = Object.fromEntries(f.formatToParts(d).map(x => [x.type, x.value]));
  return { y: p.year, m: p.month, d: p.day, h: Number(p.hour) % 24, min: Number(p.minute), wd: p.weekday };
}
const H = () => ({ 'APCA-API-KEY-ID': process.env.ALPACA_KEY_ID.trim(), 'APCA-API-SECRET-KEY': process.env.ALPACA_SECRET_KEY.trim(), 'Content-Type': 'application/json' });
async function discord(text) {
  if (!process.env.DISCORD_WEBHOOK_URL) return 'no DISCORD_WEBHOOK_URL';
  try { const r = await fetch(process.env.DISCORD_WEBHOOK_URL.trim(), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content: text.slice(0, 1900) }) }); return r.status; } catch (e) { return 'discord error ' + String(e).slice(0, 80); }
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

// one strike source (Titi, Oct 17): start at the strike the chart shows. If it costs more than the max,
// walk further out of the money one strike at a time until it fits. Never skip just because the chart strike is pricey.
async function pick(root, cp, price, ymd, chartK, maxCost, minCost = 0) {
  const step = root === 'SPY' ? 1 : 5;
  const dir = cp === 'C' ? 1 : -1; // moving OTM
  const start = chartK ? Math.round(chartK / step) * step : Math.round(price / step) * step;
  const strikes = []; for (let i = 0; i <= 10; i++) strikes.push(start + dir * i * step);
  const syms = strikes.map(s => occ(root, ymd, cp, s));
  const r = await fetch(`${DATA}/v1beta1/options/quotes/latest?symbols=${syms.join(',')}&feed=indicative`, { headers: H() });
  const q = await r.json();
  let first = null;
  for (let i = 0; i < syms.length; i++) {
    const x = q.quotes && q.quotes[syms[i]];
    if (!x || !x.ap) continue;
    const cost = x.ap * 100;
    if (i === 0) first = { strike: strikes[0], cost };
    if (cost > maxCost) continue;
    if (cost < minCost) return null; // walking further out only gets cheaper: never under the floor (Titi, Oct 19)
    return { sym: syms[i], strike: strikes[i], ask: x.ap, cost, moved: i, chart: first };
  }
  return null;
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'POST only' });
  // the key may hold & or + so read everything after key= from the raw URL
  const want = (process.env.RELAY_KEY || '').trim();
  const raw = String(req.url || '').split('key=').slice(1).join('key=');
  let dec = raw; try { dec = decodeURIComponent(raw); } catch (e) { }
  if (!want || ![raw, dec, req.query.key].includes(want)) return res.status(401).json({ ok: false, error: 'not authorized', keyLen: want.length, gotLen: raw.length });
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
    const inWin = t.wd !== 'Sat' && t.wd !== 'Sun' && ((mins >= 600 && mins <= 750) || (mins >= 900 && mins <= 955)); // Window 2 (13:45 to 15:00) off. EOD runs to 15:55 so the 15:50 candle counts (Titi, Oct 27)

    // morning: SPY first; afternoon: SPX first. Penny buys both when the cash allows.
    const order = mins < 760 ? ['SPY', 'SPXW'] : ['SPXW', 'SPY'];
    const picked = {}, notes = [];
    // Penny rule (Titi, Oct 16): holding one side and Belle fires the other side -> no new trade.
    // Discord still gets the alert; Penny tightens the open trade's stop (signal = empty watchlist penny-flip-C/P-time).
    let holding = null;
    if (inWin) {
      try {
        const pos = await (await fetch(`${TRADE}/v2/positions`, { headers: H() })).json();
        holding = (Array.isArray(pos) ? pos : []).find(p => /^(SPY|SPXW)\d{6}[CP]\d{8}$/.test(p.symbol) && p.symbol.slice(-9, -8) !== cp && Number(p.qty) > 0) || null;
      } catch (e) { holding = null; }
      if (holding) {
        notes.push(`holding ${holding.symbol.startsWith('SPXW') ? 'SPX' : 'SPY'} ${holding.symbol.slice(-9, -8) === 'C' ? 'calls' : 'puts'}, no new trade against her open trade, her stop stays the same`);
      }
    }
    // Window 3 = the EOD trade (Titi, Oct 19): the most important trade of the day, never blocked.
    // No 5 minute scalp timer: tight trail, Target 1, out by 15:58. A $100 contract can turn into $1,000.
    const scalp = mins >= 900;
    // EOD puts over calls (Titi, Oct 21: "puts are better EOD"). Window 3 calls are skipped when SPY is above PDC
    // (backtest: above PDC at 15:00, the last hour went down 67% of days). The stall break job handles EOD reversals.
    let eodNoCalls = false;
    if (scalp && cp === 'C' && a.spy) {
      try {
        const db = await (await fetch(`${DATA}/v2/stocks/SPY/bars?timeframe=1Day&feed=sip&start=${new Date(Date.now() - 10 * 864e5).toISOString().slice(0, 10)}&end=${t.y}-${t.m}-${t.d}T04:00:00Z`, { headers: H() })).json();
        const bars = db.bars || [];
        const pdc = bars.length ? bars[bars.length - 1].c : null;
        if (pdc && a.spy > pdc) { eodNoCalls = true; notes.push(`EOD calls skipped: SPY ${a.spy.toFixed(2)} above PDC ${pdc.toFixed(2)}, puts are favored EOD`); }
      } catch (e) { eodNoCalls = false; }
    }
    // after +$200 on the day (Titi, Oct 19): no entries in any chop, especially lunch (11:30 to 13:45 ET). EOD is never blocked.
  let chopSkip = false;
  if (inWin && !holding && !scalp && mins >= 690 && mins < 825) {
    try { const ac = await (await fetch(`${TRADE}/v2/account`, { headers: H() })).json(); chopSkip = Number(ac.equity) - Number(ac.last_equity) >= 200; } catch (e) { chopSkip = false; }
    if (chopSkip) notes.push('up $200+ today, no lunch or chop entries. Saving it for the EOD trade');
  }
    // Pearl (LIVE, Titi Oct 25): Window 1 (10:00 to 11:30 ET) and EOD (15:00 to 15:50 ET), calls and puts.
  // Pearl checks PEARL_ON and all her own rules (1 contract, $150 max, 1 loss and done). Penny's rules do not apply to her.
  if (inWin && ((mins >= 600 && mins <= 690) || mins >= 900) && process.env.GITHUB_TOKEN) {
    try {
      await fetch(`https://api.github.com/repos/${REPO}/actions/workflows/pearl.yml/dispatches`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${process.env.GITHUB_TOKEN.trim()}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'pearl' },
        body: JSON.stringify({ ref: 'main', inputs: { side: a.side, source: mins >= 900 ? 'EOD' : 'W1', spy_stop: n2(a.spyStop), spy_t3: '', why: String(a.why || '').slice(0, 200), sent: String(Math.floor(Date.now() / 1000)) } })
      });
    } catch (e) { notes.push('Pearl not reached'); }
  }
    // Shadow (Titi, Oct 26): every alert Penny skips, fully or for one of SPX / SPY, is scored after the close
    // (entry, highest, heat, rule E). One start per alert. No order, no Discord.
    const shadowItems = [];
    const shadowAdd = (root, why) => { const k = Number(root === 'SPY' ? a.spyStrike : a.spxStrike); if (inWin && k) shadowItems.push(`${occ(root, ymd, cp, k)}|${why}`); };
    if (holding || chopSkip || eodNoCalls) {
      const why = holding ? 'holding a trade' : (chopSkip ? 'chop filter (up $200, lunch)' : 'EOD calls above PDC');
      shadowAdd('SPXW', why);
      shadowAdd('SPY', why);
    }
  if (inWin && !holding && !chopSkip && !eodNoCalls) {
      const acct = await (await fetch(`${TRADE}/v2/account`, { headers: H() })).json();
      let bp = Number(acct.options_buying_power || acct.buying_power || 0);
      for (const root of order) {
        const price = root === 'SPY' ? a.spy : a.spx;
        const label = root === 'SPY' ? 'SPY' : 'SPX';
        if (!price) { notes.push(`${label} skipped, no price`); continue; }
        const qty = root === 'SPY' ? SPY_QTY : 1;
        const maxCost = root === 'SPY' ? SPY_MAX : MAX_COST; // per contract: SPX $100 to $250, SPY up to $0.60 (Titi, Oct 19)
        const c = await pick(root, cp, price, ymd, root === 'SPY' ? a.spyStrike : a.spxStrike, maxCost, root === 'SPY' ? 0 : MIN_COST);
        if (!c) { shadowAdd(root, 'no contract under the price cap'); notes.push(root === 'SPY' ? 'SPY skipped, nothing at $0.60 or less within 10 strikes' : `SPX skipped, nothing between ${MIN_COST} and ${MAX_COST} within 10 strikes`); continue; }
        if (c.moved > 0) notes.push(`${label}: Belle's ${c.chart ? c.chart.strike : ''}${cp} was $${c.chart ? Math.round(c.chart.cost * qty) : '?'}${qty > 1 ? ` for ${qty}` : ''}, over $${MAX_COST}, so Penny went ${c.moved} strike${c.moved > 1 ? 's' : ''} further out`);
        const lim = tick(c.ask, root);
        if (lim * 100 * qty > bp) { notes.push(`${label} skipped, not enough buying power`); shadowAdd(root, 'not enough buying power'); continue; }
        const o = await (await fetch(`${TRADE}/v2/orders`, { method: 'POST', headers: H(), body: JSON.stringify({ symbol: c.sym, qty: String(qty), side: 'buy', type: 'limit', limit_price: lim.toFixed(2), time_in_force: 'day', client_order_id: `penny-${t.y}-${t.m}-${t.d}-${label}-${Date.now()}` }) })).json();
        if (!o.id) { const why = String(o.message || o.code || 'no reason given').replace(/[;|]/g, ',').slice(0, 140); notes.push(`${label} order rejected for ${why}`); shadowAdd(root, `order rejected (${c.sym}): ${why}`); continue; } // Alpaca's reason is kept (Oct 28: wash trade rejections were invisible)
        bp -= lim * 100 * qty;
        picked[label] = { ...c, lim, id: o.id, qty };
        if (process.env.GITHUB_TOKEN) {
          await fetch(`https://api.github.com/repos/${REPO}/actions/workflows/belle-manage.yml/dispatches`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${process.env.GITHUB_TOKEN.trim()}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'penny' },
            body: JSON.stringify({ ref: 'main', inputs: { order_id: o.id, symbol: c.sym, label: `${label} ${c.strike}${cp}${scalp ? ' EOD' : ''}`, side: a.side, spy_stop: n2(a.spyStop), spy_t1: n2(a.spyT1), why: String(a.why || '').slice(0, 200) } })
          });
        }
      }
    } else if (!inWin) notes.push('no trade, outside the windows');

        if (shadowItems.length && process.env.GITHUB_TOKEN) {
      try {
        await fetch(`https://api.github.com/repos/${REPO}/actions/workflows/shadow.yml/dispatches`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${process.env.GITHUB_TOKEN.trim()}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'shadow' },
          body: JSON.stringify({ ref: 'main', inputs: { mode: 'record', sym: shadowItems.join(';'), side: a.side, sent: String(Math.floor(Date.now() / 1000)) } })
        });
      } catch (e) { }
    }
    const spyK = picked.SPY ? picked.SPY.strike : a.spyStrike;
    const spxK = picked.SPX ? picked.SPX.strike : a.spxStrike;
    const bought = Object.entries(picked).map(([k, v]) => `bought ${v.qty} ${k} ${v.strike}${cp} at ${v.lim.toFixed(2)} ($${Math.round(v.lim * 100 * v.qty)} total)`).join('\n');
    // spaced out for easy reading (Titi, Oct 17): one idea per line, a blank line between each
    const hm = a.time || `${String(t.h).padStart(2, '0')}:${String(t.min).padStart(2, '0')}`;
    const ct = (() => { const [h, m] = hm.split(':').map(Number); return `${String((h + 23) % 24).padStart(2, '0')}:${String(m).padStart(2, '0')}`; })();
    const lines = [
      `**${scalp ? 'EOD ' : ''}${a.side}  ${hm} ET (${ct} CT)**`,
      scalp ? 'Window 3 EOD trade: tight trail, Target 1, out by 15:58.' : null,
      `Belle's strike:  SPX ${a.spxStrike || 'n/a'}${cp}  |  SPY ${a.spyStrike || 'n/a'}${cp}`,
      a.spxAlt ? `Strike choices:  SPX ${a.spxAlt}  |  SPY ${a.spyAlt}` : null,
      `Stop:  SPX ${n2(a.spxStop)}  |  SPY ${n2(a.spyStop)}`,
      `Target 1:  SPX ${n2(a.spxT1)}  |  SPY ${n2(a.spyT1)}`,
      a.why ? `Why:  ${a.why}` : null,
      `PENNY:  ${[bought, ...notes].filter(Boolean).join('\n') || 'no trade'}`
    ].filter(Boolean);
    const posted = await discord(lines.join('\n\n'));
    // BELLE DRAFTS (Titi, Oct 21): Window 1 SPY entries in Titi's voice, to her private #belle-drafts channel.
    // She copies them into the community. @everyone is in the text but does not ping in the private channel.
    if (process.env.STUDENT_WEBHOOK_URL && picked.SPY && mins >= 600 && mins <= 750) {
      try {
        const p = picked.SPY, k = Math.round(p.strike), step = cp === 'C' ? 1 : -1;
        const ks = [k - step, k, k + step], syms = ks.map(x => occ('SPY', ymd, cp, x));
        const q = await (await fetch(`${DATA}/v1beta1/options/quotes/latest?symbols=${syms.join(',')}&feed=indicative`, { headers: H() })).json();
        const m = v => '$' + Number(v).toFixed(2).replace(/^0\./, '.');
        const ask = i => { const x = q.quotes && q.quotes[syms[i]]; return x && x.ap ? m(x.ap) : 'n/a'; };
        const side = cp === 'C' ? 'CALLS' : 'PUTS';
        const msg = [
          `$SPY\n$${k} ${side}\nEXPIRATION ${t.m}/${t.d}/${t.y}\n${m(p.lim)} Entry\n@everyone`,
          [a.why ? `• ${a.why}` : null, `• Stop: SPY ${cp === 'C' ? 'under' : 'over'} ${n2(a.spyStop)}`, `• Target 1: SPY ${n2(a.spyT1)}`].filter(Boolean).join('\n'),
          `Strike lesson:\n• ${ks[0]}${cp} ${ask(0)}: closer, costs more, moves faster\n• ${ks[1]}${cp} ${ask(1)}: my pick\n• ${ks[2]}${cp} ${ask(2)}: cheaper, needs a bigger move`,
          'Plan: 3 contracts. Sell 1 at +50%, 1 at +100%, the last one rides.'
        ].join('\n\n');
        await fetch(process.env.STUDENT_WEBHOOK_URL.trim(), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content: msg.slice(0, 1900), allowed_mentions: { parse: [] } }) });
      } catch (e) { }
    }
    return res.status(200).json({ ok: true, picked, notes, discord: posted });
  } catch (e) {
    await discord('PENNY error: ' + String(e).slice(0, 300));
    return res.status(500).json({ ok: false, error: String(e) });
  }
}
