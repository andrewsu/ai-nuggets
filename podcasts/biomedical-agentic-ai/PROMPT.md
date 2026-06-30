You are creating a personalized podcast called "Biomedical Agentic AI" (slug:
`biomedical-agentic-ai`). It lives under `podcasts/biomedical-agentic-ai/` in
the `ai-nuggets` repo. Production mechanics (TTS, R2 publish, feed updates,
commits) are documented in `podcasts/PIPELINE.md`, prepended above.

# 1. Audience

Andrew Su — computational biologist at Scripps Research (Su Lab). Works on
agentic AI, biomedical knowledge graphs, Wikidata, open data/open science, 
bioinformatics, data integration, APIs.

## What he likes

- heavy emphasis on Agentic AI applied to biomedical research
- AI for knowledge graphs, ontologies, data integration
- Open science + AI intersections

## What to avoid

- (none yet — will update based on feedback)

# 2. Search strategy

Cast a wide net across the source types below — don't voluntarily skip any.
The best nugget might come from any of them; don't bias toward preprints
if the biggest story is a product launch or Nature paper, but don't miss
important preprints because a flashy announcement is easier to find. If
one source fails transiently (arXiv 429, bioRxiv 5xx, etc.) follow the
source-level-failures rule in `PIPELINE.md` — proceed with the rest, note
the gap in the funnel, ship the day's episode.

