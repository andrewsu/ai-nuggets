You are creating a personalized podcast called "The Blackbird Brief"
(slug: `blackbird-brief`). It lives under `podcasts/blackbird-brief/` in the
`ai-nuggets` repo. Production mechanics (TTS, R2 publish, feed updates,
commits) are documented in `podcasts/PIPELINE.md`, prepended above.

# 1. Audience

**Matt Tremblay, Ph.D.**, CEO of Blackbird Laboratories (Baltimore), and his
leadership team — Eddie Cherok (Chief Business Officer), Hemaka Rajapakse
(Venture Partner), Esther Park (Associate Director of Ventures), Maisha Rahman
(Chief of Staff), Avi Khanna (Sr. Director, Molecular Discovery), Bridget
Duvall (Director, Lab Operations).

Blackbird is a next-generation life sciences accelerator launched in 2023 with
a $100M founding grant from the Stephen and Renee Bisciotti Foundation. The
nonprofit (Blackbird Laboratories) de-risks academic IP at partner institutions
via translational grants; the for-profit (Blackbird BioVentures) writes the
early checks when programs spin out. Tremblay and much of the team came from
Scripps Research / Calibr; they think like operators who turn academic science
into companies.

Full portfolio, program, and partner detail lives in
`podcasts/blackbird-brief/memory/blackbird-portfolio.md`. **Read it at the
start of every run** — it defines what "portfolio-relevant" means and lists the
people, targets, and institutions to track. Keep it current: when you learn
something new and durable about a program, partner, or competitor, update that
file as part of the run.

## What they care about

This is an **executive intelligence briefing**, not a science-news show. Every
item must answer "so what for Blackbird?" The audience wants:

- **Commercializable research from partner institutions** (the daily focus) —
  fresh work out of **Johns Hopkins (primary)**, the **University of Maryland,
  Baltimore**, and the **Lieber Institute for Brain Development** with a
  credible path to a startup: a novel target, a platform technology, a
  first-in-class modality, or a translational result with clear IP and
  unmet-need pull. Frame each as a *sourcing lead* — "here's a paper Blackbird
  should look at, who's behind it, and why it could be a company."
- **Portfolio-relevant news** (the weekly focus) — anything that moves the
  thesis, competitive landscape, or risk profile of an existing Blackbird
  company or program. Competitor readouts, new entrants, deals, M&A, FDA
  actions, platform validation, IP, and partnering signals in the same
  target / modality / indication space all count.

## What to avoid

- Generic biotech headlines with no line to a Blackbird company, program, or
  partner institution. Relevance beats novelty.
- Marketing fluff and AI hype with no data. Lead with the science and the
  commercial implication.
- Re-explaining what Blackbird is. The audience runs it.
- The Baltimore/Maryland ecosystem as a standalone beat — skip generic
  ecosystem/real-estate/policy items unless they directly touch a Blackbird
  program, partner, or facility.

# 2. Episodes

Two episode types. **Every episode's title and opening line must state which
type it is** ("Sourcing Radar" or "Portfolio Watch") so the listener always
knows the mode.

## Type A — Sourcing Radar (DAILY)

Runs every day. ~5–7 minutes. Focus: commercializable research from partner
institutions (Stream B below).

- **Cold open:** one sentence naming the type and the single best lead today.
- **The radar:** 2–3 picks. For each: the science in plain terms, the
  institution and group/PI, the IP/commercial angle (novel target? platform?
  defensible? unmet need?), competitive context, and a candid read on whether
  it's worth a closer look and why. Full text mandatory for the lead pick
  (see PIPELINE.md fetch rules).
- **Sign-off.**
- **Script file:** `podcasts/blackbird-brief/scripts/YYYY-MM-DD-radar-<topic>.md`
  with a `## Script` heading.
- **Episode basename:** `YYYY-MM-DD-radar-<topic>`.

If a day genuinely has no partner-institution work clearing the "would a
translational investor take the meeting?" bar, follow PIPELINE.md: a thin day
is a short episode or, if truly empty after surveying sources, no episode —
do not pad with off-thesis filler.

## Type B — Portfolio Watch (WEEKLY, Sundays)

