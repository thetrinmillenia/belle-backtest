// Belle morning timer: asks GitHub to run the Belle morning workflow.
// Vercel calls this on the schedule in vercel.json and sends Authorization: Bearer CRON_SECRET.
export default async function handler(req, res) {
  if (!process.env.CRON_SECRET || req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ ok: false, error: 'not authorized' });
  }
  if (!process.env.GITHUB_TOKEN) {
    return res.status(500).json({ ok: false, error: 'GITHUB_TOKEN is not set in Vercel' });
  }
  const r = await fetch('https://api.github.com/repos/thetrinmillenia/belle-backtest/actions/workflows/belle-morning.yml/dispatches', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${process.env.GITHUB_TOKEN.trim()}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'belle-cron'
    },
    body: JSON.stringify({ ref: 'main', inputs: { force: '0' } })
  });
  const body = await r.text();
  return res.status(r.status === 204 ? 200 : 502).json({ ok: r.status === 204, github: r.status, body });
}