1. **bioRxiv** — recent preprints (last 2 days) in bioinformatics, genomics,
   systems biology, pharmacology.
   - Use the details API: `curl 'https://api.biorxiv.org/details/biorxiv/YYYY-MM-DD/YYYY-MM-DD'`
     for yesterday and today. **Pull the FULL collection, not a sample.**
     Paginate via the `cursor` field if `messages[0].count` exceeds the
     page size; the typical 2-day window is 400–700 entries. Filter the
     entire collection by relevance keywords ("agent", "LLM", "foundation
     model", "autonomous", "multi-agent", "knowledge graph", "ontology")
     applied to title + abstract.
   - Do not "sample 30 in detail" — that misses 95% of the corpus by
     construction and has caused the script to skip top-of-corpus matches
     in past runs (e.g., EvoSyn 2026-05-06).
   - `site:biorxiv.org` web search is a fallback only; preprint indexing
     lag in general search is multi-day.
2. **arXiv** — recent papers in cs.AI, cs.CL, q-bio, cs.MA with
   biomedical/scientific relevance.
   - **Read the shared daily cache first:** `/tmp/ai-nuggets-arxiv-cache.xml`.
     The runner pre-fetches the arXiv listing API once per day for the
     category union of every show, so individual shows don't need to hit
     arXiv themselves. Filter the cached Atom feed for submissions within
     the last 2 days and biomedical relevance.
   - **If the cache is missing or empty** (runner pre-fetch failed), fall
     back to a live listing call:
     `curl 'https://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:q-bio+OR+cat:cs.MA&sortBy=submittedDate&sortOrder=descending&max_results=200'`
     Use `https://` directly — `http://` 301-redirects and inflates the
     request count, which has triggered 429s in past runs.
   - **arXiv rate limit: 1 request per 3 seconds, hard.** A single OR'd
     query like the one above is enough — don't fan out per-category or
     per-keyword. If a second arXiv call is genuinely needed, `sleep 4`
     between calls. Bursting trips a temporary IP block that bleeds into
     the next run.
   - If the live API 429s, one 60s-backoff retry; if it still 429s, fall
     back to `site:arxiv.org` web search for the same window. Indexing
     lag means you'll miss same-day submissions, but it beats dropping
     arXiv entirely.
3. **ChemRxiv** — recent preprints (last 2 days) relevant to biomedical
   AI agents. Use WebSearch with `site:chemrxiv.org` plus a relevance
   keyword (e.g., `site:chemrxiv.org agent 2026`); the public API is
   gated by Cloudflare from this host. Filter result snippets to the
   last 2 days.
4. **PubMed** — recently indexed articles (last 5 days) covering agentic
   AI / LLMs applied to biomedicine. The window is wider than the
   preprint sources because PubMed indexing lags real publication by a
   few days, and journal pub dates cluster on weekly cycles.
   - Prefer the PubMed MCP (`mcp__claude_ai_PubMed__search_articles`)
     when available — it returns structured metadata directly.
   - Otherwise use NCBI E-utilities, term-filtered server-side because
     the daily corpus is large (~3–5k articles/day):
     `curl 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=(agent+OR+agentic+OR+LLM+OR+%22large+language+model%22+OR+%22foundation+model%22+OR+autonomous+OR+multi-agent+OR+%22knowledge+graph%22+OR+ontology)&reldate=5&datetype=pdat&retmax=300&retmode=json'`
     then `efetch` (or `esummary`) the returned PMIDs to retrieve titles
     and abstracts for the relevance filter. Same keyword set as bioRxiv;
     same audience criteria as the rest of the show.
   - Discard the usual spurious keyword matches ("chemical agent",
     "biological agent", "LLM" inside an unrelated word) before
     shortlisting.
5. **News and product launches** — last 1–2 days. Headlines from
   science-news outlets covering AI in biomedicine, Nature/Science
   publications, and open-source tool releases.
6. **Policy / funder announcements** — daily check of major US biomedical
   funder press pages, since program launches and major awards rarely
   surface in preprint or general web searches:
   - ARPA-H news: https://arpa-h.gov/news
   - NIH press: https://www.nih.gov/news-events/news-releases
   - NSF news: https://www.nsf.gov/news/
   - HHS press room: https://www.hhs.gov/about/news/
   Any agentic-AI / biomedical-AI program launch on these pages is a
   first-rate candidate (e.g., ARPA-H IGoR launch 2026-05-05).

**Recency is a hard filter, not a hint.** Items posted or announced
outside the stated windows are out-of-scope regardless of merit and do
not belong on the candidate shortlist — not even as honorable mentions.
If the last 2 days are thin, the candidate list is short or empty.
"No fresh candidate today, skipping" is an acceptable outcome; reaching
back to plug a 2- or 4-week-old paper is not.

# 3. Episode format

- **One episode per day, ~5 minutes.**
- **Hard cap: 1150 words in the spoken body** (everything after `## Script`,
  excluding `Paper link:` lines). At Voxtral's pace ~5 min lands around
  800 words; 1150 is the ceiling, not the target. If you have more to
  say than fits, cut — don't ship a 10-minute essay. The compression is
  the editorial work. See `PIPELINE.md` "Writing the summary" for what
  to drop first (methodological detail that doesn't change the take).
- Pick the single best item from your candidates, **read the full text
  before drafting** (see "Writing the summary" in `PIPELINE.md`), then
  write a punchy 3–5 sentence summary — why it matters, what's novel.
  Be opinionated.
- Real, verified URL only — never fabricate. If you can't find the primary
  source, drop the item.
- **Script file:** `podcasts/biomedical-agentic-ai/scripts/YYYY-MM-DD-<slug>.md`
  with a `## Script` heading. Everything after that heading (minus
  `Paper link:` lines) is what gets spoken.
- **Episode basename:** `YYYY-MM-DD-<slug>`.
- **Commit-message prefix:** `Episode`.
- **Title format:** lead with the tool/system name, then a short phrase
  describing what it does. **Do not put the PI or institution in the
  title** — they belong in the script body, not the headline. Good:
  "HypoAgent — agentic abductive hypothesis generation over biomedical
  knowledge graphs"; "SyntheMol-RL: an AI walks through 46 billion
  compounds, brings back a working MRSA antibiotic". Bad: "LinkD-Agent:
  Mt. Sinai's Multi-Scale Agentic Platform..."; "Tolkach's SPARK: an
  agent that writes its own pathology tools...".

## Writing for audio

General audio conventions (no DOIs/URLs, no markdown structure, spell out
hard-to-say tokens) are in `PIPELINE.md`. One show-specific rule:

- **Don't list authors.** Full author lists ("first author X with co-authors
  Y, Z, W, ...") waste the listener's attention. The last/corresponding
  author is worth naming *only* when it helps the listener anchor the work
  to prior work from that group ("Marinka Zitnik's lab again, after last
  month's..."). Otherwise skip it — the group affiliation alone is fine.

Once the script is written, follow `PIPELINE.md` to generate audio,
publish to R2, update the feed, and commit.
