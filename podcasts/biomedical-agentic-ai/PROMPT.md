You are creating a personalized podcast called "Biomedical Agentic AI" (slug:
`biomedical-agentic-ai`). It lives under `podcasts/biomedical-agentic-ai/` in
the `ai-nuggets` repo. Production mechanics (TTS, R2 publish, feed updates,
commits) are documented in `podcasts/PIPELINE.md`, prepended above.

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

Once the script is written, follow `PIPELINE.md` to generate audio,
publish to R2, update the feed, and commit.
