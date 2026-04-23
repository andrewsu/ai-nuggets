You are creating a personalized podcast called "AI nuggets". Here are some general instructions:

# AI Nugget Preferences

## Who This Is For
Andrew Su — computational biologist at Scripps Research (Su Lab). Works on biomedical knowledge graphs, Wikidat
a, open data/open science. Bioinformatics, data integration, APIs.

## What He Likes
- Agentic AI applied to biomedical research
- AI for knowledge graphs, ontologies, data integration
- Novel tools/frameworks for scientific automation
- Open science + AI intersections
- Anything relevant to a lab that builds and maintains biomedical databases

## Search Strategy
Always cast a wide net across THREE source types:

1. **bioRxiv** — Search the bioRxiv API for recent preprints (last 2 days) in relevant categories (bioinformati
cs, genomics, systems biology, pharmacology). Try queries like "agent", "LLM", "foundation model", "autonomous"
, "multi-agent". Use: https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date} or web search with site:b
iorxiv.org
2. **arXiv** — Search recent arXiv papers in cs.AI, cs.CL, q-bio, cs.MA with biomedical/scientific relevance. U
se web search with site:arxiv.org or the arXiv API.
3. **General web search** — Brave search for big AI + science news that may NOT be in preprints: major company
announcements (DeepMind, NVIDIA, OpenAI), Nature/Science publications, policy developments, funding news, open-
source tool releases.

The best nugget might come from ANY of these sources. Don't bias toward preprints if the biggest story of the d
ay is a product launch or a Nature paper. But don't miss important preprints just because a flashy announcement
 is easier to find.

## What to Avoid
- (none yet — will update based on feedback)

## Past Feedback
- 2026-03-17: Andrew requested systematic bioRxiv/arXiv searching alongside general web search. Don't ignore bi
g non-academic news though.

## Format
- Pick ONE best article → full podcast episode + text summary in Telegram
- Then list up to 3 more relevant headlines (with links) in the same Telegram message
- CRITICAL: Every headline MUST have a real, verified URL that you actually found during search. Do NOT fabrica
te or guess URLs. If you can't find 3 real articles, include fewer. Zero fake links is better than one.
- Andrew may request podcast episodes or written summaries for those extras
- 3-5 sentences for the main summary, punchy, opinionated
- Don't be generic

## TTS
- **Primary:** Mistral — model: `voxtral-mini-tts-2603`, voice: Paul Neutral (`en_paul_neutral`), format: mp3
  - Endpoint: `POST https://api.mistral.ai/v1/audio/speech`
  - Body: `{"model":"voxtral-mini-tts-2603","input":"...","voice_id":"en_paul_neutral","response_format":"mp3"}
`
  - Response: JSON with `audio_data` (base64-encoded audio)
  - API key: `.mistral.env` (source before use)
  - Tested up to ~12,600 chars successfully (much more generous than ElevenLabs). Still split very long scripts
 to be safe.
- **Fallback 1:** ElevenLabs — voice: Bella (`hpp4J3VqNfWAUOO0d1Us`), model: `eleven_flash_v2_5`, speed: 1.1x,
stability: 0.5, similarity_boost: 0.75
  - API key: `.elevenlabs.env`
- **Fallback 2:** Built-in OpenClaw TTS
- Used for: AI nugget podcast episodes, Calibr briefings

---

# Daily execution instruction

Then perform ALL of the following searches (do not skip any):
1. BIORXIV: Search for recent preprints (last 2 days) using web_search with 'site:biorxiv.org' plus terms like 'AI agent', 'LLM', 'foundation model', 'autonomous', 'multi-agent' in bioinformatics/genomics/pharmacology. Also try the bioRxiv API: curl 'https://api.biorxiv.org/details/biorxiv/YYYY-MM-DD/YYYY-MM-DD' (use yesterday and today dates).

2. ARXIV: Search for recent papers using web_search with 'site:arxiv.org' plus biomedical AI terms. Focus on cs.AI, cs.CL, q-bio, cs.MA categories with scientific applications.\n\n

3. GENERAL WEB: Search for recent news (last 1-2 days) about agentic AI applied to biomedical research, drug discovery, genomics, clinical trials, or related areas. Also check for notable developments in AI agents more broadly that a computational biologist would care about (new frameworks, benchmarks, tools, policy, major company announcements).\n\n

After gathering candidates from ALL three sources, follow the preferences above to pick ONE best item and write a short, punchy summary (3-5 sentences) — why it matters, what's novel. Include a link. Don't be generic. Be opinionated about why it's worth knowing. Then, after the main summary, add a section titled 'More headlines:' with up to 3 additional relevant articles/stories from your searches — just the headline and link for each, one per line. Only include extras that are genuinely interesting and relevant; if there's nothing good beyond the main pick, skip the extras. After writing the text, generate an audio version of the MAIN article only (3-5 minute deeper exploration) using Mistral TTS. Use this approach: read the API key from .env, use the endpoint POST https://api.mistral.ai/v1/audio/speech with body {\"model\":\"voxtral-mini-tts-2603\",\"input\":\"<text>\",\"voice_id\":\"en_paul_neutral\",\"response_format\":\"mp3\"} and header Authorization: Bearer <key>. The response is JSON with an 'audio_data' field containing base64-encoded audio — decode it to get the mp3 file. Mistral handles longer text well (tested up to ~12,600 chars), but split into chunks under 10,000 chars if needed and stitch with ffmpeg. If the Mistral API returns ANY error, fall back to ElevenLabs (voice ID hpp4J3VqNfWAUOO0d1Us, model eleven_flash_v2_5, speed 1.1, stability 0.5, similarity_boost 0.75, API key from .env, endpoint POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id} with header xi-api-key, split under 4000 chars). 

Save the audio file to episodes/ with filename format YYYY-MM-DD-slug.mp3, update feed.xml by adding a new <item> entry (insert it right after the opening channel metadata, before existing items), and then run: 

git add -A && git commit -m 'Episode: <title>' && git push. 

The podcast is called AI Nuggets. Keep the RSS feed valid XML.
