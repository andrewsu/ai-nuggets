# 🦔 AI Nuggets

Personalized podcasts curated and narrated by **Nigel**, an AI assistant.
Each show under `podcasts/<slug>/` is a separate feed for a separate audience.

## Shows

| Slug | Audience | Subscribe |
|---|---|---|
| [`biomedical-agentic-ai`](podcasts/biomedical-agentic-ai/) | Andrew Su (Su Lab, Scripps) — agentic AI applied to biomedical research | [feed.xml](https://raw.githubusercontent.com/andrewsu/ai-nuggets/main/feed.xml) |
| [`calibr-briefing`](podcasts/calibr-briefing/) | Travis Young (Calibr-Skaggs, Scripps) — daily biotech & pharma briefing | [feed.xml](https://raw.githubusercontent.com/andrewsu/ai-nuggets/main/podcasts/calibr-briefing/feed.xml) |

The root `feed.xml` is a symlink to `podcasts/biomedical-agentic-ai/feed.xml`
to preserve that show's original public RSS URL.

## Repo layout

```
ai-nuggets/
├── gen_tts.py                          # shared TTS pipeline (Mistral / ElevenLabs)
├── lib/show.py                         # per-show config loader (reads show.toml)
├── scripts/
│   ├── new_show.py                     # scaffold a new podcast
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

Then edit `podcasts/my-new-show/PROMPT.md` and `show.toml` to taste, add
the slug to `worker/wrangler.toml` (`ALLOWED_PODCASTS`), and redeploy the
Worker. See `worker/README.md` for Worker setup.
