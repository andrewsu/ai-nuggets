You are creating a personalized podcast called "Calibr-Skaggs Daily Briefing"
(slug: `calibr-briefing`). It lives under `podcasts/calibr-briefing/` in the
`ai-nuggets` repo. Production mechanics (TTS, R2 publish, feed updates,
commits) are documented in `podcasts/PIPELINE.md`, prepended above.

# 1. Audience

Travis Young at Calibr-Skaggs, Scripps Research.

## What he likes

Daily biotech/pharma briefings with explicit connections to the Calibr
pipeline. Two episodes per day:

1. **Headlines** (~5 min) — Top biotech/pharma news of the day, quick
   roundup.
2. **Spotlight** (~5–8 min) — Deep dive on the single most important
   development from focus areas or headlines. Thorough analysis: what
   happened, why it matters, competitive landscape, and explicit connections
   to the Calibr pipeline. Don't spread thin across multiple topics — go
   deep on one.

## Focus areas

- **In Vivo CAR-T** — new approaches, publications, newcos, clinical data.
- **MASH / FGF21** — clinical trial data, publications, announcements.
  Relevant to Calibr's MASH biologic (dual-acting, multiple receptors,
  IND-enabling). Track efruxifermin (Akero), efimosfermin (BOS-580/GSK),
  resmetirom, and combination therapy approaches.
- **General therapeutic development** — major deals, clinical readouts, FDA
  actions, new company launches.
- **Artificial Intelligence in drug discovery** — major new findings, news
  from companies using AI in drug discovery (Xaira, Iambic, Revolution
  Medicines, and others), status of clinical development, major new findings.
- **Foresite Capital or Foresite Labs portfolio companies** — news from
  companies previously or currently funded by Foresite Capital or Foresite Labs.

## Calibr pipeline reference

Full pipeline details and therapeutic targets live in
`memory/calibr-pipeline.md` in the workspace (not in this repo).

## What to avoid

- (none yet — will update based on feedback)

# 2. Search strategy

Headlines sources:

- Fierce Biotech
- Fierce Pharma
- Endpoints News
- STAT News
- BioPharma Dive
- The Biotech Voyager
- Clinical Trials Arena
- Genetic Engineering & Biotech News

For the spotlight, pick the single most important development. Pull
publications, press releases, and trial data as needed.

# 3. Episode format

Two episodes per day. Both spoken by Nigel.

- Real, verified URLs only — never fabricate.
- Always connect drug name to underlying target or mechanism.
- Give context to headlines and deep dives — prior investors, prior deals
  in the space, etc.

## Headlines episode (~3–5 min)

- Punchy, numbered, quick roundup.
- **Script file:** `podcasts/calibr-briefing/scripts/YYYY-MM-DD-pharma-headlines.txt`
  — no `## Script` heading; the entire file is the spoken text.
- **Episode basename:** `YYYY-MM-DD-pharma-headlines`.

## Spotlight episode (~5–8 min)

- Deep, analytical, with explicit Calibr-pipeline connections.
- **Script file:** `podcasts/calibr-briefing/scripts/YYYY-MM-DD-<topic>-spotlight.txt`
  — no `## Script` heading.
- **Episode basename:** `YYYY-MM-DD-<topic>-spotlight`.

# 4. Commit

Single commit covering both episodes.

- **Commit-message prefix:** `Calibr YYYY-MM-DD`.
- Example: `Calibr 2026-05-05: <headline summary> + <spotlight summary>`.

Once both scripts are written, follow `PIPELINE.md` to generate audio,
publish to R2, update the feed, and commit.
