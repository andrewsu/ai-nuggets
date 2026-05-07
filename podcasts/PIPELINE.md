# Production pipeline (shared)

This file documents the production mechanics shared by every podcast under
`podcasts/<slug>/`. The runner (`scripts/run_all_shows.sh`) prepends it to
each show's `PROMPT.md` before piping to Claude. Each show's PROMPT.md
specifies its slug, audience, search strategy, episode format, script
filename convention, and commit-message prefix; this file handles
everything after the script content has been written.

## TTS & distribution

Voice config lives in each show's `show.toml`:

- **Primary:** Mistral `voxtral-mini-tts-2603` / `en_paul_neutral` (Paul Neutral)
- **Fallback:** ElevenLabs Bella (`hpp4J3VqNfWAUOO0d1Us`) / `eleven_flash_v2_5`

API keys in `.env` at repo root (`MISTRAL_API_KEY`, `ELEVENLABS_API_KEY`).

Don't write your own TTS code. `gen_tts.py` is the canonical pipeline:
chunking, ffmpeg stitching, duration sanity check, primary→fallback
orchestration, all already handled.

Public RSS URL pattern: subscribers fetch
`https://raw.githubusercontent.com/andrewsu/ai-nuggets/main/podcasts/<slug>/feed.xml`.
Episode mp3 enclosures are served via the `podcast` Cloudflare Worker so
downloads are logged centrally. See `worker/README.md` for setup.

## Per-episode steps

Repeat for each episode the show produces today. `<slug>` is the show's
slug; `<basename>` is the episode basename (no `.mp3`).

1. **Write the script** to `podcasts/<slug>/scripts/<basename>.<ext>` per
   the show's filename + heading convention (defined in its PROMPT.md).

2. **Generate the audio:**
   ```
   python3 gen_tts.py --show <slug> \
     podcasts/<slug>/scripts/<basename>.<ext> \
     podcasts/<slug>/episodes/<basename>.mp3
   ```
   If the script exits non-zero, investigate and fix the root cause — do
   NOT commit partial output.

3. **Publish the audio to R2** so the Worker can serve it directly:
   ```
   scripts/publish_episode.sh <slug> <basename>
   ```
   (omit the `.mp3` suffix). The script wraps `wrangler r2 object put` and
   uploads to the `ai-nuggets-episodes` bucket configured in
   `worker/wrangler.toml`. If it fails, fix the error before committing —
   the feed will reference a key that doesn't exist in R2 and listeners
   will fall back to GitHub raw (only works while mp3s are still
   committed; see footnote).

4. **Add a new `<item>`** to `podcasts/<slug>/feed.xml`, immediately after
   the opening channel metadata and before the existing items. Use the
   actual byte size of the generated mp3 for `enclosure length` and the
   rounded duration from `ffprobe` for `itunes:duration`. Keep enclosure
   URLs pointing at the Worker
   (`https://podcast.<sub>.workers.dev/p/<slug>/u/<user>/<basename>.mp3`).
   Keep the RSS feed valid XML — escape `&` → `&amp;`, `<` → `&lt;`, `>` →
   `&gt;` in every title, description, and summary. The
   `.githooks/pre-commit` hook will reject the commit if the feed doesn't
   parse, but catch it yourself first. Write guids as
   `<guid isPermaLink="false"><basename></guid>` — bare basenames without
   `isPermaLink="false"` violate RSS 2.0 and break strict podcast clients.

## Commit and push

After all of today's episodes are generated, audio published to R2, and
the feed updated:

```
git add -A && git commit -m '<commit-prefix>: <descriptive title>' && git push
```

`<commit-prefix>` is set per-show in its PROMPT.md.

## Re-invocation within the same day

The runner can be triggered manually mid-day (for testing, or to add a
bonus episode). If `podcasts/<slug>/scripts/YYYY-MM-DD-*` already exists
for today, you are in a re-invocation. The search and selection process
is **exactly the same** as the first run — same sources, same recency
filter, same audience criteria — with **one** exception: do not pick an
article that has already been featured in a shipped episode today.

Do not widen the recency window or shift the source mix to "find
something different." If after excluding today's already-shipped items
there are no fresh candidates left, the right outcome is no second
episode for the day.

## Final summary (logged to cron.log)

The runner pipes Claude's stdout into `podcasts/<slug>/logs/cron.log`, so
the final response is a permanent audit record of the run. Make it useful
for retrospective review.

After the commit/push line, print the **candidate funnel** that fed today's
selection:

- Per source (bioRxiv / arXiv / general web / press feeds — whichever the
  show's PROMPT.md specifies), report how many items were scanned and how
  many survived the relevance filter.
- List the substantive shortlist **after** discarding spurious keyword
  matches (e.g., "agent" → "chemical agent", "LLM" inside an unrelated
  word). Title + URL per item, one line each.
- Mark which one was chosen for today's episode (and for shows that pick
  multiple items, mark all that were chosen).

This makes it possible to audit, weeks later, what was on the table and
why the picked item beat the others. Keep it terse — bullet list, no
prose summary of each candidate.

## R2 cutover footnote

While we're in the R2 cutover, mp3s are still committed to git as a safety
net (the Worker falls back to GitHub raw if R2 lacks the object). Once R2
is verified end-to-end, mp3s will be excluded from git and only uploaded
to R2 — this file will be updated when that switch happens.

---
