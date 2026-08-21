# SUBSCRIPTION_AUDIT — 2026-08-21

License: LAW_INDEX @ d449889e · L18 · L20 · L22. Seat: CC (verification). Secrets: NAMES ONLY, no values.

## Scope / reachability
- Droplet A 104.131.191.95 (ubuntu-s-1vcpu-2gb-nyc3-01, up 191d): REACHED. Repo /root/Omi-Workspace @ 76ce937d (branch codex/stage-c-v36-cutover-prep-20260807).
- Droplet B 159.65.234.55: UNREACHABLE (ssh port 22 timeout). Not audited — unknown state, unknown spend.
- Desktop (Windows, C:\Users\omigr): REACHED. Repo OMI-Workspace @ f20e5769 (codex/window1-analysis-seat).
- Vercel team omi-groups-projects, project omi-workspace (prj_GELuGqSWOz71rYdlQ9m1zXcpveqI): REACHED via MCP.

## Per paid service

### Vercel (omi-workspace.vercel.app) — CONSUMED
- Consumed by: droplet A cron `dashboard_push.py --url https://omi-workspace.vercel.app/api/arb` every 1 min (HTTP 200 @ 2026-08-21 14:54Z) → live trading dashboard.
- Consumed by: droplet A `depth_recorder.py` (pid 1213728, env DASHBOARD_URL → vercel.app).
- Consumed by: GitHub integration — every branch push to OMIGROUPOPS/Omi-Workspace builds a deployment (20 deploys on 2026-08-20/21, most ERROR; prod domain serves latest READY). Builds are the main Vercel usage.
- Vercel crons (vercel.json): /api/odds/sync */15, /api/odds/sync-exchanges */15, /api/stats/sync-espn 0 */6, /api/weather/sync 0 */3.
- Machine: Vercel cloud + droplet A (pusher). Desktop: no CLI state found (.vercel absent).
- Note: `/api/arb` route has no DB — in-process only; dashboard does NOT depend on Supabase.

### The Odds API (api.the-odds-api.com) — CONSUMED ×2
- Consumer 1: droplet A `arb-executor/tennis_odds.py` (screen `tennis_odds`, running 29d, respawned by cron `deploy/respawn_tennis_odds.sh` */5). Polls /sports + /odds every ~2 min; log shows quota counter moving today (`API remaining: 4,289,833` @ 10:54). **Key is HARDCODED at tennis_odds.py:23** (last commit 41d0729e), not read from env.
- Consumer 2: Vercel cron `/api/odds/sync` (*/15, CRON_SECRET-guarded) + `/api/odds/scores` (public GET; returned live scores → ODDS_API_KEY IS set on Vercel) + `/api/debug/sync`. Machine: Vercel.
- Also present (NOT running): `backend/config.py` + `backend/data_sources/odds_api.py` (Python backend, intended for Railway/Docker) — no backend process on droplet A or desktop.
- Env var name ODDS_API_KEY in: backend/.env (droplet A, desktop + 22 codex worktrees), /opt/omi-edge/backend/.env (droplet A, stale Jan-2026 build, no node process).

### Supabase (project ref hlefsuxeojbqvdeyzjkz) — CONSUMED (Vercel only)
- Consumer: Next.js app on Vercel — 61 files in app/ lib/ components/ (auth login/signup, clients, portal, odds/sync writes tables cached_odds / line_snapshots / odds_snapshots). lib/supabaseClient.ts, lib/supabaseAuth.ts.
- Droplet A: NO consumer. `python3 -c "import supabase"` → ModuleNotFoundError; no running process references supabase. Only NEXT_PUBLIC_SUPABASE_URL / _ANON_KEY sit unused in backend/.env and /opt/omi-edge/backend/.env.
- Desktop: NO running consumer (only .env copies in worktrees).
- Host answers 401 on /rest/v1/ (project alive). Paid tier vs free: NOT DETERMINABLE from machines.

### Railway (omi-workspace-production.up.railway.app) — CONSUMED BY NOTHING FOUND
- URL returns no response (curl exit 000) → service down/deleted.
- Referenced only by dead code: arb-executor/arb_executor_ws.py:282 & arb-executor-v2/arb_executor_ws.py:276 (NCAAB edge-signal; not running), components/edge/GameDetailClient.tsx (fallback BACKEND_URL), backend/ comments.
- No Railway CLI/config on droplet A or desktop. If the Railway subscription is still billing, it is paying for nothing reachable.

