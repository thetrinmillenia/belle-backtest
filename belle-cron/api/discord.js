// PENNY COMMANDS (Titi, Nov 3): Discord slash commands for Penny's PAPER account (Alpaca paper only).
//   /out      sells all of Penny's open SPX and SPY options at market. She keeps trading.
//   /lockout  sells everything and blocks new Penny trades until tomorrow (an empty Alpaca watchlist penny-lock-YYYY-MM-DD).
//   /in       lifts today's lockout.
// Only Titi's Discord account can use them (DISCORD_OWNER_ID). Discord signs every request; the relay checks it with
// DISCORD_PUBLIC_KEY. Both are Vercel environment variables Titi adds herself. Pearl gets the same commands when she is live.
import crypto from 'crypto';

export const config = { api: { bodyParser: false } };

const TRADE = 'https://paper-api.alpaca.markets';   // PAPER only. Never the live endpoint.
const H = () => ({ 'APCA-API-KEY-ID': process.env.ALPACA_KEY_ID.trim(), 'APCA-API-SECRET-KEY': process.env.ALPACA_SECRET_KEY.trim(), 'Content-Type': 'application/json' });

async function rawBody(req) {
  const chunks = [];
  for await (const c of req) chunks.push(typeof c === 'string' ? Buffer.from(c) : c);
  return Buffer.concat(chunks);
}

function signed(body, sig, ts) {
  const pk = (process.env.DISCORD_PUBLIC_KEY || '').trim();
  if (!pk || !sig || !ts) return false;
  try {
    const key = crypto.createPublicKey({ key: Buffer.concat([Buffer.from('302a300506032b6570032100', 'hex'), Buffer.from(pk, 'hex')]), format: 'der', type: 'spki' });
    return crypto.verify(null, Buffer.concat([Buffer.from(ts), body]), key, Buffer.from(sig, 'hex'));
  } catch (e) {
    return false;
  }
}

function et(d = new Date()) {
  const f = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false });
  const p = Object.fromEntries(f.formatToParts(d).map(x => [x.type, x.value]));
  const h = Number(p.hour) % 24;
  return { y: p.year, m: p.month, d: p.day, hm: `${String(h).padStart(2, '0')}:${p.minute}`, ct: `${String((h + 23) % 24).padStart(2, '0')}:${p.minute}` };
}

async function sellAll() {
  const pos = await (await fetch(`${TRADE}/v2/positions`, { headers: H() })).json();
  const opts = (Array.isArray(pos) ? pos : []).filter(p => /^(SPY|SPXW)\d{6}[CP]\d{8}$/.test(p.symbol) && Number(p.qty) > 0);
  await fetch(`${TRADE}/v2/orders`, { method: 'DELETE', headers: H() });   // cancel her working stops first
  let n = 0;
  for (const p of opts) {
    const r = await fetch(`${TRADE}/v2/positions/${p.symbol}`, { method: 'DELETE', headers: H() });
    if (r.ok) n += Number(p.qty);
  }
  return n;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(200).send('Penny commands');
  const body = await rawBody(req);
  if (!signed(body, req.headers['x-signature-ed25519'], req.headers['x-signature-timestamp'])) return res.status(401).send('invalid request signature');
  const i = JSON.parse(body.toString('utf8'));
  if (i.type === 1) return res.status(200).json({ type: 1 });   // Discord's ping
  const reply = content => res.status(200).json({ type: 4, data: { content, allowed_mentions: { parse: [] } } });
  const user = (i.member && i.member.user && i.member.user.id) || (i.user && i.user.id);
  if (!process.env.DISCORD_OWNER_ID || user !== process.env.DISCORD_OWNER_ID.trim()) return reply('Only Titi can use this.');
  const cmd = i.data && i.data.name;
  const t = et();
  const stamp = `${t.hm} ET (${t.ct} CT)`;
  const lock = `penny-lock-${t.y}-${t.m}-${t.d}`;
  try {
    if (cmd === 'out' || cmd === 'lockout') {
      const n = await sellAll();
      if (cmd === 'out') return reply(`**PENNY OUT  ${stamp}**\n\n${n} contract${n === 1 ? '' : 's'} sold\n\nStill trading`);
      await fetch(`${TRADE}/v2/watchlists`, { method: 'POST', headers: H(), body: JSON.stringify({ name: lock, symbols: [] }) });
      return reply(`**PENNY LOCKOUT  ${stamp}**\n\n${n} contract${n === 1 ? '' : 's'} sold\n\nLocked out until tomorrow`);
    }
    if (cmd === 'in') {
      const wl = await (await fetch(`${TRADE}/v2/watchlists`, { headers: H() })).json();
      for (const w of Array.isArray(wl) ? wl : []) {
        if (w.name === lock) await fetch(`${TRADE}/v2/watchlists/${w.id}`, { method: 'DELETE', headers: H() });
      }
      return reply(`**PENNY IN  ${stamp}**\n\nPenny can trade again`);
    }
    return reply('Unknown command');
  } catch (e) {
    return reply(`PENNY command failed, check Alpaca now: ${String(e).slice(0, 150)}`);
  }
}