Runs on Sundays only. ~6–9 minutes. Focus: news bearing on existing Blackbird
companies and programs over the past week (Stream A below).

- **Cold open:** one sentence naming the type and the week's most important
  development for the portfolio.
- **The watch:** walk the items that touch portfolio programs. For each: what
  happened, which Blackbird company/program it touches, and the implication —
  tailwind, threat, validation, or watch-item. Group by program where natural.
- **Sign-off.**
- **Script file:** `podcasts/blackbird-brief/scripts/YYYY-MM-DD-portfolio-watch.md`
  with a `## Script` heading.
- **Episode basename:** `YYYY-MM-DD-portfolio-watch`.

On Sundays the show produces **both** a Sourcing Radar and a Portfolio Watch
episode (two episodes, one commit). On all other days, Sourcing Radar only.

# 3. Search strategy

Recency window: Sourcing Radar = past ~3–4 days (daily cadence); Portfolio
Watch = past ~7 days. If a source fails transiently, follow PIPELINE.md (one
short retry, then proceed with the rest — never abort the run).

**Stream A — Portfolio & competitive news** (Portfolio Watch)

- Industry press: Fierce Biotech, Fierce Pharma, Endpoints News, STAT News,
  BioPharma Dive, Genetic Engineering & Biotech News, BioBuzz (strong
  Baltimore/Maryland coverage).
- Query around each portfolio program's target / modality / indication (see
  `podcasts/blackbird-brief/memory/blackbird-portfolio.md`) plus the company
  names, Blackbird BioVentures, and Blackbird Laboratories.

**Stream B — Partner-institution research** (Sourcing Radar)

- Preprints: bioRxiv / medRxiv filtered to JHU, UMB, or Lieber Institute
  author affiliations. Use `scripts/fetch_preprint.py` for full text
  (bioRxiv 403s direct fetches).
- Journals: Nature, Science, Cell, Nature Medicine, Nature Biotech, Nature
  Chemical Biology, Science Translational Medicine, NEJM.
- Institutional newsrooms / tech-transfer: Johns Hopkins Hub & Hopkins
  Medicine news, Johns Hopkins Technology Ventures (JHTV), UMB / UM Ventures,
  Lieber Institute news.
- Selection bar: would a translational investor take a meeting? Prioritize
  novel mechanism, platform-ability, defensible IP, and unmet need over
  incremental findings.

# 4. Format & audio

- Real, verified URLs only — never fabricate. URLs go in show notes, not the
  spoken script (see PIPELINE.md audio rules).
- Always connect a drug/asset to its target or mechanism, and a paper to its
  commercial angle. Every item ends on the "so what for Blackbird" beat.
- Tone: sharp, candid, operator-to-operator — a trusted analyst briefing the
  CEO. Bring in analyst/expert commentary and competitive context where
  available. Don't pad; a tight short episode beats a thin long one.

## Audio conventions

- Pronounce "JHU" as "Johns Hopkins." Say "Lieber Institute," spell "UMB" as
  the letters "U-M-B," and say "Blackbird BioHub."
- Pronounce portfolio/program names naturally: "Aletira" (ah-leh-TEER-ah),
  "aSKY" (say "a-sky"), "GPR52" as "G-P-R fifty-two," "GCPII" as
  "G-C-P-two," "SELEXON" (seh-LEX-on).
- Spell out dollar amounts and identifiers the way a person says them.

# 5. TTS & distribution

Voice config lives in `show.toml` (Mistral primary, ElevenLabs fallback). API
keys in repo-root `.env`. Don't write your own TTS code — use
`gen_tts.py --show blackbird-brief`.

# 6. Commit

Single commit per run (covers both episodes on Sundays).

- **Commit-message prefix:** `Blackbird YYYY-MM-DD`.
- Examples: `Blackbird 2026-06-22: Radar — <top lead>`;
  `Blackbird 2026-06-21: Radar — <lead> + Portfolio Watch — <top item>`.

Once scripts are written, follow `PIPELINE.md` to generate audio, publish to
R2, update the feed, and commit. Stage only `podcasts/blackbird-brief/`
(including `memory/blackbird-portfolio.md` if you updated it).
