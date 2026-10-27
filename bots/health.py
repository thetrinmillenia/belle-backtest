"""BOT HEALTH (Titi, Oct 26 2026). After the close, checks that the timed bots really started on time today.
Writes results/bot_health.csv (no Discord). A job that started late, or never, shows "missed".
Runs in Nora's job with the GitHub token (read only)."""
import csv
import datetime as dt
import os
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
REPO = os.environ.get("GITHUB_REPOSITORY", "thetrinmillenia/belle-backtest")
GH = os.environ.get("GH_TOKEN", "").strip()
# job: (workflow, first ET minute it may start, last ET minute it may start and still do its job)
JOBS = {
    "Belle morning": ("belle-morning.yml", 5 * 60, 9 * 60 + 29),
    "ORB": ("belle-orb.yml", 9 * 60, 9 * 60 + 59),
    "Belle afternoon": ("belle-afternoon.yml", 12 * 60, 13 * 60 + 59),
    "Stall": ("belle-stall.yml", 13 * 60, 13 * 60 + 59),
}
now = dt.datetime.now(ET)
day = os.environ.get("EVAL_DATE", "").strip() or f"{now:%Y-%m-%d}"
if not os.environ.get("EVAL_DATE", "").strip() and (now.weekday() >= 5 or now.hour < 16):
    print("not after the close on a weekday, skipping")
    raise SystemExit(0)
path = "results/bot_health.csv"
if os.path.exists(path) and any(line.startswith(day + ",") for line in open(path)):
    print("already checked", day)
    raise SystemExit(0)
rows = []
for job, (wf, lo, hi) in JOBS.items():
    try:
        r = requests.get(f"https://api.github.com/repos/{REPO}/actions/workflows/{wf}/runs", timeout=20,
                         headers={"Authorization": f"Bearer {GH}", "Accept": "application/vnd.github+json"},
                         params={"created": f">={dt.date.fromisoformat(day) - dt.timedelta(days=1)}", "per_page": 100}).json()
        starts = []
        for run in r.get("workflow_runs", []):
            t = dt.datetime.fromisoformat((run.get("run_started_at") or run["created_at"]).replace("Z", "+00:00")).astimezone(ET)
            if f"{t:%Y-%m-%d}" == day:
                starts.append(t)
        on_time = [t for t in starts if lo <= t.hour * 60 + t.minute <= hi]
        status = "ok" if on_time else "missed"
        first = f"{min(on_time or starts):%H:%M}" if starts else ""
        rows.append([day, job, status, len(starts), first, f"{lo // 60:02d}:{lo % 60:02d} to {hi // 60:02d}:{hi % 60:02d}"])
    except Exception as e:
        rows.append([day, job, f"check failed: {e}"[:80], "", "", ""])
os.makedirs("results", exist_ok=True)
new = not os.path.exists(path)
with open(path, "a", newline="") as fh:
    w = csv.writer(fh)
    if new:
        w.writerow(["date", "job", "status", "starts", "first_on_time_start_et", "window_et"])
    w.writerows(rows)
for row in rows:
    print(row)
