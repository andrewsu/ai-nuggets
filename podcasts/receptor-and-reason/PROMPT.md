You are creating a personalized podcast called "Receptor & Reason" (slug:
`receptor-and-reason`). It lives under `podcasts/receptor-and-reason/` in
the `ai-nuggets` repo. Production mechanics (TTS, R2 publish, feed updates,
commits) are documented in `podcasts/PIPELINE.md`, prepended above.

# 1. Audience

Alan Huebschen — researcher at Scripps Research, working in computational
neuropsychopharmacology. Reads papers in CNS pharmacology,
psychiatric/neurology drug discovery, and computational methods routinely.

## What he likes

- Advances in neuropsychopharmacology broadly — CNS pharmacology,
  psychiatric and neurology drug discovery, novel mechanisms,
  psychedelics, pharmacogenomics. Computational/agentic-AI angles get
  extra weight but plain pharmacology wins is welcome too.
- Agentic AI in computational biology and bioinformatics.
- Computational pharmacology generally; with extra weight when agentic
  AI is used.

## Background level

Domain literacy assumed. Do not define common terms (5-HT2A, GPCR, MDD,
KOR, ADMET, QSP, transformer, RAG, foundation model). Briefly anchor
less-common tool compounds, named methods, and specific clinical-trial
endpoints on first mention.

## What to avoid

- (none yet — will update based on feedback)

# 2. Search strategy

Cast a wide net across every tier below — don't voluntarily skip a
source. The best item on a given day might come from any of them.
Apply the source-level-failures rule from `PIPELINE.md`: one quick
retry on transient failures, then proceed with remaining sources, log
the gap in the candidate funnel, ship the episode.

**Recency window: rolling 7 days.** Items posted/announced within the
last 7 calendar days are eligible for Tiers 1-3. This is wider than
biomedical-agentic-ai's 2-day window — the neuropsychopharm corpus per
day is too thin for the 8-12-item target otherwise. Older items belong
in Tier 4 (seminal fallback) or not at all.

## Tier 1 — Neuropsychopharmacology broadly (highest priority)

Tier 1 wins head-to-head selection vs. Tier 2 or Tier 3 on the same
day unless the lower-tier item is dramatically more novel/important.

1. **bioRxiv** — neuroscience and pharmacology, last 7 days. Use the
   details API:
   ```
   curl 'https://api.biorxiv.org/details/biorxiv/YYYY-MM-DD/YYYY-MM-DD'
   ```
   for each day in the window (or a single multi-day range — check
   the API behavior). **Pull the full collection per day, not a
   sample.** Paginate via `cursor` when `messages[0].count` exceeds
   page size. Filter the entire collection by title + abstract
   relevance to CNS pharmacology, psychiatric drug discovery,
   neuropharmacology, psychedelics, or pharmacogenomics.
   - Do not "sample 30 in detail" — that misses 95% of the corpus.

2. **Articles published in the last 7 days** from these journals
   (online-ahead-of-print counts):
   - *Neuropsychopharmacology* (Nature/ACNP) — https://www.nature.com/npp/
   - *Molecular Psychiatry* (Nature) — https://www.nature.com/mp/
   - *Biological Psychiatry* + *Biological Psychiatry: CNNI*
   - *International Journal of Neuropsychopharmacology* (Oxford/CINP)
   - *Progress in Neuro-Psychopharmacology and Biological Psychiatry*
   - *Neuropharmacology* (Elsevier)

3. **Psychiatric Times** — https://www.psychiatrictimes.com/ — monthly
   pipeline reviews and breaking news on psychiatric drug development.

4. **Society press pages** for major announcements:
   - ACNP — https://acnp.org/
   - SOBP — https://sobp.org/
   - ECNP — https://www.ecnp.eu/
   - CINP and WFSBP (lower cadence; check weekly)

## Tier 2 — Agentic AI in computational biology + bioinformatics

Secondary priority.

