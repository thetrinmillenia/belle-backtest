// Belle timer (Titi, Oct 26): GitHub's own clock started jobs hours late, so Vercel's clock starts them instead.
// Vercel calls /api/kick?job=NAME on the schedules in vercel.json and sends Authorization: Bearer CRON_SECRET.
// Each job checks its own time window, so an extra start just exits. No Discord posts here.
const JOBS = {
  orb: { wf: 'belle-orb.yml', inputs: {} },
  stall: { wf: 'belle-stall.yml', inputs: {} },
  eod: { wf: 'belle-eod.yml', inputs: { force: '0' } },
  nora: { wf: 'nora.yml', inputs: { force: '0' } },
  harper: { wf: 'harper.yml', inputs: { force: '0' } }
};

export default async function handler(req, res) {
  if (!process.env.CRON_SECRET || req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ ok: false, error: 'not authorized' });
  }
  if (!process.env.GITHUB_TOKEN) {
    return res.status(500).json({ ok: false, error: 'GITHUB_TOKEN is not set in Vercel' });
  }
  const job = JOBS[String(req.query.job || '')];
  if (!job) return res.status(400).json({ ok: false, error: 'unknown job' });
  const r = await fetch(`https://api.github.com/repos/thetrinmillenia/belle-backtest/actions/workflows/${job.wf}/dispatches`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${process.env.GITHUB_TOKEN.trim()}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'belle-cron'
    },
    body: JSON.stringify({ ref: 'main', inputs: job.inputs })
  });
  const body = await r.text();
  return res.status(r.status === 204 ? 200 : 502).json({ ok: r.status === 204, job: req.query.job, github: r.status, body });
}
