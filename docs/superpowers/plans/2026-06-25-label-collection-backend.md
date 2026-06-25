# Label-Collection Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/api/submit` serverless endpoint to the `tdh-labeler` and `tdh-bluff` Vercel sites that auto-commits each blind submission to a private `tdh-labels` GitHub repo, with server-side validation/auth that preserves ground-truth integrity, and a retained local-download fallback.

**Architecture:** Each static site gains a Node serverless function (`api/submit.js`) backed by a shared, dependency-free core (`api/_core.js`) with a pure, injectable `handle(cfg, rawBody, env, commitFn)`. The core validates (schema + contamination guard + frozen-ID set), authenticates (per-rater code for expert), then commits a new uniquely-named JSON file to GitHub via the Contents API. The HTML's existing export is extended to POST the same payload and show status, while still downloading locally.

**Tech Stack:** Node 18+ (Vercel serverless, global `fetch`, `Buffer`), `node:test` + `node:assert` (zero deps), one Python helper (`pull_labels.py`). No frameworks, no npm install.

**Spec:** `docs/superpowers/specs/2026-06-25-label-collection-backend-design.md`

---

## Conventions
- Run commands from repo root (`C:\Users\navka\navakanth001`).
- JS is CommonJS (`module.exports` / `require`) — no `package.json` needed; Vercel auto-detects `api/`.
- `_core.js` is underscore-prefixed so Vercel never routes it; it's imported by `submit.js`.
- Tests never hit the network — `commitFn`/`fetchFn` are injected.
- The Pyrefly pre-commit hook only checks Python; only Task 7 touches it.

## File Structure
```text
tdh-labeler/
  api/_core.js          # shared logic: validate, auth, handle, githubCommit
  api/submit.js         # Vercel handler: track=expert, requireCode=true
  tests/core.test.js    # node:test over the core (both tracks)
  .vercelignore         # exclude tests/ from deploy
  index.html            # MODIFIED: code field + POST + status
tdh-bluff/
  api/_core.js          # identical copy of the labeler core
  api/submit.js         # Vercel handler: track=lay, requireCode=false (+ best-effort rate limit)
  .vercelignore
  index.html            # MODIFIED: POST + status
tdh-labels-seed/        # contents to seed the new private repo
  pull_labels.py
  README.md
docs/MANUAL_SETUP-tdh-backend.md   # token/env/redeploy runbook
```

---

### Task 1: Core validation + auth + `handle` (TDD)

**Files:**
- Create: `tdh-labeler/api/_core.js`
- Test: `tdh-labeler/tests/core.test.js`

- [ ] **Step 1: Write the failing test**

