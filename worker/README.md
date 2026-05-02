# Podcast analytics Worker

Cloudflare Worker that fronts mp3 enclosure URLs across all podcasts in this
repo. Logs each request to D1 + Analytics Engine, then 302-redirects to the
canonical mp3 on GitHub raw (or, eventually, Cloudflare R2).

This Worker lives in this repo for convenience but is not specific to the
`biomedical-agentic-ai` show — it serves every podcast under `podcasts/<slug>/`.
If a third or fourth podcast joins, `ALLOWED_PODCASTS` in `wrangler.toml` is
the only thing that needs editing.

## Route

```
GET|HEAD /p/:podcast/u/:user_id/:episode_id.mp3
```

* `:podcast` — slug (validated against `ALLOWED_PODCASTS`)
* `:user_id` — per-listener token (free-form alphanumeric/hyphen/underscore)
* `:episode_id` — mp3 basename without extension

Anything else returns plain-text 404.

## One-time setup

Run these commands in order from this directory.

```bash
# 1. Install deps locally.
npm install

# 2. Log in to Cloudflare.
npx wrangler login

# 3. Create the D1 database. Copy the printed `database_id` into wrangler.toml,
#    replacing the REPLACE_AFTER_WRANGLER_D1_CREATE placeholder.
npx wrangler d1 create podcast

# 4. Initialize the schema locally (against the local-dev D1 emulator).
npm run db:init

# 5. Initialize the schema remotely (against the real D1 database).
npm run db:init:remote

# 6. Set the IP-hashing salt as a Worker secret. Use any random string; this
#    one combines with a YYYYMM bucket inside the Worker so listener hashes
#    rotate monthly automatically.
#
#    NOTE: rotating IP_SALT itself (the deployment-time secret) is a future
#    cron task — for now we set it once and rely on the in-Worker monthly
#    bucket. Cross-month listener linkability is broken automatically; the
#    deployment salt stays the same until you re-run this command.
npx wrangler secret put IP_SALT
# (paste a long random string, e.g. `openssl rand -hex 32`)

# 7. Local dev. The Worker binds to http://localhost:8787.
npm run dev
# In another terminal:
curl -i "http://localhost:8787/p/biomedical-agentic-ai/u/test/2026-05-01-ablatecell-virtual-cell-repos.mp3"
curl -I "http://localhost:8787/p/biomedical-agentic-ai/u/test/2026-05-01-ablatecell-virtual-cell-repos.mp3"
# Expect 302 with a `location:` header pointing at the GitHub raw URL.
# Expect a row to appear in local D1: `npx wrangler d1 execute podcast --command "SELECT * FROM requests;"`

# 8. Deploy.
npm run deploy
# Note the printed `*.workers.dev` URL — looks like
# `https://podcast.<your-subdomain>.workers.dev`.
# This is the URL that goes into the `update_feed_for_worker.py` --worker-url
# flag when rewriting feed.xml enclosures.
```

## After deployment

Rewrite each show's `feed.xml` to point at the Worker:

```bash
# from repo root
python3 scripts/update_feed_for_worker.py \
  --worker-url https://podcast.<your-subdomain>.workers.dev \
  --podcast biomedical-agentic-ai \
  --user-id andrew \
  --feed podcasts/biomedical-agentic-ai/feed.xml \
  --dry-run

# remove --dry-run to write the change
```

`--user-id` is currently a single value per feed (one canonical feed per show).
When you start generating per-listener feeds, vary `--user-id` per output file
and write to `podcasts/<slug>/feed-<user>.xml`.

## Allowed podcasts

`wrangler.toml` lists podcasts the Worker will serve under `[vars]
ALLOWED_PODCASTS`. Adding a podcast = add the slug to the comma-separated list,
redeploy. Unknown slugs get 404 without hitting D1.

## Querying analytics

`queries.sql` has a starter set of useful queries. Run any of them with:

```bash
npx wrangler d1 execute podcast --remote --command "<sql>"
# or
npx wrangler d1 execute podcast --remote --file=./queries.sql
```

Analytics Engine is also written to (binding `AE`, dataset `podcast_requests`)
for long-term aggregates. Use the Cloudflare GraphQL API or the dashboard for
those queries — D1 is the right place for ad-hoc point-in-time questions, AE
for trends across months/years.

## Storage

Right now the Worker redirects to `${GITHUB_REPO_RAW}/podcasts/<slug>/episodes/<ep>.mp3`.
When audio moves to R2, only `resolveTarget()` in `src/index.ts` changes (the
sketch is commented in place). Enclosure URLs in feeds stay stable across the
swap because they point at the Worker, not at storage.
