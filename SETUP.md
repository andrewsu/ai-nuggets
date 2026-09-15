# Setting up your own ai-nuggets deployment

This guide is for someone who wants to clone (or fork) this repo and run
their **own** personalized-podcast automation: their own Cloudflare
Worker, their own API keys, their own daily cron. If you just want to
add a podcast to an existing deployment, see
[ADDING_A_SHOW.md](ADDING_A_SHOW.md) instead.

## What this gives you

A daily cron job that, for each podcast directory under `podcasts/`:

1. Hands the show's PROMPT.md to Claude Code, which curates and writes a script.
2. Generates an mp3 with Mistral TTS (or ElevenLabs as fallback).
3. Uploads the mp3 to a Cloudflare R2 bucket.
4. Updates the show's RSS feed and commits it back to your fork.
5. Serves enclosure URLs through a Cloudflare Worker that logs every
   download to D1 + Analytics Engine, with monthly-rotating IP hashes
   for listener counting.

The repo is built for **many individualized feeds with a single
subscriber each** — not broadcast. The Worker tags every request with a
per-listener `user_id` from the URL.

## Prerequisites

### Local machine

A Linux or macOS host that can run a cron job at the desired time. The
runner script is bash; the supporting tools are Python 3.11+
(`tomllib` is in the stdlib starting 3.11) and Node 18+.

Install:

- **Python 3.11+** with `pip` and `venv`
- **ffmpeg** and **ffprobe** on `$PATH` (for stitching TTS chunks and
  reading mp3 duration)
- **Node 18+** with `npm` (for `wrangler`)
- **git**
- **Claude Code CLI** — see https://docs.claude.com/en/docs/claude-code.
  The runner expects the `claude` binary; either install it where
  `run_all_shows.sh` looks (`/home/<user>/.local/bin/claude`) or edit
  the `CLAUDE=` line at the top of the script.
- A working **cron** (or systemd timer, launchd, etc.)

Python deps the pipeline uses:

```bash
pip install requests
```

### Accounts and API keys

You will need accounts and API keys for:

| Service | What it's used for | How to get the key |
|---|---|---|
| **Cloudflare** | Workers (request routing + analytics), R2 (mp3 storage), D1 (request log DB), Analytics Engine (long-term aggregates) | dash.cloudflare.com → My Profile → API Tokens. Create a token with Workers, R2, and D1 write scopes. |
| **Mistral** | Primary TTS (`voxtral-mini-tts-2603` / Paul Neutral) | console.mistral.ai → API Keys |
| **ElevenLabs** | Fallback TTS, also primary for some shows | elevenlabs.io → Profile → API Key |
| **Anthropic** | Claude Code, which writes the daily script | console.anthropic.com → API Keys, or sign in to Claude Code with your existing Claude account |

Mistral and ElevenLabs both have generous free tiers that are enough
for a handful of daily ~3-minute episodes.

## 1. Fork and clone

Fork this repo on GitHub (so the daily commits land on your fork, not
upstream), then clone:

```bash
git clone https://github.com/<your-user>/ai-nuggets.git
cd ai-nuggets
git config core.hooksPath .githooks   # enables the feed-XML pre-commit validator
```

## 2. `.env` with API keys

Create `.env` at the repo root (it is already in `.gitignore`):

```
MISTRAL_API_KEY=...
ELEVENLABS_API_KEY=...
CLOUDFLARE_API_TOKEN=...
```

`MISTRAL_API_KEY` and `ELEVENLABS_API_KEY` are read by `gen_tts.py`.
`CLOUDFLARE_API_TOKEN` is read by `wrangler` (which uploads mp3s to R2
inside `scripts/publish_episode.sh`).

The Anthropic key is **not** read from `.env` — Claude Code manages
its own auth via `claude login`. Do that once interactively before the
first cron run, and expect to repeat it **roughly monthly**: the OAuth
refresh token in `~/.claude/.credentials.json` is set about 28 days out
by each login and cannot be renewed from cron. Check how much runway is
left at any time with:

```bash
scripts/check_credentials.py     # OK / WARN / EXPIRED + the expiry date
```

`run_all_shows.sh` runs that check pre-flight and aborts rather than
attempting any show on dead credentials, and the daily audit email
carries a warning note once fewer than `CRED_WARN_DAYS` (default 5) days
remain.

## 3. Point the Worker fallback at your fork

`worker/wrangler.toml` has a hardcoded reference to `andrewsu/ai-nuggets`
in `GITHUB_REPO_RAW`. The Worker uses this URL as a fallback when an
mp3 hasn't yet landed in R2. Edit it to point at your fork:

```toml
[vars]
GITHUB_REPO_RAW = "https://raw.githubusercontent.com/<your-user>/ai-nuggets/main"
```

While you are in `wrangler.toml`, also reset `ALLOWED_PODCASTS` to the
slugs of the shows you plan to run (or leave the demo values and remove
them later).

## 4. Deploy the Cloudflare Worker

Follow `worker/README.md`. The short version, from the `worker/`
directory:

```bash
npm install
npx wrangler login                              # opens browser for OAuth
npx wrangler d1 create podcast                  # paste the printed database_id back into wrangler.toml
npm run db:init                                 # init schema in local-dev D1
npm run db:init:remote                          # init schema in real D1
npx wrangler secret put IP_SALT                 # paste any long random string
npx wrangler r2 bucket create ai-nuggets-episodes
npm run deploy                                  # note the printed *.workers.dev URL
```

The printed URL (e.g., `https://podcast.<your-subdomain>.workers.dev`)
is what goes into the `--worker-url` flag of
`scripts/update_feed_for_worker.py` and into the `<enclosure>` URLs in
every show's `feed.xml`.

If you change the bucket name in `[[r2_buckets]]`, update
`scripts/publish_episode.sh` to match.

## 5. Create your first show

```bash
python3 scripts/new_show.py my-first-show \
  --title "My First Show" \
  --description "What this show is about" \
  --owner "Your Name <you@example.com>"
```

Then follow [ADDING_A_SHOW.md](ADDING_A_SHOW.md) from step 2 onward
(customize PROMPT.md, set TTS voice, add the slug to ALLOWED_PODCASTS,
redeploy the Worker, do a manual smoke test).

## 6. Schedule the daily cron

Edit `scripts/run_all_shows.sh` if your install paths differ:

- `REPO=` — absolute path to your clone of ai-nuggets
- `CLAUDE=` — absolute path to the `claude` binary

Add to your crontab (`crontab -e`):

```
# Daily personalized podcasts at 4 AM local time
0 4 * * * /absolute/path/to/ai-nuggets/scripts/run_all_shows.sh
```

The runner iterates over every `podcasts/*/PROMPT.md` and pipes
`PIPELINE.md + PROMPT.md` to Claude Code for each one in sequence
(sequential on purpose: avoids TTS API contention and races on
`git push`). Each show's output is logged to
`podcasts/<slug>/logs/cron.log`.

A single AUP refusal on the first attempt triggers one automatic retry
after a 3-minute pause. After both attempts fail, the runner moves to
the next show — it does not block the whole run.

## 7. Verify the unattended run

After the first cron firing, check:

- `podcasts/<slug>/logs/cron.log` — should show `=== start ===` and
  `=== done (exit 0) ===` markers.
- `git log -10` — should show new commits from your daily run.
- `curl -I "https://podcast.<sub>.workers.dev/p/<slug>/u/<listener>/<basename>.mp3"`
  — 200 (R2 hit) means listener-facing delivery works. 404 means either
  the Worker isn't recognizing the slug or the R2 upload didn't land.

## 8. Listener analytics

Once the Worker is logging requests, `worker/queries.sql` has starter
queries against D1:

```bash
cd worker
npx wrangler d1 execute podcast --remote --command "SELECT podcast, COUNT(*) FROM requests GROUP BY podcast;"
```

Long-term aggregates live in Analytics Engine (dataset
`podcast_requests`) and are queryable via Cloudflare's GraphQL API or
the dashboard.

## Common pitfalls

- **Claude Code not on PATH under cron.** Cron does not source
  `~/.bashrc`. Either use the absolute path in `CLAUDE=` (already the
  default) or symlink `claude` into `/usr/local/bin/`.
- **Every show fails with `no_output` on the same night.** Almost always
  the Claude Code OAuth session expired — `claude -p` prints `Failed to
  authenticate: OAuth session expired and could not be refreshed` and
  exits 0, so it looks like an empty run. The audit email reports those
  shows as `AUTH`; confirm with `scripts/check_credentials.py` and fix by
  running `claude` interactively on the host and typing `/login`.
- **`wrangler` can't authenticate under cron.** `scripts/publish_episode.sh`
  sources `.env` precisely to pick up `CLOUDFLARE_API_TOKEN`. If the
  upload fails with auth errors, confirm the token is in `.env` and has
  R2 write scope.
- **Feed.xml fails to commit.** The `.githooks/pre-commit` validator
  rejects malformed XML and wrong `<pubDate>` weekdays. The error
  message usually tells you exactly which line.
- **Worker returns 404 for a known slug.** The slug isn't in
  `ALLOWED_PODCASTS` or you forgot to redeploy after editing
  `wrangler.toml`. `cd worker && npm run deploy` again.
- **mp3 in feed but Worker returns 404.** The R2 upload failed silently —
  re-run `scripts/publish_episode.sh <slug> <basename>`. There is no
  fallback to GitHub raw; the mp3 must be in R2.

## Where to go next

- [`podcasts/PIPELINE.md`](podcasts/PIPELINE.md) — production-pipeline
  rules every show inherits (source-failure handling, audio-friendly
  writing, per-episode steps, re-invocation rules, audit logging).
- [`worker/README.md`](worker/README.md) — Worker internals, route
  schema, D1 schema, and analytics queries.
- [`ADDING_A_SHOW.md`](ADDING_A_SHOW.md) — full checklist for each new
  show after the infrastructure is up.