1. **arXiv** — last 7 days, categories cs.AI, cs.CL, cs.MA, q-bio.QM,
   q-bio.NC.
   - **Read the shared daily cache first:** `/tmp/ai-nuggets-arxiv-cache.xml`.
     The runner pre-fetches the arXiv listing API once per day for the
     category union of every show, so individual shows don't need to hit
     arXiv themselves. The cache uses the `q-bio` supercategory, which
     subsumes q-bio.QM and q-bio.NC. Filter the cached Atom feed for
     submissions in the last 7 days AND biological/biomedical relevance
     AND agentic/LLM/multi-agent/autonomous keywords in title or abstract.
   - **If the cache is missing or empty** (runner pre-fetch failed), fall
     back to a live listing call:
     ```
     curl 'https://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.MA+OR+cat:q-bio.QM+OR+cat:q-bio.NC&sortBy=submittedDate&sortOrder=descending&max_results=400'
     ```
     Use `https://` directly — `http://` 301-redirects and inflates the
     request count.
   - **arXiv rate limit: 1 request per 3 seconds, hard.** A single
     OR'd query is enough — don't fan out per category. If a second
     arXiv call is genuinely needed, `sleep 4` between calls.
     Receptor-and-reason runs after biomedical-agentic-ai, so the IP
     may already be in a cool-down window — assume 429 is likely.
   - If the live API 429s, one 60s-backoff retry, then one 120s-backoff
     retry. If it still 429s, fall back to `site:arxiv.org` web search
     for the same 7-day window. Indexing lag means you'll miss the
     freshest submissions, but it beats dropping arXiv entirely.

2. **bioRxiv bioinformatics + systems biology** — last 7 days. Same
   API + pagination rules as Tier 1 bioRxiv.

3. **Articles published in the last 7 days** from: *Nature
   Biotechnology*, *npj Digital Medicine*, *Briefings in
   Bioinformatics*, *Cell Systems*.

4. **AAAI / NeurIPS / ICML proceedings** as they land. Track the
   **GenBio @ ICML 2026** workshop (Generative and Agentic AI for
   Biology, Seoul, July 2026) for high-signal items as it goes online.

## Tier 3 — Computational pharmacology + agentic AI in pharmacology

Tertiary priority.

1. **Articles published in the last 7 days** from:
   *CPT: Pharmacometrics & Systems Pharmacology* (ASCPT),
   *Clinical Pharmacology & Therapeutics* (ASCPT),
   *Drug Discovery Today*.

2. **chemRxiv** — last 7 days. Use WebSearch with `site:chemrxiv.org`
   plus a relevance keyword; the public API is Cloudflare-gated from
   this host.

3. **Industry announcements** from agentic-AI-in-drug-discovery
   programs: AstraZeneca (ChatInvent), Genentech (CLADD), Xaira,
   Iambic, Recursion, Insitro. Press pages and SEC/company news.

## Tier 4 — Seminal fallback (conditional)

**Activates only when Tiers 1-3 together yield fewer than ~10 fresh
items.** Pull older, high-impact work to fill the episode to a floor
of 8 items.

Sources:

- Recent (last 12 months) high-impact reviews summarizing multi-paper
  progress in any Tier 1-3 topic
- ACNP / SOBP / ECNP archived keynotes and presidential addresses
- Highly-cited landmark papers connected to a Tier 1 item from the
  same episode (use to anchor the fresh item in lineage)

**Constraints on fallback picks:**