```js
// tdh-labeler/tests/core.test.js
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

test("valid expert submission → 200, commits at server-resolved rater path", async () => {
  let path;
  const body = JSON.stringify({ code: "abcd", _rater: "ignored",
    labels: { t01: { classification: "transfer", rationale: "good reasoning" } } });
  const r = await handle(EXPERT, body, ENV, async (_e, p) => { path = p; },
    new Date("2026-06-25T10:00:00Z"));
  assert.equal(r.status, 200);
  assert.equal(r.body.ok, true);
  assert.match(path, /^expert\/expert_a\/2026-06-25/);
});

test("missing/unknown code → 401, no commit", async () => {
  let called = false;
  const body = JSON.stringify({ code: "nope", labels: { t01: { classification: "transfer" } } });
  const r = await handle(EXPERT, body, ENV, async () => { called = true; });
  assert.equal(r.status, 401);
  assert.equal(called, false);
});

test("contaminated rationale → 422", async () => {
  const body = JSON.stringify({ code: "abcd",
    labels: { t01: { classification: "transfer", rationale: "Human A rationale for t01" } } });
  const r = await handle(EXPERT, body, ENV, noop);
  assert.equal(r.status, 422);
  assert.equal(r.body.error, "contamination");
});

test("transcript id outside frozen set → 422 unknown_transcript_id", async () => {
  const body = JSON.stringify({ code: "abcd", labels: { t99: { classification: "transfer" } } });
  const r = await handle(EXPERT, body, ENV, noop);
  assert.equal(r.body.error, "unknown_transcript_id");
});

test("bad classification → 422 validation", async () => {
  const body = JSON.stringify({ code: "abcd", labels: { t01: { classification: "wat" } } });
  const r = await handle(EXPERT, body, ENV, noop);
  assert.equal(r.body.error, "validation");
});

test("oversize → 413", async () => {
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

test("lay open submission with valid bluff shape → 200", async () => {
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

test("commit throw → 502", async () => {
  const body = JSON.stringify({ code: "abcd", labels: { t01: { classification: "transfer" } } });
  const r = await handle(EXPERT, body, ENV, async () => { throw new Error("boom"); });
  assert.equal(r.status, 502);
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `node --test tdh-labeler/tests/`
Expected: FAIL — `Cannot find module '../api/_core.js'`.

- [ ] **Step 3: Write the implementation**

```js
// tdh-labeler/api/_core.js
const FROZEN_IDS = {
  expert: new Set(["t01","t02","t06","t07","t14","t17","t19","t20",
                   "t23","t26","t28","t31","t32","t33","t35","t40"]),
  lay:    new Set(["t06","t17","t31","t35","t40"]),
};
const CLASS_ENUM = {
  expert: new Set(["transfer","transitional","none"]),
  lay:    new Set(["transfer","none","ambiguous"]),
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test tdh-labeler/tests/`
Expected: PASS (all tests).

- [ ] **Step 5: Commit**

```bash
git add tdh-labeler/api/_core.js tdh-labeler/tests/core.test.js
git commit -m "feat(tdh): submission core — validate/auth/handle (zero-dep, TDD)"
```

---

### Task 2: GitHub commit function

**Files:**
- Modify: `tdh-labeler/api/_core.js` (add `githubCommit`, export it)
- Test: `tdh-labeler/tests/core.test.js` (append)

- [ ] **Step 1: Append the failing test**

```js
// append to tdh-labeler/tests/core.test.js
const { githubCommit } = require("../api/_core.js");

test("githubCommit PUTs base64 content to the contents API", async () => {
  let url, opts;
  const fakeFetch = async (u, o) => { url = u; opts = o; return { ok: true, status: 201 }; };
  await githubCommit({ GITHUB_REPO: "o/r", GITHUB_TOKEN: "tok", GITHUB_BRANCH: "main" },
    "expert/a/x.json", { hello: "world" }, fakeFetch);
  assert.equal(url, "https://api.github.com/repos/o/r/contents/expert/a/x.json");
  assert.equal(opts.method, "PUT");
  assert.match(opts.headers.Authorization, /^Bearer tok$/);
  const sent = JSON.parse(opts.body);
  assert.equal(sent.branch, "main");
  assert.equal(Buffer.from(sent.content, "base64").toString("utf8").includes("world"), true);
});

test("githubCommit throws on non-2xx", async () => {
  const fakeFetch = async () => ({ ok: false, status: 403 });
  await assert.rejects(() => githubCommit({ GITHUB_REPO: "o/r", GITHUB_TOKEN: "t" },
    "p.json", {}, fakeFetch), /github 403/);
});
```

- [ ] **Step 2: Run to verify failure**

Run: `node --test tdh-labeler/tests/`
Expected: FAIL — `githubCommit is not a function`.

- [ ] **Step 3: Implement (append to `_core.js`, before `module.exports`)**

```js
async function githubCommit(env, path, record, fetchFn = fetch) {
  const repo = env.GITHUB_REPO;
  const branch = env.GITHUB_BRANCH || "main";
  const url = `https://api.github.com/repos/${repo}/contents/${path}`;
  const content = Buffer.from(JSON.stringify(record, null, 2), "utf8").toString("base64");
  const res = await fetchFn(url, {
    method: "PUT",
    headers: {
      "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
      "Accept": "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": "tdh-collector",
    },
    body: JSON.stringify({ message: `label: ${path}`, content, branch }),
  });
  if (!res.ok) throw new Error(`github ${res.status}`);
  return true;
}
```

And add `githubCommit` to the `module.exports` object.

- [ ] **Step 4: Run to verify pass**

Run: `node --test tdh-labeler/tests/`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tdh-labeler/api/_core.js tdh-labeler/tests/core.test.js
git commit -m "feat(tdh): githubCommit via Contents API (injected fetch, TDD)"
```

---

### Task 3: Expert Vercel handler + `.vercelignore`

**Files:**
- Create: `tdh-labeler/api/submit.js`
- Create: `tdh-labeler/.vercelignore`
- Test: `tdh-labeler/tests/handler.test.js`

- [ ] **Step 1: Write the failing test (mock req/res)**

```js
// tdh-labeler/tests/handler.test.js
const { test } = require("node:test");
const assert = require("node:assert");
const handler = require("../api/submit.js");

function mockReq(method, bodyStr) {
  async function* gen() { yield Buffer.from(bodyStr || ""); }
  const r = gen(); r.method = method; return r;
}
function mockRes() {
  return { statusCode: 0, headers: {}, body: "",
    setHeader(k, v) { this.headers[k] = v; },
    end(s) { this.body = s; } };
}

test("non-POST → 405", async () => {
  const res = mockRes();
  await handler(mockReq("GET", ""), res);
  assert.equal(res.statusCode, 405);
});

test("POST with bad code → 401 (no env allowlist match)", async () => {
  process.env.RATER_ALLOWLIST = "good:expert_a";
  process.env.GITHUB_REPO = "o/r"; process.env.GITHUB_TOKEN = "t";
  const res = mockRes();
  await handler(mockReq("POST", JSON.stringify({ code: "bad",
    labels: { t01: { classification: "transfer" } } })), res);
  assert.equal(res.statusCode, 401);
});
```

- [ ] **Step 2: Run to verify failure**

Run: `node --test tdh-labeler/tests/`
Expected: FAIL — `Cannot find module '../api/submit.js'`.

- [ ] **Step 3: Implement the handler**

```js
// tdh-labeler/api/submit.js
const { handle, githubCommit } = require("./_core.js");

module.exports = async (req, res) => {
  res.setHeader("Content-Type", "application/json");
  if (req.method !== "POST") {
    res.statusCode = 405;
    return res.end(JSON.stringify({ ok: false, error: "method" }));
  }
  let raw = "";
  for await (const chunk of req) raw += chunk;
  const result = await handle({ track: "expert", requireCode: true },
    raw, process.env, githubCommit);
  res.statusCode = result.status;
  res.end(JSON.stringify(result.body));
};
```

```text
# tdh-labeler/.vercelignore
tests/
```

- [ ] **Step 4: Run to verify pass**

Run: `node --test tdh-labeler/tests/`
Expected: PASS (all core + handler tests).

- [ ] **Step 5: Commit**

```bash
git add tdh-labeler/api/submit.js tdh-labeler/.vercelignore tdh-labeler/tests/handler.test.js
git commit -m "feat(tdh): expert Vercel handler + vercelignore"
```

---

### Task 4: Lay (bluff) deployment — copy core, lay handler, drift guard

**Files:**
- Create: `tdh-bluff/api/_core.js` (identical copy)
- Create: `tdh-bluff/api/submit.js` (lay, best-effort rate limit)
- Create: `tdh-bluff/.vercelignore`
- Test: `tdh-bluff/tests/identical.test.js`

- [ ] **Step 1: Copy the core verbatim**

Run: `cp tdh-labeler/api/_core.js tdh-bluff/api/_core.js`
Expected: file created, byte-identical.

- [ ] **Step 2: Write the drift-guard test**

```js
// tdh-bluff/tests/identical.test.js
const { test } = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");

test("bluff core is byte-identical to labeler core (no drift)", () => {
  const a = fs.readFileSync(__dirname + "/../api/_core.js");
  const b = fs.readFileSync(__dirname + "/../../tdh-labeler/api/_core.js");
  assert.ok(a.equals(b), "tdh-bluff/api/_core.js has drifted from the labeler core");
});
```

- [ ] **Step 3: Write the lay handler (best-effort in-memory rate limit)**

```js
// tdh-bluff/api/submit.js
const { handle, githubCommit } = require("./_core.js");

// Best-effort per-warm-instance limiter (resets on cold start; not robust across
// instances — robust limiting would need Vercel KV, deferred per spec §12).
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
```

```text
# tdh-bluff/.vercelignore
tests/
```

- [ ] **Step 4: Run both test suites**

Run: `node --test tdh-labeler/tests/ && node --test tdh-bluff/tests/`
Expected: PASS (identical-core guard green).

- [ ] **Step 5: Commit**

```bash
git add tdh-bluff/api/_core.js tdh-bluff/api/submit.js tdh-bluff/.vercelignore tdh-bluff/tests/identical.test.js
git commit -m "feat(tdh): lay handler + identical-core drift guard"
```

---

### Task 5: Expert client — code field + POST + status

**Files:**
- Modify: `tdh-labeler/index.html`

- [ ] **Step 1: Add the code input + status span**

In the rater card (the block containing `id="rater"` and the Export button), insert a code input after the name input and a status span after the Export button:

```html
<label class="fld">Access code (given to you when recruited)</label>
<input type="text" id="ratercode" placeholder="your code">
```
and immediately after `<button class="exp" onclick="exportAll()">⬇ Export</button>`:
```html
<div id="submitstatus" style="font-size:13px;margin-top:6px"></div>
```

- [ ] **Step 2: Replace `exportAll()` with the POST-enabled version**

Replace the existing function (currently the 4-line `function exportAll(){…a.click();}`) with:

```js
async function exportAll(){
  const name=(document.getElementById("rater").value||"rater").replace(/[^a-z0-9_]/gi,"_");
  const code=(document.getElementById("ratercode")||{}).value||"";
  const out={_rater:name,_labeled:Object.keys(store).filter(k=>store[k].classification).length,labels:store};
  // (1) local download — always runs, fallback against any network failure
  const b=new Blob([JSON.stringify(out,null,2)],{type:"application/json"});
  const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="labels_"+name+".json";a.click();
  // (2) server submit
  const st=document.getElementById("submitstatus");st.textContent="saving…";st.style.color="#999";
  try{
    const res=await fetch("/api/submit",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({track:"expert",code,...out})});
    const j=await res.json().catch(()=>({}));
    if(res.ok){st.textContent="✓ saved to server: "+j.file;st.style.color="var(--cyan)";}
    else{st.textContent="⚠ server save failed ("+(j.error||res.status)+") — email the downloaded file";st.style.color="#f88";}
  }catch(e){st.textContent="⚠ server unreachable — email the downloaded file";st.style.color="#f88";}
}
```

- [ ] **Step 3: Manual smoke (no deploy needed)**

Open `tdh-labeler/index.html` locally; the page loads, the code field renders, clicking Export still downloads the JSON and shows `⚠ server unreachable` (expected with no server). No console errors.

- [ ] **Step 4: Commit**

```bash
git add tdh-labeler/index.html
git commit -m "feat(tdh): labeler posts to /api/submit (code + status, download fallback)"
```

---

### Task 6: Lay client — POST + status

**Files:**
- Modify: `tdh-bluff/index.html`

- [ ] **Step 1: Add a status span**

After the Finish button (`<button onclick="finish()">Finish &amp; Send</button>`), insert:
```html
<div id="submitstatus" style="font-size:13px;margin-top:6px"></div>
```

- [ ] **Step 2: Replace `finish()` with the POST-enabled version**

Replace the existing `function finish(){…a.click();}` with:

```js
async function finish(){
  const name=(document.getElementById("rater")||{}).value||"rater";
  const safe=name.replace(/[^a-z0-9_]/gi,"_");
  const labels={};for(const t of DATA){const r=rec(t.transcript_id);if(r.choice)
    labels[t.transcript_id]={classification:MAP[r.choice],lay_choice:r.choice,human_confidence:r.sure??0.7};}
  const out={_rater:safe,_mode:"lay",_labeled:Object.keys(labels).length,labels};
  const b=new Blob([JSON.stringify(out,null,2)],{type:"application/json"});
  const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="bluff_"+safe+".json";a.click();
  const st=document.getElementById("submitstatus");st.textContent="saving…";st.style.color="#999";
  try{
    const res=await fetch("/api/submit",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({track:"lay",...out})});
    const j=await res.json().catch(()=>({}));
    st.textContent=res.ok?"✓ sent — thank you!":"⚠ couldn't send ("+(j.error||res.status)+") — send the downloaded file";
    st.style.color=res.ok?"#3c9":"#f88";
  }catch(e){st.textContent="⚠ couldn't send — send the downloaded file";st.style.color="#f88";}
}
```

(If `tdh-bluff/index.html` has no `id="rater"` input, the `||"rater"` fallback keeps lay anonymous — that is acceptable for the lay track.)

- [ ] **Step 3: Manual smoke**

Open `tdh-bluff/index.html` locally; answer the 5 puzzles, click Finish — JSON downloads and status shows `⚠ couldn't send` (expected offline). No console errors.

- [ ] **Step 4: Commit**

```bash
git add tdh-bluff/index.html
git commit -m "feat(tdh): bluff posts to /api/submit (status, download fallback)"
```

---

### Task 7: `tdh-labels` repo seed — `pull_labels.py` + README

**Files:**
- Create: `tdh-labels-seed/pull_labels.py`
- Create: `tdh-labels-seed/README.md`
- Test: `tdh-labels-seed/test_pull_labels.py`

- [ ] **Step 1: Write the failing test**

```python
# tdh-labels-seed/test_pull_labels.py
import json
from pathlib import Path
import pull_labels


def test_keeps_latest_per_rater_transcript(tmp_path):
    src = tmp_path / "labels"
    (src / "expert" / "expert_a").mkdir(parents=True)
    early = {"rater_id": "expert_a", "submitted_at": "2026-06-25T09:00:00Z",
             "payload": {"labels": {"t01": {"classification": "none"}}}}
    late = {"rater_id": "expert_a", "submitted_at": "2026-06-25T10:00:00Z",
            "payload": {"labels": {"t01": {"classification": "transfer"}}}}
    (src / "expert" / "expert_a" / "a.json").write_text(json.dumps(early))
    (src / "expert" / "expert_a" / "b.json").write_text(json.dumps(late))
    dest = tmp_path / "out"
    pull_labels.main(str(src), str(dest))
    got = json.loads((dest / "expert_a" / "t01.json").read_text())
    assert got["classification"] == "transfer"
```

- [ ] **Step 2: Run to verify failure**

Run: `cd tdh-labels-seed && python -m pytest test_pull_labels.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'pull_labels'`.

- [ ] **Step 3: Implement**

```python
# tdh-labels-seed/pull_labels.py
#!/usr/bin/env python3
"""Pull collected labels from a tdh-labels checkout into the detector eval dirs.
Keeps the latest submission per (rater_id, transcript_id).

Usage: python pull_labels.py <tdh-labels-checkout> <dest data/labels dir>
"""
import json
import sys
from pathlib import Path


def main(labels_root: str, dest_root: str) -> None:
    src = Path(labels_root) / "expert"
    dest = Path(dest_root)
    latest: dict[tuple[str, str], tuple[str, dict]] = {}
    for f in sorted(src.glob("*/*.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        rater = rec.get("rater_id", f.parent.name)
        ts = rec.get("submitted_at", f.stem)
        for tid, label in rec.get("payload", {}).get("labels", {}).items():
            key = (rater, tid)
            if key not in latest or ts > latest[key][0]:
                latest[key] = (ts, label)
    for (rater, tid), (_ts, label) in latest.items():
        out = dest / rater
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{tid}.json").write_text(json.dumps(label, indent=2), encoding="utf-8")
    print(f"wrote {len(latest)} label files under {dest}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: pull_labels.py <tdh-labels-checkout> <dest data/labels dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
```

```markdown
<!-- tdh-labels-seed/README.md -->
# tdh-labels (private)

Auto-collected blind labels from the tdh-labeler / tdh-bluff tools.

```
expert/<rater_id>/<timestamp>.json   # one submission; payload.labels keyed by transcript_id
lay/<handle>/<timestamp>.json
```

Append-only — every submission is a new file; git history is the audit trail.

## Pull into the detector eval pipeline
```bash
git pull
python pull_labels.py . ../transfer-detector-v0/data/labels/human_a   # repeat per rater dest
python ../transfer-detector-v0/eval/human_ceiling.py
```
Never open `transfer-detector-v0/data/transcripts/synthetic/_key.SEALED.json` until labels are final.
```

- [ ] **Step 4: Run to verify pass**

Run: `cd tdh-labels-seed && python -m pytest test_pull_labels.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tdh-labels-seed/
git commit -m "feat(tdh): tdh-labels repo seed — pull_labels.py + README"
```

---

### Task 8: Manual setup runbook

**Files:**
- Create: `docs/MANUAL_SETUP-tdh-backend.md`

- [ ] **Step 1: Write the runbook**

```markdown
# tdh backend — manual setup (one-time)

These steps need a human (token creation + Vercel env vars). Code is already deployed-ready.

## 1. Create the private data repo
- New GitHub repo: `tdh-labels` (Private). Copy `tdh-labels-seed/*` into it; push.

## 2. Fine-grained token (least privilege)
- GitHub → Settings → Developer settings → Fine-grained tokens → Generate.
- Resource owner: your account. Repository access: **Only select repositories → tdh-labels**.
- Permissions: **Contents → Read and write** (nothing else). Copy the token.

## 3. Vercel env vars (BOTH projects: tdh-labeler and tdh-bluff)
- Project → Settings → Environment Variables (Production):
  - `GITHUB_TOKEN` = the fine-grained token
  - `GITHUB_REPO`  = `navakanth1984/tdh-labels`
  - `GITHUB_BRANCH`= `main`
- tdh-labeler ONLY: `RATER_ALLOWLIST` = `code1:expert_a,code2:expert_b` (one code per recruited expert)

## 4. Redeploy
- Push to the branch Vercel tracks, or Vercel → Deployments → Redeploy. Both URLs now collect.

## 5. Verify
- Open tdh-labeler.vercel.app, label one item, enter a valid code, Export → status shows `✓ saved`.
- `git -C tdh-labels pull` → new file under `expert/<rater>/`.
```

- [ ] **Step 2: Commit**

```bash
git add docs/MANUAL_SETUP-tdh-backend.md
git commit -m "docs(tdh): manual setup runbook (token, env vars, redeploy)"
```

---

## Self-Review

**1. Spec coverage:**
- §1 write-only / blind → core returns only `{ok,file}` (Task 1). ✅
- §1 validation + contamination guard → `validate` (Task 1, tested). ✅
- §1 frozen-ID enforced → `FROZEN_IDS` per track (Task 1, tested incl. lay subset). ✅
- §1 download fallback → client keeps download then POSTs (Tasks 5/6). ✅
- §1 append-only → unique timestamp path, always create (Task 1; `buildPath`). ✅
- §3 dedicated repo + tagging + pull → Task 7 seed + `pull_labels.py`. ✅
- §4 endpoint contract / status codes → Tasks 1/3 (401/413/422/429/502/200). ✅
- §5 validation rules → Task 1; lay bluff shape pinned (transfer/none/ambiguous, 5 IDs). ✅
- §6 client changes incl. code field → Tasks 5/6. ✅
- §7 secrets/env → Task 8 runbook; code never persisted (Task 1 test). ✅
- §8 error handling → 502 on commit fail (Task 1), client fallback (Tasks 5/6). ✅
- §9 testing DI → injected `commitFn`/`fetchFn` throughout. ✅
- §10 threat model S1–S5 → code-gate (Task 3), scoped token (Task 8), frozen-ID/guard (Task 1), server-resolved rater (Task 1), write-only (Task 1). ✅
- §11 manual steps → Task 8. ✅
- §12 deferred (rate-limit robustness) → noted in Task 4 lay limiter comment. ✅

**2. Placeholder scan:** No TBD/TODO; every code step is complete. Lay bluff shape is concrete (not deferred — pinned in Task 1 tests/enums). ✅

**3. Type/name consistency:** `handle(cfg, rawBody, env, commitFn, now)`, `githubCommit(env, path, record, fetchFn)`, `buildPath(track, rater, now)`, `parseAllowlist`, `FROZEN_IDS[track]`, `CLASS_ENUM[track]`, status-code/error strings (`bad_code`/`validation`/`contamination`/`unknown_transcript_id`/`too_large`/`rate_limited`/`commit_failed`) — consistent across tasks and tests. ✅
