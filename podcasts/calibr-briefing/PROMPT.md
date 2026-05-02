You are creating a personalized podcast called "Calibr-Skaggs Daily Briefing"
(slug: `calibr-briefing`). It lives under `podcasts/calibr-briefing/` in the
`ai-nuggets` repo.

# 1. Audience

Travis Young at Calibr-Skaggs, Scripps Research.

## What he likes

Daily biotech/pharma briefings with explicit connections to the Calibr
pipeline. Two episodes per day:

1. **Headlines** (~3 min) — Top biotech/pharma news of the day, quick
   roundup.
2. **Spotlight** (~5–8 min) — Deep dive on the single most important
   development from focus areas or headlines. Thorough analysis: what
   happened, why it matters, competitive landscape, and explicit connections
   to the Calibr pipeline. Don't spread thin across multiple topics — go
   deep on one.

## Focus areas

- **In Vivo CAR-T** — new approaches, publications, newcos, clinical data.
  Relevant to Calibr's sCAR-T program (CLBR001 + SWI019, Phase 1 with AbbVie
  for B-cell lymphoma, solid tumors, autoimmune).
- **MASH / FGF21** — clinical trial data, publications, announcements.
  Relevant to Calibr's MASH biologic (dual-acting, multiple receptors,
  IND-enabling). Track efruxifermin (Akero), efimosfermin (BOS-580/GSK),
  resmetirom, and combination therapy approaches.
- **General therapeutic development** — major deals, clinical readouts, FDA
  actions, new company launches.

## Calibr pipeline reference

Full pipeline details and therapeutic targets live in
`memory/calibr-pipeline.md` in the workspace (not in this repo).

## What to avoid

- (none yet — will update based on feedback)

# 2. Search strategy

Headlines sources:

- Fierce Biotech
- Endpoints News
- STAT News
- BioPharma Dive
- Fierce Pharma

For the spotlight, pick the single most important development. Pull
publications, press releases, and trial data as needed.

# 3. Format

- Real, verified URLs only — never fabricate.
- Both episodes are spoken by Nigel.
- Headlines: punchy, numbered, quick.
- Spotlight: deep, analytical, with explicit Calibr-pipeline connections.

# 4. TTS & distribution

Voice config lives in `show.toml`:

- **Primary:** Mistral `voxtral-mini-tts-2603` / `en_paul_neutral` (Paul Neutral)
- **Fallback:** ElevenLabs Bella (`hpp4J3VqNfWAUOO0d1Us`) / `eleven_flash_v2_5`

API keys in `.env` at repo root (`MISTRAL_API_KEY`, `ELEVENLABS_API_KEY`).

Don't write your own TTS code. `gen_tts.py` is the canonical pipeline.

Public RSS URL: subscribers fetch
`https://raw.githubusercontent.com/andrewsu/ai-nuggets/main/podcasts/calibr-briefing/feed.xml`.
Episode mp3 enclosures are served via the `podcast` Cloudflare Worker so
downloads are logged centrally. See `worker/README.md` for setup.

---

# 5. Daily execution

Run this every weekday from the repo root.

## Step 1: gather candidates

Search the headlines sources above (Fierce Biotech, Endpoints, STAT,
BioPharma Dive, Fierce Pharma) plus general web for the last 24 hours.
Identify items in the focus areas (In Vivo CAR-T, MASH/FGF21, general
therapeutic development) and rank by importance.

## Step 2: produce TWO episodes

### Headlines episode (~3 min)

1. Write the script to:
   ```
   podcasts/calibr-briefing/scripts/YYYY-MM-DD-pharma-headlines.txt
   ```
   No `## Script` heading — just the spoken text.

2. Generate audio:
   ```
   python3 gen_tts.py --show calibr-briefing \
     podcasts/calibr-briefing/scripts/YYYY-MM-DD-pharma-headlines.txt \
     podcasts/calibr-briefing/episodes/YYYY-MM-DD-pharma-headlines.mp3
   ```

### Spotlight episode (~5–8 min)

1. Pick the single most important story. Write the script to:
   ```
   podcasts/calibr-briefing/scripts/YYYY-MM-DD-<topic>-spotlight.txt
   ```

2. Generate audio:
   ```
   python3 gen_tts.py --show calibr-briefing \
     podcasts/calibr-briefing/scripts/YYYY-MM-DD-<topic>-spotlight.txt \
     podcasts/calibr-briefing/episodes/YYYY-MM-DD-<topic>-spotlight.mp3
   ```

## Step 3: update feed and commit

Add new `<item>` entries to `podcasts/calibr-briefing/feed.xml` (newest
first) with real byte sizes and ffprobe durations. Keep enclosure URLs
pointing at the Worker
(`https://podcast.<sub>.workers.dev/p/calibr-briefing/u/<user>/<slug>.mp3`).
Escape `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;` in every title,
description, and summary. The `.githooks/pre-commit` hook will reject the
commit if the feed doesn't parse, but catch it yourself first.

```
git add -A && git commit -m 'Calibr: <headline + spotlight titles>' && git push
```
