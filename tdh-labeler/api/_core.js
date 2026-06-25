// Shared, dependency-free submission core for the tdh label-collection backend.
// Pure + injectable: handle(cfg, rawBody, env, commitFn, now) does no network itself.
// Underscore prefix => Vercel never routes this file; submit.js requires it.

const FROZEN_IDS = {
  expert: new Set(["t01", "t02", "t06", "t07", "t14", "t17", "t19", "t20",
                   "t23", "t26", "t28", "t31", "t32", "t33", "t35", "t40"]),
  lay:    new Set(["t06", "t17", "t31", "t35", "t40"]),
};
const CLASS_ENUM = {
  expert: new Set(["transfer", "transitional", "none"]),
  lay:    new Set(["transfer", "none", "ambiguous"]),
};
const MAX_BYTES = 256 * 1024;
const CONTAMINATION = /Human [AB] rationale for/i;

function parseAllowlist(raw) {
  const map = {};
  (raw || "").split(",").map(s => s.trim()).filter(Boolean).forEach(pair => {
    const i = pair.indexOf(":");
    if (i > 0) map[pair.slice(0, i)] = pair.slice(i + 1);
  });
  return map;
}

function validate(track, payload) {
  if (!payload || typeof payload !== "object") return "validation";
  const labels = payload.labels;
  if (!labels || typeof labels !== "object" || Array.isArray(labels)) return "validation";
  const ids = Object.keys(labels);
  if (ids.length === 0) return "validation";
  for (const id of ids) {
    if (!FROZEN_IDS[track].has(id)) return "unknown_transcript_id";
    const rec = labels[id];
    if (!rec || typeof rec !== "object") return "validation";
    if (!CLASS_ENUM[track].has(rec.classification)) return "validation";
    if (typeof rec.rationale === "string" && CONTAMINATION.test(rec.rationale)) return "contamination";
  }
  return null;
}

function buildPath(track, rater, now) {
  const ts = now.toISOString().replace(/[:.]/g, "-");
  const safe = String(rater || "anon").replace(/[^a-z0-9_]/gi, "_").slice(0, 40) || "anon";
  return `${track}/${safe}/${ts}.json`;
}

async function handle(cfg, rawBody, env, commitFn, now = new Date()) {
  if (Buffer.byteLength(rawBody || "", "utf8") > MAX_BYTES)
    return { status: 413, body: { ok: false, error: "too_large" } };

  let payload;
  try { payload = JSON.parse(rawBody); }
  catch { return { status: 422, body: { ok: false, error: "validation" } }; }

  let raterId;
  if (cfg.requireCode) {
    const allow = parseAllowlist(env.RATER_ALLOWLIST);
    const code = payload && payload.code;
    if (!code || !allow[code]) return { status: 401, body: { ok: false, error: "bad_code" } };
    raterId = allow[code];                       // server-resolved attribution
  } else {
    raterId = (payload && payload._rater) || "anon";
  }

  const verr = validate(cfg.track, payload);
  if (verr) return { status: 422, body: { ok: false, error: verr } };

  const { code, ...clean } = payload;            // never persist the code
  const record = { track: cfg.track, rater_id: raterId,
                   submitted_at: now.toISOString(), payload: clean };
  const path = buildPath(cfg.track, raterId, now);
  try { await commitFn(env, path, record); }
  catch { return { status: 502, body: { ok: false, error: "commit_failed" } }; }
  return { status: 200, body: { ok: true, file: path } };
}

module.exports = { handle, validate, buildPath, parseAllowlist,
                   FROZEN_IDS, CLASS_ENUM, MAX_BYTES };
