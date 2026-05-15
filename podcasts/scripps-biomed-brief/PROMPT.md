You are creating a personalized podcast called "Scripps Biomedical Brief" (slug:
`scripps-biomed-brief`). It lives under `podcasts/scripps-biomed-brief/`.

# 1. Audience

This podcast is curated for **Peter Schultz**, President and CEO of Scripps Research, and his leadership team. The audience consists of world-class scientists, chemists, and biomedical researchers who are at the forefront of drug discovery and basic biological research.

## What they like

- **New Targets**: Novel biological pathways or proteins that can be modulated for therapeutic benefit.
- **New Modalities**: Beyond small molecules—PROTACs, molecular glues, cell therapies, gene editing, and synthetic biology.
- **Emerging Technologies**: AI in drug discovery.
- **Translational Impact**: Research that has a clear path to improving human health or addressing unmet medical needs.
- **Technical Depth**:Scientific rigor and specific details over high-level marketing speak.

## What to avoid

- **Generic AI Hype**: Avoid vague claims about AI "revolutionizing" medicine without specific examples or data.
- **Surface-level News**: Skip the basic health tips or well-known industry news.
- **Marketing Fluff**: Focus on the science and the data, not the corporate PR.

# 2. Search strategy

Search for the latest breakthroughs (past 24-48 hours) from the following sources:
- **Journals**: Nature, Science, Cell, JACS, Angewandte Chemie, Nature Chemical Biology, Nature Biomedical Engineering.
- **Preprints**: bioRxiv (specifically Chemical Biology, Pharmacology and Toxicology, Bioengineering) and medrxiv
- **Industry News**: Fierce Biotech, Fierce Pharma, Endpoints News, STAT News, BioPharma Dive, The Biotech Voyager, Clinical Trials Arena, Genetic Engineering & Biotech News (focusing on R&D and early-stage pipelines).

**Example Queries** (but these should evolve over time):
- "novel therapeutic target"
- "first-in-class modality"
- "chemical biology drug discovery"
- "synthetic biology human health"

# 3. Format

- **Tone**: Professional, insightful, and efficient.
- **Structure**:
    - **Introduction**: A 1-sentence greeting and overview of today's briefing.
    - **The Nuggets**: 3-4 key stories. Each story should have:
        - A punchy headline.
        - 3–5 sentences summarizing the breakthrough, the technology used, and why it matters for human health.
        - A verified URL for further reading (put in the show notes, but not in the script)
    - **Closing**: A brief sign-off.
- **Length**: Total script should be around 700 words (approx. 5 minutes of audio).

# 4. TTS & distribution

Voice config lives in `show.toml`. API keys in repo-root `.env`. Don't write
your own TTS code — use `gen_tts.py --show scripps-biomed-brief`.

# 5. Daily execution

1. Write script to `podcasts/scripps-biomed-brief/scripts/YYYY-MM-DD-slug.md` with a
   `## Script` heading.
2. Generate audio:
   ```
   python3 gen_tts.py --show scripps-biomed-brief \
     podcasts/scripps-biomed-brief/scripts/YYYY-MM-DD-slug.md \
     podcasts/scripps-biomed-brief/episodes/YYYY-MM-DD-slug.mp3
   ```
3. Add a new `<item>` to `podcasts/scripps-biomed-brief/feed.xml` with real byte size and
   ffprobe duration. Enclosure URLs point at the Worker.
4. `git add -A && git commit -m 'Episode: Scripps Biomedical Brief — <title>' && git push`
