const { handle, githubCommit } = require("./_core.js");

// Best-effort per-warm-instance limiter (resets on cold start; not robust across
// instances — robust limiting would need Vercel KV, deferred per spec section 12).
const HITS = new Map();
const WINDOW_MS = 60 * 1000;
const MAX_PER_WINDOW = 20;
function rateLimited(ip) {
  const now = Date.now();
  const arr = (HITS.get(ip) || []).filter(t => now - t < WINDOW_MS);
  arr.push(now);
  HITS.set(ip, arr);
  return arr.length > MAX_PER_WINDOW;
}

module.exports = async (req, res) => {
  res.setHeader("Content-Type", "application/json");
  if (req.method !== "POST") {
    res.statusCode = 405;
    return res.end(JSON.stringify({ ok: false, error: "method" }));
  }
  const ip = (req.headers && req.headers["x-forwarded-for"]) || "unknown";
  if (rateLimited(String(ip))) {
    res.statusCode = 429;
    return res.end(JSON.stringify({ ok: false, error: "rate_limited" }));
  }
  let raw = "";
  for await (const chunk of req) raw += chunk;
  const result = await handle({ track: "lay", requireCode: false },
    raw, process.env, githubCommit);
  res.statusCode = result.status;
  res.end(JSON.stringify(result.body));
};