- Must connect to at least one fresh item from Tiers 1-3 in the same
  episode (don't fill with unrelated classics).
- Must be flagged explicitly in the spoken script — phrases like
  "for context", "revisiting", "a landmark from", "slow week so let's
  anchor today on…". The listener should always know whether an item
  is fresh or historical.
- Subject to the dedup ledger like any other item.

## Recency is a hard filter, not a hint

Items posted or announced outside the 7-day window are out-of-scope
for Tiers 1-3 regardless of merit. They belong in Tier 4 or not at
all. "Slow week, fewer items today, including some context picks" is
an acceptable outcome.

# 3. Deduplication ledger

A persistent state file prevents the same item from being shipped in
multiple episodes.

**Path:** `podcasts/receptor-and-reason/state/shipped.jsonl`

**Format:** one JSON object per shipped episode, newline-delimited:

```jsonl
{"date":"2026-05-12","basename":"2026-05-12-receptor-and-reason","items":[{"key":"doi:10.1038/...","title":"..."},{"key":"arxiv:2605.10876","title":"..."}]}
```

**Key precedence (highest first):**

1. DOI — `doi:10.xxxx/yyyy`
2. arXiv ID — `arxiv:YYMM.NNNNN`
3. bioRxiv ID — `biorxiv:YYYY.MM.DD.NNNNNN` (from DOI suffix)
4. Stable URL — `url:<canonical-url>` for press / news items

**Runner behavior — follow these steps every run:**

The ledger is ~1.7 KB per episode and grows forever. **Never read it
into context** — no `cat`, no Read tool, no dumping the key list. Every
access goes through `scripts/shipped_keys.py`, which keeps the file on
disk and hands back only what you asked for.

1. **At run start:** nothing to load. `python3 scripts/shipped_keys.py
   receptor-and-reason --stats` prints the ledger's size for the log
   without emitting any keys.
2. **During candidate filtering — before spending any fetch budget:**
   write every candidate as one `key<TAB>title` line and pipe the whole
   list through the filter:

   ```bash
   python3 scripts/shipped_keys.py receptor-and-reason \
       < candidates.tsv > fresh.tsv
   ```

   Only the lines in `fresh.tsv` are eligible. Matching is done on
   normalized keys, so a case difference, an arXiv version suffix, a
   `https://doi.org/` prefix, a bioRxiv DOI vs. its bare
   `biorxiv:YYYY.MM.DD.NNNNNN` form, and a URL carrying `utm_*` params
   or a fragment all resolve to the same item. The stderr summary is the
   dedup number for the cron.log funnel.

   **Always supply the title.** A candidate whose title matches a
   shipped title is dropped even when its key differs — that is what
   catches an article re-entering the window under a second DOI, which
   is the standing Nature-family RSS trap. If you are certain an item is
   a genuine follow-up rather than the same work, re-run with
   `--keep-title-matches` and say so in the log.
3. **After picks are finalized and the script is written:** append with
   the same `key<TAB>title` format the filter emits:

   ```bash
   python3 scripts/shipped_keys.py receptor-and-reason --append \
       --basename YYYY-MM-DD-receptor-and-reason < picks.tsv
   ```

   It verifies the whole ledger parses before writing, then appends
   exactly one line. Do not edit or reorder existing lines by hand —
   append-only.

**Failure modes** (all enforced by the script — this is what its exit
codes mean, not extra work for you):

- File missing → empty set, created on first append.
- File corrupt (any line unparseable as JSON) → the filter prints the
  bad line numbers to stderr, which lands in `logs/cron.log`, and treats
  the ledger as empty so the episode can still be produced; `--append`
  **refuses** (exit 3) and leaves the file untouched so the data can be
  recovered by hand. If you see this, fix the ledger before the next
  run — a run under an empty set can ship a repeat.
- Item key collision (same key, different titles) → dedup hit, candidate
  dropped, warning printed with both titles.

# 4. Episode format

- **Cadence:** one episode per day, daily.
- **Length:** target 12-18 minutes spoken.
- **Item count:** 8-12 items, adaptive within the range. If Tiers 1-3
  yield fewer than 10 fresh items, expand into Tier 4 to reach the
  floor of 8.
- **Item depth:** 1-2 minutes spoken per item. Each item gets
  *what + why-it-matters + brief context*. Be opinionated, acknowledge
  limitations.
- **Ordering:** mixed across tiers — no rigid section structure. Open
  with the day's most important item regardless of tier. Sequence
  remaining items by topical adjacency (transitions that flow), not
  by tier. End with the lightest item so the episode builds-down
  rather than feeling truncated.

## File conventions

- **Script file:** `podcasts/receptor-and-reason/scripts/YYYY-MM-DD-receptor-and-reason.md`
  with a `## Script` heading. Everything after that heading (minus
  `Paper link:` / `URL:` lines) is what gets spoken.
- **Episode basename:** `YYYY-MM-DD-receptor-and-reason`.
- **Commit-message prefix:** `Episode`.

## Show-specific audio conventions

General audio rules (no DOIs/URLs/tables, spell out hard-to-say
tokens) are in `PIPELINE.md`. On top of those:

- **Don't list authors.** Full author lists waste listener attention.
  Name corresponding/PI only when it anchors the work to a known
  group ("the Krystal lab again, after last week's…"). Otherwise the
  group affiliation alone is fine, or skip.
- **Anchor tool compounds and named methods on first mention.** One
  clause is enough: "GBR-12909, a dopamine reuptake inhibitor used as
  a tool compound, …". Don't repeat in subsequent mentions within
  the same episode.
- **Speak drug generic names** when both generic and brand are well
  known. Brand only when the brand is the more familiar handle.
- **Don't read out clinical-trial registration IDs** (NCT numbers,
  EudraCT). Same principle as DOIs/URLs — they're noise in audio. If
  referencing the trial, name the sponsor and indication.
- **Tier 4 (seminal) picks must be acknowledged as such** in the
  spoken script. The listener should always know whether an item is
  fresh or historical.

Once the script is written, follow `PIPELINE.md` to generate audio,
publish to R2, update the feed, and commit.
