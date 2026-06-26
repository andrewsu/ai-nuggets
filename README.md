# AI Nuggets

Personalized AI-curated podcast feeds. Each show under `podcasts/<slug>/`
is a separate feed for a separate audience.

## Shows

| Slug | Audience | Subscribe |
|---|---|---|
| [`biomedical-agentic-ai`](podcasts/biomedical-agentic-ai/) | Andrew Su (Su Lab, Scripps) — agentic AI applied to biomedical research | [feed.xml](https://raw.githubusercontent.com/andrewsu/ai-nuggets/main/podcasts/biomedical-agentic-ai/feed.xml) |
| [`blackbird-brief`](podcasts/blackbird-brief/) | **The Blackbird Brief** — Matt Tremblay & Blackbird Labs leadership; daily Sourcing Radar on commercializable JHU/UMB/Lieber research + weekly Sunday Portfolio Watch | [feed.xml](https://raw.githubusercontent.com/andrewsu/ai-nuggets/main/podcasts/blackbird-brief/feed.xml) |
| [`calibr-briefing`](podcasts/calibr-briefing/) | **Travis' Briefing** — Travis Young (Calibr-Skaggs, Scripps), daily biotech & pharma briefing | [feed.xml](https://raw.githubusercontent.com/andrewsu/ai-nuggets/main/podcasts/calibr-briefing/feed.xml) |
| [`jinglin-ai-pulse`](podcasts/jinglin-ai-pulse/) | Jinglin (Ollie) Jian (Scripps) — AI Twitter discourse, investment trends, and deep podcast highlights | [feed.xml](https://raw.githubusercontent.com/andrewsu/ai-nuggets/main/podcasts/jinglin-ai-pulse/feed.xml) |
| [`justice-biotech-brief`](podcasts/justice-biotech-brief/) | Justice Fleischmann (Rodgers Lab, Calibr at Scripps) — biotech & pharma headlines with focus on VEGF×PD-L1, JAK ADCs, and trispecific T cell engagers | [feed.xml](https://raw.githubusercontent.com/andrewsu/ai-nuggets/main/podcasts/justice-biotech-brief/feed.xml) |
| [`receptor-and-reason`](podcasts/receptor-and-reason/) | Alan Huebschen (Scripps) — neuropsychopharmacology + computational pharmacology + agentic AI in biology | [feed.xml](https://raw.githubusercontent.com/andrewsu/ai-nuggets/main/podcasts/receptor-and-reason/feed.xml) |
| [`scripps-biomed-brief`](podcasts/scripps-biomed-brief/) | Peter Schultz (Scripps) — new targets, modalities, and technologies for human health | [feed.xml](https://raw.githubusercontent.com/andrewsu/ai-nuggets/main/podcasts/scripps-biomed-brief/feed.xml) |

After cloning, run `git config core.hooksPath .githooks` once to activate the
pre-commit feed-XML validator.

- **Adding a new show to this deployment?** See [ADDING_A_SHOW.md](ADDING_A_SHOW.md).
- **Running your own ai-nuggets** (your own Cloudflare account, cron, API
  keys)? See [SETUP.md](SETUP.md).

## Repo layout

```
ai-nuggets/
├── gen_tts.py                          # shared TTS pipeline (Mistral / ElevenLabs)
├── lib/show.py                         # per-show config loader (reads show.toml)
├── scripts/
│   ├── new_show.py                     # scaffold a new podcast
│   ├── run_all_shows.sh                # daily cron entry point
│   ├── publish_episode.sh              # upload an mp3 to R2
│   └── update_feed_for_worker.py       # rewrite feed.xml enclosures for the Worker
├── worker/                             # Cloudflare Worker (analytics + redirect)
└── podcasts/<slug>/
    ├── show.toml                       # voice config, paths, RSS metadata
    ├── PROMPT.md                       # audience profile + daily recipe for the AI
    ├── feed.xml                        # this show's RSS feed
    ├── episodes/                       # mp3s
    ├── scripts/                        # daily transcripts (.md or .txt)
    └── logs/                           # run logs
```

## Adding a new show

```bash
python3 scripts/new_show.py my-new-show \
  --title "My New Show" \
  --description "What this show is about" \
  --owner "Owner Name <email>"
```

The daily runner (`scripts/run_all_shows.sh`) auto-discovers any
`podcasts/*/PROMPT.md` — no cron edit needed. After scaffolding you
still need to customize the PROMPT/show.toml, allow the slug on the
Worker, and smoke-test before letting cron take over. See
[ADDING_A_SHOW.md](ADDING_A_SHOW.md) for the full checklist.
