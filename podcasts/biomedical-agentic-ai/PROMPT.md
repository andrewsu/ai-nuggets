You are creating a personalized podcast called "Biomedical Agentic AI" (slug:
`biomedical-agentic-ai`). It lives under `podcasts/biomedical-agentic-ai/` in
the `ai-nuggets` repo.

# 1. Audience

Andrew Su — computational biologist at Scripps Research (Su Lab). Works on
biomedical knowledge graphs, Wikidata, open data/open science. Bioinformatics,
data integration, APIs.

## What he likes

- Agentic AI applied to biomedical research
- AI for knowledge graphs, ontologies, data integration
- Novel tools/frameworks for scientific automation
- Open science + AI intersections
- Anything relevant to a lab that builds and maintains biomedical databases

## What to avoid

- (none yet — will update based on feedback)

## Past feedback

- 2026-03-17: Andrew requested systematic bioRxiv/arXiv searching alongside
  general web search. Don't ignore big non-academic news though.

# 2. Search strategy

Always cast a wide net across THREE source types (do not skip any):

1. **bioRxiv** — Search for recent preprints (last 2 days) in relevant
   categories (bioinformatics, genomics, systems biology, pharmacology). Try
   queries like "agent", "LLM", "foundation model", "autonomous", "multi-agent".
   Use `https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}` or
   web search with `site:biorxiv.org`.
2. **arXiv** — Recent papers in cs.AI, cs.CL, q-bio, cs.MA with
   biomedical/scientific relevance. Use web search with `site:arxiv.org` or
   the arXiv API.
3. **General web** — big AI + science news that may NOT be in preprints:
   major company announcements (DeepMind, NVIDIA, OpenAI), Nature/Science
   publications, policy developments, funding news, open-source tool releases.

The best nugget might come from ANY of these sources. Don't bias toward
preprints if the biggest story of the day is a product launch or a Nature
paper. But don't miss important preprints because a flashy announcement is
easier to find.

# 3. Format

- Pick ONE best article → full podcast episode + text summary in Telegram.
- Then list up to 3 more relevant headlines (with links) in the same
  Telegram message.
- **CRITICAL:** every headline MUST have a real, verified URL that you
  actually found during search. Do NOT fabricate or guess URLs. If you can't
  find 3 real articles, include fewer. Zero fake links is better than one.
- Andrew may request podcast episodes or written summaries for those extras.
- 3–5 sentences for the main summary; punchy, opinionated, not generic.

# 4. TTS & distribution

Voice config lives in `show.toml`:

- **Primary:** Mistral `voxtral-mini-tts-2603` / `en_paul_neutral` (Paul Neutral)
- **Fallback:** ElevenLabs Bella (`hpp4J3VqNfWAUOO0d1Us`) / `eleven_flash_v2_5`

API keys in `.env` at repo root (`MISTRAL_API_KEY`, `ELEVENLABS_API_KEY`).

Don't write your own TTS code. `gen_tts.py` is the single canonical pipeline:
chunking, ffmpeg stitching, duration sanity check, primary→fallback
orchestration, all already handled.

Public RSS URL (subscriber-facing): the root `feed.xml` symlink points here.
Episode mp3 enclosures are served via the `podcast` Cloudflare Worker so
downloads are logged centrally. See `worker/README.md` for the Worker setup.

---

# 5. Daily execution

Run this every day from the repo root.

## Step 1: gather candidates

Perform ALL three searches (do not skip any):

1. **BIORXIV:** `site:biorxiv.org` + terms like "AI agent", "LLM",
   "foundation model", "autonomous", "multi-agent" in
   bioinformatics/genomics/pharmacology. Also try the bioRxiv API:
   `curl 'https://api.biorxiv.org/details/biorxiv/YYYY-MM-DD/YYYY-MM-DD'`
   (yesterday and today).
2. **ARXIV:** `site:arxiv.org` + biomedical AI terms. Focus on cs.AI,
   cs.CL, q-bio, cs.MA with scientific applications.
3. **GENERAL WEB:** recent news (last 1–2 days) on agentic AI applied to
   biomedical research, drug discovery, genomics, clinical trials, and
   notable broader AI agent developments (frameworks, benchmarks, tools,
   policy, major company announcements).

## Step 2: pick + summarize

Pick ONE best item from the combined candidate set. Write a punchy 3–5
sentence summary — why it matters, what's novel. Include a link. Be
opinionated. Then add a `More headlines:` section with up to 3 additional
real, verified links (skip if nothing else is genuinely interesting).

## Step 3: produce the episode

1. Write the script to:
   ```
   podcasts/biomedical-agentic-ai/scripts/YYYY-MM-DD-slug.md
   ```
   The file must contain a `## Script` heading; everything after that heading
   (minus `Paper link:` lines) is what gets spoken.

2. Generate the audio:
   ```
   python3 gen_tts.py --show biomedical-agentic-ai \
     podcasts/biomedical-agentic-ai/scripts/YYYY-MM-DD-slug.md \
     podcasts/biomedical-agentic-ai/episodes/YYYY-MM-DD-slug.mp3
   ```
   If the script exits non-zero, investigate and fix the root cause — do NOT
   commit partial output.

3. Update `podcasts/biomedical-agentic-ai/feed.xml` by inserting a new
   `<item>` immediately after the opening channel metadata and before the
   existing items. Use the actual byte size of the generated mp3 for
   `enclosure length` and the rounded duration from `ffprobe` for
   `itunes:duration`. Keep enclosure URLs pointing at the Worker
   (`https://podcast.<sub>.workers.dev/p/biomedical-agentic-ai/u/<user>/<slug>.mp3`).
   Keep the RSS feed valid XML — escape `&` → `&amp;`, `<` → `&lt;`, `>` →
   `&gt;` in every title, description, and summary. The `.githooks/pre-commit`
   hook will reject the commit if the feed doesn't parse, but catch it
   yourself first. Write guids as
   `<guid isPermaLink="false">YYYY-MM-DD-slug</guid>` — bare slugs without
   `isPermaLink="false"` violate RSS 2.0 and break strict podcast clients.

4. Commit and push:
   ```
   git add -A && git commit -m 'Episode: <title>' && git push
   ```
