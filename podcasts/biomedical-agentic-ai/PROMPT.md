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

Cast a wide net across THREE source types — do not skip any. The best nugget
might come from any of them; don't bias toward preprints if the biggest
story is a product launch or Nature paper, but don't miss important
preprints because a flashy announcement is easier to find.

1. **bioRxiv** — recent preprints (last 2 days) in bioinformatics, genomics,
   systems biology, pharmacology. Try queries like "agent", "LLM",
   "foundation model", "autonomous", "multi-agent". Use the bioRxiv API
   (`curl 'https://api.biorxiv.org/details/biorxiv/YYYY-MM-DD/YYYY-MM-DD'`,
   yesterday and today) or web search with `site:biorxiv.org`.
2. **arXiv** — recent papers in cs.AI, cs.CL, q-bio, cs.MA with
   biomedical/scientific relevance. Use `site:arxiv.org` or the arXiv API.
3. **General web** — last 1–2 days. Big AI + science news that may NOT be
   in preprints: major company announcements (DeepMind, NVIDIA, OpenAI),
   Nature/Science publications, policy developments, funding news,
   open-source tool releases.

**Recency is a hard filter, not a hint.** Items posted or announced
outside the stated windows are out-of-scope regardless of merit and do
not belong on the candidate shortlist — not even as honorable mentions.
If the last 2 days are thin, the candidate list is short or empty.
"No fresh candidate today, skipping" is an acceptable outcome; reaching
back to plug a 2- or 4-week-old paper is not.

# 3. Episode format

- **One episode per day, ~5 minutes.**
- Pick the single best item from your candidates. Write a punchy 3–5
  sentence summary — why it matters, what's novel. Be opinionated.
- Real, verified URL only — never fabricate. If you can't find the primary
  source, drop the item.
- **Script file:** `podcasts/biomedical-agentic-ai/scripts/YYYY-MM-DD-<slug>.md`
  with a `## Script` heading. Everything after that heading (minus
  `Paper link:` lines) is what gets spoken.
- **Episode basename:** `YYYY-MM-DD-<slug>`.
- **Commit-message prefix:** `Episode`.

## Writing for audio

The script will be read aloud — write for the ear, not the eye. Things that
look fine on a page can be useless or actively annoying when spoken.

- **Never read out DOIs, arXiv IDs, or URLs.** They are noise in audio and
  the link is in the show notes anyway. Drop them entirely from the script.
- **Don't list authors.** Full author lists ("first author X with co-authors
  Y, Z, W, ...") waste the listener's attention. The last/corresponding
  author is worth naming *only* when it helps the listener anchor the work
  to prior work from that group ("Marinka Zitnik's lab again, after last
  month's..."). Otherwise skip it — the group affiliation alone is fine.
- **No tables, bullet lists, or markdown structure in the spoken portion.**
  Use prose with natural transitions ("first", "the second thing", "one
  caveat").
- **Spell out or rephrase anything that's hard to say.** Greek letters,
  unusual symbols, chemical formulas, alphanumeric identifiers — read them
  the way a human would say them, not the way they're typed.

Once the script is written, follow `PIPELINE.md` to generate audio,
publish to R2, update the feed, and commit.
