CREATE TABLE IF NOT EXISTS requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,                    -- unix seconds
  podcast TEXT NOT NULL,                  -- podcast slug, e.g. 'biomedical-agentic-ai'
  user_id TEXT NOT NULL,                  -- per-listener token from URL
  episode_id TEXT NOT NULL,               -- mp3 basename without .mp3
  method TEXT NOT NULL,                   -- 'GET' or 'HEAD'
  ip_hash TEXT NOT NULL,                  -- sha256(ip | IP_SALT | YYYYMM), hex
  user_agent TEXT,
  country TEXT,                           -- cf.country
  colo TEXT,                              -- cf.colo
  asn INTEGER,                            -- cf.asn
  is_bot INTEGER NOT NULL DEFAULT 0       -- 0/1, cheap UA heuristic
);

CREATE INDEX IF NOT EXISTS idx_requests_podcast_ts        ON requests(podcast, ts);
CREATE INDEX IF NOT EXISTS idx_requests_podcast_user_ts   ON requests(podcast, user_id, ts);
CREATE INDEX IF NOT EXISTS idx_requests_podcast_episode   ON requests(podcast, episode_id);
CREATE INDEX IF NOT EXISTS idx_requests_ts                ON requests(ts);
