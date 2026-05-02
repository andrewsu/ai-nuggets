/**
 * Podcast analytics + redirect Worker.
 *
 * Route: GET|HEAD /p/:podcast/u/:user_id/:episode_id.mp3
 *   - logs one row to D1 and one data point to Analytics Engine (both via
 *     ctx.waitUntil so they don't block the redirect)
 *   - 302-redirects to the canonical mp3 URL produced by resolveTarget()
 *
 * Anything else -> 404 plain text.
 *
 * IP hashing: sha256(ip | IP_SALT | YYYYMM-bucket). The same listener gets the
 * same hash within a calendar month and a fresh hash across months. The
 * IP_SALT secret should still be rotated periodically as defense in depth.
 */

export interface Env {
  DB: D1Database;
  AE: AnalyticsEngineDataset;
  IP_SALT: string;
  GITHUB_REPO_RAW: string;
  ALLOWED_PODCASTS: string;
}

const ROUTE = /^\/p\/([a-zA-Z0-9_-]+)\/u\/([a-zA-Z0-9_-]+)\/([a-zA-Z0-9_.-]+)\.mp3$/;

const BOT_PATTERNS = [
  "bot", "crawler", "spider", "preview", "facebookexternalhit",
  "curl", "wget", "python-requests", "okhttp", "go-http-client",
  "headlesschrome", "scraper",
];

function isBot(ua: string | null): boolean {
  if (!ua) return true;
  const lower = ua.toLowerCase();
  return BOT_PATTERNS.some((p) => lower.includes(p));
}

async function hashIp(ip: string, salt: string, ts: number): Promise<string> {
  const d = new Date(ts * 1000);
  const monthBucket = `${d.getUTCFullYear()}${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
  const data = new TextEncoder().encode(`${ip}|${salt}|${monthBucket}`);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function resolveTarget(env: Env, podcast: string, _userId: string, episodeId: string): string {
  // TODO: swap to R2 once audio leaves GitHub. Sketch:
  // const obj = await env.BUCKET.get(`podcasts/${podcast}/episodes/${episodeId}.mp3`);
  // return obj
  //   ? new Response(obj.body, { headers: { "content-type": "audio/mpeg", "etag": obj.httpEtag } })
  //   : new Response("Not Found", { status: 404 });
  return `${env.GITHUB_REPO_RAW}/podcasts/${podcast}/episodes/${episodeId}.mp3`;
}

export default {
  async fetch(req: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(req.url);
    const method = req.method;

    if (method !== "GET" && method !== "HEAD") {
      return new Response("Not Found", { status: 404, headers: { "content-type": "text/plain" } });
    }

    const m = ROUTE.exec(url.pathname);
    if (!m) {
      return new Response("Not Found", { status: 404, headers: { "content-type": "text/plain" } });
    }

    const [, podcast, userId, episodeId] = m;
    const allowed = env.ALLOWED_PODCASTS.split(",").map((s) => s.trim()).filter(Boolean);
    if (!allowed.includes(podcast)) {
      return new Response("Unknown podcast", { status: 404, headers: { "content-type": "text/plain" } });
    }

    const ts = Math.floor(Date.now() / 1000);
    const ip = req.headers.get("cf-connecting-ip") ?? "0.0.0.0";
    const ua = req.headers.get("user-agent");
    const cf: any = (req as any).cf ?? {};
    const country = (cf.country as string | undefined) ?? null;
    const colo = (cf.colo as string | undefined) ?? null;
    const asn = (cf.asn as number | undefined) ?? null;
    const bot = isBot(ua);
    const ipHash = await hashIp(ip, env.IP_SALT, ts);

    ctx.waitUntil((async () => {
      try {
        await env.DB.prepare(
          `INSERT INTO requests
             (ts, podcast, user_id, episode_id, method, ip_hash, user_agent, country, colo, asn, is_bot)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        )
          .bind(ts, podcast, userId, episodeId, method, ipHash, ua, country, colo, asn, bot ? 1 : 0)
          .run();
      } catch (err) {
        console.error("D1 insert failed", err);
      }
      try {
        env.AE.writeDataPoint({
          blobs: [podcast, userId, episodeId, method, country ?? "", colo ?? "", ua ?? "", ipHash],
          doubles: [bot ? 1 : 0, asn ?? 0],
          indexes: [podcast],
        });
      } catch (err) {
        console.error("AE write failed", err);
      }
    })());

    return Response.redirect(resolveTarget(env, podcast, userId, episodeId), 302);
  },
};
