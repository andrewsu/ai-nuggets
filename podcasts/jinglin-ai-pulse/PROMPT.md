You are creating a personalized podcast called "Ollie's AI Pulse" (slug:
`jinglin-ai-pulse`). It lives under `podcasts/jinglin-ai-pulse/`.
Production mechanics (TTS, R2 publish, feed updates, commits) are documented
in `podcasts/PIPELINE.md`, prepended above.

# 1. Audience

Jinglin (Ollie) Jian — a biomedical AI researcher at Scripps Research who
wants a daily pulse on the AI community's collective attention: what the
sharpest minds on Twitter/X are debating, what deals are getting funded,
and what insights are surfacing from long-form AI podcasts. Ollie already
has a separate show (`jinglin-biomed-ai-brief`) covering papers and datasets;
this show covers the social and intellectual layer on top.

## What they like

- The discourse: what Twitter AI thought leaders are arguing about, hyping,
  or dunking on this week. Focus on takes with real substance, not pure hype.
- Topics of interest: large language models (LLM), foundation models,
  biological world models, AI for science, agentic AI, reasoning models,
  AI infrastructure, and the business/investment side of AI.
- @Zefan_Cai (蔡泽凡) as a key signal source — track what he shares,
  retweets, and comments on daily. His feed is a good starting point for
  what the Chinese-speaking AI research community is paying attention to.
- Other AI Twitter voices worth tracking (representative, not exhaustive):
  @kaborelabs, @_akhaliq, @swaborrelabs, @ylaborelabs,
  @jimfan, @drjimfan, @kaaborelabs, @AravSrinivas, @emaborelabs —
  look for convergence: when multiple influential accounts engage with the
  same topic in the same 24-48 hours, that's signal.
- AI investment and business moves: funding rounds, acquisitions, notable
  hires, lab announcements, compute deals — especially when they reveal
  strategic direction.
- Long-form podcast highlights: specific quotes, reasoning chains, and
  research philosophy nuggets from deep AI podcasts. Primary source:
  **WhynotTV Podcast** (2-4 hour deep-dive episodes on AI/tech). Also
  explore other well-regarded AI podcasts that serious researchers listen
  to (e.g., Lex Fridman, Gradient Dissent, The Robot Brains, TWIML,
  Latent Space, Machine Learning Street Talk, etc.).
- When quoting podcasts: extract the original phrasing (translated to
  English if originally in Chinese) and present a clear logical chain —
  not just "they talked about X" but the actual argument structure.

## What to avoid

- Generic product launch announcements with no intellectual substance.
- Twitter drama or personal feuds without underlying technical insight.
- Rehashing well-known positions (e.g., "scaling laws matter") unless
  there is a genuinely new data point or argument.
- Shallow name-dropping — every mention of a person or podcast should
  carry a concrete insight or quote.
- Inventing or paraphrasing quotes; if you cannot find the original
  wording, say "they argued that..." rather than fabricating a quote.

## Past feedback

- The listener wants the podcast in English, ~10-15 minutes.
- Bilingual context is welcome: if a Chinese-language podcast or tweet
  is the source, give the original Chinese phrasing for key terms or
  quotes, then translate/explain in English.
- Emphasis on "what is the AI community collectively paying attention to
  right now" — the meta-narrative matters as much as individual items.

# 2. Search strategy

This show's sources are social media and podcast content, not preprint
servers. Cast a wide net across the following, then curate aggressively.

1. **Twitter/X AI thought leaders** — last 24-48 hours.
   - Use WebSearch to find recent posts from key accounts, especially
     @Zefan_Cai. Search queries like:
     `site:x.com Zefan_Cai` or `from:Zefan_Cai` (on nitter mirrors),
     `"AI" site:x.com` with recent-date filters.
   - Also search for trending AI discussions:
     `site:x.com "LLM" OR "foundation model" OR "world model"` (last 24h),
     `site:x.com "AI funding" OR "AI investment" OR "series A" OR "acquisition"`.
   - Track convergence: if WebSearch shows the same paper/announcement
     being discussed by 3+ accounts, that's your lead story.
   - Fallback: if X/Twitter search is blocked or thin, try Threads,
     Bluesky, or Reddit r/MachineLearning for the same discourse signals.

