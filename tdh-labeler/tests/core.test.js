const { test } = require("node:test");
const assert = require("node:assert");
const { handle, buildPath, parseAllowlist } = require("../api/_core.js");

const ENV = { RATER_ALLOWLIST: "abcd:expert_a,efgh:expert_b", GITHUB_REPO: "x/y",
              GITHUB_TOKEN: "t", GITHUB_BRANCH: "main" };
const EXPERT = { track: "expert", requireCode: true };
const LAY = { track: "lay", requireCode: false };
const noop = async () => true;

test("parseAllowlist maps code->rater", () => {
  assert.deepEqual(parseAllowlist("a:x, b:y"), { a: "x", b: "y" });
});

test("buildPath encodes track/rater/timestamp", () => {
  const p = buildPath("expert", "expert_a", new Date("2026-06-25T10:00:00Z"));
  assert.match(p, /^expert\/expert_a\/2026-06-25T10-00-00-000Z\.json$/);
});

test("valid expert submission -> 200, commits at server-resolved rater path", async () => {
  let path;
  const body = JSON.stringify({ code: "abcd", _rater: "ignored",
    labels: { t01: { classification: "transfer", rationale: "good reasoning" } } });
  const r = await handle(EXPERT, body, ENV, async (_e, p) => { path = p; },
    new Date("2026-06-25T10:00:00Z"));
  assert.equal(r.status, 200);
  assert.equal(r.body.ok, true);
  assert.match(path, /^expert\/expert_a\/2026-06-25/);
});

test("missing/unknown code -> 401, no commit", async () => {
  let called = false;
  const body = JSON.stringify({ code: "nope", labels: { t01: { classification: "transfer" } } });
  const r = await handle(EXPERT, body, ENV, async () => { called = true; });
  assert.equal(r.status, 401);
  assert.equal(called, false);
});

test("contaminated rationale -> 422", async () => {
  const body = JSON.stringify({ code: "abcd",
    labels: { t01: { classification: "transfer", rationale: "Human A rationale for t01" } } });
  const r = await handle(EXPERT, body, ENV, noop);
  assert.equal(r.status, 422);
  assert.equal(r.body.error, "contamination");
});

test("transcript id outside frozen set -> 422 unknown_transcript_id", async () => {
  const body = JSON.stringify({ code: "abcd", labels: { t99: { classification: "transfer" } } });
  const r = await handle(EXPERT, body, ENV, noop);
  assert.equal(r.body.error, "unknown_transcript_id");
});

test("bad classification -> 422 validation", async () => {
  const body = JSON.stringify({ code: "abcd", labels: { t01: { classification: "wat" } } });
  const r = await handle(EXPERT, body, ENV, noop);
  assert.equal(r.body.error, "validation");
});

test("oversize -> 413", async () => {
  const body = JSON.stringify({ code: "abcd", _rater: "x".repeat(300 * 1024),
    labels: { t01: { classification: "transfer" } } });
  const r = await handle(EXPERT, body, ENV, noop);
  assert.equal(r.status, 413);
});

test("commit never stores the access code", async () => {
  let record;
  const body = JSON.stringify({ code: "abcd", labels: { t01: { classification: "none" } } });
  await handle(EXPERT, body, ENV, async (_e, _p, rec) => { record = rec; });
  assert.equal(JSON.stringify(record).includes("abcd"), false);
  assert.equal(record.rater_id, "expert_a");
});

test("lay open submission with valid bluff shape -> 200", async () => {
  const body = JSON.stringify({ _rater: "joe", _mode: "lay",
    labels: { t06: { classification: "ambiguous", lay_choice: "vague", human_confidence: 0.5 } } });
  const r = await handle(LAY, body, ENV, noop);
  assert.equal(r.status, 200);
});

test("lay rejects expert-only id t01", async () => {
  const body = JSON.stringify({ labels: { t01: { classification: "none" } } });
  const r = await handle(LAY, body, ENV, noop);
  assert.equal(r.body.error, "unknown_transcript_id");
});

test("commit throw -> 502", async () => {
  const body = JSON.stringify({ code: "abcd", labels: { t01: { classification: "transfer" } } });
  const r = await handle(EXPERT, body, ENV, async () => { throw new Error("boom"); });
  assert.equal(r.status, 502);
});