### DigitalOcean Spaces (omi-tick-archive, nyc3) — CONSUMED
- Consumer: droplet A cron `rclone copy data/durable/ws_depth_recorder → spaces:omi-tick-archive/ws_depth` every 6h (keys SPACES_KEY/SPACES_SECRET from arb-executor/.env) + `deploy/archive_sync.sh` daily 09:10. Machine: droplet A.

### Kalshi / Polymarket (exchange API keys, not subscriptions) — CONSUMED
- KALSHI_API_KEY/KALSHI_PEM_PATH (arb-executor/.env, droplet A): settle_positions.py */30, cash_ledger.py hourly, position_audit.py */30, kalshi_price_scraper.py, ws_depth_recorder.py, depth_recorder.py, fund_tracker.py, mlb_bbo_logger.py, dashboard_api.py.
- PM_US_API_KEY/PM_US_SECRET_KEY (arb-executor/.env): settle_positions.py, pregame_mapper.py, check_deposits.py; cron.d/omi-polymarket `tools/polymarket_ref.py` */5 (public gamma API).

### Anthropic / OpenAI / Resend — CONSUMED BY NOTHING FOUND (on these machines)
- Desktop user env vars: CLAUDE_API_KEY, OPEN_API_KEY, Resend_API_KEY. No running process, task, or repo code reads them (zero `resend` refs in repo). Claude Code itself authenticates via account, not CLAUDE_API_KEY.
- Droplet A: ANTHROPIC_API_KEY / OPENAI_API_KEY read only by backend/api/server.py, backend/config.py, app/api/edge/assistant/route.ts — backend not running; assistant route only live if key set on Vercel (not probed).

## Desktop summary
- No scheduled tasks, services, or startup items touching any paid service (only OneDrive/Zoom/Chrome/Teams).
- Running: one node build_window1_v38_maker_only.js (local analysis), Codex runtime. No WSL distros.
- 24 copies of backend/.env across OMI-Workspace worktrees + legacy-quarantine .env.local (extra names: CRON_SECRET, FOOTBALL_DATA_API_KEY, BACKEND_URL, SCANNER_URL, NEXT_PUBLIC_BOT_SERVER_URL).

## Hygiene findings (L20 — disclosed, not fixed)
- H1: `backend/.env` is TRACKED in git since 01dcc8b8 (2026-07-01); repo OMIGROUPOPS/Omi-Workspace is PUBLIC per Vercel deploy meta → NEXT_PUBLIC_SUPABASE_ANON_KEY, NEXT_PUBLIC_SUPABASE_URL, ODDS_API_KEY are public. Rotate ODDS_API_KEY; anon key is public-by-design but RLS must be on.
- H2: Odds API key literal at arb-executor/tennis_odds.py:23 (tracked, public repo). Rotate + move to env.
- H3: OMI_API_KEY default literal at arb-executor/arb_executor_ws.py:283 and arb-executor-v2/arb_executor_ws.py:277 (tracked). Rotate if that token still guards anything.
- H4: /opt/omi-edge (Jan-2026 build) and /root/Omi-Workspace/backend/.env (Feb-2026) are stale key copies on droplet A; nothing runs them.
- H5: Droplet B 159.65.234.55 unreachable — cannot rule out a second Odds-API/Kalshi consumer there.

## Verdict table
| Service | Consumed by | Machine |
|---|---|---|
| Vercel | dashboard_push cron, depth_recorder, GitHub auto-deploys, 4 vercel crons | droplet A → Vercel |
| The Odds API | tennis_odds.py (hardcoded key) ; /api/odds/sync + /api/odds/scores | droplet A ; Vercel |
| Supabase | Next.js app (auth, portal, odds tables) | Vercel only |
| Railway | NOTHING FOUND (URL dead) | — |
| DO Spaces | rclone archive crons | droplet A |
| Kalshi / Polymarket keys | trading + ledger crons/screens | droplet A |
| Anthropic / OpenAI / Resend keys | NOTHING FOUND running | desktop env vars only |
| Droplet B | NOT AUDITED (unreachable) | — |