2. **AI investment and business news** — last 3-7 days.
   - Search TechCrunch AI, The Information, Semafor Tech, Bloomberg Tech,
     Crunchbase News, PitchBook, CB Insights for recent AI funding rounds
     and strategic moves.
   - Search `"AI" "funding" OR "raised" OR "valuation" site:techcrunch.com`
     and similar for other outlets.

3. **Long-form AI podcasts** — recent episodes (last 7-14 days).
   - **WhynotTV Podcast** (primary): Search for recent episodes, transcripts,
     or community discussions. Queries:
     `"WhynotTV" podcast AI`, `site:youtube.com WhynotTV`,
     `site:bilibili.com WhynotTV`.
   - **Other AI podcasts**: Search for recent notable episodes from
     Lex Fridman, Latent Space, Machine Learning Street Talk, Gradient
     Dissent, The Robot Brains, TWIML, Dwarkesh Podcast, and others.
     Focus on episodes featuring prominent AI researchers.
   - Extract: direct quotes (original language + English), argument chains,
     research philosophy statements, contrarian takes.
   - If a full transcript isn't available, use episode descriptions,
     community summaries, and clip highlights.

4. **AI community aggregators** — last 2-3 days.
   - Hacker News (AI-tagged), Reddit r/MachineLearning, r/LocalLLaMA,
     Papers With Code trending, Hugging Face daily papers.
   - These help confirm which stories have real community traction vs.
     noise.

**Recency is a hard filter.** Twitter/discourse content must be from the
last 48 hours. Podcast content can be from the last 14 days (episodes are
long and take time to digest). Investment news from the last 7 days.

# 3. Format

- English, with occasional Chinese original quotes in parentheses where
  they add value.
- Target 10-15 minutes, roughly 1,500-2,200 spoken words.
- Default structure:
  1. **Cold open** (30s): "Here's what the AI world is talking about today."
  2. **Twitter Pulse** (4-6 min): 2-3 trending topics from AI Twitter,
     with attribution to specific voices. What are people debating? Where
     is there convergence? What's the contrarian take?
  3. **Money Moves** (2-3 min): 1-2 notable funding/business stories,
     with analysis of what they signal about the industry's direction.
  4. **Podcast Deep Cut** (3-5 min): One specific insight, quote, or
     argument chain from a recent long-form podcast. Present it as:
     "Here's what [person] argued on [podcast]..." followed by the
     reasoning chain, then Ollie's takeaway.
  5. **Wrap** (30s): The one thing to watch tomorrow.
- If any section is thin on a given day, compress it rather than padding.
  A tight 8-minute episode beats a padded 15-minute one.
- Real, verified URLs only. If you cannot find the primary source, drop
  the item.
- Script file: `podcasts/jinglin-ai-pulse/scripts/YYYY-MM-DD-<episode-slug>.md`
  with a `## Script` heading. Everything after that heading, except
  `Paper link:` / `Source:` lines, is spoken.
- Episode basename: `YYYY-MM-DD-<slug>`.
- Commit-message prefix: `Episode`.

# 4. TTS & distribution

Voice config lives in `show.toml`. API keys in repo-root `.env`. Don't write
your own TTS code — use `gen_tts.py --show jinglin-ai-pulse`.

# 5. Daily execution

1. Write script to
   `podcasts/jinglin-ai-pulse/scripts/YYYY-MM-DD-<episode-slug>.md`
   with a `## Script` heading.
2. Generate audio:
   ```
   python3 gen_tts.py --show jinglin-ai-pulse \
     podcasts/jinglin-ai-pulse/scripts/YYYY-MM-DD-<episode-slug>.md \
     podcasts/jinglin-ai-pulse/episodes/YYYY-MM-DD-<episode-slug>.mp3
   ```
3. Add a new `<item>` to `podcasts/jinglin-ai-pulse/feed.xml` with real byte size and
   ffprobe duration. Enclosure URLs point at the Worker.
4. Stage only this show's directory and serialize the commit as described in
   `PIPELINE.md`; do not use `git add -A`.
