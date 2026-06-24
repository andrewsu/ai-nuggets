# Adding a new show

Step-by-step checklist for adding a new podcast to an **already-running**
ai-nuggets deployment. If you are setting up the infrastructure from scratch
(Cloudflare account, cron, API keys), start with [SETUP.md](SETUP.md) first.

The daily runner (`scripts/run_all_shows.sh`) auto-discovers any directory
under `podcasts/` that contains a `PROMPT.md`. You do **not** need to edit
cron or the runner to add a show.

## 1. Scaffold

```bash
python3 scripts/new_show.py my-new-show \
  --title "My New Show" \
  --description "What this show is about" \
  --owner "Owner Name <email@example.com>"
```

The slug (`my-new-show`) is lowercase, hyphen-separated. It is used as:

- the directory name under `podcasts/`
- the path segment in Worker URLs (`/p/<slug>/...`)
- the `--show` flag for `gen_tts.py`

This creates `podcasts/my-new-show/` with `show.toml`, `PROMPT.md`,
`README.md`, an empty `feed.xml` skeleton, and empty `episodes/`,
`scripts/`, and `logs/` directories.

## 2. Customize the editorial brief

Edit `podcasts/my-new-show/PROMPT.md`. The template has five sections to
fill in:

- **Audience** — who this is for, what they care about, what to avoid.
- **Search strategy** — which sources, queries, recency window. Be
  specific (`bioRxiv neuroscience`, `arXiv cs.AI`, `Endpoints News`,
  etc.); vague briefs produce vague episodes.
- **Format** — length, tone, structure of the script.
- **TTS & distribution** — usually no edits needed; defaults pull from
  `show.toml`.
- **Daily execution** — usually no edits needed; the script-naming and
  feed-update conventions are inherited from `podcasts/PIPELINE.md`.

If the show has its own audio conventions on top of those in `PIPELINE.md`
(e.g., "always pronounce CRISPR as 'crisper'"), add them to PROMPT.md.

Also set the commit-message prefix the runner should use (e.g.,
`Episode: My New Show —`). PIPELINE.md references `<commit-prefix>`; the
show's PROMPT.md is where that value is defined.

## 3. Pick a TTS voice

The scaffold defaults to self-hosted Voxtral on Garibaldi (`neutral_male`,
1.2× speed) with a Mistral-API fallback — same config every production
show currently uses. To change voices, edit the `voice` field in
`[tts.primary]` of `podcasts/my-new-show/show.toml`.

### Voxtral voice presets

Voxtral ships 20 voices inside the model repo. The five
language-neutral ones we use most have audio samples committed at
`hpc/voice-samples/` so you can preview before committing to one:

| voice id            | sample                                                                                       |
|---------------------|----------------------------------------------------------------------------------------------|
| `neutral_male`      | https://github.com/andrewsu/ai-nuggets/raw/main/hpc/voice-samples/neutral_male.mp3 (default) |
| `neutral_female`    | https://github.com/andrewsu/ai-nuggets/raw/main/hpc/voice-samples/neutral_female.mp3         |
| `casual_male`       | https://github.com/andrewsu/ai-nuggets/raw/main/hpc/voice-samples/casual_male.mp3            |
| `casual_female`     | https://github.com/andrewsu/ai-nuggets/raw/main/hpc/voice-samples/casual_female.mp3          |
| `cheerful_female`   | https://github.com/andrewsu/ai-nuggets/raw/main/hpc/voice-samples/cheerful_female.mp3        |

Voxtral also ships per-language presets (`ar_male`, `de_{male,female}`,
`es_{male,female}`, `fr_{male,female}`, `hi_{male,female}`,
`it_{male,female}`, `nl_{male,female}`, `pt_{male,female}`) — these
don't have samples committed; preview at
https://huggingface.co/spaces/mistralai/voxtral-tts-demo.

To switch voices, edit `[tts.primary]` only — leave the Mistral
fallback alone:

```toml
[tts.primary]
provider = "voxtral"
model    = "mistralai/Voxtral-4B-TTS-2603"
voice    = "casual_female"   # ← change this
speed    = 1.2
```

Note: the Mistral-API fallback uses its own voice catalog (`en_paul_neutral`,
etc.) — see https://docs.mistral.ai/. Don't put a Voxtral preset id in
`[tts.fallback]` or a Mistral voice id in `[tts.primary]`.

`gen_tts.py` is the canonical pipeline — do not write your own TTS code.

## 4. Allow the slug on the Worker

Add the slug to `ALLOWED_PODCASTS` in `worker/wrangler.toml`:

```toml
[vars]
ALLOWED_PODCASTS = "biomedical-agentic-ai,calibr-briefing,my-new-show"
```

Redeploy:

```bash
cd worker && npm run deploy
```

Unknown slugs get a plain 404 from the Worker, so **do this before the
first episode runs** — otherwise listeners will hit 404s on the
enclosure URL.

## 5. Manual smoke test

Before letting cron run unattended overnight, run the show once by hand
to verify end-to-end:

```bash
cat podcasts/PIPELINE.md podcasts/my-new-show/PROMPT.md \
  | claude -p --permission-mode auto \
  | tee podcasts/my-new-show/logs/cron.log
```

Confirm that:

- A script appears under `podcasts/my-new-show/scripts/YYYY-MM-DD-*.md`.
- An mp3 appears under `podcasts/my-new-show/episodes/YYYY-MM-DD-*.mp3`
  with non-zero duration (`ffprobe` it).
- The mp3 was uploaded to R2 (`scripts/publish_episode.sh` ran cleanly).
- A new `<item>` is appended to `podcasts/my-new-show/feed.xml` with a
  Worker URL in the `<enclosure>`.
- The commit landed on `main` with the expected prefix.
- `curl -I "https://podcast.<sub>.workers.dev/p/my-new-show/u/<listener>/YYYY-MM-DD-foo.mp3"`
  returns 200 (R2 hit). 404 means either the Worker doesn't recognize the
  slug (recheck step 4) or the R2 upload didn't land (re-run
  `scripts/publish_episode.sh`).

If anything is wrong, fix it before the cron picks it up the next morning.

## 6. Subscriber URL

The default feed at
`https://raw.githubusercontent.com/<your-fork>/ai-nuggets/main/podcasts/my-new-show/feed.xml`
has enclosures pointing at the Worker with a single `--user-id` already
baked in by `new_show.py`'s default (or by whichever `--user-id` you used
the first time you ran `update_feed_for_worker.py`).

For a single listener, send them that URL. For multiple listeners on the
same show with **distinct** download analytics, mint per-listener feed
variants:

```bash
python3 scripts/update_feed_for_worker.py \
  --worker-url https://podcast.<sub>.workers.dev \
  --podcast my-new-show \
  --user-id alice \
  --feed podcasts/my-new-show/feed-alice.xml
```

Commit the per-listener `feed-*.xml` files and share each URL with the
matching listener. The Worker's D1 logs will tag every request with the
`user_id` from the URL.

## 7. Update the top-level Shows table

Add a row to the `## Shows` table in the repo-root [README.md](README.md)
so the new show is visible in the repo listing.

## 8. Done

The next cron run (4 AM PT by default) will produce the first automated
episode. Watch `podcasts/my-new-show/logs/cron.log` the next morning to
verify the unattended run worked.
