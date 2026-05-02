-- Example queries against the D1 'requests' table.
-- Run with: npx wrangler d1 execute podcast --remote --command "<sql>"
-- or: npx wrangler d1 execute podcast --remote --file=./queries.sql

-- 1. Downloads per podcast, last 30 days (excluding bots).
SELECT podcast, COUNT(*) AS downloads
FROM requests
WHERE ts >= unixepoch('now', '-30 days')
  AND is_bot = 0
  AND method = 'GET'
GROUP BY podcast
ORDER BY downloads DESC;

-- 2. Downloads per user per podcast, last 30 days (excluding bots).
SELECT podcast, user_id, COUNT(*) AS downloads
FROM requests
WHERE ts >= unixepoch('now', '-30 days')
  AND is_bot = 0
  AND method = 'GET'
GROUP BY podcast, user_id
ORDER BY downloads DESC;

-- 3. Downloads per episode per podcast, last 30 days.
SELECT podcast, episode_id, COUNT(*) AS downloads
FROM requests
WHERE ts >= unixepoch('now', '-30 days')
  AND is_bot = 0
  AND method = 'GET'
GROUP BY podcast, episode_id
ORDER BY downloads DESC
LIMIT 50;

-- 4. Unique listeners per podcast per month (distinct ip_hash, valid within month
--    because the salt rotates monthly).
SELECT podcast,
       strftime('%Y-%m', ts, 'unixepoch') AS month,
       COUNT(DISTINCT ip_hash)            AS unique_listeners
FROM requests
WHERE is_bot = 0
  AND method = 'GET'
GROUP BY podcast, month
ORDER BY month DESC, podcast;

-- 5. Most popular apps (User-Agent histogram), top 20, last 30 days, real listeners.
SELECT user_agent, COUNT(*) AS hits
FROM requests
WHERE ts >= unixepoch('now', '-30 days')
  AND is_bot = 0
  AND method = 'GET'
GROUP BY user_agent
ORDER BY hits DESC
LIMIT 20;

-- 6. Cold subscribers: per (podcast, user_id), last fetch >14 days ago.
--    Useful for cost-control before generating new per-user content.
SELECT podcast, user_id, MAX(ts) AS last_fetch_ts,
       (unixepoch() - MAX(ts)) / 86400 AS days_since_last_fetch
FROM requests
WHERE is_bot = 0
GROUP BY podcast, user_id
HAVING days_since_last_fetch > 14
ORDER BY days_since_last_fetch DESC;

-- 7. Country breakdown per podcast, last 30 days, real listeners.
SELECT podcast, COALESCE(country, '??') AS country, COUNT(*) AS downloads
FROM requests
WHERE ts >= unixepoch('now', '-30 days')
  AND is_bot = 0
  AND method = 'GET'
GROUP BY podcast, country
ORDER BY podcast, downloads DESC;

-- 8. GET vs HEAD ratio per podcast, last 30 days.
--    Many podcast apps issue HEAD probes before download — this lets you tell
--    real fetches from auto-discovery probes.
SELECT podcast, method, is_bot, COUNT(*) AS hits
FROM requests
WHERE ts >= unixepoch('now', '-30 days')
GROUP BY podcast, method, is_bot
ORDER BY podcast, method, is_bot;
