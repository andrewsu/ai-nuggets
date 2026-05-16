# Production pipeline (shared)

This file documents the production mechanics shared by every podcast under
`podcasts/<slug>/`. The runner (`scripts/run_all_shows.sh`) prepends it to
each show's `PROMPT.md` before piping to Claude. Each show's PROMPT.md
specifies its slug, audience, search strategy, episode format, script
filename convention, and commit-message prefix; this file handles
everything after the script content has been written.

## Source-level failures during search

Individual search sources fail transiently — arXiv rate-limits the API
(HTTP 429), bioRxiv has had brief 5xx windows, news sites occasionally
return errors from a given IP. **A single failed source must not abort
the run.**

- One quick retry after a short pause (≈30s) is fine if the failure looks
  transient. Do not sit in a long retry loop — that burns the cron window
  and ships no episode.
- If the source is still failing after the retry, **proceed with the
  remaining sources** and ship the best candidate from what you have.
  The other sources almost always carry the day's nugget; missing one of
  three or four is a small recall hit, not a reason to skip the day.
- In the candidate funnel (logged at end of run), explicitly record which
  source(s) failed and how. Example: `arXiv — HTTP 429 from this IP, one
  retry also 429, skipped`. This makes the gap auditable.
- Skipping the day is reserved for the case where the *content* bar isn't
  met (no fresh candidates after surveying available sources), not for
  source-side outages.

## Writing for audio

The script will be read aloud — write for the ear, not the eye. Things that
look fine on a page can be useless or actively annoying when spoken.

- **Never read out DOIs, arXiv IDs, or URLs.** They are noise in audio and
  the link is in the show notes anyway. Drop them entirely from the script.
- **No tables, bullet lists, or markdown structure in the spoken portion.**
  Use prose with natural transitions ("first", "the second thing", "one
  caveat").
- **Spell out or rephrase anything that's hard to say.** Greek letters,
  unusual symbols, chemical formulas, alphanumeric identifiers, ticker
  symbols, dollar amounts — read them the way a human would say them, not
  the way they're typed.

Individual shows may add their own audio conventions in their PROMPT.md.

## Paper-link URLs (show notes / `Paper link:` lines)

`bioRxiv` uses two DOI prefixes — `10.1101/` for legacy posts and
`10.64898/` for newer posts (the cutover is recent). The prefix is part of
the URL path: `https://www.biorxiv.org/content/<prefix>/<id>v<n>`. Use
**the exact prefix the bioRxiv API returns for that DOI** — never
hardcode `10.1101/`. A wrong prefix yields a real-looking URL that 404s.

The pre-commit hook (`.githooks/check-paper-urls.py`) hits the bioRxiv
details API and `arxiv.org/abs/` for every new preprint URL in the staged
diff and fails the commit if any returns "not found". Set
`GUIDE_SKIP_URL_CHECK=1` to bypass (offline only).

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

